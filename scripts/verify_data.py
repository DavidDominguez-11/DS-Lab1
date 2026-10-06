#!/usr/bin/env python3
"""Verifica que el conjunto de datos descargado este completo y sea legible.

Para cada tipo de taxi, anio y mes compara tres fuentes de verdad:

  1. El servidor de la TLC: que meses estan publicados y su Content-Length.
  2. El disco local: que archivos existen y su tamanio en bytes.
  3. DuckDB: que el archivo se pueda leer como Parquet y cuantas filas tiene
     (segun los metadatos del propio archivo).

Un mes se considera correcto solo si esta publicado, existe localmente, pesa
exactamente lo mismo que en el servidor y DuckDB puede leer sus metadatos.

Uso:
    python scripts/verify_data.py                    # anios de ANIOS
    python scripts/verify_data.py --anio 2024 2025 2026

Escribe el inventario en docs/inventario_datos.md y termina con codigo 1 si
algun mes publicado falta o no coincide.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from download_data import (  # noqa: E402
    ANIOS, RAIZ_PROYECTO, TIPOS_TAXI, construir_url, consultar_publicacion,
    ruta_destino,
)

SALIDA = RAIZ_PROYECTO / "docs" / "inventario_datos.md"


def filas_parquet(con, ruta: Path):
    """Cantidad de filas segun los metadatos del Parquet (no lee los datos)."""
    try:
        return con.execute(
            "SELECT SUM(num_rows) FROM parquet_file_metadata(?)", [str(ruta)]
        ).fetchone()[0]
    except duckdb.Error:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--anio", type=int, nargs="+", default=list(ANIOS))
    anios = sorted(set(parser.parse_args().anio))

    con = duckdb.connect()
    filas = []
    problemas = 0
    for anio in anios:
        for tipo in TIPOS_TAXI:
            for mes in range(1, 13):
                ruta = ruta_destino(tipo, anio, mes)
                estado, detalle = consultar_publicacion(construir_url(tipo, anio, mes))
                remoto = detalle if estado == "publicado" else None
                local = ruta.stat().st_size if ruta.exists() else None
                n = filas_parquet(con, ruta) if local else None

                if estado == "no_publicado" and local is None:
                    veredicto = "no publicado"
                elif estado == "error":
                    veredicto = f"ERROR servidor ({detalle})"
                elif local is None:
                    veredicto = "FALTA"
                elif remoto is not None and local != remoto:
                    veredicto = "TAMANIO DISTINTO"
                elif n is None:
                    veredicto = "ILEGIBLE"
                else:
                    veredicto = "ok"
                if veredicto not in ("ok", "no publicado"):
                    problemas += 1
                filas.append((tipo, anio, mes, estado, remoto, local, n, veredicto))
                print(f"{tipo:6} {anio}-{mes:02d}  {veredicto:16} filas={n}")

    escribir_inventario(filas, anios, problemas)
    print(f"\nInventario escrito en {SALIDA.relative_to(RAIZ_PROYECTO)}")
    print("COMPLETO" if problemas == 0 else f"INCOMPLETO: {problemas} problema(s)")
    return 0 if problemas == 0 else 1


def escribir_inventario(filas, anios, problemas) -> None:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lineas = [
        "# Inventario de datos descargados",
        "",
        f"Generado por `scripts/verify_data.py` el {ahora} para los anios "
        f"{', '.join(map(str, anios))}.",
        "",
        "Criterio: un mes esta completo si la TLC lo publica, existe en `data/raw/`, "
        "su tamanio coincide byte a byte con el `Content-Length` del servidor y DuckDB "
        "puede leer sus metadatos Parquet.",
        "",
        "## Resumen",
        "",
        "| Taxi | Anio | Meses publicados | Meses locales OK | Filas |",
        "|---|---|---:|---:|---:|",
    ]
    for anio in anios:
        for tipo in TIPOS_TAXI:
            grupo = [f for f in filas if f[0] == tipo and f[1] == anio]
            publicados = sum(f[3] == "publicado" for f in grupo)
            ok = sum(f[7] == "ok" for f in grupo)
            total = sum(f[6] or 0 for f in grupo)
            lineas.append(f"| {tipo} | {anio} | {publicados} | {ok} | {total:,} |")
    lineas += [
        "",
        f"**Estado: {'COMPLETO' if problemas == 0 else f'INCOMPLETO ({problemas} problemas)'}**",
        "",
        "## Detalle por archivo",
        "",
        "| Taxi | Mes | Servidor | Bytes servidor | Bytes local | Filas | Veredicto |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for tipo, anio, mes, estado, remoto, local, n, veredicto in filas:
        fmt = lambda v: f"{v:,}" if v is not None else "-"  # noqa: E731
        lineas.append(
            f"| {tipo} | {anio}-{mes:02d} | {estado} | {fmt(remoto)} | {fmt(local)} "
            f"| {fmt(n)} | {veredicto} |"
        )
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
