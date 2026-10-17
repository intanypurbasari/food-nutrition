"""Stage 4: bootstrap (B = 50) uncertainty for every MissForest / cross-DB imputed cell.

See src/evaluation/bootstrap.py for the resampling scheme. Run after the
Stage 3 imputation (it reads *_enriched.csv for the originally missing cells
and nutrition_repository_imputed.csv for the point estimates).

Outputs:
- data_processed/imputation_uncertainty.csv  per imputed cell: point estimate, bootstrap
                                             mean/sd, 95% percentile interval, relative sd
- reports/uncertainty_summary.csv            per source x nutrient, with high_uncertainty flag
- reports/uncertainty_summary.md             readable summary

One TKPI fit takes ~1.5 min, so B = 50 takes roughly 20-25 min on 4 cores.
"""

from __future__ import annotations

import argparse
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import NUTRITION_REPOSITORY_IMPUTED_PATH, RANDOM_SEED
from src.evaluation.bootstrap import BootstrapConfig, numeric, robust_scale, run_bootstrap, summarise_uncertainty
from src.imputation import io_utils

ROOT = Path(__file__).resolve().parents[1]
CELLS_PATH = ROOT / "data_processed" / "imputation_uncertainty.csv"
SUMMARY_PATH = ROOT / "reports" / "uncertainty_summary.csv"
REPORT_PATH = ROOT / "reports" / "uncertainty_summary.md"


def write_report(summary: pd.DataFrame, config: BootstrapConfig, threshold: float, minutes: float | None) -> None:
    runtime = "" if minutes is None else f"; waktu {minutes:.0f} menit"
    lines = [
        "# Bootstrap Uncertainty",
        "",
        f"- B = {config.n_boot} resample baris (dengan pengembalian) per sumber, seed {config.seed}+b{runtime}.",
        "- Tiap replikasi melatih ulang MissForest pada resample lalu mengimputasi data asli, jadi tiap sel yang aslinya kosong mendapat B prediksi.",
        "- relative_sd = sd bootstrap / sebaran nilai terukur nutrisi itu di sumber yang sama. Sebaran diukur dengan IQR/1,349 "
        "(setara sd untuk data normal, tetapi tahan outlier); bila IQR = 0, dipakai sd.",
        "- Pasangan dengan kurang dari 5 sel imputasi tidak ditandai.",
        f"- Nutrisi **ditandai** (high_uncertainty) bila median relative_sd > {threshold:g}.",
        "",
        "| Sumber | Nutrisi | Metode | n sel imputasi | median sd | median lebar CI 95% | median relative_sd | p90 relative_sd | Tanda |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in summary.sort_values(["source", "median_relative_sd"], ascending=[False, False]).itertuples(index=False):
        lines.append(
            f"| {row.source} | {row.nutrient} | {row.method} | {row.n_imputed} | {row.median_boot_sd:.3g} | "
            f"{row.median_ci_width:.3g} | {row.median_relative_sd:.3f} | {row.p90_relative_sd:.3f} | "
            f"{'⚠️ tinggi' if row.high_uncertainty else ''} |"
        )
    flagged = summary[summary["high_uncertainty"]]
    lines += ["", f"Nutrisi berketidakpastian tinggi: {len(flagged)} dari {len(summary)} pasangan sumber x nutrisi.", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n-boot", type=int, default=50)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--n-jobs", type=int, default=-1, help="parallel replicates (-1 = all cores)")
    parser.add_argument("--flag-threshold", type=float, default=0.5, help="flag nutrients whose median relative_sd exceeds this")
    parser.add_argument("--summary-only", action="store_true",
                        help="recompute the summary from an existing imputation_uncertainty.csv without rerunning the bootstrap")
    args = parser.parse_args()
    config = BootstrapConfig(n_boot=args.n_boot, seed=args.seed, n_jobs=args.n_jobs)
    warnings.filterwarnings("ignore")

    tkpi = io_utils.load_enriched("TKPI")
    myfcd = io_utils.load_enriched("MyFCD")
    internal = io_utils.columns_for_strategy("Imputasi internal per basis")
    crossdb = io_utils.columns_for_strategy("Cross-DB transfer / USDA")

    if args.summary_only:
        cells = pd.read_csv(CELLS_PATH).drop(columns=["relative_sd", "high_uncertainty_nutrient"], errors="ignore")
        minutes = None
    else:
        start = time.time()
        cells = run_bootstrap(tkpi, myfcd, internal + crossdb, internal, crossdb, config)
        minutes = (time.time() - start) / 60
        repository = pd.read_csv(NUTRITION_REPOSITORY_IMPUTED_PATH).set_index("food_id")
        cells.insert(
            3,
            "imputed_value",
            [repository.at[food_id, nutrient] for food_id, nutrient in zip(cells["food_id"], cells["nutrient"])],
        )

    scale = {}
    for source, frame in {"TKPI": tkpi, "MyFCD": myfcd}.items():
        for nutrient in set(cells.loc[cells["source"] == source, "nutrient"]):
            values = numeric(frame[nutrient])
            # Nutrients with no observed value in this source (e.g. MyFCD
            # carotene_total_mcg) fall back to TKPI's spread.
            if values.notna().sum() < 2:
                values = numeric(tkpi[nutrient])
            scale[(source, nutrient)] = robust_scale(values)
    summary = summarise_uncertainty(cells, pd.Series(scale), args.flag_threshold)

    cells["relative_sd"] = [b / scale.get((s, n), float("nan")) for s, n, b in zip(cells["source"], cells["nutrient"], cells["boot_sd"])]
    flags = summary.set_index(["source", "nutrient"])["high_uncertainty"]
    cells["high_uncertainty_nutrient"] = [bool(flags.loc[(s, n)]) for s, n in zip(cells["source"], cells["nutrient"])]

    CELLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    cells.to_csv(CELLS_PATH, index=False)
    summary.to_csv(SUMMARY_PATH, index=False)
    write_report(summary, config, args.flag_threshold, minutes)
    print(f"[BOOTSTRAP] {len(cells)} imputed cells, {int(summary['high_uncertainty'].sum())} nutrient(s) flagged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
