"""Tests for src.integration.database_merge."""

import pandas as pd

from src.integration.database_merge import merge_identical
from src.schema.nutrition_schema import NUTRIENT_FIELDS


def _repo():
    rows = []
    for food_id, source, name in [("tkpi_1", "TKPI", "Madu"), ("myfcd_1", "MyFCD", "HONEY"), ("myfcd_2", "MyFCD", "OTHER")]:
        row = {"food_id": food_id, "source": source, "food_name_original": name}
        row.update({n: 1.0 for n in NUTRIENT_FIELDS})
        rows.append(row)
    repo = pd.DataFrame(rows)
    repo.loc[1, ["protein_g", "fat_g"]] = [9.0, 5.0]
    return repo


def _provenance(repo):
    rows = []
    for food_id, source in zip(repo["food_id"], repo["source"]):
        for n in NUTRIENT_FIELDS:
            rows.append({"food_id": food_id, "nutrient": n, "value_source": f"measured_{source}"})
    prov = pd.DataFrame(rows)
    # TKPI protein was imputed, so MyFCD's measured value should replace it
    prov.loc[(prov.food_id == "tkpi_1") & (prov.nutrient == "protein_g"), "value_source"] = "imputed:missforest"
    return prov


def test_identical_pair_is_merged_with_tkpi_as_reference():
    repo = _repo()
    links = pd.DataFrame(
        [
            {"tkpi_food_id": "tkpi_1", "myfcd_food_id": "myfcd_1", "match_level": "identik"},
            {"tkpi_food_id": "tkpi_1", "myfcd_food_id": "myfcd_2", "match_level": "berbeda"},
        ]
    )
    integrated, provenance, conflicts = merge_identical(repo, _provenance(repo), links)

    assert set(integrated["food_id"]) == {"tkpi_1", "myfcd_2"}  # myfcd_1 merged, myfcd_2 kept
    merged = integrated.set_index("food_id").loc["tkpi_1"]
    assert merged["protein_g"] == 9.0  # imputed TKPI -> measured MyFCD
    assert merged["fat_g"] == 1.0  # both measured -> TKPI wins
    assert merged["linked_myfcd_food_id"] == "myfcd_1"
    prov = provenance.set_index(["food_id", "nutrient"])["value_source"]
    assert prov[("tkpi_1", "protein_g")] == "measured_MyFCD"
    assert "myfcd_1" not in set(provenance["food_id"])
    assert set(conflicts.loc[conflicts["nutrient"] == "fat_g", "myfcd_value"]) == {5.0}
