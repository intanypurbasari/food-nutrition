#!/usr/bin/env python3
"""Isi 6 nutrisi yang hanya ada di USDA pada nutrition_repository_imputed.csv.

magnesium_mg, sugars_total_g, saturated_fat_g, cholesterol_mg, vitamin_b6_mg
dan vitamin_b12_mcg tidak diukur oleh TKPI maupun MyFCD. Skrip ini dijalankan
setelah run_integration.py dan borrow_vitamin_a.py.

Urutan sumber nilai (yang pertama tersedia dipakai)
---------------------------------------------------
1. USDA_direct_high     nilai pangan USDA tertaut, skor kemiripan >= 0,65.
2. USDA_direct_medium   sama, skor >= 0,40 (tinjau manual).
                        Nilai pinjaman disetarakan kadar airnya sesuai Pedoman
                        TKPI (Kemenkes RI 2017, bagian 2.3): bila selisih kadar
                        air relatif > 10%, nilai dihitung atas dasar berat
                        kering (src/imputation/borrowing.py).
3. USDA_model           prediksi RandomForest yang dilatih pada seluruh pangan
                        USDA SR Legacy yang memiliki nutrisi itu, dengan 20
                        nutrisi bersama (proksimat, mineral, vitamin) sebagai
                        prediktor. Prediktor pangan lokal diambil dari hasil
                        imputasi Tahap 3, sehingga selalu lengkap.

Model tidak memakai rerata/median kategori: pada vitamin A, median kategori
jauh kurang akurat dibanding model berbasis komposisi pangan itu sendiri.
Akurasi model diukur dengan 5-fold cross-validation pada data USDA dan
dilaporkan di reports/usda_nutrients_review.md.

Keluaran
--------
- nutrition_repository_imputed.csv: keenam kolom diisi.
- usda_nutrients_provenance.csv: asal nilai per pangan x nutrisi, termasuk
  faktor penyetaraan kadar air.
- borrowed_values_documentation.csv: satu baris per pangan yang meminjam nilai
  USDA: nama kedua pangan, kadar air/lemak/protein keduanya, selisih kadar air,
  faktor dan sumber rujukan (dokumentasi Bab III Pedoman TKPI).
- reports/usda_nutrients_review.md: jumlah per sumber dan akurasi model.

Cara pakai
----------
    python scripts/fill_usda_nutrients.py            # tulis keluaran
    python scripts/fill_usda_nutrients.py --dry-run  # pratinjau saja
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_predict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import RANDOM_SEED
from src.imputation.borrowing import MOISTURE_THRESHOLD_PCT, moisture_adjustment
from src.schema.nutrition_schema import USDA_NUTRIENT_FIELDS

ROOT = Path(__file__).resolve().parents[1]
USDA_DIR = ROOT / "usda-csv"
PROCESSED = ROOT / "data_processed"
REPOSITORY_PATH = PROCESSED / "nutrition_repository_imputed.csv"
PROVENANCE_PATH = PROCESSED / "usda_nutrients_provenance.csv"
DOCUMENTATION_PATH = PROCESSED / "borrowed_values_documentation.csv"
REFERENCE = "USDA FoodData Central, SR Legacy (2019)"
# Faktor berat kering di luar [1/EXTREME_FACTOR, EXTREME_FACTOR] ditandai untuk tinjau manual.
EXTREME_FACTOR = 2.0
REVIEW_PATH = ROOT / "reports" / "usda_nutrients_review.md"

# USDA nutrient_id -> kolom skema. Satuan USDA sudah sama dengan skema
# (G, MG, UG = mcg, KCAL).
FEATURE_IDS = {
    1051: "water_g",
    1008: "energy_kcal",
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbohydrate_g",
    1079: "fiber_g",
    1007: "ash_g",
    1087: "calcium_mg",
    1091: "phosphorus_mg",
    1089: "iron_mg",
    1093: "sodium_mg",
    1092: "potassium_mg",
    1098: "copper_mg",
    1095: "zinc_mg",
    1105: "retinol_mcg",
    1107: "beta_carotene_mcg",
    1165: "vitamin_b1_mg",
    1166: "vitamin_b2_mg",
    1167: "niacin_mg",
    1162: "vitamin_c_mg",
}
TARGET_IDS = {
    1090: "magnesium_mg",
    2000: "sugars_total_g",
    1258: "saturated_fat_g",
    1253: "cholesterol_mg",
    1175: "vitamin_b6_mg",
    1178: "vitamin_b12_mcg",
}
assert sorted(TARGET_IDS.values()) == sorted(USDA_NUTRIENT_FIELDS)
FEATURES = list(FEATURE_IDS.values())

SOURCES = {
    "TKPI": PROCESSED / "tkpi_usda_links.csv",
    "MyFCD": PROCESSED / "myfcd_usda_links.csv",
}


def load_usda() -> pd.DataFrame:
    """One row per USDA fdc_id, columns = schema names of features and targets."""
    ids = {**FEATURE_IDS, **TARGET_IDS}
    food_nutrient = pd.read_csv(USDA_DIR / "food_nutrient.csv", usecols=["fdc_id", "nutrient_id", "amount"], low_memory=False)
    food_nutrient = food_nutrient[food_nutrient["nutrient_id"].isin(ids)]
    wide = food_nutrient.pivot_table(index="fdc_id", columns="nutrient_id", values="amount", aggfunc="first")
    return wide.rename(columns=ids)


def fit_models(usda: pd.DataFrame, seed: int) -> tuple[dict[str, RandomForestRegressor], pd.DataFrame]:
    """One RandomForest per target; also 5-fold CV accuracy on USDA itself."""
    models, metrics = {}, []
    for target in USDA_NUTRIENT_FIELDS:
        train = usda[usda[target].notna()]
        x, y = train.reindex(columns=FEATURES), train[target]
        model = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=seed, n_jobs=-1)
        predicted = cross_val_predict(model, x, y, cv=KFold(5, shuffle=True, random_state=seed))
        rmse = float(np.sqrt(np.mean((predicted - y) ** 2)))
        metrics.append(
            {
                "nutrient": target,
                "n_train": len(train),
                "cv_r2": 1 - float(np.sum((predicted - y) ** 2) / np.sum((y - y.mean()) ** 2)),
                "cv_nrmse": rmse / float(y.std(ddof=0)),
                "cv_spearman": float(pd.Series(predicted).corr(y.reset_index(drop=True), method="spearman")),
            }
        )
        models[target] = model.fit(x, y)
    return models, pd.DataFrame(metrics)


def best_links(path: Path) -> pd.DataFrame:
    links = pd.read_csv(path)
    links = links[links["confidence"].isin(["HIGH", "MEDIUM"])]
    return links.sort_values("similarity_score", ascending=False).drop_duplicates("source_food_id").set_index("source_food_id")


def resolve(repository: pd.DataFrame, usda: pd.DataFrame, models: dict[str, RandomForestRegressor]) -> pd.DataFrame:
    features = repository.reindex(columns=FEATURES)
    predictions = {target: model.predict(features) for target, model in models.items()}
    links = pd.concat([best_links(path) for path in SOURCES.values()])

    records = []
    for i, row in enumerate(repository.itertuples(index=False)):
        link = links.loc[row.food_id] if row.food_id in links.index else None
        linked = link is not None and link["usda_fdc_id"] in usda.index
        factor, diff, rule = (
            moisture_adjustment(float(row.water_g), float(usda.at[link["usda_fdc_id"], "water_g"])) if linked else (None, None, None)
        )
        for target in USDA_NUTRIENT_FIELDS:
            usda_value = usda.at[link["usda_fdc_id"], target] if linked else np.nan
            if pd.notna(usda_value):
                value, source = float(usda_value) * factor, f"USDA_direct_{link['confidence'].lower()}"
                moisture = {"usda_value": round(float(usda_value), 4), "water_diff_pct": diff, "moisture_factor": factor, "moisture_rule": rule}
            else:
                value, source = float(predictions[target][i]), "USDA_model"
                moisture = {"usda_value": None, "water_diff_pct": None, "moisture_factor": None, "moisture_rule": None}
            records.append(
                {
                    "food_id": row.food_id,
                    "source": row.source,
                    "nutrient": target,
                    "value": round(value, 4),
                    "value_source": source,
                    "usda_fdc_id": None if link is None else int(link["usda_fdc_id"]),
                    "usda_food_name": None if link is None else link["usda_food_name"],
                    "similarity_score": None if link is None else float(link["similarity_score"]),
                    **moisture,
                }
            )
    return pd.DataFrame(records)


DOCUMENTED = ["water_g", "fat_g", "protein_g"]


def documentation(repository: pd.DataFrame, usda: pd.DataFrame, usda_names: pd.Series) -> pd.DataFrame:
    """One row per food with a HIGH/MEDIUM USDA link (Pedoman TKPI, Bab III)."""
    links = pd.concat([best_links(path) for path in SOURCES.values()])
    rows = []
    for row in repository.itertuples(index=False):
        if row.food_id not in links.index or links.at[row.food_id, "usda_fdc_id"] not in usda.index:
            continue
        link = links.loc[row.food_id]
        fdc = link["usda_fdc_id"]
        factor, diff, rule = moisture_adjustment(float(row.water_g), float(usda.at[fdc, "water_g"]))
        record = {
            "source": row.source,
            "food_id": row.food_id,
            "food_name": row.food_name_original,
            "category": row.category_original,
            "usda_fdc_id": int(fdc),
            "usda_food_name": usda_names.get(fdc, link["usda_food_name"]),
            "usda_category": link.get("usda_category"),
            "similarity_score": float(link["similarity_score"]),
            "confidence": link["confidence"],
        }
        for column in DOCUMENTED:
            record[f"{column}_food"] = getattr(row, column)
            record[f"{column}_usda"] = usda.at[fdc, column]
        record.update({"water_diff_pct": None if pd.isna(diff) else round(diff, 2),
                       "moisture_factor": round(factor, 4), "moisture_rule": rule, "reference": REFERENCE})
        rows.append(record)
    return pd.DataFrame(rows)


def write_review(provenance: pd.DataFrame, metrics: pd.DataFrame) -> None:
    lines = [
        "# USDA-only Nutrients Review",
        "",
        "Nilai magnesium, gula total, lemak jenuh, kolesterol, vitamin B6 dan B12 untuk TKPI dan MyFCD.",
        "",
        "## Sumber nilai",
        "",
        "| Nutrisi | Sumber | TKPI | MyFCD |",
        "|---|---|---|---|",
    ]
    counts = provenance.groupby(["nutrient", "value_source", "source"]).size().unstack("source", fill_value=0)
    for (nutrient, source_label), row in counts.iterrows():
        lines.append(f"| {nutrient} | {source_label} | {row.get('TKPI', 0)} | {row.get('MyFCD', 0)} |")
    lines += [
        "",
        "## Akurasi model (5-fold CV pada USDA SR Legacy)",
        "",
        "nRMSE = RMSE / sd nilai asli (1,0 setara menebak rerata). Akurasi ini berlaku untuk pangan USDA;",
        "pada TKPI/MyFCD prediktornya berupa campuran nilai terukur dan hasil imputasi, sehingga galat sebenarnya bisa lebih besar.",
        "",
        "| Nutrisi | n latih | R² | nRMSE | Spearman |",
        "|---|---|---|---|---|",
    ]
    for row in metrics.itertuples(index=False):
        lines.append(f"| {row.nutrient} | {row.n_train} | {row.cv_r2:.3f} | {row.cv_nrmse:.3f} | {row.cv_spearman:.3f} |")
    direct = provenance[provenance["value_source"].str.startswith("USDA_direct")].drop_duplicates("food_id")
    lines += [
        "",
        "## Penyetaraan kadar air nilai pinjaman (Pedoman TKPI, Kemenkes RI 2017)",
        "",
        f"Bila |air pangan - air USDA| / air USDA > {MOISTURE_THRESHOLD_PCT:g}%, nilai USDA dikali "
        "(100 - air pangan) / (100 - air USDA) (dasar berat kering); bila tidak, dipinjam langsung.",
        "",
        "| Sumber | Pangan tertaut | Langsung | Berat kering | Tanpa data air | Median faktor (berat kering) | Rentang faktor |",
        "|---|---|---|---|---|---|---|",
    ]
    for source, part in direct.groupby("source"):
        dry = part[part["moisture_rule"] == "dry_matter"]["moisture_factor"]
        counts = part["moisture_rule"].value_counts()
        span = f"{dry.min():.2f}–{dry.max():.2f}" if len(dry) else ""
        median = f"{dry.median():.2f}" if len(dry) else ""
        lines.append(f"| {source} | {len(part)} | {counts.get('direct', 0)} | {counts.get('dry_matter', 0)} | "
                     f"{counts.get('no_water_data', 0)} | {median} | {span} |")
    extreme = direct[(direct["moisture_factor"] < 1 / EXTREME_FACTOR) | (direct["moisture_factor"] > EXTREME_FACTOR)]
    lines += [
        "",
        f"### Faktor ekstrem (< {1 / EXTREME_FACTOR:g} atau > {EXTREME_FACTOR:g}): tinjau tautannya",
        "",
        "Faktor sebesar ini biasanya berarti bentuk pangan berbeda (segar vs kering, mentah vs matang) atau tautan yang keliru. "
        "Penyetaraan berat kering mengoreksi perbedaan bentuk, tetapi tidak memperbaiki tautan yang salah pangan.",
        "",
    ]
    lines += [f"- {r.food_id} -> {r.usda_food_name} (USDA {int(r.usda_fdc_id)}): faktor {r.moisture_factor:.2f}, selisih air {r.water_diff_pct:.0f}%"
              for r in extreme.sort_values("moisture_factor").itertuples(index=False)] or ["- Tidak ada."]
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="tampilkan ringkasan tanpa menulis berkas")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    usda = load_usda()
    models, metrics = fit_models(usda, args.seed)
    print(metrics.round(3).to_string(index=False))

    repository = pd.read_csv(REPOSITORY_PATH)
    provenance = resolve(repository, usda, models)
    print(provenance.groupby(["source", "value_source"]).size().to_string())

    values = provenance.pivot(index="food_id", columns="nutrient", values="value")
    for target in USDA_NUTRIENT_FIELDS:
        repository[target] = repository["food_id"].map(values[target])
    if args.dry_run:
        return 0

    usda_names = pd.read_csv(USDA_DIR / "food.csv", usecols=["fdc_id", "description"]).set_index("fdc_id")["description"]
    repository.to_csv(REPOSITORY_PATH, index=False, encoding="utf-8")
    provenance.to_csv(PROVENANCE_PATH, index=False, encoding="utf-8")
    documentation(repository, usda, usda_names).to_csv(DOCUMENTATION_PATH, index=False, encoding="utf-8")
    write_review(provenance, metrics)
    print(f"[USDA_NUTRIENTS] wrote {REPOSITORY_PATH.name}, {PROVENANCE_PATH.name}, {DOCUMENTATION_PATH.name}, {REVIEW_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
