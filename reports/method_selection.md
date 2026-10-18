# Pemilihan Metode Imputasi per Nutrisi

Sumber: `reports/holdout_evaluation.csv` (nRMSE gabungan seluruh sel hold-out).

1. Metode dengan nRMSE terendah dipilih. Metode yang selisihnya <= 0.02 dianggap setara; di antara yang setara diutamakan missforest > crossdb > mice > knn > group_median > median > mean.
2. Nutrisi tanpa nilai terukur di MyFCD memakai cross-DB transfer dari TKPI.
3. Nutrisi lain tanpa skor hold-out memakai MissForest (bawaan Tahap 3).

## TKPI

| Nutrisi | Metode | nRMSE | nRMSE MissForest | n terukur | Alasan |
|---|---|---|---|---|---|
| water_g | **missforest** | 0.231 | 0.231 | 1144 | nRMSE terendah |
| energy_kcal | **missforest** | 0.235 | 0.235 | 1146 | nRMSE terendah |
| protein_g | **mice** | 0.525 | 0.587 | 1145 | nRMSE terendah |
| fat_g | **missforest** | 0.265 | 0.265 | 1145 | nRMSE terendah |
| carbohydrate_g | **missforest** | 0.327 | 0.327 | 1146 | nRMSE terendah |
| fiber_g | **missforest** | 0.866 | 0.866 | 925 | nRMSE terendah |
| ash_g | **missforest** | 1.015 | 1.015 | 1146 | selisih <= 0.02 dari group_median; diutamakan metode multivariat |
| calcium_mg | **missforest** | 0.724 | 0.724 | 1106 | nRMSE terendah |
| phosphorus_mg | **missforest** | 0.681 | 0.681 | 1106 | nRMSE terendah |
| iron_mg | **missforest** | 0.917 | 0.917 | 1103 | nRMSE terendah |
| sodium_mg | **group_median** | 0.993 | 1.204 | 863 | nRMSE terendah |
| potassium_mg | **missforest** | 0.851 | 0.851 | 822 | nRMSE terendah |
| copper_mg | **missforest** | 0.960 | 0.960 | 793 | nRMSE terendah |
| zinc_mg | **group_median** | 0.960 | 1.076 | 798 | nRMSE terendah |
| retinol_mcg | **group_median** | 1.002 | 6.101 | 541 | nRMSE terendah |
| beta_carotene_mcg | **group_median** | 1.007 | 1.159 | 679 | selisih <= 0.02 dari mean; diutamakan metode multivariat |
| carotene_total_mcg | **knn** | 0.992 | 1.015 | 607 | nRMSE terendah |
| vitamin_b1_mg | **group_median** | 0.997 | 23.162 | 1058 | nRMSE terendah |
| vitamin_b2_mg | **knn** | 1.021 | 1.080 | 796 | selisih <= 0.02 dari mean; diutamakan metode multivariat |
| niacin_mg | **missforest** | 1.002 | 1.002 | 807 | selisih <= 0.02 dari mean; diutamakan metode multivariat |
| vitamin_c_mg | **missforest** | 0.906 | 0.906 | 857 | nRMSE terendah |

Jumlah nutrisi per metode: missforest 13, group_median 5, knn 2, mice 1

## MyFCD

| Nutrisi | Metode | nRMSE | nRMSE MissForest | n terukur | Alasan |
|---|---|---|---|---|---|
| water_g | **missforest** | 0.530 | 0.530 | 150 | nRMSE terendah |
| energy_kcal | **crossdb** | 0.299 | 0.436 | 105 | nRMSE terendah |
| protein_g | **mice** | 0.763 | 0.981 | 150 | nRMSE terendah |
| fat_g | **missforest** | 0.579 | 0.579 | 151 | nRMSE terendah |
| carbohydrate_g | **crossdb** | 0.493 | 0.634 | 109 | nRMSE terendah |
| fiber_g | **mean** | 1.004 | 1.043 | 139 | nRMSE terendah |
| ash_g | **group_median** | 0.885 | 1.070 | 139 | nRMSE terendah |
| calcium_mg | **crossdb** | 0.615 | 0.984 | 67 | nRMSE terendah |
| phosphorus_mg | **crossdb** | 0.977 | 1.007 | 107 | selisih <= 0.02 dari mice; diutamakan metode multivariat |
| iron_mg | **mice** | 0.667 | 1.113 | 48 | nRMSE terendah |
| sodium_mg | **mice** | 0.914 | 1.044 | 64 | nRMSE terendah |
| potassium_mg | **mice** | 0.785 | 0.992 | 73 | nRMSE terendah |
| copper_mg | **crossdb** |  |  | 0 | tidak ada nilai terukur di MyFCD; hanya transfer dari TKPI yang mungkin |
| zinc_mg | **crossdb** | 1.011 | 1.043 | 49 | selisih <= 0.02 dari mice; diutamakan metode multivariat |
| retinol_mcg | **crossdb** |  |  | 0 | tidak ada nilai terukur di MyFCD; hanya transfer dari TKPI yang mungkin |
| beta_carotene_mcg | **crossdb** |  |  | 0 | tidak ada nilai terukur di MyFCD; hanya transfer dari TKPI yang mungkin |
| carotene_total_mcg | **crossdb** |  |  | 0 | tidak ada nilai terukur di MyFCD; hanya transfer dari TKPI yang mungkin |
| vitamin_b1_mg | **group_median** | 1.036 | 1.298 | 10 | nRMSE terendah |
| vitamin_b2_mg | **missforest** | 1.076 | 1.076 | 10 | nRMSE terendah |
| niacin_mg | **crossdb** | 1.009 | 1.303 | 10 | nRMSE terendah |
| vitamin_c_mg | **group_median** | 0.967 | 1.106 | 27 | nRMSE terendah |

Jumlah nutrisi per metode: crossdb 10, mice 4, missforest 3, group_median 3, mean 1
