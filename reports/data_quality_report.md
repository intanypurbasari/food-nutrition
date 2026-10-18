# Data Quality Report

- Total rows: 1380
- Valid rows: 1380
- Invalid rows: 0
- Duplicate count: 0

## Issues by Type
- No hard validation issues found.

## Warnings by Type
- outlier_minerals_exceed_ash: 5
- range_warning: 4
- outlier_implausible_minerals: 1

## Outliers
Baris berikut ditandai sebagai outlier. Nilainya dibiarkan apa adanya dan tetap ikut imputasi.

- TKPI tkpi_0044 (Misoa): outlier_minerals_exceed_ash, mineral_total_g=3.289
- TKPI tkpi_0273 (Kacang panjang, biji, kering (Yardlong bean, seeded, dried)): outlier_minerals_exceed_ash, mineral_total_g=1.735
- TKPI tkpi_0332 (Keju kacang tanah (peanut butter)): outlier_minerals_exceed_ash, mineral_total_g=1.273
- TKPI tkpi_0829 (Oramu ninahu ndawa olaho, masakan): outlier_minerals_exceed_ash, mineral_total_g=2.499
- TKPI tkpi_0859 (Tinoransa, masakan): outlier_minerals_exceed_ash, mineral_total_g=2.978
- MyFCD myfcd_0006 (BREAD, RAISIN (ROTI KISMIS)): outlier_implausible_minerals, mineral_total_g=166.313

## Source Detail
- TKPI: 1146/1146 valid rows
- MyFCD: 234/234 valid rows