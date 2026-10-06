-- =============================================================================
-- Ejercicio 8: evolucion de los indicadores a traves de 2024, 2025 y 2026.
--
-- 2026 solo tiene enero-agosto. Para comparar anios de forma justa, las
-- consultas marcadas "ene-ago" usan solo esos meses en todos los anios; las
-- series mensuales muestran todos los meses disponibles.
-- Tambien son tarjetas del tablero (mismos metadatos que sql/07_indicadores.sql).
-- Ejecutar: python scripts/sqlrun.py sql/08_evolucion.sql --db data/processed/taxi.duckdb --md docs/resultados/08_evolucion.md
-- =============================================================================

-- name: E1_resumen_anual
-- titulo: Resumen anual comparable (enero-agosto)
-- pregunta: Como cambian los indicadores principales de un anio a otro?
-- justificacion: Tabla unica para comparar los tres anios en los mismos meses.
-- visual: table
-- tamano: 24,6
SELECT
    source_year::VARCHAR                                               AS anio,
    taxi_type,
    ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0)                   AS viajes_por_dia,
    ROUND(SUM(total_amount) / COUNT(DISTINCT pickup_date) / 1e6, 3)    AS ingreso_diario_musd,
    ROUND(MEDIAN(total_amount), 2)                                     AS ticket_mediano,
    ROUND(MEDIAN(trip_distance), 2)                                    AS distancia_mediana,
    ROUND(MEDIAN(fare_amount / trip_distance) FILTER (WHERE trip_distance >= 0.5), 2) AS tarifa_por_milla,
    ROUND(100.0 * AVG((payment_type = 1)::INT), 1)                     AS pct_tarjeta,
    ROUND(100.0 * AVG((payment_type = 0 OR payment_type IS NULL)::INT), 1) AS pct_sin_dato_pago,
    ROUND(100.0 * AVG((COALESCE(cbd_congestion_fee, 0) > 0)::INT), 1)  AS pct_paga_cbd,
    ROUND(100.0 * MEDIAN(tip_amount / fare_amount)
          FILTER (WHERE payment_type = 1 AND fare_amount > 0), 1)      AS propina_pct_mediana
FROM trips_clean
WHERE source_month <= 8
GROUP BY ALL
ORDER BY taxi_type DESC, anio;

-- name: E2_variacion_interanual
-- titulo: Variación interanual de viajes por día (%)
-- pregunta: Cuanto crece o decrece la demanda de cada tipo de taxi respecto al mismo mes del anio anterior?
-- justificacion: La variacion interanual elimina la estacionalidad (verano, enero).
-- visual: bar
-- x: mes
-- y: variacion_pct
-- serie: taxi_type
-- tamano: 12,6
WITH m AS (
    SELECT source_year, source_month, taxi_type,
           COUNT(*) / COUNT(DISTINCT pickup_date) AS viajes_por_dia
    FROM trips_clean
    GROUP BY ALL
)
SELECT make_date(a.source_year, a.source_month, 1) AS mes, a.taxi_type,
       ROUND(100.0 * (a.viajes_por_dia / b.viajes_por_dia - 1), 1) AS variacion_pct
FROM m a
JOIN m b ON b.source_year = a.source_year - 1
        AND b.source_month = a.source_month
        AND b.taxi_type = a.taxi_type
ORDER BY mes, a.taxi_type;

-- name: E3_cuota_green
-- titulo: Cuota de los taxis verdes (% de viajes)
-- pregunta: Pierden participacion los taxis verdes frente a los amarillos?
-- justificacion: Normaliza el crecimiento de un tipo por el del otro.
-- visual: line
-- x: mes
-- y: pct_green
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       ROUND(100.0 * AVG((taxi_type = 'green')::INT), 2) AS pct_green
FROM trips_clean
GROUP BY 1 ORDER BY 1;

-- name: E4_velocidad_por_anio
-- titulo: Velocidad mediana yellow por hora, por año (mph)
-- pregunta: Cambio la velocidad del trafico despues del peaje de congestion (ene-2025)?
-- justificacion: El peaje CBD busca reducir el trafico en Manhattan; la velocidad de los taxis es un proxy.
-- visual: line
-- x: hora
-- y: velocidad_mediana_mph
-- serie: anio
-- tamano: 12,6
SELECT pickup_hour AS hora, source_year::VARCHAR AS anio,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 2) AS velocidad_mediana_mph
FROM trips_clean
WHERE taxi_type = 'yellow' AND duration_min >= 1 AND source_month <= 8
GROUP BY ALL ORDER BY hora, anio;

-- name: E5_velocidad_cbd
-- titulo: Velocidad mediana de viajes dentro de Manhattan, laborables 7-19 h
-- pregunta: La mejora de velocidad se concentra en los viajes que pagan el cargo CBD?
-- justificacion: Compara viajes con y sin cargo CBD en horario laboral para aislar el efecto del peaje.
-- visual: bar
-- x: anio
-- y: velocidad_mediana_mph
-- serie: grupo
-- tamano: 12,6
SELECT source_year::VARCHAR AS anio,
       CASE WHEN source_year = 2024 THEN 'Manhattan (sin peaje aun)'
            WHEN COALESCE(cbd_congestion_fee, 0) > 0 THEN 'Paga cargo CBD'
            ELSE 'No paga cargo CBD' END AS grupo,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 2) AS velocidad_mediana_mph,
       COUNT(*) AS viajes
FROM trips_clean t
JOIN zones zo ON zo.location_id = t.pu_location_id
JOIN zones zd ON zd.location_id = t.do_location_id
WHERE taxi_type = 'yellow' AND duration_min >= 1 AND source_month <= 8
  AND pickup_dow <= 5 AND pickup_hour BETWEEN 7 AND 18
  AND zo.borough = 'Manhattan' AND zd.borough = 'Manhattan'
GROUP BY ALL ORDER BY anio, grupo;

-- name: E6_composicion_del_ticket
-- titulo: Composición del pago promedio de un viaje yellow (USD, ene-ago)
-- pregunta: De donde viene el aumento del precio del viaje?
-- justificacion: Descompone el total en tarifa, propina, recargos e impuestos.
-- visual: bar
-- x: anio
-- y: tarifa,propina,peajes,recargo_congestion,cargo_cbd,cargo_aeropuerto,otros
-- apilado: true
-- tamano: 12,6
SELECT source_year::VARCHAR AS anio,
       ROUND(AVG(fare_amount), 2)                               AS tarifa,
       ROUND(AVG(tip_amount), 2)                                AS propina,
       ROUND(AVG(tolls_amount), 2)                              AS peajes,
       ROUND(AVG(COALESCE(congestion_surcharge, 0)), 2)         AS recargo_congestion,
       ROUND(AVG(COALESCE(cbd_congestion_fee, 0)), 2)           AS cargo_cbd,
       ROUND(AVG(COALESCE(airport_fee, 0)), 2)                  AS cargo_aeropuerto,
       ROUND(AVG(extra + mta_tax + improvement_surcharge), 2)   AS otros,
       ROUND(AVG(total_amount), 2)                              AS total_registrado
FROM trips_clean
WHERE taxi_type = 'yellow' AND source_month <= 8 AND payment_type IN (1, 2)
GROUP BY 1 ORDER BY 1;

-- name: E7_sin_dato_por_proveedor
-- titulo: % de viajes yellow sin dato de pago, por proveedor
-- pregunta: El crecimiento de los viajes sin dato de pago viene de algun proveedor en particular?
-- justificacion: Explica el cambio del indicador de metodo de pago (I4) y valida su lectura.
-- visual: line
-- x: mes
-- y: pct_sin_dato
-- serie: proveedor
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       'Vendor ' || vendor_id AS proveedor,
       ROUND(100.0 * AVG((payment_type = 0)::INT), 1) AS pct_sin_dato
FROM trips_clean
WHERE taxi_type = 'yellow' AND vendor_id IN (1, 2)
GROUP BY ALL ORDER BY mes, proveedor;

-- name: E8_aeropuertos_por_anio
-- titulo: Viajes desde aeropuertos por día (ene-ago)
-- pregunta: Cambia el peso de los viajes desde aeropuertos entre anios?
-- justificacion: Segmento de mayor ingreso por viaje (I9).
-- visual: bar
-- x: anio
-- y: viajes_por_dia
-- serie: aeropuerto
-- tamano: 12,6
SELECT t.source_year::VARCHAR AS anio, z.zone AS aeropuerto,
       ROUND(COUNT(*) / ANY_VALUE(d.dias), 0) AS viajes_por_dia
FROM trips_clean t
JOIN zones z ON z.location_id = t.pu_location_id
JOIN (SELECT source_year, COUNT(DISTINCT pickup_date) AS dias FROM trips_clean
      WHERE source_month <= 8 GROUP BY 1) d USING (source_year)
WHERE z.zone IN ('JFK Airport', 'LaGuardia Airport') AND t.source_month <= 8
GROUP BY 1, 2 ORDER BY 1, 2;
