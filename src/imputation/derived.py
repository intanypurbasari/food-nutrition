"""Values calculated from other nutrients instead of imputed.

Energy follows the TKPI guideline (Kementerian Kesehatan RI, 2017,
*Pedoman Metode Melengkapi Nilai Gizi Bahan Makanan pada TKPI*, p. 9): an
energy value may not be imputed or borrowed from a reference source; it must
be calculated from the food's carbohydrate, fat and protein. The general
Atwater factors 4/9/4 kcal/g reproduce the measured energy of both sources
(median |difference| 0.4 kcal in TKPI, 0.0 kcal in MyFCD), so they are the
factors the tables themselves use, with carbohydrate as reported (by
difference).
"""

from __future__ import annotations

import pandas as pd

ENERGY_COLUMN = "energy_kcal"
ATWATER_FACTORS = {"protein_g": 4.0, "fat_g": 9.0, "carbohydrate_g": 4.0}
ATWATER_METHOD = "atwater"


def atwater_energy(frame: pd.DataFrame) -> pd.Series:
    """Energy (kcal/100 g) from protein, fat and carbohydrate; NaN where a component is missing."""
    total = pd.Series(0.0, index=frame.index)
    for column, factor in ATWATER_FACTORS.items():
        total = total + pd.to_numeric(frame[column], errors="coerce") * factor
    return total.round(1)


def fill_energy(frame: pd.DataFrame, missing: pd.Series) -> pd.DataFrame:
    """Return `frame` with energy recalculated on the rows where `missing` is True.

    `frame` must already hold the final (measured or imputed) macronutrients;
    measured energy values are left untouched.
    """
    out = frame.copy()
    out[ENERGY_COLUMN] = pd.to_numeric(out[ENERGY_COLUMN], errors="coerce")
    rows = missing.reindex(out.index, fill_value=False).astype(bool)
    out.loc[rows, ENERGY_COLUMN] = atwater_energy(out.loc[rows])
    return out
