# Hold-out Evaluation

- 15% nilai terukur per nutrisi disembunyikan; mask independen per pengulangan (seed 42+r): TKPI 3x, MyFCD 10x.
- Nutrisi dengan kurang dari 10 nilai terukur tidak dievaluasi.
- Outlier tertandai dikeluarkan: myfcd_0006, tkpi_0044, tkpi_0273, tkpi_0332, tkpi_0829, tkpi_0859.
- nRMSE = RMSE / sd(nilai asli yang disembunyikan). 1,0 setara menebak rerata; makin kecil makin baik.
- Angka di tabel adalah nRMSE gabungan seluruh sel hold-out dari semua pengulangan; **tebal** = metode terbaik untuk nutrisi itu.

## TKPI

| Nutrisi | n terukur | n sel hold-out | mean | median | group_median | knn | mice | missforest | missforest_ind |
|---|---|---|---|---|---|---|---|---|---|
| ash_g | 1141 | 513 | 1.004 | 1.051 | 0.987 | 1.633 | 1.512 | 0.993 | **0.891** |
| beta_carotene_mcg | 676 | 303 | 1.001 | 1.061 | 1.025 | **0.994** | 2.595 | 1.409 | 1.303 |
| calcium_mg | 1101 | 495 | 1.001 | 1.037 | 1.012 | 0.984 | 4.659 | 0.796 | **0.767** |
| carbohydrate_g | 1141 | 513 | 1.002 | 1.090 | 0.699 | 0.849 | **0.318** | 0.324 | 0.326 |
| carotene_total_mcg | 606 | 273 | 1.004 | 1.073 | **0.971** | 1.018 | 1.208 | 1.099 | 1.073 |
| copper_mg | 788 | 354 | 1.000 | 1.032 | 0.987 | 0.997 | 1.227 | **0.909** | 0.927 |
| energy_kcal | 1141 | 513 | 1.002 | 1.052 | 0.852 | 0.570 | 0.573 | 0.264 | **0.258** |
| fat_g | 1140 | 513 | 1.002 | 1.078 | 0.787 | 0.744 | 0.446 | **0.392** | 0.398 |
| fiber_g | 922 | 414 | 1.001 | 1.055 | 0.983 | 1.006 | 1.022 | **0.846** | 0.858 |
| iron_mg | 1098 | 495 | 1.001 | 1.053 | **0.988** | 1.039 | 1.759 | 1.071 | 1.005 |
| niacin_mg | 803 | 360 | **1.010** | 1.073 | 1.015 | 1.023 | 1.441 | 1.035 | 1.152 |
| phosphorus_mg | 1101 | 495 | 1.002 | 1.056 | 0.933 | 0.908 | 1.054 | 0.701 | **0.687** |
| potassium_mg | 817 | 369 | 1.001 | 1.016 | 0.995 | 1.031 | 0.978 | **0.808** | 0.823 |
| protein_g | 1140 | 513 | 1.005 | 1.109 | 0.768 | 0.925 | 0.669 | 0.591 | **0.570** |
| retinol_mcg | 536 | 240 | **1.003** | 1.022 | 1.014 | 1.236 | 1.049 | 1.548 | 1.655 |
| sodium_mg | 859 | 387 | **1.003** | 1.047 | 1.008 | 1.046 | 1.071 | 1.166 | 1.132 |
| vitamin_b1_mg | 1053 | 474 | 1.540 | 1.069 | **0.999** | 14.628 | 14.237 | 28.543 | 19.284 |
| vitamin_b2_mg | 791 | 357 | 1.006 | 1.038 | 1.003 | **0.986** | 2.497 | 2.659 | 3.061 |
| vitamin_c_mg | 854 | 384 | 1.001 | 1.096 | 0.958 | 1.023 | 1.100 | 0.915 | **0.906** |
| water_g | 1139 | 513 | 1.003 | 1.044 | 0.836 | 0.646 | 0.298 | **0.268** | 0.269 |
| zinc_mg | 793 | 357 | 1.006 | 1.056 | **0.997** | 1.019 | 1.068 | 1.105 | 1.102 |

Jumlah nutrisi per metode terbaik: missforest_ind 6, missforest 5, group_median 4, mean 3, knn 2, mice 1

## MyFCD

| Nutrisi | n terukur | n sel hold-out | mean | median | group_median | knn | mice | missforest | crossdb |
|---|---|---|---|---|---|---|---|---|---|
| ash_g | 138 | 210 | 1.011 | 1.032 | **0.875** | 0.993 | 0.979 | 0.960 | 2.570 |
| calcium_mg | 66 | 100 | 1.009 | 1.087 | 1.053 | 1.023 | **0.701** | 0.772 | 2.555 |
| carbohydrate_g | 108 | 160 | 1.016 | 1.061 | 0.646 | 0.770 | 0.538 | 0.600 | **0.514** |
| energy_kcal | 104 | 160 | 1.018 | 1.038 | 0.879 | 0.394 | **0.300** | 0.333 | 0.322 |
| fat_g | 150 | 220 | 1.008 | 1.073 | 0.600 | 0.924 | 0.937 | **0.515** | 0.896 |
| fiber_g | 138 | 210 | 1.007 | 1.045 | **0.997** | 1.035 | 1.074 | 1.014 | 1.081 |
| iron_mg | 47 | 70 | 1.022 | 1.104 | 1.016 | 1.021 | **0.831** | 0.836 | 2.597 |
| phosphorus_mg | 106 | 160 | 1.006 | 1.067 | **0.693** | 0.989 | 0.877 | 0.955 | 1.051 |
| potassium_mg | 72 | 110 | 1.015 | 1.082 | 1.001 | 1.029 | 1.118 | **0.680** | 0.735 |
| protein_g | 149 | 220 | 1.012 | 1.049 | 0.977 | 1.028 | **0.608** | 0.850 | 1.032 |
| sodium_mg | 63 | 90 | 1.014 | 1.258 | 0.910 | 0.872 | 0.854 | **0.797** | 1.731 |
| vitamin_c_mg | 26 | 40 | 1.031 | 1.045 | **0.891** | 1.262 | 1.110 | 1.062 | 4.137 |
| water_g | 149 | 220 | 1.008 | 1.024 | 0.744 | 0.852 | **0.537** | 0.573 | 0.568 |
| zinc_mg | 48 | 70 | 1.038 | 1.007 | 0.982 | 0.986 | **0.341** | 0.785 | 1.917 |

Jumlah nutrisi per metode terbaik: mice 6, group_median 4, missforest 3, crossdb 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 3 dari 14 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 0.960 | 2.570 | 1.610 |
| calcium_mg | 0.772 | 2.555 | 1.783 |
| carbohydrate_g | 0.600 | 0.514 | -0.086 |
| energy_kcal | 0.333 | 0.322 | -0.011 |
| fat_g | 0.515 | 0.896 | 0.381 |
| fiber_g | 1.014 | 1.081 | 0.067 |
| iron_mg | 0.836 | 2.597 | 1.761 |
| phosphorus_mg | 0.955 | 1.051 | 0.096 |
| potassium_mg | 0.680 | 0.735 | 0.056 |
| protein_g | 0.850 | 1.032 | 0.182 |
| sodium_mg | 0.797 | 1.731 | 0.934 |
| vitamin_c_mg | 1.062 | 4.137 | 3.074 |
| water_g | 0.573 | 0.568 | -0.005 |
| zinc_mg | 0.785 | 1.917 | 1.132 |
