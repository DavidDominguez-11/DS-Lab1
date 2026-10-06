# Lab 8 - DuckDB

Repositorio base del laboratorio 8 del curso **CC3084 - Data Science**
(Universidad del Valle de Guatemala, Ciclo 2, 2026).

Este es el repositorio **proporcionado por el docente**. Contiene la estructura
del proyecto, el ambiente de ejecucion basado en Docker y un script que descarga
los datos de **2026**. Todo lo demas debe ser construido por cada equipo.

## Trabajo con fork

El laboratorio se desarrolla y se entrega sobre un **fork** de este repositorio.
No se trabaja directamente sobre el repositorio del docente.

1. Realice un fork de este repositorio:
   <https://github.com/menene/duckdb>

2. Clone **su propio fork** (no el del docente):

   ```bash
   git clone https://github.com/<su-usuario>/duckdb.git
   cd duckdb
   ```

3. Opcional, para recibir correcciones publicadas por el docente:

   ```bash
   git remote add upstream https://github.com/menene/duckdb.git
   git fetch upstream
   ```

Realice commits frecuentes y descriptivos: el historial del repositorio es parte
de la evaluacion. **La entrega del laboratorio es la URL de su fork.**

## Estructura

```text
duckdb/
|
+-- data/
|   +-- raw/
|   +-- processed/
|
+-- notebooks/
|
+-- scripts/
|
+-- sql/
|
+-- docs/
|
+-- Dockerfile
+-- metabase.Dockerfile
+-- docker-compose.yml
+-- README.md
```

## Requisitos

- Docker, con Docker Compose
- Git

La primera construccion del ambiente descarga varios cientos de MB y puede
tardar algunos minutos.

Considere el espacio en disco: las imagenes de Docker ocupan unos 3 GB y los
datos de los tres anios del laboratorio superan 1.5 GB, a los que se suma la
base materializada del Ejercicio 6. Se recomienda tener al menos 10 GB libres.

## Datos

El repositorio incluye `scripts/download_data.py`, que descarga los archivos de
2026 publicados por la TLC (`--help` muestra las opciones disponibles). Los
archivos se guardan en `data/raw/<tipo>/<anio>/`.

La TLC publica cada mes con varias semanas de atraso, por lo que los ultimos
meses de 2026 todavia no existen. El script consulta al servidor que meses estan
publicados, de modo que vuelve a ejecutarse sin problema conforme aparezcan
nuevos archivos.

Los datos descargados **no deben incluirse en el repositorio Git**. El archivo
`.gitignore` ya esta configurado para evitarlo.

Fuente de datos: NYC TLC Trip Record Data
<https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

Dentro de los contenedores, la carpeta `data/` del proyecto esta montada en
`/workspace/data`. Esa es la ruta que deben usar las herramientas que corren
dentro del ambiente, no la ruta de su computadora.

> **Nota sobre DuckDB:** un archivo `.duckdb` admite un solo proceso con permiso
> de escritura a la vez. Si conecta una herramienta externa a su base de datos,
> use el modo de solo lectura (`read_only`) en esa conexion; de lo contrario los
> demas procesos no podran abrir el archivo.

## Material a entregar

Al finalizar, su fork debe contener:

- el codigo fuente modificado y los scripts de descarga;
- las consultas SQL desarrolladas;
- el notebook o notebooks utilizados;
- la documentacion de las consultas;
- los scripts utilizados para los benchmarks;
- el codigo de los indicadores y visualizaciones;
- el tablero o la evidencia del tablero desarrollado;
- este `README.md`, completado segun la siguiente seccion.

Los archivos de datos descargados **no** deben incluirse.

---

# Documentacion del equipo

Las siguientes secciones deben ser completadas por cada equipo. El README final
debe permitir que una persona que no participo en el desarrollo pueda levantar el
ambiente, descargar los datos, ejecutar el analisis, reproducir los benchmarks y
generar los resultados principales.

## Como levantar el ambiente

Requisitos: Docker Desktop (o Docker Engine) con Docker Compose v2 en ejecucion,
Git y unos 10 GB libres.

```bash
git clone https://github.com/<su-usuario>/duckdb.git
cd duckdb
docker compose up --build -d      # construye y levanta ambos servicios
docker compose ps                 # lab8-lab y lab8-metabase deben estar "Up"
```

| Servicio | URL | Comprobacion |
|---|---|---|
| JupyterLab (Python 3.11 + DuckDB 1.5.5) | <http://localhost:8888> | `curl http://127.0.0.1:8888/api/status` -> 200 |
| Metabase + driver DuckDB | <http://localhost:3000> | `curl http://127.0.0.1:3000/api/health` -> `{"status":"ok"}` |

Todos los comandos de este README se ejecutan **dentro** del contenedor `lab`
con `docker compose exec lab <comando>`, desde la raiz del repositorio. Asi no
se necesita Python ni DuckDB instalados en la computadora.

Para detener el ambiente: `docker compose down` (los datos en `data/` se
conservan; la configuracion de Metabase vive en el volumen `metabase-data`).

Detalle de la estructura, herramientas disponibles y justificacion:
[`docs/01_ambiente.md`](docs/01_ambiente.md).

## Como descargar los datos

```bash
docker compose exec lab python scripts/download_data.py      # descarga lo que falte
docker compose exec lab python scripts/verify_data.py        # comprueba completitud
```

- Los anios se configuran en `ANIOS` dentro de `scripts/download_data.py`
  (o con `--anio 2024 2025`). Tambien acepta `--taxi yellow|green|all`.
- Los archivos quedan en `data/raw/<tipo>/<anio>/<tipo>_tripdata_<AAAA-MM>.parquet`
  y la tabla de zonas en `data/raw/misc/taxi_zone_lookup.csv`.
- Es **idempotente**: un archivo que ya existe y es un Parquet valido no se
  vuelve a descargar (ni siquiera se consulta al servidor); uno corrupto se
  reemplaza. Los meses que la TLC aun no publica se reportan como "no publicados".
- `verify_data.py` compara cada mes contra el servidor (publicado y
  `Content-Length`) y contra DuckDB (filas legibles), y escribe
  [`docs/inventario_datos.md`](docs/inventario_datos.md). Termina con codigo 1
  si falta algo.

Cambios al script original y evidencia: [`docs/02_descarga.md`](docs/02_descarga.md),
[`docs/05_incorporacion_2024.md`](docs/05_incorporacion_2024.md) y
[`docs/08_tres_anios.md`](docs/08_tres_anios.md).

## Como ejecutar el analisis

Todas las consultas estan en `sql/`, una por bloque, con nombre, objetivo y
fuente. `scripts/sqlrun.py` las ejecuta y escribe un markdown con el SQL, el
resultado y el tiempo de cada una (`docs/resultados/`), de modo que la consulta
documentada es exactamente la ejecutada.

| Paso | Comando (dentro de `docker compose exec lab ...`) | Documentacion |
|---|---|---|
| Vistas sobre Parquet | `sql/00_vistas.sql` (capa de lectura) y `sql/01_vistas_analisis.sql` (`trips_clean`); se crean solas al conectar | [docs/03](docs/03_consultas_directas.md) |
| Ej. 3 Exploracion directa | `python scripts/sqlrun.py sql/03_exploracion.sql --md docs/resultados/03_exploracion.md` | [docs/03](docs/03_consultas_directas.md) |
| Ej. 4 EDA | `python scripts/sqlrun.py sql/04_eda.sql --md docs/resultados/04_eda_3anios.md` | [docs/04](docs/04_eda.md) |
| Ej. 5/8 Validacion de anios | `python scripts/sqlrun.py sql/05_validacion_incorporacion.sql --md docs/resultados/05_validacion_2025.md` | [docs/05](docs/05_incorporacion_2024.md) |
| Ej. 6 Base materializada | `python scripts/build_database.py` (detener Metabase antes) | [docs/06](docs/06_benchmark.md) |
| Ej. 7 Indicadores | `python scripts/sqlrun.py sql/07_indicadores.sql --db data/processed/taxi.duckdb --md docs/resultados/07_indicadores_3anios.md` | [docs/07](docs/07_indicadores.md) |
| Ej. 7/8 Tablero | `python scripts/setup_metabase.py --sql sql/07_indicadores.sql sql/08_evolucion.sql` | [docs/07](docs/07_indicadores.md) |
| Ej. 8 Evolucion | `python scripts/sqlrun.py sql/08_evolucion.sql --db data/processed/taxi.duckdb --md docs/resultados/08_evolucion.md` | [docs/08](docs/08_tres_anios.md) |
| Ej. 9 Discusion | — | [docs/09](docs/09_discusion.md) |

Notebooks (JupyterLab en <http://localhost:8888>, carpeta `notebooks/`):
`03_exploracion`, `04_eda`, `06_benchmark`, `08_tres_anios`. Usan las mismas
consultas de `sql/` mediante `from sqlrun import conectar, cargar_consultas` y
guardan sus graficas en `docs/figuras/`.

Algunos archivos de `docs/resultados/` son **instantaneas** de cuando solo
existian ciertos anios (`04_eda.md` y `07_indicadores.md`: antes de 2025;
`05_validacion_2024.md`, `04_eda_2024_2026.md`: antes de 2025). Las vistas leen
todos los archivos presentes, asi que al re-ejecutarlas hoy incluyen los tres
anios; para reproducir una instantanea, descargue solo esos anios
(`download_data.py --anio ...`) en un clon limpio.

DuckDB usa como maximo 6 GB de RAM (`DUCKDB_MEMORY_LIMIT`) y derrama a
`data/processed/duckdb_tmp/` si hace falta.

## Como reproducir los benchmarks

```bash
docker compose exec lab python scripts/benchmark.py          # ~10-15 min con 3 anios
docker compose exec lab python scripts/benchmark.py --repeticiones 3 --escenarios 1_mes 2026   # version corta
```

Para cada escenario (`1_mes`, `2026`, `2024+2026`, `todos`) el script
materializa los archivos en `data/processed/bench/<escenario>.duckdb`, ejecuta
las consultas de [`sql/06_benchmark.sql`](sql/06_benchmark.sql) contra los
Parquet y contra la tabla (1 ejecucion inicial + 5 medidas, mediana), verifica
que ambas den el mismo resultado y escribe `docs/resultados/06_benchmark.{md,csv}`.
Las graficas se regeneran con `notebooks/06_benchmark.ipynb`. Analisis:
[`docs/06_benchmark.md`](docs/06_benchmark.md).

Los tiempos dependen de la maquina; para comparar, cierre otras cargas pesadas
(incluido Metabase: `docker compose stop metabase`) mientras corre.

## Como generar los resultados principales

Un solo comando, desde la raiz del repositorio en la computadora (Linux, macOS
o Git Bash en Windows), regenera todo: descarga, verificacion, consultas,
base materializada, tablero de Metabase y notebooks.

```bash
bash scripts/run_all.sh               # ~10 min + descarga (~2 GB la primera vez)
bash scripts/run_all.sh --benchmark   # incluye el benchmark (~15 min mas)
```

Resultados:

| Resultado | Ubicacion |
|---|---|
| Inventario de datos descargados | [`docs/inventario_datos.md`](docs/inventario_datos.md) |
| Resultados de cada consulta (SQL + tabla + tiempo) | [`docs/resultados/`](docs/resultados/) |
| Benchmark | [`docs/resultados/06_benchmark.md`](docs/resultados/06_benchmark.md) |
| Graficas | [`docs/figuras/`](docs/figuras/) |
| Tablero | <http://localhost:3000> → coleccion "Lab 8 - DuckDB" → "Taxis NYC - Indicadores" (usuario `admin@lab8.local`, contrasena `Lab8-DuckDB-2026`; instancia local, solo en 127.0.0.1). Evidencia en [`docs/tablero/`](docs/tablero/) |
| Respuestas de cada ejercicio | [`docs/01_ambiente.md`](docs/01_ambiente.md) … [`docs/09_discusion.md`](docs/09_discusion.md) |

### Hallazgos principales

1. Desde junio 2026, ~21% de los viajes yellow se solicita por la app de Uber (`request_source = HV0003`).
2. Los errores de datos son sistematicos por proveedor (VendorID 7 sin hora de llegada, VendorID 6 sin tipo de pago).
3. Yellow crecio 14% en 2025 y se estabilizo en 2026; green cae 10-14% por anio (cuota 1.8% -> 1.1%).
4. El cargo de congestion (CBD, 2025) lo paga ~73% de los viajes yellow y explica 2/3 del aumento del pago promedio, sin mejora visible en la velocidad de los taxis.
5. Los viajes sin dato de pago pasan de 9% a 25% (yellow): la "caida" del pago con tarjeta es en gran parte un cambio de registro.
6. Consultar Parquet directo es 1.7-2.6x mas lento que la tabla DuckDB en conjunto (hasta ~250x en filtros por fecha y ~3000x en conteos), a cambio de cero carga y datos siempre frescos.
