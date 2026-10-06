# Resultados de `sql/07_indicadores.sql`

Generado con `python scripts/sqlrun.py sql/07_indicadores.sql` (DuckDB 1.5.5). No editar a mano.

## `K1_viajes_totales`

- **Tiempo:** 1.97 s

```sql
SELECT COUNT(*) AS viajes FROM trips_clean;
```

| viajes |
|---|
| 69,230,926 |

## `K2_ingreso_total`

- **Tiempo:** 0.24 s

```sql
SELECT ROUND(SUM(total_amount) / 1e6, 1) AS ingreso_musd FROM trips_clean;
```

| ingreso_musd |
|---|
| 2,022.9 |

## `K3_ticket_mediano`

- **Tiempo:** 2.33 s

```sql
SELECT ROUND(MEDIAN(total_amount), 2) AS ticket_mediano_usd FROM trips_clean;
```

| ticket_mediano_usd |
|---|
| 22.1 |

## `K4_cuota_green`

- **Tiempo:** 0.48 s

```sql
SELECT ROUND(100.0 * AVG((taxi_type = 'green')::INT), 2) AS pct_viajes_green FROM trips_clean;
```

| pct_viajes_green |
|---|
| 1.36 |

## `I1_viajes_diarios_por_mes`

- **Tiempo:** 0.84 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0) AS viajes_por_dia
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;
```

| mes | taxi_type | viajes_por_dia |
|---|---|---|
| 2024-01-01 | green | 1,720 |
| 2024-01-01 | yellow | 92,522 |
| 2024-02-01 | green | 1,738 |
| 2024-02-01 | yellow | 100,000 |
| 2024-03-01 | green | 1,745 |
| 2024-03-01 | yellow | 110,921 |
| 2024-04-01 | green | 1,765 |
| 2024-04-01 | yellow | 113,757 |
| 2024-05-01 | green | 1,854 |
| 2024-05-01 | yellow | 116,652 |
| 2024-06-01 | green | 1,723 |
| 2024-06-01 | yellow | 114,223 |
| 2024-07-01 | green | 1,565 |
| 2024-07-01 | yellow | 95,885 |
| 2024-08-01 | green | 1,571 |
| 2024-08-01 | yellow | 92,447 |
| 2024-09-01 | green | 1,710 |
| 2024-09-01 | yellow | 116,089 |
| 2024-10-01 | green | 1,716 |
| 2024-10-01 | yellow | 118,726 |
| 2024-11-01 | green | 1,636 |
| 2024-11-01 | yellow | 116,951 |
| 2024-12-01 | green | 1,632 |
| 2024-12-01 | yellow | 113,478 |
| 2026-01-01 | green | 1,251 |
| 2026-01-01 | yellow | 114,862 |
| 2026-02-01 | green | 1,278 |
| 2026-02-01 | yellow | 116,082 |
| 2026-03-01 | green | 1,371 |
| 2026-03-01 | yellow | 122,934 |
| 2026-04-01 | green | 1,412 |
| 2026-04-01 | yellow | 124,116 |
| 2026-05-01 | green | 1,390 |
| 2026-05-01 | yellow | 127,858 |
| 2026-06-01 | green | 1,415 |
| 2026-06-01 | yellow | 123,186 |
| 2026-07-01 | green | 1,271 |
| 2026-07-01 | yellow | 109,284 |
| 2026-08-01 | green | 1,249 |
| 2026-08-01 | yellow | 103,354 |

## `I2_ingreso_mensual`

- **Tiempo:** 0.77 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(SUM(total_amount) / 1e6, 2) AS ingreso_musd
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;
```

| mes | taxi_type | ingreso_musd |
|---|---|---|
| 2024-01-01 | green | 1.18 |
| 2024-01-01 | yellow | 78.41 |
| 2024-02-01 | green | 1.13 |
| 2024-02-01 | yellow | 78.97 |
| 2024-03-01 | green | 1.23 |
| 2024-03-01 | yellow | 95.77 |
| 2024-04-01 | green | 1.23 |
| 2024-04-01 | yellow | 96.17 |
| 2024-05-01 | green | 1.41 |
| 2024-05-01 | yellow | 104.82 |
| 2024-06-01 | green | 1.28 |
| 2024-06-01 | yellow | 98.27 |
| 2024-07-01 | green | 1.19 |
| 2024-07-01 | yellow | 86.11 |
| 2024-08-01 | green | 1.26 |
| 2024-08-01 | yellow | 83.72 |
| 2024-09-01 | green | 1.36 |
| 2024-09-01 | yellow | 102.66 |
| 2024-10-01 | green | 1.33 |
| 2024-10-01 | yellow | 108.13 |
| 2024-11-01 | green | 1.18 |
| 2024-11-01 | yellow | 99.91 |
| 2024-12-01 | green | 1.21 |
| 2024-12-01 | yellow | 103.31 |
| 2026-01-01 | green | 0.94 |
| 2026-01-01 | yellow | 105.44 |
| 2026-02-01 | green | 0.87 |
| 2026-02-01 | yellow | 98.8 |
| 2026-03-01 | green | 1.06 |
| 2026-03-01 | yellow | 115.13 |
| 2026-04-01 | green | 1.07 |
| 2026-04-01 | yellow | 111.88 |
| 2026-05-01 | green | 1.11 |
| 2026-05-01 | yellow | 120.89 |
| 2026-06-01 | green | 1.11 |
| 2026-06-01 | yellow | 112.89 |
| 2026-07-01 | green | 1.03 |
| 2026-07-01 | yellow | 101.93 |
| 2026-08-01 | green | 1.02 |
| 2026-08-01 | yellow | 96.43 |

## `I3_precio_del_viaje`

- **Tiempo:** 2.14 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes,
       ROUND(MEDIAN(total_amount), 2)                    AS ticket_mediano,
       ROUND(MEDIAN(fare_amount / trip_distance), 2)     AS tarifa_por_milla_mediana
FROM trips_clean
WHERE taxi_type = 'yellow' AND trip_distance >= 0.5
GROUP BY ALL ORDER BY mes;
```

| mes | ticket_mediano | tarifa_por_milla_mediana |
|---|---|---|
| 2024-01-01 | 20.52 | 7.11 |
| 2024-02-01 | 20.82 | 7.15 |
| 2024-03-01 | 21 | 7.12 |
| 2024-04-01 | 21.45 | 7.15 |
| 2024-05-01 | 22 | 7.32 |
| 2024-06-01 | 21.8 | 7.2 |
| 2024-07-01 | 21.48 | 7.08 |
| 2024-08-01 | 21.48 | 7.03 |
| 2024-09-01 | 22.2 | 7.3 |
| 2024-10-01 | 22.2 | 7.39 |
| 2024-11-01 | 21.84 | 7.42 |
| 2024-12-01 | 22.4 | 7.61 |
| 2026-01-01 | 23.58 | 7.37 |
| 2026-02-01 | 24.42 | 7.75 |
| 2026-03-01 | 23.85 | 7.39 |
| 2026-04-01 | 23.95 | 7.45 |
| 2026-05-01 | 24.25 | 7.48 |
| 2026-06-01 | 24.15 | 7.52 |
| 2026-07-01 | 23.94 | 7.17 |
| 2026-08-01 | 23.94 | 6.96 |

## `I4_metodo_pago`

- **Tiempo:** 1.10 s

```sql
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
```

| mes | metodo | pct |
|---|---|---|
| 2024-01-01 | Efectivo | 14.98 |
| 2024-01-01 | Otro | 1.16 |
| 2024-01-01 | Sin dato / Flex | 4.06 |
| 2024-01-01 | Tarjeta | 79.81 |
| 2024-02-01 | Efectivo | 13.91 |
| 2024-02-01 | Otro | 1.16 |
| 2024-02-01 | Sin dato / Flex | 5.14 |
| 2024-02-01 | Tarjeta | 79.79 |
| 2024-03-01 | Efectivo | 13.56 |
| 2024-03-01 | Otro | 1.19 |
| 2024-03-01 | Sin dato / Flex | 10.52 |
| 2024-03-01 | Tarjeta | 74.73 |
| 2024-04-01 | Efectivo | 13.4 |
| 2024-04-01 | Otro | 1.16 |
| 2024-04-01 | Sin dato / Flex | 11.27 |
| 2024-04-01 | Tarjeta | 74.17 |
| 2024-05-01 | Efectivo | 13.5 |
| 2024-05-01 | Otro | 1.22 |
| 2024-05-01 | Sin dato / Flex | 10.59 |
| 2024-05-01 | Tarjeta | 74.69 |
| 2024-06-01 | Efectivo | 13.29 |
| 2024-06-01 | Otro | 1.28 |
| 2024-06-01 | Sin dato / Flex | 11.19 |
| 2024-06-01 | Tarjeta | 74.24 |
| 2024-07-01 | Efectivo | 14.78 |
| 2024-07-01 | Otro | 1.52 |
| 2024-07-01 | Sin dato / Flex | 8.76 |
| 2024-07-01 | Tarjeta | 74.95 |
| 2024-08-01 | Efectivo | 15.11 |
| 2024-08-01 | Otro | 1.64 |
| 2024-08-01 | Sin dato / Flex | 8.24 |
| 2024-08-01 | Tarjeta | 75.01 |
| 2024-09-01 | Efectivo | 12.33 |
| 2024-09-01 | Otro | 1.42 |
| 2024-09-01 | Sin dato / Flex | 12.23 |
| 2024-09-01 | Tarjeta | 74.02 |
| 2024-10-01 | Efectivo | 12.49 |
| 2024-10-01 | Otro | 1.46 |
| 2024-10-01 | Sin dato / Flex | 9.29 |
| 2024-10-01 | Tarjeta | 76.75 |

*... 40 filas mas omitidas.*

## `I5_propina`

- **Tiempo:** 0.84 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(100.0 * MEDIAN(tip_amount / fare_amount), 1) AS propina_pct_mediana
FROM trips_clean
WHERE payment_type = 1 AND fare_amount > 0
GROUP BY ALL ORDER BY mes, taxi_type;
```

| mes | taxi_type | propina_pct_mediana |
|---|---|---|
| 2024-01-01 | green | 23.6 |
| 2024-01-01 | yellow | 26.2 |
| 2024-02-01 | green | 23.5 |
| 2024-02-01 | yellow | 26.2 |
| 2024-03-01 | green | 23.5 |
| 2024-03-01 | yellow | 25.9 |
| 2024-04-01 | green | 23.5 |
| 2024-04-01 | yellow | 25.9 |
| 2024-05-01 | green | 23.4 |
| 2024-05-01 | yellow | 25.8 |
| 2024-06-01 | green | 23.3 |
| 2024-06-01 | yellow | 25.8 |
| 2024-07-01 | green | 23.4 |
| 2024-07-01 | yellow | 25.6 |
| 2024-08-01 | green | 23.3 |
| 2024-08-01 | yellow | 25.6 |
| 2024-09-01 | green | 23.1 |
| 2024-09-01 | yellow | 25.4 |
| 2024-10-01 | green | 23.4 |
| 2024-10-01 | yellow | 25.6 |
| 2024-11-01 | green | 23.3 |
| 2024-11-01 | yellow | 25.6 |
| 2024-12-01 | green | 23.7 |
| 2024-12-01 | yellow | 25.6 |
| 2026-01-01 | green | 23.6 |
| 2026-01-01 | yellow | 26.7 |
| 2026-02-01 | green | 23.5 |
| 2026-02-01 | yellow | 26.3 |
| 2026-03-01 | green | 23.6 |
| 2026-03-01 | yellow | 26.5 |
| 2026-04-01 | green | 23.8 |
| 2026-04-01 | yellow | 26.4 |
| 2026-05-01 | green | 23.5 |
| 2026-05-01 | yellow | 26.1 |
| 2026-06-01 | green | 23.5 |
| 2026-06-01 | yellow | 26.7 |
| 2026-07-01 | green | 23.5 |
| 2026-07-01 | yellow | 26.6 |
| 2026-08-01 | green | 23.5 |
| 2026-08-01 | yellow | 26.5 |

## `I6_velocidad_por_hora`

- **Tiempo:** 1.19 s

```sql
SELECT pickup_hour AS hora, taxi_type,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 1) AS velocidad_mediana_mph
FROM trips_clean
WHERE duration_min >= 1
GROUP BY ALL ORDER BY hora, taxi_type;
```

| hora | taxi_type | velocidad_mediana_mph |
|---|---|---|
| 0 | green | 12.4 |
| 0 | yellow | 11.8 |
| 1 | green | 12.6 |
| 1 | yellow | 12.2 |
| 2 | green | 13.3 |
| 2 | yellow | 12.7 |
| 3 | green | 14.2 |
| 3 | yellow | 13.7 |
| 4 | green | 15.5 |
| 4 | yellow | 15.4 |
| 5 | green | 16.1 |
| 5 | yellow | 16.2 |
| 6 | green | 12.8 |
| 6 | yellow | 13.9 |
| 7 | green | 10.4 |
| 7 | yellow | 11.1 |
| 8 | green | 9.6 |
| 8 | yellow | 9.3 |
| 9 | green | 10.1 |
| 9 | yellow | 8.9 |
| 10 | green | 10.2 |
| 10 | yellow | 8.7 |
| 11 | green | 10 |
| 11 | yellow | 8.2 |
| 12 | green | 9.9 |
| 12 | yellow | 8.1 |
| 13 | green | 9.8 |
| 13 | yellow | 8.2 |
| 14 | green | 9.2 |
| 14 | yellow | 8.1 |
| 15 | green | 9.1 |
| 15 | yellow | 7.9 |
| 16 | green | 9.3 |
| 16 | yellow | 8.1 |
| 17 | green | 9.5 |
| 17 | yellow | 8.1 |
| 18 | green | 9.9 |
| 18 | yellow | 8.4 |
| 19 | green | 10.6 |
| 19 | yellow | 9.1 |

*... 8 filas mas omitidas.*

## `I7_demanda_por_hora`

- **Tiempo:** 0.64 s

```sql
WITH base AS (
    SELECT pickup_hour, CASE WHEN pickup_dow >= 6 THEN 'Fin de semana' ELSE 'Laborable' END AS tipo_dia,
           pickup_date
    FROM trips_clean
)
SELECT pickup_hour AS hora, tipo_dia,
       ROUND(COUNT(*) / COUNT(DISTINCT pickup_date), 0) AS viajes_promedio_por_hora
FROM base
GROUP BY ALL ORDER BY hora, tipo_dia;
```

| hora | tipo_dia | viajes_promedio_por_hora |
|---|---|---|
| 0 | Fin de semana | 6,310 |
| 0 | Laborable | 2,244 |
| 1 | Fin de semana | 4,997 |
| 1 | Laborable | 1,121 |
| 2 | Fin de semana | 3,610 |
| 2 | Laborable | 621 |
| 3 | Fin de semana | 2,445 |
| 3 | Laborable | 422 |
| 4 | Fin de semana | 1,511 |
| 4 | Laborable | 476 |
| 5 | Fin de semana | 744 |
| 5 | Laborable | 893 |
| 6 | Fin de semana | 1,056 |
| 6 | Laborable | 2,046 |
| 7 | Fin de semana | 1,472 |
| 7 | Laborable | 4,012 |
| 8 | Fin de semana | 2,231 |
| 8 | Laborable | 5,385 |
| 9 | Fin de semana | 3,446 |
| 9 | Laborable | 5,370 |
| 10 | Fin de semana | 4,517 |
| 10 | Laborable | 5,248 |
| 11 | Fin de semana | 5,355 |
| 11 | Laborable | 5,489 |
| 12 | Fin de semana | 6,062 |
| 12 | Laborable | 5,873 |
| 13 | Fin de semana | 6,408 |
| 13 | Laborable | 6,083 |
| 14 | Fin de semana | 6,526 |
| 14 | Laborable | 6,713 |
| 15 | Fin de semana | 6,547 |
| 15 | Laborable | 7,019 |
| 16 | Fin de semana | 6,812 |
| 16 | Laborable | 6,819 |
| 17 | Fin de semana | 7,010 |
| 17 | Laborable | 7,681 |
| 18 | Fin de semana | 7,130 |
| 18 | Laborable | 8,078 |
| 19 | Fin de semana | 6,607 |
| 19 | Laborable | 7,092 |

*... 8 filas mas omitidas.*

## `I8_top_zonas`

- **Tiempo:** 0.94 s

```sql
SELECT z.zone || ' (' || z.borough || ')' AS zona, COUNT(*) AS viajes
FROM trips_clean t JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY 1 ORDER BY viajes DESC LIMIT 12;
```

| zona | viajes |
|---|---|
| Upper East Side South (Manhattan) | 3,150,774 |
| Midtown Center (Manhattan) | 3,052,197 |
| JFK Airport (Queens) | 3,006,262 |
| Upper East Side North (Manhattan) | 2,837,172 |
| Midtown East (Manhattan) | 2,260,694 |
| Penn Station/Madison Sq West (Manhattan) | 2,207,167 |
| Times Sq/Theatre District (Manhattan) | 2,166,486 |
| Lincoln Square East (Manhattan) | 2,108,654 |
| LaGuardia Airport (Queens) | 1,986,692 |
| Murray Hill (Manhattan) | 1,887,885 |
| Upper West Side South (Manhattan) | 1,852,833 |
| Midtown North (Manhattan) | 1,840,165 |

## `I9_aeropuertos`

- **Tiempo:** 3.03 s

```sql
SELECT CASE WHEN z.service_zone IN ('Airports', 'EWR') THEN z.zone ELSE 'Resto de la ciudad' END AS origen,
       COUNT(*)                                                    AS viajes,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)          AS pct_viajes,
       ROUND(100.0 * SUM(total_amount) / SUM(SUM(total_amount)) OVER (), 2) AS pct_ingreso,
       ROUND(MEDIAN(total_amount), 2)                              AS ticket_mediano
FROM trips_clean t JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY 1 ORDER BY viajes DESC;
```

| origen | viajes | pct_viajes | pct_ingreso | ticket_mediano |
|---|---|---|---|---|
| Resto de la ciudad | 64,235,800 | 92.78 | 81.07 | 21.19 |
| JFK Airport | 3,006,262 | 4.34 | 12.12 | 87.69 |
| LaGuardia Airport | 1,986,692 | 2.87 | 6.8 | 69 |
| Newark Airport | 2172 | 0 | 0.01 | 119.92 |

## `I10_cargo_cbd`

- **Tiempo:** 0.72 s

```sql
SELECT date_trunc('month', pickup_at)::DATE AS mes, taxi_type,
       ROUND(100.0 * AVG((COALESCE(cbd_congestion_fee, 0) > 0)::INT), 1) AS pct_paga_cbd
FROM trips_clean
GROUP BY ALL ORDER BY mes, taxi_type;
```

| mes | taxi_type | pct_paga_cbd |
|---|---|---|
| 2024-01-01 | green | 0 |
| 2024-01-01 | yellow | 0 |
| 2024-02-01 | green | 0 |
| 2024-02-01 | yellow | 0 |
| 2024-03-01 | green | 0 |
| 2024-03-01 | yellow | 0 |
| 2024-04-01 | green | 0 |
| 2024-04-01 | yellow | 0 |
| 2024-05-01 | green | 0 |
| 2024-05-01 | yellow | 0 |
| 2024-06-01 | green | 0 |
| 2024-06-01 | yellow | 0 |
| 2024-07-01 | green | 0 |
| 2024-07-01 | yellow | 0 |
| 2024-08-01 | green | 0 |
| 2024-08-01 | yellow | 0 |
| 2024-09-01 | green | 0 |
| 2024-09-01 | yellow | 0 |
| 2024-10-01 | green | 0 |
| 2024-10-01 | yellow | 0 |
| 2024-11-01 | green | 0 |
| 2024-11-01 | yellow | 0 |
| 2024-12-01 | green | 0 |
| 2024-12-01 | yellow | 0 |
| 2026-01-01 | green | 7.9 |
| 2026-01-01 | yellow | 70.9 |
| 2026-02-01 | green | 7.1 |
| 2026-02-01 | yellow | 70.9 |
| 2026-03-01 | green | 8.1 |
| 2026-03-01 | yellow | 71.5 |
| 2026-04-01 | green | 8.4 |
| 2026-04-01 | yellow | 71.7 |
| 2026-05-01 | green | 8.9 |
| 2026-05-01 | yellow | 66.8 |
| 2026-06-01 | green | 8.5 |
| 2026-06-01 | yellow | 74.2 |
| 2026-07-01 | green | 9.2 |
| 2026-07-01 | yellow | 77.1 |
| 2026-08-01 | green | 9.7 |
| 2026-08-01 | yellow | 77.1 |

## `I11_calidad_datos`

- **Tiempo:** 0.60 s

```sql
SELECT make_date(t.source_year, t.source_month, 1) AS mes, t.taxi_type,
       ROUND(100.0 * (COUNT(*) - ANY_VALUE(c.limpios)) / COUNT(*), 2) AS pct_invalidos
FROM trips t
JOIN (SELECT source_year, source_month, taxi_type, COUNT(*) AS limpios
      FROM trips_clean GROUP BY ALL) c USING (source_year, source_month, taxi_type)
GROUP BY ALL ORDER BY mes, t.taxi_type;
```

| mes | taxi_type | pct_invalidos |
|---|---|---|
| 2024-01-01 | green | 5.72 |
| 2024-01-01 | yellow | 3.25 |
| 2024-02-01 | green | 5.93 |
| 2024-02-01 | yellow | 3.58 |
| 2024-03-01 | green | 5.84 |
| 2024-03-01 | yellow | 4.02 |
| 2024-04-01 | green | 6.25 |
| 2024-04-01 | yellow | 2.89 |
| 2024-05-01 | green | 5.78 |
| 2024-05-01 | yellow | 2.89 |
| 2024-06-01 | green | 5.6 |
| 2024-06-01 | yellow | 3.18 |
| 2024-07-01 | green | 6.44 |
| 2024-07-01 | yellow | 3.4 |
| 2024-08-01 | green | 5.95 |
| 2024-08-01 | yellow | 3.8 |
| 2024-09-01 | green | 5.77 |
| 2024-09-01 | yellow | 4.14 |
| 2024-10-01 | green | 5.28 |
| 2024-10-01 | yellow | 4 |
| 2024-11-01 | green | 6.02 |
| 2024-11-01 | yellow | 3.78 |
| 2024-12-01 | green | 6.28 |
| 2024-12-01 | yellow | 4.1 |
| 2026-01-01 | green | 3.73 |
| 2026-01-01 | yellow | 4.41 |
| 2026-02-01 | green | 4.24 |
| 2026-02-01 | yellow | 4.4 |
| 2026-03-01 | green | 3.85 |
| 2026-03-01 | yellow | 3.58 |
| 2026-04-01 | green | 4.22 |
| 2026-04-01 | yellow | 2.81 |
| 2026-05-01 | green | 4.05 |
| 2026-05-01 | yellow | 3.11 |
| 2026-06-01 | green | 3.89 |
| 2026-06-01 | yellow | 3.69 |
| 2026-07-01 | green | 4.5 |
| 2026-07-01 | yellow | 4.03 |
| 2026-08-01 | green | 4.84 |
| 2026-08-01 | yellow | 3.98 |

## `I12_despacho_por_app`

- **Tiempo:** 0.29 s

```sql
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
```

| mes | origen_solicitud | pct |
|---|---|---|
| 2026-06-01 | App Uber | 22.83 |
| 2026-06-01 | Codigo A | 1.91 |
| 2026-06-01 | Codigo CC | 0.01 |
| 2026-06-01 | E-hail | 0.21 |
| 2026-06-01 | Sin dato (calle) | 75.04 |
| 2026-07-01 | App Uber | 19.84 |
| 2026-07-01 | Codigo A | 5.88 |
| 2026-07-01 | Codigo CC | 0.02 |
| 2026-07-01 | E-hail | 0.18 |
| 2026-07-01 | Sin dato (calle) | 74.09 |
| 2026-08-01 | App Lyft | 5.07 |
| 2026-08-01 | App Uber | 17.99 |
| 2026-08-01 | Codigo A | 2.93 |
| 2026-08-01 | Codigo CC | 0.01 |
| 2026-08-01 | E-hail | 0.18 |
| 2026-08-01 | Sin dato (calle) | 73.81 |
