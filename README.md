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

<!-- TODO -->

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

<!-- TODO -->
