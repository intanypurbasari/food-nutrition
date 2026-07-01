from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "nutrition_repository_sample.csv"

MACRO_FIELDS = ["energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "fiber_g", "water_g", "ash_g"]
MICRO_FIELDS = [
    "calcium_mg",
    "phosphorus_mg",
    "iron_mg",
    "sodium_mg",
    "potassium_mg",
    "copper_mg",
    "zinc_mg",
    "retinol_mcg",
    "beta_carotene_mcg",
    "carotene_total_mcg",
    "vitamin_a_mcg",
    "vitamin_b1_mg",
    "vitamin_b2_mg",
    "niacin_mg",
    "vitamin_c_mg",
    "edible_portion_percent",
]


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


st.set_page_config(page_title="Nutrition Repository", layout="wide")
st.title("Nutrition Repository")

if not DATA_PATH.exists():
    st.error("File repository belum tersedia. Jalankan `python scripts/build_repository_sample.py` lalu `python scripts/export_repository_json.py` terlebih dahulu.")
    st.stop()

try:
    data = load_data()
except Exception as exc:
    st.error(f"Data repository gagal dibaca: {exc}")
    st.stop()

if data.empty:
    st.warning("Repository masih kosong. Jalankan scraping atau isi data raw resmi terlebih dahulu, lalu jalankan pipeline cleaning dan merge.")
    st.stop()

with st.sidebar:
    st.metric("Total makanan", len(data))
    source_counts = data["source"].value_counts() if "source" in data else pd.Series(dtype=int)
    for source, count in source_counts.items():
        st.metric(str(source), int(count))
    if "completeness_score" in data:
        st.metric("Rata-rata completeness", f"{data['completeness_score'].mean():.2f}")

search = st.text_input("Cari nama makanan")
sources = sorted(data["source"].dropna().unique().tolist()) if "source" in data else []
selected_sources = st.multiselect("Sumber", options=sources, default=sources)

filtered = data.copy()
if search:
    mask = filtered["food_name_original"].fillna("").str.contains(search, case=False, na=False)
    if "food_name_normalized" in filtered:
        mask = mask | filtered["food_name_normalized"].fillna("").str.contains(search.lower(), case=False, na=False)
    filtered = filtered[mask]
if selected_sources and "source" in filtered:
    filtered = filtered[filtered["source"].isin(selected_sources)]

display_columns = [
    column
    for column in ["food_id", "food_name_original", "source", "energy_kcal", "protein_g", "fat_g", "carbohydrate_g", "completeness_score"]
    if column in filtered.columns
]
st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

if filtered.empty:
    st.info("Tidak ada hasil untuk filter saat ini.")
    st.stop()

food_options = filtered["food_id"].astype(str) + " - " + filtered["food_name_original"].astype(str)
selected_label = st.selectbox("Detail makanan", food_options.tolist())
selected_id = selected_label.split(" - ", 1)[0]
record = filtered[filtered["food_id"].astype(str) == selected_id].iloc[0]

st.subheader(record.get("food_name_original", "Detail"))
st.caption(f"Sumber: {record.get('source', '-')} | Basis: {record.get('unit_basis', 'per 100g')}")

left, right = st.columns(2)
with left:
    st.markdown("#### Makro")
    st.table(pd.DataFrame({"nutrient": MACRO_FIELDS, "value": [record.get(field) for field in MACRO_FIELDS]}))
with right:
    st.markdown("#### Mikro")
    st.table(pd.DataFrame({"nutrient": MICRO_FIELDS, "value": [record.get(field) for field in MICRO_FIELDS]}))

missing = [field for field in MACRO_FIELDS + MICRO_FIELDS if pd.isna(record.get(field))]
if missing:
    st.warning("Nutrien kosong: " + ", ".join(missing))
else:
    st.success("Seluruh field nutrisi utama terisi.")
