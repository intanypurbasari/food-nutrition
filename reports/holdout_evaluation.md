# Hold-out Evaluation

- 15% nilai terukur per nutrisi disembunyikan; mask independen per pengulangan (seed 42+r): TKPI 3x, MyFCD 10x.
- Nutrisi dengan kurang dari 10 nilai terukur tidak dievaluasi.
- Outlier tertandai dikeluarkan: tidak (semua baris dipakai).
- nRMSE = RMSE / sd(nilai asli yang disembunyikan). 1,0 setara menebak rerata; makin kecil makin baik.
- Angka di tabel adalah nRMSE gabungan seluruh sel hold-out dari semua pengulangan; **tebal** = metode terbaik untuk nutrisi itu.

## TKPI

| Nutrisi | n terukur | n sel hold-out | mean | median | group_median | knn | mice | missforest |
|---|---|---|---|---|---|---|---|---|
| ash_g | 1146 | 516 | 1.000 | 1.017 | **0.996** | 1.094 | 1.130 | 1.015 |
| beta_carotene_mcg | 679 | 306 | **1.000** | 1.038 | 1.007 | 1.092 | 1.067 | 1.159 |
| calcium_mg | 1106 | 498 | 1.005 | 1.026 | 1.002 | 0.987 | 3.107 | **0.724** |
| carbohydrate_g | 1146 | 516 | 1.002 | 1.081 | 0.709 | 0.863 | 0.437 | **0.327** |
| carotene_total_mcg | 607 | 273 | 1.000 | 1.055 | 1.007 | **0.992** | 1.106 | 1.015 |
| copper_mg | 793 | 357 | 1.005 | 1.024 | 1.000 | 1.047 | 1.029 | **0.960** |
| energy_kcal | 1146 | 516 | 1.001 | 1.055 | 0.849 | 0.583 | 0.404 | **0.235** |
| fat_g | 1145 | 516 | 1.001 | 1.080 | 0.750 | 0.780 | 0.372 | **0.265** |
| fiber_g | 925 | 417 | 1.002 | 1.035 | 0.970 | 1.063 | 1.039 | **0.866** |
| iron_mg | 1103 | 495 | 1.002 | 1.032 | 1.016 | 0.969 | 1.297 | **0.917** |
| niacin_mg | 807 | 363 | **1.001** | 1.015 | 1.009 | 1.017 | 1.046 | 1.002 |
| phosphorus_mg | 1106 | 498 | 1.007 | 1.036 | 0.901 | 0.951 | 0.894 | **0.681** |
| potassium_mg | 822 | 369 | 1.000 | 1.020 | 0.991 | 0.952 | 1.228 | **0.850** |
| protein_g | 1145 | 516 | 1.004 | 1.107 | 0.772 | 0.920 | **0.525** | 0.587 |
| retinol_mcg | 541 | 243 | 1.186 | 1.029 | **1.002** | 3.551 | 1.930 | 6.100 |
| sodium_mg | 863 | 387 | 1.001 | 1.044 | **0.993** | 1.203 | 1.031 | 1.203 |
| vitamin_b1_mg | 1058 | 477 | 1.414 | 1.072 | **0.997** | 10.706 | 14.886 | 23.162 |
| vitamin_b2_mg | 796 | 357 | **1.002** | 1.006 | 1.002 | 1.021 | 1.027 | 1.080 |
| vitamin_c_mg | 857 | 387 | 1.000 | 1.081 | 0.959 | 0.988 | 1.056 | **0.907** |
| water_g | 1144 | 516 | 1.001 | 1.055 | 0.862 | 0.630 | 0.291 | **0.231** |
| zinc_mg | 798 | 360 | 1.000 | 1.065 | **0.960** | 1.021 | 1.043 | 1.076 |

Jumlah nutrisi per metode terbaik: missforest 11, group_median 5, mean 3, knn 1, mice 1

## MyFCD

| Nutrisi | n terukur | n sel hold-out | mean | median | group_median | knn | mice | missforest | crossdb |
|---|---|---|---|---|---|---|---|---|---|
| ash_g | 139 | 210 | 1.013 | 1.044 | **0.885** | 1.007 | 2.568 | 1.070 | 2.185 |
| calcium_mg | 67 | 100 | 1.018 | 1.023 | 1.011 | 1.010 | 1.436 | 0.984 | **0.615** |
| carbohydrate_g | 109 | 160 | 1.026 | 1.074 | 0.743 | 0.725 | 0.854 | 0.634 | **0.493** |
| energy_kcal | 105 | 160 | 1.007 | 1.019 | 0.893 | 0.426 | 1.757 | 0.436 | **0.299** |
| fat_g | 151 | 230 | 1.015 | 1.077 | 0.618 | 1.063 | 0.875 | **0.579** | 0.963 |
| fiber_g | 139 | 210 | **1.004** | 1.032 | 1.025 | 1.084 | 3.025 | 1.043 | 1.041 |
| iron_mg | 48 | 70 | 1.026 | 1.009 | 1.007 | 1.008 | **0.667** | 1.113 | 0.915 |
| niacin_mg | 10 | 20 | 1.098 | 1.123 | 1.123 | 1.179 | 127.626 | 1.303 | **1.009** |
| phosphorus_mg | 107 | 160 | 1.013 | 1.005 | 1.003 | 1.020 | **0.963** | 1.007 | 0.977 |
| potassium_mg | 73 | 110 | 1.014 | 1.016 | 1.015 | 1.005 | **0.785** | 0.991 | 0.936 |
| protein_g | 150 | 220 | 1.013 | 1.055 | 0.908 | 1.020 | **0.763** | 0.981 | 1.332 |
| sodium_mg | 64 | 100 | 1.017 | 1.012 | 1.009 | 1.008 | **0.914** | 1.044 | 1.005 |
| vitamin_b1_mg | 10 | 20 | 1.124 | 1.085 | **1.036** | 1.192 | 371.852 | 1.298 | 2.024 |
| vitamin_b2_mg | 10 | 20 | 1.122 | 1.093 | 1.093 | 1.082 | 4.741 | **1.076** | 1.301 |
| vitamin_c_mg | 27 | 40 | 1.079 | 1.024 | **0.967** | 1.183 | 1.083 | 1.106 | 5.161 |
| water_g | 150 | 220 | 1.005 | 1.017 | 0.726 | 0.924 | 2.574 | **0.530** | 0.620 |
| zinc_mg | 49 | 70 | 1.023 | 1.015 | 1.015 | 1.014 | **1.005** | 1.043 | 1.011 |

Jumlah nutrisi per metode terbaik: mice 6, crossdb 4, group_median 3, missforest 3, mean 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 10 dari 17 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 1.070 | 2.185 | 1.114 |
| calcium_mg | 0.984 | 0.615 | -0.369 |
| carbohydrate_g | 0.634 | 0.493 | -0.141 |
| energy_kcal | 0.436 | 0.299 | -0.137 |
| fat_g | 0.579 | 0.963 | 0.384 |
| fiber_g | 1.043 | 1.041 | -0.003 |
| iron_mg | 1.113 | 0.915 | -0.197 |
| niacin_mg | 1.303 | 1.009 | -0.294 |
| phosphorus_mg | 1.007 | 0.977 | -0.030 |
| potassium_mg | 0.991 | 0.936 | -0.056 |
| protein_g | 0.981 | 1.332 | 0.352 |
| sodium_mg | 1.044 | 1.005 | -0.039 |
| vitamin_b1_mg | 1.298 | 2.024 | 0.726 |
| vitamin_b2_mg | 1.076 | 1.301 | 0.225 |
| vitamin_c_mg | 1.106 | 5.161 | 4.055 |
| water_g | 0.530 | 0.620 | 0.089 |
| zinc_mg | 1.043 | 1.011 | -0.032 |
