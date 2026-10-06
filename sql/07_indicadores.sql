-- =============================================================================
-- Ejercicio 7: indicadores del tablero.
--
-- Cada bloque es una tarjeta del tablero de Metabase. Los metadatos indican:
--   pregunta       la pregunta de analisis que responde (7.1)
--   justificacion  por que el indicador es relevante (7.6)
--   visual         tipo de grafica de Metabase (scalar, line, bar, row, area, table, combo)
--   x / y / serie  columnas para los ejes y la serie (cuando aplica)
--   titulo         titulo de la tarjeta
--   eje_derecho    series que se dibujan en el eje derecho (escala distinta)
--   tamano         ancho,alto de la tarjeta en la cuadricula de 24 columnas
--
-- Las consultas usan las tablas/vistas `trips`, `trips_clean` y `zones`, que
-- existen tanto en data/processed/taxi.duckdb (tablero) como en las vistas
-- Parquet en memoria (python scripts/sqlrun.py sql/07_indicadores.sql).
-- No fijan anios: al agregar 2025 el tablero se actualiza solo (Ej. 8).
-- =============================================================================

-- name: K1_viajes_totales
-- titulo: Viajes válidos
-- pregunta: Cuantos viajes validos hay en el periodo analizado?
-- justificacion: Escala del sistema; contexto para todos los demas indicadores.
-- visual: scalar
-- tamano: 6,3
SELECT COUNT(*) AS viajes FROM trips_clean;

-- name: K2_ingreso_total
-- titulo: Ingreso total (M USD)
-- pregunta: Cuanto dinero pagaron los pasajeros en total (millones de USD)?
-- justificacion: Dimension economica del servicio de taxis.
-- visual: scalar
-- tamano: 6,3
SELECT ROUND(SUM(total_amount) / 1e6, 1) AS ingreso_musd FROM trips_clean;

-- name: K3_ticket_mediano
-- titulo: Ticket mediano (USD)
-- pregunta: Cuanto paga un pasajero en un viaje tipico (mediana, USD)?
-- justificacion: La mediana resiste los valores extremos detectados en el Ej. 3.
-- visual: scalar
-- tamano: 6,3
SELECT ROUND(MEDIAN(total_amount), 2) AS ticket_mediano_usd FROM trips_clean;

-- name: K4_cuota_green
-- titulo: % de viajes green
-- pregunta: Que porcentaje de los viajes hacen los taxis verdes?
-- justificacion: Mide el peso del servicio green frente al yellow.
-- visual: scalar
-- tamano: 6,3
SELECT ROUND(100.0 * AVG((taxi_type = 'green')::INT), 2) AS pct_viajes_green FROM trips_clean;

-- name: I1_viajes_diarios_por_mes
-- titulo: Viajes por día, por mes
-- eje_derecho: green
-- pregunta: P1 Cuantos viajes diarios hace cada tipo de taxi y como evoluciona mes a mes?
-- justificacion: Indicador de demanda normalizado por dias del mes; los archivos son mensuales.
-- visual: line
-- x: mes
-- y: viajes_por_dia
-- serie: taxi_type
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0) AS viajes_por_dia
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;

-- name: I2_ingreso_mensual
-- titulo: Ingreso mensual (M USD)
-- eje_derecho: green
-- pregunta: P2 Cuanto ingreso genera el sistema cada mes?
-- justificacion: Combina volumen y precio; muestra estacionalidad economica.
-- visual: bar
-- x: mes
-- y: ingreso_musd
-- serie: taxi_type
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(SUM(total_amount) / 1e6, 2) AS ingreso_musd
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;

-- name: I3_precio_del_viaje
-- titulo: Precio del viaje yellow (mediana)
-- pregunta: P3 Se esta encareciendo el viaje? (ticket mediano y tarifa mediana por milla)
-- justificacion: Separa el efecto de precio del de distancia: la tarifa por milla no depende de lo largo del viaje.
-- visual: line
-- x: mes
-- y: ticket_mediano,tarifa_por_milla_mediana
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       ROUND(MEDIAN(total_amount), 2)                    AS ticket_mediano,
       ROUND(MEDIAN(fare_amount / trip_distance), 2)     AS tarifa_por_milla_mediana
FROM trips_clean
WHERE taxi_type = 'yellow' AND trip_distance >= 0.5
GROUP BY ALL ORDER BY mes;

-- name: I4_metodo_pago
-- titulo: Método de pago (% de viajes)
-- pregunta: P4 Como pagan los pasajeros y como cambia con el tiempo?
-- justificacion: El metodo de pago condiciona el registro de propinas y concentra los datos faltantes.
-- visual: area
-- x: mes
-- y: pct
-- serie: metodo
-- apilado: true
-- tamano: 12,6
WITH m AS (
    SELECT date_trunc('month', pickup_at)::DATE AS mes,
           CASE WHEN payment_type = 1 THEN 'Tarjeta'
                WHEN payment_type = 2 THEN 'Efectivo'
                WHEN payment_type = 0 OR payment_type IS NULL THEN 'Sin dato / Flex'
                ELSE 'Otro' END AS metodo,
           COUNT(*) AS viajes
    FROM trips_clean
    GROUP BY 1, 2
)
SELECT mes, metodo, ROUND(100.0 * viajes / SUM(viajes) OVER (PARTITION BY mes), 2) AS pct
FROM m ORDER BY mes, metodo;

-- name: I5_propina
-- titulo: Propina mediana (% de la tarifa, tarjeta)
-- pregunta: P5 Que porcentaje de la tarifa se deja de propina (pago con tarjeta)?
-- justificacion: Solo la tarjeta registra propina; la mediana evita el sesgo de propinas atipicas.
-- visual: line
-- x: mes
-- y: propina_pct_mediana
-- serie: taxi_type
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(100.0 * MEDIAN(tip_amount / fare_amount), 1) AS propina_pct_mediana
FROM trips_clean
WHERE payment_type = 1 AND fare_amount > 0
GROUP BY ALL ORDER BY mes, taxi_type;

-- name: I6_velocidad_por_hora
-- titulo: Velocidad mediana por hora (mph)
-- pregunta: P6 A que horas es mas lenta la ciudad?
-- justificacion: La velocidad mediana (distancia / duracion) es un indicador directo de congestion.
-- visual: line
-- x: hora
-- y: velocidad_mediana_mph
-- serie: taxi_type
-- tamano: 12,6
SELECT pickup_hour AS hora, taxi_type,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 1) AS velocidad_mediana_mph
FROM trips_clean
WHERE duration_min >= 1
GROUP BY ALL ORDER BY hora, taxi_type;

-- name: I7_demanda_por_hora
-- titulo: Viajes promedio por hora del día
-- pregunta: P7 Como se reparte la demanda durante el dia en dias laborables y fines de semana?
-- justificacion: Define cuando se necesita oferta de taxis; el patron cambia completamente el fin de semana.
-- visual: line
-- x: hora
-- y: viajes_promedio_por_hora
-- serie: tipo_dia
-- tamano: 12,6
WITH base AS (
    SELECT pickup_hour, CASE WHEN pickup_dow >= 6 THEN 'Fin de semana' ELSE 'Laborable' END AS tipo_dia,
           pickup_date
    FROM trips_clean
)
SELECT pickup_hour AS hora, tipo_dia,
       ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0) AS viajes_promedio_por_hora
FROM base
GROUP BY ALL ORDER BY hora, tipo_dia;

-- name: I8_top_zonas
-- titulo: Zonas de origen con más viajes
-- pregunta: P8 Cuales son las zonas donde mas viajes comienzan?
-- justificacion: Ubica la demanda en el espacio; une los datos con la tabla de zonas de la TLC.
-- visual: row
-- x: zona
-- y: viajes
-- tamano: 12,8
SELECT z.zone || ' (' || z.borough || ')' AS zona, COUNT(*) AS viajes
FROM trips_clean t JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY 1 ORDER BY viajes DESC LIMIT 12;

-- name: I9_aeropuertos
-- titulo: Aeropuertos: viajes e ingreso
-- pregunta: P9 Que peso tienen los aeropuertos en viajes e ingresos?
-- justificacion: Pocos viajes pero muy caros; segmento clave para el ingreso de los yellow.
-- visual: table
-- tamano: 12,8
SELECT CASE WHEN z.service_zone IN ('Airports', 'EWR') THEN z.zone ELSE 'Resto de la ciudad' END AS origen,
       COUNT(*)                                                    AS viajes,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)          AS pct_viajes,
       ROUND(100.0 * SUM(total_amount) / SUM(SUM(total_amount)) OVER (), 2) AS pct_ingreso,
       ROUND(MEDIAN(total_amount), 2)                              AS ticket_mediano
FROM trips_clean t JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY 1 ORDER BY viajes DESC;

-- name: I10_cargo_cbd
-- titulo: % de viajes que pagan el cargo CBD
-- pregunta: P10 Que porcentaje de los viajes paga el cargo de congestion de Manhattan (CBD)?
-- justificacion: Politica publica nueva (ene-2025); mide su alcance sobre cada tipo de taxi.
-- visual: line
-- x: mes
-- y: pct_paga_cbd
-- serie: taxi_type
-- tamano: 12,6
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(100.0 * AVG((COALESCE(cbd_congestion_fee, 0) > 0)::INT), 1) AS pct_paga_cbd
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;

-- name: I11_calidad_datos
-- titulo: % de registros inválidos por mes
-- pregunta: P12 Que porcentaje de los registros publicados es invalido cada mes?
-- justificacion: Indicador de confiabilidad: los demas indicadores solo son validos si este es bajo y estable.
-- visual: line
-- x: mes
-- y: pct_invalidos
-- serie: taxi_type
-- tamano: 12,6
SELECT make_date(t.source_year, t.source_month, 1) AS mes, t.taxi_type,
       ROUND(100.0 * (COUNT(*) - ANY_VALUE(c.limpios)) / COUNT(*), 2) AS pct_invalidos
FROM trips t
JOIN (SELECT source_year, source_month, taxi_type, COUNT(*) AS limpios
      FROM trips_clean GROUP BY ALL) c USING (source_year, source_month, taxi_type)
GROUP BY ALL ORDER BY mes, t.taxi_type;

-- name: I12_despacho_por_app
-- titulo: Origen de la solicitud (yellow, desde jun-2026)
-- pregunta: P13 Que parte de los viajes yellow se solicita por apps de terceros?
-- justificacion: Columna nueva (jun-2026) que muestra la integracion taxi-apps.
-- visual: bar
-- x: mes
-- y: pct
-- serie: origen_solicitud
-- apilado: true
-- tamano: 12,6
WITH m AS (
    SELECT date_trunc('month', pickup_at)::DATE AS mes,
           CASE request_source WHEN 'HV0003' THEN 'App Uber' WHEN 'HV0005' THEN 'App Lyft'
                               WHEN 'A' THEN 'Codigo A' WHEN 'CC' THEN 'Codigo CC'
                               WHEN 'EH0004' THEN 'E-hail' WHEN 'EH0010' THEN 'E-hail'
                               ELSE 'Sin dato (calle)' END AS origen_solicitud,
           COUNT(*) AS viajes
    FROM trips_clean
    WHERE taxi_type = 'yellow' AND pickup_at >= DATE '2026-06-01'
    GROUP BY 1, 2
)
SELECT mes, origen_solicitud, ROUND(100.0 * viajes / SUM(viajes) OVER (PARTITION BY mes), 2) AS pct
FROM m ORDER BY mes, origen_solicitud;
