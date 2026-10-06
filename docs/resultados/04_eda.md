# Resultados de `sql/04_eda.sql`

Generado con `python scripts/sqlrun.py sql/04_eda.sql` (DuckDB 1.5.5). No editar a mano.

## `viajes_por_mes`

- **Objetivo:** P1 Como evoluciona la cantidad de viajes por mes y tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.07 s

```sql
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
```

| mes | taxi_type | viajes | viajes_por_dia | ingreso_prom | ingreso_total_musd |
|---|---|---|---|---|---|
| 2026-01-01 | yellow | 3,560,724 | 114,862 | 29.61 | 105.44 |
| 2026-01-01 | green | 38,771 | 1,251 | 24.26 | 0.94 |
| 2026-02-01 | yellow | 3,250,299 | 116,082 | 30.4 | 98.8 |
| 2026-02-01 | green | 35,788 | 1,278 | 24.35 | 0.87 |
| 2026-03-01 | yellow | 3,810,964 | 122,934 | 30.21 | 115.13 |
| 2026-03-01 | green | 42,506 | 1,371 | 24.88 | 1.06 |
| 2026-04-01 | yellow | 3,723,482 | 124,116 | 30.05 | 111.88 |
| 2026-04-01 | green | 42,370 | 1,412 | 25.33 | 1.07 |
| 2026-05-01 | yellow | 3,963,589 | 127,858 | 30.5 | 120.89 |
| 2026-05-01 | green | 43,103 | 1,390 | 25.78 | 1.11 |
| 2026-06-01 | yellow | 3,695,575 | 123,186 | 30.55 | 112.89 |
| 2026-06-01 | green | 42,445 | 1,415 | 26.09 | 1.11 |
| 2026-07-01 | yellow | 3,387,798 | 109,284 | 30.09 | 101.93 |
| 2026-07-01 | green | 39,397 | 1,271 | 26.17 | 1.03 |
| 2026-08-01 | yellow | 3,203,973 | 103,354 | 30.1 | 96.43 |
| 2026-08-01 | green | 38,716 | 1,249 | 26.43 | 1.02 |

## `demanda_por_dia_semana`

- **Objetivo:** P2 Que dias de la semana concentran la demanda (promedio diario)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.95 s

```sql
SELECT
    taxi_type,
    pickup_dow                                             AS dia_iso,
    dayname(MIN(pickup_at))                                AS dia,
    ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0)       AS viajes_por_dia,
    ROUND(AVG(trip_distance), 2)                           AS distancia_prom
FROM trips_clean
GROUP BY taxi_type, pickup_dow
ORDER BY taxi_type DESC, dia_iso;
```

| taxi_type | dia_iso | dia | viajes_por_dia | distancia_prom |
|---|---|---|---|---|
| yellow | 1 | Monday | 97,189 | 3.75 |
| yellow | 2 | Tuesday | 114,679 | 3.39 |
| yellow | 3 | Wednesday | 122,219 | 3.35 |
| yellow | 4 | Thursday | 129,080 | 3.38 |
| yellow | 5 | Friday | 122,147 | 3.45 |
| yellow | 6 | Saturday | 130,155 | 3.4 |
| yellow | 7 | Sunday | 108,339 | 3.92 |
| green | 1 | Monday | 1,318 | 3.3 |
| green | 2 | Tuesday | 1,438 | 3.32 |
| green | 3 | Wednesday | 1,492 | 3.32 |
| green | 4 | Thursday | 1,526 | 3.3 |
| green | 5 | Friday | 1,384 | 3.36 |
| green | 6 | Saturday | 1,108 | 3.42 |
| green | 7 | Sunday | 1,049 | 3.52 |

## `demanda_hora_dia`

- **Objetivo:** P2 Mapa de calor de viajes promedio por hora y dia de la semana (yellow + green)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.94 s

```sql
WITH dias AS (
    SELECT pickup_dow, COUNT(DISTINCT pickup_date) AS n_dias FROM trips_clean GROUP BY 1
)
SELECT t.pickup_dow AS dia_iso, t.pickup_hour AS hora,
       ROUND(COUNT(*) / ANY_VALUE(d.n_dias), 0) AS viajes_promedio
FROM trips_clean t JOIN dias d USING (pickup_dow)
GROUP BY ALL
ORDER BY dia_iso, hora;
```

| dia_iso | hora | viajes_promedio |
|---|---|---|
| 1 | 0 | 1,948 |
| 1 | 1 | 999 |
| 1 | 2 | 566 |
| 1 | 3 | 439 |
| 1 | 4 | 596 |
| 1 | 5 | 1,123 |
| 1 | 6 | 2,277 |
| 1 | 7 | 4,089 |
| 1 | 8 | 5,321 |
| 1 | 9 | 5,026 |
| 1 | 10 | 4,728 |
| 1 | 11 | 4,906 |
| 1 | 12 | 5,227 |
| 1 | 13 | 5,349 |
| 1 | 14 | 5,970 |
| 1 | 15 | 6,290 |
| 1 | 16 | 5,883 |
| 1 | 17 | 6,607 |
| 1 | 18 | 6,531 |
| 1 | 19 | 5,635 |
| 1 | 20 | 5,784 |
| 1 | 21 | 5,677 |
| 1 | 22 | 4,533 |
| 1 | 23 | 3,003 |
| 2 | 0 | 1,758 |
| 2 | 1 | 812 |
| 2 | 2 | 436 |
| 2 | 3 | 288 |
| 2 | 4 | 409 |
| 2 | 5 | 989 |
| 2 | 6 | 2,335 |
| 2 | 7 | 4,604 |
| 2 | 8 | 6,190 |
| 2 | 9 | 6,009 |
| 2 | 10 | 5,531 |
| 2 | 11 | 5,650 |
| 2 | 12 | 5,926 |
| 2 | 13 | 6,087 |
| 2 | 14 | 6,734 |
| 2 | 15 | 7,080 |

*... 128 filas mas omitidas.*

## `velocidad_por_hora`

- **Objetivo:** P3 Como cambian la velocidad y la duracion a lo largo del dia (congestion)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.48 s

```sql
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
```

| hora | taxi_type | viajes | duracion_mediana_min | distancia_mediana_mi | velocidad_mediana_mph |
|---|---|---|---|---|---|
| 0 | yellow | 904,836 | 13.8 | 2.6 | 11.8 |
| 1 | yellow | 600,890 | 13.1 | 2.58 | 12.3 |
| 2 | yellow | 399,732 | 12.7 | 2.64 | 12.9 |
| 3 | yellow | 287,070 | 12.7 | 2.87 | 13.8 |
| 4 | yellow | 234,532 | 13.7 | 3.53 | 15.4 |
| 5 | yellow | 259,501 | 13.7 | 3.77 | 16 |
| 6 | yellow | 488,990 | 12.9 | 2.96 | 13.8 |
| 7 | yellow | 854,574 | 13.1 | 2.3 | 11.1 |
| 8 | yellow | 1,147,445 | 14.1 | 2 | 9.3 |
| 9 | yellow | 1,201,498 | 14.2 | 1.85 | 8.9 |
| 10 | yellow | 1,217,020 | 14.4 | 1.79 | 8.6 |
| 11 | yellow | 1,313,159 | 14.8 | 1.73 | 8.1 |
| 12 | yellow | 1,419,631 | 14.8 | 1.71 | 8.1 |
| 13 | yellow | 1,484,843 | 15 | 1.75 | 8.1 |
| 14 | yellow | 1,609,909 | 15.3 | 1.79 | 8 |
| 15 | yellow | 1,663,771 | 15.4 | 1.74 | 7.9 |
| 16 | yellow | 1,594,404 | 14.9 | 1.7 | 8 |
| 17 | yellow | 1,761,974 | 14.4 | 1.66 | 8 |
| 18 | yellow | 1,828,014 | 13.6 | 1.64 | 8.3 |
| 19 | yellow | 1,660,709 | 13.4 | 1.73 | 8.9 |
| 20 | yellow | 1,651,886 | 13.6 | 2.01 | 9.8 |
| 21 | yellow | 1,712,914 | 13.8 | 2.13 | 10.1 |
| 22 | yellow | 1,589,322 | 14.2 | 2.29 | 10.5 |
| 23 | yellow | 1,261,734 | 14.2 | 2.5 | 11.2 |
| 0 | green | 4,641 | 12 | 2.37 | 12.1 |
| 1 | green | 2,817 | 11.8 | 2.42 | 12.4 |
| 2 | green | 2,032 | 14 | 3.46 | 14 |
| 3 | green | 1,643 | 14.1 | 3.54 | 14.6 |
| 4 | green | 1,672 | 16.3 | 4.67 | 16.4 |
| 5 | green | 2,386 | 15.5 | 4.69 | 16.1 |
| 6 | green | 6,531 | 11.2 | 2.13 | 12.8 |
| 7 | green | 13,814 | 12.9 | 2.1 | 10.5 |
| 8 | green | 17,398 | 14.3 | 2.1 | 9.5 |
| 9 | green | 18,228 | 14 | 2.21 | 9.9 |
| 10 | green | 17,603 | 14.1 | 2.31 | 10.1 |
| 11 | green | 17,398 | 14.6 | 2.33 | 9.8 |
| 12 | green | 18,805 | 14.5 | 2.32 | 9.8 |
| 13 | green | 18,509 | 14.3 | 2.22 | 9.5 |
| 14 | green | 20,668 | 14.8 | 2.19 | 9.1 |
| 15 | green | 22,394 | 14.2 | 2.06 | 9 |

*... 8 filas mas omitidas.*

## `comparacion_tipos`

- **Objetivo:** P4 Perfil general de un viaje yellow vs green
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 5.07 s

```sql
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
```

| taxi_type | viajes | distancia_prom | distancia_mediana | duracion_mediana | pasajeros_prom | tarifa_mediana | total_mediano | tarifa_por_milla_mediana | pct_misma_zona |
|---|---|---|---|---|---|---|---|---|---|
| yellow | 28,596,404 | 3.51 | 1.92 | 14.1 | 1.25 | 15.6 | 23.58 | 7.55 | 3.8 |
| green | 323,096 | 3.35 | 2.14 | 13.3 | 1.3 | 13.5 | 20.52 | 6.68 | 8.9 |

## `percentiles_distancia_duracion`

- **Objetivo:** P4 Distribucion (percentiles) de distancia, duracion y total por tipo
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 12.72 s

```sql
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
```

| taxi_type | variable | p05 | p25 | p50 | p75 | p95 | p99 |
|---|---|---|---|---|---|---|---|
| yellow | duration_min | 4.02 | 8.62 | 14.1 | 22.25 | 44.05 | 71.3 |
| green | duration_min | 4.13 | 8.68 | 13.32 | 20.62 | 44.08 | 75.03 |
| yellow | total_amount | 12.4 | 17.45 | 23.58 | 34.42 | 77.18 | 104.96 |
| green | total_amount | 9.7 | 15.12 | 20.52 | 29.7 | 56.64 | 95.2 |
| yellow | trip_distance | 0.5 | 1.1 | 1.92 | 3.93 | 12.51 | 19.54 |
| green | trip_distance | 0.63 | 1.33 | 2.14 | 3.77 | 10.65 | 17.75 |

## `histograma_distancia`

- **Objetivo:** P4 Histograma de distancia (bins de 1 milla hasta 30; el resto en 30+)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.74 s

```sql
SELECT
    taxi_type,
    LEAST(FLOOR(trip_distance), 30)::INT                AS milla,
    COUNT(*)                                            AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct
FROM trips_clean
GROUP BY taxi_type, milla
ORDER BY taxi_type DESC, milla;
```

| taxi_type | milla | viajes | pct |
|---|---|---|---|
| yellow | 0 | 6,017,815 | 21.04 |
| yellow | 1 | 8,667,503 | 30.31 |
| yellow | 2 | 4,498,782 | 15.73 |
| yellow | 3 | 2,362,964 | 8.26 |
| yellow | 4 | 1,454,058 | 5.08 |
| yellow | 5 | 1,010,460 | 3.53 |
| yellow | 6 | 750,835 | 2.63 |
| yellow | 7 | 590,423 | 2.06 |
| yellow | 8 | 556,086 | 1.94 |
| yellow | 9 | 502,599 | 1.76 |
| yellow | 10 | 386,420 | 1.35 |
| yellow | 11 | 271,399 | 0.95 |
| yellow | 12 | 164,845 | 0.58 |
| yellow | 13 | 121,857 | 0.43 |
| yellow | 14 | 110,130 | 0.39 |
| yellow | 15 | 118,020 | 0.41 |
| yellow | 16 | 196,298 | 0.69 |
| yellow | 17 | 271,338 | 0.95 |
| yellow | 18 | 190,299 | 0.67 |
| yellow | 19 | 111,430 | 0.39 |
| yellow | 20 | 75,186 | 0.26 |
| yellow | 21 | 39,136 | 0.14 |
| yellow | 22 | 21,254 | 0.07 |
| yellow | 23 | 14,267 | 0.05 |
| yellow | 24 | 11,700 | 0.04 |
| yellow | 25 | 12,163 | 0.04 |
| yellow | 26 | 13,943 | 0.05 |
| yellow | 27 | 10,855 | 0.04 |
| yellow | 28 | 8,322 | 0.03 |
| yellow | 29 | 5,300 | 0.02 |
| yellow | 30 | 30,717 | 0.11 |
| green | 0 | 44,497 | 13.77 |
| green | 1 | 104,924 | 32.47 |
| green | 2 | 64,660 | 20.01 |
| green | 3 | 34,237 | 10.6 |
| green | 4 | 15,872 | 4.91 |
| green | 5 | 11,349 | 3.51 |
| green | 6 | 11,040 | 3.42 |
| green | 7 | 7,626 | 2.36 |
| green | 8 | 5,895 | 1.82 |

*... 22 filas mas omitidas.*

## `pasajeros`

- **Objetivo:** P4 Distribucion de la cantidad de pasajeros
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.85 s

```sql
SELECT
    taxi_type,
    COALESCE(passenger_count::VARCHAR, 'sin dato')       AS pasajeros,
    COUNT(*)                                             AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY taxi_type), 2) AS pct
FROM trips_clean
GROUP BY taxi_type, passenger_count
ORDER BY taxi_type DESC, passenger_count NULLS LAST;
```

| taxi_type | pasajeros | viajes | pct |
|---|---|---|---|
| yellow | 0 | 87,520 | 0.31 |
| yellow | 1 | 17,732,553 | 62.01 |
| yellow | 2 | 2,652,016 | 9.27 |
| yellow | 3 | 598,042 | 2.09 |
| yellow | 4 | 392,945 | 1.37 |
| yellow | 5 | 55,563 | 0.19 |
| yellow | 6 | 33,078 | 0.12 |
| yellow | 7 | 2 | 0 |
| yellow | 8 | 7 | 0 |
| yellow | 9 | 1 | 0 |
| yellow | sin dato | 7,044,677 | 24.63 |
| green | 0 | 4,265 | 1.32 |
| green | 1 | 227,940 | 70.55 |
| green | 2 | 27,456 | 8.5 |
| green | 3 | 3,092 | 0.96 |
| green | 4 | 2,248 | 0.7 |
| green | 5 | 6,114 | 1.89 |
| green | 6 | 4,230 | 1.31 |
| green | 7 | 26 | 0.01 |
| green | 8 | 28 | 0.01 |
| green | 9 | 24 | 0.01 |
| green | sin dato | 47,673 | 14.76 |

## `zonas_origen_borough`

- **Objetivo:** P5 En que borough comienzan los viajes de cada tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + data/raw/misc/taxi_zone_lookup.csv (zones)
- **Tiempo:** 0.96 s

```sql
SELECT
    t.taxi_type,
    COALESCE(z.borough, 'Desconocido')                    AS borough_origen,
    COUNT(*)                                              AS viajes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.taxi_type), 2) AS pct
FROM trips_clean t
LEFT JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY t.taxi_type, z.borough
ORDER BY t.taxi_type DESC, viajes DESC;
```

| taxi_type | borough_origen | viajes | pct |
|---|---|---|---|
| yellow | Manhattan | 24,799,696 | 86.72 |
| yellow | Queens | 2,520,729 | 8.81 |
| yellow | Brooklyn | 1,017,665 | 3.56 |
| yellow | Bronx | 218,885 | 0.77 |
| yellow | Unknown | 29,456 | 0.1 |
| yellow | N/A | 6,377 | 0.02 |
| yellow | Staten Island | 2,672 | 0.01 |
| yellow | EWR | 924 | 0 |
| green | Manhattan | 192,142 | 59.47 |
| green | Queens | 71,208 | 22.04 |
| green | Brooklyn | 51,069 | 15.81 |
| green | Bronx | 8,057 | 2.49 |
| green | Unknown | 380 | 0.12 |
| green | N/A | 186 | 0.06 |
| green | Staten Island | 54 | 0.02 |

## `top_zonas_origen`

- **Objetivo:** P5 Las 8 zonas de origen mas frecuentes por tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
- **Tiempo:** 1.12 s

```sql
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
```

| taxi_type | borough | zone | viajes | pct |
|---|---|---|---|---|
| yellow | Manhattan | Upper East Side South | 1,279,059 | 4.47 |
| yellow | Manhattan | Midtown Center | 1,190,673 | 4.16 |
| yellow | Manhattan | Upper East Side North | 1,139,696 | 3.99 |
| yellow | Queens | JFK Airport | 1,135,949 | 3.97 |
| yellow | Manhattan | Penn Station/Madison Sq West | 882,720 | 3.09 |
| yellow | Manhattan | Midtown East | 879,276 | 3.07 |
| yellow | Manhattan | Times Sq/Theatre District | 828,165 | 2.9 |
| yellow | Manhattan | Lincoln Square East | 827,442 | 2.89 |
| green | Manhattan | East Harlem North | 87,075 | 26.95 |
| green | Manhattan | East Harlem South | 41,923 | 12.98 |
| green | Queens | Forest Hills | 15,698 | 4.86 |
| green | Manhattan | Central Park | 13,002 | 4.02 |
| green | Manhattan | Morningside Heights | 12,490 | 3.87 |
| green | Queens | Elmhurst | 11,178 | 3.46 |
| green | Manhattan | Central Harlem | 11,081 | 3.43 |
| green | Brooklyn | Downtown Brooklyn/MetroTech | 10,544 | 3.26 |

## `aeropuertos`

- **Objetivo:** P6 Peso y precio de los viajes que salen de los aeropuertos (JFK 132, LGA 138, EWR 1)
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
- **Tiempo:** 2.75 s

```sql
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
```

| taxi_type | origen | viajes | pct | distancia_mediana | total_mediano |
|---|---|---|---|---|---|
| yellow | No aeropuerto | 26,733,704 | 93.49 | 1.8 | 22.74 |
| yellow | JFK Airport | 1,135,949 | 3.97 | 16.9 | 86.75 |
| yellow | LaGuardia Airport | 725,827 | 2.54 | 9.4 | 69.95 |
| yellow | Newark Airport | 924 | 0 | 0.1 | 126.9 |
| green | No aeropuerto | 322,953 | 99.96 | 2.1 | 20.52 |
| green | LaGuardia Airport | 73 | 0.02 | 3.5 | 55.55 |
| green | JFK Airport | 70 | 0.02 | 1.6 | 37.6 |

## `metodo_pago`

- **Objetivo:** P7 Distribucion de metodos de pago por tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + catalogo payment_types
- **Tiempo:** 1.71 s

```sql
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
```

| taxi_type | metodo | viajes | pct | total_mediano |
|---|---|---|---|---|
| yellow | Tarjeta | 18,770,424 | 65.64 | 22.35 |
| yellow | Flex Fare / sin dato | 7,044,677 | 24.63 | 28.98 |
| yellow | Efectivo | 2,601,327 | 9.1 | 18.25 |
| yellow | Disputa | 120,469 | 0.42 | 18.5 |
| yellow | Sin cargo | 59,506 | 0.21 | 16.45 |
| yellow | Desconocido | 1 | 0 | 0 |
| green | Tarjeta | 211,692 | 65.52 | 20.94 |
| green | Efectivo | 62,628 | 19.38 | 16.1 |
| green | NULL / sin dato | 47,673 | 14.76 | 26.47 |
| green | Sin cargo | 774 | 0.24 | 7.3 |
| green | Disputa | 329 | 0.1 | 7.7 |

## `metodo_pago_por_mes`

- **Objetivo:** P7 Evolucion mensual de la participacion de tarjeta, efectivo y sin dato
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.05 s

```sql
SELECT
    date_trunc('month', pickup_at)::DATE                                    AS mes,
    taxi_type,
    ROUND(100.0 * AVG((payment_type = 1)::INT), 2)                          AS pct_tarjeta,
    ROUND(100.0 * AVG((payment_type = 2)::INT), 2)                          AS pct_efectivo,
    ROUND(100.0 * AVG((payment_type = 0 OR payment_type IS NULL)::INT), 2)  AS pct_sin_dato
FROM trips_clean
GROUP BY ALL
ORDER BY taxi_type DESC, mes;
```

| mes | taxi_type | pct_tarjeta | pct_efectivo | pct_sin_dato |
|---|---|---|---|---|
| 2026-01-01 | yellow | 62.64 | 8.36 | 27.95 |
| 2026-02-01 | yellow | 62.6 | 8.01 | 28.58 |
| 2026-03-01 | yellow | 67.9 | 8.91 | 22.57 |
| 2026-04-01 | yellow | 70.22 | 9.37 | 19.89 |
| 2026-05-01 | yellow | 68.26 | 9.07 | 22.18 |
| 2026-06-01 | yellow | 65.21 | 9.32 | 24.97 |
| 2026-07-01 | yellow | 63.72 | 9.84 | 25.92 |
| 2026-08-01 | yellow | 63.34 | 9.92 | 26.2 |
| 2026-01-01 | green | 75.71 | 23.85 | 13.79 |
| 2026-02-01 | green | 76.07 | 23.41 | 14.79 |
| 2026-03-01 | green | 76.83 | 22.77 | 15.52 |
| 2026-04-01 | green | 77.35 | 22.27 | 14.69 |
| 2026-05-01 | green | 77.02 | 22.65 | 13.04 |
| 2026-06-01 | green | 77.26 | 22.36 | 15.02 |
| 2026-07-01 | green | 78.05 | 21.55 | 15.77 |
| 2026-08-01 | green | 76.43 | 23.2 | 15.51 |

## `propinas`

- **Objetivo:** P8 Propina como % de la tarifa (solo tarjeta: el efectivo no registra propina)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.50 s

```sql
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
```

| taxi_type | viajes_tarjeta | pct_con_propina | propina_prom | propina_pct_mediana | propina_pct_prom_si_deja |
|---|---|---|---|---|---|
| green | 211,691 | 91.4 | 3.8 | 23.5 | 25.1 |
| yellow | 18,770,330 | 91.2 | 4.26 | 26.4 | 27.6 |

## `propina_por_hora`

- **Objetivo:** P8 Cambia la propina segun la hora del dia (yellow, tarjeta)
- **Fuente:** data/raw/yellow/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.01 s

```sql
SELECT
    pickup_hour                                                    AS hora,
    COUNT(*)                                                       AS viajes,
    ROUND(100.0 * AVG(tip_amount / NULLIF(fare_amount, 0)), 1)     AS propina_pct_prom
FROM trips_clean
WHERE taxi_type = 'yellow' AND payment_type = 1 AND fare_amount > 0
GROUP BY hora
ORDER BY hora;
```

| hora | viajes | propina_pct_prom |
|---|---|---|
| 0 | 473,415 | 24.6 |
| 1 | 303,889 | 24.5 |
| 2 | 193,292 | 24.6 |
| 3 | 128,375 | 24.3 |
| 4 | 87,421 | 22.4 |
| 5 | 108,969 | 21 |
| 6 | 242,258 | 21.3 |
| 7 | 493,248 | 22.7 |
| 8 | 707,742 | 23.3 |
| 9 | 809,945 | 23.7 |
| 10 | 865,456 | 25.2 |
| 11 | 937,776 | 24.1 |
| 12 | 1,006,920 | 24.1 |
| 13 | 1,053,816 | 24.2 |
| 14 | 1,143,655 | 25.2 |
| 15 | 1,194,609 | 24 |
| 16 | 1,229,638 | 26.1 |
| 17 | 1,346,774 | 26.5 |
| 18 | 1,374,624 | 27 |
| 19 | 1,203,733 | 27 |
| 20 | 1,091,757 | 26.4 |
| 21 | 1,109,039 | 25.9 |
| 22 | 961,292 | 25.4 |
| 23 | 702,687 | 24.9 |

## `recargos`

- **Objetivo:** P9 Cuanto pesan los recargos (congestion, CBD, aeropuerto) en el total pagado
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 1.23 s

```sql
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
```

| taxi_type | pct_paga_cbd | pct_paga_congestion | pct_paga_aeropuerto | total_prom | tarifa_prom | pct_total_es_tarifa |
|---|---|---|---|---|---|---|
| green | 8.5 | 33.2 | NULL | 25.43 | 16.8 | 66 |
| yellow | 72.4 | 90.3 | 8.7 | 30.19 | 21.23 | 66.6 |

## `velocidades_imposibles`

- **Objetivo:** P10 Viajes con velocidades fisicamente imposibles (> 80 mph) aun despues de limpiar
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.97 s

```sql
SELECT
    taxi_type,
    COUNT(*) FILTER (WHERE trip_distance / (duration_min / 60) > 80)         AS mas_de_80mph,
    COUNT(*) FILTER (WHERE duration_min < 1)                                 AS menos_de_1min,
    COUNT(*)                                                                 AS viajes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE trip_distance / (duration_min / 60) > 80) / COUNT(*), 3) AS pct_mas_80mph
FROM trips_clean
GROUP BY taxi_type;
```

| taxi_type | mas_de_80mph | menos_de_1min | viajes | pct_mas_80mph |
|---|---|---|---|---|
| green | 1,087 | 3,487 | 323,096 | 0.336 |
| yellow | 7,210 | 87,686 | 28,596,404 | 0.025 |

## `atipicos_iqr_tarifa_por_milla`

- **Objetivo:** P10 Atipicos de tarifa por milla segun la regla de Tukey (Q1 - 1.5 IQR, Q3 + 1.5 IQR)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 2.21 s

```sql
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
```

| taxi_type | q1 | q3 | limite_superior | atipicos_altos | atipicos_bajos | pct_atipicos |
|---|---|---|---|---|---|---|
| green | 5.28 | 8 | 12.08 | 10,088 | 29,037 | 12.5 |
| yellow | 5.64 | 9.52 | 15.34 | 1,187,947 | 0 | 4.35 |

## `registros_invalidos_por_mes`

- **Objetivo:** P10 Los registros invalidos (descartados por trips_clean) se concentran en algun mes o proveedor?
- **Fuente:** data/raw/*/*/*.parquet (vista trips, sin limpiar)
- **Tiempo:** 0.80 s

```sql
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
```

| periodo | taxi_type | registros | pct_total_negativo | pct_distancia_cero | pct_duracion_invalida |
|---|---|---|---|---|---|
| 202,601 | yellow | 3,724,889 | 1.07 | 3.38 | 1.21 |
| 202,602 | yellow | 3,399,866 | 0.8 | 3.63 | 1.19 |
| 202,603 | yellow | 3,952,451 | 0.54 | 3.07 | 1.24 |
| 202,604 | yellow | 3,831,240 | 0.39 | 2.44 | 1.29 |
| 202,605 | yellow | 4,090,836 | 0.36 | 2.76 | 1.27 |
| 202,606 | yellow | 3,837,248 | 0.37 | 3.34 | 1.3 |
| 202,607 | yellow | 3,530,109 | 0.42 | 3.64 | 1.2 |
| 202,608 | yellow | 3,336,716 | 0.43 | 3.57 | 1.29 |
| 202,601 | green | 40,272 | 0.3 | 3.2 | 0.07 |
| 202,602 | green | 37,373 | 0.29 | 3.71 | 0.07 |
| 202,603 | green | 44,208 | 0.26 | 3.23 | 0.08 |
| 202,604 | green | 44,238 | 0.35 | 3.63 | 0.09 |
| 202,605 | green | 44,921 | 0.27 | 3.47 | 0.06 |
| 202,606 | green | 44,163 | 0.24 | 3.38 | 0.07 |
| 202,607 | green | 41,252 | 0.33 | 4 | 0.06 |
| 202,608 | green | 40,687 | 0.39 | 4.42 | 0.06 |

## `invalidos_por_proveedor`

- **Objetivo:** P10 Que proveedor (VendorID) genera los registros con duracion o distancia invalida
- **Fuente:** data/raw/*/*/*.parquet (vista trips, sin limpiar)
- **Tiempo:** 0.78 s

```sql
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
```

| taxi_type | vendor_id | registros | pct_duracion_invalida | pct_distancia_cero | pct_sin_dato_pago |
|---|---|---|---|---|---|
| yellow | 1 | 5,467,071 | 0.08 | 1.65 | 16.38 |
| yellow | 2 | 23,809,774 | 0 | 3.59 | 28.4 |
| yellow | 6 | 59,390 | 0.01 | 0 | 100 |
| yellow | 7 | 367,120 | 100 | 1.84 | 0 |
| green | 1 | 28,696 | 0.3 | 5.9 | 1.84 |
| green | 2 | 273,571 | 0.05 | 3.84 | 4.9 |
| green | 6 | 34,847 | 0.01 | 0 | 100 |

## `despacho_por_aplicacion`

- **Objetivo:** P11 Desde que aparece request_source (jun-2026), cuantos viajes se piden por app de terceros
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.40 s

```sql
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
```

| taxi_type | request_source | interpretacion | viajes | pct |
|---|---|---|---|---|
| yellow | NULL | NULL: sin app (probable parada en calle) | 7,647,917 | 74.34 |
| yellow | HV0003 | App Uber (licencia HVFHS) | 2,092,343 | 20.34 |
| yellow | A | Codigo A (no documentado por la TLC) | 363,662 | 3.54 |
| yellow | HV0005 | App Lyft (licencia HVFHS) | 162,313 | 1.58 |
| yellow | EH0004 | E-hail (base EH0004) | 19,594 | 0.19 |
| yellow | CC | Codigo CC (no documentado por la TLC) | 1,516 | 0.01 |
| yellow | EH0010 | E-hail (base EH0010) | 1 | 0 |
| green | NULL | NULL: sin app (probable parada en calle) | 101,977 | 84.59 |
| green | A | Codigo A (no documentado por la TLC) | 17,558 | 14.56 |
| green | HV0005 | App Lyft (licencia HVFHS) | 1,020 | 0.85 |
| green | CC | Codigo CC (no documentado por la TLC) | 3 | 0 |
