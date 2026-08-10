# Data Dictionary Unified Nutrition Schema

Seluruh nilai nutrisi menggunakan basis `per 100g`, kecuali ada catatan lain pada kolom `notes`.

| Kolom | Tipe | Satuan | Nullable | Contoh | Mapping TKPI | Mapping MyFCD |
|---|---|---|---|---|---|---|
| food_id | string | - | tidak | tkpi_0001 | generated | generated |
| food_name_original | string | - | tidak | Nasi putih | Nama Bahan Makanan, nama_bahan_makanan | Food Name, food_name |
| food_name_normalized | string | - | tidak | nasi putih | derived | derived |
| source | string | - | tidak | TKPI | constant | constant |
| source_url | string | - | ya | https://... | URL hasil scrape | URL hasil scrape |
| category_original | string | - | ya | Serealia | Kelompok Makanan, kelompok | Food Group, group |
| category_normalized | string | - | ya | serealia | derived | derived |
| water_g | float | g | ya | 69.0 | Air (g), air | Moisture (g), moisture |
| energy_kcal | float | kcal | ya | 130.0 | Energi (kal), energi | Energy (kcal), energy |
| protein_g | float | g | ya | 2.7 | Protein (g), protein | Protein (g), protein |
| fat_g | float | g | ya | 0.3 | Lemak (g), lemak | Fat (g), fat |
| carbohydrate_g | float | g | ya | 28.2 | Karbohidrat (g), karbohidrat | Carbohydrate (g), carbohydrate |
| fiber_g | float | g | ya | 0.4 | Serat (g), serat | Dietary Fibre (g), fiber |
| ash_g | float | g | ya | 0.3 | Abu (g), abu | Ash (g), ash |
| calcium_mg | float | mg | ya | 5.0 | Kalsium (mg), kalsium | Calcium (mg), calcium |
| phosphorus_mg | float | mg | ya | 40.0 | Fosfor (mg), fosfor | Phosphorus (mg), phosphorus |
| iron_mg | float | mg | ya | 0.5 | Besi (mg), besi | Iron (mg), iron |
| sodium_mg | float | mg | ya | 5.0 | Natrium (mg), natrium | Sodium (mg), sodium |
| potassium_mg | float | mg | ya | 50.0 | Kalium (mg), kalium | Potassium (mg), potassium |
| copper_mg | float | mg | ya | 0.06 | Tembaga (mg), tembaga | Copper (mg), copper |
| zinc_mg | float | mg | ya | 0.5 | Seng (mg), seng | Zinc (mg), zinc |
| retinol_mcg | float | mcg | ya | 0.0 | Retinol (mcg), retinol | Retinol (mcg), retinol |
| beta_carotene_mcg | float | mcg | ya | 0.0 | Beta-Karoten (mcg), b-karoten | Beta-Carotene (mcg), beta_carotene |
| carotene_total_mcg | float | mcg | ya | 0.0 | Karoten Total (mcg), karoten_total | Total Carotene (mcg), carotene_total |
| vitamin_a_mcg | float | mcg | ya | 0.0 | Vitamin A (mcg), vitamin_a | Vitamin A (mcg), vitamin_a |
| vitamin_b1_mg | float | mg | ya | 0.02 | Vitamin B1 (mg), tiamin | Thiamine (mg), vitamin_b1 |
| vitamin_b2_mg | float | mg | ya | 0.01 | Vitamin B2 (mg), riboflavin | Riboflavin (mg), vitamin_b2 |
| niacin_mg | float | mg | ya | 0.4 | Niasin (mg), niasin | Niacin (mg), niacin |
| vitamin_c_mg | float | mg | ya | 0.0 | Vitamin C (mg), vitamin_c | Vitamin C (mg), vitamin_c |
| unit_basis | string | - | tidak | per 100g | constant | constant |
| scraped_at | datetime | ISO8601 | tidak | 2026-07-01T10:00:00 | generated | generated |
| cleaned_at | datetime | ISO8601 | ya | 2026-07-01T11:00:00 | generated | generated |
| missing_nutrient_count | int | - | tidak | 3 | derived | derived |
| completeness_score | float | 0-1 | tidak | 0.85 | derived | derived |
| notes | string | - | ya | BDD diasumsikan 100% | manual/derived | manual/derived |
