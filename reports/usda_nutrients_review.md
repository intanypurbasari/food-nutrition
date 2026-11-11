# USDA-only Nutrients Review

Nilai magnesium, gula total, lemak jenuh, kolesterol, vitamin B6 dan B12 untuk TKPI dan MyFCD.

## Sumber nilai

| Nutrisi | Sumber | TKPI | MyFCD |
|---|---|---|---|
| cholesterol_mg | USDA_direct_high | 18 | 17 |
| cholesterol_mg | USDA_direct_medium | 118 | 31 |
| cholesterol_mg | USDA_model | 1010 | 186 |
| magnesium_mg | USDA_direct_high | 18 | 17 |
| magnesium_mg | USDA_direct_medium | 117 | 30 |
| magnesium_mg | USDA_model | 1011 | 187 |
| saturated_fat_g | USDA_direct_high | 14 | 17 |
| saturated_fat_g | USDA_direct_medium | 113 | 32 |
| saturated_fat_g | USDA_model | 1019 | 185 |
| sugars_total_g | USDA_direct_high | 7 | 15 |
| sugars_total_g | USDA_direct_medium | 92 | 29 |
| sugars_total_g | USDA_model | 1047 | 190 |
| vitamin_b12_mcg | USDA_direct_high | 18 | 17 |
| vitamin_b12_mcg | USDA_direct_medium | 116 | 30 |
| vitamin_b12_mcg | USDA_model | 1012 | 187 |
| vitamin_b6_mg | USDA_direct_high | 17 | 17 |
| vitamin_b6_mg | USDA_direct_medium | 113 | 30 |
| vitamin_b6_mg | USDA_model | 1016 | 187 |

## Akurasi model (5-fold CV pada USDA SR Legacy)

nRMSE = RMSE / sd nilai asli (1,0 setara menebak rerata). Akurasi ini berlaku untuk pangan USDA;
pada TKPI/MyFCD prediktornya berupa campuran nilai terukur dan hasil imputasi, sehingga galat sebenarnya bisa lebih besar.

| Nutrisi | n latih | R² | nRMSE | Spearman |
|---|---|---|---|---|
| magnesium_mg | 7421 | 0.817 | 0.428 | 0.916 |
| sugars_total_g | 6007 | 0.829 | 0.413 | 0.911 |
| saturated_fat_g | 7450 | 0.716 | 0.533 | 0.976 |
| cholesterol_mg | 7394 | 0.637 | 0.603 | 0.910 |
| vitamin_b6_mg | 7262 | 0.736 | 0.514 | 0.901 |
| vitamin_b12_mcg | 7113 | 0.682 | 0.564 | 0.891 |

## Penyetaraan kadar air nilai pinjaman (Pedoman TKPI, Kemenkes RI 2017)

Bila |air pangan - air USDA| / air USDA > 10%, nilai USDA dikali (100 - air pangan) / (100 - air USDA) (dasar berat kering); bila tidak, dipinjam langsung.

| Sumber | Pangan tertaut | Langsung | Berat kering | Tanpa data air | Median faktor (berat kering) | Rentang faktor |
|---|---|---|---|---|---|---|
| MyFCD | 49 | 12 | 37 | 0 | 0.98 | 0.07–3.40 |
| TKPI | 136 | 75 | 61 | 0 | 0.93 | 0.14–8.23 |

### Faktor ekstrem (< 0.5 atau > 2): tinjau tautannya

Faktor sebesar ini biasanya berarti bentuk pangan berbeda (segar vs kering, mentah vs matang) atau tautan yang keliru. Penyetaraan berat kering mengoreksi perbedaan bentuk, tetapi tidak memperbaiki tautan yang salah pangan.

- myfcd_0122 -> Beverages, chocolate powder, no sugar added (USDA 174824): faktor 0.07, selisih air 1166%
- tkpi_0620 -> Persimmons, japanese, dried (USDA 169942): faktor 0.14, selisih air 287%
- tkpi_0663 -> Mango, dried, sweetened (USDA 169091): faktor 0.16, selisih air 422%
- tkpi_1130 -> Spices, turmeric, ground (USDA 172231): faktor 0.17, selisih air 561%
- tkpi_0657 -> Persimmons, japanese, dried (USDA 169942): faktor 0.28, selisih air 240%
- tkpi_0283 -> Hyacinth beans, mature seeds, raw (USDA 175210): faktor 0.28, selisih air 692%
- tkpi_1116 -> Spices, garlic powder (USDA 171325): faktor 0.31, selisih air 1001%
- tkpi_0423 -> Garlic, raw (USDA 169230): faktor 0.37, selisih air 45%
- tkpi_0127 -> Spaghetti, spinach, dry (USDA 168911): faktor 0.37, selisih air 693%
- tkpi_0900 -> Fish, mackerel, salted (USDA 168149): faktor 0.39, selisih air 80%
- myfcd_0104 -> Fish oil, cod liver (USDA 173577): faktor 0.39, selisih air inf%
- tkpi_1044 -> Egg, duck, whole, fresh, raw (USDA 172189): faktor 0.41, selisih air 24%
- tkpi_0486 -> Winged bean leaves, raw (USDA 170478): faktor 0.41, selisih air 18%
- myfcd_0097 -> Cheese, cream, low fat (USDA 169079): faktor 0.42, selisih air 29%
- tkpi_0894 -> Fish, mackerel, salted (USDA 168149): faktor 0.42, selisih air 77%
- tkpi_0434 -> Taro, raw (USDA 169308): faktor 0.44, selisih air 23%
- myfcd_0019 -> Crackers, multigrain (USDA 171838): faktor 0.44, selisih air 2181%
- myfcd_0125 -> Beverages, coffee, instant, decaffeinated, powder (USDA 174133): faktor 0.44, selisih air 1682%
- myfcd_0128 -> Beverages, tea, instant, unsweetened, powder (USDA 173230): faktor 0.45, selisih air 1020%
- myfcd_0176 -> Puff pastry, frozen, ready-to-bake (USDA 172790): faktor 0.47, selisih air 571%
- tkpi_0140 -> Yam, raw (USDA 170071): faktor 0.49, selisih air 22%
- tkpi_1126 -> Spices, ginger, ground (USDA 170926): faktor 0.50, selisih air 453%
- myfcd_0099 -> Yogurt, vanilla, low fat. (USDA 170888): faktor 2.05, selisih air 28%
- tkpi_0494 -> Hyacinth-beans, immature seeds, raw (USDA 169234): faktor 2.12, selisih air 15%
- tkpi_0727 -> Durian, raw or frozen (USDA 168192): faktor 2.14, selisih air 61%
- tkpi_0157 -> Cassava, raw (USDA 169985): faktor 2.18, selisih air 80%
- tkpi_0985 -> Fish, anchovy, european, raw (USDA 174182): faktor 2.34, selisih air 48%
- myfcd_0228 -> Spinach, raw (USDA 168462): faktor 2.44, selisih air 14%
- tkpi_0957 -> Fish, shark, mixed species, raw (USDA 173697): faktor 2.91, selisih air 69%
- tkpi_0158 -> Taro, raw (USDA 169308): faktor 2.93, selisih air 80%
- tkpi_0021 -> Millet, cooked (USDA 168871): faktor 3.09, selisih air 84%
- myfcd_0131 -> Beverages, Orange juice drink (USDA 169044): faktor 3.11, selisih air 34%
- myfcd_0225 -> Cabbage, raw (USDA 169975): faktor 3.40, selisih air 20%
- tkpi_0008 -> Rice, white, glutinous, unenriched, cooked (USDA 169711): faktor 3.73, selisih air 83%
- tkpi_0232 -> Arrowroot, raw (USDA 168490): faktor 4.49, selisih air 83%
- tkpi_1135 -> Fish broth (USDA 171606): faktor 8.23, selisih air 30%
