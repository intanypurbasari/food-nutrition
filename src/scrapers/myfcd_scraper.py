from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from config.settings import MYFCD_URL
from src.scrapers.base import (
    ROOT,
    ScrapeResult,
    fetch_with_cache,
    looks_js_heavy,
    post_with_cache,
    setup_logger,
    write_json_report,
    write_raw_outputs,
)

DATATABLE_URL = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data"
COMPARE_URL = "https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/food_compare"

MYFCD_NUTRIENT_MAP = {
    "WATER": ("water_g", "1"),
    "ENERCT": ("energy_kcal", "5"),
    "PROTCNT": ("protein_g", "1"),
    "FAT": ("fat_g", "1"),
    "CHOAVLDF": ("carbohydrate_g", "1"),
    "FIBTG": ("fiber_g", "1"),
    "ASH": ("ash_g", "1"),
    "CA": ("calcium_mg", "2"),
    "P": ("phosphorus_mg", "2"),
    "FE": ("iron_mg", "2"),
    "NA": ("sodium_mg", "2"),
    "K": ("potassium_mg", "2"),
    "CU": ("copper_mg", "2"),
    "ZN": ("zinc_mg", "2"),
    "RETOL": ("retinol_mcg", "3"),
    "CARTB": ("beta_carotene_mcg", "3"),
    "THIA": ("vitamin_b1_mg", "2"),
    "RIBF": ("vitamin_b2_mg", "2"),
    "NIA": ("niacin_mg", "2"),
    "VITC": ("vitamin_c_mg", "2"),
}


def write_fallback_report(reason: str) -> None:
    path = ROOT / "reports" / "myfcd_fallback_report.md"
    path.write_text(
        "\n".join(
            [
                "# MyFCD Fallback Report",
                "",
                "Automatic scraping with requests + BeautifulSoup did not produce reliable data.",
                "",
                f"Reason: {reason}",
                "",
                "No captcha, login wall, JavaScript protection, or access limitation was bypassed.",
                "",
                "Recommended options:",
                "",
                "1. Ask the research supervisor/team whether limited Playwright/Selenium rendering is approved.",
                "2. Request an official dataset or download route from the data owner.",
                "3. Use a manual entry/download template while waiting for approval.",
            ]
        ),
        encoding="utf-8",
    )


def _datatable_payload(limit: int) -> dict[str, str]:
    payload = {
        "draw": "1",
        "start": "0",
        "length": str(max(limit, 2)),
        "search[value]": "",
        "search[regex]": "false",
        "my_food_group": "0",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
    }
    for index in range(3):
        payload[f"columns[{index}][data]"] = str(index)
        payload[f"columns[{index}][name]"] = ""
        payload[f"columns[{index}][searchable]"] = "true"
        payload[f"columns[{index}][orderable]"] = "true"
        payload[f"columns[{index}][search][value]"] = ""
        payload[f"columns[{index}][search][regex]"] = "false"
    return payload


def _fetch_listing(limit: int, logger) -> tuple[list[list[str]], list[dict[str, Any]]]:
    html, meta = post_with_cache(
        DATATABLE_URL,
        _datatable_payload(limit),
        "myfcd",
        logger,
        extra_headers={"Referer": MYFCD_URL, "X-Requested-With": "XMLHttpRequest"},
    )
    if html is None:
        return [], [{"source": "MyFCD", "stage": "datatable_fetch", **meta}]
    try:
        data = json.loads(html)
    except json.JSONDecodeError as exc:
        return [], [{"source": "MyFCD", "stage": "datatable_parse", "message": str(exc)}]
    return data.get("data", [])[:limit], []


def _convert_unit(value: float, from_unit: str | None, to_unit: str, conv: dict[str, Any]) -> float:
    if not from_unit or from_unit == to_unit:
        return value
    if from_unit not in conv or to_unit not in conv:
        return value
    from_rate = float(conv[from_unit]["conversion_rate_to_base_unit"])
    to_rate = float(conv[to_unit]["conversion_rate_to_base_unit"])
    return value * from_rate / to_rate


def _average_nutrient(product_nutrients: list[dict[str, Any]], nutrient_id: str, target_unit: str, conv: dict[str, Any]) -> float | None:
    values = []
    for nutrient in product_nutrients:
        if nutrient.get("nutrient_id") != nutrient_id:
            continue
        try:
            raw_value = float(nutrient.get("value"))
        except (TypeError, ValueError):
            continue
        source_unit = nutrient.get("nutrient_unit") or nutrient.get("unit")
        values.append(_convert_unit(raw_value, source_unit, target_unit, conv))
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _fetch_compare(ids: list[str], logger) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    data = [("senaraiIDFoodToCompare[]", item) for item in ids]
    html, meta = post_with_cache(
        COMPARE_URL,
        data,
        "myfcd",
        logger,
        extra_headers={"Referer": MYFCD_URL, "X-Requested-With": "XMLHttpRequest"},
    )
    if html is None:
        return None, {"source": "MyFCD", "stage": "compare_fetch", **meta}
    try:
        return json.loads(html), None
    except json.JSONDecodeError as exc:
        return None, {"source": "MyFCD", "stage": "compare_parse", "message": str(exc)}


def _rows_from_compare(compare_data: dict[str, Any], keep_ids: set[str]) -> list[dict[str, Any]]:
    rows = []
    conv = compare_data.get("common_data", {}).get("nutrient_units_conv", {})
    for product in compare_data.get("senarai_food_products", []):
        product_data = product.get("product_data", {})
        product_id = product_data.get("id") or product_data.get("ndb_no")
        if product_id not in keep_ids:
            continue
        record = {
            "food_name_original": product_data.get("product_name") or product_data.get("description"),
            "source": "MyFCD",
            "source_url": f"https://myfcd.moh.gov.my/myfcdcurrent/index.php/site/detail_product/{product_id}/0/20/0/0/0",
            "category_original": product_data.get("foodgroupname") or product_data.get("food_group"),
            "unit_basis": "per 100g",
            "notes": product_data.get("notes"),
            "myfcd_id": product_id,
        }
        if product_data.get("perc_ep") not in {None, ""}:
            record["edible_portion_percent"] = product_data.get("perc_ep")
        for nutrient_id, (field, target_unit) in MYFCD_NUTRIENT_MAP.items():
            value = _average_nutrient(product.get("product_nutrients", []), nutrient_id, target_unit, conv)
            if value is not None:
                record[field] = value
        rows.append(record)
    return rows


def scrape_myfcd(limit: int = 20) -> ScrapeResult:
    logger = setup_logger("myfcd_scraper", ROOT / "logs" / "myfcd_scrape.log")
    html, meta = fetch_with_cache(MYFCD_URL, "myfcd", logger)
    errors = []
    rows = []

    if html is None:
        reason = f"Fetch failed: {meta}"
        errors.append({"source": "MyFCD", "stage": "fetch", **meta})
        write_fallback_report(reason)
    else:
        listing, listing_errors = _fetch_listing(limit, logger)
        errors.extend(listing_errors)
        ids = [item[0] for item in listing if item]
        chunk_size = 10
        for start in range(0, len(ids), chunk_size):
            chunk = ids[start : start + chunk_size]
            if len(chunk) == 1 and len(ids) > 1:
                chunk.append(ids[0])
            elif len(chunk) == 1:
                break
            compare_data, compare_error = _fetch_compare(chunk, logger)
            if compare_error:
                errors.append(compare_error)
                continue
            rows.extend(_rows_from_compare(compare_data or {}, set(chunk[: chunk_size])))
        rows = rows[:limit]
        if not rows:
            reason = "MyFCD listing was accessible, but no nutrient comparison rows were extracted."
            errors.append({"source": "MyFCD", "stage": "parse", "url": MYFCD_URL, "message": reason})
            if looks_js_heavy(html):
                write_fallback_report(reason)

    write_raw_outputs(rows, "myfcd")
    if errors:
        write_json_report(Path(ROOT / "reports" / "myfcd_scrape_errors.json"), errors)
    else:
        for stale_report in [
            ROOT / "reports" / "myfcd_scrape_errors.json",
            ROOT / "reports" / "myfcd_fallback_report.md",
        ]:
            if stale_report.exists():
                stale_report.unlink()
    return ScrapeResult(rows=rows, errors=errors)
