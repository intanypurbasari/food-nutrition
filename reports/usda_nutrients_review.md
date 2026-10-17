# USDA-only Nutrients Review

Nilai magnesium, gula total, lemak jenuh, kolesterol, vitamin B6 dan B12 untuk TKPI dan MyFCD.

## Sumber nilai

| Nutrisi | Sumber | TKPI | MyFCD |
|---|---|---|---|
| cholesterol_mg | USDA_direct_high | 18 | 17 |
| cholesterol_mg | USDA_direct_medium | 118 | 31 |
| cholesterol_mg | USDA_model | 1010 | 186 |
| magnesium_mg | USDA_direct_high | 18 | 17 |
| magnesium_mg | USDA_direct_medium | 117 | 30 |
| magnesium_mg | USDA_model | 1011 | 187 |
| saturated_fat_g | USDA_direct_high | 14 | 17 |
| saturated_fat_g | USDA_direct_medium | 113 | 32 |
| saturated_fat_g | USDA_model | 1019 | 185 |
| sugars_total_g | USDA_direct_high | 7 | 15 |
| sugars_total_g | USDA_direct_medium | 92 | 29 |
| sugars_total_g | USDA_model | 1047 | 190 |
| vitamin_b12_mcg | USDA_direct_high | 18 | 17 |
| vitamin_b12_mcg | USDA_direct_medium | 116 | 30 |
| vitamin_b12_mcg | USDA_model | 1012 | 187 |
| vitamin_b6_mg | USDA_direct_high | 17 | 17 |
| vitamin_b6_mg | USDA_direct_medium | 113 | 30 |
| vitamin_b6_mg | USDA_model | 1016 | 187 |

## Akurasi model (5-fold CV pada USDA SR Legacy)

nRMSE = RMSE / sd nilai asli (1,0 setara menebak rerata). Akurasi ini berlaku untuk pangan USDA;
pada TKPI/MyFCD prediktornya berupa campuran nilai terukur dan hasil imputasi, sehingga galat sebenarnya bisa lebih besar.

| Nutrisi | n latih | R² | nRMSE | Spearman |
|---|---|---|---|---|
| magnesium_mg | 7421 | 0.817 | 0.428 | 0.916 |
| sugars_total_g | 6007 | 0.829 | 0.413 | 0.911 |
| saturated_fat_g | 7450 | 0.716 | 0.533 | 0.976 |
| cholesterol_mg | 7394 | 0.637 | 0.603 | 0.910 |
| vitamin_b6_mg | 7262 | 0.736 | 0.514 | 0.901 |
| vitamin_b12_mcg | 7113 | 0.682 | 0.564 | 0.891 |
