# Resultados del benchmark Parquet vs tabla DuckDB

Generado por `scripts/benchmark.py` el 2026-10-06 00:37 UTC. DuckDB 1.5.5, 16 hilos, Linux x86_64. Tiempo = mediana de 5 ejecuciones despues de una primera ejecucion (que se reporta aparte). No editar a mano.

## Materializacion

| Escenario | Archivos | Filas | Parquet (MiB) | DuckDB (MiB) | Materializacion (s) |
|---|---:|---:|---:|---:|---:|
| 1_mes | 2 | 3,765,161 | 62 | 102 | 2.3 |
| 2026 | 16 | 30,040,469 | 496 | 816 | 9.6 |
| 2024+2026 | 40 | 71,870,407 | 1,172 | 1,940 | 31.3 |

## Tiempo por consulta (mediana, segundos)

| Consulta | 1_mes Parquet | 1_mes tabla | 1_mes aceleracion | 2026 Parquet | 2026 tabla | 2026 aceleracion | 2024+2026 Parquet | 2024+2026 tabla | 2024+2026 aceleracion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1_conteo_total | 0.026 | 0.000 | 132.5x | 0.140 | 0.000 | 466.0x | 0.294 | 0.000 | 979.7x |
| B2_viajes_por_mes | 0.318 | 0.043 | 7.5x | 1.206 | 0.257 | 4.7x | 2.590 | 0.531 | 4.9x |
| B3_demanda_hora_dia | 0.501 | 0.062 | 8.0x | 2.282 | 0.379 | 6.0x | 4.936 | 0.785 | 6.3x |
| B4_top_zonas | 0.343 | 0.052 | 6.6x | 1.323 | 0.319 | 4.1x | 2.751 | 0.626 | 4.4x |
| B5_propinas | 0.355 | 0.095 | 3.7x | 1.823 | 0.946 | 1.9x | 4.343 | 2.111 | 2.1x |
| B6_percentiles | 0.911 | 0.632 | 1.4x | 6.015 | 5.080 | 1.2x | 12.214 | 10.495 | 1.2x |
| B7_un_dia | 0.092 | 0.003 | 28.8x | 0.222 | 0.003 | 74.0x | 0.982 | 0.003 | 288.8x |
| B8_filas_completas | 0.924 | 0.303 | 3.1x | 2.353 | 0.782 | 3.0x | 4.448 | 1.023 | 4.3x |

## Primera ejecucion (segundos)

| Consulta | 1_mes Parquet | 1_mes tabla | 2026 Parquet | 2026 tabla | 2024+2026 Parquet | 2024+2026 tabla |
|---|---:|---:|---:|---:|---:|---:|
| B1_conteo_total | 0.033 | 0.001 | 0.161 | 0.002 | 0.321 | 0.006 |
| B2_viajes_por_mes | 0.295 | 0.184 | 1.299 | 1.136 | 2.750 | 2.561 |
| B3_demanda_hora_dia | 0.555 | 0.066 | 2.280 | 0.381 | 4.976 | 0.791 |
| B4_top_zonas | 0.314 | 0.067 | 1.369 | 0.368 | 2.757 | 0.788 |
| B5_propinas | 0.344 | 0.108 | 1.757 | 1.018 | 4.353 | 2.585 |
| B6_percentiles | 0.895 | 0.644 | 5.794 | 4.978 | 11.916 | 11.089 |
| B7_un_dia | 0.097 | 0.004 | 0.242 | 0.004 | 0.547 | 0.004 |
| B8_filas_completas | 0.945 | 0.402 | 2.571 | 1.265 | 4.709 | 1.963 |

## Total de las consultas (suma de medianas, segundos)

| Escenario | Parquet | Tabla | Aceleracion | Resultados identicos |
|---|---:|---:|---:|---|
| 1_mes | 3.47 | 1.19 | 2.9x | si |
| 2026 | 15.36 | 7.77 | 2.0x | si |
| 2024+2026 | 32.56 | 15.58 | 2.1x | si |
