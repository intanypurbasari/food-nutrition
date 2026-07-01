from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.cleaning.normalizers import (
    compute_completeness_score,
    compute_missing_nutrient_count,
    normalize_category,
    normalize_column_name,
    normalize_food_name,
    normalize_numeric,
)
from src.schema.nutrition_schema import NUTRIENT_FIELDS, NutritionRecord, schema_columns


ROOT = Path(__file__).resolve().parents[1]


COMMON_ALIASES = {
    "food_name_original": [
        "food_name_original",
        "nama_bahan_makanan",
        "nama_bahan",
        "nama_makanan",
        "food_name",
        "name",
        "nama",
    ],
    "category_original": ["category_original", "kelompok_makanan", "kelompok", "food_group", "group", "category"],
    "source_url": ["source_url", "url", "detail_url"],
    "scraped_at": ["scraped_at", "scrape_time"],
    "energy_kcal": ["energy_kcal", "energi_kal", "energi", "energy", "energy_kcal_kcal"],
    "protein_g": ["protein_g", "protein"],
    "fat_g": ["fat_g", "lemak_g", "lemak", "fat"],
    "carbohydrate_g": ["carbohydrate_g", "karbohidrat_g", "karbohidrat", "carbohydrate", "carbohydrates"],
    "fiber_g": ["fiber_g", "serat_g", "serat", "dietary_fibre_g", "dietary_fiber_g", "fibre", "fiber"],
    "water_g": ["water_g", "air_g", "air", "moisture_g", "moisture"],
    "ash_g": ["ash_g", "abu_g", "abu", "ash"],
    "calcium_mg": ["calcium_mg", "kalsium_mg", "kalsium", "calcium"],
    "phosphorus_mg": ["phosphorus_mg", "fosfor_mg", "fosfor", "phosphorus"],
    "iron_mg": ["iron_mg", "besi_mg", "besi", "iron"],
    "sodium_mg": ["sodium_mg", "natrium_mg", "natrium", "sodium"],
    "potassium_mg": ["potassium_mg", "kalium_mg", "kalium", "potassium"],
    "copper_mg": ["copper_mg", "tembaga_mg", "tembaga", "copper"],
    "zinc_mg": ["zinc_mg", "seng_mg", "seng", "zinc"],
    "retinol_mcg": ["retinol_mcg", "retinol"],
    "beta_carotene_mcg": ["beta_carotene_mcg", "beta_karoten_mcg", "b_karoten_mcg", "karoten_beta", "beta_carotene"],
    "carotene_total_mcg": ["carotene_total_mcg", "karoten_total_mcg", "total_carotene_mcg", "carotene_total"],
    "vitamin_a_mcg": ["vitamin_a_mcg", "vitamin_a"],
    "vitamin_b1_mg": ["vitamin_b1_mg", "vitamin_b1", "thiamine_mg", "thiamine", "tiamin"],
    "vitamin_b2_mg": ["vitamin_b2_mg", "vitamin_b2", "riboflavin_mg", "riboflavin"],
    "niacin_mg": ["niacin_mg", "niacin", "niasin_mg", "niasin"],
    "vitamin_c_mg": ["vitamin_c_mg", "vitamin_c"],
    "edible_portion_percent": ["edible_portion_percent", "bdd", "bdd_percent", "edible_portion"],
    "notes": ["notes", "catatan", "keterangan", "raw_text"],
}


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    return value


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: normalize_column_name(column) for column in df.columns}
    return df.rename(columns=renamed)


def pick_value(row: pd.Series, aliases: list[str]) -> Any:
    for alias in aliases:
        if alias in row.index:
            value = row.get(alias)
            if not pd.isna(value) and str(value).strip():
                return value
    return None


def clean_dataframe(df: pd.DataFrame, source: str, source_prefix: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = normalize_columns(df)
    cleaned_rows: list[dict[str, Any]] = []
    dropped_rows = []
    cleaned_at = datetime.now(timezone.utc).isoformat()

    for idx, row in df.iterrows():
        food_name = pick_value(row, COMMON_ALIASES["food_name_original"])
        if food_name is None or not str(food_name).strip():
            dropped_rows.append({"row_index": int(idx), "reason": "missing food_name"})
            continue

        record: dict[str, Any] = {column: None for column in schema_columns()}
        record["food_id"] = f"{source_prefix}_{len(cleaned_rows) + 1:04d}"
        record["food_name_original"] = str(food_name).strip()
        record["food_name_normalized"] = normalize_food_name(food_name)
        record["source"] = source
        record["source_url"] = _json_safe(pick_value(row, COMMON_ALIASES["source_url"]))
        category = pick_value(row, COMMON_ALIASES["category_original"])
        record["category_original"] = _json_safe(category)
        record["category_normalized"] = normalize_category(category)
        record["unit_basis"] = "per 100g"
        record["scraped_at"] = _json_safe(pick_value(row, COMMON_ALIASES["scraped_at"])) or cleaned_at
        record["cleaned_at"] = cleaned_at
        record["notes"] = _json_safe(pick_value(row, COMMON_ALIASES["notes"]))

        for nutrient in NUTRIENT_FIELDS:
            record[nutrient] = normalize_numeric(pick_value(row, COMMON_ALIASES.get(nutrient, [nutrient])))

        record["missing_nutrient_count"] = compute_missing_nutrient_count(record)
        record["completeness_score"] = compute_completeness_score(record)
        validated = NutritionRecord(**record)
        cleaned_rows.append(validated.model_dump(mode="json"))

    return pd.DataFrame(cleaned_rows, columns=schema_columns()), {
        "source": source,
        "input_rows": int(len(df)),
        "output_rows": int(len(cleaned_rows)),
        "dropped_rows": dropped_rows,
    }


def write_clean_outputs(df: pd.DataFrame, source_slug: str, report_title: str, summary: dict[str, Any]) -> None:
    (ROOT / "data_clean").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)
    csv_path = ROOT / "data_clean" / f"{source_slug}_clean.csv"
    json_path = ROOT / "data_clean" / f"{source_slug}_clean.json"
    report_path = ROOT / "reports" / f"{source_slug}_missing_value_report.md"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    records = json.loads(df.where(pd.notna(df), None).to_json(orient="records", force_ascii=False))
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"# {report_title}", ""]
    lines.append(f"- Input rows: {summary['input_rows']}")
    lines.append(f"- Output rows: {summary['output_rows']}")
    lines.append(f"- Dropped rows: {len(summary['dropped_rows'])}")
    lines.append("")
    lines.append("## Missing Value per Nutrient")
    lines.append("")
    lines.append("| Nutrient | Missing Count | Missing Percent |")
    lines.append("|---|---:|---:|")
    total = len(df)
    for field in NUTRIENT_FIELDS:
        missing = int(df[field].isna().sum()) if field in df else total
        percent = (missing / total * 100) if total else 0
        lines.append(f"| {field} | {missing} | {percent:.2f}% |")
    if summary["dropped_rows"]:
        lines.append("")
        lines.append("## Dropped Rows")
        for item in summary["dropped_rows"]:
            lines.append(f"- Row {item['row_index']}: {item['reason']}")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def clean_source(raw_path: Path, source: str, source_slug: str, source_prefix: str) -> int:
    if not raw_path.exists() or raw_path.stat().st_size == 0:
        print(f"No raw {source} data found at {raw_path}. Nothing to clean.")
        return 0

    try:
        df = pd.read_csv(raw_path)
    except pd.errors.EmptyDataError:
        print(f"Raw {source} file is empty. Nothing to clean.")
        return 0

    if df.empty:
        print(f"Raw {source} file has no rows. Nothing to clean.")
        return 0

    cleaned, summary = clean_dataframe(df, source=source, source_prefix=source_prefix)
    write_clean_outputs(cleaned, source_slug, f"{source} Missing Value Report", summary)
    print(f"{source} clean rows written: {len(cleaned)}")
    return 0
