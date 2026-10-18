"""Final TKPI + MyFCD integration (last step of the sub-study workflow).

Runs after imputation, vitamin A and the USDA-only nutrients. Inputs are the
stacked repository (one row per source food) plus the provenance of every
value; output is one row per distinct food:

- Pairs marked ``identik`` in tkpi_myfcd_links_curated.csv are merged into
  the TKPI row (TKPI is the reference). Per nutrient: a value measured in
  TKPI wins; otherwise a value measured in MyFCD; otherwise TKPI's imputed
  value. Only identical foods are merged (same food and preparation), in
  line with FAO/INFOODS food-matching practice; similar or different pairs
  stay separate rows.
- Every other food from either database is kept as its own row.
- Each cell gets a provenance label (measured_TKPI, measured_MyFCD,
  imputed:<method>, transfer_TKPI, or the vitamin A / USDA source).
"""

from __future__ import annotations

import pandas as pd

from src.cleaning.normalizers import compute_completeness_score, compute_missing_nutrient_count, is_missing
from src.schema.nutrition_schema import NUTRIENT_FIELDS, USDA_NUTRIENT_FIELDS

MERGE_LEVEL = "identik"


def _measured(clean: pd.DataFrame) -> pd.DataFrame:
    """Boolean frame (food_id x nutrient): value observed in the cleaned source data."""
    columns = [c for c in NUTRIENT_FIELDS if c in clean.columns]
    return clean.set_index("food_id")[columns].apply(lambda s: ~s.apply(is_missing))


def cell_provenance(
    repository: pd.DataFrame,
    measured: pd.DataFrame,
    selection: pd.DataFrame,
    vitamin_a: pd.DataFrame,
    usda: pd.DataFrame,
) -> pd.DataFrame:
    """Long table food_id x nutrient -> value_source for the stacked repository."""
    vitamin_a = vitamin_a.set_index("food_id")["vitamin_a_mcg_source"]
    usda = usda.set_index(["food_id", "nutrient"])["value_source"]
    rows = []
    for row in repository.itertuples(index=False):
        for nutrient in NUTRIENT_FIELDS + USDA_NUTRIENT_FIELDS:
            if nutrient == "vitamin_a_mcg":
                label = f"vitamin_a:{vitamin_a.get(row.food_id, 'unresolved')}"
            elif nutrient in USDA_NUTRIENT_FIELDS:
                label = usda.get((row.food_id, nutrient), "unresolved")
            elif row.food_id in measured.index and bool(measured.at[row.food_id, nutrient]):
                label = f"measured_{row.source}"
            elif (row.source, nutrient) in selection.index:
                method = selection.loc[(row.source, nutrient), "method"]
                label = "transfer_TKPI" if method == "crossdb" else f"imputed:{method}"
            else:
                label = "unresolved"
            rows.append({"food_id": row.food_id, "nutrient": nutrient, "value_source": label})
    return pd.DataFrame(rows)


def merge_identical(
    repository: pd.DataFrame, provenance: pd.DataFrame, links: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Merge identical TKPI-MyFCD pairs; return (integrated, provenance, conflicts)."""
    pairs = links[links["match_level"] == MERGE_LEVEL]
    repo = repository.set_index("food_id")
    prov = provenance.set_index(["food_id", "nutrient"])["value_source"].to_dict()

    conflicts = []
    for pair in pairs.itertuples(index=False):
        tkpi_id, myfcd_id = pair.tkpi_food_id, pair.myfcd_food_id
        for nutrient in NUTRIENT_FIELDS:
            if nutrient == "vitamin_a_mcg":
                continue
            tkpi_label, myfcd_label = prov[(tkpi_id, nutrient)], prov[(myfcd_id, nutrient)]
            tkpi_value, myfcd_value = repo.at[tkpi_id, nutrient], repo.at[myfcd_id, nutrient]
            if tkpi_label == "measured_TKPI" and myfcd_label == "measured_MyFCD":
                conflicts.append(
                    {"tkpi_food_id": tkpi_id, "myfcd_food_id": myfcd_id, "food_name": repo.at[tkpi_id, "food_name_original"],
                     "nutrient": nutrient, "tkpi_value": tkpi_value, "myfcd_value": myfcd_value}
                )
            elif tkpi_label != "measured_TKPI" and myfcd_label == "measured_MyFCD":
                repo.at[tkpi_id, nutrient] = myfcd_value
                prov[(tkpi_id, nutrient)] = "measured_MyFCD"
        repo.at[tkpi_id, "linked_myfcd_food_id"] = myfcd_id

    merged_myfcd = set(pairs["myfcd_food_id"])
    integrated = repo.drop(index=list(merged_myfcd)).reset_index()
    records = integrated.to_dict("records")
    integrated["missing_nutrient_count"] = [compute_missing_nutrient_count(r) for r in records]
    integrated["completeness_score"] = [compute_completeness_score(r) for r in records]

    provenance_out = pd.DataFrame(
        [{"food_id": f, "nutrient": n, "value_source": v} for (f, n), v in prov.items() if f not in merged_myfcd]
    )
    conflicts = pd.DataFrame(conflicts)
    if not conflicts.empty:
        conflicts["abs_diff"] = (conflicts["tkpi_value"] - conflicts["myfcd_value"]).abs()
        base = conflicts[["tkpi_value", "myfcd_value"]].abs().max(axis=1)
        conflicts["rel_diff"] = (conflicts["abs_diff"] / base.where(base > 0)).round(4)
    return integrated, provenance_out, conflicts
