#!/usr/bin/env python3
"""Materializa los Parquet de data/raw/ en una base DuckDB (Ejercicio 6.2).

Crea data/processed/taxi.duckdb con:
  - tabla `trips`: el resultado de la vista `trips` de sql/00_vistas.sql
    (yellow + green normalizados, todos los anios descargados);
  - tabla `zones`: la tabla de zonas de la TLC;
  - las vistas de sql/01_vistas_analisis.sql (trips_clean, payment_types),
    que ahora leen las tablas en lugar de los Parquet.

Como las vistas de analisis son las mismas, cualquier consulta de sql/ se puede
ejecutar sin cambios contra los Parquet o contra esta base.

La base se reconstruye desde cero en un archivo temporal y se renombra al final:
el proceso es reproducible y una interrupcion no deja una base a medias.

Uso:
    python scripts/build_database.py
    python scripts/build_database.py --db data/processed/otra.duckdb

Nota: un archivo .duckdb admite un solo proceso escritor. Si Metabase tiene la
base abierta, detengalo antes (docker compose stop metabase).
"""

import argparse
import os
import sys
import time
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlrun import RAIZ_PROYECTO, VISTAS_ANALISIS, VISTAS_PARQUET  # noqa: E402

DB_POR_DEFECTO = RAIZ_PROYECTO / "data" / "processed" / "taxi.duckdb"


def materializar(destino: Path, sql_parquet: str, sql_analisis: str) -> dict:
    """Crea `destino` a partir de las vistas Parquet. Devuelve tiempos y tamanio."""
    os.chdir(RAIZ_PROYECTO)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + ".tmp")
    for f in (temporal, Path(str(temporal) + ".wal")):
        f.unlink(missing_ok=True)

    inicio = time.perf_counter()
    con = duckdb.connect()                      # vistas Parquet en memoria
    con.execute(sql_parquet)
    con.execute(f"ATTACH '{temporal.as_posix()}' AS db")
    con.execute("CREATE TABLE db.trips AS SELECT * FROM trips")
    con.execute("CREATE TABLE db.zones AS SELECT * FROM zones")
    con.execute("USE db")
    con.execute(sql_analisis)                   # trips_clean sobre la tabla
    filas = con.execute("SELECT COUNT(*) FROM db.trips").fetchone()[0]
    con.execute("CHECKPOINT db")
    con.close()
    segundos = time.perf_counter() - inicio

    temporal.replace(destino)
    return {"filas": filas, "segundos": segundos, "bytes": destino.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DB_POR_DEFECTO)
    args = parser.parse_args()
    destino = args.db if args.db.is_absolute() else RAIZ_PROYECTO / args.db

    r = materializar(
        destino,
        VISTAS_PARQUET.read_text(encoding="utf-8"),
        VISTAS_ANALISIS.read_text(encoding="utf-8"),
    )
    print(f"Base creada: {destino.relative_to(RAIZ_PROYECTO)}")
    print(f"  filas en trips : {r['filas']:,}")
    print(f"  tiempo         : {r['segundos']:.1f} s")
    print(f"  tamanio        : {r['bytes'] / 2**20:,.0f} MiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
