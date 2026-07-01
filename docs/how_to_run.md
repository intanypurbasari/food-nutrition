# How To Run

## Setup Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Setup macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Recon

```bash
python scripts/source_recon.py
```

Output:

- `docs/source_recon_report.md`
- `reports/source_recon_summary.json`

## Menjalankan Pipeline End-to-End

```bash
python scripts/run_pipeline.py --limit 20
```

Jika raw data sudah tersedia:

```bash
python scripts/run_pipeline.py --skip-scrape
```

## Menjalankan Tahap Manual

```bash
python scripts/scrape_tkpi.py --limit 20
python scripts/scrape_myfcd.py --limit 20
python scripts/clean_tkpi.py
python scripts/clean_myfcd.py
python scripts/validate_dataset.py
python scripts/build_repository_sample.py
python scripts/export_repository_json.py
```

## Menjalankan Prototipe

```bash
streamlit run app/prototype.py
```

Jika file repository belum tersedia, jalankan tahap cleaning, merge, dan export lebih dulu.
