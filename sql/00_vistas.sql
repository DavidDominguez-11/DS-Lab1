-- =============================================================================
-- Vistas base del laboratorio.
--
-- Todas las vistas leen DIRECTAMENTE los archivos Parquet de data/raw/: no se
-- copia ningun dato. Como usan patrones glob (*/*.parquet), cualquier archivo
-- nuevo que descargue scripts/download_data.py (otro mes u otro anio) aparece
-- automaticamente en las consultas sin modificar este archivo.
--
-- Las rutas son relativas a la raiz del proyecto (scripts/sqlrun.py hace chdir).
-- =============================================================================

-- union_by_name=true es obligatorio: el esquema cambia entre archivos (por
-- ejemplo, request_source aparece en junio de 2026 y cbd_congestion_fee en
-- 2025). Sin esa opcion DuckDB toma el esquema del primer archivo y descarta
-- en silencio las columnas que no esten en el.
CREATE OR REPLACE VIEW yellow_raw AS
SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true, filename = true);

CREATE OR REPLACE VIEW green_raw AS
SELECT * FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true, filename = true);

-- Vista unificada: mismos nombres de columna para amarillos y verdes.
--   * tpep_* (yellow) y lpep_* (green) -> pickup_at / dropoff_at
--   * columnas exclusivas de un tipo quedan en NULL para el otro
--   * source_year / source_month salen del NOMBRE del archivo, no de la fecha
--     del viaje, para poder detectar registros fuera de su periodo.
CREATE OR REPLACE VIEW trips AS
SELECT
    'yellow'                                   AS taxi_type,
    VendorID                                   AS vendor_id,
    tpep_pickup_datetime                       AS pickup_at,
    tpep_dropoff_datetime                      AS dropoff_at,
    passenger_count,
    trip_distance,
    RatecodeID                                 AS ratecode_id,
    store_and_fwd_flag,
    PULocationID                               AS pu_location_id,
    DOLocationID                               AS do_location_id,
    payment_type,
    fare_amount, extra, mta_tax, tip_amount, tolls_amount,
    improvement_surcharge, total_amount, congestion_surcharge,
    Airport_fee                                AS airport_fee,
    cbd_congestion_fee,
    CAST(NULL AS DOUBLE)                       AS ehail_fee,
    CAST(NULL AS BIGINT)                       AS trip_type,
    request_source,
    CAST(regexp_extract(filename, '_(\d{4})-\d{2}\.parquet$', 1) AS INTEGER) AS source_year,
    CAST(regexp_extract(filename, '_\d{4}-(\d{2})\.parquet$', 1) AS INTEGER) AS source_month,
    filename                                   AS source_file
FROM yellow_raw
UNION ALL
SELECT
    'green', VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,
    passenger_count, trip_distance, RatecodeID, store_and_fwd_flag,
    PULocationID, DOLocationID, payment_type,
    fare_amount, extra, mta_tax, tip_amount, tolls_amount,
    improvement_surcharge, total_amount, congestion_surcharge,
    CAST(NULL AS DOUBLE),                       -- los verdes no tienen airport_fee
    cbd_congestion_fee, ehail_fee, trip_type, request_source,
    CAST(regexp_extract(filename, '_(\d{4})-\d{2}\.parquet$', 1) AS INTEGER),
    CAST(regexp_extract(filename, '_\d{4}-(\d{2})\.parquet$', 1) AS INTEGER),
    filename
FROM green_raw;

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

-- Zonas de taxi de la TLC (descargadas por scripts/download_data.py).
CREATE OR REPLACE VIEW zones AS
SELECT LocationID AS location_id, Borough AS borough, Zone AS zone, service_zone
FROM read_csv('data/raw/misc/taxi_zone_lookup.csv', header = true);

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
