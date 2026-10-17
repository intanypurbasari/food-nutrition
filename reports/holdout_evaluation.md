# Hold-out Evaluation

- 15% nilai terukur per nutrisi disembunyikan; mask independen per pengulangan (seed 42+r): TKPI 3x, MyFCD 10x.
- Nutrisi dengan kurang dari 10 nilai terukur tidak dievaluasi.
- Outlier tertandai dikeluarkan: tidak (semua baris dipakai).
- nRMSE = RMSE / sd(nilai asli yang disembunyikan). 1,0 setara menebak rerata; makin kecil makin baik.
- Angka di tabel adalah nRMSE gabungan seluruh sel hold-out dari semua pengulangan; **tebal** = metode terbaik untuk nutrisi itu.

## TKPI

| Nutrisi | n terukur | n sel hold-out | mean | median | knn | mice | missforest |
|---|---|---|---|---|---|---|---|
| ash_g | 1146 | 516 | **1.000** | 1.017 | 1.073 | 1.357 | 1.288 |
| beta_carotene_mcg | 679 | 306 | 1.001 | 1.031 | 1.024 | **0.994** | 1.151 |
| calcium_mg | 1106 | 498 | 1.005 | 1.026 | 1.005 | 3.248 | **0.797** |
| carbohydrate_g | 1146 | 516 | 1.002 | 1.081 | 0.857 | 0.457 | **0.330** |
| carotene_total_mcg | 607 | 273 | 1.002 | 1.056 | **1.001** | 1.220 | 1.047 |
| copper_mg | 795 | 357 | **1.002** | 1.002 | 1.022 | 1.090 | 1.017 |
| energy_kcal | 1146 | 516 | 1.001 | 1.055 | 0.572 | 0.322 | **0.227** |
| fat_g | 1145 | 516 | 1.001 | 1.080 | 0.737 | 0.401 | **0.268** |
| fiber_g | 925 | 417 | 1.002 | 1.035 | 1.029 | 1.005 | **0.929** |
| iron_mg | 1103 | 495 | 1.002 | 1.032 | **0.974** | 1.693 | 1.031 |
| niacin_mg | 807 | 363 | 1.001 | 1.067 | **0.998** | 1.534 | 1.232 |
| phosphorus_mg | 1106 | 498 | 1.007 | 1.036 | 0.925 | 0.916 | **0.768** |
| potassium_mg | 823 | 369 | 1.006 | 1.037 | **0.990** | 3.008 | 1.049 |
| protein_g | 1145 | 516 | 1.004 | 1.107 | 0.908 | **0.536** | 0.570 |
| retinol_mcg | 541 | 243 | 1.001 | 1.016 | 0.890 | 1.029 | **0.875** |
| sodium_mg | 864 | 390 | 1.004 | 1.032 | 1.016 | 1.059 | **0.953** |
| vitamin_b1_mg | 1058 | 477 | **1.002** | 1.003 | 1.002 | 1.015 | 1.216 |
| vitamin_b2_mg | 796 | 357 | **1.015** | 1.029 | 1.484 | 2.560 | 1.611 |
| vitamin_c_mg | 857 | 387 | 1.000 | 1.111 | 1.024 | 0.981 | **0.895** |
| water_g | 1144 | 516 | 1.001 | 1.055 | 0.616 | 0.330 | **0.221** |
| zinc_mg | 799 | 360 | 1.002 | 1.039 | **1.001** | 1.089 | 1.006 |

Jumlah nutrisi per metode terbaik: missforest 10, knn 5, mean 4, mice 2

## MyFCD

| Nutrisi | n terukur | n sel hold-out | mean | median | knn | mice | missforest | crossdb |
|---|---|---|---|---|---|---|---|---|
| ash_g | 139 | 210 | 1.013 | 1.044 | **1.004** | 2.198 | 1.158 | 2.630 |
| beta_carotene_mcg | 37 | 60 | 1.030 | **1.017** | 1.067 | 5.521 | 1.248 | 14547.369 |
| calcium_mg | 67 | 100 | 1.018 | 1.023 | 1.011 | 1.958 | 0.979 | **0.502** |
| carbohydrate_g | 109 | 160 | 1.026 | 1.074 | 0.725 | 0.731 | 0.617 | **0.495** |
| copper_mg | 49 | 70 | 1.023 | 1.015 | 1.015 | **1.011** | 1.045 | 3.007 |
| energy_kcal | 105 | 160 | 1.007 | 1.019 | 0.419 | 1.797 | 0.410 | **0.279** |
| fat_g | 151 | 230 | 1.015 | 1.077 | 1.085 | 0.857 | **0.564** | 0.969 |
| fiber_g | 139 | 210 | **1.004** | 1.032 | 1.086 | 2.130 | 1.129 | 1.027 |
| iron_mg | 48 | 70 | 1.026 | 1.009 | 1.008 | 0.921 | 1.120 | **0.860** |
| niacin_mg | 10 | 20 | 1.116 | **1.084** | 1.204 | 1.983 | 1.148 | 1.092 |
| phosphorus_mg | 107 | 160 | 1.013 | 1.005 | 1.020 | **0.934** | 0.999 | 0.980 |
| potassium_mg | 73 | 110 | 1.014 | 1.016 | 1.008 | 1.058 | 1.002 | **0.678** |
| protein_g | 150 | 220 | 1.013 | 1.055 | 1.020 | **0.825** | 1.024 | 1.120 |
| retinol_mcg | 38 | 60 | 1.077 | **1.072** | 1.098 | 9.247 | 1.114 | 13167.201 |
| sodium_mg | 64 | 100 | 1.017 | 1.012 | 1.009 | 1.023 | 1.015 | **0.996** |
| vitamin_b1_mg | 10 | 20 | 1.105 | **1.077** | 1.162 | 527.318 | 1.200 | 6.883 |
| vitamin_b2_mg | 10 | 20 | 1.122 | 1.085 | 1.075 | 1.818 | 1.085 | **0.930** |
| vitamin_c_mg | 27 | 40 | 1.082 | 1.118 | 0.929 | 0.953 | **0.915** | 4.280 |
| water_g | 150 | 220 | 1.005 | 1.017 | 0.913 | 2.498 | **0.512** | 0.592 |
| zinc_mg | 49 | 70 | 52.574 | 1.033 | 1.042 | 9.654 | 72.166 | **0.758** |

Jumlah nutrisi per metode terbaik: crossdb 8, median 4, mice 3, missforest 3, knn 1, mean 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 11 dari 20 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 1.158 | 2.630 | 1.473 |
| beta_carotene_mcg | 1.248 | 14547.369 | 14546.121 |
| calcium_mg | 0.979 | 0.502 | -0.477 |
| carbohydrate_g | 0.617 | 0.495 | -0.122 |
| copper_mg | 1.045 | 3.007 | 1.962 |
| energy_kcal | 0.410 | 0.279 | -0.132 |
| fat_g | 0.564 | 0.969 | 0.405 |
| fiber_g | 1.129 | 1.027 | -0.102 |
| iron_mg | 1.120 | 0.860 | -0.260 |
| niacin_mg | 1.148 | 1.092 | -0.055 |
| phosphorus_mg | 0.999 | 0.980 | -0.019 |
| potassium_mg | 1.002 | 0.678 | -0.324 |
| protein_g | 1.024 | 1.120 | 0.097 |
| retinol_mcg | 1.114 | 13167.201 | 13166.086 |
| sodium_mg | 1.015 | 0.996 | -0.020 |
| vitamin_b1_mg | 1.200 | 6.883 | 5.682 |
| vitamin_b2_mg | 1.085 | 0.930 | -0.155 |
| vitamin_c_mg | 0.915 | 4.280 | 3.365 |
| water_g | 0.512 | 0.592 | 0.079 |
| zinc_mg | 72.166 | 0.758 | -71.408 |
