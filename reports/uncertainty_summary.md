# Bootstrap Uncertainty

- B = 50 resample baris (dengan pengembalian) per sumber, seed 42+b.
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
| MyFCD | zinc_mg | missforest | 185 | 17.9 | 53.4 | 59.728 | 463.105 | ⚠️ tinggi |
| MyFCD | iron_mg | missforest | 186 | 3.16 | 7.34 | 5.136 | 42.548 | ⚠️ tinggi |
| MyFCD | niacin_mg | missforest | 224 | 3.6 | 12 | 2.489 | 3.000 | ⚠️ tinggi |
| MyFCD | vitamin_b2_mg | missforest | 224 | 0.434 | 1.46 | 2.384 | 3.084 | ⚠️ tinggi |
| MyFCD | vitamin_b1_mg | missforest | 224 | 0.14 | 0.501 | 2.107 | 3.097 | ⚠️ tinggi |
| MyFCD | carotene_total_mcg | crossdb | 234 | 995 | 3.21e+03 | 1.434 | 3.887 | ⚠️ tinggi |
| MyFCD | phosphorus_mg | missforest | 127 | 110 | 379 | 1.313 | 2.034 | ⚠️ tinggi |
| MyFCD | calcium_mg | missforest | 167 | 43.7 | 145 | 0.931 | 1.232 | ⚠️ tinggi |
| MyFCD | protein_g | missforest | 84 | 4.78 | 16.1 | 0.914 | 0.914 | ⚠️ tinggi |
| MyFCD | fiber_g | missforest | 95 | 2.73 | 9.69 | 0.762 | 1.182 | ⚠️ tinggi |
| MyFCD | potassium_mg | missforest | 161 | 110 | 326 | 0.718 | 1.500 | ⚠️ tinggi |
| MyFCD | vitamin_c_mg | missforest | 207 | 2.26 | 7.67 | 0.673 | 0.734 | ⚠️ tinggi |
| MyFCD | sodium_mg | missforest | 170 | 129 | 445 | 0.591 | 0.814 | ⚠️ tinggi |
| MyFCD | fat_g | missforest | 83 | 6.28 | 20.8 | 0.462 | 0.631 |  |
| MyFCD | ash_g | missforest | 95 | 0.462 | 1.73 | 0.411 | 0.786 |  |
| MyFCD | water_g | missforest | 84 | 16.4 | 58.8 | 0.410 | 0.437 |  |
| MyFCD | energy_kcal | missforest | 129 | 80.7 | 279 | 0.400 | 0.419 |  |
| MyFCD | carbohydrate_g | missforest | 125 | 11.3 | 44.1 | 0.359 | 0.478 |  |
| MyFCD | retinol_mcg | missforest | 196 | 0.0293 | 0.0901 | 0.291 | 0.623 |  |
| MyFCD | beta_carotene_mcg | missforest | 197 | 0.0413 | 0.0867 | 0.193 | 1.906 |  |
| MyFCD | copper_mg | missforest | 185 | 1.99 | 4.03 | 0.069 | 0.620 |  |

Nutrisi berketidakpastian tinggi: 21 dari 39 pasangan sumber x nutrisi.
