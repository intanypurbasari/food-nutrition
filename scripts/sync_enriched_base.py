"""Salin kolom gizi dari data_clean ke *_enriched.csv tanpa menjalankan ulang entity resolution.

*_enriched.csv dibuat oleh scripts/entity_resolution_threeway.ipynb dan tidak
diperbarui oleh run_pipeline.py. Menjalankan ulang notebook dapat mengganti
tautan USDA yang skornya seri, jadi skrip ini hanya memperbarui sel gizi yang
nilainya berubah dan membiarkan kolom/tautan USDA apa adanya.

Jalankan setelah clean_tkpi/clean_myfcd, lalu ulangi tahap imputasi.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import MYFCD_ENRICHED_PATH, TKPI_ENRICHED_PATH
from src.schema.nutrition_schema import NUTRIENT_FIELDS


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "TKPI": (ROOT / "data_clean" / "tkpi_clean.csv", TKPI_ENRICHED_PATH),
    "MyFCD": (ROOT / "data_clean" / "myfcd_clean.csv", MYFCD_ENRICHED_PATH),
}


def _same(a: str, b: str) -> bool:
    if a == "" or b == "":
        return a == b
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


def sync(source: str, dry_run: bool) -> int:
    clean_path, enriched_path = SOURCES[source]
    with clean_path.open(newline="", encoding="utf-8") as handle:
        clean = {row["food_id"]: row for row in csv.DictReader(handle)}

    text = enriched_path.read_text(encoding="utf-8")
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0]
    index = {name: i for i, name in enumerate(header)}
    columns = [field for field in NUTRIENT_FIELDS if field in index]

    enriched_ids = [row[index["food_id"]] for row in rows[1:]]
    if set(enriched_ids) != set(clean):
        print(f"[SYNC] {source}: food_id di data_clean dan {enriched_path.name} berbeda. Dibatalkan.")
        return -1
    mismatched = [
        food_id
        for food_id, row in zip(enriched_ids, rows[1:])
        if row[index["food_name_original"]] != clean[food_id]["food_name_original"]
    ]
    if mismatched:
        print(
            f"[SYNC] {source}: {len(mismatched)} food_id menunjuk ke pangan yang berbeda "
            f"(contoh: {mismatched[:3]}). Urutan data berubah; jalankan ulang notebook entity resolution. Dibatalkan."
        )
        return -1

    changed: dict[str, int] = {}
    for row in rows[1:]:
        source_row = clean[row[index["food_id"]]]
        for column in columns:
            if not _same(row[index[column]], source_row[column]):
                row[index[column]] = source_row[column]
                changed[column] = changed.get(column, 0) + 1

    total = sum(changed.values())
    print(f"[SYNC] {source}: {total} sel diperbarui {changed if changed else ''}".rstrip())
    if total and not dry_run:
        out = io.StringIO()
        csv.writer(out, lineterminator="\n").writerows(rows)
        enriched_path.write_text(out.getvalue(), encoding="utf-8", newline="")
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="tampilkan perubahan tanpa menulis berkas")
    args = parser.parse_args()
    results = [sync(source, args.dry_run) for source in SOURCES]
    return 1 if any(result < 0 for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
