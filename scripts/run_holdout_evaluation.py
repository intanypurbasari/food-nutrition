"""Stage 4: hold-out evaluation (RMSE / nRMSE) of every Stage 3 imputation method.

Hides 15% of the observed cells of each nutrient (per source), imputes them
with mean, median, KNN, MICE and MissForest, and for MyFCD also with the
cross-database transfer (MissForest fit on the full TKPI). Repeated with
independent masks; see src/evaluation/holdout.py for the metric definitions.

Outputs:
- reports/holdout_evaluation_raw.csv   one row per held-out cell x method x repeat (true vs imputed)
- reports/holdout_evaluation.csv       pooled RMSE / nRMSE / MAE + best method per nutrient
- reports/holdout_evaluation.md        readable summary tables
(with --exclude-flagged-outliers the files are named holdout_evaluation_no_outliers*)
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS, RANDOM_SEED
from src.evaluation.holdout import HoldoutConfig, evaluate_source, summarise
from src.imputation import io_utils
from src.imputation.baselines import group_median_impute, knn_impute, mean_impute, median_impute, mice_impute
from src.imputation.cross_transfer import apply_fitted_imputer
from src.imputation.missforest_imputer import fit_random_forest_imputer, missforest_impute

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
QUALITY_REPORT_PATH = ROOT / "reports" / "data_quality_report.json"

BASE_METHODS = {
    "mean": mean_impute,
    "median": median_impute,
    "group_median": group_median_impute,
    "knn": knn_impute,
    "mice": mice_impute,
    "missforest": missforest_impute,
}
METHOD_ORDER = ["mean", "median", "group_median", "knn", "mice", "missforest", "crossdb"]


def _fmt(value: float) -> str:
    return "" if pd.isna(value) else f"{value:.3f}"


def flagged_outliers() -> set[str]:
    """food_id of rows flagged as outlier_* by validate_dataset.py."""
    report = json.loads(QUALITY_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        warning["food_id"]
        for source in report.get("sources", [])
        for warning in source.get("warnings", [])
        if warning["type"].startswith("outlier_")
    }


def write_report(summary: pd.DataFrame, configs: dict[str, HoldoutConfig], excluded: set[str], path: Path) -> None:
    config = configs["TKPI"]
    lines = [
        "# Hold-out Evaluation",
        "",
        f"- {config.fraction:.0%} nilai terukur per nutrisi disembunyikan; mask independen per pengulangan (seed {config.seed}+r): "
        + ", ".join(f"{source} {c.repeats}x" for source, c in configs.items())
        + ".",
        f"- Nutrisi dengan kurang dari {config.min_observed} nilai terukur tidak dievaluasi.",
        "- Outlier tertandai dikeluarkan: " + (", ".join(sorted(excluded)) if excluded else "tidak (semua baris dipakai)") + ".",
        "- nRMSE = RMSE / sd(nilai asli yang disembunyikan). 1,0 setara menebak rerata; makin kecil makin baik.",
        "- Angka di tabel adalah nRMSE gabungan seluruh sel hold-out dari semua pengulangan; **tebal** = metode terbaik untuk nutrisi itu.",
        "",
    ]
    for source in ["TKPI", "MyFCD"]:
        part = summary[summary["source"] == source]
        if part.empty:
            continue
        methods = [m for m in METHOD_ORDER if m in set(part["method"])]
        lines += [f"## {source}", "", "| Nutrisi | n terukur | n sel hold-out | " + " | ".join(methods) + " |"]
        lines.append("|---|---|---|" + "---|" * len(methods))
        for nutrient, block in part.groupby("nutrient", sort=False):
            by_method = block.set_index("method")
            best = block["best_method"].iloc[0]
            cells = []
            for method in methods:
                value = _fmt(by_method["nrmse"].get(method))
                cells.append(f"**{value}**" if method == best and value else value)
            first = block.iloc[0]
            lines.append(f"| {nutrient} | {first['n_observed']} | {first['n_holdout_cells']} | " + " | ".join(cells) + " |")
        wins = part.drop_duplicates("nutrient")["best_method"].value_counts()
        lines += ["", "Jumlah nutrisi per metode terbaik: " + ", ".join(f"{m} {n}" for m, n in wins.items()), ""]

    myfcd = summary[(summary["source"] == "MyFCD") & summary["method"].isin(["missforest", "crossdb"])]
    pivot = myfcd.pivot(index="nutrient", columns="method", values="nrmse").dropna()
    if not pivot.empty:
        better = int((pivot["crossdb"] < pivot["missforest"]).sum())
        lines += [
            "## MyFCD: cross-DB transfer vs MissForest internal",
            "",
            f"Cross-DB transfer (dilatih pada TKPI) lebih akurat pada {better} dari {len(pivot)} nutrisi.",
            "",
            "| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |",
            "|---|---|---|---|",
        ]
        for nutrient, row in pivot.iterrows():
            lines.append(f"| {nutrient} | {_fmt(row['missforest'])} | {_fmt(row['crossdb'])} | {_fmt(row['crossdb'] - row['missforest'])} |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fraction", type=float, default=0.15)
    parser.add_argument("--repeats-tkpi", type=int, default=3)
    parser.add_argument("--repeats-myfcd", type=int, default=10, help="MyFCD is small and cheap to refit; more repeats steady its few held-out cells")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--exclude-flagged-outliers", action="store_true",
                        help="sensitivity run without rows flagged outlier_* in reports/data_quality_report.json")
    args = parser.parse_args()
    configs = {
        "TKPI": HoldoutConfig(fraction=args.fraction, repeats=args.repeats_tkpi, seed=args.seed),
        "MyFCD": HoldoutConfig(fraction=args.fraction, repeats=args.repeats_myfcd, seed=args.seed),
    }
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*ConvergenceWarning.*")

    tkpi = io_utils.load_enriched("TKPI")
    myfcd = io_utils.load_enriched("MyFCD")
    excluded: set[str] = set()
    if args.exclude_flagged_outliers:
        excluded = flagged_outliers()
        tkpi = tkpi[~tkpi["food_id"].isin(excluded)].reset_index(drop=True)
        myfcd = myfcd[~myfcd["food_id"].isin(excluded)].reset_index(drop=True)
        print(f"[HOLDOUT] excluded flagged outliers: {sorted(excluded)}")

    print("[HOLDOUT] fitting cross-DB transfer imputer on full TKPI")
    transfer_imputer = fit_random_forest_imputer(tkpi, random_state=args.seed)
    myfcd_methods = {**BASE_METHODS, "crossdb": lambda df, columns: apply_fitted_imputer(transfer_imputer, df, columns)}

    results = pd.concat(
        [
            evaluate_source("TKPI", tkpi, IMPUTATION_NUTRIENT_FIELDS, BASE_METHODS, configs["TKPI"]),
            evaluate_source("MyFCD", myfcd, IMPUTATION_NUTRIENT_FIELDS, myfcd_methods, configs["MyFCD"]),
        ],
        ignore_index=True,
    )
    stem = "holdout_evaluation_no_outliers" if args.exclude_flagged_outliers else "holdout_evaluation"
    REPORTS.mkdir(parents=True, exist_ok=True)
    results.to_csv(REPORTS / f"{stem}_raw.csv", index=False)
    n_observed = {
        (source, column): int(frame[column].notna().sum())
        for source, frame in {"TKPI": tkpi, "MyFCD": myfcd}.items()
        for column in IMPUTATION_NUTRIENT_FIELDS
        if column in frame.columns
    }
    summary = summarise(results, n_observed)
    summary.to_csv(REPORTS / f"{stem}.csv", index=False)
    write_report(summary, configs, excluded, REPORTS / f"{stem}.md")
    print(f"[HOLDOUT] wrote reports/{stem}_raw.csv, {stem}.csv, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
