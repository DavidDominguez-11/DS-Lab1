# Resultados de `sql/07_indicadores.sql`

Generado con `python scripts/sqlrun.py sql/07_indicadores.sql` (DuckDB 1.5.5). No editar a mano.

## `K1_viajes_totales`

- **Tiempo:** 4.10 s

```sql
SELECT COUNT(*) AS viajes FROM trips_clean;
```

| viajes |
|---|
| 114,486,390 |

## `K2_ingreso_total`

- **Tiempo:** 0.56 s

```sql
SELECT ROUND(SUM(total_amount) / 1e6, 1) AS ingreso_musd FROM trips_clean;
```

| ingreso_musd |
|---|
| 3,324.5 |

## `K3_ticket_mediano`

- **Tiempo:** 4.82 s

```sql
SELECT ROUND(MEDIAN(total_amount), 2) AS ticket_mediano_usd FROM trips_clean;
```

| ticket_mediano_usd |
|---|
| 22.05 |

## `K4_cuota_green`

- **Tiempo:** 0.63 s

```sql
SELECT ROUND(100.0 * AVG((taxi_type = 'green')::INT), 2) AS pct_viajes_green FROM trips_clean;
```

| pct_viajes_green |
|---|
| 1.32 |

## `I1_viajes_diarios_por_mes`

- **Tiempo:** 1.04 s

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
| 2025-01-01 | green | 1,460 |
| 2025-01-01 | yellow | 104,935 |
| 2025-02-01 | green | 1,559 |
| 2025-02-01 | yellow | 118,214 |
| 2025-03-01 | green | 1,551 |
| 2025-03-01 | yellow | 124,117 |
| 2025-04-01 | green | 1,618 |
| 2025-04-01 | yellow | 123,496 |
| 2025-05-01 | green | 1,676 |
| 2025-05-01 | yellow | 134,015 |
| 2025-06-01 | green | 1,568 |
| 2025-06-01 | yellow | 131,179 |
| 2025-07-01 | green | 1,497 |
| 2025-07-01 | yellow | 114,483 |
| 2025-08-01 | green | 1,436 |
| 2025-08-01 | yellow | 104,085 |

*... 24 filas mas omitidas.*

## `I2_ingreso_mensual`

- **Tiempo:** 0.89 s

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
| 2025-01-01 | green | 1.02 |
| 2025-01-01 | yellow | 87.2 |
| 2025-02-01 | green | 1 |
| 2025-02-01 | yellow | 88.01 |
| 2025-03-01 | green | 1.15 |
| 2025-03-01 | yellow | 107.38 |
| 2025-04-01 | green | 1.19 |
| 2025-04-01 | yellow | 104.64 |
| 2025-05-01 | green | 1.32 |
| 2025-05-01 | yellow | 121.4 |
| 2025-06-01 | green | 1.21 |
| 2025-06-01 | yellow | 115.64 |
| 2025-07-01 | green | 1.19 |
| 2025-07-01 | yellow | 102.81 |
| 2025-08-01 | green | 1.23 |
| 2025-08-01 | yellow | 93.24 |

*... 24 filas mas omitidas.*

## `I3_precio_del_viaje`

- **Tiempo:** 3.18 s

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
| 2025-01-01 | 20.75 | 7.09 |
| 2025-02-01 | 21.06 | 7.13 |
| 2025-03-01 | 21.81 | 7.09 |
| 2025-04-01 | 21.97 | 7.13 |
| 2025-05-01 | 22.74 | 7.14 |
| 2025-06-01 | 22.93 | 7.05 |
| 2025-07-01 | 22.64 | 6.89 |
| 2025-08-01 | 22.1 | 6.62 |
| 2025-09-01 | 23.33 | 7.16 |
| 2025-10-01 | 22.99 | 7.23 |
| 2025-11-01 | 22.35 | 7.19 |
| 2025-12-01 | 24.94 | 7.67 |
| 2026-01-01 | 23.58 | 7.37 |
| 2026-02-01 | 24.42 | 7.75 |
| 2026-03-01 | 23.85 | 7.39 |
| 2026-04-01 | 23.95 | 7.45 |
| 2026-05-01 | 24.25 | 7.48 |
| 2026-06-01 | 24.15 | 7.52 |
| 2026-07-01 | 23.94 | 7.17 |
| 2026-08-01 | 23.94 | 6.96 |

## `I4_metodo_pago`

- **Tiempo:** 2.24 s

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

*... 88 filas mas omitidas.*

## `I5_propina`

- **Tiempo:** 1.51 s

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
| 2025-01-01 | green | 23.8 |
| 2025-01-01 | yellow | 27 |
| 2025-02-01 | green | 23.6 |
| 2025-02-01 | yellow | 27 |
| 2025-03-01 | green | 23.4 |
| 2025-03-01 | yellow | 26.8 |
| 2025-04-01 | green | 23.5 |
| 2025-04-01 | yellow | 26.7 |
| 2025-05-01 | green | 23.4 |
| 2025-05-01 | yellow | 26.4 |
| 2025-06-01 | green | 23.3 |
| 2025-06-01 | yellow | 26.5 |
| 2025-07-01 | green | 23.4 |
| 2025-07-01 | yellow | 26.4 |
| 2025-08-01 | green | 23 |
| 2025-08-01 | yellow | 26.4 |

*... 24 filas mas omitidas.*

## `I6_velocidad_por_hora`

- **Tiempo:** 1.95 s

```sql
SELECT pickup_hour AS hora, taxi_type,
       ROUND(MEDIAN(trip_distance / (duration_min / 60)), 1) AS velocidad_mediana_mph
FROM trips_clean
WHERE duration_min >= 1
GROUP BY ALL ORDER BY hora, taxi_type;
```

| hora | taxi_type | velocidad_mediana_mph |
|---|---|---|
| 0 | green | 12.5 |
| 0 | yellow | 11.9 |
| 1 | green | 12.7 |
| 1 | yellow | 12.3 |
| 2 | green | 13.5 |
| 2 | yellow | 12.8 |
| 3 | green | 14.4 |
| 3 | yellow | 13.8 |
| 4 | green | 15.7 |
| 4 | yellow | 15.5 |
| 5 | green | 16.3 |
| 5 | yellow | 16.3 |
| 6 | green | 12.7 |
| 6 | yellow | 14 |
| 7 | green | 10.4 |
| 7 | yellow | 11.2 |
| 8 | green | 9.6 |
| 8 | yellow | 9.3 |
| 9 | green | 10.1 |
| 9 | yellow | 9 |
| 10 | green | 10.1 |
| 10 | yellow | 8.7 |
| 11 | green | 9.9 |
| 11 | yellow | 8.2 |
| 12 | green | 9.9 |
| 12 | yellow | 8.2 |
| 13 | green | 9.8 |
| 13 | yellow | 8.2 |
| 14 | green | 9.3 |
| 14 | yellow | 8.1 |
| 15 | green | 9.2 |
| 15 | yellow | 8 |
| 16 | green | 9.3 |
| 16 | yellow | 8.2 |
| 17 | green | 9.5 |
| 17 | yellow | 8.1 |
| 18 | green | 9.9 |
| 18 | yellow | 8.5 |
| 19 | green | 10.6 |
| 19 | yellow | 9.1 |

*... 8 filas mas omitidas.*

## `I7_demanda_por_hora`

- **Tiempo:** 0.90 s

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
| 0 | Fin de semana | 6,665 |
| 0 | Laborable | 2,336 |
| 1 | Fin de semana | 5,267 |
| 1 | Laborable | 1,172 |
| 2 | Fin de semana | 3,796 |
| 2 | Laborable | 650 |
| 3 | Fin de semana | 2,568 |
| 3 | Laborable | 439 |
| 4 | Fin de semana | 1,612 |
| 4 | Laborable | 499 |
| 5 | Fin de semana | 815 |
| 5 | Laborable | 921 |
| 6 | Fin de semana | 1,120 |
| 6 | Laborable | 2,109 |
| 7 | Fin de semana | 1,551 |
| 7 | Laborable | 4,138 |
| 8 | Fin de semana | 2,332 |
| 8 | Laborable | 5,541 |
| 9 | Fin de semana | 3,575 |
| 9 | Laborable | 5,532 |
| 10 | Fin de semana | 4,684 |
| 10 | Laborable | 5,412 |
| 11 | Fin de semana | 5,518 |
| 11 | Laborable | 5,645 |
| 12 | Fin de semana | 6,224 |
| 12 | Laborable | 6,050 |
| 13 | Fin de semana | 6,595 |
| 13 | Laborable | 6,275 |
| 14 | Fin de semana | 6,721 |
| 14 | Laborable | 6,903 |
| 15 | Fin de semana | 6,759 |
| 15 | Laborable | 7,235 |
| 16 | Fin de semana | 7,038 |
| 16 | Laborable | 6,993 |
| 17 | Fin de semana | 7,263 |
| 17 | Laborable | 7,875 |
| 18 | Fin de semana | 7,412 |
| 18 | Laborable | 8,264 |
| 19 | Fin de semana | 6,876 |
| 19 | Laborable | 7,297 |

*... 8 filas mas omitidas.*

## `I8_top_zonas`

- **Tiempo:** 1.46 s

```sql
SELECT z.zone || ' (' || z.borough || ')' AS zona, COUNT(*) AS viajes
FROM trips_clean t JOIN zones z ON z.location_id = t.pu_location_id
GROUP BY 1 ORDER BY viajes DESC LIMIT 12;
```

| zona | viajes |
|---|---|
| Upper East Side South (Manhattan) | 5,186,121 |
| Midtown Center (Manhattan) | 5,025,898 |
| JFK Airport (Queens) | 4,898,233 |
| Upper East Side North (Manhattan) | 4,622,017 |
| Midtown East (Manhattan) | 3,694,890 |
| Penn Station/Madison Sq West (Manhattan) | 3,670,631 |
| Times Sq/Theatre District (Manhattan) | 3,574,931 |
| Lincoln Square East (Manhattan) | 3,415,821 |
| LaGuardia Airport (Queens) | 3,226,309 |
| Murray Hill (Manhattan) | 3,088,347 |
| Union Sq (Manhattan) | 3,012,888 |
| Midtown North (Manhattan) | 3,009,395 |

## `I9_aeropuertos`

- **Tiempo:** 5.09 s

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
| Resto de la ciudad | 106,358,326 | 92.9 | 81.23 | 21.15 |
| JFK Airport | 4,898,233 | 4.28 | 12.02 | 88.21 |
| LaGuardia Airport | 3,226,309 | 2.82 | 6.74 | 69.01 |
| Newark Airport | 3522 | 0 | 0.01 | 116.38 |

## `I10_cargo_cbd`

- **Tiempo:** 1.14 s

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
| 2025-01-01 | green | 7.2 |
| 2025-01-01 | yellow | 65.8 |
| 2025-02-01 | green | 8.7 |
| 2025-02-01 | yellow | 74 |
| 2025-03-01 | green | 9.9 |
| 2025-03-01 | yellow | 74.3 |
| 2025-04-01 | green | 10.3 |
| 2025-04-01 | yellow | 74 |
| 2025-05-01 | green | 10.5 |
| 2025-05-01 | yellow | 73.3 |
| 2025-06-01 | green | 10.3 |
| 2025-06-01 | yellow | 73.7 |
| 2025-07-01 | green | 9.9 |
| 2025-07-01 | yellow | 74.4 |
| 2025-08-01 | green | 10.8 |
| 2025-08-01 | yellow | 73.7 |

*... 24 filas mas omitidas.*

## `I11_calidad_datos`

- **Tiempo:** 0.86 s

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
| 2025-01-01 | green | 6.34 |
| 2025-01-01 | yellow | 6.4 |
| 2025-02-01 | green | 6.37 |
| 2025-02-01 | yellow | 7.48 |
| 2025-03-01 | green | 6.69 |
| 2025-03-01 | yellow | 7.18 |
| 2025-04-01 | green | 6.92 |
| 2025-04-01 | yellow | 6.69 |
| 2025-05-01 | green | 6.24 |
| 2025-05-01 | yellow | 9.53 |
| 2025-06-01 | green | 4.78 |
| 2025-06-01 | yellow | 8.97 |
| 2025-07-01 | green | 3.75 |
| 2025-07-01 | yellow | 8.98 |
| 2025-08-01 | green | 3.84 |
| 2025-08-01 | yellow | 9.72 |

*... 24 filas mas omitidas.*

## `I12_despacho_por_app`

- **Tiempo:** 0.26 s

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
