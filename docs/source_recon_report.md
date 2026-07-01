# Source Reconnaissance Report

Recon dilakukan ringan dengan request terbatas, delay minimal, cache lokal, dan tanpa bypass proteksi.

## TKPI

- URL: https://www.panganku.org/id-ID/cari_nutrisi
- Status: accessible
- Selector kandidat: table, form
- Catatan: A normal public form/AJAX flow for limited extraction was detected. tables=1, forms=1, links=15 Normal category POST flow is available for limited listing/detail extraction.

## MyFCD

- URL: https://myfcd.moh.gov.my/myfcdcurrent/
- Status: accessible
- Selector kandidat: table
- Catatan: A normal public form/AJAX flow for limited extraction was detected. tables=5, forms=0, links=19 Public DataTables AJAX endpoint is referenced by the page.
