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
    "notes": ["notes", "catatan", "keterangan", "raw_text"],
}



# Source columns whose values are known to be unreliable and are treated as
# not measured. MyFCD lists copper, retinol and beta-carotene with mixed
# units per food (ug or mg) and the stored values are mostly 0 or ~0.0001,
# far below plausible levels (e.g. carob flour copper 1 ug vs 571 ug in
# USDA). Checked against the MyFCD site: the scraper reproduces the site, so
# the error is in the source and cannot be corrected with one factor.
UNRELIABLE_SOURCE_FIELDS = {
    "MyFCD": ["copper_mg", "retinol_mcg", "beta_carotene_mcg"],
}
UNRELIABLE_NOTE = "nilai sumber tidak andal, dikosongkan: {fields}"

# Values recorded in ug under an mg column (unity measure error, factor 1000).
# A value above the threshold is divided by 1000; the original is kept in
# notes. TKPI copper: 18 values of 26-4303 "mg" while the natural maximum in
# USDA SR Legacy is ~15 mg/100 g (liver; p99.9 = 11 mg) and same-type TKPI
# foods sit at 0.04-0.34 mg (e.g. bananas) - read as ug they match. Basis:
# FAO/INFOODS Guidelines for Checking Food Composition Data (2012) and for
# Converting Units (2012); Di Zio, Guarnera & Luzi (2005), Survey Methodology
# 31(1):53-63. Values between REVIEW_RANGE bounds are kept but reported.
UNIT_ERROR_CORRECTIONS = {
    "TKPI": {
        "copper_mg": {
            "threshold": 20.0,
            "factor": 1000.0,
            "review_range": (5.0, 20.0),
        }
    },
}
# Single source cells that are chemically impossible and are treated as not
# measured, keyed by the source's own food code. Verified on panganku.org.
# - CP006 Kacang kedelai, goreng: Na 3492, K 11890, Cu 26.3, Zn 60 mg give
#   16.5 g of minerals against 3.7 g ash (minerals cannot exceed ash).
# - KR003 Lemak babi (lard): Cu 9 mg with 0 g ash and every other mineral 0.
UNRELIABLE_SOURCE_CELLS = {
    "TKPI": {
        "CP006": ["sodium_mg", "potassium_mg", "copper_mg", "zinc_mg"],
        "KR003": ["copper_mg"],
    },
}
UNIT_CORRECTION_NOTE = "{field} dikoreksi ug->mg: {original:g} -> {corrected:g}"

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
    excluded_counts: dict[str, int] = {}
    unit_corrections: list[dict[str, Any]] = []
    review_values: list[dict[str, Any]] = []
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

        source_code = str(row.get("kode_pangan") or row.get("myfcd_id") or "").strip()
        for field, rule in UNIT_ERROR_CORRECTIONS.get(source, {}).items():
            value = record.get(field)
            if value is None:
                continue
            low, high = rule["review_range"]
            if field in UNRELIABLE_SOURCE_CELLS.get(source, {}).get(source_code, []):
                continue  # blanked below
            if value > rule["threshold"]:
                corrected = value / rule["factor"]
                record[field] = corrected
                note = UNIT_CORRECTION_NOTE.format(field=field, original=value, corrected=corrected)
                record["notes"] = f"{record['notes']} | {note}" if record["notes"] else note
                unit_corrections.append({"food_id": record["food_id"], "food_name_original": record["food_name_original"],
                                         "field": field, "original": value, "corrected": corrected})
            elif low < value <= high:
                review_values.append({"food_id": record["food_id"], "food_name_original": record["food_name_original"],
                                      "field": field, "value": value})

        unreliable = UNRELIABLE_SOURCE_FIELDS.get(source, []) + UNRELIABLE_SOURCE_CELLS.get(source, {}).get(source_code, [])
        blanked = [field for field in unreliable if record.get(field) is not None]
        for field in blanked:
            record[field] = None
            excluded_counts[field] = excluded_counts.get(field, 0) + 1
        if blanked:
            note = UNRELIABLE_NOTE.format(fields=", ".join(blanked))
            record["notes"] = f"{record['notes']} | {note}" if record["notes"] else note

        record["missing_nutrient_count"] = compute_missing_nutrient_count(record)
        record["completeness_score"] = compute_completeness_score(record)
        validated = NutritionRecord(**record)
        cleaned_rows.append(validated.model_dump(mode="json"))

    return pd.DataFrame(cleaned_rows, columns=schema_columns()), {
        "source": source,
        "input_rows": int(len(df)),
        "output_rows": int(len(cleaned_rows)),
        "dropped_rows": dropped_rows,
        "excluded_counts": excluded_counts,
        "unit_corrections": unit_corrections,
        "review_values": review_values,
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
    if summary.get("excluded_counts"):
        lines.append("")
        lines.append("## Nilai sumber yang dikosongkan")
        lines.append("")
        lines.append("Kolom berikut dianggap tidak terukur karena nilai sumbernya tidak andal (lihat UNRELIABLE_SOURCE_FIELDS dan UNRELIABLE_SOURCE_CELLS di scripts/clean_common.py).")
        lines.append("")
        for field, count in summary["excluded_counts"].items():
            lines.append(f"- {field}: {count} nilai dikosongkan")
    if summary.get("unit_corrections"):
        lines.append("")
        lines.append("## Koreksi kesalahan satuan (ug tercatat sebagai mg)")
        lines.append("")
        lines.append("Nilai di atas ambang dibagi 1000 (lihat UNIT_ERROR_CORRECTIONS di scripts/clean_common.py). Nilai asli tetap tercatat di kolom notes.")
        lines.append("")
        lines.append("| food_id | Pangan | Kolom | Nilai asli | Setelah koreksi |")
        lines.append("|---|---|---|---:|---:|")
        for item in summary["unit_corrections"]:
            lines.append(f"| {item['food_id']} | {item['food_name_original']} | {item['field']} | {item['original']:g} | {item['corrected']:g} |")
    if summary.get("review_values"):
        lines.append("")
        lines.append("## Perlu ditinjau manual (tidak dibagi 1000)")
        lines.append("")
        for item in summary["review_values"]:
            lines.append(f"- {item['food_id']} {item['food_name_original']}: {item['field']} = {item['value']:g}")
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
