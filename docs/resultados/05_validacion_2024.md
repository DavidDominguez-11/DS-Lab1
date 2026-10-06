# Resultados de `sql/05_validacion_incorporacion.sql`

Generado con `python scripts/sqlrun.py sql/05_validacion_incorporacion.sql` (DuckDB 1.5.5). No editar a mano.

## `archivos_por_anio`

- **Objetivo:** Archivos presentes por tipo y anio, con el rango de meses (5.5)
- **Fuente:** glob('data/raw/*/*/*.parquet')
- **Tiempo:** 0.06 s

```sql
SELECT
    split_part(file, '/', 4)                                  AS anio,
    split_part(file, '/', 3)                                  AS taxi,
    COUNT(*)                                                  AS archivos,
    MIN(regexp_extract(file, '-(\d{2})\.parquet', 1))         AS primer_mes,
    MAX(regexp_extract(file, '-(\d{2})\.parquet', 1))         AS ultimo_mes
FROM glob('data/raw/*/*/*.parquet')
GROUP BY ALL
ORDER BY anio, taxi DESC;
```

| anio | taxi | archivos | primer_mes | ultimo_mes |
|---|---|---|---|---|
| 2024 | yellow | 12 | 01 | 12 |
| 2024 | green | 12 | 01 | 12 |
| 2026 | yellow | 8 | 01 | 08 |
| 2026 | green | 8 | 01 | 08 |

## `filas_metadatos_vs_lectura`

- **Objetivo:** Las filas declaradas en los metadatos coinciden con las que lee la vista trips (5.5)
- **Fuente:** parquet_file_metadata('data/raw/*/*/*.parquet') y vista trips
- **Tiempo:** 0.17 s

```sql
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
```

| anio | taxi_type | filas_metadatos | filas_leidas | coincide |
|---|---|---|---|---|
| 2024 | yellow | 41,169,720 | 41,169,720 | si |
| 2024 | green | 660,218 | 660,218 | si |
| 2026 | yellow | 29,703,355 | 29,703,355 | si |
| 2026 | green | 337,114 | 337,114 | si |

## `columnas_por_anio`

- **Objetivo:** Columnas que no existen en todos los anios (deriva de esquema entre anios) (5.7)
- **Fuente:** parquet_schema('data/raw/*/*/*.parquet')
- **Tiempo:** 0.07 s

```sql
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
```

| taxi | columna | anios_presente | tipos_fisicos |
|---|---|---|---|
| yellow | cbd_congestion_fee | 2026 | DOUBLE |
| yellow | request_source | 2026 | BYTE_ARRAY |
| green | cbd_congestion_fee | 2026 | DOUBLE |
| green | request_source | 2026 | BYTE_ARRAY |

## `riesgo_sin_union_by_name`

- **Objetivo:** Que columnas se perderian leyendo todos los anios sin union_by_name (5.7)
- **Fuente:** data/raw/yellow/*/*.parquet
- **Tiempo:** 0.06 s

```sql
SELECT 'sin union_by_name' AS lectura, COUNT(*) AS columnas,
       BOOL_OR(column_name = 'cbd_congestion_fee') AS incluye_cbd_fee,
       BOOL_OR(column_name = 'request_source')     AS incluye_request_source
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet'))
UNION ALL
SELECT 'con union_by_name', COUNT(*),
       BOOL_OR(column_name = 'cbd_congestion_fee'), BOOL_OR(column_name = 'request_source')
FROM (DESCRIBE SELECT * FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true));
```

| lectura | columnas | incluye_cbd_fee | incluye_request_source |
|---|---|---|---|
| sin union_by_name | 19 | no | no |
| con union_by_name | 21 | si | si |

## `nulos_estructurales_por_anio`

- **Objetivo:** Columnas nuevas quedan en NULL (no en 0) para los anios en que no existian (5.7)
- **Fuente:** vista trips
- **Tiempo:** 0.20 s

```sql
SELECT
    source_year                                                AS anio,
    taxi_type,
    COUNT(*)                                                   AS registros,
    ROUND(100.0 * AVG((cbd_congestion_fee IS NULL)::INT), 2)   AS pct_cbd_fee_nulo,
    ROUND(100.0 * AVG((request_source IS NULL)::INT), 2)       AS pct_request_source_nulo
FROM trips
GROUP BY ALL
ORDER BY anio, taxi_type DESC;
```

| anio | taxi_type | registros | pct_cbd_fee_nulo | pct_request_source_nulo |
|---|---|---|---|---|
| 2024 | yellow | 41,169,720 | 100 | 100 |
| 2024 | green | 660,218 | 100 | 100 |
| 2026 | yellow | 29,703,355 | 0 | 90.23 |
| 2026 | green | 337,114 | 0 | 94.3 |

## `consulta_conjunta_rango_fechas`

- **Objetivo:** Consulta conjunta sobre todos los anios: rango de fechas y registros por anio (5.6)
- **Fuente:** vista trips_clean (todos los Parquet)
- **Tiempo:** 2.31 s

```sql
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
```

| anio | taxi_type | viajes_limpios | primer_viaje | ultimo_viaje | meses |
|---|---|---|---|---|---|
| 2024 | yellow | 39,690,153 | 2024-01-01 00:00:00 | 2024-12-31 23:59:58 | 12 |
| 2024 | green | 621,273 | 2024-01-01 00:03:57 | 2024-12-31 23:56:49 | 12 |
| 2026 | yellow | 28,596,404 | 2026-01-01 00:00:00 | 2026-08-31 23:59:59 | 8 |
| 2026 | green | 323,096 | 2026-01-01 00:03:27 | 2026-08-31 23:58:28 | 8 |

## `comparacion_mismo_mes_entre_anios`

- **Objetivo:** Consulta conjunta: viajes por dia en el mismo mes de cada anio (solo meses presentes en todos los anios) (5.6)
- **Fuente:** vista trips_clean (todos los Parquet)
- **Tiempo:** 4.75 s

```sql
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
```

| taxi_type | mes | 2024 | 2026 |
|---|---|---|---|
| yellow | 1 | 92,522 | 114,862 |
| yellow | 2 | 100,000 | 116,082 |
| yellow | 3 | 110,921 | 122,934 |
| yellow | 4 | 113,757 | 124,116 |
| yellow | 5 | 116,652 | 127,858 |
| yellow | 6 | 114,223 | 123,186 |
| yellow | 7 | 95,885 | 109,284 |
| yellow | 8 | 92,447 | 103,354 |
| green | 1 | 1,720 | 1,251 |
| green | 2 | 1,738 | 1,278 |
| green | 3 | 1,745 | 1,371 |
| green | 4 | 1,765 | 1,412 |
| green | 5 | 1,854 | 1,390 |
| green | 6 | 1,723 | 1,415 |
| green | 7 | 1,565 | 1,271 |
| green | 8 | 1,571 | 1,249 |
