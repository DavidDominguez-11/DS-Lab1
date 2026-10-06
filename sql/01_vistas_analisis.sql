-- =============================================================================
-- Capa de analisis: vistas que dependen solo de `trips` y `zones`.
--
-- Este archivo funciona igual si `trips`/`zones` son vistas sobre Parquet
-- (sql/00_vistas.sql, uso normal) o tablas materializadas dentro de una base
-- DuckDB (scripts/build_database.py, Ejercicio 6). Asi el mismo texto SQL se
-- ejecuta contra ambas estrategias y el benchmark compara solo el almacenamiento.
-- =============================================================================

-- Vista limpia usada en el analisis exploratorio y los indicadores.
-- Cada filtro corresponde a un problema de calidad documentado en
-- docs/03_consultas_directas.md (seccion 3.6).
CREATE OR REPLACE VIEW trips_clean AS
SELECT
    *,
    -- NULL cuando el proveedor no registra la hora de llegada (ver VendorID 7 abajo)
    CASE WHEN dropoff_at > pickup_at
         THEN date_diff('second', pickup_at, dropoff_at) / 60.0 END AS duration_min,
    CAST(pickup_at AS DATE)                            AS pickup_date,
    hour(pickup_at)                                    AS pickup_hour,
    isodow(pickup_at)                                  AS pickup_dow     -- 1 = lunes
FROM trips
WHERE year(pickup_at) = source_year                 -- fechas fuera del periodo del archivo
  AND month(pickup_at) = source_month
  -- duracion nula o negativa. Excepcion: VendorID 7 registra dropoff = pickup
  -- en el 100% de sus viajes (error sistematico del proveedor, no del viaje);
  -- sus distancias y montos son validos, asi que se conservan con duration_min NULL.
  AND (dropoff_at > pickup_at OR (vendor_id = 7 AND dropoff_at = pickup_at))
  AND dropoff_at <= pickup_at + INTERVAL 6 HOUR     -- duraciones imposibles (> 6 h)
  AND trip_distance > 0 AND trip_distance <= 100    -- distancia nula o absurda (millas)
  AND fare_amount >= 0 AND total_amount >= 0        -- anulaciones / reembolsos
  AND total_amount <= 1000;                         -- montos extremos

-- Catalogo de tipos de pago (diccionario de datos de la TLC).
CREATE OR REPLACE VIEW payment_types AS
SELECT * FROM (VALUES
    (0, 'Flex Fare / sin dato'),
    (1, 'Tarjeta'),
    (2, 'Efectivo'),
    (3, 'Sin cargo'),
    (4, 'Disputa'),
    (5, 'Desconocido'),
    (6, 'Viaje anulado')
) AS t(payment_type, payment_desc);
