"""Figures 2-4 of the manuscript, rebuilt from the repository data.

- missingness correlation (Fig. 2 TKPI, Fig. 3 MyFCD): the correlation matrix of the missing-value
  indicators is recomputed from data_clean/*_clean.csv and written to reports/missing_corr_*.csv
  (same layout as scripts/Analisis Pola Missingness.ipynb: nutrient order of the notebook, rounded to
  4 decimals, nutrients whose indicator is constant dropped), so the CSVs always match the cleaned data.
- hold-out nRMSE (Fig. 4): heat map of reports/holdout_evaluation.csv, all methods incl. SoftImpute and
  the Atwater calculation of energy.

Outputs: reports/missing_corr_TKPI.csv, reports/missing_corr_MyFCD.csv and, in reports/figures/,
dsj_fig2_missingness_tkpi.png, dsj_fig3_missingness_myfcd.png, dsj_fig4_holdout_nrmse.png.

Usage:
    python scripts/plot_dsj_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT = REPORTS / "figures"
# Nutrient order of the missingness notebook (macronutrients, then minerals, then vitamins).
NUTRIENTS = ["energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_g", "water_g", "ash_g",
             "calcium_mg", "phosphorus_mg", "iron_mg", "sodium_mg", "potassium_mg", "copper_mg", "zinc_mg",
             "retinol_mcg", "beta_carotene_mcg", "carotene_total_mcg", "vitamin_a_mcg",
             "vitamin_b1_mg", "vitamin_b2_mg", "niacin_mg", "vitamin_c_mg"]
SOURCES = {"TKPI": ROOT / "data_clean" / "tkpi_clean.csv", "MyFCD": ROOT / "data_clean" / "myfcd_clean.csv"}
INK, MUTED = "#1f1f1f", "#5a5a5a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})


def missingness_corr(path: Path) -> pd.DataFrame:
    """Correlation (phi) of the missing-value indicators of the nutrients that are neither always nor never missing."""
    frame = pd.read_csv(path)
    for column in NUTRIENTS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    indicators = frame[NUTRIENTS].isna().astype(int)
    kept = [c for c in NUTRIENTS if indicators[c].nunique() > 1]
    return indicators[kept].corr().round(4)


def missingness_heatmap(matrix: pd.DataFrame, title: str, path: Path) -> None:
    n = len(matrix)
    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    image = ax.imshow(matrix.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(n)); ax.set_xticklabels(matrix.columns, rotation=60, ha="right", fontsize=7.5)
    ax.set_yticks(range(n)); ax.set_yticklabels(matrix.index, fontsize=7.5)
    for i in range(n):
        for j in range(n):
            v = matrix.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.2, color="white" if abs(v) > 0.6 else INK)
    ax.set_xticks(np.arange(-0.5, n), minor=True); ax.set_yticks(np.arange(-0.5, n), minor=True)
    ax.grid(which="minor", color="white", lw=0.6); ax.tick_params(which="minor", length=0)
    bar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.02)
    bar.set_label("Correlation of missingness indicators (r)")
    ax.set_title(title, fontsize=10, color=INK)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def holdout_heatmap(path: Path) -> None:
    scores = pd.read_csv(REPORTS / "holdout_evaluation.csv")
    order = ["mean", "median", "group_median", "knn", "mice", "softimpute", "missforest", "missforest_ind", "crossdb", "atwater"]
    label = {"mean": "Mean", "median": "Median", "group_median": "Group median", "knn": "KNN", "mice": "MICE",
             "softimpute": "SoftImpute", "missforest": "MissForest", "missforest_ind": "MissForest\n+ indicators",
             "crossdb": "Cross-DB\ntransfer", "atwater": "Atwater\n(energy)"}
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 6.4), gridspec_kw={"width_ratios": [7, 7], "wspace": 0.6})
    for ax, source in zip(axes, ["TKPI", "MyFCD"]):
        table = scores[scores.source == source].pivot(index="nutrient", columns="method", values="nrmse")
        table = table[[c for c in order if c in table.columns]]
        table = table.loc[table.min(axis=1).sort_values().index]
        clipped = np.clip(table.values, 0, 2)
        image = ax.imshow(clipped, cmap="RdBu_r", vmin=0, vmax=2, aspect="auto")
        best = np.nanargmin(table.values, axis=1)
        for i in range(table.shape[0]):
            for j in range(table.shape[1]):
                v = table.values[i, j]
                if np.isnan(v):
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#e6e6e6", lw=0))
                    ax.text(j, i, "–", ha="center", va="center", fontsize=6, color=MUTED)
                    continue
                ax.text(j, i, f"{v:.2f}" if v < 10 else f"{v:.0f}", ha="center", va="center", fontsize=5.6,
                        weight="bold" if j == best[i] else "normal",
                        color="white" if abs(clipped[i, j] - 1) > 0.6 else INK)
            ax.add_patch(plt.Rectangle((best[i] - 0.5, i - 0.5), 1, 1, fill=False, ec=INK, lw=1.2))
        ax.set_xticks(range(table.shape[1]))
        ax.set_xticklabels([label[c] for c in table.columns], rotation=60, ha="right", fontsize=7)
        ax.set_yticks(range(table.shape[0])); ax.set_yticklabels(table.index, fontsize=7)
        ax.set_title(source, fontsize=10, color=INK)
        ax.tick_params(length=0)
    bar = fig.colorbar(image, ax=axes, fraction=0.03, pad=0.02, extend="max")
    bar.set_label("nRMSE (1.0 = predicting the mean; colour capped at 2)")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    names = {"TKPI": "dsj_fig2_missingness_tkpi.png", "MyFCD": "dsj_fig3_missingness_myfcd.png"}
    for source, path in SOURCES.items():
        matrix = missingness_corr(path)
        matrix.to_csv(REPORTS / f"missing_corr_{source}.csv")
        missingness_heatmap(matrix, f"{source} ({len(matrix)} nutrients with non-constant missingness)", OUT / names[source])
        print(f"[DSJ-FIG] {source}: {len(matrix)} nutrients -> reports/missing_corr_{source}.csv, figures/{names[source]}")
    holdout_heatmap(OUT / "dsj_fig4_holdout_nrmse.png")
    print("[DSJ-FIG] wrote figures/dsj_fig4_holdout_nrmse.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
