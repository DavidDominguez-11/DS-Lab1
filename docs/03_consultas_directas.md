# Ejercicio 3 — Consultas directas sobre archivos Parquet

- **Consultas:** [`sql/03_exploracion.sql`](../sql/03_exploracion.sql) (cada consulta tiene nombre, objetivo y fuente).
- **Resultados completos (generados, con SQL y tiempos):** [`docs/resultados/03_exploracion.md`](resultados/03_exploracion.md).
- **Notebook:** [`notebooks/03_exploracion.ipynb`](../notebooks/03_exploracion.ipynb).
- **Reproducir:** `docker compose exec lab python scripts/sqlrun.py sql/03_exploracion.sql --md docs/resultados/03_exploracion.md`

Ninguna consulta crea tablas. Se usan cuatro funciones de DuckDB que leen los archivos en su lugar:

| Función | Qué lee |
|---|---|
| `glob('data/raw/*/2026/*.parquet')` | Solo el listado de archivos del sistema de archivos. |
| `parquet_file_metadata(...)` / `parquet_schema(...)` | Solo el *footer* de cada Parquet (metadatos: filas, row groups, esquema). No toca los datos. |
| `read_parquet(..., union_by_name = true, filename = true)` | Los datos, columna por columna, solo las columnas que la consulta necesita. |
| `SUMMARIZE SELECT * FROM read_parquet(...)` | Perfil estadístico de todas las columnas en una pasada. |

Las consultas de calidad (`calidad_*`) usan la vista `trips` de [`sql/00_vistas.sql`](../sql/00_vistas.sql), que **también es una
consulta directa sobre Parquet** (una vista no guarda datos; solo normaliza los nombres
`tpep_*`/`lpep_*` para poder comparar ambos tipos de taxi con una sola consulta).

## Documentación de cada consulta

| Consulta | Objetivo | Fuente | Resultado | Decisión tomada |
|---|---|---|---|---|
| `archivos_disponibles` | 3.1 Cantidad de archivos | `glob` sobre `data/raw/*/2026/*.parquet` | **16 archivos**: 8 yellow + 8 green, de 2026-01 a 2026-08 | Coincide con el inventario del Ej. 2; no faltan meses. |
| `registros_por_archivo` | 3.2 Filas por archivo sin leer datos | footer de cada archivo | Yellow: 3.3–4.1 M filas/mes (4 row groups). Green: 37–45 mil filas/mes (1 row group) | Los verdes son ~1% del volumen: en comparaciones se usarán **proporciones y promedios**, no totales. |
| `registros_totales` | 3.2 Cantidad total de registros | `read_parquet` sobre yellow, green y ambos | **29,703,355 yellow + 337,114 green = 30,040,469** | Confirma que el `COUNT(*)` coincide con los metadatos (DuckDB lo resuelve desde el footer en 0.08 s). |
| `columnas_y_tipos` | 3.3/3.4 Columnas y tipos | `DESCRIBE` de ambos conjuntos | 21 columnas yellow, 22 green; 18 comunes. Exclusivas yellow: `tpep_*`, `Airport_fee`. Exclusivas green: `lpep_*`, `ehail_fee`, `trip_type` | Se crea la vista `trips` con nombres unificados (`pickup_at`, `dropoff_at`, …). |
| `deriva_de_esquema` | 3.4/3.6 Columnas ausentes en algunos archivos | `parquet_schema` de cada archivo | `request_source` solo existe de **2026-06 a 2026-08** en ambos tipos | Todas las lecturas usan `union_by_name = true`. |
| `efecto_union_by_name` | 3.6 Demostrar el riesgo | `DESCRIBE` con y sin la opción | Sin la opción: 20 columnas, **sin** `request_source`, y sin ningún error ni advertencia | Ver problema de calidad #1. |
| `muestra_yellow`, `muestra_green` | 3.5 Muestra de registros | `read_parquet … USING SAMPLE reservoir(8 ROWS) REPEATABLE (42)` | 8 viajes de cada tipo (ver resultados). La semilla hace la muestra reproducible | En la muestra green ya aparece un viaje de 0 millas con tarifa cobrada. |
| `perfil_yellow`, `perfil_green` | 3.6 Rango, nulos y cardinalidad de cada columna | `SUMMARIZE` | Fechas desde 2001/2008, distancias de hasta 328,522 mi, montos negativos, 26% de nulos en 5 columnas yellow, `ehail_fee` 100% nulo | Origen de la lista de problemas de calidad. |
| `calidad_fechas` | 3.6 Fechas fuera de periodo y duraciones inválidas | vista `trips` | 146 yellow / 98 green fuera de su mes; 371,683 yellow con duración ≤ 0; 7,315 con > 6 h | Filtros de fecha y duración en `trips_clean`. |
| `calidad_valores` | 3.6 Distancias y montos imposibles | vista `trips` | 952,231 yellow con distancia 0; 161,835 con total negativo; 49 con total > $1,000 | Filtros de distancia y monto en `trips_clean`. |
| `calidad_nulos_por_tipo_pago` | 3.6 ¿Dónde se concentran los nulos? | vista `trips` | **El 100% de los nulos** está en yellow `payment_type = 0` (25.98%) y green `payment_type IS NULL` (14.47%) | Esos viajes **no se eliminan**: son viajes reales sin metadatos. Se excluyen solo de los análisis que requieren esas columnas (pasajeros, propinas). |
| `calidad_codigos_fuera_de_diccionario` | 3.6 Códigos no documentados | vista `trips` | 769,693 yellow con `RatecodeID = 99` (no definido); `ehail_fee` nunca tiene valor | `RatecodeID` 99 se agrupa como "desconocido"; `ehail_fee` se ignora. |
| `calidad_total_vs_componentes` | 3.6 ¿`total_amount` = suma de componentes? | vista `trips` (yellow) | Solo ~63% cuadra exactamente. Diferencias típicas: +2.50, −2.50, −3.25 | `total_amount` se usa tal como lo reporta la TLC; los análisis de recargos usan las columnas individuales. |
| `duplicados_exactos` | 3.6 Registros repetidos | vista `trips` | 7 duplicados yellow, 0 green | Irrelevante (7 de 29.7 M); no se deduplica. |
| `impacto_limpieza` | 3.6 Cuántos datos descarta `trips_clean` | vistas `trips` y `trips_clean` | Se descarta 4.94% yellow y 4.16% green | Pérdida aceptable; los filtros quedan documentados en `sql/00_vistas.sql`. |

## 3.6 Problemas de calidad de datos identificados

1. **Deriva de esquema entre meses.** `request_source` aparece en junio de 2026. Con
   `read_parquet('…/*.parquet')` sin opciones, DuckDB toma el esquema del **primer archivo** y
   descarta la columna en silencio (20 vs 21 columnas, sin error). Es el problema más
   peligroso porque no se nota. Solución: `union_by_name = true` en todas las lecturas.
2. **Esquemas distintos entre yellow y green.** Mismo concepto con distinto nombre
   (`tpep_pickup_datetime` vs `lpep_pickup_datetime`) y columnas exclusivas. Solución: vista `trips`.
3. **Registros sin metadatos (`payment_type = 0` en yellow, 26%).** `passenger_count`,
   `RatecodeID`, `store_and_fwd_flag`, `congestion_surcharge` y `Airport_fee` son NULL al mismo
   tiempo, la propina promedio es $0.40 (vs $4.28 con tarjeta). Según el diccionario de la TLC,
   el código 0 corresponde a viajes "Flex Fare"/sin dato de pago. En green el equivalente es
   `payment_type IS NULL` (14.5%).
4. **Fechas fuera del periodo.** Viajes de 2001 y 2008 dentro de archivos de 2026 (relojes mal
   configurados en el taxímetro), y viajes del último día del mes anterior.
5. **Duraciones imposibles.** 371,683 viajes yellow con `dropoff ≤ pickup` y miles de más de 6 h
   (máximo de dropoff: 1–2 días después del pickup).
6. **Distancias imposibles.** 3.2% de viajes yellow con 0 millas y máximos de 328,522 millas.
7. **Montos negativos.** ~162 mil viajes yellow con total negativo (hasta −$2,560): son
   anulaciones o reembolsos que se registran como un viaje "espejo".
8. **Códigos fuera del diccionario.** `RatecodeID = 99`; `payment_type = 5` aparece solo 2 veces.
9. **`total_amount` no siempre cuadra con sus componentes** (±2.50 = congestion surcharge,
   −3.25 = congestion + CBD fee), es decir, algunos recargos se registran en una columna pero no
   se suman al total, o viceversa.
10. **Columnas vacías.** `ehail_fee` es 100% nulo en green.
11. **Zonas desconocidas.** Unos 50 mil viajes yellow con `PULocationID` 264/265 (Unknown / Outside NYC).

**Decisión general:** no se modifica ni se reescribe ningún archivo crudo. La limpieza vive en
una vista (`trips_clean`), de modo que es **transparente, versionada y reversible**: cualquiera
puede ver exactamente qué se filtró y cambiar el criterio sin volver a descargar ni procesar nada.

## 3.9 ¿Qué significa consultar directamente un archivo Parquet?

Significa que el motor de consultas usa el archivo `.parquet` **como si fuera una tabla**, sin
un paso previo de importación (`CREATE TABLE … AS`, `COPY`, `INSERT`). DuckDB lee el archivo
en el momento de la consulta y no guarda una copia.

Por qué es útil con mucho volumen:

- **Formato columnar.** Parquet guarda cada columna por separado y comprimida. Una consulta
  que solo usa `trip_distance` lee solo esa columna (*projection pushdown*), no los 21 campos.
- **Metadatos en el footer.** Cada archivo trae número de filas y estadísticas min/max por
  *row group*. Por eso `COUNT(*)` sobre 30 M de filas tarda 0.08 s: DuckDB no lee ningún
  dato. Los filtros (`WHERE pickup_at >= …`) pueden saltar row groups completos cuyo
  rango min/max no aplica (*filter pushdown*).
- **Sin duplicar almacenamiento ni tiempo de carga.** Los ~500 MB de 2026 se consultan tal cual;
  no hay que esperar una importación ni mantener una segunda copia sincronizada.
- **Glob = conjunto de datos que crece solo.** `data/raw/yellow/*/*.parquet` incluye
  automáticamente cualquier archivo nuevo; el "esquema de la base" es la estructura de carpetas.
- **Fuera de memoria.** DuckDB procesa los archivos por bloques en paralelo (16 hilos aquí) y no
  necesita que el conjunto completo quepa en RAM, a diferencia de `pandas.read_parquet`.

El costo es que cada consulta vuelve a descomprimir y decodificar las columnas que usa; eso
se cuantifica en el Ejercicio 6.
