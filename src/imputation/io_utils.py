"""Shared I/O, availability-matrix strategy-routing, and post-imputation
validation utilities for Stage 3. Every imputation method module and CLI
script depends on this module rather than reimplementing loading, routing,
or validation logic directly.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.imputation_settings import (
    MYFCD_ENRICHED_PATH,
    TKPI_ENRICHED_PATH,
    AVAILABILITY_MATRIX_PATH,
    TKPI_MYFCD_LINKS_MUTUAL_PATH,
    IMPUTATION_NUTRIENT_FIELDS,
)
from src.cleaning.normalizers import is_missing
from src.validation.quality_checks import validate_dataframe

_ENRICHED_PATHS = {"TKPI": TKPI_ENRICHED_PATH, "MyFCD": MYFCD_ENRICHED_PATH}


def load_enriched(source: str) -> pd.DataFrame:
    """Load the USDA-enriched CSV for `source` ("TKPI" or "MyFCD").

    Unlike the optional-source merge in scripts/build_repository_sample.py,
    imputation cannot silently proceed on a missing input, so this raises
    rather than returning None.
    """
    if source not in _ENRICHED_PATHS:
        raise ValueError(f"Unknown source '{source}'; expected one of {sorted(_ENRICHED_PATHS)}")

    path = _ENRICHED_PATHS[source]
    if not path.exists() or path.stat().st_size == 0:
        print(f"[IMPUTE] {source}: enriched file not found or empty at {path}")
        raise FileNotFoundError(f"Required enriched input for {source} not found: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Enriched input for {source} has no rows: {path}")
    print(f"[IMPUTE] {source}: loaded {len(df)} rows from {path.name}")
    return df


def load_availability_matrix() -> pd.DataFrame:
    """Load availability_matrix.csv, indexed by nutrient name."""
    if not AVAILABILITY_MATRIX_PATH.exists() or AVAILABILITY_MATRIX_PATH.stat().st_size == 0:
        raise FileNotFoundError(f"Availability matrix not found: {AVAILABILITY_MATRIX_PATH}")
    return pd.read_csv(AVAILABILITY_MATRIX_PATH, index_col=0)


def get_strategy(nutrient: str) -> str:
    """Return the strategi_imputasi value for `nutrient` from availability_matrix.csv.

    Raises KeyError (rather than defaulting) if the nutrient is not present
    in the routing table, i.e. any nutrient the Stage 2 availability matrix
    does not cover.
    """
    matrix = load_availability_matrix()
    if nutrient not in matrix.index:
        raise KeyError(f"No imputation strategy found for nutrient '{nutrient}' in availability_matrix.csv")
    return str(matrix.loc[nutrient, "strategi_imputasi"])


def columns_for_strategy(strategy: str) -> list[str]:
    """Return NUTRIENT_FIELDS entries whose availability-matrix strategy matches `strategy`.

    Nutrients absent from availability_matrix.csv are skipped rather than
    raising, since they simply have no Stage 2 routing decision assigned yet.
    """
    matched = []
    for nutrient in IMPUTATION_NUTRIENT_FIELDS:
        try:
            nutrient_strategy = get_strategy(nutrient)
        except KeyError:
            continue
        if nutrient_strategy == strategy:
            matched.append(nutrient)
    return matched


def load_mutual_links() -> pd.DataFrame:
    """Load the 52 mutual-best TKPI<->MyFCD row-pairing table, unchanged."""
    if not TKPI_MYFCD_LINKS_MUTUAL_PATH.exists() or TKPI_MYFCD_LINKS_MUTUAL_PATH.stat().st_size == 0:
        raise FileNotFoundError(f"Mutual links table not found: {TKPI_MYFCD_LINKS_MUTUAL_PATH}")
    return pd.read_csv(TKPI_MYFCD_LINKS_MUTUAL_PATH)


def validate_imputed_output(df: pd.DataFrame, source_name: str, targeted_columns: list[str]) -> dict:
    """Validate an imputed DataFrame's schema/range consistency and completeness.

    Wraps src.validation.quality_checks.validate_dataframe and additionally
    checks, using the repo's canonical src.cleaning.normalizers.is_missing
    semantics, that none of `targeted_columns` still contain missing values.
    """
    report = validate_dataframe(df, source_name)
    remaining_missing = {
        column: int(df[column].apply(is_missing).sum()) for column in targeted_columns if column in df.columns
    }
    report["remaining_missing_in_targeted_columns"] = remaining_missing
    return report


def write_output(df: pd.DataFrame, path: Path) -> None:
    """Write `df` to `path` as UTF-8 CSV, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"[IMPUTE] wrote {len(df)} rows to {path}")
