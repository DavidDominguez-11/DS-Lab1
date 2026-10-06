# Ejercicio 5 — Incorporación de los datos de 2024

- **Consultas de validación:** [`sql/05_validacion_incorporacion.sql`](../sql/05_validacion_incorporacion.sql)
- **Resultados:** [`docs/resultados/05_validacion_2024.md`](resultados/05_validacion_2024.md)
- **EDA re-ejecutado sin cambios sobre 2024 + 2026:** [`docs/resultados/04_eda_2024_2026.md`](resultados/04_eda_2024_2026.md)
- **Evidencia de descarga:** `docs/evidencia/descarga_2024_incorporacion.log`, `docs/evidencia/descarga_2024_segunda_ejecucion.log`

## 5.1 Modificación del sistema de descarga

Gracias a la parametrización del Ejercicio 2, el cambio completo fue **una línea**:

```diff
-ANIOS = (2026,)
+ANIOS = (2024, 2026)
```

(Equivalente sin tocar el código: `python scripts/download_data.py --anio 2024`.)
Los datos se obtienen directamente de la fuente original de la TLC
(`https://d37ci6vzurychx.cloudfront.net/trip-data/<tipo>_tripdata_2024-MM.parquet`).

## 5.2–5.4 Ejecución

```bash
docker compose exec lab python scripts/download_data.py
```

| Ejecución | Descargados | Ya existían | No publicados | Fallidos |
|---|---:|---:|---:|---:|
| Incorporación de 2024 | **24** (12 yellow + 12 green 2024) | **17** (16 de 2026 + tabla de zonas) | 8 (sep–dic 2026) | 0 |
| Segunda ejecución | 0 | 41 | 8 | 0 |

Los 16 archivos de 2026 se conservaron y **no se volvieron a descargar** (no se hizo ni
siquiera una petición HTTP por ellos).

## 5.5 Verificación de los nuevos archivos

1. `python scripts/verify_data.py --anio 2024 2026` → **COMPLETO**
   ([`docs/inventario_datos.md`](inventario_datos.md)): 12/12 meses de 2024 por tipo, tamaño
   idéntico al del servidor y legibles por DuckDB.

   | Taxi | Año | Meses | Filas |
   |---|---|---:|---:|
   | yellow | 2024 | 12 | 41,169,720 |
   | green | 2024 | 12 | 660,218 |
   | yellow | 2026 | 8 | 29,703,355 |
   | green | 2026 | 8 | 337,114 |

2. `archivos_por_anio`: 2024 tiene meses 01–12 para ambos tipos; 2026 sigue con 01–08.
3. `filas_metadatos_vs_lectura`: las filas declaradas en el footer de cada Parquet coinciden
   exactamente con las que lee la vista `trips` para cada tipo y año → ningún archivo se omite
   ni se lee dos veces.

## 5.6 Consulta conjunta de 2024 y 2026

`consulta_conjunta_rango_fechas` y `comparacion_mismo_mes_entre_anios` leen ambos años en una
sola consulta usando la misma vista `trips_clean`, sin unir manualmente nada:

| Tipo | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| yellow 2024 (viajes/día) | 92,522 | 100,000 | 110,921 | 113,757 | 116,652 | 114,223 | 95,885 | 92,447 |
| yellow 2026 | 114,862 | 116,082 | 122,934 | 124,116 | 127,858 | 123,186 | 109,284 | 103,354 |
| green 2024 | 1,720 | 1,738 | 1,745 | 1,765 | 1,854 | 1,723 | 1,565 | 1,571 |
| green 2026 | 1,251 | 1,278 | 1,371 | 1,412 | 1,390 | 1,415 | 1,271 | 1,249 |

Primer resultado conjunto: entre 2024 y 2026 los yellow **crecen entre 8% y 24%** según el mes,
mientras los green **caen entre 18% y 27%**. (Se analiza a fondo en el Ejercicio 8 junto con 2025.)

## 5.7 ¿Hay que modificar las consultas anteriores?

**No fue necesario modificar ninguna consulta para que funcionara.** Las 21 consultas de
`sql/04_eda.sql` se re-ejecutaron tal cual y ahora cubren ambos años
(`docs/resultados/04_eda_2024_2026.md`). Los tiempos pasaron de 0.5–15 s a 0.9–37 s, en línea
con el volumen ×2.4.

Sin embargo, hay que distinguir *funcionar* de *significar lo mismo*:

| Caso | Situación | Decisión |
|---|---|---|
| Consultas del Ej. 3 | Usan `glob('data/raw/*/2026/*.parquet')` o `WHERE source_year = 2026` a propósito | Se mantienen: documentan la exploración de 2026. |
| Consultas por mes (`viajes_por_mes`, `metodo_pago_por_mes`, …) | Agrupan por `date_trunc('month', pickup_at)`, que ya distingue años | Sin cambio. |
| Consultas agregadas globales (`comparacion_tipos`, `propinas`, `demanda_hora_dia`, …) | Ahora mezclan 2024 y 2026 en un solo promedio | Correcto como "panorama general"; para comparar años se agrega `source_year` al `GROUP BY` (Ej. 8). |
| `cbd_congestion_fee` | No existe en 2024 → la vista devuelve **NULL** (no 0) para 2024 | `recargos` usa `AVG(cbd_congestion_fee > 0)`: los NULL se excluyen del promedio, así que el % sigue refiriéndose a los viajes donde el cargo existe. Correcto, pero hay que leerlo así. |
| `request_source` | Solo existe desde 2026-06 | `despacho_por_aplicacion` ya filtraba por fecha. |
| `trips_clean` | Filtra con `source_year`/`source_month` del nombre de archivo, no con un año fijo | Funciona para cualquier año. |

### Riesgo detectado al incorporar 2024

Ahora el primer archivo en orden alfabético es `…/2024/…_2024-01.parquet`, que **no** tiene
`cbd_congestion_fee` ni `request_source`. Una lectura sin `union_by_name` (`riesgo_sin_union_by_name`)
pasa de 21 a **19 columnas** y pierde ambas columnas para *todos* los años, sin error. Cualquier
consulta que hubiera usado `read_parquet('…/*/*.parquet')` sin esa opción habría empezado a fallar
("columna no encontrada") o, peor, a dar resultados distintos solo por haber agregado archivos
viejos. La decisión del Ej. 3 de leer siempre con `union_by_name = true` dentro de las vistas
es lo que evitó el problema.

## 5.9 ¿Qué características del diseño permiten incorporar archivos sin modificar el flujo?

1. **Año como parámetro** (`ANIOS` / `--anio`): la descarga no tiene años "cableados".
2. **Convención de rutas estable** `data/raw/<tipo>/<año>/<nombre original>`: cada archivo nuevo
   cae en un lugar predecible.
3. **Vistas sobre patrones glob** (`data/raw/yellow/*/*.parquet`): el conjunto de datos se define
   por la carpeta, no por una lista de archivos. Un archivo nuevo aparece en todas las consultas
   automáticamente, sin pasos de carga.
4. **`union_by_name = true`** absorbe la deriva de esquema entre años (columnas nuevas = NULL en
   archivos viejos).
5. **Metadatos derivados del nombre del archivo** (`source_year`, `source_month` con
   `filename = true`): la limpieza y la validación no dependen de un año fijo.
6. **Una sola capa de normalización** (`sql/00_vistas.sql` + `sql/01_vistas_analisis.sql`): si la TLC cambia algo, se corrige en
   un lugar y todas las consultas lo heredan.
7. **Idempotencia**: el script puede re-ejecutarse cuantas veces sea; solo descarga lo que falta, y
   `verify_data.py` confirma el resultado.
