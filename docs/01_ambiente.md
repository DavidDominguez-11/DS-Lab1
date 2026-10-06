# Ejercicio 1 — Estructura del proyecto y preparación del ambiente

## Propósito de cada directorio

| Ruta | Propósito |
|---|---|
| `data/raw/` | Datos **originales** tal como los publica la TLC (`data/raw/<tipo>/<anio>/*.parquet`). Nunca se modifican: son la fuente de verdad y se pueden regenerar con el script de descarga. Ignorado por Git. |
| `data/processed/` | Productos **derivados** de los datos crudos: la base materializada `taxi.duckdb` (Ej. 6), la base de vistas para Metabase y archivos intermedios. Se puede borrar y reconstruir. Ignorado por Git. |
| `notebooks/` | Notebooks de Jupyter donde se ejecuta y narra el análisis (exploración, EDA, benchmark, gráficas). |
| `scripts/` | Código Python reutilizable y ejecutable por línea de comandos: descarga, verificación, construcción de la base, benchmark, ejecución de SQL. Es la parte "automatizable" del flujo. |
| `sql/` | Consultas SQL versionadas, una por archivo o por tema. Los notebooks y scripts las leen desde aquí, de modo que la consulta documentada es exactamente la consulta ejecutada. |
| `docs/` | Documentación del laboratorio: respuestas a cada ejercicio, inventario de datos, resultados del benchmark y evidencia del tablero. |
| `Dockerfile` | Imagen del ambiente de análisis (Python 3.11 + DuckDB + JupyterLab + pandas/pyarrow/matplotlib). |
| `metabase.Dockerfile` | Imagen de Metabase con el driver de DuckDB, usada como herramienta de visualización (Ej. 7). |
| `docker-compose.yml` | Orquesta ambos servicios, publica los puertos y monta las carpetas del proyecto dentro de los contenedores. |
| `README.md` | Instrucciones para reproducir todo el trabajo. |

La separación `raw` / `processed` hace explícito qué es dato fuente (inmutable) y qué es
producto del proceso (regenerable). La separación `sql` / `scripts` / `notebooks` evita
que la lógica quede escondida dentro de celdas de un notebook.

## 1.1–1.2 Fork, clonación y levantamiento

```bash
# 1. Fork de https://github.com/menene/duckdb desde la interfaz de GitHub
git clone https://github.com/<usuario>/duckdb.git
cd duckdb
git remote add upstream https://github.com/menene/duckdb.git   # opcional

# 2. Construir y levantar ambos servicios en segundo plano
docker compose up --build -d
docker compose ps
```

La primera construcción tarda varios minutos (descarga la imagen de Python, las
dependencias de `requirements.txt`, Metabase y el driver de DuckDB).

## 1.3 Verificación de los servicios

| Servicio | Contenedor | URL | Verificación | Resultado |
|---|---|---|---|---|
| JupyterLab | `lab8-lab` | <http://localhost:8888> | `curl http://127.0.0.1:8888/api/status` | HTTP 200 |
| Metabase | `lab8-metabase` | <http://localhost:3000> | `curl http://127.0.0.1:3000/api/health` | `{"status":"ok"}` |
| DuckDB (Python) | `lab8-lab` | — | `docker compose exec lab python -c "import duckdb; print(duckdb.sql('select version()'))"` | `v1.5.5` |

Ambos puertos se publican solo en `127.0.0.1`, por lo que no quedan expuestos a la red.
Jupyter corre sin token (ambiente local de laboratorio).

## 1.4 Herramientas disponibles

**Contenedor `lab` (Debian 13, Python 3.11.14)**

| Herramienta | Versión | Uso en el laboratorio |
|---|---|---|
| duckdb | 1.5.5 | Motor de consultas analíticas sobre Parquet y base materializada |
| jupyterlab | 4.6.4 | Notebooks de análisis |
| pandas | 3.0.6 | Recibir resultados pequeños de DuckDB para graficar |
| pyarrow | 25.0.1 | Intercambio columnar DuckDB ↔ pandas |
| matplotlib | 3.11.2 | Gráficas en los notebooks |
| requests | 2.34.2 | Descarga de los archivos de la TLC |
| curl | 8.14.1 | Pruebas manuales contra el servidor |

**Contenedor `metabase`**: Metabase v0.63.19 sobre OpenJDK 21 con el plugin
`duckdb.metabase-driver.jar` 1.5.5.0 (alineado con duckdb 1.5.5 de Python, condición
necesaria para que Metabase pueda abrir una base creada desde Python).

**Volúmenes**: `./data`, `./notebooks`, `./scripts`, `./sql` y `./docs` se montan en
`/workspace/...` dentro de `lab`; `./data` también se monta en `/workspace/data` dentro de
`metabase`. Los cambios hechos en el host se ven inmediatamente en los contenedores y
viceversa; nada importante vive solo dentro de un contenedor.

## 1.6 ¿Por qué un ambiente reproducible?

- **Mismos resultados en cualquier máquina.** Las versiones están fijadas
  (`duckdb==1.5.5`, imagen `python:3.11.14-slim`, Metabase `v0.63.19`). Un compañero o el
  docente obtiene exactamente las mismas librerías, sin el clásico "en mi máquina sí funciona".
- **Compatibilidad entre piezas.** El formato de archivo `.duckdb` y el driver de Metabase
  dependen de la versión de DuckDB; si cada quien instalara la suya, Metabase podría no
  abrir la base generada en Python. El ambiente congela esa combinación.
- **El análisis depende del código, no del estado de una laptop.** Los datos se
  regeneran con scripts y las consultas están versionadas, así que el ambiente + el repo
  bastan para reconstruir todo desde cero.
- **Aislamiento.** No se contamina la instalación de Python del sistema (en esta máquina,
  por ejemplo, el Python local es 3.14 y no tiene DuckDB; dentro del contenedor todo funciona igual).
- **Auditoría.** Un resultado de análisis solo es creíble si alguien más puede volver a
  obtenerlo; la reproducibilidad es parte de la validez del análisis.
