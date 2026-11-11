"""Tests for src.imputation.derived (energy by Atwater, TKPI guideline)."""

import numpy as np
import pandas as pd

from src.imputation.derived import atwater_energy, fill_energy


def test_atwater_energy_uses_4_9_4():
    frame = pd.DataFrame({"protein_g": [10.0], "fat_g": [5.0], "carbohydrate_g": [20.0]})
    assert atwater_energy(frame).iloc[0] == 4 * 10 + 9 * 5 + 4 * 20


def test_fill_energy_only_replaces_missing_rows():
    frame = pd.DataFrame(
        {"energy_kcal": [100.0, np.nan], "protein_g": [1.0, 2.0], "fat_g": [1.0, 1.0], "carbohydrate_g": [1.0, 3.0]}
    )
    filled = fill_energy(frame, frame["energy_kcal"].isna())
    assert filled["energy_kcal"].tolist() == [100.0, 4 * 2 + 9 * 1 + 4 * 3]
