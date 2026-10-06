# Ejercicio 9 — Discusión

## 9.1 ¿Qué características de DuckDB resultaron más útiles?

1. **Consultar Parquet en su lugar con patrones glob** (`read_parquet('data/raw/yellow/*/*.parquet')`).
   El "esquema" del conjunto de datos es la estructura de carpetas: incorporar 2024 y 2025 no
   requirió ningún paso de carga.
2. **`union_by_name = true`** (+ `UNION ALL BY NAME` para el contrato de esquema). Resolvió la
   deriva de esquema real de los datos (`cbd_congestion_fee` desde 2025, `request_source` desde
   junio 2026) y evitó el error silencioso de perder columnas.
3. **`filename = true`**: el año y mes de cada registro salen del nombre del archivo, lo que permitió
   detectar viajes fuera de su periodo y validar conteos por archivo.
4. **Funciones de metadatos** (`glob`, `parquet_file_metadata`, `parquet_schema`, `SUMMARIZE`,
   `DESCRIBE`): exploración y verificación de completitud sin leer los datos.
5. **SQL analítico expresivo**: `GROUP BY ALL`, `QUALIFY`, `FILTER (WHERE …)`, `PIVOT`/`UNPIVOT`,
   `QUANTILE_CONT` con listas, `MEDIAN`, `USING SAMPLE … REPEATABLE`. Consultas que en pandas
   requerirían varias etapas se escriben en una.
6. **Motor embebido y paralelo**: un `pip install`, sin servidor, usa los 16 hilos y procesa
   más datos que la RAM (agrega 121 M de filas en segundos).
7. **Vistas** como capa de normalización y limpieza versionada (`sql/00`, `sql/01`), y
   **`ATTACH`** para materializar una base desde las mismas vistas.
8. **El mismo motor en Python, en Metabase y en archivo**: la base creada en el notebook la abre
   Metabase con el driver de DuckDB, en modo `read_only`.

## 9.2 Ventajas y limitaciones de consultar Parquet directamente

| Ventajas | Limitaciones |
|---|---|
| Cero tiempo de carga y cero copia: los datos nuevos se consultan apenas se descargan. | Cada consulta vuelve a descomprimir/decodificar: 2–8× más lento que la tabla en agregaciones repetidas (Ej. 6). |
| Formato columnar: solo se leen las columnas usadas; `COUNT(*)` sale de los metadatos. | Costo fijo por archivo (abrir footers): los filtros muy selectivos tardan ~1 s con 40 archivos vs 3 ms en la tabla. |
| Ocupa ~40% menos disco que la base DuckDB (1.2 vs 1.9 GB con 2 años). | Hay que manejar la deriva de esquema explícitamente (`union_by_name`); sin ella se pierden columnas en silencio. |
| Fuente de verdad inmutable y portable (otras herramientas leen los mismos archivos). | Las vistas dependen de rutas relativas y del directorio de trabajo; no sirven tal cual para Metabase. |
| Escala con los archivos: agregar un año no cambia ninguna consulta. | No hay caché del Parquet decodificado entre consultas (la primera y las siguientes tardan lo mismo). |

## 9.3 Ventajas y limitaciones de las tablas materializadas

| Ventajas | Limitaciones |
|---|---|
| 1.7–2.6× más rápido en conjunto, hasta ~3000× en conteos y ~250× en filtros por fecha (zonemaps + catálogo). | Es una **copia**: hay que reconstruirla cuando llegan archivos (33 s para 121 M filas) o queda desactualizada. |
| Los bloques quedan en el buffer pool: ideal para consultas repetidas (tablero). | Ocupa ~1.66× el espacio del Parquet (3.3 GB con 3 años). |
| Latencia interactiva para Metabase (0.2–3 s por tarjeta con 70–120 M filas). | Un solo proceso escritor: Metabase debe abrirla en solo lectura y reconstruirse en un archivo aparte. |
| Las transformaciones (unir yellow+green, normalizar) se pagan una sola vez. | Para consultas limitadas por CPU (percentiles exactos) la ganancia es mínima (1.2×). |
| El archivo `.duckdb` es autocontenido y se abre desde cualquier herramienta compatible. | Acopla el formato a la versión de DuckDB (Python 1.5.5 = driver de Metabase 1.5.5.0). |

## 9.4 Ventajas frente a cargar todo con Pandas

Medición (`scripts/pandas_vs_duckdb.py`, salida en `docs/evidencia/pandas_vs_duckdb.log`):

| | pandas | DuckDB |
|---|---|---|
| Cargar 1 mes yellow (4.6 M filas) | 0.8–1.0 s, **652 MiB** en el DataFrame (pico de 1.8 GB de RAM del proceso) | no necesita cargar |
| Todo el conjunto (121 M filas) | ~**16.8 GiB** estimados solo para el DataFrame: más que la RAM total de la máquina (16 GB), sin contar copias intermedias | se consulta directamente |
| Viajes e ingreso por mes de **todos** los yellow (120 M filas) | inviable en esta máquina sin trocear manualmente los archivos | **1.9–2.3 s** (dos ejecuciones) |


- **Memoria:** pandas necesita todo el DataFrame en RAM. DuckDB procesa los archivos por bloques,
  solo con las columnas necesarias, y puede derramar a disco.
- **Velocidad:** DuckDB es vectorizado y usa todos los núcleos; pandas ejecuta la mayoría de
  operaciones en un solo hilo y materializa cada paso intermedio.
- **Proyección y filtros sobre el archivo:** DuckDB lee solo las columnas y row groups útiles;
  `pd.read_parquet` sin `columns`/`filters` lee todo.
- **Esquemas cambiantes:** concatenar 64 DataFrames con columnas distintas requiere código manual;
  en DuckDB es una opción (`union_by_name`).
- **SQL declarativo y versionable:** las consultas viven en `sql/` como texto, se documentan y se
  reutilizan idénticas en notebooks, scripts, benchmark y Metabase.
- **Rol de pandas en este flujo:** recibir resultados ya agregados (decenas de filas) para graficar.
  Esa división —DuckDB agrega, pandas/matplotlib presentan— es la que se usó en los notebooks.

## 9.5 ¿Qué permite incorporar nuevos datos con cambios mínimos?

- Años como parámetro (`ANIOS` / `--anio`): incorporar 2024 y 2025 fue cambiar **una línea** cada vez.
- Descarga idempotente (omite archivos existentes, valida PAR1 y `Content-Length`, consulta qué
  meses publica la TLC).
- Estructura de carpetas estable `data/raw/<tipo>/<año>/` + vistas con glob.
- Contrato de esquema (`union_by_name` + columnas opcionales declaradas).
- Metadatos derivados del nombre del archivo (`source_year`, `source_month`) en lugar de años fijos.
- Consultas que no mencionan años (salvo las que lo hacen a propósito) y comparaciones "ene–ago"
  calculadas a partir de los meses comunes.
- Base materializada y tablero regenerables con un comando cada uno.
- Verificación automática (`verify_data.py`, `05_validacion_incorporacion.sql`) para saber que la
  incorporación fue correcta.

## 9.6 ¿Qué debería automatizarse en producción?

1. **Descarga programada** (p. ej. diaria/semanal con cron, Airflow o GitHub Actions) del script
   actual: detecta solos los meses nuevos.
2. **Verificación como compuerta**: si `verify_data.py` o las consultas de validación fallan (filas
   que no cuadran, columna nueva, tasa de inválidos fuera de rango), no se publica la actualización y
   se alerta.
3. **Detección de deriva de esquema**: comparar `parquet_schema` del archivo nuevo contra el contrato
   y avisar de columnas nuevas o con tipo distinto (así se habría detectado `request_source`).
4. **Reconstrucción incremental de la base** (insertar solo los meses nuevos en lugar de reconstruir
   todo) y cambio atómico del archivo que lee Metabase, seguido del refresco de Metabase.
5. **Monitoreo de calidad** (el indicador I11 y el % sin dato de pago) con umbrales.
6. **Ejecución de las consultas/notebooks** para regenerar resultados y del benchmark ante cambios de
   versión de DuckDB.
7. Gestión de credenciales de Metabase por variables de entorno/secretos (aquí son locales y fijas).

## 9.7 Decisiones de diseño importantes para la reproducibilidad

- Ambiente Docker con versiones fijadas (DuckDB 1.5.5 alineado con el driver de Metabase).
- Datos fuera de Git (`.gitignore`) pero **regenerables** por script desde la fuente oficial, con
  inventario versionado (`docs/inventario_datos.md`) de lo que se descargó.
- Datos crudos inmutables; toda limpieza en vistas SQL documentadas, nunca reescribiendo archivos.
- SQL en archivos con metadatos (objetivo, fuente) y un único ejecutor (`sqlrun.py`) que genera los
  resultados en markdown: la consulta documentada **es** la consulta ejecutada.
- Rutas relativas a la raíz del proyecto resueltas desde `__file__` (no dependen del directorio actual).
- Muestras con semilla (`REPEATABLE (42)`) y consultas deterministas (desempates en `ORDER BY`).
- Base materializada y tablero de Metabase **generados por scripts** idempotentes, no por clics.
- Benchmark automatizado que además verifica que ambas estrategias den resultados idénticos.
- Commits por ejercicio que muestran la evolución del sistema (p. ej. el cambio de `ANIOS`).

## 9.8 ¿Qué se aprende que no sería evidente con datos pequeños?

- **La memoria es una restricción de diseño, no un detalle.** La consulta de percentiles funcionó con
  30 M y 72 M de filas y falló con 121 M; hubo que reescribirla para no generar intermedios de
  cientos de millones de filas y fijar `memory_limit`/`temp_directory`. Con un CSV pequeño cualquier
  forma de escribirla funciona.
- **Los errores de datos tienen estructura.** En 121 M de registros los problemas no son "ruido":
  un proveedor entero sin hora de llegada, otro sin tipo de pago, 25% de viajes sin dato de pago
  creciendo en el tiempo. Una muestra pequeña los haría parecer casos aislados.
- **El esquema cambia con el tiempo** y un error silencioso (columnas perdidas sin `union_by_name`)
  solo aparece al combinar muchos archivos de distintas épocas.
- **El orden y la organización física importan:** la misma consulta de "un día" tarda 3 ms o 1 s
  según cómo estén almacenados y ordenados los datos y cuántos archivos haya que abrir.
- **Leer menos es la principal optimización:** proyectar columnas, empujar filtros y agregar antes
  de traer datos a Python vale más que cualquier micro-optimización.
- **Promedios vs medianas:** con colas tan largas (distancias de 300 mil millas, totales de US$ 7 mil)
  los promedios engañan; hacen falta medianas, percentiles y filtros documentados.
- **Comparar periodos exige cuidado:** con un año incompleto (2026) hay que comparar los mismos meses;
  y cambios que parecían de comportamiento (menos pago con tarjeta) resultaron cambios de registro.
- **Materializar o no es un trade-off medible** (tiempo de carga, espacio, frescura vs latencia), no
  una regla fija.
