# Nutrition Repository

**Knowledge Repository Nutrisi dan Kesehatan Mental Berbasis Digital untuk Mendukung Sistem Rekomendasi Gizi Personal.**

Sub-riset dari program penelitian **Jatim Melaju 2026** (kolaborasi UNAIR, ITS, dan UPNVJT). Mitra UPNVJT (Prodi Informatika) bertanggung jawab atas harmonisasi, integrasi, dan imputasi data komposisi pangan lintas basis data: fondasi bagi knowledge repository dan sistem rekomendasi gizi pada riset utama.

Status proyek: **Tahap 1 sampai 3 selesai, Tahap 4 belum dimulai.**

## Mengapa Proyek Ini Penting

Bidang *nutritional psychiatry* menunjukkan bahwa kecukupan nutrisi tertentu, seperti vitamin B kompleks, magnesium, zinc, dan omega-3, berperan dalam regulasi neurotransmiter yang memengaruhi stres, depresi, dan fungsi kognitif. Untuk membangun sistem rekomendasi gizi personal yang mempertimbangkan kesehatan mental, dibutuhkan basis data komposisi pangan yang lengkap, konsisten, dan siap komputasi.

Masalahnya: TKPI dan MyFCD tidak memakai kunci pengenal yang sama, taksonomi kategorinya berbeda, dan masing-masing punya pola data hilang yang berbeda pula (TKPI kehilangan mikronutrien secara terlokalisasi, MyFCD kehilangan seluruh panel proksimat pada sebagian baris). Repositori ini membangun alur kerja yang *reproducible* dan *auditable* untuk menautkan, mendiagnosis, dan mengisi kekosongan tersebut, tanpa pernah mengarang nilai yang tidak bisa dipertanggungjawabkan.

## Daftar Isi

- [Sekilas Angka](#sekilas-angka)
- [Status per Tahap](#status-per-tahap)
- [Contoh Data](#contoh-data)
- [Struktur Folder](#struktur-folder)
- [Setup](#setup)
- [Cara Menjalankan](#cara-menjalankan)
- [Metodologi Sub-Riset](#metodologi-sub-riset-harmonisasi--integrasi)
- [Tahap 1: Resolusi Entitas](#tahap-1-resolusi-entitas)
- [Tahap 2: Diagnosis Mekanisme Missing Data](#tahap-2-diagnosis-mekanisme-missing-data)
- [Tahap 3: Imputasi Berbasis Machine Learning](#tahap-3-imputasi-berbasis-machine-learning)
- [Tahap 4: Kuantifikasi Ketidakpastian dan Evaluasi](#tahap-4-kuantifikasi-ketidakpastian-dan-evaluasi-belum-dimulai)
- [Insight dan Temuan Kunci](#insight-dan-temuan-kunci)
- [Reproducibility dan Pengujian](#reproducibility-dan-pengujian)
- [Tim dan Kontributor](#tim-dan-kontributor)
- [Rencana Lanjutan](#rencana-lanjutan)
- [Sumber Data](#sumber-data)
- [Etika Scraping](#etika-scraping)
- [Catatan Lisensi Data](#catatan-lisensi-data)
- [Sitasi](#sitasi)

## Sekilas Angka

| Metrik | Nilai |
|---|---|
| Item pangan TKPI | 1.146 |
| Item pangan MyFCD | 234 |
| Item pangan USDA SR Legacy (rujukan) | 7.793 |
| Pasangan tautan TKPI ke MyFCD (TF-IDF cosine) | 156 (52 mutual-best) |
| Baris pada dataset terintegrasi final | 1.380 |
| Sel nutrisi berhasil diimputasi (dari 22 nutrisi yang dirutekan) | 95,5% |
| Metode imputasi diimplementasikan | 6 (mean, median, KNN, MICE, MissForest, cross-database transfer) |
| Unit test | 23, seluruhnya hijau |
| Baris ekspor siap-evaluasi (format long) | 187.308 |

## Status per Tahap

| Tahap | Deskripsi | Penanggung Jawab | Status | Output Utama |
|---|---|---|---|---|
| 1 | Resolusi Entitas (TKPI, MyFCD, USDA) | Joyce | Selesai | `tkpi_enriched.csv`, `myfcd_enriched.csv`, tabel linkage |
| 2 | Diagnosis Mekanisme Missing Data | Intan | Selesai | `availability_matrix.csv`, laporan korelasi missingness |
| 3 | Imputasi Berbasis Machine Learning | Tim (lihat `docs/stage3_imputation.md`) | Selesai | `nutrition_repository_imputed.csv`, `nutrition_repository_imputed_long.csv` |
| 4 | Kuantifikasi Ketidakpastian dan Evaluasi (bootstrap, RMSE hold-out) | Fetty | Belum dimulai | (menunggu) |

## Contoh Data

Cuplikan `data_processed/nutrition_repository_imputed.csv` setelah Tahap 3. Baris MyFCD di bawah menunjukkan `carotene_total_mcg` yang sebelumnya 100% kosong di MyFCD, kini terisi lewat cross-database transfer dari TKPI; `vitamin_a_mcg` sengaja dibiarkan kosong karena belum punya jalur data yang sah (lihat [Insight dan Temuan Kunci](#insight-dan-temuan-kunci)).

| food_id | nama pangan | sumber | energi (kkal) | protein (g) | zat besi (mg) | karoten total (mcg) | vitamin A (mcg) |
|---|---|---|---|---|---|---|---|
| tkpi_0001 | Beras giling, mentah | TKPI | 357,0 | 8,4 | 1,8 | 0,0 | *(kosong, unresolved)* |
| tkpi_0003 | Beras giling var rojolele, mentah | TKPI | 357,0 | 8,4 | 1,8 | 80,0 | *(kosong, unresolved)* |
| myfcd_0001 | Biscuit, Coconut | MyFCD | 450,4 | 8,3 | 1,47 | 16,9 (hasil cross-DB transfer) | *(kosong, unresolved)* |
| myfcd_0002 | Biscuit, Lemon Puff | MyFCD | 454,7 | 7,9 | 1,49 | 28,1 (hasil cross-DB transfer) | *(kosong, unresolved)* |

## Struktur Folder

```text
config/          Konfigurasi scraper (settings.py) dan Tahap 3 (imputation_settings.py)
data_raw/        Hasil scraping mentah
data_clean/      Dataset per sumber setelah normalisasi
data_processed/  Repository gabungan, linkage table, hasil imputasi, export JSON
docs/            Dokumentasi proyek, laporan naratif, metodologi, dan gambar
reports/         Laporan terstruktur hasil pipeline (kualitas, missingness, imputasi)
scripts/         Entry point CLI untuk setiap tahap
src/
  cleaning/      Normalisasi dan pembersihan data
  schema/        Skema unifikasi (Pydantic) dan daftar nutrisi kanonik
  scrapers/      Scraper TKPI dan MyFCD (etis: delay, limit, cache)
  validation/    Quality checks (required field, tipe numerik, range, konsistensi)
  imputation/    Modul Tahap 3: baseline, MissForest, cross-DB transfer, integrasi
tests/           Unit test (pytest) dan fixture kecil untuk setiap modul
app/             Prototipe Streamlit (di luar cakupan Tahap 1 sampai 4)
usda-csv/        Tabel referensi USDA FoodData Central
```

## Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cara Menjalankan

### Pipeline lengkap, semua tahap sekali jalan

```bash
python scripts/source_recon.py
python scripts/run_pipeline.py --limit 20 --include-imputation
```

Jika data raw sudah tersedia dan scraping ingin dilewati (paling umum dipakai untuk pengembangan lokal):

```bash
python scripts/run_pipeline.py --skip-scrape --include-imputation
```

Tanpa flag `--include-imputation`, pipeline berhenti setelah tahap export repository, yaitu perilaku asli sebelum Tahap 3 ada. Ini sengaja dijaga agar tidak berubah demi kompatibilitas mundur.

### Menjalankan tahap secara manual

Tahap 1, dari scrape sampai export:

```bash
python scripts/scrape_tkpi.py --limit 20
python scripts/scrape_myfcd.py --limit 20
python scripts/clean_tkpi.py
python scripts/clean_myfcd.py
python scripts/validate_dataset.py
python scripts/build_repository_sample.py
python scripts/export_repository_json.py
```

Tahap 1 lanjutan (resolusi entitas) dan Tahap 2 (diagnosis missingness) saat ini hanya tersedia sebagai notebook: `scripts/entity_resolution_threeway.ipynb` dan `scripts/Analisis Pola Missingness.ipynb`.

Tahap 3, imputasi. Urutan berikut wajib diikuti karena tiap script bergantung pada output script sebelumnya:

```bash
python scripts/run_baseline_imputation.py       # mean, median, KNN, MICE
python scripts/run_missforest_imputation.py     # MissForest dalam-basis-data + cross-DB transfer
python scripts/run_integration.py               # dataset terintegrasi final
python scripts/export_evaluation_ready.py       # ekspor long-format untuk Tahap 4
```

Detail metodologi, keputusan teknis, dan daftar lengkap output Tahap 3 ada di [`docs/stage3_imputation.md`](docs/stage3_imputation.md).

### Menjalankan test

```bash
pytest -q
```

23 test mencakup normalizer, skema, dan quality checks dari Tahap 1, serta I/O, baseline, MissForest, dan integrasi dari Tahap 3. Semuanya harus hijau sebelum perubahan apa pun di-commit.

### Menjalankan prototipe

```bash
streamlit run app/prototype.py
```

Jika file repository belum tersedia, jalankan tahap cleaning, merge, dan export lebih dulu.

## Metodologi Sub-Riset (Harmonisasi & Integrasi)

```text
TKPI + MyFCD + USDA SR Legacy (data sumber)
        |
        v
Tahap 1  Resolusi Entitas        crosswalk kategori -> normalisasi nama -> TF-IDF cosine -> label keyakinan
        |
        v
Tahap 2  Diagnosis Missing Data  uji Little's MCAR per basis data + korelasi ko-okurensi kehilangan
        |
        v
Tahap 3  Imputasi ML             baseline (mean/median/KNN/MICE) + MissForest + cross-database transfer + value borrowing USDA
        |
        v
Tahap 4  Kuantifikasi Ketidakpastian   bootstrap (B=50) + evaluasi hold-out RMSE/nRMSE   [belum dimulai]
        |
        v
Dataset Komposisi Pangan Terintegrasi & Diperkaya
```

1. **Resolusi Entitas (Entity Resolution).** Penautan antar-item pangan lintas basis data menggunakan record linkage berbasis kemiripan teks: crosswalk kategori, normalisasi nama, pencocokan TF-IDF cosine, dan pelabelan tingkat keyakinan (HIGH, MEDIUM, LOW).
2. **Diagnosis Mekanisme Missing Data.** Uji Little's MCAR per basis data dilengkapi analisis pola ko-okurensi kehilangan. Temuan: TKPI bersifat **MAR** (kehilangan terlokalisasi pada mineral), MyFCD bersifat **MNAR / struktural** (kehilangan menyeluruh pada panel proksimat).
3. **Imputasi Berbasis Machine Learning.** MissForest dengan pendekatan **cross-database transfer** (imputer dilatih pada TKPI, diterapkan pada MyFCD), serta value borrowing dari USDA untuk nutrisi yang kosong di kedua basis regional.
4. **Kuantifikasi Ketidakpastian.** Interval kepercayaan bootstrap (B = 50) dengan penandaan nutrisi berketidakpastian tinggi. Belum dimulai, lihat [Tahap 4](#tahap-4-kuantifikasi-ketidakpastian-dan-evaluasi-belum-dimulai).

Integrasi data dilakukan pada tahap akhir, setelah imputasi, agar skema cross-database transfer dapat diterapkan.

## Tahap 1: Resolusi Entitas

Tidak adanya kunci pengenal yang sama antar basis data membuat penautan dilakukan lewat kemiripan teks (TF-IDF cosine), dibatasi per kategori pangan lewat crosswalk manual agar kompleksitas komputasi turun dan presisi naik.

Output (`data_processed/`):

- `tkpi_usda_links.csv`, `myfcd_usda_links.csv`: tabel penautan masing-masing basis regional ke USDA.
- `tkpi_myfcd_links.csv`: tabel penautan langsung TKPI ke MyFCD (kolom `tkpi_food_id`, `myfcd_food_id`, `similarity_score`). Berisi 156 pasangan hasil pencocokan TF-IDF cosine.
- `tkpi_myfcd_links_mutual.csv`: subset tautan satu-ke-satu (mutual-best), 52 pasangan berpresisi tinggi untuk pelaporan konservatif.
- `tkpi_only_nonmatch.csv`, `myfcd_only_nonmatch.csv`: pangan unik per basis data (990 TKPI, 179 MyFCD) yang tidak memiliki padanan.
- `tkpi_enriched.csv`, `myfcd_enriched.csv`: TKPI/MyFCD yang diperkaya dengan 6 kolom nutrisi pinjaman dari USDA (`magnesium_mg`, `sugars_total_g`, `saturated_fat_g`, `cholesterol_mg`, `vitamin_b6_mg`, `vitamin_b12_mcg`), masing-masing dengan kolom `_source`/`_confidence`. **Ini input utama Tahap 3.**

Kode: `scripts/entity_resolution_threeway.ipynb`, sebuah TF-IDF cosine matcher murni-numpy tanpa dependensi sklearn.

## Tahap 2: Diagnosis Mekanisme Missing Data

Output (`data_processed/`, `reports/`):

- **`availability_matrix.csv`**: tabel perutean strategi imputasi per nutrisi (kolom `strategi_imputasi`), bernilai `"Imputasi internal per basis"`, `"Cross-DB transfer / USDA"`, atau `"Pinjam USDA (kosong di kedua basis)"`. **Ini rujukan tunggal yang dipakai Tahap 3; strategi tidak pernah diturunkan ulang oleh kode Tahap 3.**
- `missing_corr_TKPI.csv`, `missing_corr_MyFCD.csv`: matriks korelasi antar indikator kehilangan (koefisien phi).
- `ringkasan_r_perbandingan.csv`: ringkasan nilai korelasi per kelompok nutrisi (makronutrien, mineral, vitamin).
- `tkpi_missing_value_report.md`, `myfcd_missing_value_report.md`: persentase missing per nutrisi (TKPI 1.146 baris, MyFCD 234 baris).

Kode: `scripts/Analisis Pola Missingness.ipynb`.

## Tahap 3: Imputasi Berbasis Machine Learning

Mengimplementasikan strategi imputasi per nutrisi sesuai routing `availability_matrix.csv` dari Tahap 2, dalam paket baru `src/imputation/`.

| Metode | Modul | Cakupan |
|---|---|---|
| Mean, median (baseline) | `src/imputation/baselines.py` | 20 nutrisi berstrategi "imputasi internal", per basis data |
| KNN, k=5 (baseline) | `src/imputation/baselines.py` | idem |
| MICE, `IterativeImputer` (baseline) | `src/imputation/baselines.py` | idem, seed 42 untuk reproducibility |
| **MissForest dalam-basis-data** | `src/imputation/missforest_imputer.py` | idem, metode utama, bukan baseline |
| **Cross-database transfer, TKPI ke MyFCD** | `src/imputation/cross_transfer.py` | `carotene_total_mcg`, 53% terisi di TKPI, 0% di MyFCD. **Kebaruan metodologis utama.** |
| Value borrowing USDA (pass-through) | `src/imputation/integrate.py` | 6 kolom yang sudah dipinjam Tahap 1 |

**Catatan teknis.** `missingpy`, implementasi MissForest yang umum dirujuk di literatur, sudah tidak kompatibel dengan scikit-learn versi terkini (mengimpor modul privat yang sudah dihapus, tidak dipelihara sejak 2018). Sebagai gantinya dipakai `sklearn.impute.IterativeImputer(estimator=RandomForestRegressor)`, yang setara secara algoritmik dengan MissForest.

Output (`data_processed/`, `reports/`):

- `tkpi_imputed_baseline_{mean,median,knn,mice}.csv`, `myfcd_imputed_baseline_{mean,median,knn,mice}.csv`: hasil tiap baseline, per basis data.
- `tkpi_imputed_missforest.csv`, `myfcd_imputed_missforest.csv`: hasil MissForest dalam-basis-data.
- `myfcd_imputed_crossdb.csv`: hasil cross-database transfer.
- **`nutrition_repository_imputed.csv`**: dataset terintegrasi final, 1.380 baris (1.146 TKPI + 234 MyFCD), nilai terbaik per nutrisi per pangan sesuai strategi Tahap 2.
- **`nutrition_repository_imputed_long.csv`**: format long (187.308 baris, kolom `food_id, source_db, nutrient, method, value`) untuk kebutuhan Tahap 4.
- `reports/imputation_summary.md`: akuntansi penuh, berapa sel terselesaikan per strategi dan berapa yang masih *unresolved*.
- `reports/imputation_method_comparison.csv`: statistik deskriptif (count, mean, std) per nutrisi kali metode. **Bukan metrik akurasi**; perbandingan terhadap ground truth adalah tanggung jawab Tahap 4.

Dokumentasi metodologi lengkap ada di [`docs/stage3_imputation.md`](docs/stage3_imputation.md). Laporan kemajuan bergaya akademik, siap tempel ke laporan resmi Jatim Melaju, ada di [`docs/laporan_kemajuan_tahap3.md`](docs/laporan_kemajuan_tahap3.md).

## Tahap 4: Kuantifikasi Ketidakpastian dan Evaluasi (belum dimulai)

Sesuai rencana pada metodologi riset: interval kepercayaan bootstrap (B=50) per sel imputasi, serta evaluasi hold-out (15% data TKPI disembunyikan, dihitung RMSE/nRMSE per nutrisi, dibandingkan antar metode dari Tahap 3). `nutrition_repository_imputed_long.csv` dan `imputation_method_comparison.csv` dari Tahap 3 sudah disiapkan sebagai input langsung untuk tahap ini, tetapi perhitungan akurasi dan ketidakpastiannya sendiri belum diimplementasikan.

## Insight dan Temuan Kunci

- **Tidak ada irisan nama pangan yang identik** antar basis data, sehingga penautan memerlukan pendekatan kemiripan teks, bukan join berbasis kunci.
- **Mekanisme kehilangan berbeda antar basis data.** TKPI bersifat MAR dengan korelasi blok mineral hingga 0,96; MyFCD bersifat MNAR/struktural dengan korelasi panel proksimat rerata 0,862. Strategi imputasi seragam untuk kedua basis data berpotensi bias, sehingga memang tidak diterapkan.
- **Ketersediaan nutrisi berbeda per basis data.** `carotene_total_mcg` terisi 53% di TKPI namun 0% di MyFCD, menjadikannya kandidat utama cross-database transfer; `vitamin_a_mcg` kosong 100% di keduanya, menjadikannya kandidat peminjaman USDA.
- **Hasil cross-database transfer terukur.** Setelah Tahap 3, `carotene_total_mcg` di MyFCD terisi 100%, sebelumnya 0%, dengan rata-rata 112,35 mcg. Nilai ini murni hasil relasi antar-nutrisi yang dipelajari dari TKPI, diterapkan pada nilai nutrisi lain milik MyFCD sendiri.
- **95,5% sel data berhasil diselesaikan** dari 22 nutrisi yang dirutekan Tahap 2, yaitu 28.980 dari 30.360 sel. Sisanya seluruhnya berasal dari satu gap yang teridentifikasi, bukan tersebar acak.
- **Gap yang jujur, bukan ditutup-tutupi.** `vitamin_a_mcg` diberi strategi "pinjam USDA" oleh Tahap 2, tetapi Tahap 1 belum benar-benar meminjam kolom tersebut dari USDA. Tahap 3 melaporkan ini eksplisit sebagai *unresolved* di `reports/imputation_summary.md`, bukan mengisinya dengan tebakan. Ini jadi rekomendasi konkret untuk Tahap 1 selanjutnya.
- **Reproducibility terverifikasi.** Seluruh metode stokastik (MICE, MissForest, cross-database transfer) memakai `RANDOM_SEED = 42` yang tetap; dua kali proses ulang menghasilkan keluaran identik hingga level byte.

## Reproducibility dan Pengujian

- `config/imputation_settings.py`: `RANDOM_SEED = 42` dipakai konsisten di seluruh metode stokastik Tahap 3.
- 23 unit test (pytest) mencakup Tahap 1 (normalizer, skema, quality checks) dan Tahap 3 (I/O, baseline, MissForest, cross-database transfer, integrasi), memakai fixture kecil di `tests/fixtures/` yang meniru skema data asli tanpa memuat data produksi.
- Semua path bersifat relatif terhadap root repository (`ROOT = Path(__file__).resolve().parents[1]`); tidak ada absolute path yang di-hardcode di mana pun dalam kode Tahap 3.

## Tim dan Kontributor

Riset utama Jatim Melaju 2026 dipimpin oleh Peneliti Utama dari UNAIR (Dr. Riris Diana Rachmayanti, Dr. Triska Susila Nindya), dengan Peneliti Mitra dari ITS (Retno Aulia Vinarti, Ahmad Muklason) dan UPNVJT (Dr. Intan Yuniar Purbasari, Fetty Tri Anggraeny).

Sub-riset harmonisasi dan integrasi data pada repositori ini dikerjakan oleh tim UPNVJT:

| Tahap | Kontributor |
|---|---|
| Tahap 1, Resolusi Entitas | Joyce |
| Tahap 2, Diagnosis Missing Data | Intan |
| Tahap 3, Imputasi Machine Learning | Galih, dengan supervisi Dr. Intan Yuniar Purbasari |
| Tahap 4, Evaluasi | Fetty |

## Rencana Lanjutan

1. Menambahkan `vitamin_a_mcg` ke daftar kolom peminjaman nilai USDA pada Tahap 1.
2. Menuntaskan uji Little's MCAR formal untuk MyFCD pada Tahap 2.
3. Membangun Tahap 4: kuantifikasi ketidakpastian (bootstrap B=50) dan evaluasi hold-out (RMSE/nRMSE) di atas output yang sudah disiapkan Tahap 3.
4. Menghubungkan knowledge repository ini ke digitalisasi Angka Kecukupan Gizi (AKG) dan pemodelan profil pengguna, sesuai roadmap riset utama Jatim Melaju.

## Sumber Data

- **TKPI**, Tabel Komposisi Pangan Indonesia: <https://www.panganku.org/>
- **MyFCD**, Malaysian Food Composition Database: <https://myfcd.moh.gov.my/>
- **USDA SR Legacy**, USDA FoodData Central: <https://fdc.nal.usda.gov/download-datasets>

## Etika Scraping

Semua scraper wajib memakai delay, limit kecil, user-agent wajar, cache lokal, dan tidak melakukan bypass captcha, login wall, rate limit, atau proteksi situs.

## Catatan Lisensi Data

Dataset `*_clean.csv` merupakan data turunan dari TKPI dan MyFCD. Sebelum meredistribusi nilai nutrisi mentah secara terbuka, pastikan hak penggunaan/lisensi data sumber memperbolehkannya. Untuk dataset final berukuran besar, disarankan menggunakan repositori berarsip permanen, misalnya Zenodo atau GigaDB, yang menyediakan DOI untuk sitasi.

## Sitasi

Luaran publikasi yang ditargetkan dari sub-riset ini:

> *Cross-Database Transfer Imputation for Southeast Asian Food Composition Harmonisation: Integrating TKPI, MyFCD, and USDA with Uncertainty Quantification*, ditargetkan ke jurnal **GigaByte** (Scopus Q2).

Detail lengkap ada di laporan kemajuan resmi Jatim Melaju 2026.
