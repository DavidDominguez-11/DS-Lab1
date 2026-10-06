# Ejercicio 7 — Indicadores y tablero

| Pieza | Archivo |
|---|---|
| Consultas de los indicadores (7.3, 7.7) | [`sql/07_indicadores.sql`](../sql/07_indicadores.sql) — cada bloque lleva pregunta, justificación, tipo de gráfica y tamaño |
| Construcción del tablero (7.4, 7.5) | [`scripts/setup_metabase.py`](../scripts/setup_metabase.py) — crea por API la conexión, las 16 tarjetas y el tablero |
| Base consultada | `data/processed/taxi.duckdb` (tabla materializada del Ej. 6), abierta por Metabase en **solo lectura** |
| Resultados de cada consulta | [`docs/resultados/07_indicadores.md`](resultados/07_indicadores.md) |
| Evidencia del tablero | [`docs/tablero/`](tablero/) — capturas y `tablero.json` (tarjetas, posición, filas devueltas y tiempo de cada una en Metabase) |

```bash
docker compose exec lab python scripts/build_database.py      # base para el tablero
docker compose exec lab python scripts/setup_metabase.py      # crea/actualiza el tablero
# abrir http://localhost:3000  (usuario admin@lab8.local / Lab8-DuckDB-2026)
```

**Por qué Metabase + tabla materializada:** el tablero ejecuta las mismas consultas una y otra vez
(cada vez que alguien lo abre o filtra). El Ej. 6 mostró que ese es justo el escenario donde la
tabla DuckDB gana (2–8× en agregaciones, hasta ~300× en filtros selectivos). Las 16 tarjetas
responden en 0.2–3 s sobre ~70 M de viajes. Metabase abre la base con `read_only = true`, así el
contenedor `lab` puede seguir consultando y la reconstrucción (`build_database.py` escribe un
archivo temporal y lo renombra) no se bloquea.

**Por qué el tablero se crea con un script:** un tablero armado con clics no es reproducible ni
versionable. Con `setup_metabase.py` el tablero es código: las consultas viven en `sql/`, el
script es idempotente (actualiza las tarjetas existentes por nombre de consulta) y al final ejecuta
cada tarjeta *dentro de Metabase* para verificar que responde (`status: completed`).

> **Nota sobre los datos.** La interpretación de la sección 7.8 corresponde al momento del
> Ejercicio 7, cuando solo estaban descargados 2024 y enero–agosto 2026 (69.2 M viajes válidos;
> resultados en `docs/resultados/07_indicadores.md`). Las capturas de `docs/tablero/` son del
> tablero **final**, después de incorporar 2025 en el Ejercicio 8 (114.5 M viajes; resultados en
> `docs/resultados/07_indicadores_3anios.md`): por eso sus números son mayores. Las consultas son
> las mismas; el tablero se actualizó solo al reconstruir la base.

## 7.1 Preguntas de análisis

| # | Pregunta |
|---|---|
| P1 | ¿Cuántos viajes diarios hace cada tipo de taxi y cómo evoluciona mes a mes? |
| P2 | ¿Cuánto ingreso genera el sistema cada mes? |
| P3 | ¿Se está encareciendo el viaje? ¿Es por precio o por distancia? |
| P4 | ¿Cómo pagan los pasajeros y cambia con el tiempo? |
| P5 | ¿Qué porcentaje de la tarifa se deja de propina? |
| P6 | ¿A qué horas es más lenta la ciudad? |
| P7 | ¿Cómo se reparte la demanda durante el día en días laborables y en fines de semana? |
| P8 | ¿En qué zonas comienzan más viajes? |
| P9 | ¿Qué peso tienen los aeropuertos en viajes e ingresos? |
| P10 | ¿Qué alcance tiene el cargo de congestión de Manhattan (CBD)? |
| P11 | ¿Qué peso tienen los taxis verdes frente a los amarillos? |
| P12 | ¿Qué tan confiables son los datos publicados cada mes? |
| P13 | ¿Qué parte de los viajes yellow se solicita por apps de terceros? |
| P14 | ¿Cuál es la escala del sistema (viajes, ingreso, ticket típico)? |

## 7.2 / 7.6 Indicadores, visualización y justificación

| Tarjeta | Indicador | Responde | Visualización | Justificación |
|---|---|---|---|---|
| K1 | Viajes válidos | P14 | número | Escala; contexto para el resto. |
| K2 | Ingreso total (M USD) | P14 | número | Dimensión económica del servicio. |
| K3 | Ticket mediano | P14 | número | Precio típico; mediana porque hay montos extremos (Ej. 3). |
| K4 | % de viajes green | P11 | número | Peso del servicio green. |
| I1 | Viajes por día, por mes y tipo | P1 | líneas (green en eje derecho) | Demanda normalizada por días del mes; la escala green es ~1% de la yellow, por eso un segundo eje. |
| I2 | Ingreso mensual por tipo | P2 | barras (green en eje derecho) | Combina volumen y precio; estacionalidad económica. |
| I3 | Ticket mediano y tarifa mediana por milla (yellow) | P3 | líneas, 2 ejes | La tarifa por milla separa el efecto precio del efecto distancia. |
| I4 | % de viajes por método de pago | P4 | área apilada al 100% | Proporciones que suman 100% por mes; muestra también el crecimiento de "sin dato". |
| I5 | Propina mediana como % de la tarifa (tarjeta) | P5 | líneas | Solo la tarjeta registra propina; mediana robusta. |
| I6 | Velocidad mediana por hora | P6 | líneas | Proxy directo de congestión (distancia/duración). |
| I7 | Viajes promedio por hora, laborable vs fin de semana | P7 | líneas | El patrón diario cambia por completo el fin de semana. |
| I8 | Top 12 zonas de origen | P8 | barras horizontales | Ranking con nombres largos → barras horizontales. |
| I9 | Aeropuertos: % de viajes, % de ingreso, ticket | P9 | tabla | Pocas filas y varias métricas que se comparan entre sí. |
| I10 | % de viajes que pagan el cargo CBD | P10 | líneas | Política nueva (ene-2025); la serie muestra su entrada en vigor. |
| I11 | % de registros inválidos por mes | P12 | líneas | Indicador de confiabilidad: condiciona la lectura del resto. |
| I12 | Origen de la solicitud (yellow, desde jun-2026) | P13 | barras apiladas al 100% | Columna nueva; composición por mes. |

Los indicadores se organizan en el tablero de arriba hacia abajo: escala (K1–K4) → demanda e
ingreso en el tiempo (I1–I2) → precio y pago (I3–I5) → patrones intradía (I6–I7) → geografía
(I8–I9) → políticas y nuevas fuentes (I10, I12) → calidad (I11). Todas las series de tiempo usan
el mismo eje "mes", de modo que se pueden leer en paralelo (p. ej., la caída de I1 en julio
coincide con la de I2, y el salto de "sin dato" de I4 coincide con I11 estable → no es basura sino
un cambio en lo que reporta un proveedor).

## 7.8 Interpretación (datos 2024 y ene–ago 2026)

- **Escala (K1–K4):** 69.2 M viajes válidos, US$ 2,023 M pagados, ticket mediano US$ 22.10. Los
  green son solo el **1.36%** de los viajes.
- **Demanda (I1):** yellow tiene dos valles por año — enero/febrero y julio/agosto (~92 mil
  viajes/día en 2024) — y picos en primavera y otoño (~117–119 mil). Entre 2024 y 2026 la demanda
  yellow sube (+8 a +24% según el mes) y la green baja (−18 a −27%).
- **Ingreso (I2):** sigue a la demanda: de US$ 78 M (ene-2024) a US$ 108 M (oct-2024) y US$ 96–121 M
  por mes en 2026.
- **Precio (I3):** el ticket mediano yellow pasa de US$ 20.52 (ene-2024) a ~US$ 24 (2026), +16%,
  mientras la tarifa por milla apenas cambia (7.1 → 7.0–7.7). El encarecimiento viene sobre todo de
  **recargos** (el cargo CBD de US$ 0.75 desde 2025) y de viajes algo más largos (distancia mediana
  yellow 1.80 → 1.92 mi), no de la tarifa base.
- **Pago (I4):** la tarjeta "cae" de 80% a ~63%, pero la categoría **sin dato / Flex Fare sube de 4%
  a ~25%**, mientras el efectivo yellow solo baja de 13.3% (2024) a 9.1% (2026). La caída de la
  tarjeta es en gran parte un cambio en el registro, no en el comportamiento → cualquier análisis de pagos debe excluir o tratar aparte el
  código 0.
- **Propina (I5):** muy estable: ~26% de la tarifa en yellow y ~23.5% en green durante todo el periodo.
- **Congestión (I6):** la velocidad cae de ~16 mph a las 5 h a ~8 mph entre 11 y 17 h en yellow; los
  green son algo más rápidos de día (operan fuera del centro de Manhattan).
- **Ritmo del día (I7):** días laborables con pico de 18 a 19 h (~8 mil viajes/h); fines de semana
  con demanda alta de madrugada (6.3 mil viajes a las 0 h vs 2.2 mil un día laborable) y mañana tardía.
- **Geografía (I8–I9):** 10 de las 12 zonas top están en Manhattan (Upper East Side y Midtown); JFK
  y LaGuardia están en el top-10. Los aeropuertos son 7.2% de los viajes pero **18.9% del ingreso**
  (ticket mediano de US$ 88 en JFK).
- **Cargo CBD (I10):** 0% en 2024 (no existía); en 2026 lo paga ~72% de los viajes yellow y ~8% de
  los green — la política recae casi completa en los yellow.
- **Calidad (I11):** 3–6% de registros inválidos por mes, con green consistentemente más alto que
  yellow; con 2024 y 2026 ningún mes es anómalo, lo que valida las series. (Al agregar 2025 en el
  Ej. 8, este mismo indicador detectó un aumento a 6–11% en los yellow de 2025 por montos negativos
  de un proveedor; ver docs/08.)
- **Apps (I12):** desde junio 2026, ~21% de los viajes yellow viene de la app de Uber.

### Principales hallazgos

1. **El taxi amarillo crece y el verde se encoge** entre 2024 y 2026 (I1).
2. **El viaje es ~16% más caro, pero no por la tarifa por milla** sino por recargos nuevos (I3, I10).
3. **Una parte grande del "cambio" en métodos de pago es un cambio de registro** (I4): sin el
   indicador de calidad y el desglose "sin dato", se concluiría erróneamente que la gente dejó de
   pagar con tarjeta.
4. **Los aeropuertos son desproporcionadamente importantes para el ingreso** (I9).
5. **Las apps ya son un canal relevante del taxi amarillo** (I12).
