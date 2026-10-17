#!/usr/bin/env python3
"""Isi vitamin_a_mcg (RAE) pada nutrition_repository_imputed.csv.

Latar belakang
--------------
`vitamin_a_mcg` 100% kosong pada TKPI maupun MyFCD, sehingga Tahap 2
merutekannya ke strategi "Pinjam USDA (kosong di kedua basis)", tetapi Tahap 1
tidak pernah meminjamnya dan Tahap 3 melaporkannya sebagai *unresolved*.
Skrip ini dijalankan setelah run_integration.py dan mengisi celah tersebut.

Urutan sumber nilai (yang pertama tersedia dipakai)
---------------------------------------------------
1. derived_measured        RAE = retinol + beta-karoten/12 (IOM 2001), keduanya
                           nilai terukur pangan itu sendiri.
2. derived_partly_imputed  Rumus yang sama; salah satu komponen terukur, yang lain
                           diambil dari hasil imputasi Tahap 3.
3. USDA_direct_high        Tidak ada komponen terukur; pinjam "Vitamin A, RAE"
                           (nutrient_id 1106) dari pangan USDA tertaut, skor >= 0,65.
4. USDA_direct_medium      Sama, skor >= 0,40 (tinjau manual).
5. derived_imputed         Rumus RAE dari retinol dan beta-karoten hasil imputasi.

Data terukur pangan lokal didahulukan karena tautan USDA menunjuk ke pangan
lain: pada data ini, untuk tautan MEDIUM, nilai USDA dan RAE turunan berbeda
lebih dari 2x pada sekitar separuh pasangan. Rumus RAE sendiri hampir eksak
pada data USDA (Spearman 0,991; median |galat| 0,0 mcg; n = 5.245).

carotene_total_mcg sengaja tidak dipakai, untuk menghindari penghitungan ganda
dengan beta-karoten.

Keluaran
--------
- nutrition_repository_imputed.csv: kolom vitamin_a_mcg diisi;
  missing_nutrient_count dan completeness_score dihitung ulang.
- vitamin_a_provenance.csv: asal nilai per pangan (sumber, tautan USDA, skor).
- reports/vitamin_a_review.md: ringkasan dan daftar pangan yang nilai turunannya
  sangat berbeda dari pangan USDA tertaut berskor HIGH (tinjau manual).

Cara pakai
----------
    python scripts/borrow_vitamin_a.py            # tulis keluaran
    python scripts/borrow_vitamin_a.py --dry-run  # pratinjau saja
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning.normalizers import compute_completeness_score, compute_missing_nutrient_count

ROOT = Path(__file__).resolve().parents[1]
USDA_DIR = ROOT / "usda-csv"
PROCESSED = ROOT / "data_processed"
REPOSITORY_PATH = PROCESSED / "nutrition_repository_imputed.csv"
PROVENANCE_PATH = PROCESSED / "vitamin_a_provenance.csv"
REVIEW_PATH = ROOT / "reports" / "vitamin_a_review.md"

VITAMIN_A_RAE_NUTRIENT_ID = 1106  # "Vitamin A, RAE", satuan UG (mikrogram)
TARGET_COLUMN = "vitamin_a_mcg"
SOURCE_COLUMN = f"{TARGET_COLUMN}_source"
# Beda nilai turunan vs USDA HIGH yang dianggap perlu ditinjau.
REVIEW_RATIO = 10.0
REVIEW_MIN_DIFF_MCG = 100.0

SOURCES = {
    "TKPI": {"enriched": PROCESSED / "tkpi_enriched.csv", "links": PROCESSED / "tkpi_usda_links.csv"},
    "MyFCD": {"enriched": PROCESSED / "myfcd_enriched.csv", "links": PROCESSED / "myfcd_usda_links.csv"},
}


def load_usda_vitamin_a() -> pd.Series:
    """Vitamin A, RAE per fdc_id."""
    food_nutrient = pd.read_csv(
        USDA_DIR / "food_nutrient.csv",
        usecols=["fdc_id", "nutrient_id", "amount"],
        low_memory=False,
    )
    rows = food_nutrient[food_nutrient["nutrient_id"] == VITAMIN_A_RAE_NUTRIENT_ID]
    return rows.groupby("fdc_id")["amount"].first()


def rae(retinol: float, beta_carotene: float) -> float:
    return round(retinol + beta_carotene / 12.0, 4)


def resolve_source(config: dict, usda_rae: pd.Series, imputed: pd.DataFrame) -> pd.DataFrame:
    measured = pd.read_csv(config["enriched"], usecols=["food_id", "retinol_mcg", "beta_carotene_mcg"])
    links = pd.read_csv(config["links"])
    links = links[links["confidence"].isin(["HIGH", "MEDIUM"])].copy()
    links["usda_rae"] = links["usda_fdc_id"].map(usda_rae)
    links = (
        links[links["usda_rae"].notna()]
        .sort_values("similarity_score", ascending=False)
        .drop_duplicates("source_food_id")
        .set_index("source_food_id")
    )

    records = []
    for row in measured.itertuples(index=False):
        food_id = row.food_id
        retinol, beta = row.retinol_mcg, row.beta_carotene_mcg
        link = links.loc[food_id] if food_id in links.index else None
        record = {
            "food_id": food_id,
            "usda_fdc_id": None if link is None else int(link["usda_fdc_id"]),
            "usda_food_name": None if link is None else link["usda_food_name"],
            "similarity_score": None if link is None else float(link["similarity_score"]),
            "confidence": None if link is None else link["confidence"],
            "usda_rae": None if link is None else float(link["usda_rae"]),
        }

        imputed_retinol = imputed.at[food_id, "retinol_mcg"] if food_id in imputed.index else float("nan")
        imputed_beta = imputed.at[food_id, "beta_carotene_mcg"] if food_id in imputed.index else float("nan")

        if pd.notna(retinol) and pd.notna(beta):
            value, source = rae(retinol, beta), "derived_measured"
        elif (pd.notna(retinol) or pd.notna(beta)) and pd.notna(imputed_retinol) and pd.notna(imputed_beta):
            value = rae(retinol if pd.notna(retinol) else imputed_retinol, beta if pd.notna(beta) else imputed_beta)
            source = "derived_partly_imputed"
        elif link is not None:
            value, source = float(link["usda_rae"]), f"USDA_direct_{link['confidence'].lower()}"
        elif pd.notna(imputed_retinol) and pd.notna(imputed_beta):
            value, source = rae(imputed_retinol, imputed_beta), "derived_imputed"
        else:
            value, source = None, "unresolved"

        record[TARGET_COLUMN] = value
        record[SOURCE_COLUMN] = source
        records.append(record)
    return pd.DataFrame(records)


def needs_review(row: pd.Series) -> bool:
    if row["confidence"] != "HIGH" or not str(row[SOURCE_COLUMN]).startswith("derived"):
        return False
    derived, usda = row[TARGET_COLUMN], row["usda_rae"]
    if pd.isna(derived) or pd.isna(usda) or abs(derived - usda) < REVIEW_MIN_DIFF_MCG:
        return False
    low, high = sorted([derived, usda])
    return high > REVIEW_RATIO * max(low, 1.0)


def write_review(provenance: pd.DataFrame, repository: pd.DataFrame) -> None:
    names = repository.set_index("food_id")["food_name_original"]
    lines = ["# Vitamin A (RAE) Review", "", "## Sumber nilai", "", "| Sumber | TKPI | MyFCD |", "|---|---|---|"]
    counts = provenance.groupby(["source", SOURCE_COLUMN]).size().unstack(0, fill_value=0)
    for source_label, row in counts.iterrows():
        lines.append(f"| {source_label} | {row.get('TKPI', 0)} | {row.get('MyFCD', 0)} |")

    flagged = provenance[provenance.apply(needs_review, axis=1)]
    lines += ["", "## Perlu tinjau manual", ""]
    if flagged.empty:
        lines.append("- Tidak ada.")
    else:
        lines.append(
            f"RAE turunan berbeda lebih dari {REVIEW_RATIO:g}x (dan lebih dari {REVIEW_MIN_DIFF_MCG:g} mcg) "
            "dari pangan USDA tertaut berskor HIGH. Nilai turunan tetap dipakai."
        )
        lines.append("")
        for row in flagged.itertuples(index=False):
            lines.append(
                f"- {row.food_id} ({names.get(row.food_id, '')}): turunan {getattr(row, TARGET_COLUMN):g} mcg, "
                f"USDA {row.usda_rae:g} mcg ({row.usda_food_name})"
            )
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="tampilkan ringkasan tanpa menulis berkas")
    args = parser.parse_args()

    usda_rae = load_usda_vitamin_a()
    repository = pd.read_csv(REPOSITORY_PATH)
    imputed = repository.set_index("food_id")[["retinol_mcg", "beta_carotene_mcg"]]

    frames = []
    for source_name, config in SOURCES.items():
        frame = resolve_source(config, usda_rae, imputed)
        frame.insert(1, "source", source_name)
        frames.append(frame)
        print(f"[VITAMIN_A] {source_name}: {frame[SOURCE_COLUMN].value_counts().to_dict()}")
    provenance = pd.concat(frames, ignore_index=True)

    values = provenance.set_index("food_id")[TARGET_COLUMN]
    repository[TARGET_COLUMN] = repository["food_id"].map(values)
    records = repository.to_dict("records")
    repository["missing_nutrient_count"] = [compute_missing_nutrient_count(r) for r in records]
    repository["completeness_score"] = [compute_completeness_score(r) for r in records]

    filled = repository[TARGET_COLUMN].notna()
    flagged = int(provenance.apply(needs_review, axis=1).sum())
    print(f"[VITAMIN_A] vitamin_a_mcg terisi {int(filled.sum())}/{len(repository)} baris, {flagged} perlu tinjau manual")
    if args.dry_run:
        return 0

    repository.to_csv(REPOSITORY_PATH, index=False, encoding="utf-8")
    provenance.to_csv(PROVENANCE_PATH, index=False, encoding="utf-8")
    write_review(provenance, repository)
    print(f"[VITAMIN_A] wrote {REPOSITORY_PATH.name}, {PROVENANCE_PATH.name}, {REVIEW_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
