# DS-Lab7 — Spark MLlib (ENEIC)

CC3066 Data Science, UVG, Semestre II 2026. Laboratorio 7: análisis exploratorio, segmentación con KMeans y predicción del salario mensual de personas asalariadas con regresión lineal y Random Forest (PySpark 3.5 / `pyspark.ml`), usando la Encuesta Nacional de Empleo e Ingresos Continua (ENEIC) del INE.

- Enunciado: [`Laboratorio_7_Spark_MLlib_2026.md`](Laboratorio_7_Spark_MLlib_2026.md)
- Notebook: [`Lab7_Spark_MLlib.ipynb`](Lab7_Spark_MLlib.ipynb)

## Datos

Entrenamiento: bases de **Personas** ENEIC I–IV 2025. Prueba: ENEIC I 2026.
Fuente: <https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/>

Los Excel (~210 MB) **no se versionan**. El notebook los descarga automáticamente del INE a `data/raw/` si no existen.

## Cómo ejecutarlo (Docker, recomendado)

Requisitos: Docker Desktop (se recomiendan ≥ 8 GB de RAM asignados).

```bash
docker compose up --build
```

Abrir <http://localhost:8888> y ejecutar `Lab7_Spark_MLlib.ipynb` de principio a fin (*Run → Run All Cells*). Spark UI en <http://localhost:4040>.

Ejecución sin interfaz (regenera el notebook con sus salidas):

```bash
docker compose run --rm pyspark jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 Lab7_Spark_MLlib.ipynb
```

> En Linux, si el contenedor no puede escribir en `data/` o `modelos/` por permisos del volumen, ejecutar con el usuario del host: `docker compose run --rm --user "$(id -u):$(id -g)" pyspark ...`.

## Sin Docker

Requiere Python 3.11 y Java 17 (`JAVA_HOME` configurado).

```bash
pip install -r requirements.txt
jupyter lab
```

## Estructura

```
Lab7_Spark_MLlib.ipynb   notebook con código, resultados y discusión
data/raw/                Excel del INE (descargados por el notebook, ignorados por git)
data/parquet/            Parquet crudo por archivo y conjuntos preparados 2025 / 2026 (ignorados)
modelos/                 pipelines de MLlib guardados (ignorados)
Dockerfile, docker-compose.yml, requirements.txt   ambiente reproducible
```
