# Konteks Penelitian

## Judul Penelitian Payung

Pengembangan Knowledge Repository Nutrisi dan Kesehatan Mental Berbasis Digital untuk Mendukung Sistem Rekomendasi Gizi Personal.

## Fokus Tim UPN

Fokus tim UPN "Veteran" Jawa Timur adalah **Technology for Merging + Imputation Multiple Datasets**. Artinya, ruang kerja utama tim berada pada lapisan data engineering: bagaimana beberapa dataset komposisi pangan dari sumber berbeda dapat dikumpulkan, disamakan skemanya, digabungkan, dan disiapkan untuk tahap imputasi nilai yang hilang.

## Posisi Proyek Ini

Proyek ini berada pada bagian hulu dari sistem yang lebih besar. Outputnya bukan sistem rekomendasi gizi penuh, melainkan fondasi data awal berupa:

- hasil pengumpulan data komposisi pangan dari TKPI dan MyFCD;
- data mentah dalam format CSV/JSON;
- data bersih yang mengikuti unified schema;
- laporan kualitas data dan missing value;
- repository sample hasil penggabungan;
- prototipe pencarian sederhana sebagai proof of concept.

Pipeline ini dirancang agar hasil kerja dapat diaudit dan direproduksi. Jika sumber data tidak dapat diakses secara otomatis dengan cara yang etis, keterbatasan tersebut dicatat sebagai fallback report, bukan ditutup-tutupi dengan data buatan.
