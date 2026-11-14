# Masking Sweep

- Fraksi sel terukur yang disembunyikan: 5%-50%; 10 seed per fraksi.
- Angka: rerata ± sd (antar seed) dari median nRMSE per nutrisi; makin kecil makin baik.

## MyFCD

| Fraksi | crossdb | group_median | knn | mean | mice | missforest | softimpute |
|---|---|---|---|---|---|---|---|
| 5% | 1.126 ± 0.231 | 0.842 ± 0.241 | 0.995 ± 0.138 | 1.588 ± 0.531 | 1.046 ± 0.300 | 0.866 ± 0.163 | 1.410 ± 0.270 |
| 10% | 1.213 ± 0.384 | 0.859 ± 0.132 | 0.981 ± 0.067 | 1.201 ± 0.158 | 1.059 ± 0.229 | 0.942 ± 0.300 | 1.216 ± 0.192 |
| 15% | 1.159 ± 0.207 | 0.977 ± 0.070 | 1.065 ± 0.050 | 1.244 ± 0.191 | 1.147 ± 0.147 | 1.105 ± 0.154 | 1.412 ± 0.151 |
| 20% | 1.197 ± 0.243 | 0.943 ± 0.098 | 1.017 ± 0.029 | 1.123 ± 0.087 | 1.113 ± 0.118 | 1.094 ± 0.143 | 1.336 ± 0.081 |
| 25% | 1.249 ± 0.299 | 0.956 ± 0.036 | 1.056 ± 0.118 | 1.195 ± 0.181 | 1.205 ± 0.180 | 1.177 ± 0.305 | 1.441 ± 0.192 |
| 30% | 1.102 ± 0.119 | 0.968 ± 0.058 | 1.025 ± 0.028 | 1.103 ± 0.074 | 1.164 ± 0.282 | 1.039 ± 0.055 | 1.302 ± 0.169 |
| 35% | 1.059 ± 0.058 | 0.995 ± 0.036 | 1.037 ± 0.027 | 1.057 ± 0.062 | 1.143 ± 0.167 | 1.121 ± 0.108 | 1.260 ± 0.157 |
| 40% | 1.094 ± 0.094 | 1.009 ± 0.009 | 1.077 ± 0.083 | 1.046 ± 0.031 | 1.214 ± 0.240 | 1.109 ± 0.143 | 1.225 ± 0.127 |
| 45% | 1.037 ± 0.045 | 1.007 ± 0.012 | 1.019 ± 0.008 | 1.032 ± 0.017 | 1.279 ± 0.318 | 1.055 ± 0.076 | 1.224 ± 0.093 |
| 50% | 1.106 ± 0.175 | 1.009 ± 0.011 | 1.028 ± 0.019 | 1.025 ± 0.012 | 1.235 ± 0.222 | 1.061 ± 0.048 | 1.225 ± 0.081 |

## TKPI

| Fraksi | group_median | knn | mean | mice | missforest | softimpute |
|---|---|---|---|---|---|---|
| 5% | 0.972 ± 0.028 | 0.993 ± 0.023 | 1.009 ± 0.004 | 0.947 ± 0.053 | 0.889 ± 0.058 | 0.924 ± 0.048 |
| 10% | 0.971 ± 0.017 | 1.004 ± 0.020 | 1.006 ± 0.003 | 0.970 ± 0.055 | 0.923 ± 0.064 | 0.931 ± 0.025 |
| 15% | 0.971 ± 0.015 | 1.000 ± 0.024 | 1.002 ± 0.001 | 1.038 ± 0.067 | 0.943 ± 0.047 | 0.942 ± 0.026 |
| 20% | 0.978 ± 0.011 | 1.000 ± 0.020 | 1.003 ± 0.001 | 1.048 ± 0.076 | 0.948 ± 0.059 | 0.947 ± 0.022 |
| 25% | 0.981 ± 0.013 | 0.994 ± 0.011 | 1.002 ± 0.001 | 1.035 ± 0.058 | 0.960 ± 0.037 | 0.956 ± 0.021 |
| 30% | 0.977 ± 0.008 | 1.006 ± 0.004 | 1.002 ± 0.001 | 1.039 ± 0.050 | 0.986 ± 0.039 | 0.956 ± 0.028 |
| 35% | 0.986 ± 0.004 | 1.010 ± 0.008 | 1.001 ± 0.001 | 1.021 ± 0.038 | 0.991 ± 0.017 | 0.963 ± 0.013 |
| 40% | 0.980 ± 0.009 | 1.017 ± 0.012 | 1.001 ± 0.001 | 1.001 ± 0.026 | 0.995 ± 0.020 | 0.969 ± 0.010 |
| 45% | 0.983 ± 0.006 | 1.032 ± 0.011 | 1.002 ± 0.001 | 1.013 ± 0.016 | 1.032 ± 0.036 | 0.984 ± 0.012 |
| 50% | 0.988 ± 0.007 | 1.029 ± 0.011 | 1.001 ± 0.000 | 0.995 ± 0.022 | 1.006 ± 0.013 | 0.994 ± 0.012 |

## Uji berpasangan (Wilcoxon, koreksi Holm antar fraksi)

| Sumber | A vs B | Fraksi | HL shift (A - B) | p Holm |
|---|---|---|---|---|
| TKPI | knn vs softimpute | 5% | +0.067 | 0.020 |
| TKPI | knn vs softimpute | 10% | +0.072 | 0.020 |
| TKPI | knn vs softimpute | 15% | +0.057 | 0.020 |
| TKPI | knn vs softimpute | 20% | +0.052 | 0.020 |
| TKPI | knn vs softimpute | 25% | +0.039 | 0.020 |
| TKPI | knn vs softimpute | 30% | +0.050 | 0.020 |
| TKPI | knn vs softimpute | 35% | +0.045 | 0.020 |
| TKPI | knn vs softimpute | 40% | +0.047 | 0.020 |
| TKPI | knn vs softimpute | 45% | +0.048 | 0.020 |
| TKPI | knn vs softimpute | 50% | +0.035 | 0.020 |
| TKPI | softimpute vs missforest | 5% | +0.028 | 0.504 |
| TKPI | softimpute vs missforest | 10% | +0.008 | 1.000 |
| TKPI | softimpute vs missforest | 15% | -0.004 | 1.000 |
| TKPI | softimpute vs missforest | 20% | -0.000 | 1.000 |
| TKPI | softimpute vs missforest | 25% | -0.003 | 1.000 |
| TKPI | softimpute vs missforest | 30% | -0.030 | 0.504 |
| TKPI | softimpute vs missforest | 35% | -0.027 | 0.020 |
| TKPI | softimpute vs missforest | 40% | -0.026 | 0.031 |
| TKPI | softimpute vs missforest | 45% | -0.043 | 0.020 |
| TKPI | softimpute vs missforest | 50% | -0.013 | 0.068 |
| MyFCD | missforest vs crossdb | 5% | -0.262 | 0.035 |
| MyFCD | missforest vs crossdb | 10% | -0.218 | 0.020 |
| MyFCD | missforest vs crossdb | 15% | -0.025 | 1.000 |
| MyFCD | missforest vs crossdb | 20% | -0.044 | 1.000 |
| MyFCD | missforest vs crossdb | 25% | -0.082 | 1.000 |
| MyFCD | missforest vs crossdb | 30% | -0.052 | 1.000 |
| MyFCD | missforest vs crossdb | 35% | +0.052 | 0.844 |
| MyFCD | missforest vs crossdb | 40% | +0.005 | 1.000 |
| MyFCD | missforest vs crossdb | 45% | +0.016 | 1.000 |
| MyFCD | missforest vs crossdb | 50% | -0.019 | 1.000 |
| MyFCD | softimpute vs crossdb | 5% | +0.288 | 0.148 |
| MyFCD | softimpute vs crossdb | 10% | +0.047 | 0.625 |
| MyFCD | softimpute vs crossdb | 15% | +0.228 | 0.117 |
| MyFCD | softimpute vs crossdb | 20% | +0.165 | 0.262 |
| MyFCD | softimpute vs crossdb | 25% | +0.205 | 0.193 |
| MyFCD | softimpute vs crossdb | 30% | +0.184 | 0.096 |
| MyFCD | softimpute vs crossdb | 35% | +0.190 | 0.035 |
| MyFCD | softimpute vs crossdb | 40% | +0.127 | 0.047 |
| MyFCD | softimpute vs crossdb | 45% | +0.177 | 0.020 |
| MyFCD | softimpute vs crossdb | 50% | +0.137 | 0.137 |

## Waktu komputasi (detik per imputasi penuh)

| Sumber | Metode | Detik |
|---|---|---|
| TKPI | mean | 0.02 ± 0.00 |
| TKPI | group_median | 0.11 ± 0.00 |
| TKPI | knn | 0.12 ± 0.02 |
| TKPI | mice | 0.49 ± 0.03 |
| TKPI | softimpute | 0.13 ± 0.07 |
| TKPI | missforest | 69.93 ± 1.84 |
| MyFCD | mean | 0.01 ± 0.00 |
| MyFCD | group_median | 0.04 ± 0.00 |
| MyFCD | knn | 0.02 ± 0.00 |
| MyFCD | mice | 0.06 ± 0.00 |
| MyFCD | softimpute | 0.02 ± 0.00 |
| MyFCD | missforest | 8.12 ± 0.28 |
| MyFCD | crossdb | 0.84 ± 0.02 |
