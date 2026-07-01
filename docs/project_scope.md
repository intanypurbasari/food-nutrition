# Scope Proyek

## Jobdesk Mahasiswa

Ruang kerja mahasiswa pada proyek ini meliputi:

1. Melakukan source reconnaissance ringan terhadap TKPI dan MyFCD.
2. Membuat scraper terbatas dan etis untuk TKPI dan MyFCD.
3. Mengonversi hasil scraping mentah menjadi CSV dan JSON.
4. Membersihkan dan menormalisasi data ke unified schema.
5. Menghasilkan laporan missing value dan kualitas data.
6. Menggabungkan dataset bersih menjadi repository sample.
7. Membantu desain prototipe aplikasi knowledge repository berbasis Streamlit.

## Sumber Data

Target data collection utama:

- TKPI: Tabel Komposisi Pangan Indonesia.
- MyFCD: Malaysian Food Composition Database.

USDA FoodData Central tidak menjadi target scraping pada scope ini. USDA hanya dipakai sebagai referensi struktur skema agar desain kolom lebih kompatibel dengan praktik internasional.

## Batasan Etis Scraping

Scraping dilakukan dengan batasan berikut:

- memakai delay minimal antar request;
- memakai limit kecil secara default;
- memakai user-agent yang wajar dan menjelaskan tujuan akademik;
- tidak melakukan request paralel agresif;
- tidak melakukan bypass captcha, login wall, rate limit, atau proteksi situs;
- tidak membuat data final palsu jika scraping gagal;
- mencatat kendala akses secara jujur dalam laporan fallback.

Jika skala pengambilan data perlu diperbesar, perlu ada pembahasan lebih lanjut dengan dosen atau pengelola data resmi.
