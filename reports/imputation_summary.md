# Imputation Summary

- Total rows: 1380
- Per-nutrient cell resolution, routed via data_processed/availability_matrix.csv's strategi_imputasi.
- resolved_count + unresolved_count always sums to total_rows for every nutrient (full accounting, no silent gaps).

| Nutrient | Strategy | Resolved (internal) | Resolved (cross-DB) | Resolved (USDA-borrow) | Unresolved |
|---|---|---|---|---|---|
| water_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| energy_kcal | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| protein_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| fat_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| carbohydrate_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| fiber_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| ash_g | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| calcium_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| phosphorus_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| iron_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| sodium_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| potassium_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| copper_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| zinc_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| retinol_mcg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| beta_carotene_mcg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| carotene_total_mcg | Cross-DB transfer / USDA | 1146 | 234 | 0 | 0 |
| vitamin_a_mcg | Pinjam USDA (kosong di kedua basis) | 0 | 0 | 0 | 1380 |
| vitamin_b1_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| vitamin_b2_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| niacin_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| vitamin_c_mg | Imputasi internal per basis | 1380 | 0 | 0 | 0 |
| edible_portion_percent | Tidak dirutekan Stage 2 (di luar cakupan availability_matrix) | 0 | 0 | 0 | 1380 |

Nutrients with no strategy in availability_matrix.csv (e.g. edible_portion_percent) are labeled as not routed by Stage 2 and passed through from the enriched source unchanged.
vitamin_a_mcg has strategy "Pinjam USDA (kosong di kedua basis)" but is not among the 6 columns Stage 1 actually borrowed from USDA, so it remains fully unresolved (NaN) rather than fabricated.