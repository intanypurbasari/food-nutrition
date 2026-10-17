# Bootstrap Uncertainty

- B = 50 resample baris (dengan pengembalian) per sumber, seed 42+b; waktu 19 menit.
- Tiap replikasi melatih ulang MissForest pada resample lalu mengimputasi data asli, jadi tiap sel yang aslinya kosong mendapat B prediksi.
- relative_sd = sd bootstrap / sebaran nilai terukur nutrisi itu di sumber yang sama. Sebaran diukur dengan IQR/1,349 (setara sd untuk data normal, tetapi tahan outlier); bila IQR = 0, dipakai sd.
- Pasangan dengan kurang dari 5 sel imputasi tidak ditandai.
- Nutrisi **ditandai** (high_uncertainty) bila median relative_sd > 0.5.

| Sumber | Nutrisi | Metode | n sel imputasi | median sd | median lebar CI 95% | median relative_sd | p90 relative_sd | Tanda |
|---|---|---|---|---|---|---|---|---|
| TKPI | copper_mg | missforest | 351 | 1.27 | 2.47 | 5.692 | 141.340 | ⚠️ tinggi |
| TKPI | retinol_mcg | missforest | 605 | 102 | 326 | 3.520 | 19.227 | ⚠️ tinggi |
| TKPI | beta_carotene_mcg | missforest | 467 | 313 | 854 | 2.507 | 13.018 | ⚠️ tinggi |
| TKPI | carotene_total_mcg | missforest | 539 | 1.34e+03 | 4.63e+03 | 1.927 | 5.982 | ⚠️ tinggi |
| TKPI | sodium_mg | missforest | 282 | 82.1 | 290 | 0.706 | 5.356 | ⚠️ tinggi |
| TKPI | vitamin_c_mg | missforest | 289 | 5.04 | 15.5 | 0.618 | 2.451 | ⚠️ tinggi |
| TKPI | protein_g | missforest | 1 | 5.82 | 20.3 | 0.613 | 0.613 |  |
| TKPI | vitamin_b2_mg | missforest | 350 | 0.0661 | 0.236 | 0.525 | 1.221 | ⚠️ tinggi |
| TKPI | zinc_mg | missforest | 347 | 0.467 | 1.66 | 0.525 | 2.378 | ⚠️ tinggi |
| TKPI | niacin_mg | missforest | 339 | 0.686 | 2.43 | 0.487 | 2.061 |  |
| TKPI | vitamin_b1_mg | missforest | 88 | 0.0734 | 0.255 | 0.450 | 14.081 |  |
| TKPI | fiber_g | missforest | 221 | 1.08 | 3.67 | 0.439 | 1.301 |  |
| TKPI | calcium_mg | missforest | 40 | 34.4 | 122 | 0.349 | 0.681 |  |
| TKPI | iron_mg | missforest | 43 | 0.753 | 2.68 | 0.339 | 0.850 |  |
| TKPI | potassium_mg | missforest | 323 | 77.3 | 269 | 0.333 | 0.669 |  |
| TKPI | phosphorus_mg | missforest | 40 | 15.3 | 55.3 | 0.129 | 0.291 |  |
| TKPI | fat_g | missforest | 1 | 0.342 | 1.05 | 0.061 | 0.061 |  |
| TKPI | water_g | missforest | 2 | 0.558 | 2.17 | 0.014 | 0.015 |  |
| MyFCD | zinc_mg | missforest | 185 | 7.49 | 2.39 | 24.937 | 412.030 | ⚠️ tinggi |
| MyFCD | beta_carotene_mcg | crossdb | 234 | 545 | 1.27e+03 | 4.366 | 18.388 | ⚠️ tinggi |
| MyFCD | copper_mg | crossdb | 234 | 0.935 | 1.54 | 4.207 | 137.169 | ⚠️ tinggi |
| MyFCD | iron_mg | missforest | 186 | 2.04 | 7.34 | 3.320 | 36.897 | ⚠️ tinggi |
| MyFCD | retinol_mcg | crossdb | 234 | 93.9 | 289 | 3.247 | 49.461 | ⚠️ tinggi |
| MyFCD | niacin_mg | missforest | 224 | 3.54 | 11.8 | 2.442 | 3.105 | ⚠️ tinggi |
| MyFCD | vitamin_b1_mg | missforest | 224 | 0.157 | 0.544 | 2.360 | 3.160 | ⚠️ tinggi |
| MyFCD | vitamin_b2_mg | missforest | 224 | 0.38 | 1.18 | 2.084 | 2.716 | ⚠️ tinggi |
| MyFCD | carotene_total_mcg | crossdb | 234 | 1.27e+03 | 4.09e+03 | 1.832 | 4.914 | ⚠️ tinggi |
| MyFCD | fiber_g | missforest | 95 | 5.15 | 19.9 | 1.439 | 1.637 | ⚠️ tinggi |
| MyFCD | phosphorus_mg | missforest | 127 | 117 | 393 | 1.392 | 1.927 | ⚠️ tinggi |
| MyFCD | protein_g | missforest | 84 | 4.94 | 17.6 | 0.946 | 0.946 | ⚠️ tinggi |
| MyFCD | potassium_mg | missforest | 161 | 133 | 463 | 0.867 | 1.847 | ⚠️ tinggi |
| MyFCD | calcium_mg | missforest | 167 | 39 | 145 | 0.829 | 1.206 | ⚠️ tinggi |
| MyFCD | sodium_mg | missforest | 170 | 136 | 438 | 0.625 | 1.328 | ⚠️ tinggi |
| MyFCD | vitamin_c_mg | missforest | 207 | 1.87 | 6.79 | 0.558 | 0.648 | ⚠️ tinggi |
| MyFCD | fat_g | missforest | 83 | 6.66 | 22.3 | 0.490 | 0.727 |  |
| MyFCD | energy_kcal | missforest | 129 | 88.6 | 284 | 0.439 | 0.445 |  |
| MyFCD | water_g | missforest | 84 | 16.8 | 55.8 | 0.421 | 0.457 |  |
| MyFCD | ash_g | missforest | 95 | 0.427 | 1.59 | 0.380 | 0.608 |  |
| MyFCD | carbohydrate_g | missforest | 125 | 11.3 | 38.4 | 0.360 | 0.477 |  |

Nutrisi berketidakpastian tinggi: 24 dari 39 pasangan sumber x nutrisi.
