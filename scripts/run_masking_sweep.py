"""Masking sweep: imputation error as the share of hidden observed cells grows.

For each source, 5% to 50% of the observed cells of every nutrient are
hidden (independent masks per seed), every method imputes the masked frame,
and nRMSE is computed per nutrient on the hidden cells. As in Indriani et
al. (2026, Array 32:101428), each seed is summarised by the median of its
per-nutrient nRMSE, and methods are reported as mean +/- sd over seeds.
For MyFCD the cross-DB transfer (MissForest fitted once on the full TKPI)
is applied to the same masks, which shows how its advantage over
within-MyFCD imputation changes as the target becomes sparser.

Paired comparisons over seeds use the Wilcoxon signed-rank test with a Holm
correction across fractions and the Hodges-Lehmann shift (median of Walsh
averages of the per-seed differences).

Outputs (reports/):
- masking_sweep_raw.csv     source x method x fraction x seed x nutrient -> nrmse
- masking_sweep.csv         per-seed median nRMSE, mean and sd over seeds
- masking_sweep_tests.csv   paired tests for the focal method pairs
- runtime.csv               seconds per full imputation call on the unmasked data
- masking_sweep.md          readable summary
"""

from __future__ import annotations

import argparse
import sys
import time
import warnings
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS, RANDOM_SEED
from src.evaluation.holdout import _numeric, apply_masks, make_masks, score
from src.imputation import io_utils
from src.imputation.baselines import group_median_impute, knn_impute, mean_impute, mice_impute, softimpute_impute
from src.imputation.cross_transfer import apply_fitted_imputer
from src.imputation.missforest_imputer import fit_random_forest_imputer, missforest_impute

REPORTS = Path(__file__).resolve().parents[1] / "reports"
FRACTIONS = [round(0.05 * k, 2) for k in range(1, 11)]
METHODS = {
    "mean": mean_impute,
    "group_median": group_median_impute,
    "knn": knn_impute,
    "mice": mice_impute,
    "softimpute": softimpute_impute,
    "missforest": missforest_impute,
}
# Focal paired comparisons: (source, method A, method B); shift = nRMSE_A - nRMSE_B, positive favours B.
PAIRS = [("TKPI", "knn", "softimpute"), ("TKPI", "softimpute", "missforest"),
         ("MyFCD", "missforest", "crossdb"), ("MyFCD", "softimpute", "crossdb")]


def one_run(source: str, frame: pd.DataFrame, columns: list[str], fraction: float, seed: int, methods: dict) -> list[dict]:
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(seed)
    masks = make_masks(frame, columns, fraction, rng, min_observed=10)
    masked = apply_masks(frame, masks)
    rows = []
    for method, impute in methods.items():
        imputed = impute(masked, list(masks))
        for column, hidden in masks.items():
            predicted = _numeric(imputed.loc[hidden, column])
            if predicted.isna().any():
                continue
            rows.append({"source": source, "method": method, "fraction": fraction, "seed": seed, "nutrient": column,
                         "nrmse": score(_numeric(frame.loc[hidden, column]), predicted)["nrmse"]})
    return rows


def hodges_lehmann(diff: np.ndarray) -> float:
    walsh = [(a + b) / 2 for (i, a), (j, b) in combinations_with_replacement(enumerate(diff), 2)]
    return float(np.median(walsh))


def paired_tests(per_seed: pd.DataFrame) -> pd.DataFrame:
    out = []
    for source, a, b in PAIRS:
        block = per_seed[(per_seed["source"] == source) & per_seed["method"].isin([a, b])]
        if block.empty:
            continue
        rows = []
        for fraction, part in block.groupby("fraction"):
            wide = part.pivot(index="seed", columns="method", values="median_nrmse").dropna()
            diff = (wide[a] - wide[b]).to_numpy()
            p = wilcoxon(diff).pvalue if np.any(diff != 0) else 1.0
            rows.append({"source": source, "method_a": a, "method_b": b, "fraction": fraction, "n_seeds": len(diff),
                         "mean_a": wide[a].mean(), "mean_b": wide[b].mean(), "hl_shift": hodges_lehmann(diff), "p": p})
        rows = pd.DataFrame(rows).sort_values("p").reset_index(drop=True)
        m = len(rows)
        rows["p_holm"] = np.minimum(1.0, np.maximum.accumulate([(m - k) * p for k, p in enumerate(rows["p"])]))
        out.append(rows.sort_values("fraction"))
    return pd.concat(out, ignore_index=True)


def runtimes(frames: dict, transfer, repeats: int) -> pd.DataFrame:
    rows = []
    for source, frame in frames.items():
        columns = io_utils.observed_columns(frame)
        methods = dict(METHODS)
        if source == "MyFCD":
            methods["crossdb"] = lambda df, cols: apply_fitted_imputer(transfer, df, cols)
        for method, impute in methods.items():
            seconds = []
            for _ in range(repeats):
                start = time.perf_counter()
                impute(frame, columns)
                seconds.append(time.perf_counter() - start)
            rows.append({"source": source, "method": method, "seconds_mean": np.mean(seconds), "seconds_sd": np.std(seconds)})
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, tests: pd.DataFrame, runtime: pd.DataFrame, seeds: int) -> None:
    lines = ["# Masking Sweep", "",
             f"- Fraksi sel terukur yang disembunyikan: {FRACTIONS[0]:.0%}-{FRACTIONS[-1]:.0%}; {seeds} seed per fraksi.",
             "- Angka: rerata ± sd (antar seed) dari median nRMSE per nutrisi; makin kecil makin baik.", ""]
    for source, part in summary.groupby("source", sort=False):
        table = part.pivot(index="fraction", columns="method", values="label")
        lines += [f"## {source}", "", "| Fraksi | " + " | ".join(table.columns) + " |", "|---" * (len(table.columns) + 1) + "|"]
        for fraction, row in table.iterrows():
            lines.append(f"| {fraction:.0%} | " + " | ".join(row.fillna("")) + " |")
        lines.append("")
    lines += ["## Uji berpasangan (Wilcoxon, koreksi Holm antar fraksi)", "",
              "| Sumber | A vs B | Fraksi | HL shift (A - B) | p Holm |", "|---|---|---|---|---|"]
    for r in tests.itertuples(index=False):
        lines.append(f"| {r.source} | {r.method_a} vs {r.method_b} | {r.fraction:.0%} | {r.hl_shift:+.3f} | {r.p_holm:.3f} |")
    lines += ["", "## Waktu komputasi (detik per imputasi penuh)", "", "| Sumber | Metode | Detik |", "|---|---|---|"]
    for r in runtime.itertuples(index=False):
        lines.append(f"| {r.source} | {r.method} | {r.seconds_mean:.2f} ± {r.seconds_sd:.2f} |")
    (REPORTS / "masking_sweep.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--runtime-repeats", type=int, default=3)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    frames = {source: io_utils.load_enriched(source) for source in ["TKPI", "MyFCD"]}
    print("[SWEEP] fitting cross-DB transfer imputer on full TKPI")
    transfer = fit_random_forest_imputer(frames["TKPI"], random_state=RANDOM_SEED)
    jobs = []
    for source, frame in frames.items():
        columns = [c for c in IMPUTATION_NUTRIENT_FIELDS if c in frame.columns]
        methods = dict(METHODS)
        if source == "MyFCD":
            methods["crossdb"] = lambda df, cols: apply_fitted_imputer(transfer, df, cols)
        for fraction in FRACTIONS:
            for seed in range(args.seeds):
                jobs.append(delayed(one_run)(source, frame, columns, fraction, RANDOM_SEED + seed, methods))
    results = Parallel(n_jobs=args.n_jobs, verbose=5)(jobs)
    raw = pd.DataFrame([row for rows in results for row in rows])
    REPORTS.mkdir(exist_ok=True)
    raw.to_csv(REPORTS / "masking_sweep_raw.csv", index=False)

    per_seed = raw.groupby(["source", "method", "fraction", "seed"])["nrmse"].median().rename("median_nrmse").reset_index()
    summary = per_seed.groupby(["source", "method", "fraction"])["median_nrmse"].agg(["mean", "std"]).reset_index()
    summary["label"] = [f"{m:.3f} ± {s:.3f}" for m, s in zip(summary["mean"], summary["std"])]
    summary.drop(columns="label").to_csv(REPORTS / "masking_sweep.csv", index=False)
    tests = paired_tests(per_seed)
    tests.to_csv(REPORTS / "masking_sweep_tests.csv", index=False)
    runtime = runtimes(frames, transfer, args.runtime_repeats)
    runtime.to_csv(REPORTS / "runtime.csv", index=False)
    write_report(summary, tests, runtime, args.seeds)
    print("[SWEEP] wrote reports/masking_sweep*.csv, runtime.csv, masking_sweep.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
