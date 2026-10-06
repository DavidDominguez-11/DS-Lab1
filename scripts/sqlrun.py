#!/usr/bin/env python3
"""Ejecuta archivos SQL documentados del directorio sql/ con DuckDB.

Cada archivo SQL contiene uno o varios bloques con este formato:

    -- name: conteo_registros
    -- objetivo: cuantas filas hay en total
    -- fuente: data/raw/*/2026/*.parquet
    SELECT COUNT(*) FROM read_parquet('data/raw/*/2026/*.parquet');

Los bloques sin `-- name:` (por ejemplo, la creacion de vistas) se ejecutan sin
mostrar resultados. Las rutas de los archivos SQL son relativas a la raiz del
proyecto, por lo que el script cambia a ese directorio antes de ejecutar.

Uso:
    python scripts/sqlrun.py sql/03_exploracion.sql                 # imprime resultados
    python scripts/sqlrun.py sql/03_exploracion.sql --md docs/resultados/03_exploracion.md
    python scripts/sqlrun.py sql/04_eda.sql --solo viajes_por_mes

Desde un notebook:
    from sqlrun import conectar, cargar_consultas
    con = conectar()                           # crea las vistas de sql/00 y sql/01
    q = cargar_consultas("sql/04_eda.sql")
    con.sql(q["viajes_por_mes"].sql).df()
"""

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
VISTAS_PARQUET = RAIZ_PROYECTO / "sql" / "00_vistas.sql"         # trips/zones sobre los archivos
VISTAS_ANALISIS = RAIZ_PROYECTO / "sql" / "01_vistas_analisis.sql"  # trips_clean, catalogos
MAX_FILAS_MD = 40


@dataclass
class Consulta:
    nombre: str
    sql: str
    meta: dict = field(default_factory=dict)


def cargar_consultas(ruta) -> dict:
    """Devuelve {nombre: Consulta} en el orden del archivo.

    Las sentencias sin nombre se guardan con claves `_anon_<n>`.
    """
    texto = (RAIZ_PROYECTO / ruta).read_text(encoding="utf-8")
    bloques = re.split(r"(?m)^(?=-- name:)", texto)
    consultas = {}
    for i, bloque in enumerate(bloques):
        if not bloque.strip():
            continue
        meta = dict(re.findall(r"(?m)^-- (\w+):\s*(.*)$", bloque))
        nombre = meta.pop("name", f"_anon_{i}")
        cuerpo = "\n".join(
            linea for linea in bloque.splitlines()
            if not re.match(r"^-- \w+:", linea)
        ).strip()
        if cuerpo.replace(";", "").strip():
            consultas[nombre] = Consulta(nombre, cuerpo, meta)
    return consultas


def conectar(base=None, read_only=False, vistas=True):
    """Conexion con el directorio de trabajo en la raiz y las vistas creadas."""
    os.chdir(RAIZ_PROYECTO)
    con = duckdb.connect(str(base) if base else ":memory:", read_only=read_only)
    if vistas and not read_only:
        con.execute(VISTAS_PARQUET.read_text(encoding="utf-8"))
        con.execute(VISTAS_ANALISIS.read_text(encoding="utf-8"))
    return con


def a_markdown(columnas, filas, max_filas=MAX_FILAS_MD) -> str:
    def fmt(v):
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "si" if v else "no"
        if isinstance(v, float):
            return f"{v:,.4f}".rstrip("0").rstrip(".") if abs(v) < 1e15 else f"{v:.3e}"
        if isinstance(v, int):
            return f"{v:,}" if abs(v) >= 10000 else str(v)   # sin coma en anios
        return str(v).replace("|", "\\|").replace("\n", " ")

    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for fila in filas[:max_filas]:
        lineas.append("| " + " | ".join(fmt(v) for v in fila) + " |")
    if len(filas) > max_filas:
        lineas.append(f"\n*... {len(filas) - max_filas} filas mas omitidas.*")
    return "\n".join(lineas)


def ejecutar(con, consulta: Consulta):
    inicio = time.perf_counter()
    rel = con.execute(consulta.sql)
    filas = rel.fetchall() if rel.description else []
    columnas = [d[0] for d in rel.description] if rel.description else []
    return columnas, filas, time.perf_counter() - inicio


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta un archivo SQL documentado.")
    parser.add_argument("archivo", help="ruta del .sql relativa a la raiz del proyecto")
    parser.add_argument("--md", help="escribe los resultados en este archivo markdown")
    parser.add_argument("--solo", nargs="+", help="ejecuta solo estas consultas")
    parser.add_argument("--db", help="base DuckDB a usar (por defecto, en memoria)")
    args = parser.parse_args()

    con = conectar(args.db)
    consultas = cargar_consultas(args.archivo)
    salida = [
        f"# Resultados de `{args.archivo}`",
        "",
        f"Generado con `python scripts/sqlrun.py {args.archivo}` "
        f"(DuckDB {duckdb.__version__}). No editar a mano.",
        "",
    ]
    for c in consultas.values():
        if c.nombre.startswith("_anon_"):
            con.execute(c.sql)
            continue
        if args.solo and c.nombre not in args.solo:
            continue
        columnas, filas, segundos = ejecutar(con, c)
        print(f"\n### {c.nombre}  ({segundos:.2f} s)")
        print(a_markdown(columnas, filas, max_filas=25))
        salida += [f"## `{c.nombre}`", ""]
        for clave in ("objetivo", "fuente"):
            if clave in c.meta:
                salida.append(f"- **{clave.capitalize()}:** {c.meta[clave]}")
        salida += [
            f"- **Tiempo:** {segundos:.2f} s", "",
            "```sql", c.sql, "```", "",
            a_markdown(columnas, filas), "",
        ]
    if args.md:
        destino = RAIZ_PROYECTO / args.md
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n".join(salida), encoding="utf-8")
        print(f"\nResultados escritos en {args.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
