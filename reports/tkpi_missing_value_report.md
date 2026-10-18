# TKPI Missing Value Report

- Input rows: 1146
- Output rows: 1146
- Dropped rows: 0

## Missing Value per Nutrient

| Nutrient | Missing Count | Missing Percent |
|---|---:|---:|
| water_g | 2 | 0.17% |
| energy_kcal | 0 | 0.00% |
| protein_g | 1 | 0.09% |
| fat_g | 1 | 0.09% |
| carbohydrate_g | 0 | 0.00% |
| fiber_g | 221 | 19.28% |
| ash_g | 0 | 0.00% |
| calcium_mg | 40 | 3.49% |
| phosphorus_mg | 40 | 3.49% |
| iron_mg | 43 | 3.75% |
| sodium_mg | 283 | 24.69% |
| potassium_mg | 324 | 28.27% |
| copper_mg | 353 | 30.80% |
| zinc_mg | 348 | 30.37% |
| retinol_mcg | 605 | 52.79% |
| beta_carotene_mcg | 467 | 40.75% |
| carotene_total_mcg | 539 | 47.03% |
| vitamin_a_mcg | 1146 | 100.00% |
| vitamin_b1_mg | 88 | 7.68% |
| vitamin_b2_mg | 350 | 30.54% |
| niacin_mg | 339 | 29.58% |
| vitamin_c_mg | 289 | 25.22% |

## Nilai sumber yang dikosongkan

Kolom berikut dianggap tidak terukur karena nilai sumbernya tidak andal (lihat UNRELIABLE_SOURCE_FIELDS dan UNRELIABLE_SOURCE_CELLS di scripts/clean_common.py).

- sodium_mg: 1 nilai dikosongkan
- potassium_mg: 1 nilai dikosongkan
- copper_mg: 2 nilai dikosongkan
- zinc_mg: 1 nilai dikosongkan

## Koreksi kesalahan satuan (ug tercatat sebagai mg)

Nilai di atas ambang dibagi 1000 (lihat UNIT_ERROR_CORRECTIONS di scripts/clean_common.py). Nilai asli tetap tercatat di kolom notes.

| food_id | Pangan | Kolom | Nilai asli | Setelah koreksi |
|---|---|---|---:|---:|
| tkpi_0275 | Kacang tanah sangan tanpa selaput (Groundnut, baked without husk) | copper_mg | 520.4 | 0.5204 |
| tkpi_0382 | Tepung kacang kedelai | copper_mg | 4303.45 | 4.30345 |
| tkpi_0535 | Tekokak, kering (Devil�s fig, dried) | copper_mg | 1044.2 | 1.0442 |
| tkpi_0567 | Terung panjang, kukus | copper_mg | 67.1 | 0.0671 |
| tkpi_0612 | Apel malang, segar (Apel, green, fresh) | copper_mg | 110.16 | 0.11016 |
| tkpi_0613 | Apel, segar | copper_mg | 124.2 | 0.1242 |
| tkpi_0614 | Arbai, segar (Arbein, fresh) | copper_mg | 63.52 | 0.06352 |
| tkpi_0624 | Buah nona, segar (Sugarapple, fresh) | copper_mg | 325.7 | 0.3257 |
| tkpi_0633 | Duwet, segar (Jambolan, fresh) | copper_mg | 191.28 | 0.19128 |
| tkpi_0644 | Jeruk bali, segar (Pummelo, fresh) | copper_mg | 171.25 | 0.17125 |
| tkpi_0646 | Jeruk garut-keprok (Mandarin) | copper_mg | 169.3 | 0.1693 |
| tkpi_0648 | Jeruk manis, segar (orange, fresh) | copper_mg | 160 | 0.16 |
| tkpi_0650 | Jeruk ragi, segar | copper_mg | 155 | 0.155 |
| tkpi_0651 | Kawista, segar (Wood apple, fresh) | copper_mg | 308.43 | 0.30843 |
| tkpi_0680 | Nangka masak pohon, segar (Jack fruit, fresh) | copper_mg | 246.58 | 0.24658 |
| tkpi_0696 | Pisang mas, segar (Banana, mas, fresh) | copper_mg | 195.78 | 0.19578 |
| tkpi_0927 | Ikan teri, segar (Anchovies, fresh) | copper_mg | 305.2 | 0.3052 |

## Perlu ditinjau manual (tidak dibagi 1000)

- tkpi_0073 Jagung titi: copper_mg = 9
- tkpi_0975 Ikan sale lais, mentah (Sheatfish): copper_mg = 17.6