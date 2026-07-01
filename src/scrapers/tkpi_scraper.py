from __future__ import annotations

from pathlib import Path
import re

from config.settings import TKPI_URL
from bs4 import BeautifulSoup
from src.scrapers.base import (
    ROOT,
    ScrapeResult,
    fetch_with_cache,
    post_with_cache,
    setup_logger,
    write_json_report,
    write_raw_outputs,
)

DETAIL_URL = "https://www.panganku.org/id-ID/view"

TKPI_NUTRIENT_MAP = {
    "air": "water_g",
    "energi": "energy_kcal",
    "protein": "protein_g",
    "lemak": "fat_g",
    "karbohidrat": "carbohydrate_g",
    "serat": "fiber_g",
    "abu": "ash_g",
    "kalsium": "calcium_mg",
    "fosfor": "phosphorus_mg",
    "besi": "iron_mg",
    "natrium": "sodium_mg",
    "kalium": "potassium_mg",
    "tembaga": "copper_mg",
    "seng": "zinc_mg",
    "retinol": "retinol_mcg",
    "beta-karoten": "beta_carotene_mcg",
    "karoten total": "carotene_total_mcg",
    "thiamin": "vitamin_b1_mg",
    "riboflavin": "vitamin_b2_mg",
    "niasin": "niacin_mg",
    "vitamin c": "vitamin_c_mg",
}

TKPI_RAW_COLUMNS = [
    "kode_pangan",
    "food_name_original",
    "category_original",
    "tipe_bahan",
    "source",
    "source_url",
    "water_g",
    "energy_kcal",
    "protein_g",
    "fat_g",
    "carbohydrate_g",
    "fiber_g",
    "ash_g",
    "calcium_mg",
    "phosphorus_mg",
    "iron_mg",
    "sodium_mg",
    "potassium_mg",
    "copper_mg",
    "zinc_mg",
    "retinol_mcg",
    "beta_carotene_mcg",
    "carotene_total_mcg",
    "vitamin_b1_mg",
    "vitamin_b2_mg",
    "niacin_mg",
    "vitamin_c_mg",
    "notes",
]


def _first_number(text: str) -> str | None:
    match = re.search(r"[-+]?\d+(?:[.,]\d+)?", text.replace("\xa0", " "))
    return match.group(0) if match else None


def _extract_categories(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    categories = []
    for option in soup.select("select[name='kategori'] option"):
        value = option.get("value")
        if value:
            categories.append(value)
    return categories or ["Serealia"]


def _parse_listing(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("table#data tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(cells) >= 5 and cells[1] != "Kode Pangan":
            rows.append(
                {
                    "kode_pangan": cells[1],
                    "food_name_original": cells[2],
                    "category_original": cells[3],
                    "tipe_bahan": cells[4],
                }
            )
    return rows


def _parse_detail(html: str, listing_row: dict[str, str], source_url: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    record = dict(listing_row)
    record.update({"source": "TKPI", "source_url": source_url})

    for tr in soup.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
        if len(cells) == 3 and cells[1] == ":":
            key = cells[0].strip().lower()
            value = cells[2].strip()
            if key == "nama":
                record["food_name_original"] = value
            elif key == "kategori":
                record["category_original"] = value
            elif key == "keterangan" and value:
                record["notes"] = value
        elif len(cells) >= 2:
            label = cells[0].strip().lower()
            value_text = cells[1]
            for prefix, field in TKPI_NUTRIENT_MAP.items():
                if label.startswith(prefix):
                    number = _first_number(value_text)
                    if number is not None:
                        record[field] = number
                    break
    return record


def scrape_tkpi(limit: int = 20) -> ScrapeResult:
    logger = setup_logger("tkpi_scraper", ROOT / "logs" / "tkpi_scrape.log")
    html, meta = fetch_with_cache(TKPI_URL, "tkpi", logger)
    errors = []
    rows = []

    if html is None:
        errors.append({"source": "TKPI", "stage": "fetch", **meta})
    else:
        categories = _extract_categories(html)
        listing_rows = []
        for category in categories:
            if len(listing_rows) >= limit:
                break
            category_html, category_meta = post_with_cache(
                TKPI_URL,
                {"kategori": category},
                "tkpi",
                logger,
                extra_headers={"Referer": TKPI_URL},
            )
            if category_html is None:
                errors.append({"source": "TKPI", "stage": "category_fetch", "category": category, **category_meta})
                continue
            listing_rows.extend(_parse_listing(category_html))

        for item in listing_rows[:limit]:
            detail_html, detail_meta = post_with_cache(
                DETAIL_URL,
                {"haha": item["kode_pangan"]},
                "tkpi",
                logger,
                extra_headers={"Referer": TKPI_URL},
            )
            if detail_html is None:
                errors.append({"source": "TKPI", "stage": "detail_fetch", "code": item["kode_pangan"], **detail_meta})
                continue
            record = _parse_detail(detail_html, item, DETAIL_URL)
            rows.append(record)

        if not rows:
            errors.append({"source": "TKPI", "stage": "parse", "url": TKPI_URL, "message": "No TKPI food rows were extracted."})

    write_raw_outputs(rows, "tkpi", columns=TKPI_RAW_COLUMNS)
    if errors:
        write_json_report(Path(ROOT / "reports" / "tkpi_scrape_errors.json"), errors)
    else:
        stale_report = ROOT / "reports" / "tkpi_scrape_errors.json"
        if stale_report.exists():
            stale_report.unlink()
    return ScrapeResult(rows=rows, errors=errors)
