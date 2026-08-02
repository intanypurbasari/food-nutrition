"""Tests for src.imputation.baselines."""

from pathlib import Path

import pandas as pd

from src.imputation.baselines import knn_impute, mean_impute, median_impute, mice_impute

FIXTURE = Path(__file__).parent / "fixtures" / "sample_fixture_enriched_tkpi.csv"

# water_g in the fixture: [50, 60, 70, None, 80, 90, None, 40, 55, 65]
# present values sorted: [40, 50, 55, 60, 65, 70, 80, 90] -> mean 63.75, median 62.5
WATER_G_MEAN = 63.75
WATER_G_MEDIAN = 62.5


def _load_fixture() -> pd.DataFrame:
    return pd.read_csv(FIXTURE).drop(columns=["fixture_label"])


def test_mean_impute_fills_known_value_and_leaves_other_columns_untouched():
    df = _load_fixture()
    result = mean_impute(df, ["water_g"])
    assert result.loc[3, "water_g"] == WATER_G_MEAN
    assert result.loc[6, "water_g"] == WATER_G_MEAN
    # non-targeted column (carotene_total_mcg) passes through unchanged
    assert result["carotene_total_mcg"].isna().sum() == df["carotene_total_mcg"].isna().sum()
    # original df is not mutated
    assert df["water_g"].isna().sum() == 2


def test_median_impute_fills_known_value():
    df = _load_fixture()
    result = median_impute(df, ["water_g"])
    assert result.loc[3, "water_g"] == WATER_G_MEDIAN
    assert result.loc[6, "water_g"] == WATER_G_MEDIAN


def test_knn_impute_leaves_no_missing_in_targeted_columns():
    df = _load_fixture()
    columns = ["water_g", "iron_mg", "calcium_mg"]
    result = knn_impute(df, columns)
    assert result[columns].isna().sum().sum() == 0
    assert result["carotene_total_mcg"].isna().sum() == df["carotene_total_mcg"].isna().sum()


def test_mice_impute_is_reproducible_given_fixed_seed():
    df = _load_fixture()
    columns = ["water_g", "iron_mg", "calcium_mg", "phosphorus_mg"]
    result_a = mice_impute(df, columns, random_state=42)
    result_b = mice_impute(df, columns, random_state=42)
    pd.testing.assert_frame_equal(result_a[columns], result_b[columns])
    assert result_a[columns].isna().sum().sum() == 0
