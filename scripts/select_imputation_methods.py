"""Choose the imputation method per source x nutrient from the hold-out evaluation.

Reads reports/holdout_evaluation.csv (scripts/run_holdout_evaluation.py) and
writes data_processed/method_selection.csv, which run_integration.py and the
bootstrap use instead of the single-method routing.

Rule
----
1. Candidates are the methods scored for that source x nutrient (mean, median,
   median per food group,
   KNN, MICE, MissForest; for MyFCD also the cross-DB transfer from TKPI).
2. Every method whose pooled nRMSE is within TOLERANCE of the lowest counts as
   tied. Among tied methods the first in PREFERENCE wins: multivariate methods
   keep between-food variation, whereas mean/median fill one constant per
   nutrient, so they are chosen only when clearly better.
3. A nutrient with no observed value in a source cannot be evaluated or imputed
   internally; it takes the cross-DB transfer (MyFCD) as its only option.
4. Anything else without a score keeps MissForest (the Stage 3 default).

Outputs:
- data_processed/method_selection.csv
- reports/method_selection.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS, METHOD_SELECTION_PATH
from src.imputation import io_utils

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_SUMMARY_PATH = ROOT / "reports" / "holdout_evaluation.csv"
REPORT_PATH = ROOT / "reports" / "method_selection.md"

TOLERANCE = 0.02
# Ties go to the simpler variant: indicators must earn their place.
PREFERENCE = ["missforest", "missforest_ind", "crossdb", "mice", "knn", "group_median", "median", "mean"]
DEFAULT_METHOD = "missforest"


def choose(block: pd.DataFrame, tolerance: float) -> tuple[str, str]:
    """Return (method, reason) for one source x nutrient block of the hold-out summary."""
    best = block["nrmse"].min()
    tied = set(block.loc[block["nrmse"] <= best + tolerance, "method"])
    method = next(m for m in PREFERENCE if m in tied)
    lowest = block.loc[block["nrmse"].idxmin(), "method"]
    if method == lowest:
        reason = "nRMSE terendah"
    else:
        reason = f"selisih <= {tolerance:g} dari {lowest}; diutamakan metode multivariat"
    return method, reason


def select(summary: pd.DataFrame, enriched: dict[str, pd.DataFrame], tolerance: float) -> pd.DataFrame:
    rows = []
    tkpi_observed = set(io_utils.observed_columns(enriched["TKPI"]))
    for source, frame in enriched.items():
        observed = set(io_utils.observed_columns(frame))
        for nutrient in IMPUTATION_NUTRIENT_FIELDS:
            block = summary[(summary["source"] == source) & (summary["nutrient"] == nutrient)].dropna(subset=["nrmse"])
            n_observed = int(frame[nutrient].notna().sum()) if nutrient in frame else 0
            if not block.empty:
                method, reason = choose(block, tolerance)
                chosen = block.set_index("method").loc[method]
                missforest = block.set_index("method")["nrmse"].get("missforest")
                rows.append(
                    {
                        "source": source,
                        "nutrient": nutrient,
                        "method": method,
                        "reason": reason,
                        "n_observed": n_observed,
                        "n_holdout_cells": int(chosen["n_holdout_cells"]),
                        "nrmse": round(float(chosen["nrmse"]), 4),
                        "nrmse_missforest": None if missforest is None else round(float(missforest), 4),
                    }
                )
            elif nutrient not in observed:
                if source == "MyFCD" and nutrient in tkpi_observed:
                    rows.append({"source": source, "nutrient": nutrient, "method": "crossdb",
                                 "reason": "tidak ada nilai terukur di MyFCD; hanya transfer dari TKPI yang mungkin",
                                 "n_observed": 0})
                # Not observed in TKPI either (vitamin_a_mcg): filled later by borrow_vitamin_a.py.
            else:
                rows.append({"source": source, "nutrient": nutrient, "method": DEFAULT_METHOD,
                             "reason": "tidak cukup nilai terukur untuk hold-out; metode bawaan Tahap 3",
                             "n_observed": n_observed})
    return pd.DataFrame(rows)


def write_report(selection: pd.DataFrame, tolerance: float) -> None:
    lines = [
        "# Pemilihan Metode Imputasi per Nutrisi",
        "",
        "Sumber: `reports/holdout_evaluation.csv` (nRMSE gabungan seluruh sel hold-out).",
        "",
        f"1. Metode dengan nRMSE terendah dipilih. Metode yang selisihnya <= {tolerance:g} dianggap setara; "
        "di antara yang setara diutamakan " + " > ".join(PREFERENCE) + ".",
        "2. Nutrisi tanpa nilai terukur di MyFCD memakai cross-DB transfer dari TKPI.",
        "3. Nutrisi lain tanpa skor hold-out memakai MissForest (bawaan Tahap 3).",
        "",
    ]
    for source in ["TKPI", "MyFCD"]:
        part = selection[selection["source"] == source]
        lines += [f"## {source}", "", "| Nutrisi | Metode | nRMSE | nRMSE MissForest | n terukur | Alasan |", "|---|---|---|---|---|---|"]
        for row in part.itertuples(index=False):
            nrmse = "" if pd.isna(getattr(row, "nrmse", None)) else f"{row.nrmse:.3f}"
            mf = "" if pd.isna(getattr(row, "nrmse_missforest", None)) else f"{row.nrmse_missforest:.3f}"
            lines.append(f"| {row.nutrient} | **{row.method}** | {nrmse} | {mf} | {row.n_observed} | {row.reason} |")
        counts = part["method"].value_counts()
        lines += ["", "Jumlah nutrisi per metode: " + ", ".join(f"{m} {n}" for m, n in counts.items()), ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = parser.parse_args()

    summary = pd.read_csv(HOLDOUT_SUMMARY_PATH)
    enriched = {source: io_utils.load_enriched(source) for source in ["TKPI", "MyFCD"]}
    selection = select(summary, enriched, args.tolerance)

    METHOD_SELECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(METHOD_SELECTION_PATH, index=False)
    write_report(selection, args.tolerance)
    print(selection.groupby("source")["method"].value_counts().to_string())
    print(f"[SELECT] wrote {METHOD_SELECTION_PATH.name}, {REPORT_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
