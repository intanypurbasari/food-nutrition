# Final Output Summary

Tanggal eksekusi: 2026-07-01

## Ringkasan Dataset

Pipeline berhasil menghasilkan repository gabungan dengan total **1.380 record**:

- TKPI: 1.146 record
- MyFCD: 234 record

Seluruh record sudah dipetakan ke unified schema berisi 36 kolom.

## Output Utama

- `data_raw/tkpi_raw.csv`
- `data_raw/myfcd_raw.csv`
- `data_clean/tkpi_clean.csv`
- `data_clean/myfcd_clean.csv`
- `data_processed/nutrition_repository_sample.csv`
- `data_processed/nutrition_repository_sample.json`
- `data_processed/nutrition_repository_by_source.json`
- `data_processed/nutrition_repository_by_category.json`
- `reports/data_quality_report.md`
- `reports/integration_summary.md`

## Kualitas Data

Validasi terakhir:

- Total rows: 1.380
- Valid rows: 1.380
- Invalid rows: 0
- Duplicate count: 0

Terdapat 4 range warning pada nilai energi di TKPI, seluruhnya berasal dari bahan minyak/lemak sekitar 902 kcal per 100g. Nilai tersebut tidak dihapus karena masih masuk akal untuk bahan pangan berlemak tinggi.

## Catatan Metode

Data TKPI diambil melalui flow publik kategori dan detail pangan dengan delay, cache lokal, dan retry ringan. Data MyFCD diambil melalui endpoint publik DataTables dan endpoint perbandingan nutrisi yang digunakan halaman web. Tidak ada bypass captcha, login, rate limit, atau proteksi situs.
