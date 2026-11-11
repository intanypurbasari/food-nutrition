"""Tests for src.imputation.borrowing (moisture adjustment, TKPI guideline 2.3)."""

import math

from src.imputation.borrowing import moisture_adjustment


def test_guideline_example_black_walnut_uses_dry_matter():
    # Pedoman TKPI contoh 1: black walnut (air 4,36) dari english walnut (air 3,645), selisih 19,62%
    factor, diff, rule = moisture_adjustment(4.36, 3.645)
    assert rule == "dry_matter"
    assert round(diff, 2) == 19.62
    assert round(0.558 * factor, 3) == 0.554  # pedoman: 0,553 (dibulatkan dari 0,5538)


def test_guideline_example_asian_pear_is_borrowed_directly():
    # Pedoman TKPI contoh 2: selisih 5,72% < 10%
    factor, diff, rule = moisture_adjustment(88.6, 83.81)
    assert (factor, rule) == (1.0, "direct")
    assert round(diff, 2) == 5.72


def test_missing_water_keeps_value():
    factor, diff, rule = moisture_adjustment(float("nan"), 50.0)
    assert (factor, rule) == (1.0, "no_water_data") and math.isnan(diff)
