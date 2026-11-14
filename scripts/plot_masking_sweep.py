"""Figures for the masking sweep (reports/masking_sweep*.csv -> reports/figures/).

- masking_sweep.png        nRMSE against the share of hidden cells, all methods, TKPI and MyFCD
- transfer_vs_internal.png MyFCD: cross-DB transfer against within-MyFCD MissForest and SoftImpute,
                           with the fractions where the Holm-corrected Wilcoxon test is significant marked
                           (colour of the mark = the method that is better)
- transfer_by_nutrient.png MyFCD: log2(nRMSE transfer / nRMSE MissForest) per nutrient and fraction;
                           the median across nutrients hides that transfer wins on some nutrients and
                           loses on others
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPORTS = Path(__file__).resolve().parents[1] / "reports"
OUT = REPORTS / "figures"
LABEL = {"mean": "Mean", "group_median": "Group median", "knn": "KNN", "mice": "MICE", "softimpute": "SoftImpute",
         "missforest": "MissForest", "crossdb": "Cross-DB transfer"}
# Fixed categorical order (identity, never re-cycled); mean is the grey reference.
COLOR = {"mean": "#9e9e9e", "group_median": "#8c6d31", "knn": "#e6550d", "mice": "#756bb1",
         "softimpute": "#3182bd", "missforest": "#31a354", "crossdb": "#d6278a"}
MARKER = {"mean": "o", "group_median": "s", "knn": "^", "mice": "v", "softimpute": "D", "missforest": "P", "crossdb": "*"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def lines(ax, part: pd.DataFrame, methods: list[str], ylim=None) -> None:
    for method in methods:
        m = part[part["method"] == method].sort_values("fraction")
        if m.empty:
            continue
        x = m["fraction"] * 100
        ax.plot(x, m["mean"], color=COLOR[method], marker=MARKER[method], ms=5, lw=2, label=LABEL[method])
        ax.fill_between(x, m["mean"] - m["std"], m["mean"] + m["std"], color=COLOR[method], alpha=0.12, lw=0)
    ax.axhline(1.0, color="#555555", lw=0.8, ls="--")
    ax.set_xlabel("Observed cells hidden (%)")
    ax.grid(axis="y", color="#e5e5e5", lw=0.6)
    if ylim:
        ax.set_ylim(*ylim)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(REPORTS / "masking_sweep.csv")
    tests = pd.read_csv(REPORTS / "masking_sweep_tests.csv")

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    order = ["mean", "group_median", "knn", "mice", "softimpute", "missforest", "crossdb"]
    for ax, source in zip(axes, ["TKPI", "MyFCD"]):
        lines(ax, summary[summary["source"] == source], order)
        ax.set_title(source)
    axes[0].set_ylabel("Median nRMSE across nutrients\n(mean ± sd over seeds)")
    handles, labels = [], []
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h); labels.append(l)
    fig.legend(handles, labels, loc="lower center", ncol=7, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "masking_sweep.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    myfcd = summary[summary["source"] == "MyFCD"]
    fig, ax = plt.subplots(figsize=(5.6, 4.3))
    lines(ax, myfcd, ["softimpute", "missforest", "crossdb"])
    sig = tests[(tests["source"] == "MyFCD") & (tests["method_a"] == "missforest") & (tests["method_b"] == "crossdb")]
    top = ax.get_ylim()[1]
    for r in sig.itertuples(index=False):
        if r.p_holm < 0.05:
            # hl_shift = MissForest - transfer; negative means MissForest has the lower error
            better = "missforest" if r.hl_shift < 0 else "crossdb"
            ax.text(r.fraction * 100, top, "*", ha="center", va="top", fontsize=14, color=COLOR[better])
    ax.set_title("MyFCD: transfer from TKPI vs within-MyFCD imputation")
    ax.set_ylabel("Median nRMSE across nutrients")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    ax.text(0.99, 0.98, "* Wilcoxon transfer vs MissForest, Holm p < 0.05\n(colour = method with lower error)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / "transfer_vs_internal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    raw = pd.read_csv(REPORTS / "masking_sweep_raw.csv")
    per = raw[raw["source"] == "MyFCD"].groupby(["nutrient", "method", "fraction"])["nrmse"].mean().unstack("method")
    ratio = np.log2(per["crossdb"] / per["missforest"]).unstack("fraction")
    ratio = ratio.loc[ratio.mean(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    image = ax.imshow(ratio.to_numpy(), cmap="PiYG", vmin=-3, vmax=3, aspect="auto")
    for i in range(ratio.shape[0]):
        for j in range(ratio.shape[1]):
            v = ratio.iat[i, j]
            if np.isnan(v):
                ax.text(j, i, "–", ha="center", va="center", fontsize=7, color="#999999")
            else:
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=6.5,
                        color="white" if abs(v) > 2 else "#222222")
    ax.set_xticks(range(ratio.shape[1]), [f"{f:.0%}" for f in ratio.columns])
    ax.set_yticks(range(ratio.shape[0]), [n.rsplit("_", 1)[0].replace("_", " ").replace("vitamin b", "vitamin B").replace("vitamin c", "vitamin C") for n in ratio.index])
    ax.set_xlabel("Observed cells hidden")
    ax.set_title("MyFCD: log2(nRMSE transfer / nRMSE MissForest)")
    ax.spines[:].set_visible(False)
    bar = fig.colorbar(image, ax=ax, shrink=0.8)
    bar.set_label("< 0: transfer better    > 0: MissForest better")
    fig.tight_layout()
    fig.savefig(OUT / "transfer_by_nutrient.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[PLOT] wrote reports/figures/masking_sweep.png, transfer_vs_internal.png, transfer_by_nutrient.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
