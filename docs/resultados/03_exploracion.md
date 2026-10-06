# Resultados de `sql/03_exploracion.sql`

Generado con `python scripts/sqlrun.py sql/03_exploracion.sql` (DuckDB 1.5.5). No editar a mano.

## `archivos_disponibles`

- **Objetivo:** 3.1 Cuantos archivos Parquet hay por tipo de taxi y anio
- **Fuente:** data/raw/*/2026/*.parquet (listado del sistema de archivos con glob)
- **Tiempo:** 0.02 s

```sql
SELECT
    split_part(file, '/', 3)                 AS taxi,
    split_part(file, '/', 4)                 AS anio,
    COUNT(*)                                 AS archivos,
    MIN(regexp_extract(file, '(\d{4}-\d{2})', 1)) AS primer_mes,
    MAX(regexp_extract(file, '(\d{4}-\d{2})', 1)) AS ultimo_mes
FROM glob('data/raw/*/2026/*.parquet')
GROUP BY ALL
ORDER BY taxi;
```

| taxi | anio | archivos | primer_mes | ultimo_mes |
|---|---|---|---|---|
| green | 2026 | 8 | 2026-01 | 2026-08 |
| yellow | 2026 | 8 | 2026-01 | 2026-08 |

## `registros_por_archivo`

- **Objetivo:** 3.2 Filas por archivo segun los metadatos Parquet (sin leer los datos)
- **Fuente:** data/raw/*/2026/*.parquet (pie de cada archivo)
- **Tiempo:** 0.03 s

```sql
SELECT
    regexp_extract(file_name, '(yellow|green)', 1)       AS taxi,
    regexp_extract(file_name, '(\d{4}-\d{2})', 1)        AS mes,
    num_rows                                             AS filas,
    num_row_groups                                       AS row_groups
FROM parquet_file_metadata('data/raw/*/2026/*.parquet')
ORDER BY taxi DESC, mes;
```

| taxi | mes | filas | row_groups |
|---|---|---|---|
| yellow | 2026-01 | 3,724,889 | 4 |
| yellow | 2026-02 | 3,399,866 | 4 |
| yellow | 2026-03 | 3,952,451 | 4 |
| yellow | 2026-04 | 3,831,240 | 4 |
| yellow | 2026-05 | 4,090,836 | 4 |
| yellow | 2026-06 | 3,837,248 | 4 |
| yellow | 2026-07 | 3,530,109 | 4 |
| yellow | 2026-08 | 3,336,716 | 4 |
| green | 2026-01 | 40,272 | 1 |
| green | 2026-02 | 37,373 | 1 |
| green | 2026-03 | 44,208 | 1 |
| green | 2026-04 | 44,238 | 1 |
| green | 2026-05 | 44,921 | 1 |
| green | 2026-06 | 44,163 | 1 |
| green | 2026-07 | 41,252 | 1 |
| green | 2026-08 | 40,687 | 1 |

## `registros_totales`

- **Objetivo:** 3.2 Total de registros por tipo de taxi leyendo los archivos
- **Fuente:** data/raw/yellow/2026/*.parquet y data/raw/green/2026/*.parquet
- **Tiempo:** 0.07 s

```sql
SELECT 'yellow' AS taxi, COUNT(*) AS registros FROM read_parquet('data/raw/yellow/2026/*.parquet')
UNION ALL
SELECT 'green', COUNT(*) FROM read_parquet('data/raw/green/2026/*.parquet')
UNION ALL
SELECT 'total', COUNT(*) FROM read_parquet('data/raw/*/2026/*.parquet', union_by_name = true);
```

| taxi | registros |
|---|---|
| yellow | 29,703,355 |
| green | 337,114 |
| total | 30,040,469 |

## `columnas_y_tipos`

- **Objetivo:** 3.3 y 3.4 Columnas y tipos de datos de cada tipo de taxi (lado a lado)
- **Fuente:** data/raw/yellow/2026/*.parquet y data/raw/green/2026/*.parquet
- **Tiempo:** 0.03 s

```sql
WITH y AS (
    SELECT column_name, column_type
    FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true))
), g AS (
    SELECT column_name, column_type
    FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/green/2026/*.parquet', union_by_name = true))
)
SELECT
    COALESCE(y.column_name, g.column_name) AS columna,
    y.column_type                          AS tipo_yellow,
    g.column_type                          AS tipo_green
FROM y FULL OUTER JOIN g USING (column_name)
ORDER BY (y.column_name IS NULL), (g.column_name IS NULL), columna;
```

| columna | tipo_yellow | tipo_green |
|---|---|---|
| DOLocationID | INTEGER | INTEGER |
| PULocationID | INTEGER | INTEGER |
| RatecodeID | BIGINT | BIGINT |
| VendorID | INTEGER | INTEGER |
| cbd_congestion_fee | DOUBLE | DOUBLE |
| congestion_surcharge | DOUBLE | DOUBLE |
| extra | DOUBLE | DOUBLE |
| fare_amount | DOUBLE | DOUBLE |
| improvement_surcharge | DOUBLE | DOUBLE |
| mta_tax | DOUBLE | DOUBLE |
| passenger_count | BIGINT | BIGINT |
| payment_type | BIGINT | BIGINT |
| request_source | VARCHAR | VARCHAR |
| store_and_fwd_flag | VARCHAR | VARCHAR |
| tip_amount | DOUBLE | DOUBLE |
| tolls_amount | DOUBLE | DOUBLE |
| total_amount | DOUBLE | DOUBLE |
| trip_distance | DOUBLE | DOUBLE |
| Airport_fee | DOUBLE | NULL |
| tpep_dropoff_datetime | TIMESTAMP | NULL |
| tpep_pickup_datetime | TIMESTAMP | NULL |
| ehail_fee | NULL | DOUBLE |
| lpep_dropoff_datetime | NULL | TIMESTAMP |
| lpep_pickup_datetime | NULL | TIMESTAMP |
| trip_type | NULL | BIGINT |

## `deriva_de_esquema`

- **Objetivo:** 3.4/3.6 Columnas que NO estan en todos los archivos (cambios de esquema entre meses)
- **Fuente:** data/raw/*/2026/*.parquet (esquema fisico de cada archivo)
- **Tiempo:** 0.03 s

```sql
WITH s AS (
    SELECT regexp_extract(file_name, '(yellow|green)', 1)  AS taxi,
           regexp_extract(file_name, '(\d{4}-\d{2})', 1)   AS mes,
           name                                            AS columna
    FROM parquet_schema('data/raw/*/2026/*.parquet')
    WHERE name NOT IN ('schema', 'duckdb_schema')
), archivos AS (
    SELECT taxi, COUNT(DISTINCT mes) AS total FROM s GROUP BY taxi
)
SELECT s.taxi, s.columna, COUNT(*) AS archivos_con_columna, a.total AS archivos_totales,
       MIN(s.mes) AS desde, MAX(s.mes) AS hasta
FROM s JOIN archivos a USING (taxi)
GROUP BY ALL
HAVING COUNT(*) < a.total
ORDER BY s.taxi, s.columna;
```

| taxi | columna | archivos_con_columna | archivos_totales | desde | hasta |
|---|---|---|---|---|---|
| green | request_source | 3 | 8 | 2026-06 | 2026-08 |
| yellow | request_source | 3 | 8 | 2026-06 | 2026-08 |

## `efecto_union_by_name`

- **Objetivo:** 3.6 Mostrar que sin union_by_name DuckDB descarta columnas en silencio
- **Fuente:** data/raw/yellow/2026/*.parquet
- **Tiempo:** 0.03 s

```sql
SELECT 'sin union_by_name' AS lectura,
       COUNT(*) AS columnas,
       BOOL_OR(column_name = 'request_source') AS incluye_request_source
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet'))
UNION ALL
SELECT 'con union_by_name', COUNT(*), BOOL_OR(column_name = 'request_source')
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true));
```

| lectura | columnas | incluye_request_source |
|---|---|---|
| sin union_by_name | 20 | no |
| con union_by_name | 21 | si |

## `muestra_yellow`

- **Objetivo:** 3.5 Muestra aleatoria reproducible de viajes amarillos
- **Fuente:** data/raw/yellow/2026/*.parquet
- **Tiempo:** 0.17 s

```sql
SELECT tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance,
       PULocationID, DOLocationID, payment_type, fare_amount, tip_amount, total_amount,
       cbd_congestion_fee, request_source
FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true)
USING SAMPLE reservoir(8 ROWS) REPEATABLE (42);
```

| tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | PULocationID | DOLocationID | payment_type | fare_amount | tip_amount | total_amount | cbd_congestion_fee | request_source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01-01 00:24:41 | 2026-01-01 00:36:23 | 1 | 4.8 | 87 | 162 | 2 | 21.2 | 0 | 26.95 | 0.75 | NULL |
| 2026-01-01 02:08:35 | 2026-01-01 02:21:22 | 2 | 2.3 | 90 | 229 | 1 | 14.2 | 1.4 | 21.35 | 0.75 | NULL |
| 2026-01-01 02:01:56 | 2026-01-01 02:17:20 | 1 | 5.69 | 80 | 95 | 2 | 26.1 | 0 | 28.6 | 0 | NULL |
| 2026-01-01 04:36:54 | 2026-01-01 04:48:35 | 1 | 2.56 | 68 | 79 | 1 | 14.2 | 3.99 | 23.94 | 0.75 | NULL |
| 2026-01-01 09:37:17 | 2026-01-01 09:42:10 | 1 | 0.8 | 239 | 142 | 1 | 6.5 | 2.1 | 12.6 | 0 | NULL |
| 2026-01-01 11:29:34 | 2026-01-01 11:36:19 | 1 | 0.74 | 161 | 163 | 1 | 7.9 | 3.16 | 15.81 | 0.75 | NULL |
| 2026-01-01 11:42:55 | 2026-01-01 11:49:37 | 1 | 1.03 | 163 | 186 | 2 | 7.9 | 0 | 12.65 | 0.75 | NULL |
| 2026-01-01 13:36:51 | 2026-01-01 13:45:33 | 1 | 0.8 | 186 | 48 | 2 | 8.6 | 0 | 13.35 | 0.75 | NULL |

## `muestra_green`

- **Objetivo:** 3.5 Muestra aleatoria reproducible de viajes verdes
- **Fuente:** data/raw/green/2026/*.parquet
- **Tiempo:** 0.08 s

```sql
SELECT lpep_pickup_datetime, lpep_dropoff_datetime, passenger_count, trip_distance,
       PULocationID, DOLocationID, payment_type, trip_type, fare_amount, tip_amount,
       total_amount, ehail_fee
FROM read_parquet('data/raw/green/2026/*.parquet', union_by_name = true)
USING SAMPLE reservoir(8 ROWS) REPEATABLE (42);
```

| lpep_pickup_datetime | lpep_dropoff_datetime | passenger_count | trip_distance | PULocationID | DOLocationID | payment_type | trip_type | fare_amount | tip_amount | total_amount | ehail_fee |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01-03 17:06:05 | 2026-01-03 17:11:27 | 1 | 1.15 | 74 | 41 | 1 | 1 | 7.2 | 4 | 12.7 | NULL |
| 2026-01-11 22:28:43 | 2026-01-11 22:32:53 | 2 | 0 | 74 | 42 | 1 | 1 | 5.8 | 1.66 | 9.96 | NULL |
| 2026-01-13 18:36:59 | 2026-01-13 18:41:12 | 1 | 1.08 | 43 | 238 | 1 | 1 | 7.2 | 3.49 | 17.44 | NULL |
| 2026-01-16 15:15:45 | 2026-01-16 15:43:34 | 1 | 9.39 | 244 | 233 | 2 | 1 | 38 | 0 | 43 | NULL |
| 2026-01-20 15:12:55 | 2026-01-20 15:24:05 | 1 | 1.4 | 82 | 82 | 2 | 1 | 11.4 | 0 | 12.9 | NULL |
| 2026-01-23 10:19:05 | 2026-01-23 10:37:24 | 1 | 3.02 | 74 | 238 | 1 | 1 | 18.4 | 4.53 | 27.18 | NULL |
| 2026-01-24 15:40:48 | 2026-01-24 15:52:07 | 1 | 1.05 | 65 | 40 | 1 | 1 | 10.7 | 1.59 | 13.79 | NULL |
| 2026-01-30 00:16:28 | 2026-01-30 00:23:47 | 1 | 1.36 | 75 | 238 | 1 | 1 | 9.3 | 1.77 | 13.57 | NULL |

## `perfil_yellow`

- **Objetivo:** 3.6 Perfil estadistico de todas las columnas (min, max, nulos, cardinalidad)
- **Fuente:** data/raw/yellow/2026/*.parquet
- **Tiempo:** 7.42 s

```sql
SELECT column_name, column_type, min, max, approx_unique, null_percentage
FROM (SUMMARIZE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true));
```

| column_name | column_type | min | max | approx_unique | null_percentage |
|---|---|---|---|---|---|
| VendorID | INTEGER | 1 | 7 | 4 | 0.00 |
| tpep_pickup_datetime | TIMESTAMP | 2001-01-01 09:23:58 | 2026-08-31 23:59:59 | 16,867,928 | 0.00 |
| tpep_dropoff_datetime | TIMESTAMP | 2001-01-01 16:09:38 | 2026-09-01 20:16:00 | 16,587,125 | 0.00 |
| passenger_count | BIGINT | 0 | 9 | 11 | 25.98 |
| trip_distance | DOUBLE | 0.0 | 328522.2 | 7217 | 0.00 |
| RatecodeID | BIGINT | 1 | 99 | 7 | 25.98 |
| store_and_fwd_flag | VARCHAR | N | Y | 2 | 25.98 |
| PULocationID | INTEGER | 1 | 265 | 290 | 0.00 |
| DOLocationID | INTEGER | 1 | 265 | 298 | 0.00 |
| payment_type | BIGINT | 0 | 5 | 6 | 0.00 |
| fare_amount | DOUBLE | -2555.2 | 7045.0 | 18,028 | 0.00 |
| extra | DOUBLE | -7.5 | 244.35 | 360 | 0.00 |
| mta_tax | DOUBLE | -0.5 | 11.5 | 21 | 0.00 |
| tip_amount | DOUBLE | -222.0 | 766.0 | 6049 | 0.00 |
| tolls_amount | DOUBLE | -129.48 | 1400.0 | 3451 | 0.00 |
| improvement_surcharge | DOUBLE | -1.0 | 4.0 | 6 | 0.00 |
| total_amount | DOUBLE | -2560.2 | 7053.5 | 38,649 | 0.00 |
| congestion_surcharge | DOUBLE | -2.5 | 2.75 | 7 | 25.98 |
| Airport_fee | DOUBLE | -2.0 | 27.0 | 15 | 25.98 |
| cbd_congestion_fee | DOUBLE | -0.75 | 0.75 | 3 | 0.00 |
| request_source | VARCHAR | A | HV0005 | 3 | 90.23 |

## `perfil_green`

- **Objetivo:** 3.6 Perfil estadistico de todas las columnas (min, max, nulos, cardinalidad)
- **Fuente:** data/raw/green/2026/*.parquet
- **Tiempo:** 0.21 s

```sql
SELECT column_name, column_type, min, max, approx_unique, null_percentage
FROM (SUMMARIZE SELECT * FROM read_parquet('data/raw/green/2026/*.parquet', union_by_name = true));
```

| column_name | column_type | min | max | approx_unique | null_percentage |
|---|---|---|---|---|---|
| VendorID | INTEGER | 1 | 6 | 3 | 0.00 |
| lpep_pickup_datetime | TIMESTAMP | 2008-12-31 17:35:31 | 2026-08-31 23:58:28 | 332,702 | 0.00 |
| lpep_dropoff_datetime | TIMESTAMP | 2008-12-31 23:16:26 | 2026-09-02 09:39:37 | 396,286 | 0.00 |
| store_and_fwd_flag | VARCHAR | N | Y | 2 | 14.47 |
| RatecodeID | BIGINT | 1 | 99 | 7 | 14.47 |
| PULocationID | INTEGER | 1 | 265 | 263 | 0.00 |
| DOLocationID | INTEGER | 1 | 265 | 266 | 0.00 |
| passenger_count | BIGINT | 0 | 9 | 11 | 14.47 |
| trip_distance | DOUBLE | 0.0 | 179830.92 | 2472 | 0.00 |
| fare_amount | DOUBLE | -500.0 | 1676.7 | 4808 | 0.00 |
| extra | DOUBLE | -7.5 | 10.0 | 21 | 0.00 |
| mta_tax | DOUBLE | -0.5 | 5.0 | 7 | 0.00 |
| tip_amount | DOUBLE | -14.0 | 495.0 | 2212 | 0.00 |
| tolls_amount | DOUBLE | -24.5 | 85.0 | 75 | 0.00 |
| ehail_fee | DOUBLE | NULL | NULL | 0 | 100.00 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 5 | 0.00 |
| total_amount | DOUBLE | -501.5 | 1678.2 | 8186 | 0.00 |
| payment_type | BIGINT | 1 | 4 | 4 | 14.47 |
| trip_type | BIGINT | 1 | 2 | 2 | 14.47 |
| congestion_surcharge | DOUBLE | -2.75 | 2.75 | 5 | 14.47 |
| cbd_congestion_fee | DOUBLE | -0.75 | 0.75 | 3 | 0.00 |
| request_source | VARCHAR | A | HV0005 | 2 | 94.30 |

## `calidad_fechas`

- **Objetivo:** 3.6 Viajes con fechas fuera del mes del archivo o con duracion invalida
- **Fuente:** data/raw/*/2026/*.parquet (via vista trips de sql/00_vistas.sql)
- **Tiempo:** 2.20 s

```sql
SELECT
    taxi_type,
    COUNT(*)                                                          AS registros,
    MIN(pickup_at)                                                    AS pickup_min,
    MAX(pickup_at)                                                    AS pickup_max,
    COUNT(*) FILTER (WHERE year(pickup_at) <> source_year
                        OR month(pickup_at) <> source_month)          AS fuera_de_su_mes,
    COUNT(*) FILTER (WHERE dropoff_at <= pickup_at)                   AS duracion_cero_o_negativa,
    COUNT(*) FILTER (WHERE dropoff_at > pickup_at + INTERVAL 6 HOUR)  AS duracion_mayor_6h
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type;
```

| taxi_type | registros | pickup_min | pickup_max | fuera_de_su_mes | duracion_cero_o_negativa | duracion_mayor_6h |
|---|---|---|---|---|---|---|
| green | 337,114 | 2008-12-31 17:35:31 | 2026-08-31 23:58:28 | 98 | 234 | 1104 |
| yellow | 29,703,355 | 2001-01-01 09:23:58 | 2026-08-31 23:59:59 | 146 | 371,683 | 7315 |

## `calidad_valores`

- **Objetivo:** 3.6 Distancias y montos imposibles o sospechosos
- **Fuente:** data/raw/*/2026/*.parquet (via vista trips)
- **Tiempo:** 1.55 s

```sql
SELECT
    taxi_type,
    COUNT(*) FILTER (WHERE trip_distance = 0)          AS distancia_cero,
    COUNT(*) FILTER (WHERE trip_distance > 100)        AS distancia_mayor_100mi,
    MAX(trip_distance)                                 AS distancia_max,
    COUNT(*) FILTER (WHERE fare_amount < 0)            AS tarifa_negativa,
    COUNT(*) FILTER (WHERE total_amount < 0)           AS total_negativo,
    MIN(total_amount)                                  AS total_min,
    COUNT(*) FILTER (WHERE total_amount > 1000)        AS total_mayor_1000,
    MAX(total_amount)                                  AS total_max,
    COUNT(*) FILTER (WHERE passenger_count = 0)        AS pasajeros_cero,
    COUNT(*) FILTER (WHERE pu_location_id IN (264, 265)) AS zona_origen_desconocida
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type;
```

| taxi_type | distancia_cero | distancia_mayor_100mi | distancia_max | tarifa_negativa | total_negativo | total_min | total_mayor_1000 | total_max | pasajeros_cero | zona_origen_desconocida |
|---|---|---|---|---|---|---|---|---|---|---|
| green | 12,212 | 72 | 179,830.92 | 999 | 1023 | -501.5 | 1 | 1,678.2 | 4527 | 1131 |
| yellow | 952,231 | 1223 | 328,522.2 | 157,364 | 161,835 | -2,560.2 | 49 | 7,053.5 | 91,359 | 49,676 |

## `calidad_nulos_por_tipo_pago`

- **Objetivo:** 3.6 Ver si los nulos se concentran en algun tipo de pago
- **Fuente:** data/raw/*/2026/*.parquet (via vista trips)
- **Tiempo:** 0.83 s

```sql
SELECT
    taxi_type,
    payment_type,
    COUNT(*)                                                  AS registros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct,
    ROUND(100.0 * AVG((passenger_count IS NULL)::INT), 1)     AS pct_pasajeros_nulo,
    ROUND(100.0 * AVG((ratecode_id IS NULL)::INT), 1)         AS pct_ratecode_nulo,
    ROUND(100.0 * AVG((congestion_surcharge IS NULL)::INT), 1) AS pct_congestion_nulo,
    ROUND(AVG(tip_amount), 2)                                 AS propina_prom
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type, payment_type
ORDER BY taxi_type DESC, payment_type NULLS LAST;
```

| taxi_type | payment_type | registros | pct | pct_pasajeros_nulo | pct_ratecode_nulo | pct_congestion_nulo | propina_prom |
|---|---|---|---|---|---|---|---|
| yellow | 0 | 7,716,688 | 25.98 | 100 | 100 | 100 | 0.4 |
| yellow | 1 | 18,941,008 | 63.77 | 0 | 0 | 0 | 4.28 |
| yellow | 2 | 2,708,031 | 9.12 | 0 | 0 | 0 | 0 |
| yellow | 3 | 98,138 | 0.33 | 0 | 0 | 0 | 0 |
| yellow | 4 | 239,488 | 0.81 | 0 | 0 | 0 | 0 |
| yellow | 5 | 2 | 0 | 0 | 0 | 0 | 0 |
| green | 1 | 219,980 | 65.25 | 0 | 0 | 0 | 3.84 |
| green | 2 | 65,921 | 19.55 | 0 | 0 | 0 | 0 |
| green | 3 | 1688 | 0.5 | 0 | 0 | 0 | 0 |
| green | 4 | 750 | 0.22 | 0 | 0 | 0 | 0 |
| green | NULL | 48,775 | 14.47 | 100 | 100 | 100 | 0.79 |

## `calidad_codigos_fuera_de_diccionario`

- **Objetivo:** 3.6 Valores de codigos no definidos en el diccionario de datos de la TLC
- **Fuente:** data/raw/*/2026/*.parquet (via vista trips)
- **Tiempo:** 0.48 s

```sql
SELECT
    taxi_type,
    COUNT(*) FILTER (WHERE ratecode_id = 99)                         AS ratecode_99,
    COUNT(*) FILTER (WHERE ratecode_id NOT IN (1,2,3,4,5,6,99))      AS ratecode_otro,
    COUNT(*) FILTER (WHERE vendor_id NOT IN (1,2,6,7))               AS vendor_desconocido,
    COUNT(*) FILTER (WHERE payment_type NOT IN (0,1,2,3,4,5,6))      AS payment_otro,
    COUNT(*) FILTER (WHERE taxi_type = 'green' AND trip_type IS NULL AND payment_type IS NOT NULL) AS trip_type_nulo,
    COUNT(ehail_fee)                                                 AS ehail_fee_no_nulo
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type;
```

| taxi_type | ratecode_99 | ratecode_otro | vendor_desconocido | payment_otro | trip_type_nulo | ehail_fee_no_nulo |
|---|---|---|---|---|---|---|
| green | 2 | 0 | 0 | 0 | 2 | 0 |
| yellow | 769,693 | 0 | 0 | 0 | 0 | 0 |

## `calidad_total_vs_componentes`

- **Objetivo:** 3.6 Verificar si total_amount coincide con la suma de sus componentes
- **Fuente:** data/raw/yellow/2026/*.parquet (via vista trips)
- **Tiempo:** 1.85 s

```sql
SELECT
    payment_type,
    ROUND(total_amount - (fare_amount + extra + mta_tax + tip_amount + tolls_amount
          + improvement_surcharge + COALESCE(congestion_surcharge, 0)
          + COALESCE(airport_fee, 0) + COALESCE(cbd_congestion_fee, 0)), 2) AS diferencia,
    COUNT(*) AS registros
FROM trips
WHERE source_year = 2026 AND taxi_type = 'yellow'
GROUP BY 1, 2
QUALIFY ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) <= 10
ORDER BY registros DESC;
```

| payment_type | diferencia | registros |
|---|---|---|
| 1 | 0 | 15,469,459 |
| 0 | 2.5 | 4,747,991 |
| 1 | -3.25 | 2,440,215 |
| 2 | 0 | 2,269,576 |
| 0 | 0 | 812,122 |
| 1 | -2.5 | 646,881 |
| 2 | -3.25 | 294,687 |
| 4 | 0 | 209,877 |
| 0 | 5.5 | 112,169 |
| 0 | 3.5 | 86,542 |

## `duplicados_exactos`

- **Objetivo:** 3.6 Registros repetidos exactamente (todas las columnas iguales)
- **Fuente:** data/raw/*/2026/*.parquet (via vista trips)
- **Tiempo:** 4.60 s

```sql
SELECT taxi_type,
       COUNT(*)                                       AS registros,
       COUNT(*) - COUNT(DISTINCT (vendor_id, pickup_at, dropoff_at, passenger_count,
            trip_distance, pu_location_id, do_location_id, payment_type,
            fare_amount, tip_amount, total_amount))   AS duplicados
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type;
```

| taxi_type | registros | duplicados |
|---|---|---|
| green | 337,114 | 0 |
| yellow | 29,703,355 | 7 |

## `impacto_limpieza`

- **Objetivo:** 3.6 Cuantos registros sobreviven a los filtros de la vista trips_clean
- **Fuente:** data/raw/*/2026/*.parquet (vistas trips y trips_clean)
- **Tiempo:** 3.46 s

```sql
SELECT t.taxi_type,
       t.registros                                         AS crudos,
       c.registros                                         AS limpios,
       t.registros - c.registros                           AS descartados,
       ROUND(100.0 * (t.registros - c.registros) / t.registros, 2) AS pct_descartado
FROM (SELECT taxi_type, COUNT(*) AS registros FROM trips WHERE source_year = 2026 GROUP BY 1) t
JOIN (SELECT taxi_type, COUNT(*) AS registros FROM trips_clean WHERE source_year = 2026 GROUP BY 1) c
  USING (taxi_type)
ORDER BY crudos DESC;
```

| taxi_type | crudos | limpios | descartados | pct_descartado |
|---|---|---|---|---|
| yellow | 29,703,355 | 28,596,404 | 1,106,951 | 3.73 |
| green | 337,114 | 323,096 | 14,018 | 4.16 |
