-- =============================================================================
-- Ejercicio 3: consultas directas sobre los archivos Parquet de 2026.
--
-- Ninguna consulta usa tablas: todas leen los .parquet con read_parquet(),
-- glob(), parquet_file_metadata() o parquet_schema().
-- Ejecutar: python scripts/sqlrun.py sql/03_exploracion.sql --md docs/resultados/03_exploracion.md
-- =============================================================================

-- name: archivos_disponibles
-- objetivo: 3.1 Cuantos archivos Parquet hay por tipo de taxi y anio
-- fuente: data/raw/*/2026/*.parquet (listado del sistema de archivos con glob)
SELECT
    split_part(file, '/', 3)                 AS taxi,
    split_part(file, '/', 4)                 AS anio,
    COUNT(*)                                 AS archivos,
    MIN(regexp_extract(file, '(\d{4}-\d{2})', 1)) AS primer_mes,
    MAX(regexp_extract(file, '(\d{4}-\d{2})', 1)) AS ultimo_mes
FROM glob('data/raw/*/2026/*.parquet')
GROUP BY ALL
ORDER BY taxi;

-- name: registros_por_archivo
-- objetivo: 3.2 Filas por archivo segun los metadatos Parquet (sin leer los datos)
-- fuente: data/raw/*/2026/*.parquet (pie de cada archivo)
SELECT
    regexp_extract(file_name, '(yellow|green)', 1)       AS taxi,
    regexp_extract(file_name, '(\d{4}-\d{2})', 1)        AS mes,
    num_rows                                             AS filas,
    num_row_groups                                       AS row_groups
FROM parquet_file_metadata('data/raw/*/2026/*.parquet')
ORDER BY taxi DESC, mes;

-- name: registros_totales
-- objetivo: 3.2 Total de registros por tipo de taxi leyendo los archivos
-- fuente: data/raw/yellow/2026/*.parquet y data/raw/green/2026/*.parquet
SELECT 'yellow' AS taxi, COUNT(*) AS registros FROM read_parquet('data/raw/yellow/2026/*.parquet')
UNION ALL
SELECT 'green', COUNT(*) FROM read_parquet('data/raw/green/2026/*.parquet')
UNION ALL
SELECT 'total', COUNT(*) FROM read_parquet('data/raw/*/2026/*.parquet', union_by_name = true);

-- name: columnas_y_tipos
-- objetivo: 3.3 y 3.4 Columnas y tipos de datos de cada tipo de taxi (lado a lado)
-- fuente: data/raw/yellow/2026/*.parquet y data/raw/green/2026/*.parquet
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

-- name: deriva_de_esquema
-- objetivo: 3.4/3.6 Columnas que NO estan en todos los archivos (cambios de esquema entre meses)
-- fuente: data/raw/*/2026/*.parquet (esquema fisico de cada archivo)
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

-- name: efecto_union_by_name
-- objetivo: 3.6 Mostrar que sin union_by_name DuckDB descarta columnas en silencio
-- fuente: data/raw/yellow/2026/*.parquet
SELECT 'sin union_by_name' AS lectura,
       COUNT(*) AS columnas,
       BOOL_OR(column_name = 'request_source') AS incluye_request_source
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet'))
UNION ALL
SELECT 'con union_by_name', COUNT(*), BOOL_OR(column_name = 'request_source')
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true));

-- name: muestra_yellow
-- objetivo: 3.5 Muestra aleatoria reproducible de viajes amarillos
-- fuente: data/raw/yellow/2026/*.parquet
SELECT tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance,
       PULocationID, DOLocationID, payment_type, fare_amount, tip_amount, total_amount,
       cbd_congestion_fee, request_source
FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true)
USING SAMPLE reservoir(8 ROWS) REPEATABLE (42);

-- name: muestra_green
-- objetivo: 3.5 Muestra aleatoria reproducible de viajes verdes
-- fuente: data/raw/green/2026/*.parquet
SELECT lpep_pickup_datetime, lpep_dropoff_datetime, passenger_count, trip_distance,
       PULocationID, DOLocationID, payment_type, trip_type, fare_amount, tip_amount,
       total_amount, ehail_fee
FROM read_parquet('data/raw/green/2026/*.parquet', union_by_name = true)
USING SAMPLE reservoir(8 ROWS) REPEATABLE (42);

-- name: perfil_yellow
-- objetivo: 3.6 Perfil estadistico de todas las columnas (min, max, nulos, cardinalidad)
-- fuente: data/raw/yellow/2026/*.parquet
SELECT column_name, column_type, min, max, approx_unique, null_percentage
FROM (SUMMARIZE SELECT * FROM read_parquet('data/raw/yellow/2026/*.parquet', union_by_name = true));

-- name: perfil_green
-- objetivo: 3.6 Perfil estadistico de todas las columnas (min, max, nulos, cardinalidad)
-- fuente: data/raw/green/2026/*.parquet
SELECT column_name, column_type, min, max, approx_unique, null_percentage
FROM (SUMMARIZE SELECT * FROM read_parquet('data/raw/green/2026/*.parquet', union_by_name = true));

-- name: calidad_fechas
-- objetivo: 3.6 Viajes con fechas fuera del mes del archivo o con duracion invalida
-- fuente: data/raw/*/2026/*.parquet (via vista trips de sql/00_vistas.sql)
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

-- name: calidad_valores
-- objetivo: 3.6 Distancias y montos imposibles o sospechosos
-- fuente: data/raw/*/2026/*.parquet (via vista trips)
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

-- name: calidad_nulos_por_tipo_pago
-- objetivo: 3.6 Ver si los nulos se concentran en algun tipo de pago
-- fuente: data/raw/*/2026/*.parquet (via vista trips)
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

-- name: calidad_codigos_fuera_de_diccionario
-- objetivo: 3.6 Valores de codigos no definidos en el diccionario de datos de la TLC
-- fuente: data/raw/*/2026/*.parquet (via vista trips)
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

-- name: calidad_total_vs_componentes
-- objetivo: 3.6 Verificar si total_amount coincide con la suma de sus componentes
-- fuente: data/raw/yellow/2026/*.parquet (via vista trips)
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

-- name: duplicados_exactos
-- objetivo: 3.6 Registros repetidos exactamente (todas las columnas iguales)
-- fuente: data/raw/*/2026/*.parquet (via vista trips)
SELECT taxi_type,
       COUNT(*)                                       AS registros,
       COUNT(*) - COUNT(DISTINCT (vendor_id, pickup_at, dropoff_at, passenger_count,
            trip_distance, pu_location_id, do_location_id, payment_type,
            fare_amount, tip_amount, total_amount))   AS duplicados
FROM trips
WHERE source_year = 2026
GROUP BY taxi_type;

-- name: impacto_limpieza
-- objetivo: 3.6 Cuantos registros sobreviven a los filtros de la vista trips_clean
-- fuente: data/raw/*/2026/*.parquet (vistas trips y trips_clean)
SELECT t.taxi_type,
       t.registros                                         AS crudos,
       c.registros                                         AS limpios,
       t.registros - c.registros                           AS descartados,
       ROUND(100.0 * (t.registros - c.registros) / t.registros, 2) AS pct_descartado
FROM (SELECT taxi_type, COUNT(*) AS registros FROM trips WHERE source_year = 2026 GROUP BY 1) t
JOIN (SELECT taxi_type, COUNT(*) AS registros FROM trips_clean WHERE source_year = 2026 GROUP BY 1) c
  USING (taxi_type)
ORDER BY crudos DESC;
