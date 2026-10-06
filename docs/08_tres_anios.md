# Ejercicio 8 — Incorporación de 2025 y análisis de los tres años

| Pieza | Archivo |
|---|---|
| Cambio en la descarga | `ANIOS = (2024, 2025, 2026)` en [`scripts/download_data.py`](../scripts/download_data.py) |
| Evidencia de descarga | `docs/evidencia/descarga_2025_incorporacion.log`, `descarga_2025_segunda_ejecucion.log`, [`docs/inventario_datos.md`](inventario_datos.md) |
| Validación de la incorporación | [`docs/resultados/05_validacion_2025.md`](resultados/05_validacion_2025.md) (mismo SQL del Ej. 5) |
| Consultas anteriores re-ejecutadas | [`04_eda_3anios.md`](resultados/04_eda_3anios.md), [`07_indicadores_3anios.md`](resultados/07_indicadores_3anios.md), [`03_exploracion.md`](resultados/03_exploracion.md) |
| Consultas de evolución (8.5–8.7) | [`sql/08_evolucion.sql`](../sql/08_evolucion.sql) → [`docs/resultados/08_evolucion.md`](resultados/08_evolucion.md) |
| Tablero actualizado (8.4) | Metabase: 16 tarjetas del Ej. 7 + 8 tarjetas de evolución; capturas en [`docs/tablero/`](tablero/) |
| Notebook con gráficas | [`notebooks/08_tres_anios.ipynb`](../notebooks/08_tres_anios.ipynb) |

## 8.1 – 8.2 Descarga

Un solo cambio: `ANIOS = (2024, 2026)` → `ANIOS = (2024, 2025, 2026)`.

| Ejecución | Descargados | Ya existían | No publicados | Fallidos |
|---|---:|---:|---:|---:|
| Incorporación de 2025 | **24** (12 yellow + 12 green) | **41** (2024, 2026 y tabla de zonas) | 8 (sep–dic 2026) | 0 |
| Segunda ejecución | 0 | 65 | 8 | 0 |

`verify_data.py` → **COMPLETO**: 64 archivos publicados, todos presentes, tamaño idéntico al
servidor y legibles.

| Taxi | 2024 | 2025 | 2026 (ene–ago) |
|---|---:|---:|---:|
| yellow | 41,169,720 | 48,722,602 | 29,703,355 |
| green | 660,218 | 591,375 | 337,114 |
| **Total** | | | **121,184,384 filas** |

## 8.3 ¿Siguen funcionando las consultas?

| Archivo | Resultado con los tres años | Cambio necesario |
|---|---|---|
| `sql/03_exploracion.sql` | ✅ sin cambios (fijado a 2026 por diseño) | ninguno |
| `sql/05_validacion_incorporacion.sql` | ✅ sin cambios; ya muestra 2024/2025/2026 y la columna `cbd_congestion_fee` presente en 2025–2026 | ninguno |
| `sql/07_indicadores.sql` | ✅ sin cambios, sobre Parquet y sobre la tabla | ninguno |
| `sql/04_eda.sql` | ✅ 20 de 21 sin cambios; ❌ `percentiles_distancia_duracion` falló por **memoria** | reescritura (ver abajo) |
| `sql/06_benchmark.sql` (B6) | misma consulta de percentiles | misma reescritura |
| `scripts/build_database.py` | ✅ reconstruye 121 M filas en 33 s (3.3 GB) | ninguno |

**El único cambio necesario fue de escala, no de esquema.** La consulta de percentiles hacía
`UNPIVOT` de los datos crudos antes de agregar: con dos años eran ~207 M de valores intermedios;
con tres, ~360 M, y la consulta falló con `Cannot allocate memory` (la máquina virtual de Docker
comparte 16 GB entre DuckDB y Metabase). Se reescribió para calcular los cuantiles de cada
columna en una sola pasada (`QUANTILE_CONT(col, [lista])`) y "despivotear" solo las 2 filas del
resultado: mismo resultado, una fracción de la memoria. Además `scripts/sqlrun.py` ahora fija
`memory_limit` (6 GB, configurable con `DUCKDB_MEMORY_LIMIT`) y un `temp_directory` para que DuckDB
pueda derramar a disco en lugar de competir por RAM con Metabase. Ningún cambio fue necesario por
la llegada de 2025 en sí: la deriva de esquema (`cbd_congestion_fee` nueva en 2025) ya la absorbía
el contrato de esquema de `sql/00_vistas.sql`.

## 8.4 Indicadores y tablero actualizados

El tablero se actualizó con dos comandos y **sin modificar ninguna consulta del Ej. 7**:

```bash
docker compose exec lab python scripts/build_database.py                      # 121 M filas
docker compose exec lab python scripts/setup_metabase.py --sql sql/07_indicadores.sql sql/08_evolucion.sql
```

Las series mensuales del Ej. 7 ahora cubren enero 2024 – agosto 2026, y se agregaron 8 tarjetas
de evolución (`E1`–`E8`) que comparan años usando **solo enero–agosto** en cada año, porque 2026
aún no tiene septiembre–diciembre (comparar un año completo contra 8 meses mezclaría estacionalidad
con tendencia).

## 8.5 Evolución de los indicadores (enero–agosto de cada año)

| Indicador | yellow 2024 | yellow 2025 | yellow 2026 | green 2024 | green 2025 | green 2026 |
|---|---:|---:|---:|---:|---:|---:|
| Viajes por día | 104,511 | **119,263** | 117,681 | 1,709 | 1,545 | **1,330** |
| Ingreso por día (M USD) | 2.96 | 3.38 | **3.55** | 0.041 | 0.038 | 0.034 |
| Ticket mediano (USD) | 21.00 | 21.57 | **23.58** | 19.15 | 19.70 | 20.52 |
| Distancia mediana (mi) | 1.80 | 1.87 | 1.92 | 1.96 | 2.02 | 2.14 |
| Tarifa mediana por milla (USD) | 7.14 | 7.04 | 7.38 | 6.72 | 6.69 | 6.62 |
| % pago con tarjeta | 75.9 | 68.9 | 65.6 | 70.6 | 74.7 | 76.9 |
| % sin dato de pago | 9.0 | 19.4 | **24.6** | 4.0 | 6.9 | 14.8 |
| % paga cargo CBD | 0 | 73.0 | 72.4 | 0 | 9.7 | 8.5 |
| Propina mediana (% tarifa) | 25.9 | 26.7 | 26.4 | 23.5 | 23.4 | 23.5 |

Otros indicadores:

- **Variación interanual (E2):** yellow +5.5% a +19.4% cada mes de 2025 vs 2024; en 2026 vs 2025
  entre −6.1% y +0.5% salvo enero (+9.5%). Green: **negativa todos los meses** (−4% a −18%).
- **Cuota green (E3):** de 1.83% (ene-2024) a 1.08–1.19% (2026).
- **Velocidad (E4, E5):** las curvas por hora de 2024, 2025 y 2026 prácticamente se superponen
  (p. ej. 5 h: 16.6 / 16.6 / 16.0 mph). En viajes dentro de Manhattan en días laborables de 7 a 19 h,
  la mediana fue 7.77 mph en 2024; en 2025, 7.51 mph para los viajes que pagan el cargo CBD y
  8.49 mph para los que no (≈7.75 mph combinado), y en 2026 7.06 / 8.14 mph.
- **Composición del pago promedio yellow (E6, efectivo y tarjeta):** total de US$ 28.67 → 28.99 →
  29.48. De los +US$ 0.81, el cargo CBD aporta +0.55; tarifa +0.29, propina +0.10; el recargo de
  congestión estatal se mantiene (~US$ 2.30).
- **Sin dato de pago por proveedor (E7):** sube en **ambos** proveedores principales: Vendor 2 de
  4.1% (ene-2024) a 20–25% (2025) y Vendor 1 de 3.8% a 15–20%.
- **Aeropuertos (E8):** JFK estable (4,956 → 5,084 → 4,675 viajes/día) y **LaGuardia en descenso**
  (3,376 → 3,305 → 2,987, −11.5%) aunque el total de viajes yellow creció.

## 8.6 Cambios y patrones visibles al considerar los tres años

1. **El taxi amarillo creció fuerte en 2025 y se estabilizó en 2026; el verde cae sin pausa.**
   Con solo 2024 y 2026 (Ej. 5) parecía un crecimiento continuo de +8–24%; con 2025 se ve que el
   salto ocurrió en 2025 (+14% en viajes/día ene–ago) y que 2026 está ligeramente por debajo
   (−1.3%). El green pierde 10–14% por año y su cuota baja de 1.8% a 1.1%. El año 2025 coincide con
   la entrada del peaje de congestión, que cobra a los vehículos de apps (FHV) un cargo mayor por
   viaje que a los taxis; los datos son consistentes con un traslado de demanda hacia el taxi
   amarillo, aunque con estos datos no se puede afirmar causalidad.
2. **El peaje de congestión se refleja en el precio pero no en la velocidad de los taxis.** El
   cargo CBD aparece de golpe en enero de 2025 en ~73% de los viajes yellow (≈10% green) y explica
   dos tercios del aumento del pago promedio. En cambio, la velocidad mediana de los taxis en
   Manhattan en horario laboral no mejora (7.77 mph en 2024 vs ≈7.75 en 2025). Hay que matizar:
   también hubo 14% más viajes de taxi en la misma zona, así que la velocidad de los taxis no es
   una medida limpia del tráfico general.
3. **La calidad de los datos empeora con el tiempo, y eso distorsiona los indicadores de pago.**
   Los viajes sin dato de pago pasan de 9% a 19% y 25% (yellow) y de 4% a 15% (green), en ambos
   proveedores. Por eso "% tarjeta" yellow cae de 76% a 66%: es sobre todo un cambio en lo que se
   reporta (Flex Fare / sin dato), no necesariamente en cómo se paga. Mirar un solo año ocultaba
   esta tendencia; con tres años es evidente y obliga a leer cualquier indicador de pago junto con
   el indicador de calidad.
4. **El viaje se encarece por recargos y por distancia, no por la tarifa base.** Ticket mediano
   yellow +12% (21.00 → 23.58), mientras la tarifa por milla se mueve dentro de ±4% y la distancia
   mediana sube 7% (1.80 → 1.92 mi). La propina como % de la tarifa es la variable más estable de
   todo el conjunto (~26% / ~23.5%).
5. **2025 tuvo un problema de calidad propio que no se ve con dos años.** El indicador de registros
   inválidos (I11) de los yellow sube de 3–4% a **6–11% durante 2025** y vuelve a ~4% en 2026. La
   causa es un solo proveedor: el Vendor 2 registró montos negativos (anulaciones/reembolsos) en el
   **7.4% de sus viajes de 2025**, contra 2.3% en 2024 y 0.7% en 2026. Esos registros quedan fuera
   de `trips_clean`, pero si se sumaran ingresos sobre los datos crudos, 2025 aparecería
   artificialmente más bajo. (Consulta `calidad_por_anio_y_proveedor` en `sql/05_validacion_incorporacion.sql` y tarjeta I11.)
6. **Los aeropuertos no acompañaron el crecimiento.** Mientras los viajes yellow totales crecen,
   los de LaGuardia caen 11.5% y JFK vuelve a niveles de 2024 → el crecimiento de 2025 vino de
   viajes urbanos.

## 8.7 Consultas

Todas en [`sql/08_evolucion.sql`](../sql/08_evolucion.sql) (E1–E8, con pregunta y justificación),
más las consultas sin cambios de `sql/05_validacion_incorporacion.sql` (validación) y
`sql/07_indicadores.sql` (series mensuales). Resultados completos con el SQL ejecutado en
[`docs/resultados/08_evolucion.md`](resultados/08_evolucion.md).
