from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from src.schema.nutrition_schema import NutritionRecord


FIXTURE = Path(__file__).parent / "fixtures" / "sample_fixture_tkpi.csv"


def test_schema_accepts_valid_fixture_row():
    row = pd.read_csv(FIXTURE).iloc[0].drop(labels=["fixture_label"]).to_dict()
    record = NutritionRecord(**row)
    assert record.food_id == "tkpi_0001"
    assert record.source == "TKPI"


def test_schema_rejects_invalid_type():
    row = pd.read_csv(FIXTURE).iloc[0].drop(labels=["fixture_label"]).to_dict()
    row["energy_kcal"] = "not-a-number"
    with pytest.raises(ValidationError):
        NutritionRecord(**row)
