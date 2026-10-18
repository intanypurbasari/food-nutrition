"""Final step: integrate TKPI and MyFCD into one food composition dataset.

Run after run_integration.py, borrow_vitamin_a.py and fill_usda_nutrients.py.
See src/integration/database_merge.py for the merge rules.

Outputs:
- data_processed/nutrition_repository_integrated.csv             one row per distinct food
- data_processed/nutrition_repository_integrated_provenance.csv  food_id x nutrient -> value_source
- reports/integration_report.md                                  rows, merged pairs, provenance, conflicts
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import (
    INTEGRATED_PROVENANCE_PATH,
    NUTRITION_REPOSITORY_IMPUTED_PATH,
    NUTRITION_REPOSITORY_INTEGRATED_PATH,
    TKPI_MYFCD_LINKS_CURATED_PATH,
)
from src.imputation import io_utils
from src.integration.database_merge import MERGE_LEVEL, _measured, cell_provenance, merge_identical

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "integration_report.md"


def write_report(stacked: pd.DataFrame, integrated: pd.DataFrame, provenance: pd.DataFrame,
                 links: pd.DataFrame, conflicts: pd.DataFrame) -> None:
    pairs = links[links["match_level"] == MERGE_LEVEL]
    lines = [
        "# Integrasi TKPI + MyFCD",
        "",
        f"- Baris sebelum integrasi: {len(stacked)} (TKPI {int((stacked['source'] == 'TKPI').sum())}, "
        f"MyFCD {int((stacked['source'] == 'MyFCD').sum())})",
        f"- Pasangan dilebur (`{MERGE_LEVEL}` di tkpi_myfcd_links_curated.csv): {len(pairs)}",
        f"- Baris setelah integrasi: {len(integrated)}",
        "- Tautan lain: " + ", ".join(f"{k} {v}" for k, v in links["match_level"].value_counts().items()
                                      if k != MERGE_LEVEL) + " (tetap baris terpisah)",
        "",
        "Aturan nilai pasangan yang dilebur (per nutrisi): terukur di TKPI > terukur di MyFCD > nilai imputasi TKPI.",
        "",
        "## Pasangan yang dilebur",
        "",
        "| TKPI | MyFCD | Catatan |",
        "|---|---|---|",
    ]
    for pair in pairs.itertuples(index=False):
        lines.append(f"| {pair.tkpi_food_id} {pair.tkpi_food_name} | {pair.myfcd_food_id} {pair.myfcd_food_name} | {pair.note} |")
    filled = provenance[provenance["value_source"] == "measured_MyFCD"]
    filled = filled[filled["food_id"].isin(pairs["tkpi_food_id"])]
    lines += ["", f"Nilai TKPI yang tadinya hasil imputasi dan kini diganti nilai terukur MyFCD: {len(filled)} sel.", ""]

    lines += ["## Asal nilai (seluruh sel dataset terintegrasi)", "", "| Asal nilai | Jumlah sel | % |", "|---|---|---|"]
    counts = provenance["value_source"].value_counts()
    for label, n in counts.items():
        lines.append(f"| {label} | {n} | {100 * n / len(provenance):.1f} |")

    lines += ["", "## Konflik (terukur di kedua basis data; nilai TKPI dipakai)", ""]
    if conflicts.empty:
        lines.append("- Tidak ada.")
    else:
        lines += ["| Pangan | Nutrisi | TKPI | MyFCD | Selisih relatif |", "|---|---|---|---|---|"]
        for c in conflicts.sort_values("rel_diff", ascending=False).itertuples(index=False):
            rel = "" if pd.isna(c.rel_diff) else f"{c.rel_diff:.0%}"
            lines.append(f"| {c.food_name} | {c.nutrient} | {c.tkpi_value:g} | {c.myfcd_value:g} | {rel} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    stacked = pd.read_csv(NUTRITION_REPOSITORY_IMPUTED_PATH)
    clean = pd.concat(
        [pd.read_csv(ROOT / "data_clean" / "tkpi_clean.csv"), pd.read_csv(ROOT / "data_clean" / "myfcd_clean.csv")],
        ignore_index=True,
    )
    selection = io_utils.load_method_selection()
    if selection is None:
        raise FileNotFoundError("data_processed/method_selection.csv is required; run select_imputation_methods.py")
    vitamin_a = pd.read_csv(ROOT / "data_processed" / "vitamin_a_provenance.csv")
    usda = pd.read_csv(ROOT / "data_processed" / "usda_nutrients_provenance.csv")
    links = pd.read_csv(TKPI_MYFCD_LINKS_CURATED_PATH)

    provenance = cell_provenance(stacked, _measured(clean), selection, vitamin_a, usda)
    integrated, provenance, conflicts = merge_identical(stacked, provenance, links)

    integrated.to_csv(NUTRITION_REPOSITORY_INTEGRATED_PATH, index=False, encoding="utf-8")
    provenance.to_csv(INTEGRATED_PROVENANCE_PATH, index=False, encoding="utf-8")
    write_report(stacked, integrated, provenance, links, conflicts)
    print(f"[INTEGRATE] {len(stacked)} -> {len(integrated)} rows; {len(conflicts)} conflicting measured cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
