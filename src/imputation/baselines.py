"""Baseline (mean / median / KNN / MICE / SoftImpute) imputation methods.

Each function operates only on the given `columns`, fit-and-transform on a
single source's own data (no cross-source leakage between TKPI and MyFCD),
and leaves every other column in the DataFrame unchanged.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401  (required by IterativeImputer)
from sklearn.impute import IterativeImputer, KNNImputer

from config.imputation_settings import RANDOM_SEED
from src.cleaning.normalizers import is_missing

MICE_MAX_ITER = 10


def _to_numeric_with_missing(series: pd.Series) -> pd.Series:
    """Coerce a column to numeric, treating repo-canonical missing tokens as NaN."""
    return series.apply(lambda value: None if is_missing(value) else value).astype(float)


def mean_impute(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Fill missing values in `columns` with each column's own mean.

    Only touches `columns`; every other column passes through unchanged.
    Must be called separately per source (TKPI, MyFCD) - never impute one
    source's column using another source's statistics.
    """
    result = df.copy()
    for column in columns:
        if column not in result.columns:
            continue
        numeric = _to_numeric_with_missing(result[column])
        result[column] = numeric.fillna(numeric.mean())
    return result


def median_impute(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Fill missing values in `columns` with each column's own median.

    Only touches `columns`; every other column passes through unchanged.
    Must be called separately per source (TKPI, MyFCD) - never impute one
    source's column using another source's statistics.
    """
    result = df.copy()
    for column in columns:
        if column not in result.columns:
            continue
        numeric = _to_numeric_with_missing(result[column])
        result[column] = numeric.fillna(numeric.median())
    return result


GROUP_COLUMN = "category_normalized"
MIN_GROUP_OBSERVED = 3


def group_medians(train: pd.DataFrame, column: str, min_group: int = MIN_GROUP_OBSERVED) -> tuple[dict, float]:
    """Per food-group medians of `column` (groups with >= min_group observed values) and the overall median."""
    values = _to_numeric_with_missing(train[column])
    groups = train[GROUP_COLUMN] if GROUP_COLUMN in train.columns else pd.Series(None, index=train.index)
    by_group = values.groupby(groups).agg(["median", "count"])
    medians = by_group.loc[by_group["count"] >= min_group, "median"].to_dict()
    return medians, values.median()


def group_median_impute(df: pd.DataFrame, columns: list[str], min_group: int = MIN_GROUP_OBSERVED) -> pd.DataFrame:
    """Fill missing values in `columns` with the median of the food's own group (category_normalized).

    Groups with fewer than `min_group` observed values for a column fall back
    to the column's overall median. Unlike plain median imputation this keeps
    between-group differences, e.g. retinol for meat versus vegetables. Only
    touches `columns`; must be called separately per source.
    """
    result = df.copy()
    for column in columns:
        if column not in result.columns:
            continue
        medians, overall = group_medians(df, column, min_group)
        numeric = _to_numeric_with_missing(result[column])
        groups = result[GROUP_COLUMN] if GROUP_COLUMN in result.columns else pd.Series(None, index=result.index)
        fill = groups.map(medians).astype(float).fillna(overall)
        result[column] = numeric.fillna(fill)
    return result


def knn_impute(df: pd.DataFrame, columns: list[str], n_neighbors: int = 5) -> pd.DataFrame:
    """Fill missing values in `columns` using multivariate KNN imputation.

    Uses sklearn.impute.KNNImputer fit_transform restricted to `columns` only
    (non-nutrient columns like food_id/category never influence or receive
    neighbor-based fills). Only touches `columns`; every other column passes
    through unchanged. Must be called separately per source, same contract
    as mean_impute/median_impute.

    KNNImputer has no random_state parameter - given fixed input data and a
    fixed k (n_neighbors), its output is deterministic, so RANDOM_SEED from
    config is not applicable here.
    """
    result = df.copy()
    present_columns = [column for column in columns if column in result.columns]
    if not present_columns:
        return result

    numeric_block = pd.DataFrame(
        {column: _to_numeric_with_missing(result[column]) for column in present_columns}
    )
    imputer = KNNImputer(n_neighbors=n_neighbors)
    imputed_values = imputer.fit_transform(numeric_block)
    result[present_columns] = imputed_values
    return result


def mice_impute(df: pd.DataFrame, columns: list[str], random_state: int | None = None) -> pd.DataFrame:
    """Fill missing values in `columns` via Multiple Imputation by Chained Equations.

    Uses sklearn.impute.IterativeImputer (which requires importing
    sklearn.experimental.enable_iterative_imputer first), restricted to
    `columns` only. Only touches `columns`; every other column passes
    through unchanged. Must be called separately per source, same contract
    as the other baseline functions.

    `random_state` defaults to config.imputation_settings.RANDOM_SEED when
    None, for reproducibility. Uses max_iter=MICE_MAX_ITER (10); convergence
    is not separately verified here - that belongs to Stage 4 evaluation,
    not this function.
    """
    if random_state is None:
        random_state = RANDOM_SEED

    result = df.copy()
    present_columns = [column for column in columns if column in result.columns]
    if not present_columns:
        return result

    numeric_block = pd.DataFrame(
        {column: _to_numeric_with_missing(result[column]) for column in present_columns}
    )
    imputer = IterativeImputer(max_iter=MICE_MAX_ITER, random_state=random_state)
    imputed_values = imputer.fit_transform(numeric_block)
    result[present_columns] = imputed_values
    return result


SOFTIMPUTE_MAX_RANK = 5
SOFTIMPUTE_SHRINKAGE_DIVISOR = 50.0
SOFTIMPUTE_TOLERANCE = 1e-3
SOFTIMPUTE_MAX_ITER = 100


def softimpute_impute(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Fill missing values in `columns` by nuclear-norm matrix completion (SoftImpute).

    Mazumder, Hastie and Tibshirani (2010), in the configuration Indriani et al.
    (2026, Array 32:101428) characterised on TKPI: columns MinMax-scaled on their
    observed values, missing cells initialised at 0, then iterative
    soft-thresholded SVD with shrinkage = largest singular value / 50, rank
    capped at 5, until the relative change of the filled cells is below 1e-3.
    Values are returned to the original scale and clipped at 0. Columns with
    no observed value are left untouched. Deterministic (full SVD, no random
    state). Same contract as the other baseline functions.
    """
    result = df.copy()
    present = [c for c in columns if c in result.columns]
    block = pd.DataFrame({c: _to_numeric_with_missing(result[c]) for c in present})
    usable = [c for c in present if block[c].notna().any()]
    if not usable:
        return result
    x = block[usable].to_numpy(dtype=float)
    lo, hi = np.nanmin(x, axis=0), np.nanmax(x, axis=0)
    span = np.where(hi > lo, hi - lo, 1.0)
    scaled = (x - lo) / span
    missing = np.isnan(scaled)
    filled = np.where(missing, 0.0, scaled)
    shrinkage = np.linalg.svd(filled, compute_uv=False)[0] / SOFTIMPUTE_SHRINKAGE_DIVISOR
    for _ in range(SOFTIMPUTE_MAX_ITER):
        u, s, vt = np.linalg.svd(filled, full_matrices=False)
        s = np.maximum(s[:SOFTIMPUTE_MAX_RANK] - shrinkage, 0.0)
        rank = int((s > 0).sum())
        reconstruction = (u[:, :rank] * s[:rank]) @ vt[:rank]
        old = filled[missing]
        new = reconstruction[missing]
        filled[missing] = new
        norm = np.sqrt(np.sum(old ** 2))
        if norm > 0 and np.sqrt(np.sum((old - new) ** 2)) / norm < SOFTIMPUTE_TOLERANCE:
            break
    values = np.clip(filled * span + lo, 0.0, None)
    result[usable] = np.where(missing, values, x)
    return result
