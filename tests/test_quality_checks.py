from pathlib import Path

import pandas as pd

from src.validation.quality_checks import validate_dataframe


FIXTURE = Path(__file__).parent / "fixtures" / "sample_fixture_tkpi.csv"


def test_quality_checks_detect_invalid_required_and_range():
    df = pd.read_csv(FIXTURE).drop(columns=["fixture_label"])
    df.loc[0, "food_name_original"] = ""
    df.loc[1, "energy_kcal"] = -1
    report = validate_dataframe(df, "TKPI")
    assert report["invalid_rows"] == 2
    assert report["issues_by_type"]["missing_required"] == 1
    assert report["issues_by_type"]["invalid_range"] == 1


def test_quality_checks_detect_duplicates_as_warning():
    df = pd.read_csv(FIXTURE).drop(columns=["fixture_label"])
    duplicate = df.iloc[[0]].copy()
    df = pd.concat([df, duplicate], ignore_index=True)
    report = validate_dataframe(df, "TKPI")
    assert report["duplicate_count"] == 2
    assert report["warnings_by_type"]["duplicate_food_name_normalized"] == 2
