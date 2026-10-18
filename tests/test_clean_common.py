"""Tests for source-specific rules in scripts.clean_common."""

import pandas as pd

from scripts.clean_common import UNRELIABLE_SOURCE_FIELDS, clean_dataframe


def _raw(source: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "food_name_original": "BISCUIT, MILK",
                "source": source,
                "notes": "asli",
                "copper_mg": 0.0001,
                "retinol_mcg": 0.0468,
                "beta_carotene_mcg": 0.0,
                "zinc_mg": 0.5983,
            },
            {"food_name_original": "CORDIAL", "source": source, "zinc_mg": 0.12},
        ]
    )


def test_unreliable_myfcd_fields_are_blanked_and_noted():
    df, summary = clean_dataframe(_raw("MyFCD"), "MyFCD", "myfcd")
    for field in UNRELIABLE_SOURCE_FIELDS["MyFCD"]:
        assert df[field].isna().all()
    assert df.loc[0, "zinc_mg"] == 0.5983
    assert df.loc[0, "notes"].startswith("asli | nilai sumber tidak andal")
    assert pd.isna(df.loc[1, "notes"])  # nothing blanked, note untouched
    assert summary["excluded_counts"] == {"copper_mg": 1, "retinol_mcg": 1, "beta_carotene_mcg": 1}


def test_other_sources_keep_those_fields():
    df, summary = clean_dataframe(_raw("TKPI"), "TKPI", "tkpi")
    assert df.loc[0, "copper_mg"] == 0.0001
    assert summary["excluded_counts"] == {}


def test_tkpi_copper_unit_error_is_divided_by_1000_and_noted():
    raw = pd.DataFrame(
        [
            {"food_name_original": "Apel", "source": "TKPI", "copper_mg": 124.2},
            {"food_name_original": "Hati", "source": "TKPI", "copper_mg": 9.5},
            {"food_name_original": "Pisang", "source": "TKPI", "copper_mg": 0.2},
        ]
    )
    df, summary = clean_dataframe(raw, "TKPI", "tkpi")
    assert abs(df.loc[0, "copper_mg"] - 0.1242) < 1e-12
    assert "124.2 -> 0.1242" in df.loc[0, "notes"]
    assert df.loc[1, "copper_mg"] == 9.5 and df.loc[2, "copper_mg"] == 0.2
    assert len(summary["unit_corrections"]) == 1
    assert [item["food_name_original"] for item in summary["review_values"]] == ["Hati"]


def test_impossible_source_cells_are_blanked_by_food_code():
    raw = pd.DataFrame(
        [{"kode_pangan": "CP006", "food_name_original": "Kacang kedelai, goreng", "source": "TKPI",
          "calcium_mg": 296, "sodium_mg": 3492, "potassium_mg": 11890, "copper_mg": 26.3, "zinc_mg": 60.0}]
    )
    df, summary = clean_dataframe(raw, "TKPI", "tkpi")
    assert df.loc[0, ["sodium_mg", "potassium_mg", "copper_mg", "zinc_mg"]].isna().all()
    assert df.loc[0, "calcium_mg"] == 296
    assert summary["unit_corrections"] == []  # blanked, not divided by 1000
