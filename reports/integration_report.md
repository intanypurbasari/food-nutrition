# Integrasi TKPI + MyFCD

- Baris sebelum integrasi: 1380 (TKPI 1146, MyFCD 234)
- Pasangan dilebur (`identik` di tkpi_myfcd_links_curated.csv): 8
- Baris setelah integrasi: 1372
- Tautan lain: berbeda 32, mirip 12 (tetap baris terpisah)

Aturan nilai pasangan yang dilebur (per nutrisi): terukur di TKPI > terukur di MyFCD > nilai imputasi TKPI.

## Pasangan yang dilebur

| TKPI | MyFCD | Catatan |
|---|---|---|
| tkpi_1083 Minyak kelapa (Coconut oil) | myfcd_0110 OIL, COCONUT (MINYAK KELAPA) | pangan sama (minyak kelapa) |
| tkpi_0467 Jagung muda / semi, segar (Baby corn, fresh) | myfcd_0035 BABY CORN (JAGUNG SAYUR) | pangan sama (jagung muda) |
| tkpi_0833 Rendang sapi, masakan | myfcd_0215 BEEF RENDANG (RENDANG DAGING LEMBU) | hidangan sama (rendang daging sapi) |
| tkpi_1100 Madu (Honey) | myfcd_0060 HONEY | pangan sama (madu) |
| tkpi_0621 Buah Naga Merah, segar | myfcd_0040 DRAGON FRUIT, RED (BUAH NAGA, ISI MERAH) | pangan sama (buah naga merah, segar) |
| tkpi_0622 Buah Naga Putih, segar | myfcd_0041 DRAGON FRUIT, WHITE (BUAH NAGA, ISI PUTIH) | pangan sama (buah naga putih, segar) |
| tkpi_0191 Bubur sagu | myfcd_0193 DESSERT, SAGO PORRIDGE (BUBUR SAGU) | hidangan sama (bubur sagu) |
| tkpi_1088 Mentega (Margarine) | myfcd_0114 SOFT MARGARINE (MARJERIN LEMBUT) | pangan sama (margarin) |

Nilai TKPI yang tadinya hasil imputasi dan kini diganti nilai terukur MyFCD: 1 sel.

## Asal nilai (seluruh sel dataset terintegrasi)

| Asal nilai | Jumlah sel | % |
|---|---|---|
| measured_TKPI | 19733 | 51.4 |
| USDA_model | 7201 | 18.7 |
| imputed:group_median | 2302 | 6.0 |
| transfer_TKPI | 1836 | 4.8 |
| imputed:missforest | 1743 | 4.5 |
| measured_MyFCD | 1340 | 3.5 |
| USDA_direct_medium | 845 | 2.2 |
| imputed:missforest_ind | 828 | 2.2 |
| vitamin_a:derived_partly_imputed | 642 | 1.7 |
| imputed:mice | 587 | 1.5 |
| vitamin_a:derived_imputed | 389 | 1.0 |
| imputed:knn | 350 | 0.9 |
| vitamin_a:derived_measured | 289 | 0.8 |
| USDA_direct_high | 186 | 0.5 |
| imputed:mean | 93 | 0.2 |
| vitamin_a:USDA_direct_medium | 35 | 0.1 |
| vitamin_a:USDA_direct_high | 17 | 0.0 |

## Konflik (terukur di kedua basis data; nilai TKPI dipakai)

| Pangan | Nutrisi | TKPI | MyFCD | Selisih relatif |
|---|---|---|---|---|
| Minyak kelapa (Coconut oil) | water_g | 0 | 0.204 | 100% |
| Rendang sapi, masakan | fiber_g | 0 | 2.9333 | 100% |
| Minyak kelapa (Coconut oil) | phosphorus_mg | 0 | 0.3931 | 100% |
| Madu (Honey) | fiber_g | 0.2 | 0 | 100% |
| Jagung muda / semi, segar (Baby corn, fresh) | sodium_mg | 353 | 3.5833 | 99% |
| Buah Naga Merah, segar | fat_g | 3.1 | 0.0667 | 98% |
| Bubur sagu | protein_g | 0.2 | 2.8533 | 93% |
| Minyak kelapa (Coconut oil) | protein_g | 1 | 0.0762 | 92% |
| Buah Naga Putih, segar | fat_g | 1 | 0.15 | 85% |
| Madu (Honey) | protein_g | 0.3 | 0.0467 | 84% |
| Mentega (Margarine) | potassium_mg | 103 | 16.7375 | 84% |
| Rendang sapi, masakan | ash_g | 3.8 | 0.8467 | 78% |
| Madu (Honey) | ash_g | 0.2 | 0.0467 | 77% |
| Buah Naga Merah, segar | fiber_g | 3.2 | 0.8667 | 73% |
| Buah Naga Merah, segar | iron_mg | 0.4 | 0.1333 | 67% |
| Rendang sapi, masakan | fat_g | 7.9 | 23.46 | 66% |
| Buah Naga Putih, segar | fiber_g | 3.2 | 1.1 | 66% |
| Buah Naga Putih, segar | vitamin_c_mg | 1 | 2.55 | 61% |
| Buah Naga Putih, segar | iron_mg | 0.5 | 0.2 | 60% |
| Jagung muda / semi, segar (Baby corn, fresh) | phosphorus_mg | 100 | 40.0333 | 60% |
| Buah Naga Putih, segar | sodium_mg | 7 | 16.95 | 59% |
| Rendang sapi, masakan | carbohydrate_g | 7.8 | 18.4833 | 58% |
| Buah Naga Merah, segar | vitamin_c_mg | 1 | 2.3667 | 58% |
| Mentega (Margarine) | phosphorus_mg | 16 | 6.914 | 57% |
| Jagung muda / semi, segar (Baby corn, fresh) | calcium_mg | 7 | 15.3667 | 54% |
| Buah Naga Putih, segar | protein_g | 0.8 | 1.6 | 50% |
| Bubur sagu | ash_g | 0.3 | 0.5767 | 48% |
| Rendang sapi, masakan | energy_kcal | 193 | 360.1 | 46% |
| Jagung muda / semi, segar (Baby corn, fresh) | potassium_mg | 230.2 | 133.333 | 42% |
| Buah Naga Merah, segar | phosphorus_mg | 14 | 23.9333 | 42% |
| Buah Naga Putih, segar | calcium_mg | 13 | 7.75 | 40% |
| Jagung muda / semi, segar (Baby corn, fresh) | iron_mg | 0.5 | 0.3 | 40% |
| Jagung muda / semi, segar (Baby corn, fresh) | zinc_mg | 0.8 | 0.4833 | 40% |
| Buah Naga Merah, segar | sodium_mg | 10 | 16.3 | 39% |
| Rendang sapi, masakan | water_g | 57.9 | 35.52 | 39% |
| Jagung muda / semi, segar (Baby corn, fresh) | ash_g | 0.8 | 0.55 | 31% |
| Buah Naga Merah, segar | calcium_mg | 13 | 8.9667 | 31% |
| Bubur sagu | energy_kcal | 167 | 240.317 | 31% |
| Bubur sagu | carbohydrate_g | 33 | 47.1767 | 30% |
| Bubur sagu | water_g | 62.5 | 44.0077 | 30% |
| Buah Naga Merah, segar | ash_g | 0.4 | 0.5667 | 29% |
| Buah Naga Merah, segar | energy_kcal | 71 | 51.3333 | 28% |
| Jagung muda / semi, segar (Baby corn, fresh) | fiber_g | 1.9 | 1.4167 | 25% |
| Buah Naga Merah, segar | potassium_mg | 128 | 167.067 | 23% |
| Buah Naga Putih, segar | potassium_mg | 231 | 181.95 | 21% |
| Buah Naga Merah, segar | protein_g | 1.7 | 1.3667 | 20% |
| Jagung muda / semi, segar (Baby corn, fresh) | carbohydrate_g | 7.4 | 6.1167 | 17% |
| Rendang sapi, masakan | protein_g | 22.6 | 18.7567 | 17% |
| Buah Naga Merah, segar | carbohydrate_g | 9.1 | 10.9 | 17% |
| Buah Naga Merah, segar | zinc_mg | 0.4 | 0.4667 | 14% |
| Buah Naga Putih, segar | zinc_mg | 0.4 | 0.45 | 11% |
| Bubur sagu | fat_g | 4 | 4.4667 | 10% |
| Jagung muda / semi, segar (Baby corn, fresh) | vitamin_c_mg | 8 | 8.9 | 10% |
| Madu (Honey) | energy_kcal | 294 | 324.013 | 9% |
| Buah Naga Putih, segar | phosphorus_mg | 27 | 24.5 | 9% |
| Buah Naga Putih, segar | ash_g | 0.6 | 0.65 | 8% |
| Buah Naga Putih, segar | energy_kcal | 56 | 52.5 | 6% |
| Jagung muda / semi, segar (Baby corn, fresh) | energy_kcal | 35 | 37 | 5% |
| Madu (Honey) | water_g | 20 | 18.95 | 5% |
| Buah Naga Putih, segar | carbohydrate_g | 10.9 | 10.55 | 3% |
| Madu (Honey) | carbohydrate_g | 79.5 | 80.9567 | 2% |
| Jagung muda / semi, segar (Baby corn, fresh) | water_g | 89.5 | 91.05 | 2% |
| Minyak kelapa (Coconut oil) | fat_g | 98 | 99.63 | 2% |
| Jagung muda / semi, segar (Baby corn, fresh) | protein_g | 2.2 | 2.1667 | 2% |
| Buah Naga Merah, segar | water_g | 85.7 | 86.7667 | 1% |
| Buah Naga Putih, segar | water_g | 86.6 | 87.05 | 1% |
| Jagung muda / semi, segar (Baby corn, fresh) | fat_g | 0.1 | 0.1 | 0% |
| Madu (Honey) | fat_g | 0 | 0 |  |
