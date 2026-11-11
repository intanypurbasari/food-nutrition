"""Moisture adjustment of values borrowed from another food composition table.

TKPI guideline (Kementerian Kesehatan RI, 2017, *Pedoman Metode Melengkapi
Nilai Gizi Bahan Makanan pada TKPI*, section 2.3, pp. 11-12): when the water
content of the target food and of the reference food differ by more than 10%,
relative to the reference,

    |water_target - water_reference| / water_reference x 100 > 10,

a nutrient value may not be adopted directly; it is converted on a dry-matter
(solids) basis,

    value_target = value_reference x (100 - water_target) / (100 - water_reference).

Below the threshold the reference value is adopted unchanged. Borrowed values
"harus disesuaikan/dikontrol terhadap kadar air" (p. 3), and the water, fat and
protein of both matched foods must be documented (chapter III).
"""

from __future__ import annotations

import math

MOISTURE_THRESHOLD_PCT = 10.0


def moisture_adjustment(water_target: float, water_reference: float, threshold: float = MOISTURE_THRESHOLD_PCT) -> tuple[float, float, str]:
    """Return (factor, water_diff_pct, rule) for a value borrowed from the reference food.

    rule is "direct" (difference <= threshold, factor 1), "dry_matter" (factor
    applied) or "no_water_data" (a water content is unknown, or the reference
    has no solids, so the value is adopted unchanged).
    """
    if any(v is None or math.isnan(v) for v in (water_target, water_reference)):
        return 1.0, float("nan"), "no_water_data"
    if water_target == water_reference:
        diff = 0.0
    elif water_reference == 0:
        diff = float("inf")  # e.g. an oil as reference: any water in the target exceeds the threshold
    else:
        diff = abs(water_target - water_reference) / water_reference * 100
    if diff <= threshold:
        return 1.0, diff, "direct"
    if water_reference >= 100:
        return 1.0, diff, "no_water_data"
    return (100 - water_target) / (100 - water_reference), diff, "dry_matter"
