"""Tests for src.imputation.missforest_imputer and src.imputation.cross_transfer."""

from pathlib import Path

import pandas as pd

from src.imputation.cross_transfer import cross_db_transfer_impute
from src.imputation.missforest_imputer import missforest_impute

FIXTURES = Path(__file__).parent / "fixtures"
TKPI_FIXTURE = FIXTURES / "sample_fixture_enriched_tkpi.csv"
MYFCD_FIXTURE = FIXTURES / "sample_fixture_enriched_myfcd.csv"

INTERNAL_COLUMNS = ["water_g", "iron_mg", "calcium_mg", "phosphorus_mg", "potassium_mg"]


def _load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path).drop(columns=["fixture_label"])


def test_missforest_impute_leaves_no_missing_in_targeted_columns():
    df = _load(TKPI_FIXTURE)
    result = missforest_impute(df, INTERNAL_COLUMNS, random_state=42)
    assert result[INTERNAL_COLUMNS].isna().sum().sum() == 0
    # non-targeted column (carotene_total_mcg, cross-db strategy) untouched
    assert result["carotene_total_mcg"].isna().sum() == df["carotene_total_mcg"].isna().sum()


def test_cross_db_transfer_fills_myfcd_target_without_mutating_tkpi():
    train_df = _load(TKPI_FIXTURE)
    apply_df = _load(MYFCD_FIXTURE)
    train_df_before = train_df.copy()

    result = cross_db_transfer_impute(train_df, apply_df, ["carotene_total_mcg"], random_state=42)

    assert result["carotene_total_mcg"].isna().sum() == 0
    assert len(result) == len(apply_df)
    pd.testing.assert_frame_equal(train_df, train_df_before)
