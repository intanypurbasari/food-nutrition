# Nutrition Repository

Knowledge Repository Nutrisi dan Kesehatan Mental berbasis digital untuk mendukung sistem rekomendasi gizi personal.

Status proyek: **in progress**.

## Ringkasan

Repositori ini menyiapkan pipeline data engineering untuk mengumpulkan, membersihkan, memvalidasi, menggabungkan, dan mengekspor data komposisi pangan dari TKPI dan MyFCD. Fokus pekerjaan adalah lapisan hulu: data collection, data preparation, dan proof of concept knowledge repository. USDA FoodData Central digunakan hanya sebagai referensi struktur skema, bukan target scraping.

Pipeline ini tidak membuat data final palsu. Jika sumber tidak bisa diakses secara etis dengan request terbatas, script akan menghasilkan laporan fallback.

## Struktur Folder

```text
config/          Konfigurasi default
data_raw/        Hasil scraping mentah
data_clean/      Dataset per sumber setelah normalisasi
data_processed/  Repository gabungan dan export JSON
docs/            Dokumentasi proyek dan laporan naratif
reports/         Laporan terstruktur hasil pipeline
scripts/         Entry point CLI
src/             Modul Python reusable
tests/           Unit test dan fixture kecil
app/             Prototipe Streamlit
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

## Output Utama

- `data_raw/tkpi_raw.csv` dan `data_raw/myfcd_raw.csv`
- `data_clean/tkpi_clean.csv` dan `data_clean/myfcd_clean.csv`
- `data_processed/nutrition_repository_sample.csv`
- `data_processed/nutrition_repository_sample.json`
- `reports/data_quality_report.md`
- `reports/integration_summary.md`
- `app/prototype.py`

## Etika Scraping

Semua scraper wajib memakai delay, limit kecil, user-agent wajar, cache lokal, dan tidak melakukan bypass captcha, login wall, rate limit, atau proteksi situs.
