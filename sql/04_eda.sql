-- =============================================================================
-- Ejercicio 4: analisis exploratorio con DuckDB.
--
-- Todas las consultas leen los Parquet a traves de las vistas de
-- sql/00_vistas.sql. Se usa trips_clean (sin los registros invalidos
-- documentados en el Ejercicio 3) salvo en la seccion de atipicos, que usa
-- trips porque justamente busca los registros invalidos.
--
-- Ninguna consulta fija el anio: trabajan sobre todos los archivos presentes en
-- data/raw/. Para el Ejercicio 4 solo existen los archivos de 2026.
-- Ejecutar: python scripts/sqlrun.py sql/04_eda.sql --md docs/resultados/04_eda.md
-- =============================================================================

-- ---------------------------------------------------------------- temporal --

-- name: viajes_por_mes
-- objetivo: P1 Como evoluciona la cantidad de viajes por mes y tipo de taxi
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    date_trunc('month', pickup_at)::DATE                  AS mes,
    taxi_type,
    COUNT(*)                                              AS viajes,
    ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0)      AS viajes_por_dia,
    ROUND(AVG(total_amount), 2)                           AS ingreso_prom,
    ROUND(SUM(total_amount) / 1e6, 2)                     AS ingreso_total_musd
FROM trips_clean
GROUP BY ALL
ORDER BY mes, taxi_type DESC;

-- name: demanda_por_dia_semana
-- objetivo: P2 Que dias de la semana concentran la demanda (promedio diario)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    pickup_dow                                             AS dia_iso,
    dayname(MIN(pickup_at))                                AS dia,
    ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0)       AS viajes_por_dia,
    ROUND(AVG(trip_distance), 2)                           AS distancia_prom
FROM trips_clean
GROUP BY taxi_type, pickup_dow
ORDER BY taxi_type DESC, dia_iso;

-- name: demanda_hora_dia
-- objetivo: P2 Mapa de calor de viajes promedio por hora y dia de la semana (yellow + green)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
WITH dias AS (
    SELECT pickup_dow, COUNT(DISTINCT pickup_date) AS n_dias FROM trips_clean GROUP BY 1
)
SELECT t.pickup_dow AS dia_iso, t.pickup_hour AS hora,
       ROUND(COUNT(*) / ANY_VALUE(d.n_dias), 0) AS viajes_promedio
FROM trips_clean t JOIN dias d USING (pickup_dow)
GROUP BY ALL
ORDER BY dia_iso, hora;

-- name: velocidad_por_hora
-- objetivo: P3 Como cambian la velocidad y la duracion a lo largo del dia (congestion)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    pickup_hour                                                      AS hora,
    taxi_type,
    COUNT(*)                                                         AS viajes,
    ROUND(MEDIAN(duration_min), 1)                                   AS duracion_mediana_min,
    ROUND(MEDIAN(trip_distance), 2)                                  AS distancia_mediana_mi,
    ROUND(MEDIAN(trip_distance / (duration_min / 60)), 1)            AS velocidad_mediana_mph
FROM trips_clean
WHERE duration_min >= 1
GROUP BY ALL
ORDER BY taxi_type DESC, hora;

-- --------------------------------------------------- caracteristicas viaje --

-- name: comparacion_tipos
-- objetivo: P4 Perfil general de un viaje yellow vs green
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    COUNT(*)                                          AS viajes,
    ROUND(AVG(trip_distance), 2)                      AS distancia_prom,
    ROUND(MEDIAN(trip_distance), 2)                   AS distancia_mediana,
    ROUND(MEDIAN(duration_min), 1)                    AS duracion_mediana,
    ROUND(AVG(passenger_count), 2)                    AS pasajeros_prom,
    ROUND(MEDIAN(fare_amount), 2)                     AS tarifa_mediana,
    ROUND(MEDIAN(total_amount), 2)                    AS total_mediano,
    ROUND(MEDIAN(fare_amount / trip_distance), 2)     AS tarifa_por_milla_mediana,
    ROUND(100.0 * AVG((pu_location_id = do_location_id)::INT), 1) AS pct_misma_zona
FROM trips_clean
GROUP BY taxi_type
ORDER BY viajes DESC;

-- name: percentiles_distancia_duracion
-- objetivo: P4 Distribucion (percentiles) de distancia, duracion y total por tipo
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    variable,
    ROUND(QUANTILE_CONT(valor, 0.05), 2) AS p05,
    ROUND(QUANTILE_CONT(valor, 0.25), 2) AS p25,
    ROUND(QUANTILE_CONT(valor, 0.50), 2) AS p50,
    ROUND(QUANTILE_CONT(valor, 0.75), 2) AS p75,
    ROUND(QUANTILE_CONT(valor, 0.95), 2) AS p95,
    ROUND(QUANTILE_CONT(valor, 0.99), 2) AS p99
FROM (
    UNPIVOT (SELECT taxi_type, trip_distance, duration_min, total_amount FROM trips_clean)
    ON trip_distance, duration_min, total_amount
    INTO NAME variable VALUE valor
)
GROUP BY ALL
ORDER BY variable, taxi_type DESC;

-- name: histograma_distancia
-- objetivo: P4 Histograma de distancia (bins de 1 milla hasta 30; el resto en 30+)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    LEAST(FLOOR(trip_distance), 30)::INT                AS milla,
    COUNT(*)                                            AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct
FROM trips_clean
GROUP BY taxi_type, milla
ORDER BY taxi_type DESC, milla;

-- name: pasajeros
-- objetivo: P4 Distribucion de la cantidad de pasajeros
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    COALESCE(passenger_count::VARCHAR, 'sin dato')       AS pasajeros,
    COUNT(*)                                             AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct
FROM trips_clean
GROUP BY taxi_type, passenger_count
ORDER BY taxi_type DESC, passenger_count NULLS LAST;

-- name: zonas_origen_borough
-- objetivo: P5 En que borough comienzan los viajes de cada tipo de taxi
-- fuente: data/raw/*/*/*.parquet (trips_clean) + data/raw/misc/taxi_zone_lookup.csv (zones)
SELECT
    t.taxi_type,
    COALESCE(z.borough, 'Desconocido')                    AS borough_origen,
    COUNT(*)                                              AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.taxi_type), 2) AS pct
FROM trips_clean t
LEFT JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY t.taxi_type, z.borough
ORDER BY t.taxi_type DESC, viajes DESC;

-- name: top_zonas_origen
-- objetivo: P5 Las 8 zonas de origen mas frecuentes por tipo de taxi
-- fuente: data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
SELECT taxi_type, borough, zone, viajes, pct
FROM (
    SELECT
        t.taxi_type, z.borough, z.zone,
        COUNT(*) AS viajes,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.taxi_type), 2) AS pct
    FROM trips_clean t
    LEFT JOIN zones z ON z.location_id = t.pu_location_id
    GROUP BY t.taxi_type, z.borough, z.zone
)
QUALIFY ROW_NUMBER() OVER (PARTITION BY taxi_type ORDER BY viajes DESC) <= 8
ORDER BY taxi_type DESC, viajes DESC;

-- name: aeropuertos
-- objetivo: P6 Peso y precio de los viajes que salen de los aeropuertos (JFK 132, LGA 138, EWR 1)
-- fuente: data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
SELECT
    taxi_type,
    CASE WHEN z.service_zone IN ('Airports', 'EWR') THEN z.zone ELSE 'No aeropuerto' END AS origen,
    COUNT(*)                                       AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct,
    ROUND(MEDIAN(trip_distance), 1)                AS distancia_mediana,
    ROUND(MEDIAN(total_amount), 2)                 AS total_mediano
FROM trips_clean t
LEFT JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY taxi_type, origen
ORDER BY taxi_type DESC, viajes DESC;

-- ------------------------------------------------------------------- pago --

-- name: metodo_pago
-- objetivo: P7 Distribucion de metodos de pago por tipo de taxi
-- fuente: data/raw/*/*/*.parquet (trips_clean) + catalogo payment_types
SELECT
    t.taxi_type,
    COALESCE(p.payment_desc, 'NULL / sin dato')          AS metodo,
    COUNT(*)                                             AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.taxi_type), 2) AS pct,
    ROUND(MEDIAN(t.total_amount), 2)                     AS total_mediano
FROM trips_clean t
LEFT JOIN payment_types p USING (payment_type)
GROUP BY t.taxi_type, p.payment_desc
ORDER BY t.taxi_type DESC, viajes DESC;

-- name: metodo_pago_por_mes
-- objetivo: P7 Evolucion mensual de la participacion de tarjeta, efectivo y sin dato
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    date_trunc('month', pickup_at)::DATE                                    AS mes,
    taxi_type,
    ROUND(100.0 * AVG((payment_type = 1)::INT), 2)                          AS pct_tarjeta,
    ROUND(100.0 * AVG((payment_type = 2)::INT), 2)                          AS pct_efectivo,
    ROUND(100.0 * AVG((payment_type = 0 OR payment_type IS NULL)::INT), 2)  AS pct_sin_dato
FROM trips_clean
GROUP BY ALL
ORDER BY taxi_type DESC, mes;

-- name: propinas
-- objetivo: P8 Propina como % de la tarifa (solo tarjeta: el efectivo no registra propina)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    COUNT(*)                                                       AS viajes_tarjeta,
    ROUND(100.0 * AVG((tip_amount > 0)::INT), 1)                   AS pct_con_propina,
    ROUND(AVG(tip_amount), 2)                                      AS propina_prom,
    ROUND(100.0 * MEDIAN(tip_amount / NULLIF(fare_amount, 0)), 1)  AS propina_pct_mediana,
    ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)) FILTER (WHERE tip_amount > 0), 1) AS propina_pct_prom_si_deja
FROM trips_clean
WHERE payment_type = 1 AND fare_amount > 0
GROUP BY taxi_type;

-- name: propina_por_hora
-- objetivo: P8 Cambia la propina segun la hora del dia (yellow, tarjeta)
-- fuente: data/raw/yellow/*/*.parquet (vista trips_clean)
SELECT
    pickup_hour                                                    AS hora,
    COUNT(*)                                                       AS viajes,
    ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)), 1)     AS propina_pct_prom
FROM trips_clean
WHERE taxi_type = 'yellow' AND payment_type = 1 AND fare_amount > 0
GROUP BY hora
ORDER BY hora;

-- name: recargos
-- objetivo: P9 Cuanto pesan los recargos (congestion, CBD, aeropuerto) en el total pagado
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    ROUND(100.0 * AVG((cbd_congestion_fee > 0)::INT), 1)             AS pct_paga_cbd,
    ROUND(100.0 * AVG((congestion_surcharge > 0)::INT), 1)           AS pct_paga_congestion,
    ROUND(100.0 * AVG((airport_fee > 0)::INT), 1)                    AS pct_paga_aeropuerto,
    ROUND(AVG(total_amount), 2)                                      AS total_prom,
    ROUND(AVG(fare_amount), 2)                                       AS tarifa_prom,
    ROUND(100.0 * AVG(fare_amount / NULLIF(total_amount, 0)), 1)     AS pct_total_es_tarifa
FROM trips_clean
GROUP BY taxi_type;

-- -------------------------------------------------- atipicos / inconsistencias --

-- name: velocidades_imposibles
-- objetivo: P10 Viajes con velocidades fisicamente imposibles (> 80 mph) aun despues de limpiar
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    COUNT(*) FILTER (WHERE trip_distance / (duration_min / 60) > 80)         AS mas_de_80mph,
    COUNT(*) FILTER (WHERE duration_min < 1)                                 AS menos_de_1min,
    COUNT(*)                                                                 AS viajes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE trip_distance / (duration_min / 60) > 80) / COUNT(*), 3) AS pct_mas_80mph
FROM trips_clean
GROUP BY taxi_type;

-- name: atipicos_iqr_tarifa_por_milla
-- objetivo: P10 Atipicos de tarifa por milla segun la regla de Tukey (Q1 - 1.5 IQR, Q3 + 1.5 IQR)
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
WITH base AS (
    SELECT taxi_type, fare_amount / trip_distance AS fpm
    FROM trips_clean WHERE trip_distance >= 0.5
), limites AS (
    SELECT taxi_type,
           QUANTILE_CONT(fpm, 0.25) AS q1,
           QUANTILE_CONT(fpm, 0.75) AS q3
    FROM base GROUP BY taxi_type
)
SELECT b.taxi_type,
       ROUND(ANY_VALUE(l.q1), 2)                         AS q1,
       ROUND(ANY_VALUE(l.q3), 2)                         AS q3,
       ROUND(ANY_VALUE(l.q3 + 1.5 * (l.q3 - l.q1)), 2)  AS limite_superior,
       COUNT(*) FILTER (WHERE b.fpm > l.q3 + 1.5 * (l.q3 - l.q1)) AS atipicos_altos,
       COUNT(*) FILTER (WHERE b.fpm < l.q1 - 1.5 * (l.q3 - l.q1)) AS atipicos_bajos,
       ROUND(100.0 * COUNT(*) FILTER (WHERE b.fpm > l.q3 + 1.5 * (l.q3 - l.q1)
                                         OR b.fpm < l.q1 - 1.5 * (l.q3 - l.q1)) / COUNT(*), 2) AS pct_atipicos
FROM base b JOIN limites l USING (taxi_type)
GROUP BY b.taxi_type;

-- name: registros_invalidos_por_mes
-- objetivo: P10 Los registros invalidos (descartados por trips_clean) se concentran en algun mes o proveedor?
-- fuente: data/raw/*/*/*.parquet (vista trips, sin limpiar)
SELECT
    source_year * 100 + source_month                      AS periodo,
    taxi_type,
    COUNT(*)                                              AS registros,
    ROUND(100.0 * AVG((total_amount < 0)::INT), 2)        AS pct_total_negativo,
    ROUND(100.0 * AVG((trip_distance = 0)::INT), 2)       AS pct_distancia_cero,
    ROUND(100.0 * AVG((dropoff_at <= pickup_at)::INT), 2) AS pct_duracion_invalida
FROM trips
GROUP BY ALL
ORDER BY taxi_type DESC, periodo;

-- name: invalidos_por_proveedor
-- objetivo: P10 Que proveedor (VendorID) genera los registros con duracion o distancia invalida
-- fuente: data/raw/*/*/*.parquet (vista trips, sin limpiar)
SELECT
    taxi_type,
    vendor_id,
    COUNT(*)                                              AS registros,
    ROUND(100.0 * AVG((dropoff_at <= pickup_at)::INT), 2) AS pct_duracion_invalida,
    ROUND(100.0 * AVG((trip_distance = 0)::INT), 2)       AS pct_distancia_cero,
    ROUND(100.0 * AVG((payment_type = 0 OR payment_type IS NULL)::INT), 2) AS pct_sin_dato_pago
FROM trips
GROUP BY ALL
ORDER BY taxi_type DESC, vendor_id;

-- name: despacho_por_aplicacion
-- objetivo: P11 Desde que aparece request_source (jun-2026), cuantos viajes se piden por app de terceros
-- fuente: data/raw/*/*/*.parquet (vista trips_clean)
SELECT
    taxi_type,
    COALESCE(request_source, 'NULL')                      AS request_source,
    CASE request_source
        WHEN 'HV0003' THEN 'App Uber (licencia HVFHS)'
        WHEN 'HV0005' THEN 'App Lyft (licencia HVFHS)'
        WHEN 'A'      THEN 'Codigo A (no documentado por la TLC)'
        WHEN 'CC'     THEN 'Codigo CC (no documentado por la TLC)'
        WHEN 'EH0004' THEN 'E-hail (base EH0004)'
        WHEN 'EH0010' THEN 'E-hail (base EH0010)'
        ELSE 'NULL: sin app (probable parada en calle)'
    END                                                   AS interpretacion,
    COUNT(*)                                              AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct
FROM trips_clean
WHERE pickup_at >= DATE '2026-06-01'
GROUP BY taxi_type, request_source
ORDER BY taxi_type DESC, viajes DESC;
