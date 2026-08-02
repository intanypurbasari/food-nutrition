# Nutrition Repository

Knowledge Repository Nutrisi dan Kesehatan Mental berbasis digital untuk mendukung sistem rekomendasi gizi personal.

Status proyek: **in progress**.

## Ringkasan

Repositori ini menyiapkan pipeline data engineering untuk mengumpulkan, membersihkan, memvalidasi, menggabungkan, dan mengekspor data komposisi pangan dari **TKPI** (Tabel Komposisi Pangan Indonesia) dan **MyFCD** (Malaysian Food Composition Database). Fokus pekerjaan adalah lapisan hulu: data collection, data preparation, dan proof of concept knowledge repository. **USDA FoodData Central (SR Legacy)** digunakan sebagai referensi struktur skema sekaligus sumber peminjaman nilai (value borrowing) untuk nutrisi yang tidak tersedia pada skema regional.

Pipeline ini tidak membuat data final palsu. Jika sumber tidak bisa diakses secara etis dengan request terbatas, script akan menghasilkan laporan fallback.

Sub-riset ini merupakan bagian dari program penelitian yang lebih besar (Jatim Melaju 2026) dengan kebaruan metodologis berupa **cross-database transfer imputation** untuk harmonisasi data komposisi pangan lintas-negara.

## Struktur Folder

```text
config/          Konfigurasi default
data_raw/        Hasil scraping mentah
data_clean/      Dataset per sumber setelah normalisasi
data_processed/  Repository gabungan, linkage table, dan export JSON
docs/            Dokumentasi proyek, laporan naratif, dan gambar
reports/         Laporan terstruktur hasil pipeline
scripts/         Entry point CLI
src/             Modul Python reusable
tests/           Unit test dan fixture kecil
app/             Prototipe Streamlit
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

## Menjalankan Pipeline

```bash
python scripts/source_recon.py
python scripts/run_pipeline.py --limit 20
```

Jika data raw sudah tersedia dan scraping ingin dilewati:

```bash
python scripts/run_pipeline.py --skip-scrape
```

## Metodologi Sub-Riset (Harmonisasi & Integrasi)

Alur kerja harmonisasi dan integrasi data terdiri atas empat tahap utama, dilanjutkan evaluasi dan integrasi:

1. **Resolusi Entitas (Entity Resolution).** Penautan antar-item pangan lintas basis data menggunakan record linkage berbasis kemiripan teks: crosswalk kategori, normalisasi nama, pencocokan TF-IDF cosine, dan pelabelan tingkat keyakinan (HIGH / MEDIUM / LOW).
2. **Diagnosis Mekanisme Missing Data.** Uji Little's MCAR per basis data dilengkapi analisis pola ko-okurensi kehilangan. Temuan: TKPI bersifat **MAR** (kehilangan terlokalisasi pada mineral), MyFCD bersifat **MNAR / struktural** (kehilangan menyeluruh pada panel proksimat).
3. **Imputasi Berbasis Machine Learning.** MissForest dengan pendekatan **cross-database transfer** (imputer dilatih pada TKPI, diterapkan pada MyFCD), serta value borrowing dari USDA untuk nutrisi yang kosong di kedua basis regional.
4. **Kuantifikasi Ketidakpastian.** Interval kepercayaan bootstrap (B = 50) dengan penandaan nutrisi berketidakpastian tinggi.

Integrasi data dilakukan pada tahap akhir (setelah imputasi dan evaluasi) agar skema cross-database transfer dapat diterapkan.

## Output Utama

Output dasar pipeline:

- `data_raw/tkpi_raw.csv` dan `data_raw/myfcd_raw.csv`
- `data_clean/tkpi_clean.csv` dan `data_clean/myfcd_clean.csv`
- `data_processed/nutrition_repository_sample.csv`
- `data_processed/nutrition_repository_sample.json`
- `reports/data_quality_report.md`
- `reports/integration_summary.md`
- `app/prototype.py`

Output Stage 3 (imputasi ML):

- `data_processed/nutrition_repository_imputed.csv`
- `data_processed/nutrition_repository_imputed_long.csv`
- `reports/imputation_summary.md`
- `reports/imputation_method_comparison.csv`

## Output Tahap Resolusi Entitas & Diagnosis Missing Data (Update)

### Entity Resolution (`data_processed/`)

- `tkpi_usda_links.csv`, `myfcd_usda_links.csv` — Tabel penautan masing-masing basis regional ke USDA.
- `tkpi_myfcd_links.csv` — Tabel penautan langsung TKPI–MyFCD (kolom: `tkpi_food_id`, `myfcd_food_id`, `similarity_score`). Berisi 156 pasangan hasil pencocokan TF-IDF cosine.
- `tkpi_myfcd_links_mutual.csv` — Subset tautan 1-1 (mutual-best), 52 pasangan berpresisi tinggi untuk pelaporan konservatif.
- `tkpi_myfcd_links_detailed.csv` — Versi lengkap tautan (nama pangan, kelompok, label keyakinan) untuk audit manual.
- `tkpi_only_nonmatch.csv`, `myfcd_only_nonmatch.csv` — Pangan unik per basis data (990 TKPI, 179 MyFCD) yang tidak memiliki padanan.
- `tkpi_enriched.csv`, `myfcd_enriched.csv` — TKPI/MyFCD yang diperkaya dengan kolom nutrisi dari USDA.

### Diagnosis Missing Data (`reports/`)

- `availability_matrix_TKPI_vs_MyFCD.csv` — Peta keterisian 22 nutrisi pada kedua basis data beserta strategi imputasi (imputasi internal / cross-database transfer / peminjaman USDA).
- `missing_corr_TKPI.csv`, `missing_corr_MyFCD.csv` — Matriks korelasi antar indikator kehilangan (koefisien phi).
- `ringkasan_r_perbandingan.csv` — Ringkasan nilai korelasi per kelompok nutrisi (makronutrien, mineral, vitamin).

### Kode Analisis (`scripts/`)

- `entity_resolution_threeway.py` — Pipeline resolusi entitas tiga basis data (TKPI–MyFCD–USDA).
- `analisis_pola_kehilangan.py` — Analisis pola missingness (matriks korelasi, ringkasan, heatmap).

### Dokumentasi & Gambar (`docs/`)

- `heatmap_missing_TKPI.png`, `heatmap_missing_MyFCD.png` — Heatmap korelasi indikator kehilangan.
- `SubStudy_Workflow_Diagram_EN.png` — Diagram alur sub-riset (versi Bahasa Inggris untuk manuskrip).
- `Diagram_Alir_SubRiset_ID.png` — Diagram alur sub-riset (versi Bahasa Indonesia untuk laporan).

## Stage 3 — Machine Learning Imputation

Stage 3 mengimplementasikan tahap 3 dari alur "Metodologi Sub-Riset" di atas: imputasi nutrisi yang hilang menggunakan mean/median/KNN/MICE sebagai baseline pembanding, serta **MissForest** (dalam basis data dan cross-database transfer TKPI→MyFCD) sebagai metode utama, dengan strategi per nutrisi mengikuti routing yang sudah ditetapkan Stage 2 di `data_processed/availability_matrix.csv`. Nutrisi yang belum memiliki jalur data nyata (mis. `vitamin_a_mcg`) dilaporkan eksplisit sebagai *unresolved*, bukan diisi dengan nilai fabrikasi.

Jalankan seluruh tahap Stage 3 berurutan:

```bash
python scripts/run_baseline_imputation.py
python scripts/run_missforest_imputation.py
python scripts/run_integration.py
python scripts/export_evaluation_ready.py
```

atau lewat orchestrator utama dengan flag opsional `--include-imputation`:

```bash
python scripts/run_pipeline.py --skip-scrape --include-imputation
```

Detail metodologi lengkap, kode implementasi (`src/imputation/`), dan daftar output: lihat [`docs/stage3_imputation.md`](docs/stage3_imputation.md).

## Temuan Kunci

- **Tidak ada irisan nama pangan yang identik** antar basis data, sehingga penautan memerlukan pendekatan kemiripan teks, bukan join berbasis kunci.
- **Mekanisme kehilangan berbeda antar basis data**: TKPI = MAR (r blok mineral hingga 0,96), MyFCD = MNAR/struktural (r panel proksimat rerata 0,862).
- **Ketersediaan nutrisi berbeda per basis data**: mis. `carotene_total_mcg` terisi 53% di TKPI namun 0% di MyFCD (kandidat cross-database transfer), sedangkan `vitamin_a_mcg` kosong 100% di keduanya (kandidat peminjaman USDA).

## Sumber Data

- **TKPI** — Tabel Komposisi Pangan Indonesia: <https://www.panganku.org/>
- **MyFCD** — Malaysian Food Composition Database: <https://myfcd.moh.gov.my/>
- **USDA SR Legacy** — USDA FoodData Central: <https://fdc.nal.usda.gov/download-datasets>

## Etika Scraping

Semua scraper wajib memakai delay, limit kecil, user-agent wajar, cache lokal, dan tidak melakukan bypass captcha, login wall, rate limit, atau proteksi situs.

## Catatan Lisensi Data

Dataset `*_clean.csv` merupakan data turunan dari TKPI dan MyFCD. Sebelum meredistribusi nilai nutrisi mentah secara terbuka, pastikan hak penggunaan/lisensi data sumber memperbolehkannya. Untuk dataset final berukuran besar, disarankan menggunakan repositori berarsip permanen (mis. Zenodo atau GigaDB) yang menyediakan DOI untuk sitasi.
