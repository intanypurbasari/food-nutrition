# Bootstrap Uncertainty

- B = 50 resample baris (dengan pengembalian) per sumber, seed 42+b; waktu 17 menit.
- Tiap replikasi melatih ulang MissForest pada resample lalu mengimputasi data asli, jadi tiap sel yang aslinya kosong mendapat B prediksi.
- relative_sd = sd bootstrap / sebaran nilai terukur nutrisi itu di sumber yang sama. Sebaran diukur dengan IQR/1,349 (setara sd untuk data normal, tetapi tahan outlier); bila IQR = 0, dipakai sd.
- Pasangan dengan kurang dari 5 sel imputasi tidak ditandai.
- Nutrisi **ditandai** (high_uncertainty) bila median relative_sd > 0.5.

| Sumber | Nutrisi | Metode | n sel imputasi | median sd | median lebar CI 95% | median relative_sd | p90 relative_sd | Tanda |
|---|---|---|---|---|---|---|---|---|
| TKPI | retinol_mcg | missforest | 605 | 101 | 324 | 3.477 | 18.654 | ⚠️ tinggi |
| TKPI | beta_carotene_mcg | missforest | 467 | 404 | 1.19e+03 | 3.237 | 14.418 | ⚠️ tinggi |
| TKPI | carotene_total_mcg | missforest | 539 | 1.24e+03 | 4.09e+03 | 1.787 | 5.402 | ⚠️ tinggi |
| TKPI | sodium_mg | missforest | 283 | 80.1 | 277 | 0.695 | 5.739 | ⚠️ tinggi |
| TKPI | copper_mg | missforest | 353 | 0.127 | 0.406 | 0.591 | 2.446 | ⚠️ tinggi |
| TKPI | vitamin_c_mg | missforest | 289 | 4.71 | 15.3 | 0.578 | 2.266 | ⚠️ tinggi |
| TKPI | protein_g | missforest | 1 | 5.3 | 20 | 0.558 | 0.558 |  |
| TKPI | vitamin_b2_mg | missforest | 350 | 0.0627 | 0.223 | 0.498 | 1.885 |  |
| TKPI | niacin_mg | missforest | 339 | 0.687 | 2.47 | 0.488 | 1.891 |  |
| TKPI | vitamin_b1_mg | missforest | 88 | 0.073 | 0.26 | 0.447 | 42.730 |  |
| TKPI | zinc_mg | missforest | 348 | 0.383 | 1.39 | 0.430 | 1.779 |  |
| TKPI | fiber_g | missforest | 221 | 0.97 | 3.29 | 0.397 | 1.300 |  |
| TKPI | calcium_mg | missforest | 40 | 30.5 | 114 | 0.309 | 0.773 |  |
| TKPI | iron_mg | missforest | 43 | 0.67 | 2.48 | 0.301 | 0.805 |  |
| TKPI | potassium_mg | missforest | 324 | 68 | 244 | 0.293 | 0.747 |  |
| TKPI | phosphorus_mg | missforest | 40 | 16.7 | 58.3 | 0.141 | 0.304 |  |
| TKPI | fat_g | missforest | 1 | 0.239 | 0.933 | 0.043 | 0.043 |  |
| TKPI | water_g | missforest | 2 | 0.542 | 2.02 | 0.013 | 0.016 |  |
| MyFCD | zinc_mg | missforest | 185 | 7.49 | 2.39 | 24.937 | 412.030 | ⚠️ tinggi |
| MyFCD | iron_mg | missforest | 186 | 2.04 | 7.34 | 3.320 | 36.897 | ⚠️ tinggi |
| MyFCD | retinol_mcg | crossdb | 234 | 87 | 327 | 3.010 | 51.803 | ⚠️ tinggi |
| MyFCD | beta_carotene_mcg | crossdb | 234 | 340 | 813 | 2.724 | 17.348 | ⚠️ tinggi |
| MyFCD | niacin_mg | missforest | 224 | 3.54 | 11.8 | 2.442 | 3.105 | ⚠️ tinggi |
| MyFCD | vitamin_b1_mg | missforest | 224 | 0.157 | 0.544 | 2.360 | 3.160 | ⚠️ tinggi |
| MyFCD | vitamin_b2_mg | missforest | 224 | 0.38 | 1.18 | 2.084 | 2.716 | ⚠️ tinggi |
| MyFCD | fiber_g | missforest | 95 | 5.15 | 19.9 | 1.439 | 1.637 | ⚠️ tinggi |
| MyFCD | carotene_total_mcg | crossdb | 234 | 991 | 3.31e+03 | 1.428 | 4.669 | ⚠️ tinggi |
| MyFCD | phosphorus_mg | missforest | 127 | 117 | 393 | 1.392 | 1.927 | ⚠️ tinggi |
| MyFCD | protein_g | missforest | 84 | 4.94 | 17.6 | 0.946 | 0.946 | ⚠️ tinggi |
| MyFCD | potassium_mg | missforest | 161 | 133 | 463 | 0.867 | 1.847 | ⚠️ tinggi |
| MyFCD | calcium_mg | missforest | 167 | 39 | 145 | 0.829 | 1.206 | ⚠️ tinggi |
| MyFCD | sodium_mg | missforest | 170 | 136 | 438 | 0.625 | 1.328 | ⚠️ tinggi |
| MyFCD | vitamin_c_mg | missforest | 207 | 1.87 | 6.79 | 0.558 | 0.648 | ⚠️ tinggi |
| MyFCD | copper_mg | crossdb | 234 | 0.109 | 0.372 | 0.505 | 3.634 | ⚠️ tinggi |
| MyFCD | fat_g | missforest | 83 | 6.66 | 22.3 | 0.490 | 0.727 |  |
| MyFCD | energy_kcal | missforest | 129 | 88.6 | 284 | 0.439 | 0.445 |  |
| MyFCD | water_g | missforest | 84 | 16.8 | 55.8 | 0.421 | 0.457 |  |
| MyFCD | ash_g | missforest | 95 | 0.427 | 1.59 | 0.380 | 0.608 |  |
| MyFCD | carbohydrate_g | missforest | 125 | 11.3 | 38.4 | 0.360 | 0.477 |  |

Nutrisi berketidakpastian tinggi: 22 dari 39 pasangan sumber x nutrisi.
