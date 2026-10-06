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
--
-- Contrato de esquema: las columnas que solo existen en algunos periodos se
-- declaran en una relacion vacia unida con UNION ALL BY NAME. Asi la columna
-- existe siempre (NULL si ningun archivo la trae) y las vistas funcionan con
-- cualquier subconjunto de archivos, por ejemplo solo 2024 o un solo mes.
CREATE OR REPLACE VIEW yellow_raw AS
SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true, filename = true)
UNION ALL BY NAME
SELECT NULL::DOUBLE AS cbd_congestion_fee, NULL::VARCHAR AS request_source WHERE false;

CREATE OR REPLACE VIEW green_raw AS
SELECT * FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true, filename = true)
UNION ALL BY NAME
SELECT NULL::DOUBLE AS cbd_congestion_fee, NULL::VARCHAR AS request_source WHERE false;

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

-- Zonas de taxi de la TLC (descargadas por scripts/download_data.py).
CREATE OR REPLACE VIEW zones AS
SELECT LocationID AS location_id, Borough AS borough, Zone AS zone, service_zone
FROM read_csv('data/raw/misc/taxi_zone_lookup.csv', header = true);
