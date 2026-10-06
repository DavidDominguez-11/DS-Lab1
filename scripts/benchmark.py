#!/usr/bin/env python3
"""Benchmark: consultar Parquet directamente vs. tabla materializada en DuckDB.

Para cada escenario (cantidad de datos) el script:
  1. Define las vistas Parquet de sql/00_vistas.sql restringidas a los archivos
     del escenario, y las vistas de analisis de sql/01_vistas_analisis.sql.
  2. Materializa esos mismos datos en data/processed/bench/<escenario>.duckdb
     (mismo procedimiento que scripts/build_database.py) y mide tiempo y tamanio.
  3. Ejecuta cada consulta de sql/06_benchmark.sql contra ambas estrategias:
     una ejecucion "primera" y REPETICIONES ejecuciones medidas, cada estrategia
     en su propia conexion nueva.
  4. Verifica que ambas estrategias devuelvan exactamente el mismo resultado.

Resultados:
  docs/resultados/06_benchmark.csv           un renglon por escenario/estrategia/consulta
  docs/resultados/06_benchmark_carga.csv     tiempo de materializacion y tamanios
  docs/resultados/06_benchmark.md            tablas resumen

Uso:
    python scripts/benchmark.py                 # todos los escenarios
    python scripts/benchmark.py --repeticiones 3 --escenarios 1_mes 2026
"""

import argparse
import csv
import glob
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_database import materializar  # noqa: E402
from sqlrun import (  # noqa: E402
    RAIZ_PROYECTO, VISTAS_ANALISIS, VISTAS_PARQUET, cargar_consultas,
)

# Escenarios de tamanio creciente, definidos por los meses (AAAA-MM) que incluyen.
# Un escenario cuyo conjunto de archivos coincide con el anterior se omite (p. ej.
# "todos" antes de descargar 2025 es igual a "2024+2026").
ESCENARIOS = {
    "1_mes":      ["2026-01"],
    "2026":       ["2026-*"],
    "2024+2026":  ["2024-*", "2026-*"],
    "todos":      ["*"],
}
REPETICIONES = 5
DIR_BENCH = RAIZ_PROYECTO / "data" / "processed" / "bench"
DIR_RESULTADOS = RAIZ_PROYECTO / "docs" / "resultados"

PATRON_YELLOW = "'data/raw/yellow/*/*.parquet'"
PATRON_GREEN = "'data/raw/green/*/*.parquet'"


def archivos(tipo: str, meses) -> list:
    rutas = set()
    for m in meses:
        rutas.update(glob.glob(f"data/raw/{tipo}/*/{tipo}_tripdata_{m}.parquet"))
    return sorted(rutas)


def sql_parquet_para(yellow, green) -> str:
    """sql/00_vistas.sql con los patrones glob sustituidos por listas de archivos."""
    lista = lambda rutas: "[" + ", ".join(f"'{r}'" for r in rutas) + "]"  # noqa: E731
    sql = VISTAS_PARQUET.read_text(encoding="utf-8")
    assert PATRON_YELLOW in sql and PATRON_GREEN in sql
    return sql.replace(PATRON_YELLOW, lista(yellow)).replace(PATRON_GREEN, lista(green))


def medir(con, sql: str, repeticiones: int):
    inicio = time.perf_counter()
    resultado = con.execute(sql).fetchall()
    primera = time.perf_counter() - inicio
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        con.execute(sql).fetchall()
        tiempos.append(time.perf_counter() - inicio)
    return primera, tiempos, resultado


def normalizar(filas):
    """Resultado comparable entre estrategias (redondea flotantes, ordena)."""
    def v(x):
        if isinstance(x, float):
            return round(x, 6)
        if isinstance(x, list):
            return tuple(v(i) for i in x)
        return x
    return sorted((tuple(v(c) for c in f) for f in filas), key=repr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repeticiones", type=int, default=REPETICIONES)
    parser.add_argument("--escenarios", nargs="+", choices=ESCENARIOS, default=list(ESCENARIOS))
    args = parser.parse_args()

    os.chdir(RAIZ_PROYECTO)
    consultas = {k: c for k, c in cargar_consultas("sql/06_benchmark.sql").items()
                 if not k.startswith("_anon_")}
    sql_analisis = VISTAS_ANALISIS.read_text(encoding="utf-8")
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)

    filas_csv, carga_csv = [], []
    vistos = set()
    for nombre in args.escenarios:
        yellow = archivos("yellow", ESCENARIOS[nombre])
        green = archivos("green", ESCENARIOS[nombre])
        clave = tuple(yellow + green)
        if not clave or clave in vistos:
            print(f"\n[{nombre}] se omite: mismo conjunto de archivos que un escenario anterior")
            continue
        vistos.add(clave)
        sql_parquet = sql_parquet_para(yellow, green)
        mb_parquet = sum(Path(f).stat().st_size for f in clave) / 2**20

        db = DIR_BENCH / f"{nombre.replace('+', '_')}.duckdb"
        carga = materializar(db, sql_parquet, sql_analisis)
        print(f"\n[{nombre}] {len(clave)} archivos, {carga['filas']:,} filas, "
              f"Parquet {mb_parquet:,.0f} MiB -> DuckDB {carga['bytes'] / 2**20:,.0f} MiB "
              f"en {carga['segundos']:.1f} s")
        carga_csv.append({
            "escenario": nombre, "archivos": len(clave), "filas": carga["filas"],
            "parquet_mib": round(mb_parquet, 1),
            "duckdb_mib": round(carga["bytes"] / 2**20, 1),
            "materializacion_s": round(carga["segundos"], 2),
        })

        resultados = {}
        for estrategia in ("parquet", "tabla"):
            if estrategia == "parquet":
                con = duckdb.connect()
                con.execute(sql_parquet)
                con.execute(sql_analisis)
            else:
                con = duckdb.connect(str(db), read_only=True)
            for c in consultas.values():
                primera, tiempos, res = medir(con, c.sql, args.repeticiones)
                resultados[(estrategia, c.nombre)] = normalizar(res)
                fila = {
                    "escenario": nombre, "filas": carga["filas"], "estrategia": estrategia,
                    "consulta": c.nombre, "primera_s": round(primera, 4),
                    "mediana_s": round(statistics.median(tiempos), 4),
                    "min_s": round(min(tiempos), 4), "max_s": round(max(tiempos), 4),
                    "repeticiones": args.repeticiones,
                }
                filas_csv.append(fila)
                print(f"  {estrategia:7} {c.nombre:22} primera {primera:7.3f} s  "
                      f"mediana {fila['mediana_s']:7.3f} s")
            con.close()

        for c in consultas.values():
            iguales = resultados[("parquet", c.nombre)] == resultados[("tabla", c.nombre)]
            for f in filas_csv:
                if f["escenario"] == nombre and f["consulta"] == c.nombre:
                    f["mismo_resultado"] = iguales
            if not iguales:
                print(f"  ADVERTENCIA: {c.nombre} devuelve resultados distintos")

    escribir_csv(DIR_RESULTADOS / "06_benchmark.csv", filas_csv)
    escribir_csv(DIR_RESULTADOS / "06_benchmark_carga.csv", carga_csv)
    escribir_md(DIR_RESULTADOS / "06_benchmark.md", filas_csv, carga_csv, args.repeticiones)
    print("\nResultados en docs/resultados/06_benchmark.{csv,md}")
    return 0


def escribir_csv(ruta: Path, filas) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def escribir_md(ruta: Path, filas, carga, repeticiones) -> None:
    escenarios = [c["escenario"] for c in carga]
    consultas = list(dict.fromkeys(f["consulta"] for f in filas))
    idx = {(f["escenario"], f["estrategia"], f["consulta"]): f for f in filas}
    lineas = [
        "# Resultados del benchmark Parquet vs tabla DuckDB",
        "",
        f"Generado por `scripts/benchmark.py` el "
        f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. DuckDB {duckdb.__version__}, "
        f"{os.cpu_count()} hilos, {platform.system()} {platform.machine()}. "
        f"Tiempo = mediana de {repeticiones} ejecuciones despues de una primera ejecucion "
        "(que se reporta aparte). No editar a mano.",
        "",
        "## Materializacion",
        "",
        "| Escenario | Archivos | Filas | Parquet (MiB) | DuckDB (MiB) | Materializacion (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for c in carga:
        lineas.append(f"| {c['escenario']} | {c['archivos']} | {c['filas']:,} | "
                      f"{c['parquet_mib']:,.0f} | {c['duckdb_mib']:,.0f} | {c['materializacion_s']:.1f} |")
    lineas += ["", "## Tiempo por consulta (mediana, segundos)", "",
               "| Consulta | " + " | ".join(f"{e} Parquet | {e} tabla | {e} aceleracion"
                                              for e in escenarios) + " |",
               "|---|" + "---:|" * (3 * len(escenarios))]
    for q in consultas:
        celdas = []
        for e in escenarios:
            p = idx[(e, "parquet", q)]["mediana_s"]
            t = idx[(e, "tabla", q)]["mediana_s"]
            celdas += [f"{p:.3f}", f"{t:.3f}", f"{p / t:.1f}x" if t else "-"]
        lineas.append(f"| {q} | " + " | ".join(celdas) + " |")
    lineas += ["", "## Primera ejecucion (segundos)", "",
               "| Consulta | " + " | ".join(f"{e} Parquet | {e} tabla" for e in escenarios) + " |",
               "|---|" + "---:|" * (2 * len(escenarios))]
    for q in consultas:
        celdas = []
        for e in escenarios:
            celdas += [f"{idx[(e, 'parquet', q)]['primera_s']:.3f}",
                       f"{idx[(e, 'tabla', q)]['primera_s']:.3f}"]
        lineas.append(f"| {q} | " + " | ".join(celdas) + " |")
    lineas += ["", "## Total de las consultas (suma de medianas, segundos)", "",
               "| Escenario | Parquet | Tabla | Aceleracion | Resultados identicos |",
               "|---|---:|---:|---:|---|"]
    for e in escenarios:
        p = sum(idx[(e, "parquet", q)]["mediana_s"] for q in consultas)
        t = sum(idx[(e, "tabla", q)]["mediana_s"] for q in consultas)
        ok = all(idx[(e, "parquet", q)].get("mismo_resultado") for q in consultas)
        lineas.append(f"| {e} | {p:.2f} | {t:.2f} | {p / t:.1f}x | {'si' if ok else 'NO'} |")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
