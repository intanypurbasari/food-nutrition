# Stage 3 — Machine Learning Imputation Pipeline

Dokumen ini menjelaskan metodologi, cakupan, dan output Stage 3 (imputasi berbasis machine learning), yang dibangun di atas output Stage 1 (resolusi entitas, Joyce) dan Stage 2 (diagnosis missing data, Intan). Stage 3 tidak mengubah file input dari kedua tahap tersebut; seluruh output Stage 3 adalah file baru di bawah `data_processed/` dan `reports/`.

## Ringkasan Alur

```text
tkpi_enriched.csv, myfcd_enriched.csv      (Stage 1, read-only)
availability_matrix.csv                     (Stage 2, read-only - router strategi)
            |
            v
scripts/run_baseline_imputation.py   -> tkpi/myfcd_imputed_baseline_{mean,median,knn,mice}.csv
scripts/run_missforest_imputation.py -> tkpi/myfcd_imputed_missforest.csv, myfcd_imputed_crossdb.csv
scripts/run_integration.py           -> nutrition_repository_imputed.csv, reports/imputation_summary.md
scripts/export_evaluation_ready.py   -> nutrition_repository_imputed_long.csv, reports/imputation_method_comparison.csv
```

Setiap nutrisi diimputasi sesuai strategi yang sudah ditetapkan Stage 2 di `data_processed/availability_matrix.csv` (kolom `strategi_imputasi`), bukan hasil keputusan ulang oleh Stage 3.

## Metode

### Mean baseline dan Median baseline

`src/imputation/baselines.py`: `mean_impute` dan `median_impute` mengisi nilai kosong dengan mean/median kolom itu sendiri, dihitung terpisah per basis data (TKPI dan MyFCD tidak pernah dicampur). Hanya menyentuh nutrisi berstrategi **"Imputasi internal per basis"** (20 dari 22 nutrisi yang dirutekan Stage 2).

### KNN baseline

`knn_impute` menggunakan `sklearn.impute.KNNImputer` (n_neighbors=5, default) — imputasi multivariat berbasis kemiripan antar baris pada ruang fitur nutrisi yang sama. Deterministik untuk data dan k yang tetap (`KNNImputer` tidak memiliki parameter `random_state`).

### MICE baseline

`mice_impute` menggunakan `sklearn.impute.IterativeImputer` (Multiple Imputation by Chained Equations), `max_iter=10`, `random_state` dari `config.imputation_settings.RANDOM_SEED` (42) untuk reproducibility.

### MissForest (dalam basis data)

`src/imputation/missforest_imputer.py`: `missforest_impute` menggunakan `IterativeImputer(estimator=RandomForestRegressor)` sebagai implementasi MissForest. **Catatan keputusan dependency:** paket asli `missingpy` dicoba lebih dulu (Milestone 1) dan terbukti tidak lagi kompatibel dengan scikit-learn versi terkini (`ModuleNotFoundError: sklearn.neighbors.base`, modul privat yang sudah dihapus sejak lama). Fit dilakukan pada seluruh ruang fitur nutrisi bersama (bukan hanya kolom target) agar model dapat memanfaatkan korelasi antar nutrisi — inilah yang membedakannya dari baseline univariat (mean/median).

### MissForest cross-database transfer (TKPI → MyFCD)

`src/imputation/cross_transfer.py`: `cross_db_transfer_impute` — kebaruan metodologis utama sub-riset ini. Imputer dilatih pada TKPI (fit), lalu diterapkan pada MyFCD (transform) menggunakan `IterativeImputer.transform()`, yang menerapkan estimator per-fitur hasil fit-TKPI ke data MyFCD dengan memakai nilai nutrisi lain milik MyFCD sendiri sebagai prediktor. Metode ini menargetkan nutrisi berstrategi **"Cross-DB transfer / USDA"** — saat ini hanya `carotene_total_mcg` (53% terisi di TKPI, 0% di MyFCD).

### Peminjaman nilai USDA (value borrowing)

Untuk nutrisi berstrategi **"Pinjam USDA (kosong di kedua basis)"**, Stage 3 memakai kolom yang sudah dipinjam Stage 1 di `*_enriched.csv` (`magnesium_mg`, `sugars_total_g`, `saturated_fat_g`, `cholesterol_mg`, `vitamin_b6_mg`, `vitamin_b12_mcg`) apa adanya — tidak melakukan value borrowing ulang.

## Keterbatasan yang Terdokumentasi: `vitamin_a_mcg`

`vitamin_a_mcg` memiliki strategi **"Pinjam USDA (kosong di kedua basis)"** di `availability_matrix.csv`, tetapi **bukan** salah satu dari 6 kolom yang benar-benar dipinjam Stage 1 dari USDA. Artinya belum ada jalur data nyata untuk mengisi nutrisi ini pada tahap Stage 3 saat ini. Sesuai kebijakan non-fabrikasi proyek ini, sel `vitamin_a_mcg` **dibiarkan kosong (NaN)** di seluruh output Stage 3 dan dilaporkan eksplisit sebagai *unresolved* di `reports/imputation_summary.md` — bukan bug, melainkan gap yang jujur dan tercatat. Menutup gap ini (mis. menambah value borrowing USDA untuk vitamin A) adalah pekerjaan lanjutan di luar cakupan Stage 3.

Field lain, `edible_portion_percent`, sempat 100% kosong di kedua basis data dan tidak pernah masuk cakupan diagnosis Stage 2 (tidak ada baris untuknya di `availability_matrix.csv`). Karena tidak pernah terisi sejak tahap scraping paling awal dan tidak ada rencana pengisian, field ini **dihapus sepenuhnya dari skema** (`src/schema/nutrition_schema.py`) alih-alih dibiarkan sebagai kolom kosong permanen — bukan lagi diberi label "tidak dirutekan Stage 2", karena kolomnya sudah tidak ada sama sekali di seluruh output pipeline (data_clean, enriched, hingga dataset terintegrasi).

## Output

### `data_processed/`

| File | Deskripsi |
|---|---|
| `tkpi_imputed_baseline_{mean,median,knn,mice}.csv` | Hasil masing-masing baseline, per sumber (TKPI) |
| `myfcd_imputed_baseline_{mean,median,knn,mice}.csv` | Hasil masing-masing baseline, per sumber (MyFCD) |
| `tkpi_imputed_missforest.csv`, `myfcd_imputed_missforest.csv` | MissForest dalam-basis-data, per sumber |
| `myfcd_imputed_crossdb.csv` | MissForest cross-database transfer (dilatih di TKPI, diterapkan ke MyFCD) |
| `nutrition_repository_imputed.csv` | Dataset terintegrasi final (1.380 baris = 1.146 TKPI + 234 MyFCD), nilai terbaik per nutrisi per pangan sesuai strategi `availability_matrix.csv` |
| `nutrition_repository_imputed_long.csv` | Format long (food_id, source_db, nutrient, method, value) untuk kebutuhan evaluasi Stage 4 |

### `reports/`

| File | Deskripsi |
|---|---|
| `imputation_summary.md` | Akuntansi lengkap per nutrisi: berapa sel diselesaikan lewat internal/cross-DB/USDA-borrow, dan berapa yang masih unresolved |
| `imputation_method_comparison.csv` | Statistik deskriptif (count/mean/std) per nutrisi x metode — **deskriptif saja, bukan metrik akurasi**; perbandingan akurasi terhadap ground truth adalah tanggung jawab Stage 4 |

## Cara Menjalankan

Urutan berikut harus dijalankan sesuai urutan (setiap tahap bergantung pada output tahap sebelumnya):

```bash
python scripts/run_baseline_imputation.py       # mean, median, knn, mice
python scripts/run_missforest_imputation.py     # within-database + cross-db transfer
python scripts/run_integration.py               # dataset terintegrasi final
python scripts/export_evaluation_ready.py       # export long-format untuk Stage 4
```

Atau, sekaligus lewat pipeline orchestrator utama:

```bash
python scripts/run_pipeline.py --skip-scrape --include-imputation
```

Flag `--include-imputation` bersifat opsional (default off); tanpa flag ini, `run_pipeline.py` berperilaku identik dengan sebelum Stage 3 ada.

## Reproducibility

`config.imputation_settings.RANDOM_SEED = 42` dipakai oleh semua metode stokastik (MICE, MissForest, cross-DB transfer). KNN tidak memerlukan seed karena deterministik untuk data dan k tetap. Konvergensi MICE/MissForest tidak diverifikasi secara terpisah oleh Stage 3 — itu bagian dari evaluasi Stage 4.
