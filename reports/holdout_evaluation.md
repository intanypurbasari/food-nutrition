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
| ash_g | 139 | 210 | 1.013 | 1.044 | **1.007** | 2.568 | 1.070 | 2.394 |
| calcium_mg | 67 | 100 | 1.018 | 1.023 | 1.010 | 1.436 | 0.984 | **0.537** |
| carbohydrate_g | 109 | 160 | 1.026 | 1.074 | 0.725 | 0.854 | 0.634 | **0.491** |
| energy_kcal | 105 | 160 | 1.007 | 1.019 | 0.426 | 1.757 | 0.436 | **0.278** |
| fat_g | 151 | 230 | 1.015 | 1.077 | 1.063 | 0.875 | **0.579** | 0.963 |
| fiber_g | 139 | 210 | **1.004** | 1.032 | 1.084 | 3.025 | 1.043 | 1.018 |
| iron_mg | 48 | 70 | 1.026 | 1.009 | 1.008 | **0.667** | 1.113 | 0.887 |
| niacin_mg | 10 | 20 | 1.098 | 1.123 | 1.179 | 127.626 | 1.303 | **1.010** |
| phosphorus_mg | 107 | 160 | 1.013 | 1.005 | 1.020 | **0.963** | 1.007 | 0.976 |
| potassium_mg | 73 | 110 | 1.014 | 1.016 | 1.005 | 0.785 | 0.991 | **0.667** |
| protein_g | 150 | 220 | 1.013 | 1.055 | 1.020 | **0.763** | 0.981 | 1.170 |
| sodium_mg | 64 | 100 | 1.017 | 1.012 | 1.008 | **0.914** | 1.044 | 0.998 |
| vitamin_b1_mg | 10 | 20 | 1.124 | **1.085** | 1.192 | 371.852 | 1.298 | 1.825 |
| vitamin_b2_mg | 10 | 20 | 1.122 | 1.093 | 1.082 | 4.741 | 1.076 | **0.324** |
| vitamin_c_mg | 27 | 40 | 1.079 | **1.024** | 1.183 | 1.083 | 1.106 | 4.508 |
| water_g | 150 | 220 | 1.005 | 1.017 | 0.924 | 2.574 | **0.530** | 0.618 |
| zinc_mg | 49 | 70 | 1.023 | 1.015 | 1.014 | 1.005 | 1.043 | **0.999** |

Jumlah nutrisi per metode terbaik: crossdb 7, mice 4, missforest 2, median 2, knn 1, mean 1

## MyFCD: cross-DB transfer vs MissForest internal

Cross-DB transfer (dilatih pada TKPI) lebih akurat pada 11 dari 17 nutrisi.

| Nutrisi | missforest | crossdb | selisih (crossdb - missforest) |
|---|---|---|---|
| ash_g | 1.070 | 2.394 | 1.324 |
| calcium_mg | 0.984 | 0.537 | -0.447 |
| carbohydrate_g | 0.634 | 0.491 | -0.143 |
| energy_kcal | 0.436 | 0.278 | -0.158 |
| fat_g | 0.579 | 0.963 | 0.384 |
| fiber_g | 1.043 | 1.018 | -0.026 |
| iron_mg | 1.113 | 0.887 | -0.226 |
| niacin_mg | 1.303 | 1.010 | -0.293 |
| phosphorus_mg | 1.007 | 0.976 | -0.030 |
| potassium_mg | 0.991 | 0.667 | -0.324 |
| protein_g | 0.981 | 1.170 | 0.189 |
| sodium_mg | 1.044 | 0.998 | -0.045 |
| vitamin_b1_mg | 1.298 | 1.825 | 0.527 |
| vitamin_b2_mg | 1.076 | 0.324 | -0.752 |
| vitamin_c_mg | 1.106 | 4.508 | 3.403 |
| water_g | 0.530 | 0.618 | 0.088 |
| zinc_mg | 1.043 | 0.999 | -0.044 |
