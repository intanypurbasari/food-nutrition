"""Flow diagram of the imputation method chosen for every nutrient, with all rows and with flagged outliers excluded.

For each source (TKPI, MyFCD) the diagram follows the 22 nutrients of the schema:
total -> kind of treatment (imputed, calculated, derived) -> method chosen on the hold-out evaluation with all rows
-> method that the same rule chooses when flagged outlier foods are excluded. One ribbon per nutrient; ribbons that
change method are drawn darker with an outline.

The "outliers excluded" column re-applies the selection rule of scripts/select_imputation_methods.py to
reports/holdout_evaluation_no_outliers.csv. It is a sensitivity analysis: the released dataset uses the all-rows
selection (data_processed/method_selection.csv). Nutrients that cannot be re-evaluated without outliers (never measured,
or fewer than 10 measured values left) keep their all-rows method and are shown in a separate hatched group.

Outputs (reports/figures/): selection_flow_<source>_<lang>.png, lang = id | en

Usage:
    python scripts/plot_selection_flow.py            # both languages
    python scripts/plot_selection_flow.py --lang en
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS  # noqa: E402
from select_imputation_methods import TOLERANCE, choose  # noqa: E402

OUT = ROOT / "reports" / "figures"
ORDER = ["missforest", "missforest_ind", "crossdb", "mice", "softimpute", "knn", "group_median", "median", "mean",
         "atwater", "derived"]
COLOR = {"missforest": "#31a354", "missforest_ind": "#a1d99b", "crossdb": "#d6278a", "mice": "#756bb1",
         "softimpute": "#3182bd", "knn": "#e6550d", "group_median": "#8c6d31", "median": "#bdbdbd", "mean": "#9e9e9e",
         "atwater": "#3a3a3a", "derived": "#e0a030"}
DARK_TEXT = {"missforest_ind", "median", "mean", "derived"}
TEXT = {
    "id": {
        "names": {"missforest": "MissForest", "missforest_ind": "MissForest + indikator", "crossdb": "Transfer lintas-DB",
                  "mice": "MICE", "softimpute": "SoftImpute", "knn": "KNN", "group_median": "Median kelompok",
                  "median": "Median", "mean": "Rerata", "atwater": "Atwater (energi)", "derived": "Turunan RAE (vit. A)"},
        "heads": ["Total nutrisi", "Perlakuan", "Metode terpilih\n(semua baris)", "Metode terpilih\n(tanpa outlier)"],
        "total": "{n} nutrisi", "imputed": "Diimputasi · {n}", "calc": "Dihitung · {n}", "deriv": "Diturunkan · {n}",
        "fixed": "Tidak dapat dievaluasi ulang · {n}",
        "title": "{s}: dari {n} nutrisi sampai metode imputasi",
        "sub": "{c} dari {m} nutrisi yang dapat dievaluasi ulang berganti metode saat outlier dikeluarkan",
        "note": "Pita gelap bergaris = nutrisi yang berganti metode. Pemilihan tanpa outlier adalah analisis sensitivitas; "
                "dataset akhir memakai pemilihan dari semua baris.\n{fixed_note}",
        "fixed_note_my": "Tidak dapat dievaluasi ulang: tidak pernah terukur di MyFCD (tembaga, retinol, β-karoten, karoten total) "
                         "atau tersisa < 10 nilai terukur (niasin, vitamin B1, B2); metode semula dipertahankan.",
        "fixed_note_tk": "",
    },
    "en": {
        "names": {"missforest": "MissForest", "missforest_ind": "MissForest + indicators", "crossdb": "Cross-DB transfer",
                  "mice": "MICE", "softimpute": "SoftImpute", "knn": "KNN", "group_median": "Group median",
                  "median": "Median", "mean": "Mean", "atwater": "Atwater (energy)", "derived": "Derived RAE (vit. A)"},
        "heads": ["All nutrients", "Treatment", "Method chosen\n(all rows)", "Method chosen\n(outliers excluded)"],
        "total": "{n} nutrients", "imputed": "Imputed · {n}", "calc": "Calculated · {n}", "deriv": "Derived · {n}",
        "fixed": "Cannot be re-evaluated · {n}",
        "title": "{s}: from {n} nutrients to the imputation method",
        "sub": "{c} of the {m} nutrients that can be re-evaluated change method when outliers are excluded",
        "note": "Dark outlined ribbons = nutrients that change method. Selection without outliers is a sensitivity analysis; "
                "the released dataset uses the all-rows selection.\n{fixed_note}",
        "fixed_note_my": "Cannot be re-evaluated: never measured in MyFCD (copper, retinol, β-carotene, total carotene) "
                         "or < 10 measured values left (niacin, vitamin B1, B2); the original method is kept.",
        "fixed_note_tk": "",
    },
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def methods_by_source() -> dict[str, tuple[dict, dict, set]]:
    """(all-rows method, outliers-excluded method, nutrients that cannot be re-evaluated) per source."""
    selection = pd.read_csv(ROOT / "data_processed" / "method_selection.csv")
    no_outliers = pd.read_csv(ROOT / "reports" / "holdout_evaluation_no_outliers.csv")
    result = {}
    for source in ["TKPI", "MyFCD"]:
        allrows = {n: "derived" for n in IMPUTATION_NUTRIENT_FIELDS if n == "vitamin_a_mcg"}
        allrows.update(selection[selection["source"] == source].set_index("nutrient")["method"].to_dict())
        reselected, fixed = {}, set()
        for nutrient, method in allrows.items():
            if method in ("atwater", "derived"):
                reselected[nutrient] = method
                continue
            block = no_outliers[(no_outliers["source"] == source) & (no_outliers["nutrient"] == nutrient)]
            block = block.dropna(subset=["nrmse"])
            block = block[block["method"] != "atwater"]
            if block.empty:
                reselected[nutrient] = method
                fixed.add(nutrient)
            else:
                reselected[nutrient] = choose(block, TOLERANCE)[0]
        result[source] = (allrows, reselected, fixed)
    return result


ID_NAMES = {"water": "air", "energy": "energi", "protein": "protein", "fat": "lemak", "carbohydrate": "karbohidrat",
            "fiber": "serat", "ash": "abu", "calcium": "kalsium", "phosphorus": "fosfor", "iron": "besi",
            "sodium": "natrium", "potassium": "kalium", "copper": "tembaga", "zinc": "seng", "retinol": "retinol",
            "beta carotene": "β-karoten", "carotene total": "karoten total", "niacin": "niasin"}


def pretty(nutrient: str, lang: str = "en") -> str:
    base = nutrient.rsplit("_", 1)[0].replace("_", " ")
    if lang == "id" and base in ID_NAMES:
        return ID_NAMES[base]
    return (base.replace("vitamin b", "vit. B").replace("vitamin c", "vit. C").replace("vitamin a", "vit. A")
            .replace("beta carotene", "β-carotene"))


def stack(groups: list[tuple[str, list[str]]], gap: float) -> dict:
    """Vertical layout: for each group its y range and for each nutrient its y range (top to bottom)."""
    y, layout = 0.0, {}
    for key, items in groups:
        if not items:
            continue
        layout[key] = {"top": y, "bottom": y + len(items), "rows": {n: (y + i, y + i + 1) for i, n in enumerate(items)}}
        y += len(items) + gap
    return layout


def ribbon(ax, x0, a0, b0, x1, a1, b1, color, alpha, edge=None, hatch=None):
    t = np.linspace(0, 1, 40)
    s = 3 * t**2 - 2 * t**3
    xs = x0 + (x1 - x0) * t
    top = a0 + (a1 - a0) * s
    bottom = b0 + (b1 - b0) * s
    verts = list(zip(xs, top)) + list(zip(xs[::-1], bottom[::-1]))
    patch = PathPatch(MplPath(verts + [verts[0]], [MplPath.MOVETO] + [MplPath.LINETO] * (len(verts) - 1) + [MplPath.CLOSEPOLY]),
                      facecolor=color, edgecolor=edge or "none", lw=0.7 if edge else 0, alpha=alpha, hatch=hatch)
    ax.add_patch(patch)


def draw(source: str, allrows: dict, reselected: dict, fixed: set, lang: str) -> Path:
    t = TEXT[lang]
    nutrients = [n for n in IMPUTATION_NUTRIENT_FIELDS if n in allrows]
    n_total = len(IMPUTATION_NUTRIENT_FIELDS)
    gap = 0.8
    by_method = lambda mapping: [(m, [n for n in nutrients if mapping[n] == m]) for m in ORDER]
    left = by_method(allrows)
    left = [(m, sorted(items, key=nutrients.index)) for m, items in left]
    pos2 = {n: i for i, (_, items) in enumerate(left) for n in items}
    flat2 = [n for _, items in left for n in items]
    right_groups = [(m, sorted([n for n in nutrients if reselected[n] == m and n not in fixed], key=flat2.index)) for m in ORDER]
    right_groups.append(("fixed", sorted([n for n in nutrients if n in fixed], key=flat2.index)))
    lay2, lay3 = stack(left, gap), stack(right_groups, gap)
    imputed = [n for n in flat2 if allrows[n] not in ("atwater", "derived")]
    kinds = [("imputed", imputed), ("calc", [n for n in nutrients if allrows[n] == "atwater"]),
             ("deriv", [n for n in nutrients if allrows[n] == "derived"])]
    lay1 = stack(kinds, gap)
    lay0 = {"all": {"top": 0.0, "bottom": float(n_total), "rows": {}}}
    height = max(lay2[max(lay2, key=lambda k: lay2[k]["bottom"])]["bottom"], lay3[max(lay3, key=lambda k: lay3[k]["bottom"])]["bottom"])

    x0, x1, x2, x3 = 0.0, 1.7, 5.9, 9.2
    w0, w1, w23 = 0.35, 1.3, 1.15
    fig, ax = plt.subplots(figsize=(12.0, 9.2))
    ax.set_xlim(-1.2, 12.6); ax.set_ylim(height + 3.6, -4.6); ax.axis("off")

    def bar(x, w, top, bottom, color, text=None, dark=False, hatch=None):
        ax.add_patch(Rectangle((x - w / 2, top), w, bottom - top, fc=color, ec="white", lw=0.8, hatch=hatch))
        if text:
            ax.text(x, (top + bottom) / 2, text, ha="center", va="center", fontsize=6.6, color="#222222" if dark else "white")

    # column 0 -> 1: total to kinds
    cursor = 0.0
    for key, items in kinds:
        if not items:
            continue
        g = lay1[key]
        ribbon(ax, x0 + w0 / 2, cursor, cursor + len(items), x1 - w1 / 2, g["top"], g["bottom"], "#9aa5b1", 0.45)
        cursor += len(items)
    bar(x0, w0, 0, n_total, "#44546a")
    ax.text(x0 - w0 / 2 - 0.1, n_total / 2, t["total"].format(n=n_total), ha="right", va="center", fontsize=8.5, weight="bold")
    for key, items in kinds:
        if items:
            g = lay1[key]
            bar(x1, w1, g["top"], g["bottom"], "#44546a" if key == "imputed" else COLOR["atwater" if key == "calc" else "derived"],
                t[key].format(n=len(items)), dark=(key == "deriv"))
    # column 1 -> 2: imputed split by method, calc/derived straight
    cursor = lay1["imputed"]["top"]
    for method, items in left:
        if not items or method in ("atwater", "derived"):
            continue
        g = lay2[method]
        ribbon(ax, x1 + w1 / 2, cursor, cursor + len(items), x2 - w23 / 2, g["top"], g["bottom"], COLOR[method], 0.5)
        cursor += len(items)
    for key, method in (("calc", "atwater"), ("deriv", "derived")):
        if kinds[[k for k, _ in kinds].index(key)][1]:
            g1, g2 = lay1[key], lay2[method]
            ribbon(ax, x1 + w1 / 2, g1["top"], g1["bottom"], x2 - w23 / 2, g2["top"], g2["bottom"], COLOR[method], 0.5)
    # column 2 -> 3: one ribbon per nutrient
    changed = 0
    evaluable = 0
    for n in nutrients:
        m2, m3 = allrows[n], reselected[n]
        a2, b2 = None, None
        a2, b2 = lay2[m2]["rows"][n]
        group3 = "fixed" if n in fixed else m3
        a3, b3 = lay3[group3]["rows"][n]
        moved = (m2 != m3) and n not in fixed
        if m2 not in ("atwater", "derived") and n not in fixed:
            evaluable += 1
            changed += int(moved)
        ribbon(ax, x2 + w23 / 2, a2, b2, x3 - w23 / 2, a3, b3, COLOR[m2], 0.85 if moved else 0.38,
               edge="#111111" if moved else None, hatch="////" if n in fixed else None)
    # bars with nutrient names
    for method, items in left:
        if items:
            g = lay2[method]
            for n in items:
                a, b = g["rows"][n]
                bar(x2, w23, a, b, COLOR[method], pretty(n, lang), dark=method in DARK_TEXT)
            ax.text(x2 - w23 / 2 - 0.08, (g["top"] + g["bottom"]) / 2, f"{t['names'][method]} · {len(items)}", ha="right", va="center",
                    fontsize=7.4, weight="bold", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2))
    for key, items in right_groups:
        if not items:
            continue
        g = lay3[key]
        for n in items:
            a, b = g["rows"][n]
            col = COLOR[reselected[n]] if key != "fixed" else "#d9d9d9"
            bar(x3, w23, a, b, col, pretty(n, lang), dark=(key in DARK_TEXT or key == "fixed"), hatch="////" if key == "fixed" else None)
        label = t["fixed"].format(n=len(items)) if key == "fixed" else f"{t['names'][key]} · {len(items)}"
        ax.text(x3 + w23 / 2 + 0.1, (g["top"] + g["bottom"]) / 2, label, ha="left", va="center", fontsize=7.4, weight="bold")
    for x, head in zip([x0, x1, x2, x3], t["heads"]):
        ax.text(x, -1.3, head, ha="center", va="center", fontsize=8.5, weight="bold", color="#222222")
    ax.text(-1.2, -4.3, t["title"].format(s=source, n=n_total), fontsize=11.5, weight="bold", va="center")
    ax.text(-1.2, -3.4, t["sub"].format(c=changed, m=evaluable), fontsize=8.5, color="#555555", va="center")
    note = t["note"].format(fixed_note=t["fixed_note_my"] if (fixed and source == "MyFCD") else "").strip()
    ax.text(-1.2, height + 3.4, note, fontsize=7, color="#555555", va="bottom")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"selection_flow_{source.lower()}_{lang}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[FLOW] {source}: {evaluable} evaluable imputed nutrients, {changed} change method -> {path.relative_to(ROOT)}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lang", choices=["id", "en", "both"], default="both")
    args = parser.parse_args()
    languages = ["id", "en"] if args.lang == "both" else [args.lang]
    for source, (allrows, reselected, fixed) in methods_by_source().items():
        for lang in languages:
            draw(source, allrows, reselected, fixed, lang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
