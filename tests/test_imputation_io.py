"""Tests for src.imputation.io_utils."""

from pathlib import Path

import pandas as pd
import pytest

from src.imputation import io_utils

FIXTURES = Path(__file__).parent / "fixtures"
TKPI_FIXTURE = FIXTURES / "sample_fixture_enriched_tkpi.csv"
MYFCD_FIXTURE = FIXTURES / "sample_fixture_enriched_myfcd.csv"


def test_load_enriched_happy_path(monkeypatch):
    monkeypatch.setitem(io_utils._ENRICHED_PATHS, "TKPI", TKPI_FIXTURE)
    df = io_utils.load_enriched("TKPI")
    assert len(df) == 10
    assert "food_id" in df.columns
    assert "magnesium_mg" in df.columns


def test_load_enriched_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setitem(io_utils._ENRICHED_PATHS, "TKPI", tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        io_utils.load_enriched("TKPI")


def test_get_strategy_all_three_buckets():
    assert io_utils.get_strategy("iron_mg") == "Imputasi internal per basis"
    assert io_utils.get_strategy("carotene_total_mcg") == "Cross-DB transfer / USDA"
    assert io_utils.get_strategy("vitamin_a_mcg") == "Pinjam USDA (kosong di kedua basis)"


def test_get_strategy_unknown_nutrient_raises_key_error():
    with pytest.raises(KeyError):
        io_utils.get_strategy("edible_portion_percent")


def test_columns_for_strategy_skips_unrouted_nutrients():
    internal_columns = io_utils.columns_for_strategy("Imputasi internal per basis")
    assert "iron_mg" in internal_columns
    assert "edible_portion_percent" not in internal_columns
    assert "vitamin_a_mcg" not in internal_columns


def test_load_mutual_links_has_expected_columns():
    df = io_utils.load_mutual_links()
    assert not df.empty
    assert {"tkpi_food_id", "myfcd_food_id"}.issubset(df.columns)


def test_validate_imputed_output_detects_remaining_missing():
    df = pd.DataFrame(
        {
            "food_id": ["a", "b"],
            "food_name_original": ["Food A", "Food B"],
            "source": ["TKPI", "TKPI"],
            "unit_basis": ["per 100g", "per 100g"],
            "iron_mg": [1.0, None],
        }
    )
    report = io_utils.validate_imputed_output(df, "TKPI", targeted_columns=["iron_mg"])
    assert report["remaining_missing_in_targeted_columns"]["iron_mg"] == 1
