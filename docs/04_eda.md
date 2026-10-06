# Ejercicio 4 — Análisis exploratorio con DuckDB (2026)

- **Consultas:** [`sql/04_eda.sql`](../sql/04_eda.sql) · **Resultados completos con SQL:** [`docs/resultados/04_eda.md`](resultados/04_eda.md)
- **Notebook con gráficas:** [`notebooks/04_eda.ipynb`](../notebooks/04_eda.ipynb) · **Figuras:** [`docs/figuras/`](figuras/)
- **Reproducir:** `docker compose exec lab python scripts/sqlrun.py sql/04_eda.sql --md docs/resultados/04_eda.md`

Datos: enero–agosto 2026, vista `trips_clean` (28.6 M viajes yellow y 323 mil green tras
descartar el 3.7% y 4.2% de registros inválidos del Ej. 3). Las consultas no fijan el año:
cubren cualquier archivo presente en `data/raw/`.

## 4.1 Preguntas y su justificación

| # | Pregunta | Por qué es relevante para este conjunto de datos | Consulta(s) |
|---|---|---|---|
| P1 | ¿Cómo evoluciona el volumen de viajes y el ingreso por mes, para cada tipo de taxi? | Los datos llegan como un archivo por mes: es la unidad natural de comparación. Se usa **viajes por día** porque los meses tienen distinto número de días. | `viajes_por_mes` |
| P2 | ¿Qué días y horas concentran la demanda? | `pickup_at` tiene precisión de segundos; la demanda de taxi depende fuertemente de la rutina semanal. | `demanda_por_dia_semana`, `demanda_hora_dia` |
| P3 | ¿Cómo cambian la velocidad y la duración durante el día? | Combinando `trip_distance` y la duración se aproxima la congestión de la ciudad. | `velocidad_por_hora` |
| P4 | ¿Cómo es un viaje típico y en qué se diferencian yellow y green? | Los dos servicios tienen reglas distintas (los green no pueden recoger en el sur de Manhattan ni en aeropuertos). | `comparacion_tipos`, `percentiles_distancia_duracion`, `histograma_distancia`, `pasajeros` |
| P5 | ¿Dónde empiezan los viajes? | `PULocationID` + tabla de zonas de la TLC permite verificar si los green realmente sirven a los boroughs exteriores. | `zonas_origen_borough`, `top_zonas_origen` |
| P6 | ¿Qué peso tienen los aeropuertos? | Son los viajes más largos y caros; tienen tarifas y recargos propios. | `aeropuertos` |
| P7 | ¿Cómo se paga? | `payment_type` determina si se registra la propina y concentra el problema de datos faltantes. | `metodo_pago`, `metodo_pago_por_mes` |
| P8 | ¿Cuánto se deja de propina y cuándo? | Solo los pagos con tarjeta registran propina: hay que filtrar para no subestimarla. | `propinas`, `propina_por_hora` |
| P9 | ¿Qué peso tienen los recargos (congestión, CBD, aeropuerto)? | `cbd_congestion_fee` es nuevo (peaje de congestión de Manhattan desde enero 2025). | `recargos` |
| P10 | ¿Qué valores atípicos e inconsistencias quedan? ¿Quién los genera? | Validar que la limpieza sea suficiente y encontrar la causa de los errores. | `velocidades_imposibles`, `atipicos_iqr_tarifa_por_milla`, `registros_invalidos_por_mes`, `invalidos_por_proveedor` |
| P11 | ¿Qué revela la nueva columna `request_source`? | Columna aparecida en junio 2026 (deriva de esquema del Ej. 3). | `despacho_por_aplicacion` |

## 4.4 Resultados

### Comportamiento temporal

**P1 – Volumen mensual** (`04_viajes_por_mes.png`). Los yellow pasan de ~115 mil viajes/día en
enero a un máximo de **127,858 en mayo** y caen a **103,354 en agosto** (−19% respecto al pico).
Los green siguen la misma curva a otra escala (1,250 → 1,415 → 1,249). El ingreso total yellow
es de ~$96–121 M por mes; el ticket promedio es estable (~$30). Verano (julio–agosto) es
temporada baja: menos viajes de trabajo y más gente fuera de la ciudad.

**P2 – Semana y hora** (`04_heatmap_hora_dia.png`).
- Yellow: el **lunes es el día más bajo** (95.9 mil/día) y **jueves y sábado los más altos**
  (~127–129 mil). Domingo y lunes tienen los viajes más largos (3.9 y 3.8 mi): más viajes a aeropuertos.
- Green: el pico es de **martes a jueves** y el fin de semana cae ~30% → servicio orientado a
  traslados cotidianos, no a vida nocturna.
- El pico absoluto es de 17 a 21 h entre semana; sábado y domingo de 0–2 h tienen tanta demanda
  como un lunes a las 9 h (salidas nocturnas). El mínimo es a las 4–5 h.

**P3 – Velocidad** (`04_velocidad_por_hora.png`). La velocidad mediana yellow cae de **16 mph a
las 5 h a 7.9 mph a las 15 h**: a media tarde un taxi va a la mitad de la velocidad. La duración
mediana es casi constante (13–15 min) porque a horas de congestión los viajes son más cortos
en distancia: los pasajeros compensan.

### Características de los viajes

**P4 – Perfil.** Viaje mediano yellow: 1.92 mi, 14.1 min, $23.58 total. Green: 2.14 mi,
13.3 min, $20.52. Las distribuciones tienen **cola larga a la derecha**: el promedio de distancia
(3.5 mi) casi duplica la mediana, el p99 yellow llega a 19.5 mi. El histograma yellow muestra
un **segundo pico en 16–18 mi** (viajes a JFK) que el green no tiene. El 62% (yellow) y 71% (green)
de los viajes con dato llevan 1 pasajero.

**P5 – Origen** (`04_borough_origen.png`). El **86.6% de los viajes yellow empieza en Manhattan**
(Upper East Side y Midtown al frente). El green, pensado para los boroughs exteriores, también
tiene un 59.5% en Manhattan, pero en **East Harlem** (40% de todos los viajes green en solo dos
zonas), que está fuera de la zona exclusiva de los yellow; Queens (22%) y Brooklyn (16%) completan.

**P6 – Aeropuertos.** JFK (4.0%) y LaGuardia (2.5%) generan el 6.5% de los viajes yellow pero con
totales medianos de **$86.75 y $69.94** (3–4 veces un viaje normal). Los green prácticamente no
recogen en aeropuertos (0.04%), como lo establece su licencia.

### Variables de pago

**P7 – Método de pago** (`04_metodo_pago_por_mes.png`). Tarjeta 65% en ambos tipos. El efectivo
es el doble de frecuente en green (19.4% vs 9.1%), coherente con su público de los boroughs
exteriores. El 25% de los viajes yellow no tiene dato de pago (`payment_type = 0`) y esa
proporción **varía por mes** (20–29%), por lo que cualquier serie de "% tarjeta" está afectada.

**P8 – Propinas.** Con tarjeta, el 91% de los viajes deja propina; la propina mediana es el
**26.4% de la tarifa (yellow) y 23.5% (green)**, influenciada por los botones sugeridos de la
pantalla del taxi. La propina relativa sube en la tarde-noche (27% a las 18 h) y es mínima a las
5–6 h (21%): viajes de madrugada al aeropuerto/trabajo con tarifas altas.

**P9 – Recargos.** El **72.4% de los viajes yellow paga el cargo CBD** (peaje de congestión de
Manhattan, $0.75) contra el 8.5% de los green, y el 90% de los yellow paga el `congestion_surcharge`.
La tarifa base representa solo ~2/3 del total pagado: el resto son impuestos, recargos y propina.

### Atípicos e inconsistencias

**P10.**
- Aun después de limpiar quedan 7,210 viajes yellow a más de 80 mph y 87,686 de menos de 1 minuto.
- La regla de Tukey sobre **tarifa por milla** marca el 4.35% de los yellow como atípicos altos
  (> $15.36/mi; viajes cortos con mucho tráfico) y el 12.5% de los green, incluyendo 29 mil atípicos
  *bajos* (posiblemente tarifas planas o negociadas; no se verificó contra `RatecodeID`).
- Los registros con total negativo pasan de 1.07% en enero a 0.36–0.43% desde abril: la calidad
  mejora durante el año.
- **Por proveedor** (`invalidos_por_proveedor`): **VendorID 7 registra `dropoff = pickup` en el
  100% de sus 367 mil viajes** y **VendorID 6 no envía nunca el tipo de pago** (100% sin dato).
  Los errores no son aleatorios: son sistemáticos de ciertos proveedores de taxímetro. Por eso
  `trips_clean` conserva los viajes del VendorID 7 (sus distancias y tarifas son válidas) dejando
  solo su `duration_min` en NULL, en vez de eliminar a un proveedor completo.

**P11 – `request_source`** (`04_request_source.png`). Desde junio 2026, **el 20.6% de los viajes
yellow se solicitó por la app de Uber** (`HV0003`, licencia HVFHS de Uber) y 1.6% por Lyft
(`HV0005`). En los green solo 0.85% (Lyft). El 74% (yellow) y 85% (green) restante viene sin dato,
lo que corresponde mayormente a viajes tomados en la calle. Los códigos `A` y `CC` no están
documentados públicamente por la TLC y se reportan como tales.

## 4.5 Hallazgos relevantes

1. **Uno de cada cinco viajes de taxi amarillo ya se pide por la app de Uber.** La columna
   `request_source` (nueva en junio 2026) revela que el 20.6% de los viajes yellow viene de
   `HV0003`. El taxi tradicional y las apps ya no son mercados separados.
2. **Los errores de datos son sistemáticos por proveedor, no aleatorios.** VendorID 7 nunca registra
   la hora de llegada y VendorID 6 nunca el tipo de pago; el `payment_type = 0` (25% de los yellow)
   y la ausencia simultánea de 5 columnas son el mismo fenómeno. Una limpieza "ingenua"
   (`WHERE dropoff > pickup`) habría eliminado a un proveedor entero y sesgado los conteos.
3. **Yellow y green atienden mercados distintos.** Yellow: Manhattan (87%), aeropuertos (6.5% de
   viajes, ~3× el precio), pico jueves/sábado, 72% paga el cargo CBD. Green: East Harlem, Queens y
   Brooklyn, sin aeropuertos, pico entre semana con caída de 30% el fin de semana, el doble de uso de
   efectivo y solo 8.5% de viajes dentro de la zona de congestión.
4. **La congestión reduce la velocidad a la mitad, pero no la duración.** La velocidad mediana va de
   16 mph (5 h) a 7.9 mph (15 h), mientras la duración mediana se mantiene en 13–15 min: en horas
   pico la gente hace viajes más cortos.
5. **Estacionalidad clara:** de mayo a agosto la demanda diaria cae 19% (yellow) y 12% (green).
