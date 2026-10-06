# Resultados del benchmark Parquet vs tabla DuckDB

Generado por `scripts/benchmark.py` el 2026-10-06 01:15 UTC. DuckDB 1.5.5, 16 hilos, Linux x86_64. Tiempo = mediana de 5 ejecuciones despues de una primera ejecucion (que se reporta aparte). No editar a mano.

## Materializacion

| Escenario | Archivos | Filas | Parquet (MiB) | DuckDB (MiB) | Materializacion (s) |
|---|---:|---:|---:|---:|---:|
| 1_mes | 2 | 3,765,161 | 62 | 102 | 2.6 |
| 2026 | 16 | 30,040,469 | 496 | 816 | 10.2 |
| 2024+2026 | 40 | 71,870,407 | 1,172 | 1,940 | 21.9 |
| todos | 64 | 121,184,384 | 1,977 | 3,306 | 47.4 |

## Tiempo por consulta (mediana, segundos)

| Consulta | 1_mes Parquet | 1_mes tabla | 1_mes aceleracion | 2026 Parquet | 2026 tabla | 2026 aceleracion | 2024+2026 Parquet | 2024+2026 tabla | 2024+2026 aceleracion | todos Parquet | todos tabla | todos aceleracion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1_conteo_total | 0.080 | 0.000 | 398.5x | 0.178 | 0.000 | 445.7x | 0.286 | 0.000 | 1430.0x | 1.141 | 0.000 | 2853.0x |
| B2_viajes_por_mes | 0.380 | 0.044 | 8.7x | 1.280 | 0.269 | 4.8x | 2.629 | 0.603 | 4.4x | 4.230 | 0.903 | 4.7x |
| B3_demanda_hora_dia | 0.529 | 0.062 | 8.5x | 2.594 | 0.381 | 6.8x | 4.943 | 0.840 | 5.9x | 8.087 | 1.682 | 4.8x |
| B4_top_zonas | 0.321 | 0.052 | 6.2x | 1.437 | 0.290 | 4.9x | 2.804 | 0.894 | 3.1x | 4.415 | 1.317 | 3.4x |
| B5_propinas | 0.365 | 0.094 | 3.9x | 1.917 | 0.866 | 2.2x | 4.418 | 2.222 | 2.0x | 6.490 | 3.290 | 2.0x |
| B6_percentiles | 1.099 | 0.851 | 1.3x | 8.065 | 7.223 | 1.1x | 16.844 | 15.155 | 1.1x | 29.340 | 27.221 | 1.1x |
| B7_un_dia | 0.088 | 0.003 | 34.0x | 0.221 | 0.003 | 76.3x | 0.868 | 0.004 | 241.0x | 0.881 | 0.004 | 244.8x |
| B8_filas_completas | 0.928 | 0.327 | 2.8x | 2.360 | 0.842 | 2.8x | 4.247 | 1.098 | 3.9x | 6.635 | 1.513 | 4.4x |

## Primera ejecucion (segundos)

| Consulta | 1_mes Parquet | 1_mes tabla | 2026 Parquet | 2026 tabla | 2024+2026 Parquet | 2024+2026 tabla | todos Parquet | todos tabla |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B1_conteo_total | 0.104 | 0.001 | 0.208 | 0.002 | 0.417 | 0.005 | 0.458 | 0.006 |
| B2_viajes_por_mes | 0.528 | 0.188 | 1.458 | 1.107 | 3.146 | 2.639 | 4.248 | 4.353 |
| B3_demanda_hora_dia | 0.520 | 0.064 | 2.431 | 0.396 | 5.000 | 0.852 | 8.060 | 1.309 |
| B4_top_zonas | 0.328 | 0.075 | 1.431 | 0.354 | 3.059 | 1.035 | 4.422 | 1.528 |
| B5_propinas | 0.318 | 0.095 | 5.443 | 1.014 | 4.885 | 2.532 | 6.349 | 3.592 |
| B6_percentiles | 1.098 | 0.851 | 7.944 | 7.448 | 16.233 | 15.399 | 27.720 | 27.887 |
| B7_un_dia | 0.088 | 0.003 | 0.232 | 0.004 | 0.568 | 0.004 | 0.669 | 0.005 |
| B8_filas_completas | 0.920 | 0.373 | 2.468 | 1.205 | 4.620 | 1.948 | 6.989 | 2.978 |

## Total de las consultas (suma de medianas, segundos)

| Escenario | Parquet | Tabla | Aceleracion | Resultados identicos |
|---|---:|---:|---:|---|
| 1_mes | 3.79 | 1.43 | 2.6x | si |
| 2026 | 18.05 | 9.87 | 1.8x | si |
| 2024+2026 | 37.04 | 20.82 | 1.8x | si |
| todos | 61.22 | 35.93 | 1.7x | si |
