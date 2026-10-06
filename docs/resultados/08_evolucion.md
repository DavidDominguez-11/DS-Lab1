# Resultados de `sql/08_evolucion.sql`

Generado con `python scripts/sqlrun.py sql/08_evolucion.sql` (DuckDB 1.5.5). No editar a mano.

## `E1_resumen_anual`

- **Tiempo:** 8.99 s

```sql
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
```

| anio | taxi_type | viajes_por_dia | ingreso_diario_musd | ticket_mediano | distancia_mediana | tarifa_por_milla | pct_tarjeta | pct_sin_dato_pago | pct_paga_cbd | propina_pct_mediana |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | yellow | 104,511 | 2.96 | 21 | 1.8 | 7.14 | 75.9 | 9 | 0 | 25.9 |
| 2025 | yellow | 119,263 | 3.376 | 21.57 | 1.87 | 7.04 | 68.9 | 19.4 | 73 | 26.7 |
| 2026 | yellow | 117,681 | 3.553 | 23.58 | 1.92 | 7.38 | 65.6 | 24.6 | 72.4 | 26.4 |
| 2024 | green | 1,709 | 0.041 | 19.15 | 1.96 | 6.72 | 70.6 | 4 | 0 | 23.5 |
| 2025 | green | 1,545 | 0.038 | 19.7 | 2.02 | 6.69 | 74.7 | 6.9 | 9.7 | 23.4 |
| 2026 | green | 1,330 | 0.034 | 20.52 | 2.14 | 6.62 | 76.9 | 14.8 | 8.5 | 23.5 |

## `E2_variacion_interanual`

- **Tiempo:** 1.97 s

```sql
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
```

| mes | taxi_type | variacion_pct |
|---|---|---|
| 2025-01-01 | green | -15.1 |
| 2025-01-01 | yellow | 13.4 |
| 2025-02-01 | green | -10.3 |
| 2025-02-01 | yellow | 18.2 |
| 2025-03-01 | green | -11.1 |
| 2025-03-01 | yellow | 11.9 |
| 2025-04-01 | green | -8.3 |
| 2025-04-01 | yellow | 8.6 |
| 2025-05-01 | green | -9.6 |
| 2025-05-01 | yellow | 14.9 |
| 2025-06-01 | green | -9 |
| 2025-06-01 | yellow | 14.8 |
| 2025-07-01 | green | -4.3 |
| 2025-07-01 | yellow | 19.4 |
| 2025-08-01 | green | -8.5 |
| 2025-08-01 | yellow | 12.6 |
| 2025-09-01 | green | -8 |
| 2025-09-01 | yellow | 11.8 |
| 2025-10-01 | green | -10.6 |
| 2025-10-01 | yellow | 9 |
| 2025-11-01 | green | -8.1 |
| 2025-11-01 | yellow | 5.5 |
| 2025-12-01 | green | -8.5 |
| 2025-12-01 | yellow | 16.7 |
| 2026-01-01 | green | -14.3 |
| 2026-01-01 | yellow | 9.5 |
| 2026-02-01 | green | -18 |
| 2026-02-01 | yellow | -1.8 |
| 2026-03-01 | green | -11.6 |
| 2026-03-01 | yellow | -1 |
| 2026-04-01 | green | -12.7 |
| 2026-04-01 | yellow | 0.5 |
| 2026-05-01 | green | -17 |
| 2026-05-01 | yellow | -4.6 |
| 2026-06-01 | green | -9.7 |
| 2026-06-01 | yellow | -6.1 |
| 2026-07-01 | green | -15.1 |
| 2026-07-01 | yellow | -4.5 |
| 2026-08-01 | green | -13.1 |
| 2026-08-01 | yellow | -0.7 |

## `E3_cuota_green`

- **Tiempo:** 1.23 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       ROUND(100.0 * AVG((taxi_type = 'green')::INT), 2) AS pct_green
FROM trips_clean
GROUP BY 1 ORDER BY 1;
```

| mes | pct_green |
|---|---|
| 2024-01-01 | 1.83 |
| 2024-02-01 | 1.71 |
| 2024-03-01 | 1.55 |
| 2024-04-01 | 1.53 |
| 2024-05-01 | 1.56 |
| 2024-06-01 | 1.49 |
| 2024-07-01 | 1.61 |
| 2024-08-01 | 1.67 |
| 2024-09-01 | 1.45 |
| 2024-10-01 | 1.42 |
| 2024-11-01 | 1.38 |
| 2024-12-01 | 1.42 |
| 2025-01-01 | 1.37 |
| 2025-02-01 | 1.3 |
| 2025-03-01 | 1.23 |
| 2025-04-01 | 1.29 |
| 2025-05-01 | 1.23 |
| 2025-06-01 | 1.18 |
| 2025-07-01 | 1.29 |
| 2025-08-01 | 1.36 |
| 2025-09-01 | 1.2 |
| 2025-10-01 | 1.17 |
| 2025-11-01 | 1.2 |
| 2025-12-01 | 1.12 |
| 2026-01-01 | 1.08 |
| 2026-02-01 | 1.09 |
| 2026-03-01 | 1.1 |
| 2026-04-01 | 1.13 |
| 2026-05-01 | 1.08 |
| 2026-06-01 | 1.14 |
| 2026-07-01 | 1.15 |
| 2026-08-01 | 1.19 |

## `E4_velocidad_por_anio`

- **Tiempo:** 1.57 s

```sql
SELECT pickup_hour AS hora, source_year::VARCHAR AS anio,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 2) AS velocidad_mediana_mph
FROM trips_clean
WHERE taxi_type = 'yellow' AND duration_min >= 1 AND source_month <= 8
GROUP BY ALL ORDER BY hora, anio;
```

| hora | anio | velocidad_mediana_mph |
|---|---|---|
| 0 | 2024 | 12.09 |
| 0 | 2025 | 12.28 |
| 0 | 2026 | 11.82 |
| 1 | 2024 | 12.32 |
| 1 | 2025 | 12.59 |
| 1 | 2026 | 12.3 |
| 2 | 2024 | 12.71 |
| 2 | 2025 | 13.02 |
| 2 | 2026 | 12.9 |
| 3 | 2024 | 13.68 |
| 3 | 2025 | 13.98 |
| 3 | 2026 | 13.81 |
| 4 | 2024 | 15.57 |
| 4 | 2025 | 15.71 |
| 4 | 2026 | 15.38 |
| 5 | 2024 | 16.55 |
| 5 | 2025 | 16.62 |
| 5 | 2026 | 16.01 |
| 6 | 2024 | 14.19 |
| 6 | 2025 | 14.24 |
| 6 | 2026 | 13.8 |
| 7 | 2024 | 11.39 |
| 7 | 2025 | 11.45 |
| 7 | 2026 | 11.08 |
| 8 | 2024 | 9.39 |
| 8 | 2025 | 9.57 |
| 8 | 2026 | 9.3 |
| 9 | 2024 | 9.01 |
| 9 | 2025 | 9.16 |
| 9 | 2026 | 8.85 |
| 10 | 2024 | 8.86 |
| 10 | 2025 | 8.92 |
| 10 | 2026 | 8.57 |
| 11 | 2024 | 8.4 |
| 11 | 2025 | 8.5 |
| 11 | 2026 | 8.15 |
| 12 | 2024 | 8.37 |
| 12 | 2025 | 8.45 |
| 12 | 2026 | 8.07 |
| 13 | 2024 | 8.48 |

*... 32 filas mas omitidas.*

## `E5_velocidad_cbd`

- **Tiempo:** 1.77 s

```sql
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
```

| anio | grupo | velocidad_mediana_mph | viajes |
|---|---|---|---|
| 2024 | Manhattan (sin peaje aun) | 7.77 | 10,304,678 |
| 2025 | No paga cargo CBD | 8.49 | 2,699,258 |
| 2025 | Paga cargo CBD | 7.51 | 8,157,326 |
| 2026 | No paga cargo CBD | 8.14 | 2,716,032 |
| 2026 | Paga cargo CBD | 7.06 | 7,738,384 |

## `E6_composicion_del_ticket`

- **Tiempo:** 1.33 s

```sql
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
```

| anio | tarifa | propina | peajes | recargo_congestion | cargo_cbd | cargo_aeropuerto | otros | total_registrado |
|---|---|---|---|---|---|---|---|---|
| 2024 | 19.43 | 3.64 | 0.61 | 2.32 | 0 | 0.15 | 3.08 | 28.67 |
| 2025 | 19.17 | 3.74 | 0.57 | 2.31 | 0.56 | 0.15 | 3.1 | 28.99 |
| 2026 | 19.72 | 3.74 | 0.59 | 2.26 | 0.55 | 0.17 | 2.98 | 29.48 |

## `E7_sin_dato_por_proveedor`

- **Tiempo:** 1.54 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       'Vendor ' || vendor_id AS proveedor,
       ROUND(100.0 * AVG((payment_type = 0)::INT), 1) AS pct_sin_dato
FROM trips_clean
WHERE taxi_type = 'yellow' AND vendor_id IN (1, 2)
GROUP BY ALL ORDER BY mes, proveedor;
```

| mes | proveedor | pct_sin_dato |
|---|---|---|
| 2024-01-01 | Vendor 1 | 3.8 |
| 2024-01-01 | Vendor 2 | 4.1 |
| 2024-02-01 | Vendor 1 | 3.8 |
| 2024-02-01 | Vendor 2 | 5.5 |
| 2024-03-01 | Vendor 1 | 7.4 |
| 2024-03-01 | Vendor 2 | 11.6 |
| 2024-04-01 | Vendor 1 | 10.7 |
| 2024-04-01 | Vendor 2 | 11.6 |
| 2024-05-01 | Vendor 1 | 9.4 |
| 2024-05-01 | Vendor 2 | 11.1 |
| 2024-06-01 | Vendor 1 | 9.5 |
| 2024-06-01 | Vendor 2 | 11.9 |
| 2024-07-01 | Vendor 1 | 7.6 |
| 2024-07-01 | Vendor 2 | 9.2 |
| 2024-08-01 | Vendor 1 | 6.9 |
| 2024-08-01 | Vendor 2 | 8.8 |
| 2024-09-01 | Vendor 1 | 10 |
| 2024-09-01 | Vendor 2 | 13.1 |
| 2024-10-01 | Vendor 1 | 7.2 |
| 2024-10-01 | Vendor 2 | 10.1 |
| 2024-11-01 | Vendor 1 | 8.3 |
| 2024-11-01 | Vendor 2 | 10 |
| 2024-12-01 | Vendor 1 | 8 |
| 2024-12-01 | Vendor 2 | 8.3 |
| 2025-01-01 | Vendor 1 | 11.6 |
| 2025-01-01 | Vendor 2 | 13 |
| 2025-02-01 | Vendor 1 | 14.8 |
| 2025-02-01 | Vendor 2 | 20.2 |
| 2025-03-01 | Vendor 1 | 15.9 |
| 2025-03-01 | Vendor 2 | 19.8 |
| 2025-04-01 | Vendor 1 | 14.7 |
| 2025-04-01 | Vendor 2 | 16.5 |
| 2025-05-01 | Vendor 1 | 18.4 |
| 2025-05-01 | Vendor 2 | 22.3 |
| 2025-06-01 | Vendor 1 | 20.2 |
| 2025-06-01 | Vendor 2 | 25.3 |
| 2025-07-01 | Vendor 1 | 19.6 |
| 2025-07-01 | Vendor 2 | 23.7 |
| 2025-08-01 | Vendor 1 | 14.5 |
| 2025-08-01 | Vendor 2 | 22 |

*... 24 filas mas omitidas.*

## `E8_aeropuertos_por_anio`

- **Tiempo:** 0.91 s

```sql
SELECT t.source_year::VARCHAR AS anio, z.zone AS aeropuerto,
       ROUND(COUNT(*) / ANY_VALUE(d.dias), 0) AS viajes_por_dia
FROM trips_clean t
JOIN zones z ON z.location_id = t.pu_location_id
JOIN (SELECT source_year, COUNT(DISTINCT pickup_date) AS dias FROM trips_clean
      WHERE source_month <= 8 GROUP BY 1) d USING (source_year)
WHERE z.zone IN ('JFK Airport', 'LaGuardia Airport') AND t.source_month <= 8
GROUP BY 1, 2 ORDER BY 1, 2;
```

| anio | aeropuerto | viajes_por_dia |
|---|---|---|
| 2024 | JFK Airport | 4,956 |
| 2024 | LaGuardia Airport | 3,376 |
| 2025 | JFK Airport | 5,084 |
| 2025 | LaGuardia Airport | 3,305 |
| 2026 | JFK Airport | 4,675 |
| 2026 | LaGuardia Airport | 2,987 |
