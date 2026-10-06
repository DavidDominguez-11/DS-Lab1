#!/usr/bin/env python3
"""Ejercicio 9.4: costo de cargar los datos con pandas vs agregarlos con DuckDB.

Carga UN mes de taxis amarillos con pandas, mide tiempo y memoria, y extrapola
al conjunto completo; luego hace el mismo calculo con DuckDB sobre todos los
archivos sin cargarlos en memoria.

Uso: python scripts/pandas_vs_duckdb.py
"""
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])

import time, glob, duckdb, pandas as pd, resource
f='data/raw/yellow/2025/yellow_tripdata_2025-05.parquet'
t=time.time(); df=pd.read_parquet(f); tl=time.time()-t
mem=df.memory_usage(deep=True).sum()/2**20
t=time.time(); r=df.groupby(df.tpep_pickup_datetime.dt.to_period('M')).total_amount.agg(['count','sum']); tg=time.time()-t
rows=len(df)
total_rows=sum(duckdb.sql(f"select sum(num_rows) from parquet_file_metadata('{x}')").fetchone()[0] for x in glob.glob('data/raw/*/*/*.parquet'))
print(f"filas_mes={rows} carga_s={tl:.2f} memoria_MiB={mem:.0f} groupby_s={tg:.2f} MiB_por_millon={mem/rows*1e6:.1f}")
print(f"filas_totales={total_rows} memoria_estimada_GiB={mem/rows*total_rows/1024:.1f} carga_estimada_s={tl/rows*total_rows:.0f}")
print('pico_RSS_MiB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
c=duckdb.connect(); t=time.time()
c.sql("select date_trunc('month',tpep_pickup_datetime) m, count(*), sum(total_amount) from read_parquet('data/raw/yellow/*/*.parquet', union_by_name=true) group by 1").fetchall()
print(f"duckdb_mismo_calculo_todos_los_yellow_s={time.time()-t:.2f}")
