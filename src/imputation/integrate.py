"""Assembles the final "best available value per nutrient per food" dataset.

Per-nutrient source selection follows availability_matrix.csv's
strategi_imputasi routing exactly:

- "Imputasi internal per basis": value comes from the within-database
  MissForest output (Milestone 6) for that source's own data.
- "Cross-DB transfer / USDA": MyFCD rows come from the cross-database
  transfer output (Milestone 7, myfcd_imputed_crossdb.csv); TKPI rows come
  from its own within-database MissForest output, since TKPI already has
  partial real+imputed data for these nutrients.
- "Pinjam USDA (kosong di kedua basis)": value comes from the matching
  already-borrowed USDA column in *_enriched.csv IF that nutrient is one of
  the 6 columns Stage 1 actually borrowed (magnesium_mg, sugars_total_g,
  saturated_fat_g, cholesterol_mg, vitamin_b6_mg, vitamin_b12_mcg).
  vitamin_a_mcg has this strategy but is NOT among those 6 columns, so it is
  left as NaN and reported as unresolved - never fabricated.

Nutrients absent from availability_matrix.csv entirely (i.e. any nutrient
Stage 2's missingness diagnosis did not cover) are passed through from the
enriched source unchanged and reported separately as "not routed by
Stage 2", rather than silently folded into either resolved or unresolved.
(edible_portion_percent was previously the only such case, but was removed
from the schema entirely rather than left unrouted - see
src/schema/nutrition_schema.py.)
"""

from __future__ import annotations

import pandas as pd

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS, USDA_BORROWED_COLUMNS
from src.cleaning.normalizers import compute_completeness_score, compute_missing_nutrient_count, is_missing
from src.imputation import io_utils
from src.schema.nutrition_schema import schema_columns

NOT_ROUTED_LABEL = "Tidak dirutekan Stage 2 (di luar cakupan availability_matrix)"


def _missing_count(series: pd.Series) -> int:
    return int(series.apply(is_missing).sum())


def _assemble_source_nutrients(
    source_name: str, sources: dict[str, pd.DataFrame], stats: dict[str, dict[str, int]]
) -> pd.DataFrame:
    """Build the nutrient columns for one source (TKPI or MyFCD), updating `stats` in place."""
    base = sources["enriched"].copy()
    internal = sources["missforest"]
    crossdb = sources.get("crossdb")  # only present for MyFCD

    for nutrient in IMPUTATION_NUTRIENT_FIELDS:
        entry = stats.setdefault(
            nutrient,
            {"strategy": None, "resolved_internal": 0, "resolved_crossdb": 0, "resolved_usda_borrow": 0, "unresolved": 0},
        )

        try:
            strategy = io_utils.get_strategy(nutrient)
        except KeyError:
            entry["strategy"] = NOT_ROUTED_LABEL
            entry["unresolved"] += _missing_count(base[nutrient])
            continue

        entry["strategy"] = strategy

        if strategy == "Imputasi internal per basis":
            base[nutrient] = internal[nutrient]
            entry["resolved_internal"] += len(base)
        elif strategy == "Cross-DB transfer / USDA":
            if source_name == "MyFCD" and crossdb is not None:
                base[nutrient] = crossdb[nutrient]
                entry["resolved_crossdb"] += len(base)
            else:
                base[nutrient] = internal[nutrient]
                entry["resolved_internal"] += len(base)
        elif strategy == "Pinjam USDA (kosong di kedua basis)":
            if nutrient in USDA_BORROWED_COLUMNS and nutrient in base.columns:
                # Already borrowed by Stage 1; nothing further to compute.
                entry["resolved_usda_borrow"] += len(base) - _missing_count(base[nutrient])
                entry["unresolved"] += _missing_count(base[nutrient])
            else:
                entry["unresolved"] += len(base)
        else:
            raise ValueError(f"Unknown strategi_imputasi value for '{nutrient}': {strategy}")

    return base


def assemble_integrated(
    tkpi_sources: dict[str, pd.DataFrame], myfcd_sources: dict[str, pd.DataFrame]
) -> tuple[pd.DataFrame, dict[str, dict[str, int]]]:
    """Assemble the integrated dataset and a per-nutrient resolution-stats dict.

    `tkpi_sources`/`myfcd_sources` are dicts keyed by method name
    ("enriched", "missforest", and, for myfcd_sources only, "crossdb")
    mapping to that method's already-loaded DataFrame, row-aligned with the
    corresponding enriched file.
    """
    stats: dict[str, dict[str, int]] = {}

    tkpi_assembled = _assemble_source_nutrients("TKPI", tkpi_sources, stats)
    myfcd_assembled = _assemble_source_nutrients("MyFCD", myfcd_sources, stats)

    combined = pd.concat([tkpi_assembled, myfcd_assembled], ignore_index=True)

    for column in schema_columns():
        if column not in combined.columns:
            combined[column] = None
    combined = combined[schema_columns()]

    # Recompute derived completeness fields post-imputation - the enriched
    # source's original values reflect pre-imputation missingness and would
    # otherwise be stale/inconsistent with the actual assembled nutrient values.
    row_dicts = combined.to_dict(orient="records")
    combined["missing_nutrient_count"] = [compute_missing_nutrient_count(row) for row in row_dicts]
    combined["completeness_score"] = [compute_completeness_score(row) for row in row_dicts]

    return combined, stats
