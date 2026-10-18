# Imputation Summary

- Total rows: 1380
- Per-nutrient cell resolution, routed via data_processed/availability_matrix.csv's strategi_imputasi.
- resolved_count + unresolved_count always sums to total_rows for every nutrient (full accounting, no silent gaps).

| Nutrient | Strategy | Method TKPI | Method MyFCD | Resolved (internal) | Resolved (cross-DB) | Resolved (USDA-borrow) | Unresolved |
|---|---|---|---|---|---|---|---|
| water_g | Dipilih per nutrisi (method_selection.csv) | missforest | missforest | 1380 | 0 | 0 | 0 |
| energy_kcal | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| protein_g | Dipilih per nutrisi (method_selection.csv) | mice | mice | 1380 | 0 | 0 | 0 |
| fat_g | Dipilih per nutrisi (method_selection.csv) | missforest | missforest | 1380 | 0 | 0 | 0 |
| carbohydrate_g | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| fiber_g | Dipilih per nutrisi (method_selection.csv) | missforest | mean | 1380 | 0 | 0 | 0 |
| ash_g | Dipilih per nutrisi (method_selection.csv) | missforest | group_median | 1380 | 0 | 0 | 0 |
| calcium_mg | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| phosphorus_mg | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| iron_mg | Dipilih per nutrisi (method_selection.csv) | missforest | mice | 1380 | 0 | 0 | 0 |
| sodium_mg | Dipilih per nutrisi (method_selection.csv) | group_median | mice | 1380 | 0 | 0 | 0 |
| potassium_mg | Dipilih per nutrisi (method_selection.csv) | missforest | mice | 1380 | 0 | 0 | 0 |
| copper_mg | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| zinc_mg | Dipilih per nutrisi (method_selection.csv) | group_median | crossdb | 1146 | 234 | 0 | 0 |
| retinol_mcg | Dipilih per nutrisi (method_selection.csv) | group_median | crossdb | 1146 | 234 | 0 | 0 |
| beta_carotene_mcg | Dipilih per nutrisi (method_selection.csv) | group_median | crossdb | 1146 | 234 | 0 | 0 |
| carotene_total_mcg | Dipilih per nutrisi (method_selection.csv) | missforest_ind | crossdb | 1146 | 234 | 0 | 0 |
| vitamin_a_mcg | Pinjam USDA (kosong di kedua basis) |  |  | 0 | 0 | 0 | 1380 |
| vitamin_b1_mg | Dipilih per nutrisi (method_selection.csv) | group_median | group_median | 1380 | 0 | 0 | 0 |
| vitamin_b2_mg | Dipilih per nutrisi (method_selection.csv) | knn | missforest | 1380 | 0 | 0 | 0 |
| niacin_mg | Dipilih per nutrisi (method_selection.csv) | missforest | crossdb | 1146 | 234 | 0 | 0 |
| vitamin_c_mg | Dipilih per nutrisi (method_selection.csv) | missforest_ind | group_median | 1380 | 0 | 0 | 0 |

Nutrients with no strategy in availability_matrix.csv are labeled as not routed by Stage 2 and passed through from the enriched source unchanged.
vitamin_a_mcg has strategy "Pinjam USDA (kosong di kedua basis)" but is not among the 6 columns Stage 1 actually borrowed from USDA, so it is unresolved here; scripts/borrow_vitamin_a.py fills it afterwards (see reports/vitamin_a_review.md).