"""Hold-out evaluation of imputation methods (Stage 4, Bab 2.7).

For each source, a fraction of the *observed* cells of every nutrient is
hidden, each method imputes the masked frame, and the imputed values are
compared with the hidden true values. This is the accuracy counterpart of
the descriptive statistics in reports/imputation_method_comparison.csv.

Metrics per (source, nutrient, method), pooled over the held-out cells of
all repeats:
- RMSE  = sqrt(mean((imputed - true)^2))
- nRMSE = RMSE / sd(true held-out values), the per-variable form of the
  normalised RMSE used by Stekhoven & Buhlmann (2012) for MissForest. 1.0
  means no better than predicting the held-out mean; lower is better.
- MAE   = mean(|imputed - true|)
Pooling keeps nRMSE stable when one repeat happens to hide near-identical
values (sd close to 0); the spread across repeats is reported separately.

Each source is masked and imputed on its own, as in Stage 3. For MyFCD the
cross-database transfer (imputer fit on the full TKPI, applied to the masked
MyFCD) is evaluated on the same masks as the within-MyFCD methods, so the two
can be compared nutrient by nutrient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.cleaning.normalizers import is_missing

ImputeFn = Callable[[pd.DataFrame, list[str]], pd.DataFrame]


@dataclass(frozen=True)
class HoldoutConfig:
    fraction: float = 0.15
    repeats: int = 3
    seed: int = 42
    # Nutrients with fewer observed cells than this are not evaluated: masking
    # them would leave too little to train on and too little to score.
    min_observed: int = 10


def _numeric(series: pd.Series) -> pd.Series:
    return series.apply(lambda value: np.nan if is_missing(value) else value).astype(float)


def make_masks(df: pd.DataFrame, columns: list[str], fraction: float, rng: np.random.Generator, min_observed: int) -> dict[str, pd.Index]:
    """Pick, per column, a random `fraction` of observed rows to hide."""
    masks: dict[str, pd.Index] = {}
    for column in columns:
        observed = df.index[_numeric(df[column]).notna()]
        if len(observed) < min_observed:
            continue
        size = max(1, int(round(fraction * len(observed))))
        masks[column] = pd.Index(rng.choice(observed, size=size, replace=False))
    return masks


def apply_masks(df: pd.DataFrame, masks: dict[str, pd.Index]) -> pd.DataFrame:
    masked = df.copy()
    for column, rows in masks.items():
        masked[column] = _numeric(masked[column])
        masked.loc[rows, column] = np.nan
    return masked


def score(true: pd.Series, imputed: pd.Series) -> dict[str, float]:
    true = true.astype(float)
    imputed = imputed.astype(float)
    error = imputed - true
    rmse = float(np.sqrt(np.mean(error**2)))
    sd = float(np.std(true, ddof=0))
    return {
        "rmse": rmse,
        "nrmse": rmse / sd if sd > 0 else float("nan"),
        "mae": float(np.mean(np.abs(error))),
    }


def evaluate_source(
    source: str,
    df: pd.DataFrame,
    columns: list[str],
    methods: dict[str, ImputeFn],
    config: HoldoutConfig,
    log: Callable[[str], None] = print,
) -> pd.DataFrame:
    """Run every method on `repeats` independent masks of `df`; one row per held-out cell."""
    rows = []
    for repeat in range(config.repeats):
        rng = np.random.default_rng(config.seed + repeat)
        masks = make_masks(df, columns, config.fraction, rng, config.min_observed)
        masked = apply_masks(df, masks)
        target_columns = list(masks)
        for method, impute in methods.items():
            log(f"[HOLDOUT] {source} repeat {repeat + 1}/{config.repeats}: {method}")
            imputed = impute(masked, target_columns)
            for column, hidden_rows in masks.items():
                if column not in imputed.columns:
                    continue
                predicted = _numeric(imputed.loc[hidden_rows, column])
                if predicted.isna().any():
                    # Method could not fill this column (e.g. no predictor signal).
                    continue
                rows.append(
                    pd.DataFrame(
                        {
                            "source": source,
                            "nutrient": column,
                            "method": method,
                            "repeat": repeat + 1,
                            "food_id": df.loc[hidden_rows, "food_id"].to_numpy(),
                            "true": _numeric(df.loc[hidden_rows, column]).to_numpy(),
                            "imputed": predicted.to_numpy(),
                        }
                    )
                )
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarise(cells: pd.DataFrame, n_observed: dict[tuple[str, str], int]) -> pd.DataFrame:
    """Pooled metrics per source x nutrient x method, plus the best method per nutrient (lowest nRMSE)."""
    records = []
    for (source, nutrient, method), block in cells.groupby(["source", "nutrient", "method"]):
        per_repeat = [score(r["true"], r["imputed"])["nrmse"] for _, r in block.groupby("repeat")]
        records.append(
            {
                "source": source,
                "nutrient": nutrient,
                "method": method,
                "n_observed": n_observed.get((source, nutrient)),
                "n_holdout_cells": len(block),
                **score(block["true"], block["imputed"]),
                "nrmse_repeat_sd": float(np.nanstd(per_repeat, ddof=1)) if len(per_repeat) > 1 else float("nan"),
            }
        )
    summary = pd.DataFrame(records)
    # nRMSE is undefined when every held-out value is identical (sd = 0); RMSE breaks those ties.
    best = (
        summary.sort_values(["nrmse", "rmse"], na_position="last")
        .drop_duplicates(["source", "nutrient"])[["source", "nutrient", "method"]]
        .rename(columns={"method": "best_method"})
    )
    return summary.merge(best, on=["source", "nutrient"], how="left")
