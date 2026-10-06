# Inventario de datos descargados

Generado por `scripts/verify_data.py` el 2026-10-05 23:16 UTC para los anios 2026.

Criterio: un mes esta completo si la TLC lo publica, existe en `data/raw/`, su tamanio coincide byte a byte con el `Content-Length` del servidor y DuckDB puede leer sus metadatos Parquet.

## Resumen

| Taxi | Anio | Meses publicados | Meses locales OK | Filas |
|---|---|---:|---:|---:|
| yellow | 2026 | 8 | 8 | 29,703,355 |
| green | 2026 | 8 | 8 | 337,114 |

**Estado: COMPLETO**

## Detalle por archivo

| Taxi | Mes | Servidor | Bytes servidor | Bytes local | Filas | Veredicto |
|---|---|---|---:|---:|---:|---|
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
