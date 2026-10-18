from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

import pandas as pd

from src.cleaning.normalizers import compute_completeness_score, compute_missing_nutrient_count, is_missing
from src.schema.nutrition_schema import NUTRIENT_FIELDS


REQUIRED_FIELDS = ["food_id", "food_name_original", "source", "unit_basis"]
MINERAL_FIELDS_MG = ["calcium_mg", "phosphorus_mg", "iron_mg", "sodium_mg", "potassium_mg", "copper_mg", "zinc_mg"]
# Per 100 g bahan, total mineral tidak mungkin melebihi 100 g.
MAX_MINERAL_TOTAL_G = 100.0
# Minerals are part of ash, so their sum cannot exceed it (FAO/INFOODS data
# checking guidelines). TKPI ash values are often slightly inconsistent, so
# only gross violations are flagged.
ASH_EXCESS_RATIO = 2.0
ASH_EXCESS_MIN_G = 1.0


def _is_numeric_or_missing(value: Any) -> bool:
    if is_missing(value):
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return not (isinstance(value, float) and math.isnan(value))
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_dataframe(df: pd.DataFrame, source_name: str) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    invalid_rows: set[int] = set()

    for index, row in df.iterrows():
        for field in REQUIRED_FIELDS:
            if field not in df.columns or is_missing(row.get(field)):
                issues.append({"row": int(index), "type": "missing_required", "field": field})
                invalid_rows.add(int(index))

        for field in NUTRIENT_FIELDS:
            if field in df.columns and not _is_numeric_or_missing(row.get(field)):
                issues.append({"row": int(index), "type": "invalid_numeric", "field": field, "value": row.get(field)})
                invalid_rows.add(int(index))

        if "energy_kcal" in df.columns and _is_numeric_or_missing(row.get("energy_kcal")) and not is_missing(row.get("energy_kcal")):
            energy = float(row.get("energy_kcal"))
            if energy < 0:
                issues.append({"row": int(index), "type": "invalid_range", "field": "energy_kcal", "value": energy})
                invalid_rows.add(int(index))
            elif energy > 900:
                warnings.append({"row": int(index), "type": "range_warning", "field": "energy_kcal", "value": energy})

        minerals = [
            float(row.get(field))
            for field in MINERAL_FIELDS_MG
            if field in df.columns and _is_numeric_or_missing(row.get(field)) and not is_missing(row.get(field))
        ]
        mineral_total_g = sum(minerals) / 1000
        if mineral_total_g > MAX_MINERAL_TOTAL_G:
            warnings.append(
                {
                    "row": int(index),
                    "type": "outlier_implausible_minerals",
                    "food_id": row.get("food_id"),
                    "food_name_original": row.get("food_name_original"),
                    "field": "mineral_total_g",
                    "value": round(mineral_total_g, 3),
                }
            )

        ash = row.get("ash_g") if "ash_g" in df.columns else None
        if (
            mineral_total_g <= MAX_MINERAL_TOTAL_G
            and _is_numeric_or_missing(ash)
            and not is_missing(ash)
            and mineral_total_g > ASH_EXCESS_RATIO * float(ash)
            and mineral_total_g - float(ash) > ASH_EXCESS_MIN_G
        ):
            warnings.append(
                {
                    "row": int(index),
                    "type": "outlier_minerals_exceed_ash",
                    "food_id": row.get("food_id"),
                    "food_name_original": row.get("food_name_original"),
                    "field": "mineral_total_g",
                    "value": round(mineral_total_g, 3),
                    "ash_g": float(ash),
                }
            )

        row_dict = row.to_dict()
        expected_missing = compute_missing_nutrient_count(row_dict)
        expected_score = compute_completeness_score(row_dict)
        actual_missing = row.get("missing_nutrient_count")
        actual_score = row.get("completeness_score")
        if not is_missing(actual_missing) and int(float(actual_missing)) != expected_missing:
            issues.append(
                {
                    "row": int(index),
                    "type": "completeness_mismatch",
                    "field": "missing_nutrient_count",
                    "expected": expected_missing,
                    "actual": actual_missing,
                }
            )
            invalid_rows.add(int(index))
        if not is_missing(actual_score) and abs(float(actual_score) - expected_score) > 0.001:
            issues.append(
                {
                    "row": int(index),
                    "type": "completeness_mismatch",
                    "field": "completeness_score",
                    "expected": expected_score,
                    "actual": actual_score,
                }
            )
            invalid_rows.add(int(index))

    duplicate_count = 0
    if {"source", "food_name_normalized"}.issubset(df.columns):
        duplicated = df.duplicated(subset=["source", "food_name_normalized"], keep=False)
        duplicate_count = int(duplicated.sum())
        for index in df[duplicated].index:
            warnings.append({"row": int(index), "type": "duplicate_food_name_normalized"})

    issue_counts = Counter(item["type"] for item in issues)
    warning_counts = Counter(item["type"] for item in warnings)

    return {
        "source": source_name,
        "total_rows": int(len(df)),
        "valid_rows": int(len(df) - len(invalid_rows)),
        "invalid_rows": int(len(invalid_rows)),
        "duplicate_count": duplicate_count,
        "issues_by_type": dict(issue_counts),
        "warnings_by_type": dict(warning_counts),
        "issues": issues,
        "warnings": warnings,
    }


def combine_quality_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    issues_by_type: defaultdict[str, int] = defaultdict(int)
    warnings_by_type: defaultdict[str, int] = defaultdict(int)
    for report in reports:
        for key, value in report["issues_by_type"].items():
            issues_by_type[key] += value
        for key, value in report["warnings_by_type"].items():
            warnings_by_type[key] += value

    return {
        "total_rows": sum(report["total_rows"] for report in reports),
        "valid_rows": sum(report["valid_rows"] for report in reports),
        "invalid_rows": sum(report["invalid_rows"] for report in reports),
        "duplicate_count": sum(report["duplicate_count"] for report in reports),
        "issues_by_type": dict(issues_by_type),
        "warnings_by_type": dict(warnings_by_type),
        "sources": reports,
    }
