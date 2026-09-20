<!--
CATATAN PENGGUNAAN (hapus blok ini sebelum ditempel ke Word):
Bagian di bawah ini ditulis mengikuti gaya dan struktur dokumen "LAPORAN KEMAJUAN JATIM MELAJU 2026"
(BAB 2 METODOLOGI dan BAB 3 HASIL DAN LUARAN YANG DICAPAI), khusus memuat progres Tahap 3
(Imputasi Data Berbasis Machine Learning) yang sudah dikerjakan. Tempel sebagai kelanjutan sub-bab
3.5 dan 3.6 pada BAB 3, dan gabungkan draft BAB 4 di bagian bawah ke laporan utama. Setelah ditempel
ke Word, sesuaikan ke format resmi: Times New Roman 12, spasi 1,5, kertas A4, margin kiri 4 cm/
kanan 3 cm/atas 3 cm/bawah 3 cm.

Semua angka pada tabel diambil langsung dari output pipeline yang sudah dijalankan
(reports/imputation_summary.md, reports/imputation_method_comparison.csv, data_processed/
nutrition_repository_imputed.csv) per 3 Agustus 2026 — bukan estimasi. Bagian bertanda [GAMBAR ...]
adalah placeholder yang perlu diisi dengan tangkapan layar/chart, karena laporan ini berupa teks.
-->

## 3.5. Hasil Tahap 3: Imputasi Data Berbasis Machine Learning

### 3.5.1. Ikhtisar Implementasi

Tahap 3 mengimplementasikan kerangka imputasi yang dirancang pada metodologi Bab 2.5, dengan strategi per nutrisi yang mengikuti hasil diagnosis Tahap 2 (`availability_matrix.csv`) sebagai rujukan tunggal, bukan diturunkan ulang secara ad-hoc. Implementasi dilakukan secara bertahap dalam 11 milestone tersepisah, masing-masing diverifikasi (unit test, validasi kelengkapan data, dan pengecekan reproducibility) sebelum dilanjutkan ke milestone berikutnya. Ringkasan milestone disajikan pada Tabel 3.3.

**Tabel 3.3.** Ringkasan milestone implementasi Tahap 3

| No | Milestone | Keluaran Utama |
|---|---|---|
| 1 | Konfigurasi & dependensi | `config/imputation_settings.py`, `requirements.txt` (scikit-learn, scipy) |
| 2 | Modul I/O & perutean strategi | `src/imputation/io_utils.py` — pembaca `availability_matrix.csv` |
| 3 | Baseline Mean & Median | `*_imputed_baseline_mean.csv`, `*_imputed_baseline_median.csv` |
| 4 | Baseline KNN | `*_imputed_baseline_knn.csv` |
| 5 | Baseline MICE | `*_imputed_baseline_mice.csv` |
| 6 | MissForest dalam-basis-data | `tkpi_imputed_missforest.csv`, `myfcd_imputed_missforest.csv` |
| 7 | MissForest cross-database transfer | `myfcd_imputed_crossdb.csv` |
| 8 | Integrasi dataset final | `nutrition_repository_imputed.csv`, `reports/imputation_summary.md` |
| 9 | Ekspor format long untuk evaluasi | `nutrition_repository_imputed_long.csv`, `reports/imputation_method_comparison.csv` |
| 10 | Unit test menyeluruh | 17 test baru (23 test total, seluruhnya lulus) |
| 11 | Dokumentasi & integrasi pipeline | `docs/stage3_imputation.md`, flag `--include-imputation` pada `run_pipeline.py` |

Seluruh kode berada pada paket baru `src/imputation/` dan dapat dijalankan ulang secara end-to-end melalui:

```bash
python scripts/run_pipeline.py --skip-scrape --include-imputation
```

tanpa mengubah perilaku pipeline lama (scraping–cleaning–validasi–merge) yang sudah berjalan sejak Tahap 1.

### 3.5.2. Catatan Keputusan Teknis: Pemilihan Implementasi MissForest

Paket Python `missingpy` (implementasi MissForest yang umum dirujuk di literatur) diuji-instal pada lingkungan riset dan terbukti **tidak lagi kompatibel** dengan versi scikit-learn terkini — modul yang diimpornya (`sklearn.neighbors.base`) sudah dihapus dari scikit-learn sejak beberapa rilis lalu dan paket tersebut tidak lagi dipelihara (rilis terakhir 2018). Sebagai gantinya, digunakan `sklearn.impute.IterativeImputer` dengan `estimator=RandomForestRegressor`, yang secara algoritmik ekuivalen dengan MissForest (imputasi iteratif berbasis Random Forest per-fitur) namun didukung penuh oleh scikit-learn versi aktif. Keputusan ini didokumentasikan pada commit `060f721` agar dapat ditelusuri.

### 3.5.3. Hasil Perutean Strategi Imputasi per Kelompok Nutrisi

Seluruh 22 kolom nutrisi pada skema unifikasi memiliki strategi imputasi yang ditetapkan Tahap 2 pada `availability_matrix.csv`. (Skema sebelumnya memuat kolom ke-23, `edible_portion_percent`, yang tidak pernah masuk cakupan diagnosis Tahap 2 dan tidak pernah terisi sejak tahap scraping; kolom ini sudah dihapus sepenuhnya dari skema per keputusan tim, bukan lagi dilewatkan sebagai kolom kosong.) Distribusi strategi per kelompok nutrisi disajikan pada Tabel 3.4.

**Tabel 3.4.** Distribusi strategi imputasi per kelompok nutrisi

| Kelompok Nutrisi | Jumlah Nutrisi | Imputasi Internal (MissForest) | Cross-DB Transfer | Pinjam USDA |
|---|---|---|---|---|
| Makronutrien/Proksimat | 7 | 7 | 0 | 0 |
| Mineral | 7 | 7 | 0 | 0 |
| Vitamin | 8 | 6 | 1 (`carotene_total_mcg`) | 1 (`vitamin_a_mcg`) |
| **Total** | **22** | **20** | **1** | **1** |

[GAMBAR 3.5.a — Diagram alur Tahap 3 tiga-strategi (imputasi internal / cross-DB transfer / pinjam USDA) yang telah didiskusikan dan disetujui tim, dilampirkan sebagai gambar terpisah pada laporan ini.]

### 3.5.4. Hasil Baseline Pembanding

Empat metode baseline diimplementasikan sesuai kebutuhan evaluasi pada Bab 2.7: mean, median, KNN (`k=5`), dan MICE (`IterativeImputer`, `max_iter=10`). Keempatnya dijalankan secara terpisah per basis data (tidak mencampur baris TKPI dan MyFCD) dan hanya menyasar 20 nutrisi berstrategi "imputasi internal". Seluruh baseline berhasil menghasilkan keluaran tanpa nilai kosong tersisa pada kolom target (0 missing, terverifikasi otomatis melalui `validate_imputed_output`).

**Tabel 3.5.** Ringkasan keluaran baseline (per basis data, kolom bertarget "imputasi internal")

| Metode | Baris TKPI | Baris MyFCD | Missing tersisa |
|---|---|---|---|
| Mean | 1.146 | 234 | 0 |
| Median | 1.146 | 234 | 0 |
| KNN (k=5) | 1.146 | 234 | 0 |
| MICE (seed=42) | 1.146 | 234 | 0 |

### 3.5.5. Hasil MissForest Dalam-Basis-Data

MissForest (via `IterativeImputer(RandomForestRegressor)`, `n_estimators=50`, `max_iter=10`) dilatih dan diterapkan secara terpisah pada TKPI dan MyFCD, menggunakan seluruh ruang fitur nutrisi bersama (bukan hanya kolom target) agar dapat memanfaatkan korelasi antar-nutrisi — inilah yang membedakannya secara metodologis dari baseline mean/median yang bersifat univariat. Kolom yang 100% kosong pada basis data terkait (`vitamin_a_mcg`) dikeluarkan dari ruang prediktor karena tidak memberi sinyal apa pun. TKPI mengimputasi 21 kolom target (20 nutrisi internal ditambah `carotene_total_mcg`, karena TKPI punya 53% data asli untuk nutrisi ini dan bisa dipakai untuk melatih model sendiri); MyFCD mengimputasi 20 kolom target (tidak termasuk `carotene_total_mcg`, karena MyFCD 0% data asli untuk nutrisi ini dan mengandalkan cross-database transfer sepenuhnya, lihat 3.5.6). Hasil: seluruh kolom target terisi penuh (0 missing) pada kedua basis data, dan hasil terverifikasi reproducible (dua kali proses ulang dengan seed tetap = 42 menghasilkan keluaran identik).

### 3.5.6. Hasil Cross-Database Transfer (TKPI → MyFCD) — Kebaruan Metodologis Utama

Sesuai kebaruan yang dijanjikan pada Bab 2.5 dan judul artikel target (*Cross-Database Transfer Imputation for Southeast Asian Food Composition Harmonisation*), imputer MissForest dilatih pada TKPI (basis data dengan cakupan lebih padat) kemudian diterapkan pada MyFCD melalui mekanisme `transform()`: model belajar hubungan antar-nutrisi dari TKPI, lalu memprediksi nilai kolom target pada MyFCD menggunakan nilai nutrisi lain milik MyFCD sendiri sebagai prediktor. Metode ini saat ini menyasar satu nutrisi yang memenuhi kriteria "0% di MyFCD, tersedia sebagian di TKPI": `carotene_total_mcg`.

**Tabel 3.6.** Hasil cross-database transfer untuk `carotene_total_mcg`

| Kondisi | Basis Data | Keterisian Sebelum | Keterisian Sesudah | Rerata Nilai (setelah) |
|---|---|---|---|---|
| Sebelum Tahap 3 | TKPI | 607/1.146 (53,0%) | — | 96,84 mcg (dari data yang tersedia) |
| Sebelum Tahap 3 | MyFCD | 0/234 (0,0%) | — | — |
| Setelah Tahap 3 | TKPI | — | 1.146/1.146 (100%, via MissForest dalam-basis-data) | 96,84 mcg |
| Setelah Tahap 3 | MyFCD | — | 234/234 (100%, via cross-database transfer) | 112,35 mcg |

[GAMBAR 3.5.b — Grafik batang perbandingan keterisian `carotene_total_mcg` sebelum vs sesudah Tahap 3, per basis data. Sumber data: Tabel 3.6 / `reports/imputation_method_comparison.csv`.]

### 3.5.7. Peminjaman Nilai USDA (Value Borrowing) — Pass-Through dari Tahap 1

Enam kolom yang sudah dipinjam Tahap 1 dari USDA (`magnesium_mg`, `sugars_total_g`, `saturated_fat_g`, `cholesterol_mg`, `vitamin_b6_mg`, `vitamin_b12_mcg`) digunakan apa adanya oleh Tahap 3 tanpa pemrosesan ulang, sesuai prinsip tidak menduplikasi pekerjaan tahap sebelumnya.

### 3.5.8. Temuan Penting: Gap yang Terdokumentasi, Bukan Ditutupi

Satu nutrisi, `vitamin_a_mcg`, memiliki strategi "Pinjam USDA (kosong di kedua basis)" pada `availability_matrix.csv`, namun **belum termasuk** di antara 6 kolom yang benar-benar dipinjam Tahap 1. Akibatnya, saat ini belum ada jalur data nyata untuk mengisi nutrisi tersebut. Sesuai kebijakan non-fabrikasi proyek ini, sel `vitamin_a_mcg` **dibiarkan kosong (NaN)** di seluruh keluaran Tahap 3, dan dilaporkan eksplisit sebagai *unresolved* — bukan diisi dengan tebakan atau nilai rata-rata paksa. Temuan ini menjadi rekomendasi konkret untuk Tahap 1 (lihat Bab 4).

### 3.5.9. Dataset Terintegrasi dan Akuntansi Penuh

Keluaran akhir Tahap 3, `nutrition_repository_imputed.csv`, memuat 1.380 baris (1.146 TKPI + 234 MyFCD), konsisten dengan total baris yang telah dilaporkan pada `integration_summary.md` sejak Tahap 1. Setiap sel nutrisi pada dataset ini diberi label sumber resolusi secara penuh dan dapat diaudit (Tabel 3.7).

**Tabel 3.7.** Akuntansi resolusi sel nutrisi pada dataset terintegrasi (22 nutrisi × 1.380 baris = 30.360 sel)

| Status Resolusi | Jumlah Sel | Persentase dari Total Sel |
|---|---|---|
| Terselesaikan — imputasi internal (MissForest), 20 nutrisi | 27.600 | 90,9% |
| Terselesaikan — imputasi internal (MissForest), sisi TKPI dari `carotene_total_mcg` | 1.146 | 3,8% |
| Terselesaikan — cross-database transfer, sisi MyFCD dari `carotene_total_mcg` | 234 | 0,8% |
| Belum terselesaikan — `vitamin_a_mcg` (menunggu value borrowing USDA) | 1.380 | 4,5% |
| **Total** | **30.360** | **100%** |

Tingkat penyelesaian Tahap 3 mencapai **95,5%** (28.980 dari 30.360 sel), dengan sisa 4,5% seluruhnya berasal dari satu gap yang sudah teridentifikasi dan tercatat di atas (`vitamin_a_mcg`).

[GAMBAR 3.5.c — Diagram lingkaran/batang status resolusi sel nutrisi sesuai Tabel 3.7. Sumber data: `reports/imputation_summary.md`.]

### 3.5.10. Ekspor Siap-Evaluasi untuk Tahap 4

Untuk mendukung Tahap 4 (Kuantifikasi Ketidakpastian) dan evaluasi hold-out pada Bab 2.7, seluruh keluaran metode (mean, median, KNN, MICE, MissForest, cross-DB transfer, serta nilai asli sebelum imputasi) diekspor ke format long (`food_id, source_db, nutrient, method, value`) pada `nutrition_repository_imputed_long.csv` — total 187.308 baris — beserta statistik deskriptif per pasangan nutrisi × metode pada `reports/imputation_method_comparison.csv`. Statistik ini **bersifat deskriptif saja** (count/mean/std) dan secara eksplisit bukan metrik akurasi; perhitungan RMSE/nRMSE terhadap data hold-out adalah tanggung jawab Tahap 4 yang belum dimulai (lihat Bab 4).

### 3.5.11. Reproducibility dan Jaminan Kualitas

Seluruh metode stokastik (MICE, MissForest, cross-database transfer) menggunakan `RANDOM_SEED = 42` yang tetap dan telah diverifikasi menghasilkan keluaran identik-byte pada pengulangan proses. Sebanyak 17 unit test baru ditambahkan (23 test total pada seluruh proyek, seluruhnya lulus), mencakup pengujian ketepatan nilai mean/median pada data terkendali, kelengkapan hasil KNN/MICE/MissForest, serta jaminan bahwa proses cross-database transfer tidak pernah mengubah data TKPI (basis data sumber pelatihan).

---

## 3.6. Luaran Konkret Tahap 3

**Tabel 3.8.** Berkas keluaran Tahap 3

| Berkas | Lokasi | Deskripsi |
|---|---|---|
| `tkpi/myfcd_imputed_baseline_{mean,median,knn,mice}.csv` | `data_processed/` | Hasil 4 metode baseline, per basis data |
| `tkpi/myfcd_imputed_missforest.csv` | `data_processed/` | Hasil MissForest dalam-basis-data |
| `myfcd_imputed_crossdb.csv` | `data_processed/` | Hasil cross-database transfer TKPI→MyFCD |
| `nutrition_repository_imputed.csv` | `data_processed/` | Dataset terintegrasi final (1.380 baris) |
| `nutrition_repository_imputed_long.csv` | `data_processed/` | Format long untuk Tahap 4 (187.308 baris) |
| `imputation_summary.md` | `reports/` | Akuntansi resolusi per nutrisi |
| `imputation_method_comparison.csv` | `reports/` | Statistik deskriptif per metode |
| `stage3_imputation.md` | `docs/` | Dokumentasi metodologi lengkap |

Seluruh kode sumber (`src/imputation/`, `scripts/run_baseline_imputation.py`, `scripts/run_missforest_imputation.py`, `scripts/run_integration.py`, `scripts/export_evaluation_ready.py`) telah diunggah ke repositori GitHub tim, tersusun dalam 11 commit terpisah (satu commit per milestone) untuk menjaga keterlacakan (traceability) proses pengembangan.

---

## Draft tambahan BAB 4. KESIMPULAN DAN SARAN (bagian Tahap 3)

Tahap 3 (imputasi data berbasis machine learning) telah diselesaikan sesuai rancangan pada Bab 2.5: empat metode baseline pembanding (mean, median, KNN, MICE), MissForest dalam-basis-data, dan cross-database transfer TKPI→MyFCD sebagai kebaruan metodologis utama, seluruhnya beroperasi mengikuti strategi yang telah dirutekan Tahap 2 tanpa mengulang keputusan diagnosis. Dari 22 nutrisi yang dirutekan, 95,5% sel data berhasil diselesaikan; sisanya (`vitamin_a_mcg`) terdokumentasi eksplisit sebagai gap yang belum tertutup, bukan cacat tersembunyi.

**Saran untuk kelanjutan:**
1. Menambahkan `vitamin_a_mcg` ke daftar kolom peminjaman nilai USDA pada Tahap 1, agar strategi "Pinjam USDA" pada `availability_matrix.csv` memiliki jalur data yang benar-benar dapat dieksekusi.
2. Melanjutkan ke Tahap 4 (Kuantifikasi Ketidakpastian, bootstrap B=50) dan evaluasi hold-out (RMSE/nRMSE, 15% data TKPI) sesuai Bab 2.6–2.7, memanfaatkan `nutrition_repository_imputed_long.csv` yang sudah disiapkan sebagai input langsung.
3. Uji Little's MCAR formal untuk MyFCD (disebutkan masih "dalam proses" pada Tabel 3.1) perlu dituntaskan agar Tabel 3.1 dapat diisi lengkap.

---

## Daftar Pustaka Tambahan (rujukan metode Tahap 3)

7. Stekhoven DJ, Bühlmann P. MissForest—non-parametric missing value imputation for mixed-type data. Bioinformatics. 2012;28(1):112–8.
8. van Buuren S, Groothuis-Oudshoorn K. mice: Multivariate Imputation by Chained Equations in R. J Stat Softw. 2011;45(3):1–67.
9. Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine Learning in Python. J Mach Learn Res. 2011;12:2825–30.
