"""Baseline (mean / median / KNN / MICE) imputation methods.

Each function operates only on the given `columns`, fit-and-transform on a
single source's own data (no cross-source leakage between TKPI and MyFCD),
and leaves every other column in the DataFrame unchanged.
"""

from __future__ import annotations

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
