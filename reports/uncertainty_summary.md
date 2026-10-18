# Bootstrap Uncertainty

- B = 50 resample baris (dengan pengembalian) per sumber, seed 42+b; waktu 18 menit.
- Tiap replikasi melatih ulang metode yang dipakai Tahap 3 untuk nutrisi itu (data_processed/method_selection.csv) pada resample, lalu mengimputasi data asli; tiap sel yang aslinya kosong mendapat B prediksi.
- relative_sd = sd bootstrap / sebaran nilai terukur nutrisi itu di sumber yang sama. Sebaran diukur dengan IQR/1,349 (setara sd untuk data normal, tetapi tahan outlier); bila IQR = 0, dipakai sd.
- Pasangan dengan kurang dari 5 sel imputasi tidak ditandai.
- Nutrisi **ditandai** (high_uncertainty) bila median relative_sd > 0.5.

| Sumber | Nutrisi | Metode | n sel imputasi | median sd | median lebar CI 95% | median relative_sd | p90 relative_sd | Tanda |
|---|---|---|---|---|---|---|---|---|
| TKPI | carotene_total_mcg | knn | 539 | 602 | 1.96e+03 | 0.868 | 2.278 | ⚠️ tinggi |
| TKPI | copper_mg | missforest | 353 | 0.127 | 0.406 | 0.591 | 2.446 | ⚠️ tinggi |
| TKPI | vitamin_c_mg | missforest | 289 | 4.71 | 15.3 | 0.578 | 2.266 | ⚠️ tinggi |
| TKPI | vitamin_b2_mg | knn | 350 | 0.0645 | 0.23 | 0.511 | 1.382 | ⚠️ tinggi |
| TKPI | niacin_mg | missforest | 339 | 0.687 | 2.47 | 0.488 | 1.891 |  |
| TKPI | fiber_g | missforest | 221 | 0.97 | 3.29 | 0.397 | 1.300 |  |
| TKPI | calcium_mg | missforest | 40 | 30.5 | 114 | 0.309 | 0.773 |  |
| TKPI | iron_mg | missforest | 43 | 0.67 | 2.48 | 0.301 | 0.805 |  |
| TKPI | potassium_mg | missforest | 324 | 68 | 244 | 0.293 | 0.747 |  |
| TKPI | phosphorus_mg | missforest | 40 | 16.7 | 58.3 | 0.141 | 0.304 |  |
| TKPI | zinc_mg | group_median | 348 | 0.0818 | 0.366 | 0.092 | 0.308 |  |
| TKPI | sodium_mg | group_median | 283 | 10.5 | 28 | 0.091 | 0.473 |  |
| TKPI | protein_g | mice | 1 | 0.777 | 2.55 | 0.082 | 0.082 |  |
| TKPI | vitamin_b1_mg | group_median | 88 | 0.0132 | 0.0477 | 0.081 | 0.219 |  |
| TKPI | beta_carotene_mcg | group_median | 467 | 6.13 | 19.5 | 0.049 | 0.976 |  |
| TKPI | fat_g | missforest | 1 | 0.239 | 0.933 | 0.043 | 0.043 |  |
| TKPI | water_g | missforest | 2 | 0.542 | 2.02 | 0.013 | 0.016 |  |
| TKPI | retinol_mcg | group_median | 605 | 0 | 0 | 0.000 | 0.234 |  |
| MyFCD | sodium_mg | mice | 170 | 1.01e+03 | 3.13e+03 | 4.646 | 5.612 | ⚠️ tinggi |
| MyFCD | iron_mg | mice | 186 | 2.85 | 8.61 | 4.632 | 5.849 | ⚠️ tinggi |
| MyFCD | retinol_mcg | crossdb | 234 | 87 | 327 | 3.010 | 51.803 | ⚠️ tinggi |
| MyFCD | beta_carotene_mcg | crossdb | 234 | 340 | 813 | 2.724 | 17.348 | ⚠️ tinggi |
| MyFCD | vitamin_b2_mg | missforest | 224 | 0.38 | 1.18 | 2.084 | 2.716 | ⚠️ tinggi |
| MyFCD | carotene_total_mcg | crossdb | 234 | 991 | 3.31e+03 | 1.428 | 4.669 | ⚠️ tinggi |
| MyFCD | potassium_mg | mice | 161 | 216 | 679 | 1.407 | 2.183 | ⚠️ tinggi |
| MyFCD | zinc_mg | crossdb | 185 | 0.409 | 1.54 | 1.360 | 7.276 | ⚠️ tinggi |
| MyFCD | vitamin_b1_mg | group_median | 224 | 0.0664 | 0.129 | 1.000 | 1.167 | ⚠️ tinggi |
| MyFCD | calcium_mg | crossdb | 167 | 34.8 | 130 | 0.740 | 1.889 | ⚠️ tinggi |
| MyFCD | copper_mg | crossdb | 234 | 0.109 | 0.372 | 0.505 | 3.634 | ⚠️ tinggi |
| MyFCD | fat_g | missforest | 83 | 6.66 | 22.3 | 0.490 | 0.727 |  |
| MyFCD | phosphorus_mg | crossdb | 127 | 37.6 | 142 | 0.447 | 0.479 |  |
| MyFCD | water_g | missforest | 84 | 16.8 | 55.8 | 0.421 | 0.457 |  |
| MyFCD | niacin_mg | crossdb | 224 | 0.537 | 1.79 | 0.371 | 2.844 |  |
| MyFCD | carbohydrate_g | crossdb | 125 | 10.2 | 36.9 | 0.325 | 0.349 |  |
| MyFCD | ash_g | group_median | 95 | 0.217 | 0.793 | 0.193 | 0.543 |  |
| MyFCD | protein_g | mice | 84 | 0.959 | 3.24 | 0.184 | 1.161 |  |
| MyFCD | vitamin_c_mg | group_median | 207 | 0.518 | 2.49 | 0.155 | 0.349 |  |
| MyFCD | energy_kcal | crossdb | 129 | 30.1 | 113 | 0.149 | 0.288 |  |
| MyFCD | fiber_g | mean | 95 | 0.456 | 1.82 | 0.127 | 0.127 |  |

Nutrisi berketidakpastian tinggi: 15 dari 39 pasangan sumber x nutrisi.
