"""Bootstrap uncertainty of imputed cells (Stage 4, Bab 2.6).

For b = 1..B the rows of each source are resampled with replacement, the
same imputation method as Stage 3 is fit on the resample, and the fitted
imputer is applied to the original (unresampled) frame. Every originally
missing cell therefore gets B predictions; their spread is the uncertainty
of that imputed value.

Each nutrient is resampled with the method Stage 3 actually used for it
(data_processed/method_selection.csv). The cross-DB transfer uses the TKPI
MissForest fit of the same b, applied to MyFCD, so its uncertainty reflects
resampling of its training source.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.experimental import enable_iterative_imputer  # noqa: F401  (required by IterativeImputer)
from sklearn.impute import IterativeImputer, KNNImputer

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS
from src.imputation.baselines import GROUP_COLUMN, MICE_MAX_ITER, group_medians

from src.cleaning.normalizers import is_missing
from src.imputation.cross_transfer import apply_fitted_imputer
from src.imputation.missforest_imputer import fit_random_forest_imputer


@dataclass(frozen=True)
class BootstrapConfig:
    n_boot: int = 50
    seed: int = 42
    n_jobs: int = -1


def numeric(series: pd.Series) -> pd.Series:
    return series.apply(lambda value: np.nan if is_missing(value) else value).astype(float)


def robust_scale(values: pd.Series) -> float:
    """IQR / 1.349 (equals sd for normal data, but not inflated by outliers); sd when IQR is 0."""
    values = values.dropna()
    iqr = float(values.quantile(0.75) - values.quantile(0.25))
    return iqr / 1.349 if iqr > 0 else float(values.std())


def _resample(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = rng.integers(0, len(df), size=len(df))
    return df.iloc[rows].reset_index(drop=True)


def _observed(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [c for c in columns if c in df.columns and numeric(df[c]).notna().any()]


def _fit_apply(method: str, train: pd.DataFrame, apply: pd.DataFrame, columns: list[str], seed: int) -> pd.DataFrame:
    """Fit `method` on `train` and impute `columns` of `apply`, mirroring Stage 3.

    Columns with no observed value in `train` (possible in a small resample)
    are left missing, so that replicate does not count for them.
    """
    usable = _observed(train, columns)
    result = apply.copy()
    if method == "group_median":
        for column in usable:
            medians, overall = group_medians(train, column)
            groups = apply[GROUP_COLUMN] if GROUP_COLUMN in apply.columns else pd.Series(None, index=apply.index)
            result[column] = numeric(apply[column]).fillna(groups.map(medians).astype(float).fillna(overall))
        return result
    if method in ("mean", "median"):
        for column in usable:
            values = numeric(train[column])
            fill = values.mean() if method == "mean" else values.median()
            result[column] = numeric(apply[column]).fillna(fill)
        return result
    if method in ("knn", "mice"):
        imputer = KNNImputer(n_neighbors=5) if method == "knn" else IterativeImputer(max_iter=MICE_MAX_ITER, random_state=seed)
        train_block = pd.DataFrame({c: numeric(train[c]) for c in usable})
        apply_block = pd.DataFrame({c: numeric(apply[c]) for c in usable})
        imputer.fit(train_block)
        result[usable] = imputer.transform(apply_block)
        return result
    raise ValueError(f"Unsupported method '{method}'")


def _one_replicate(
    b: int,
    frames: dict[str, pd.DataFrame],
    plan: dict[str, dict[str, str]],
    feature_columns: dict[str, list[str]],
    seed: int,
) -> dict[str, pd.DataFrame]:
    """Predictions of one bootstrap replicate for every planned (source, nutrient)."""
    rng = np.random.default_rng(seed + b)
    replicate_seed = seed + b
    resampled = {source: _resample(frame, rng) for source, frame in frames.items()}

    forest_fits: dict[str, object] = {}

    def forest(source: str):
        if source not in forest_fits:
            forest_fits[source] = fit_random_forest_imputer(resampled[source], random_state=replicate_seed)
        return forest_fits[source]

    predictions = {}
    for source, nutrient_methods in plan.items():
        out = frames[source][["food_id"]].copy()
        for method in sorted(set(nutrient_methods.values())):
            targets = [n for n, m in nutrient_methods.items() if m == method]
            if method == "missforest":
                predicted = apply_fitted_imputer(forest(source), frames[source], targets)
            elif method == "crossdb":
                predicted = apply_fitted_imputer(forest("TKPI"), frames[source], targets)
            else:
                predicted = _fit_apply(method, resampled[source], frames[source], feature_columns[source], replicate_seed)
            for target in targets:
                out[target] = predicted[target] if target in predicted.columns else np.nan
        predictions[source] = out
    return predictions


def _predictions_for_missing(original: pd.DataFrame, predicted: pd.DataFrame, columns: list[str]) -> np.ndarray:
    """Matrix (rows x columns) of predictions, NaN where the cell was observed or not predicted."""
    out = np.full((len(original), len(columns)), np.nan)
    for j, column in enumerate(columns):
        missing = numeric(original[column]).isna().to_numpy()
        if column in predicted.columns:
            values = numeric(predicted[column]).to_numpy()
            # A replicate whose resample had no observed value for `column`
            # leaves it unimputed; that replicate then simply does not count.
            out[missing, j] = np.where(np.isnan(values[missing]), np.nan, values[missing])
    return out


def run_bootstrap(
    frames: dict[str, pd.DataFrame],
    plan: dict[str, dict[str, str]],
    config: BootstrapConfig,
) -> pd.DataFrame:
    """Long table of per-cell bootstrap statistics for every originally missing cell.

    `plan` maps source -> {nutrient: method}; methods are missforest, crossdb
    (TKPI fit applied to that source), mice, knn, group_median, median and mean. Baseline
    methods use the source's observed columns as their feature space, exactly
    as in Stage 3.
    """
    feature_columns = {source: _observed(frame, IMPUTATION_NUTRIENT_FIELDS) for source, frame in frames.items()}
    replicates = Parallel(n_jobs=config.n_jobs, verbose=5)(
        delayed(_one_replicate)(b, frames, plan, feature_columns, config.seed) for b in range(config.n_boot)
    )

    out = []
    for source, nutrient_methods in plan.items():
        original = frames[source]
        columns = list(nutrient_methods)
        stack = np.stack([_predictions_for_missing(original, rep[source], columns) for rep in replicates])
        for j, column in enumerate(columns):
            missing = numeric(original[column]).isna().to_numpy()
            if not missing.any():
                continue
            cells = stack[:, missing, j]
            with np.errstate(all="ignore"):
                out.append(
                    pd.DataFrame(
                        {
                            "source": source,
                            "food_id": original.loc[missing, "food_id"].to_numpy(),
                            "nutrient": column,
                            "method": nutrient_methods[column],
                            "n_boot": np.sum(~np.isnan(cells), axis=0),
                            "boot_mean": np.nanmean(cells, axis=0),
                            "boot_sd": np.nanstd(cells, axis=0, ddof=1),
                            "ci_low": np.nanpercentile(cells, 2.5, axis=0),
                            "ci_high": np.nanpercentile(cells, 97.5, axis=0),
                        }
                    )
                )
    return pd.concat(out, ignore_index=True)


MIN_CELLS_TO_FLAG = 5


def summarise_uncertainty(cells: pd.DataFrame, observed_scale: pd.Series, threshold: float) -> pd.DataFrame:
    """Per source x nutrient: median relative bootstrap sd and a high-uncertainty flag.

    relative_sd = boot_sd / spread of the observed values of that nutrient in
    that source (see robust_scale), i.e. how wide the imputation spread is
    compared with the nutrient's own natural spread. A nutrient is flagged
    when its median relative_sd exceeds `threshold` and it has at least
    MIN_CELLS_TO_FLAG imputed cells.
    """
    cells = cells.copy()
    key = list(zip(cells["source"], cells["nutrient"]))
    cells["relative_sd"] = cells["boot_sd"].to_numpy() / np.array([observed_scale.get(k, np.nan) for k in key])
    cells["ci_width"] = cells["ci_high"] - cells["ci_low"]
    summary = (
        cells.groupby(["source", "nutrient", "method"])
        .agg(
            n_imputed=("food_id", "size"),
            median_boot_sd=("boot_sd", "median"),
            median_ci_width=("ci_width", "median"),
            median_relative_sd=("relative_sd", "median"),
            p90_relative_sd=("relative_sd", lambda s: s.quantile(0.9)),
        )
        .reset_index()
    )
    summary["high_uncertainty"] = (summary["median_relative_sd"] > threshold) & (summary["n_imputed"] >= MIN_CELLS_TO_FLAG)
    return summary
