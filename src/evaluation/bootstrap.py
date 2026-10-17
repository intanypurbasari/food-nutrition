"""Bootstrap uncertainty of imputed cells (Stage 4, Bab 2.6).

For b = 1..B the rows of each source are resampled with replacement, the
same MissForest imputer as Stage 3 is fit on the resample, and the fitted
imputer is applied to the original (unresampled) frame. Every originally
missing cell therefore gets B predictions; their spread is the uncertainty
of that imputed value.

Routing follows Stage 3 (availability_matrix.csv):
- TKPI: every imputed nutrient comes from TKPI's own bootstrap fit.
- MyFCD, "Imputasi internal per basis": MyFCD's own bootstrap fit.
- MyFCD, "Cross-DB transfer / USDA": the TKPI bootstrap fit of the same b,
  applied to MyFCD - so the transfer's uncertainty reflects resampling of
  its training source.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

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


def _one_replicate(
    b: int,
    tkpi: pd.DataFrame,
    myfcd: pd.DataFrame,
    tkpi_columns: list[str],
    myfcd_internal: list[str],
    myfcd_crossdb: list[str],
    seed: int,
) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed + b)
    replicate_seed = seed + b
    tkpi_fit = fit_random_forest_imputer(_resample(tkpi, rng), random_state=replicate_seed)
    myfcd_fit = fit_random_forest_imputer(_resample(myfcd, rng), random_state=replicate_seed)

    tkpi_pred = apply_fitted_imputer(tkpi_fit, tkpi, tkpi_columns)
    myfcd_pred = apply_fitted_imputer(myfcd_fit, myfcd, myfcd_internal)
    if myfcd_crossdb:
        transfer = apply_fitted_imputer(tkpi_fit, myfcd, myfcd_crossdb)
        myfcd_pred[myfcd_crossdb] = transfer[myfcd_crossdb]
    return {"TKPI": tkpi_pred, "MyFCD": myfcd_pred}


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
    tkpi: pd.DataFrame,
    myfcd: pd.DataFrame,
    tkpi_columns: list[str],
    myfcd_internal: list[str],
    myfcd_crossdb: list[str],
    config: BootstrapConfig,
) -> pd.DataFrame:
    """Long table of per-cell bootstrap statistics for every originally missing cell."""
    replicates = Parallel(n_jobs=config.n_jobs, verbose=5)(
        delayed(_one_replicate)(b, tkpi, myfcd, tkpi_columns, myfcd_internal, myfcd_crossdb, config.seed)
        for b in range(config.n_boot)
    )

    frames = []
    plan = {"TKPI": (tkpi, tkpi_columns), "MyFCD": (myfcd, myfcd_internal + myfcd_crossdb)}
    for source, (original, columns) in plan.items():
        stack = np.stack([_predictions_for_missing(original, rep[source], columns) for rep in replicates])
        for j, column in enumerate(columns):
            missing = numeric(original[column]).isna().to_numpy()
            if not missing.any():
                continue
            cells = stack[:, missing, j]
            with np.errstate(all="ignore"):
                frame = pd.DataFrame(
                    {
                        "source": source,
                        "food_id": original.loc[missing, "food_id"].to_numpy(),
                        "nutrient": column,
                        "method": "crossdb" if source == "MyFCD" and column in myfcd_crossdb else "missforest",
                        "n_boot": np.sum(~np.isnan(cells), axis=0),
                        "boot_mean": np.nanmean(cells, axis=0),
                        "boot_sd": np.nanstd(cells, axis=0, ddof=1),
                        "ci_low": np.nanpercentile(cells, 2.5, axis=0),
                        "ci_high": np.nanpercentile(cells, 97.5, axis=0),
                    }
                )
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


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
