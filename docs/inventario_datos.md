# Inventario de datos descargados

Generado por `scripts/verify_data.py` el 2026-10-06 00:21 UTC para los anios 2024, 2026.

Criterio: un mes esta completo si la TLC lo publica, existe en `data/raw/`, su tamanio coincide byte a byte con el `Content-Length` del servidor y DuckDB puede leer sus metadatos Parquet.

## Resumen

| Taxi | Anio | Meses publicados | Meses locales OK | Filas |
|---|---|---:|---:|---:|
| yellow | 2024 | 12 | 12 | 41,169,720 |
| green | 2024 | 12 | 12 | 660,218 |
| yellow | 2026 | 8 | 8 | 29,703,355 |
| green | 2026 | 8 | 8 | 337,114 |

**Estado: COMPLETO**

## Detalle por archivo

| Taxi | Mes | Servidor | Bytes servidor | Bytes local | Filas | Veredicto |
|---|---|---|---:|---:|---:|---|
| yellow | 2024-01 | publicado | 49,961,641 | 49,961,641 | 2,964,624 | ok |
| yellow | 2024-02 | publicado | 50,349,284 | 50,349,284 | 3,007,526 | ok |
| yellow | 2024-03 | publicado | 60,078,280 | 60,078,280 | 3,582,628 | ok |
| yellow | 2024-04 | publicado | 59,133,625 | 59,133,625 | 3,514,289 | ok |
| yellow | 2024-05 | publicado | 62,553,128 | 62,553,128 | 3,723,833 | ok |
| yellow | 2024-06 | publicado | 59,859,922 | 59,859,922 | 3,539,193 | ok |
| yellow | 2024-07 | publicado | 52,299,432 | 52,299,432 | 3,076,903 | ok |
| yellow | 2024-08 | publicado | 51,067,350 | 51,067,350 | 2,979,183 | ok |
| yellow | 2024-09 | publicado | 61,170,186 | 61,170,186 | 3,633,030 | ok |
| yellow | 2024-10 | publicado | 64,346,071 | 64,346,071 | 3,833,771 | ok |
| yellow | 2024-11 | publicado | 60,658,709 | 60,658,709 | 3,646,369 | ok |
| yellow | 2024-12 | publicado | 61,524,085 | 61,524,085 | 3,668,371 | ok |
| green | 2024-01 | publicado | 1,362,284 | 1,362,284 | 56,551 | ok |
| green | 2024-02 | publicado | 1,283,805 | 1,283,805 | 53,577 | ok |
| green | 2024-03 | publicado | 1,372,372 | 1,372,372 | 57,457 | ok |
| green | 2024-04 | publicado | 1,346,502 | 1,346,502 | 56,471 | ok |
| green | 2024-05 | publicado | 1,453,912 | 1,453,912 | 61,003 | ok |
| green | 2024-06 | publicado | 1,326,194 | 1,326,194 | 54,748 | ok |
| green | 2024-07 | publicado | 1,250,973 | 1,250,973 | 51,837 | ok |
| green | 2024-08 | publicado | 1,267,079 | 1,267,079 | 51,771 | ok |
| green | 2024-09 | publicado | 1,326,186 | 1,326,186 | 54,440 | ok |
| green | 2024-10 | publicado | 1,353,731 | 1,353,731 | 56,147 | ok |
| green | 2024-11 | publicado | 1,264,688 | 1,264,688 | 52,222 | ok |
| green | 2024-12 | publicado | 1,312,306 | 1,312,306 | 53,994 | ok |
| yellow | 2026-01 | publicado | 64,165,080 | 64,165,080 | 3,724,889 | ok |
| yellow | 2026-02 | publicado | 58,683,353 | 58,683,353 | 3,399,866 | ok |
| yellow | 2026-03 | publicado | 67,891,249 | 67,891,249 | 3,952,451 | ok |
| yellow | 2026-04 | publicado | 64,818,115 | 64,818,115 | 3,831,240 | ok |
| yellow | 2026-05 | publicado | 69,699,174 | 69,699,174 | 4,090,836 | ok |
| yellow | 2026-06 | publicado | 65,465,637 | 65,465,637 | 3,837,248 | ok |
| yellow | 2026-07 | publicado | 61,685,033 | 61,685,033 | 3,530,109 | ok |
| yellow | 2026-08 | publicado | 59,043,961 | 59,043,961 | 3,336,716 | ok |
| yellow | 2026-09 | no_publicado | - | - | - | no publicado |
| yellow | 2026-10 | no_publicado | - | - | - | no publicado |
| yellow | 2026-11 | no_publicado | - | - | - | no publicado |
| yellow | 2026-12 | no_publicado | - | - | - | no publicado |
| green | 2026-01 | publicado | 991,656 | 991,656 | 40,272 | ok |
| green | 2026-02 | publicado | 920,753 | 920,753 | 37,373 | ok |
| green | 2026-03 | publicado | 1,082,530 | 1,082,530 | 44,208 | ok |
| green | 2026-04 | publicado | 1,075,896 | 1,075,896 | 44,238 | ok |
| green | 2026-05 | publicado | 1,102,947 | 1,102,947 | 44,921 | ok |
| green | 2026-06 | publicado | 1,075,836 | 1,075,836 | 44,163 | ok |
| green | 2026-07 | publicado | 1,018,250 | 1,018,250 | 41,252 | ok |
| green | 2026-08 | publicado | 1,007,530 | 1,007,530 | 40,687 | ok |
| green | 2026-09 | no_publicado | - | - | - | no publicado |
| green | 2026-10 | no_publicado | - | - | - | no publicado |
| green | 2026-11 | no_publicado | - | - | - | no publicado |
| green | 2026-12 | no_publicado | - | - | - | no publicado |
