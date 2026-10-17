# Hold-out Evaluation

- 15% nilai terukur per nutrisi disembunyikan; mask independen per pengulangan (seed 42+r): TKPI 3x, MyFCD 10x.
- Nutrisi dengan kurang dari 10 nilai terukur tidak dievaluasi.
- Outlier tertandai dikeluarkan: myfcd_0006.
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
| ash_g | 138 | 210 | 1.011 | 1.032 | 0.993 | 1.062 | **0.927** | 1.427 |
| beta_carotene_mcg | 36 | 50 | 1.031 | **1.021** | 1.051 | 1.118 | 1.272 | 13730.479 |
| calcium_mg | 66 | 100 | 1.009 | 1.087 | 1.026 | **0.701** | 0.779 | 1.082 |
| carbohydrate_g | 108 | 160 | 1.016 | 1.061 | 0.773 | 0.545 | 0.630 | **0.499** |
| copper_mg | 48 | 70 | 1.027 | **1.023** | 1.060 | 1.158 | 1.225 | 2219.521 |
| energy_kcal | 104 | 160 | 1.018 | 1.038 | 0.395 | **0.283** | 0.320 | 0.329 |
| fat_g | 150 | 220 | 1.008 | 1.073 | 0.978 | 0.937 | **0.427** | 0.950 |
| fiber_g | 138 | 210 | 1.007 | 1.045 | 1.029 | 1.107 | **0.895** | 1.037 |
| iron_mg | 47 | 70 | 1.022 | 1.104 | 1.006 | **0.815** | 0.868 | 1.972 |
| phosphorus_mg | 106 | 160 | 1.006 | 1.067 | 1.001 | **0.874** | 0.962 | 0.908 |
| potassium_mg | 72 | 110 | 1.015 | 1.082 | 1.072 | 1.132 | **0.696** | 0.767 |
| protein_g | 149 | 220 | 1.012 | 1.049 | 1.027 | **0.615** | 0.819 | 1.007 |
| retinol_mcg | 37 | 60 | 1.120 | **1.020** | 1.612 | 1.951 | 1.604 | 16866.192 |
| sodium_mg | 63 | 90 | 1.014 | 1.258 | 0.866 | 0.854 | **0.755** | 1.339 |
| vitamin_c_mg | 26 | 40 | 1.063 | 1.040 | 0.993 | **0.974** | 1.252 | 4.113 |
| water_g | 149 | 220 | 1.008 | 1.024 | 0.851 | 0.544 | **0.525** | 0.559 |
| zinc_mg | 48 | 70 | 1.029 | 1.037 | 1.016 | **0.360** | 0.840 | 0.773 |

Jumlah nutrisi per metode terbaik: mice 7, missforest 6, median 3, crossdb 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 3 dari 17 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 0.927 | 1.427 | 0.500 |
| beta_carotene_mcg | 1.272 | 13730.479 | 13729.207 |
| calcium_mg | 0.779 | 1.082 | 0.303 |
| carbohydrate_g | 0.630 | 0.499 | -0.131 |
| copper_mg | 1.225 | 2219.521 | 2218.297 |
| energy_kcal | 0.320 | 0.329 | 0.009 |
| fat_g | 0.427 | 0.950 | 0.523 |
| fiber_g | 0.895 | 1.037 | 0.141 |
| iron_mg | 0.868 | 1.972 | 1.103 |
| phosphorus_mg | 0.962 | 0.908 | -0.054 |
| potassium_mg | 0.696 | 0.767 | 0.071 |
| protein_g | 0.819 | 1.007 | 0.188 |
| retinol_mcg | 1.604 | 16866.192 | 16864.588 |
| sodium_mg | 0.755 | 1.339 | 0.584 |
| vitamin_c_mg | 1.252 | 4.113 | 2.862 |
| water_g | 0.525 | 0.559 | 0.034 |
| zinc_mg | 0.840 | 0.773 | -0.068 |
