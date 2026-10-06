# Resultados de `sql/04_eda.sql`

Generado con `python scripts/sqlrun.py sql/04_eda.sql` (DuckDB 1.5.5). No editar a mano.

## `viajes_por_mes`

- **Objetivo:** P1 Como evoluciona la cantidad de viajes por mes y tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 4.15 s

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
| 2024-01-01 | yellow | 2,868,179 | 92,522 | 27.34 | 78.41 |
| 2024-01-01 | green | 53,318 | 1,720 | 22.19 | 1.18 |
| 2024-02-01 | yellow | 2,900,004 | 100,000 | 27.23 | 78.97 |
| 2024-02-01 | green | 50,398 | 1,738 | 22.48 | 1.13 |
| 2024-03-01 | yellow | 3,438,547 | 110,921 | 27.85 | 95.77 |
| 2024-03-01 | green | 54,102 | 1,745 | 22.76 | 1.23 |
| 2024-04-01 | yellow | 3,412,716 | 113,757 | 28.18 | 96.17 |
| 2024-04-01 | green | 52,943 | 1,765 | 23.29 | 1.23 |
| 2024-05-01 | yellow | 3,616,200 | 116,652 | 28.99 | 104.82 |
| 2024-05-01 | green | 57,478 | 1,854 | 24.5 | 1.41 |
| 2024-06-01 | yellow | 3,426,685 | 114,223 | 28.68 | 98.27 |
| 2024-06-01 | green | 51,683 | 1,723 | 24.79 | 1.28 |
| 2024-07-01 | yellow | 2,972,422 | 95,885 | 28.97 | 86.11 |
| 2024-07-01 | green | 48,501 | 1,565 | 24.49 | 1.19 |
| 2024-08-01 | yellow | 2,865,870 | 92,447 | 29.21 | 83.72 |
| 2024-08-01 | green | 48,690 | 1,571 | 25.9 | 1.26 |
| 2024-09-01 | yellow | 3,482,674 | 116,089 | 29.48 | 102.66 |
| 2024-09-01 | green | 51,298 | 1,710 | 26.54 | 1.36 |
| 2024-10-01 | yellow | 3,680,520 | 118,726 | 29.38 | 108.13 |
| 2024-10-01 | green | 53,182 | 1,716 | 25 | 1.33 |
| 2024-11-01 | yellow | 3,508,530 | 116,951 | 28.48 | 99.91 |
| 2024-11-01 | green | 49,076 | 1,636 | 24 | 1.18 |
| 2024-12-01 | yellow | 3,517,806 | 113,478 | 29.37 | 103.31 |
| 2024-12-01 | green | 50,604 | 1,632 | 23.82 | 1.21 |
| 2025-01-01 | yellow | 3,252,972 | 104,935 | 26.81 | 87.2 |
| 2025-01-01 | green | 45,260 | 1,460 | 22.56 | 1.02 |
| 2025-02-01 | yellow | 3,309,997 | 118,214 | 26.59 | 88.01 |
| 2025-02-01 | green | 43,650 | 1,559 | 22.92 | 1 |
| 2025-03-01 | yellow | 3,847,635 | 124,117 | 27.91 | 107.38 |
| 2025-03-01 | green | 48,093 | 1,551 | 23.96 | 1.15 |
| 2025-04-01 | yellow | 3,704,884 | 123,496 | 28.24 | 104.64 |
| 2025-04-01 | green | 48,527 | 1,618 | 24.55 | 1.19 |
| 2025-05-01 | yellow | 4,154,469 | 134,015 | 29.22 | 121.4 |
| 2025-05-01 | green | 51,941 | 1,676 | 25.34 | 1.32 |
| 2025-06-01 | yellow | 3,935,382 | 131,179 | 29.39 | 115.64 |
| 2025-06-01 | green | 47,029 | 1,568 | 25.78 | 1.21 |
| 2025-07-01 | yellow | 3,548,969 | 114,483 | 28.97 | 102.81 |
| 2025-07-01 | green | 46,397 | 1,497 | 25.67 | 1.19 |
| 2025-08-01 | yellow | 3,226,648 | 104,085 | 28.9 | 93.24 |
| 2025-08-01 | green | 44,530 | 1,436 | 27.69 | 1.23 |

*... 24 filas mas omitidas.*

## `demanda_por_dia_semana`

- **Objetivo:** P2 Que dias de la semana concentran la demanda (promedio diario)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 3.87 s

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
| yellow | 1 | Monday | 98,618 | 3.76 |
| yellow | 2 | Tuesday | 113,828 | 3.35 |
| yellow | 3 | Wednesday | 120,568 | 3.29 |
| yellow | 4 | Thursday | 126,165 | 3.35 |
| yellow | 5 | Friday | 120,228 | 3.41 |
| yellow | 6 | Saturday | 125,836 | 3.31 |
| yellow | 7 | Sunday | 106,856 | 3.89 |
| green | 1 | Monday | 1,538 | 3.07 |
| green | 2 | Tuesday | 1,631 | 3.06 |
| green | 3 | Wednesday | 1,696 | 3.06 |
| green | 4 | Thursday | 1,737 | 3.05 |
| green | 5 | Friday | 1,627 | 3.1 |
| green | 6 | Saturday | 1,345 | 3.25 |
| green | 7 | Sunday | 1,248 | 3.36 |

## `demanda_hora_dia`

- **Objetivo:** P2 Mapa de calor de viajes promedio por hora y dia de la semana (yellow + green)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 7.68 s

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
| 1 | 0 | 1,858 |
| 1 | 1 | 946 |
| 1 | 2 | 538 |
| 1 | 3 | 402 |
| 1 | 4 | 523 |
| 1 | 5 | 938 |
| 1 | 6 | 2,049 |
| 1 | 7 | 3,820 |
| 1 | 8 | 5,045 |
| 1 | 9 | 4,990 |
| 1 | 10 | 4,895 |
| 1 | 11 | 5,100 |
| 1 | 12 | 5,494 |
| 1 | 13 | 5,703 |
| 1 | 14 | 6,264 |
| 1 | 15 | 6,546 |
| 1 | 16 | 6,284 |
| 1 | 17 | 6,943 |
| 1 | 18 | 6,978 |
| 1 | 19 | 5,906 |
| 1 | 20 | 5,790 |
| 1 | 21 | 5,710 |
| 1 | 22 | 4,534 |
| 1 | 23 | 2,900 |
| 2 | 0 | 1,632 |
| 2 | 1 | 738 |
| 2 | 2 | 374 |
| 2 | 3 | 246 |
| 2 | 4 | 345 |
| 2 | 5 | 821 |
| 2 | 6 | 2,065 |
| 2 | 7 | 4,263 |
| 2 | 8 | 5,830 |
| 2 | 9 | 5,825 |
| 2 | 10 | 5,558 |
| 2 | 11 | 5,707 |
| 2 | 12 | 6,063 |
| 2 | 13 | 6,223 |
| 2 | 14 | 6,827 |
| 2 | 15 | 7,126 |

*... 128 filas mas omitidas.*

## `velocidad_por_hora`

- **Objetivo:** P3 Como cambian la velocidad y la duracion a lo largo del dia (congestion)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 6.13 s

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
| 0 | yellow | 3,418,974 | 12.9 | 2.4 | 11.9 |
| 1 | yellow | 2,239,653 | 12 | 2.3 | 12.3 |
| 2 | yellow | 1,468,594 | 11.5 | 2.3 | 12.8 |
| 3 | yellow | 998,990 | 11.5 | 2.51 | 13.8 |
| 4 | yellow | 777,525 | 12.9 | 3.26 | 15.5 |
| 5 | yellow | 848,347 | 13.1 | 3.52 | 16.3 |
| 6 | yellow | 1,734,036 | 11.8 | 2.66 | 14 |
| 7 | yellow | 3,217,545 | 12.1 | 2.1 | 11.2 |
| 8 | yellow | 4,379,860 | 13.2 | 1.87 | 9.3 |
| 9 | yellow | 4,706,133 | 13.4 | 1.77 | 9 |
| 10 | yellow | 4,931,790 | 13.6 | 1.71 | 8.7 |
| 11 | yellow | 5,322,467 | 14.2 | 1.69 | 8.2 |
| 12 | yellow | 5,788,678 | 14.3 | 1.68 | 8.2 |
| 13 | yellow | 6,043,413 | 14.5 | 1.7 | 8.2 |
| 14 | yellow | 6,499,403 | 14.9 | 1.74 | 8.1 |
| 15 | yellow | 6,728,046 | 14.9 | 1.71 | 8 |
| 16 | yellow | 6,629,339 | 14.6 | 1.7 | 8.2 |
| 17 | yellow | 7,293,740 | 14.2 | 1.68 | 8.1 |
| 18 | yellow | 7,609,013 | 13.3 | 1.65 | 8.5 |
| 19 | yellow | 6,825,670 | 13 | 1.72 | 9.1 |
| 20 | yellow | 6,517,604 | 13 | 1.95 | 9.9 |
| 21 | yellow | 6,689,281 | 13.2 | 2.07 | 10.3 |
| 22 | yellow | 6,211,072 | 13.5 | 2.2 | 10.7 |
| 23 | yellow | 4,859,604 | 13.5 | 2.37 | 11.3 |
| 0 | green | 23,939 | 11.1 | 2.28 | 12.5 |
| 1 | green | 15,839 | 11.1 | 2.33 | 12.7 |
| 2 | green | 11,071 | 12.2 | 2.8 | 13.5 |
| 3 | green | 8484 | 13 | 3.2 | 14.4 |
| 4 | green | 7636 | 14 | 3.83 | 15.7 |
| 5 | green | 9212 | 12.3 | 3.62 | 16.3 |
| 6 | green | 25,906 | 10.3 | 1.91 | 12.7 |
| 7 | green | 57,544 | 12.1 | 1.89 | 10.4 |
| 8 | green | 74,089 | 13.3 | 1.94 | 9.6 |
| 9 | green | 79,437 | 13.1 | 2.08 | 10.1 |
| 10 | green | 78,454 | 13.1 | 2.15 | 10.1 |
| 11 | green | 78,294 | 13.6 | 2.22 | 9.9 |
| 12 | green | 83,280 | 13.4 | 2.17 | 9.9 |
| 13 | green | 83,914 | 13.3 | 2.11 | 9.8 |
| 14 | green | 95,011 | 13.9 | 2.08 | 9.3 |
| 15 | green | 103,648 | 13.5 | 2 | 9.2 |

*... 8 filas mas omitidas.*

## `comparacion_tipos`

- **Objetivo:** P4 Perfil general de un viaje yellow vs green
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 28.40 s

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
| yellow | 112,980,446 | 3.47 | 1.86 | 13.5 | 1.3 | 14.4 | 22.07 | 7.35 | 4 |
| green | 1,505,944 | 3.12 | 2.04 | 12.5 | 1.31 | 13.5 | 19.85 | 6.77 | 9.6 |

## `percentiles_distancia_duracion`

- **Objetivo:** P4 Distribucion (percentiles) de distancia, duracion y total por tipo
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 28.99 s

```sql
-- Los cuantiles se calculan columna por columna en una sola pasada y solo despues
-- se "despivotean" las 2 filas resultantes. (Una version anterior hacia UNPIVOT de
-- los datos crudos: con 3 anios generaba ~360 M de filas intermedias y agotaba la memoria.)
WITH q AS (
    SELECT taxi_type,
           QUANTILE_CONT(trip_distance, [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) AS trip_distance,
           QUANTILE_CONT(duration_min,  [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) AS duration_min,
           QUANTILE_CONT(total_amount,  [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) AS total_amount
    FROM trips_clean
    GROUP BY taxi_type
)
SELECT taxi_type, variable,
       ROUND(v[1], 2) AS p05, ROUND(v[2], 2) AS p25, ROUND(v[3], 2) AS p50,
       ROUND(v[4], 2) AS p75, ROUND(v[5], 2) AS p95, ROUND(v[6], 2) AS p99
FROM (UNPIVOT q ON trip_distance, duration_min, total_amount INTO NAME variable VALUE v)
ORDER BY variable, taxi_type DESC;
```

| taxi_type | variable | p05 | p25 | p50 | p75 | p95 | p99 |
|---|---|---|---|---|---|---|---|
| yellow | duration_min | 3.88 | 8.25 | 13.52 | 21.6 | 44.03 | 70.9 |
| green | duration_min | 3.85 | 8.15 | 12.5 | 19 | 38.17 | 65.3 |
| yellow | total_amount | 11.8 | 16.65 | 22.07 | 31.98 | 80.15 | 104.88 |
| green | total_amount | 9.4 | 14.38 | 19.85 | 28.86 | 56.55 | 95.67 |
| yellow | trip_distance | 0.51 | 1.09 | 1.86 | 3.66 | 13.35 | 19.79 |
| green | trip_distance | 0.6 | 1.29 | 2.04 | 3.57 | 9.58 | 17.24 |

## `histograma_distancia`

- **Objetivo:** P4 Histograma de distancia (bins de 1 milla hasta 30; el resto en 30+)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 3.97 s

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
| yellow | 0 | 24,104,565 | 21.34 |
| yellow | 1 | 35,823,303 | 31.71 |
| yellow | 2 | 18,125,403 | 16.04 |
| yellow | 3 | 9,003,830 | 7.97 |
| yellow | 4 | 5,137,575 | 4.55 |
| yellow | 5 | 3,436,251 | 3.04 |
| yellow | 6 | 2,499,016 | 2.21 |
| yellow | 7 | 1,959,825 | 1.73 |
| yellow | 8 | 1,975,242 | 1.75 |
| yellow | 9 | 1,915,376 | 1.7 |
| yellow | 10 | 1,494,183 | 1.32 |
| yellow | 11 | 1,054,365 | 0.93 |
| yellow | 12 | 626,888 | 0.55 |
| yellow | 13 | 445,592 | 0.39 |
| yellow | 14 | 410,348 | 0.36 |
| yellow | 15 | 467,477 | 0.41 |
| yellow | 16 | 820,780 | 0.73 |
| yellow | 17 | 1,230,043 | 1.09 |
| yellow | 18 | 894,398 | 0.79 |
| yellow | 19 | 513,212 | 0.45 |
| yellow | 20 | 343,311 | 0.3 |
| yellow | 21 | 187,909 | 0.17 |
| yellow | 22 | 92,787 | 0.08 |
| yellow | 23 | 57,015 | 0.05 |
| yellow | 24 | 45,259 | 0.04 |
| yellow | 25 | 46,625 | 0.04 |
| yellow | 26 | 55,057 | 0.05 |
| yellow | 27 | 45,380 | 0.04 |
| yellow | 28 | 36,164 | 0.03 |
| yellow | 29 | 21,897 | 0.02 |
| yellow | 30 | 111,370 | 0.1 |
| green | 0 | 224,484 | 14.91 |
| green | 1 | 510,166 | 33.88 |
| green | 2 | 299,767 | 19.91 |
| green | 3 | 158,671 | 10.54 |
| green | 4 | 72,810 | 4.83 |
| green | 5 | 50,402 | 3.35 |
| green | 6 | 47,178 | 3.13 |
| green | 7 | 33,127 | 2.2 |
| green | 8 | 23,645 | 1.57 |

*... 22 filas mas omitidas.*

## `pasajeros`

- **Objetivo:** P4 Distribucion de la cantidad de pasajeros
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 4.09 s

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
| yellow | 0 | 721,290 | 0.64 |
| yellow | 1 | 74,035,336 | 65.53 |
| yellow | 2 | 12,831,834 | 11.36 |
| yellow | 3 | 2,993,469 | 2.65 |
| yellow | 4 | 1,922,274 | 1.7 |
| yellow | 5 | 542,699 | 0.48 |
| yellow | 6 | 345,184 | 0.31 |
| yellow | 7 | 46 | 0 |
| yellow | 8 | 158 | 0 |
| yellow | 9 | 37 | 0 |
| yellow | sin dato | 19,588,119 | 17.34 |
| green | 0 | 18,300 | 1.22 |
| green | 1 | 1,150,688 | 76.41 |
| green | 2 | 137,805 | 9.15 |
| green | 3 | 15,522 | 1.03 |
| green | 4 | 8410 | 0.56 |
| green | 5 | 32,679 | 2.17 |
| green | 6 | 23,595 | 1.57 |
| green | 7 | 113 | 0.01 |
| green | 8 | 135 | 0.01 |
| green | 9 | 79 | 0.01 |
| green | sin dato | 118,618 | 7.88 |

## `zonas_origen_borough`

- **Objetivo:** P5 En que borough comienzan los viajes de cada tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + data/raw/misc/taxi_zone_lookup.csv (zones)
- **Tiempo:** 4.23 s

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
| yellow | Manhattan | 98,640,354 | 87.31 |
| yellow | Queens | 10,367,921 | 9.18 |
| yellow | Brooklyn | 3,045,786 | 2.7 |
| yellow | Bronx | 672,468 | 0.6 |
| yellow | Unknown | 217,846 | 0.19 |
| yellow | N/A | 24,742 | 0.02 |
| yellow | Staten Island | 7811 | 0.01 |
| yellow | EWR | 3518 | 0 |
| green | Manhattan | 912,949 | 60.62 |
| green | Queens | 350,214 | 23.26 |
| green | Brooklyn | 216,107 | 14.35 |
| green | Bronx | 24,435 | 1.62 |
| green | Unknown | 1419 | 0.09 |
| green | N/A | 699 | 0.05 |
| green | Staten Island | 117 | 0.01 |
| green | EWR | 4 | 0 |

## `top_zonas_origen`

- **Objetivo:** P5 Las 8 zonas de origen mas frecuentes por tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
- **Tiempo:** 4.27 s

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
| yellow | Manhattan | Upper East Side South | 5,185,831 | 4.59 |
| yellow | Manhattan | Midtown Center | 5,025,590 | 4.45 |
| yellow | Queens | JFK Airport | 4,897,816 | 4.34 |
| yellow | Manhattan | Upper East Side North | 4,611,553 | 4.08 |
| yellow | Manhattan | Midtown East | 3,694,645 | 3.27 |
| yellow | Manhattan | Penn Station/Madison Sq West | 3,670,049 | 3.25 |
| yellow | Manhattan | Times Sq/Theatre District | 3,574,653 | 3.16 |
| yellow | Manhattan | Lincoln Square East | 3,415,503 | 3.02 |
| green | Manhattan | East Harlem North | 376,467 | 25 |
| green | Manhattan | East Harlem South | 212,669 | 14.12 |
| green | Queens | Forest Hills | 72,839 | 4.84 |
| green | Manhattan | Central Park | 72,330 | 4.8 |
| green | Manhattan | Morningside Heights | 71,258 | 4.73 |
| green | Manhattan | Central Harlem | 62,021 | 4.12 |
| green | Queens | Elmhurst | 61,131 | 4.06 |
| green | Brooklyn | Fort Greene | 49,052 | 3.26 |

## `aeropuertos`

- **Objetivo:** P6 Peso y precio de los viajes que salen de los aeropuertos (JFK 132, LGA 138, EWR 1)
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + taxi_zone_lookup.csv (zones)
- **Tiempo:** 10.55 s

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
| yellow | No aeropuerto | 104,853,153 | 92.81 | 1.7 | 21.2 |
| yellow | JFK Airport | 4,897,816 | 4.34 | 17.2 | 88.21 |
| yellow | LaGuardia Airport | 3,225,959 | 2.86 | 9.4 | 69.01 |
| yellow | Newark Airport | 3518 | 0 | 0.1 | 116.38 |
| green | No aeropuerto | 1,505,173 | 99.95 | 2 | 19.85 |
| green | JFK Airport | 417 | 0.03 | 2.3 | 33.6 |
| green | LaGuardia Airport | 350 | 0.02 | 3.6 | 47.65 |
| green | Newark Airport | 4 | 0 | 0.5 | 113 |

## `metodo_pago`

- **Objetivo:** P7 Distribucion de metodos de pago por tipo de taxi
- **Fuente:** data/raw/*/*/*.parquet (trips_clean) + catalogo payment_types
- **Tiempo:** 6.81 s

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
| yellow | Tarjeta | 79,723,045 | 70.56 | 22 |
| yellow | Flex Fare / sin dato | 19,588,119 | 17.34 | 25.09 |
| yellow | Efectivo | 12,243,273 | 10.84 | 17.9 |
| yellow | Disputa | 1,043,657 | 0.92 | 18.6 |
| yellow | Sin cargo | 382,350 | 0.34 | 16.5 |
| yellow | Desconocido | 2 | 0 | 35.99 |
| green | Tarjeta | 1,025,772 | 68.11 | 20.82 |
| green | Efectivo | 355,327 | 23.59 | 15.7 |
| green | NULL / sin dato | 118,618 | 7.88 | 25.92 |
| green | Sin cargo | 4613 | 0.31 | 7.6 |
| green | Disputa | 1572 | 0.1 | 7.7 |
| green | Desconocido | 42 | 0 | 11.35 |

## `metodo_pago_por_mes`

- **Objetivo:** P7 Evolucion mensual de la participacion de tarjeta, efectivo y sin dato
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 4.09 s

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
| 2024-01-01 | yellow | 80.09 | 14.73 | 4.02 |
| 2024-02-01 | yellow | 80.03 | 13.66 | 5.13 |
| 2024-03-01 | yellow | 74.87 | 13.3 | 10.62 |
| 2024-04-01 | yellow | 74.26 | 13.19 | 11.39 |
| 2024-05-01 | yellow | 74.78 | 13.29 | 10.71 |
| 2024-06-01 | yellow | 74.32 | 13.08 | 11.31 |
| 2024-07-01 | yellow | 75.04 | 14.57 | 8.85 |
| 2024-08-01 | yellow | 75.11 | 14.91 | 8.32 |
| 2024-09-01 | yellow | 74.08 | 12.13 | 12.37 |
| 2024-10-01 | yellow | 76.83 | 12.3 | 9.38 |
| 2024-11-01 | yellow | 76.83 | 12.13 | 9.58 |
| 2024-12-01 | yellow | 76.97 | 13.16 | 8.23 |
| 2025-01-01 | yellow | 74.51 | 11.31 | 12.7 |
| 2025-02-01 | yellow | 69.98 | 9.62 | 18.98 |
| 2025-03-01 | yellow | 69.7 | 9.88 | 18.87 |
| 2025-04-01 | yellow | 71.89 | 10.44 | 15.97 |
| 2025-05-01 | yellow | 67.84 | 9.41 | 21.12 |
| 2025-06-01 | yellow | 65.41 | 9.16 | 23.8 |
| 2025-07-01 | yellow | 65.48 | 10.09 | 22.57 |
| 2025-08-01 | yellow | 66.99 | 10.69 | 20.23 |
| 2025-09-01 | yellow | 68.14 | 8.88 | 21.26 |
| 2025-10-01 | yellow | 72.12 | 9.33 | 17.04 |
| 2025-11-01 | yellow | 72.36 | 9.56 | 16.86 |
| 2025-12-01 | yellow | 63.16 | 9.27 | 26.44 |
| 2026-01-01 | yellow | 62.64 | 8.36 | 27.95 |
| 2026-02-01 | yellow | 62.6 | 8.01 | 28.58 |
| 2026-03-01 | yellow | 67.9 | 8.91 | 22.57 |
| 2026-04-01 | yellow | 70.22 | 9.37 | 19.89 |
| 2026-05-01 | yellow | 68.26 | 9.07 | 22.18 |
| 2026-06-01 | yellow | 65.21 | 9.32 | 24.97 |
| 2026-07-01 | yellow | 63.72 | 9.84 | 25.92 |
| 2026-08-01 | yellow | 63.34 | 9.92 | 26.2 |
| 2024-01-01 | green | 68.95 | 30.49 | 6.13 |
| 2024-02-01 | green | 69.86 | 29.67 | 5.62 |
| 2024-03-01 | green | 68.79 | 30.81 | 3.77 |
| 2024-04-01 | green | 71.49 | 28.08 | 3.65 |
| 2024-05-01 | green | 71.44 | 28.09 | 3.2 |
| 2024-06-01 | green | 71.55 | 28 | 3.53 |
| 2024-07-01 | green | 71.29 | 28.24 | 3.18 |
| 2024-08-01 | green | 71.5 | 27.93 | 3.14 |

*... 24 filas mas omitidas.*

## `propinas`

- **Objetivo:** P8 Propina como % de la tarifa (solo tarjeta: el efectivo no registra propina)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 6.89 s

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
| green | 1,025,747 | 91.3 | 3.72 | 23.5 | 24.7 |
| yellow | 79,722,275 | 93 | 4.32 | 26.2 | 27.2 |

## `propina_por_hora`

- **Objetivo:** P8 Cambia la propina segun la hora del dia (yellow, tarjeta)
- **Fuente:** data/raw/yellow/*/*.parquet (vista trips_clean)
- **Tiempo:** 3.57 s

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
| 0 | 2,100,914 | 24.8 |
| 1 | 1,362,843 | 24.7 |
| 2 | 874,101 | 25.3 |
| 3 | 555,123 | 25.2 |
| 4 | 355,500 | 28.1 |
| 5 | 427,406 | 22.1 |
| 6 | 1,001,915 | 22.1 |
| 7 | 2,094,064 | 23.5 |
| 8 | 2,973,395 | 24.5 |
| 9 | 3,396,646 | 24.3 |
| 10 | 3,662,542 | 24.8 |
| 11 | 3,953,960 | 24.9 |
| 12 | 4,275,124 | 24.2 |
| 13 | 4,451,997 | 24.2 |
| 14 | 4,800,924 | 24.6 |
| 15 | 4,994,997 | 24.2 |
| 16 | 5,135,528 | 26.1 |
| 17 | 5,630,069 | 26.5 |
| 18 | 5,826,939 | 27 |
| 19 | 5,139,372 | 27.3 |
| 20 | 4,680,264 | 26 |
| 21 | 4,743,391 | 25.8 |
| 22 | 4,197,283 | 25.6 |
| 23 | 3,087,978 | 24.9 |

## `recargos`

- **Objetivo:** P9 Cuanto pesan los recargos (congestion, CBD, aeropuerto) en el total pagado
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 4.40 s

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
| green | 9.2 | 32.2 | NULL | 24.79 | 17.73 | 70.5 |
| yellow | 72.8 | 91.6 | 8.8 | 29.1 | 20.23 | 65.9 |

## `velocidades_imposibles`

- **Objetivo:** P10 Viajes con velocidades fisicamente imposibles (> 80 mph) aun despues de limpiar
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 3.88 s

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
| green | 6332 | 17,797 | 1,505,944 | 0.42 |
| yellow | 30,495 | 353,320 | 112,980,446 | 0.027 |

## `atipicos_iqr_tarifa_por_milla`

- **Objetivo:** P10 Atipicos de tarifa por milla segun la regla de Tukey (Q1 - 1.5 IQR, Q3 + 1.5 IQR)
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 11.80 s

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
| yellow | 5.6 | 9.18 | 14.54 | 4,163,596 | 144,504 | 3.98 |
| green | 5.56 | 8.03 | 11.74 | 50,738 | 57,513 | 7.43 |

## `registros_invalidos_por_mes`

- **Objetivo:** P10 Los registros invalidos (descartados por trips_clean) se concentran en algun mes o proveedor?
- **Fuente:** data/raw/*/*/*.parquet (vista trips, sin limpiar)
- **Tiempo:** 3.30 s

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
| 202,401 | yellow | 2,964,624 | 1.2 | 2.04 | 0.03 |
| 202,402 | yellow | 3,007,526 | 1.2 | 2.27 | 0.03 |
| 202,403 | yellow | 3,582,628 | 1.24 | 2.43 | 0.03 |
| 202,404 | yellow | 3,514,289 | 1.24 | 1.3 | 0.03 |
| 202,405 | yellow | 3,723,833 | 1.32 | 1.34 | 0.03 |
| 202,406 | yellow | 3,539,193 | 1.38 | 1.5 | 0.03 |
| 202,407 | yellow | 3,076,903 | 1.64 | 1.56 | 0.03 |
| 202,408 | yellow | 2,979,183 | 1.78 | 1.93 | 0.03 |
| 202,409 | yellow | 3,633,030 | 1.54 | 2.23 | 0.03 |
| 202,410 | yellow | 3,833,771 | 1.6 | 2.13 | 0.03 |
| 202,411 | yellow | 3,646,369 | 1.66 | 1.87 | 0.05 |
| 202,412 | yellow | 3,668,371 | 1.92 | 2.06 | 0.03 |
| 202,501 | yellow | 3,475,226 | 1.81 | 2.62 | 0.06 |
| 202,502 | yellow | 3,577,543 | 1.54 | 2.79 | 0.14 |
| 202,503 | yellow | 4,145,257 | 1.66 | 2.5 | 0.54 |
| 202,504 | yellow | 3,970,553 | 1.83 | 2.3 | 0.88 |
| 202,505 | yellow | 4,591,845 | 2.45 | 3.07 | 1.4 |
| 202,506 | yellow | 4,322,960 | 1.72 | 3.12 | 1.59 |
| 202,507 | yellow | 3,898,963 | 1.96 | 3.17 | 1.44 |
| 202,508 | yellow | 3,574,091 | 2.46 | 2.94 | 1.34 |
| 202,509 | yellow | 4,251,015 | 1.85 | 2.93 | 1.35 |
| 202,510 | yellow | 4,428,699 | 2.46 | 2.84 | 1.53 |
| 202,511 | yellow | 4,181,444 | 3.04 | 2.62 | 1.49 |
| 202,512 | yellow | 4,305,006 | 1.14 | 3.55 | 1.35 |
| 202,601 | yellow | 3,724,889 | 1.07 | 3.38 | 1.21 |
| 202,602 | yellow | 3,399,866 | 0.8 | 3.63 | 1.19 |
| 202,603 | yellow | 3,952,451 | 0.54 | 3.07 | 1.24 |
| 202,604 | yellow | 3,831,240 | 0.39 | 2.44 | 1.29 |
| 202,605 | yellow | 4,090,836 | 0.36 | 2.76 | 1.27 |
| 202,606 | yellow | 3,837,248 | 0.37 | 3.34 | 1.3 |
| 202,607 | yellow | 3,530,109 | 0.42 | 3.64 | 1.2 |
| 202,608 | yellow | 3,336,716 | 0.43 | 3.57 | 1.29 |
| 202,401 | green | 56,551 | 0.33 | 5.08 | 0.13 |
| 202,402 | green | 53,577 | 0.33 | 5.31 | 0.09 |
| 202,403 | green | 57,457 | 0.34 | 5.26 | 0.06 |
| 202,404 | green | 56,471 | 0.38 | 5.66 | 0.12 |
| 202,405 | green | 61,003 | 0.37 | 5.09 | 0.09 |
| 202,406 | green | 54,748 | 0.33 | 4.98 | 0.1 |
| 202,407 | green | 51,837 | 0.35 | 5.76 | 0.11 |
| 202,408 | green | 51,771 | 0.35 | 5.19 | 0.1 |

*... 24 filas mas omitidas.*

## `invalidos_por_proveedor`

- **Objetivo:** P10 Que proveedor (VendorID) genera los registros con duracion o distancia invalida
- **Fuente:** data/raw/*/*/*.parquet (vista trips, sin limpiar)
- **Tiempo:** 3.01 s

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
| yellow | 1 | 24,769,862 | 0.09 | 2.19 | 13.48 |
| yellow | 2 | 93,837,123 | 0 | 2.74 | 21.31 |
| yellow | 6 | 85,441 | 1.44 | 0 | 100 |
| yellow | 7 | 903,251 | 100 | 1.63 | 0 |
| green | 1 | 174,635 | 0.38 | 14.55 | 1.49 |
| green | 2 | 1,352,140 | 0.06 | 3.39 | 4.32 |
| green | 6 | 61,932 | 2.24 | 0 | 100 |

## `despacho_por_aplicacion`

- **Objetivo:** P11 Desde que aparece request_source (jun-2026), cuantos viajes se piden por app de terceros
- **Fuente:** data/raw/*/*/*.parquet (vista trips_clean)
- **Tiempo:** 0.87 s

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
| yellow | CC | Codigo CC (no documentado por la TLC) | 1516 | 0.01 |
| yellow | EH0010 | E-hail (base EH0010) | 1 | 0 |
| green | NULL | NULL: sin app (probable parada en calle) | 101,977 | 84.59 |
| green | A | Codigo A (no documentado por la TLC) | 17,558 | 14.56 |
| green | HV0005 | App Lyft (licencia HVFHS) | 1020 | 0.85 |
| green | CC | Codigo CC (no documentado por la TLC) | 3 | 0 |
