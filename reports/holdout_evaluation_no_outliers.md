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
| ash_g | 138 | 210 | 1.011 | 1.032 | 0.993 | 0.979 | **0.960** | 1.188 |
| calcium_mg | 66 | 100 | 1.009 | 1.087 | 1.023 | **0.701** | 0.772 | 1.184 |
| carbohydrate_g | 108 | 160 | 1.016 | 1.061 | 0.770 | 0.538 | 0.600 | **0.494** |
| energy_kcal | 104 | 160 | 1.018 | 1.038 | 0.394 | **0.300** | 0.333 | 0.329 |
| fat_g | 150 | 220 | 1.008 | 1.073 | 0.924 | 0.937 | **0.515** | 0.936 |
| fiber_g | 138 | 210 | **1.007** | 1.045 | 1.035 | 1.074 | 1.014 | 1.023 |
| iron_mg | 47 | 70 | 1.022 | 1.104 | 1.021 | **0.831** | 0.836 | 2.016 |
| phosphorus_mg | 106 | 160 | 1.006 | 1.067 | 0.989 | **0.877** | 0.955 | 0.905 |
| potassium_mg | 72 | 110 | 1.015 | 1.082 | 1.029 | 1.118 | **0.680** | 0.846 |
| protein_g | 149 | 220 | 1.012 | 1.049 | 1.028 | **0.608** | 0.850 | 1.029 |
| sodium_mg | 63 | 90 | 1.014 | 1.258 | 0.872 | 0.854 | **0.797** | 1.085 |
| vitamin_c_mg | 26 | 40 | **1.031** | 1.045 | 1.262 | 1.110 | 1.062 | 3.831 |
| water_g | 149 | 220 | 1.008 | 1.024 | 0.852 | **0.537** | 0.573 | 0.549 |
| zinc_mg | 48 | 70 | 1.038 | 1.007 | 0.986 | **0.341** | 0.785 | 1.822 |

Jumlah nutrisi per metode terbaik: mice 7, missforest 4, mean 2, crossdb 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 4 dari 14 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 0.960 | 1.188 | 0.229 |
| calcium_mg | 0.772 | 1.184 | 0.412 |
| carbohydrate_g | 0.600 | 0.494 | -0.106 |
| energy_kcal | 0.333 | 0.329 | -0.004 |
| fat_g | 0.515 | 0.936 | 0.421 |
| fiber_g | 1.014 | 1.023 | 0.010 |
| iron_mg | 0.836 | 2.016 | 1.180 |
| phosphorus_mg | 0.955 | 0.905 | -0.051 |
| potassium_mg | 0.680 | 0.846 | 0.166 |
| protein_g | 0.850 | 1.029 | 0.178 |
| sodium_mg | 0.797 | 1.085 | 0.289 |
| vitamin_c_mg | 1.062 | 3.831 | 2.769 |
| water_g | 0.573 | 0.549 | -0.024 |
| zinc_mg | 0.785 | 1.822 | 1.037 |
