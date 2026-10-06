-- =============================================================================
-- Ejercicios 5 y 8: validar la incorporacion de nuevos anios.
--
-- Ninguna consulta menciona un anio concreto: se ejecutan igual despues de
-- incorporar 2024 (Ej. 5) y 2025 (Ej. 8) y muestran todos los anios presentes.
-- Ejecutar: python scripts/sqlrun.py sql/05_validacion_incorporacion.sql --md docs/resultados/05_validacion_incorporacion.md
-- =============================================================================

-- name: archivos_por_anio
-- objetivo: Archivos presentes por tipo y anio, con el rango de meses (5.5)
-- fuente: glob('data/raw/*/*/*.parquet')
SELECT
    split_part(file, '/', 4)                                  AS anio,
    split_part(file, '/', 3)                                  AS taxi,
    COUNT(*)                                                  AS archivos,
    MIN(regexp_extract(file, '-(\d{2})\.parquet', 1))         AS primer_mes,
    MAX(regexp_extract(file, '-(\d{2})\.parquet', 1))         AS ultimo_mes
FROM glob('data/raw/*/*/*.parquet')
GROUP BY ALL
ORDER BY anio, taxi DESC;

-- name: filas_metadatos_vs_lectura
-- objetivo: Las filas declaradas en los metadatos coinciden con las que lee la vista trips (5.5)
-- fuente: parquet_file_metadata('data/raw/*/*/*.parquet') y vista trips
WITH meta AS (
    SELECT regexp_extract(file_name, '(yellow|green)', 1)                 AS taxi_type,
           CAST(regexp_extract(file_name, '_(\d{4})-', 1) AS INTEGER)     AS anio,
           SUM(num_rows)                                                  AS filas_metadatos
    FROM parquet_file_metadata('data/raw/*/*/*.parquet')
    GROUP BY ALL
), lectura AS (
    SELECT taxi_type, source_year AS anio, COUNT(*) AS filas_leidas
    FROM trips GROUP BY ALL
)
SELECT m.anio, m.taxi_type, m.filas_metadatos, l.filas_leidas,
       m.filas_metadatos = l.filas_leidas AS coincide
FROM meta m JOIN lectura l USING (taxi_type, anio)
ORDER BY m.anio, m.taxi_type DESC;

-- name: columnas_por_anio
-- objetivo: Columnas que no existen en todos los anios (deriva de esquema entre anios) (5.7)
-- fuente: parquet_schema('data/raw/*/*/*.parquet')
WITH s AS (
    SELECT DISTINCT
        regexp_extract(file_name, '(yellow|green)', 1)  AS taxi,
        regexp_extract(file_name, '_(\d{4})-', 1)       AS anio,
        name                                            AS columna,
        type                                            AS tipo_fisico
    FROM parquet_schema('data/raw/*/*/*.parquet')
    WHERE name NOT IN ('schema', 'duckdb_schema')
)
SELECT taxi, columna,
       string_agg(DISTINCT anio, ', ' ORDER BY anio)         AS anios_presente,
       string_agg(DISTINCT tipo_fisico, ', ')                AS tipos_fisicos
FROM s
GROUP BY taxi, columna
HAVING COUNT(DISTINCT anio) < (SELECT COUNT(DISTINCT anio) FROM s)
    OR COUNT(DISTINCT tipo_fisico) > 1
ORDER BY taxi DESC, columna;

-- name: riesgo_sin_union_by_name
-- objetivo: Que columnas se perderian leyendo todos los anios sin union_by_name (5.7)
-- fuente: data/raw/yellow/*/*.parquet
SELECT 'sin union_by_name' AS lectura, COUNT(*) AS columnas,
       BOOL_OR(column_name = 'cbd_congestion_fee') AS incluye_cbd_fee,
       BOOL_OR(column_name = 'request_source')     AS incluye_request_source
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet'))
UNION ALL
SELECT 'con union_by_name', COUNT(*),
       BOOL_OR(column_name = 'cbd_congestion_fee'), BOOL_OR(column_name = 'request_source')
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true));

-- name: nulos_estructurales_por_anio
-- objetivo: Columnas nuevas quedan en NULL (no en 0) para los anios en que no existian (5.7)
-- fuente: vista trips
SELECT
    source_year                                                AS anio,
    taxi_type,
    COUNT(*)                                                   AS registros,
    ROUND(100.0 * AVG((cbd_congestion_fee IS NULL)::INT), 2)   AS pct_cbd_fee_nulo,
    ROUND(100.0 * AVG((request_source IS NULL)::INT), 2)       AS pct_request_source_nulo
FROM trips
GROUP BY ALL
ORDER BY anio, taxi_type DESC;

-- name: consulta_conjunta_rango_fechas
-- objetivo: Consulta conjunta sobre todos los anios: rango de fechas y registros por anio (5.6)
-- fuente: vista trips_clean (todos los Parquet)
SELECT
    source_year                   AS anio,
    taxi_type,
    COUNT(*)                      AS viajes_limpios,
    MIN(pickup_at)                AS primer_viaje,
    MAX(pickup_at)                AS ultimo_viaje,
    COUNT(DISTINCT source_month)  AS meses
FROM trips_clean
GROUP BY ALL
ORDER BY anio, taxi_type DESC;

-- name: comparacion_mismo_mes_entre_anios
-- objetivo: Consulta conjunta: viajes por dia en el mismo mes de cada anio (solo meses presentes en todos los anios) (5.6)
-- fuente: vista trips_clean (todos los Parquet)
WITH m AS (
    SELECT source_year AS anio, source_month AS mes, taxi_type,
           COUNT(*) / COUNT(DISTINCT pickup_date) AS viajes_por_dia
    FROM trips_clean
    GROUP BY ALL
), comunes AS (
    SELECT mes FROM m GROUP BY mes
    HAVING COUNT(DISTINCT anio) = (SELECT COUNT(DISTINCT anio) FROM m)
)
PIVOT (SELECT * FROM m WHERE mes IN (SELECT mes FROM comunes))
ON anio USING ROUND(ANY_VALUE(viajes_por_dia), 0)
GROUP BY taxi_type, mes
ORDER BY taxi_type DESC, mes;
