"""Baseline (mean / median) imputation methods.

Each function operates only on the given `columns`, fit-and-transform on a
single source's own data (no cross-source leakage between TKPI and MyFCD),
and leaves every other column in the DataFrame unchanged.
"""

from __future__ import annotations

import pandas as pd

from src.cleaning.normalizers import is_missing


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
