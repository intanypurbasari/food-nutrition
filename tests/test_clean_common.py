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
