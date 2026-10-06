-- =============================================================================
-- Ejercicio 6: consultas del benchmark Parquet vs tabla DuckDB.
--
-- El texto de cada consulta es IDENTICO para ambas estrategias: solo cambia
-- que `trips` / `zones` sean vistas sobre Parquet (sql/00_vistas.sql) o tablas
-- materializadas (scripts/build_database.py). `trips_clean` se define igual en
-- los dos casos (sql/01_vistas_analisis.sql).
--
-- Se eligieron para cubrir patrones distintos de acceso:
--   B1 conteo total              -> metadatos / escaneo minimo
--   B2 agregacion temporal       -> 2 columnas + filtros de limpieza
--   B3 heatmap hora x dia        -> agregacion con COUNT DISTINCT y join
--   B4 top zonas con join        -> join con dimension + ventana
--   B5 propinas (filtro + agg)   -> varias columnas numericas filtradas
--   B6 percentiles               -> agregacion pesada (cuantiles exactos)
--   B7 filtro muy selectivo      -> un solo dia (aprovecha min/max por bloque)
--   B8 SELECT de muchas columnas -> leer filas completas (top 100 mil por monto)
-- Ejecutar: python scripts/benchmark.py
-- =============================================================================

-- name: B1_conteo_total
-- objetivo: Contar todos los registros crudos
SELECT COUNT(*) AS registros FROM trips;

-- name: B2_viajes_por_mes
-- objetivo: Viajes e ingreso por mes y tipo (= viajes_por_mes del Ej. 4)
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       COUNT(*) AS viajes, ROUND(SUM(total_amount) / 1e6, 2) AS ingreso_musd
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;

-- name: B3_demanda_hora_dia
-- objetivo: Viajes promedio por hora y dia de la semana (= demanda_hora_dia del Ej. 4)
WITH dias AS (
    SELECT pickup_dow, COUNT(DISTINCT pickup_date) AS n_dias FROM trips_clean GROUP BY 1
)
SELECT t.pickup_dow, t.pickup_hour, ROUND(COUNT(*) / ANY_VALUE(d.n_dias), 0) AS viajes
FROM trips_clean t JOIN dias d USING (pickup_dow)
GROUP BY ALL ORDER BY 1, 2;

-- name: B4_top_zonas
-- objetivo: Top 8 zonas de origen por tipo (= top_zonas_origen del Ej. 4)
SELECT taxi_type, borough, zone, viajes
FROM (
    SELECT t.taxi_type, z.borough, z.zone, COUNT(*) AS viajes
    FROM trips_clean t LEFT JOIN zones z ON z.location_id = t.pu_location_id
    GROUP BY t.taxi_type, z.borough, z.zone
)
QUALIFY ROW_NUMBER() OVER (PARTITION BY taxi_type ORDER BY viajes DESC) <= 8
ORDER BY taxi_type, viajes DESC;

-- name: B5_propinas
-- objetivo: Propina como % de la tarifa con tarjeta (= propinas del Ej. 4)
SELECT taxi_type, COUNT(*) AS viajes,
       ROUND(100.0 * AVG((tip_amount > 0)::INT), 1) AS pct_con_propina,
       ROUND(100.0 * MEDIAN(tip_amount / NULLIF(fare_amount, 0)), 1) AS propina_pct_mediana
FROM trips_clean
WHERE payment_type = 1 AND fare_amount > 0
GROUP BY taxi_type ORDER BY taxi_type;

-- name: B6_percentiles
-- objetivo: Percentiles exactos de distancia, duracion y total (= percentiles_distancia_duracion del Ej. 4)
SELECT taxi_type, variable,
       QUANTILE_CONT(valor, [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) AS percentiles
FROM (
    UNPIVOT (SELECT taxi_type, trip_distance, duration_min, total_amount FROM trips_clean)
    ON trip_distance, duration_min, total_amount
    INTO NAME variable VALUE valor
)
GROUP BY ALL ORDER BY 1, 2;

-- name: B7_un_dia
-- objetivo: Filtro muy selectivo: estadisticas de un solo dia (15-ene-2026, presente en todos los escenarios)
SELECT taxi_type, COUNT(*) AS viajes, ROUND(AVG(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_at >= TIMESTAMP '2026-01-15' AND pickup_at < TIMESTAMP '2026-01-16'
GROUP BY taxi_type ORDER BY taxi_type;

-- name: B8_filas_completas
-- objetivo: Traer todas las columnas de los 100 mil viajes mas caros (lectura de filas completas)
SELECT * EXCLUDE (source_file)
FROM trips
-- desempate por todas las columnas para que el resultado sea determinista
ORDER BY total_amount DESC, pickup_at, dropoff_at, taxi_type, vendor_id, pu_location_id,
         do_location_id, trip_distance, fare_amount, tip_amount, payment_type
LIMIT 100000;
