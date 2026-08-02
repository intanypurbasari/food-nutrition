"""Tests for src.imputation.integrate."""

from pathlib import Path

import pandas as pd

from src.imputation.baselines import mean_impute
from src.imputation.integrate import assemble_integrated

FIXTURES = Path(__file__).parent / "fixtures"
TKPI_FIXTURE = FIXTURES / "sample_fixture_enriched_tkpi.csv"
MYFCD_FIXTURE = FIXTURES / "sample_fixture_enriched_myfcd.csv"

INTERNAL_COLUMNS = [
    "water_g", "energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_g", "ash_g",
    "calcium_mg", "phosphorus_mg", "iron_mg", "sodium_mg", "potassium_mg", "copper_mg", "zinc_mg",
    "retinol_mcg", "beta_carotene_mcg", "vitamin_b1_mg", "vitamin_b2_mg", "niacin_mg", "vitamin_c_mg",
]


def _load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path).drop(columns=["fixture_label"])


def _build_sources():
    tkpi_enriched = _load(TKPI_FIXTURE)
    myfcd_enriched = _load(MYFCD_FIXTURE)

    # Simulate a fully-resolved missforest output using mean_impute (fine for
    # testing integrate.py's SELECTION logic, which doesn't care how the
    # missforest source's values were produced).
    tkpi_missforest = mean_impute(tkpi_enriched, INTERNAL_COLUMNS + ["carotene_total_mcg"])
    myfcd_missforest = mean_impute(myfcd_enriched, INTERNAL_COLUMNS)

    # Cross-db source: MyFCD's carotene_total_mcg filled with a distinct,
    # recognizable constant so we can tell it apart from the missforest source.
    myfcd_crossdb = myfcd_enriched.copy()
    myfcd_crossdb["carotene_total_mcg"] = 999.0

    tkpi_sources = {"enriched": tkpi_enriched, "missforest": tkpi_missforest}
    myfcd_sources = {"enriched": myfcd_enriched, "missforest": myfcd_missforest, "crossdb": myfcd_crossdb}
    return tkpi_sources, myfcd_sources


def test_internal_strategy_nutrient_comes_from_missforest_source():
    tkpi_sources, myfcd_sources = _build_sources()
    integrated, stats = assemble_integrated(tkpi_sources, myfcd_sources)

    tkpi_rows = integrated[integrated["source"] == "TKPI"].reset_index(drop=True)
    expected = tkpi_sources["missforest"]["iron_mg"].reset_index(drop=True)
    pd.testing.assert_series_equal(tkpi_rows["iron_mg"], expected, check_names=False)
    assert stats["iron_mg"]["strategy"] == "Imputasi internal per basis"
    assert stats["iron_mg"]["unresolved"] == 0


def test_crossdb_strategy_splits_by_source():
    tkpi_sources, myfcd_sources = _build_sources()
    integrated, stats = assemble_integrated(tkpi_sources, myfcd_sources)

    tkpi_rows = integrated[integrated["source"] == "TKPI"].reset_index(drop=True)
    myfcd_rows = integrated[integrated["source"] == "MyFCD"].reset_index(drop=True)

    # TKPI side uses its own within-database (missforest) result.
    expected_tkpi = tkpi_sources["missforest"]["carotene_total_mcg"].reset_index(drop=True)
    pd.testing.assert_series_equal(tkpi_rows["carotene_total_mcg"], expected_tkpi, check_names=False)

    # MyFCD side uses the cross-db transfer result (all 999.0 sentinel values).
    assert (myfcd_rows["carotene_total_mcg"] == 999.0).all()

    assert stats["carotene_total_mcg"]["strategy"] == "Cross-DB transfer / USDA"
    assert stats["carotene_total_mcg"]["resolved_internal"] == len(tkpi_rows)
    assert stats["carotene_total_mcg"]["resolved_crossdb"] == len(myfcd_rows)


def test_usda_borrow_nutrient_with_no_matching_column_is_unresolved_not_fabricated():
    tkpi_sources, myfcd_sources = _build_sources()
    integrated, stats = assemble_integrated(tkpi_sources, myfcd_sources)

    assert integrated["vitamin_a_mcg"].isna().all()
    assert stats["vitamin_a_mcg"]["strategy"] == "Pinjam USDA (kosong di kedua basis)"
    assert stats["vitamin_a_mcg"]["resolved_usda_borrow"] == 0
    assert stats["vitamin_a_mcg"]["unresolved"] == len(integrated)


def test_full_accounting_sums_to_total_rows_for_every_nutrient():
    tkpi_sources, myfcd_sources = _build_sources()
    integrated, stats = assemble_integrated(tkpi_sources, myfcd_sources)

    total_rows = len(integrated)
    for nutrient, entry in stats.items():
        total = entry["resolved_internal"] + entry["resolved_crossdb"] + entry["resolved_usda_borrow"] + entry["unresolved"]
        assert total == total_rows, f"{nutrient}: {entry}"
