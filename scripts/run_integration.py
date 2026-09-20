from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import (
    IMPUTATION_SUMMARY_REPORT_PATH,
    MYFCD_IMPUTED_BASELINE_PATHS,
    MYFCD_IMPUTED_CROSSDB_PATH,
    MYFCD_IMPUTED_MISSFOREST_PATH,
    NUTRITION_REPOSITORY_IMPUTED_PATH,
    TKPI_IMPUTED_BASELINE_PATHS,
    TKPI_IMPUTED_MISSFOREST_PATH,
)
from src.imputation import io_utils
from src.imputation.integrate import assemble_integrated

ROOT = Path(__file__).resolve().parents[1]


def _load_required_csv(label: str, path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(
            f"Required Stage 3 output '{label}' not found at {path}. "
            "Run the corresponding milestone's script (baseline/missforest) first."
        )
    df = pd.read_csv(path)
    print(f"[IMPUTE] loaded {label}: {len(df)} rows from {path.name}")
    return df


def load_all_sources() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    tkpi_sources: dict[str, pd.DataFrame] = {
        "enriched": io_utils.load_enriched("TKPI"),
        "missforest": _load_required_csv("tkpi_missforest", TKPI_IMPUTED_MISSFOREST_PATH),
    }
    for method, path in TKPI_IMPUTED_BASELINE_PATHS.items():
        tkpi_sources[f"baseline_{method}"] = _load_required_csv(f"tkpi_baseline_{method}", path)

    myfcd_sources: dict[str, pd.DataFrame] = {
        "enriched": io_utils.load_enriched("MyFCD"),
        "missforest": _load_required_csv("myfcd_missforest", MYFCD_IMPUTED_MISSFOREST_PATH),
        "crossdb": _load_required_csv("myfcd_crossdb", MYFCD_IMPUTED_CROSSDB_PATH),
    }
    for method, path in MYFCD_IMPUTED_BASELINE_PATHS.items():
        myfcd_sources[f"baseline_{method}"] = _load_required_csv(f"myfcd_baseline_{method}", path)

    return tkpi_sources, myfcd_sources


def write_summary_report(stats: dict[str, dict[str, int]], total_rows: int) -> None:
    lines = [
        "# Imputation Summary",
        "",
        f"- Total rows: {total_rows}",
        "- Per-nutrient cell resolution, routed via data_processed/availability_matrix.csv's strategi_imputasi.",
        "- resolved_count + unresolved_count always sums to total_rows for every nutrient (full accounting, no silent gaps).",
        "",
        "| Nutrient | Strategy | Resolved (internal) | Resolved (cross-DB) | Resolved (USDA-borrow) | Unresolved |",
        "|---|---|---|---|---|---|",
    ]
    for nutrient, entry in stats.items():
        lines.append(
            f"| {nutrient} | {entry['strategy']} | {entry['resolved_internal']} | "
            f"{entry['resolved_crossdb']} | {entry['resolved_usda_borrow']} | {entry['unresolved']} |"
        )

    lines.append("")
    lines.append(
        "Nutrients with no strategy in availability_matrix.csv are labeled as not routed by "
        "Stage 2 and passed through from the enriched source unchanged."
    )
    lines.append(
        "vitamin_a_mcg has strategy \"Pinjam USDA (kosong di kedua basis)\" but is not among the 6 "
        "columns Stage 1 actually borrowed from USDA, so it remains fully unresolved (NaN) rather than fabricated."
    )

    IMPUTATION_SUMMARY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMPUTATION_SUMMARY_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[IMPUTE] wrote {IMPUTATION_SUMMARY_REPORT_PATH}")


def main() -> int:
    tkpi_sources, myfcd_sources = load_all_sources()
    integrated, stats = assemble_integrated(tkpi_sources, myfcd_sources)

    io_utils.write_output(integrated, NUTRITION_REPOSITORY_IMPUTED_PATH)
    write_summary_report(stats, total_rows=len(integrated))

    print(f"[IMPUTE] integrated dataset rows: {len(integrated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
