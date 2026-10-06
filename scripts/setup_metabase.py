#!/usr/bin/env python3
"""Configura el tablero de Metabase a partir de los archivos SQL (Ejercicios 7 y 8).

Todo el tablero se construye por la API de Metabase, de modo que se puede
reproducir desde cero sin hacer clics:

  1. Completa la configuracion inicial de Metabase (usuario administrador) si
     todavia no se hizo.
  2. Registra data/processed/taxi.duckdb como base de datos DuckDB en modo
     SOLO LECTURA (asi no bloquea al contenedor `lab`).
  3. Crea o actualiza una pregunta (card) de SQL nativo por cada bloque de los
     archivos de indicadores, usando sus metadatos (visual, x, y, serie, ...).
  4. Crea o actualiza el tablero y acomoda las tarjetas.
  5. Ejecuta cada tarjeta dentro de Metabase para validar que funciona y
     guarda la definicion del tablero en docs/tablero/tablero.json.

Es idempotente: se puede ejecutar de nuevo despues de cambiar el SQL o de
incorporar mas datos (las tarjetas se actualizan por nombre).

Uso (desde el contenedor lab, que ve a Metabase como http://metabase:3000):
    python scripts/setup_metabase.py
    python scripts/setup_metabase.py --sql sql/07_indicadores.sql sql/08_evolucion.sql

Credenciales: variables MB_EMAIL y MB_PASSWORD (por defecto las del README,
solo validas para esta instancia local publicada en 127.0.0.1).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlrun import RAIZ_PROYECTO, cargar_consultas  # noqa: E402

MB_URL = os.environ.get("MB_URL", "http://metabase:3000")
MB_EMAIL = os.environ.get("MB_EMAIL", "admin@lab8.local")
MB_PASSWORD = os.environ.get("MB_PASSWORD", "Lab8-DuckDB-2026")
NOMBRE_DB = "Taxis NYC (DuckDB)"
RUTA_DB_EN_METABASE = "/workspace/data/processed/taxi.duckdb"
NOMBRE_COLECCION = "Lab 8 - DuckDB"
NOMBRE_TABLERO = "Taxis NYC - Indicadores"
SQL_POR_DEFECTO = ["sql/07_indicadores.sql"]
DIR_EVIDENCIA = RAIZ_PROYECTO / "docs" / "tablero"
ANCHO_GRILLA = 24

TEXTO_INTRO = (
    "## Viajes de taxi de Nueva York (TLC) — yellow y green\n"
    "Fuente: archivos Parquet de la TLC materializados en `taxi.duckdb` "
    "(`scripts/build_database.py`). Todas las tarjetas usan la vista `trips_clean` "
    "(sin registros inválidos, ver docs/03). Cada tarjeta es una consulta SQL de "
    "`sql/07_indicadores.sql` / `sql/08_evolucion.sql`; la descripción de la tarjeta "
    "indica la pregunta que responde."
)


class Metabase:
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.s = requests.Session()

    def req(self, metodo, ruta, **kw):
        r = self.s.request(metodo, f"{self.url}/api{ruta}", timeout=300, **kw)
        if not r.ok:
            raise RuntimeError(f"{metodo} {ruta} -> {r.status_code}: {r.text[:500]}")
        return r.json() if r.content and "json" in r.headers.get("Content-Type", "") else r.content

    def esperar(self):
        for _ in range(60):
            try:
                if self.s.get(f"{self.url}/api/health", timeout=5).json().get("status") == "ok":
                    return
            except requests.RequestException:
                pass
            time.sleep(5)
        raise RuntimeError("Metabase no responde")


def configurar_inicial(mb: Metabase):
    props = mb.req("GET", "/session/properties")
    if props.get("has-user-setup"):
        return
    print("Configuracion inicial de Metabase (usuario administrador)")
    mb.req("POST", "/setup", json={
        "token": props["setup-token"],
        "user": {"email": MB_EMAIL, "password": MB_PASSWORD, "first_name": "Lab",
                 "last_name": "Ocho", "site_name": "Lab 8 DuckDB"},
        "prefs": {"site_name": "Lab 8 DuckDB", "site_locale": "es", "allow_tracking": False},
    })


def iniciar_sesion(mb: Metabase):
    sesion = mb.req("POST", "/session", json={"username": MB_EMAIL, "password": MB_PASSWORD})
    mb.s.headers["X-Metabase-Session"] = sesion["id"]


def base_de_datos(mb: Metabase) -> int:
    detalles = {"database_file": RUTA_DB_EN_METABASE, "read_only": True,
                "old_implicit_casting": True}
    for db in mb.req("GET", "/database")["data"]:
        if db["name"] == NOMBRE_DB:
            mb.req("PUT", f"/database/{db['id']}", json={"details": detalles})
            mb.req("POST", f"/database/{db['id']}/sync_schema")
            return db["id"]
    db = mb.req("POST", "/database", json={
        "engine": "duckdb", "name": NOMBRE_DB, "details": detalles, "is_full_sync": True,
    })
    print(f"Base de datos registrada: {NOMBRE_DB} (id {db['id']})")
    return db["id"]


def coleccion(mb: Metabase) -> int:
    for c in mb.req("GET", "/collection"):
        if c.get("name") == NOMBRE_COLECCION and not c.get("archived"):
            return c["id"]
    return mb.req("POST", "/collection", json={"name": NOMBRE_COLECCION, "color": "#509EE3"})["id"]


def titulo(nombre: str) -> str:
    codigo, _, resto = nombre.partition("_")
    return f"{codigo} · {resto.replace('_', ' ').capitalize()}"


def ajustes_visuales(meta: dict) -> dict:
    v = {}
    if meta.get("x"):
        v["graph.dimensions"] = [meta["x"]] + ([meta["serie"]] if meta.get("serie") else [])
    if meta.get("y"):
        v["graph.metrics"] = [c.strip() for c in meta["y"].split(",")]
    if meta.get("apilado") == "true":
        v["stackable.stack_type"] = "stacked"
    if meta.get("visual") in ("line", "area"):
        v["graph.show_values"] = False
    if meta.get("eje_derecho"):        # series de escala muy distinta (green vs yellow)
        v["series_settings"] = {serie.strip(): {"axis": "right"}
                                for serie in meta["eje_derecho"].split(",")}
    return v


def tarjetas(mb: Metabase, db_id: int, col_id: int, archivos) -> list:
    # las tarjetas se identifican por el nombre de la consulta guardado al final
    # de su descripcion, asi cambiar el titulo no crea duplicados
    existentes = {}
    for card in mb.req("GET", "/card", params={"f": "all"}):
        m = re.search(r"\((\w+)\)$", card.get("description") or "")
        if m and card.get("collection_id") == col_id and not card.get("archived"):
            existentes[m.group(1)] = card
    resultado = []
    for archivo in archivos:
        for c in cargar_consultas(archivo).values():
            if c.nombre.startswith("_anon_"):
                continue
            cuerpo = {
                "name": f"{c.nombre.split('_')[0]} · {c.meta['titulo']}" if "titulo" in c.meta
                        else titulo(c.nombre),
                "description": f"{c.meta.get('pregunta', '')}\n\nJustificación: "
                               f"{c.meta.get('justificacion', '')}\n\nSQL: {archivo} ({c.nombre})",
                "display": c.meta.get("visual", "table"),
                "visualization_settings": ajustes_visuales(c.meta),
                "collection_id": col_id,
                "dataset_query": {"type": "native", "database": db_id,
                                  "native": {"query": c.sql.rstrip().rstrip(";")}},
            }
            previa = existentes.get(c.nombre)
            card = (mb.req("PUT", f"/card/{previa['id']}", json=cuerpo) if previa
                    else mb.req("POST", "/card", json=cuerpo))
            ancho, alto = (int(x) for x in c.meta.get("tamano", "12,6").split(","))
            resultado.append({"id": card["id"], "nombre": c.nombre, "titulo": cuerpo["name"],
                              "ancho": ancho, "alto": alto})
            print(f"  tarjeta {'actualizada' if previa else 'creada':11} {cuerpo['name']}")
    return resultado


def tablero(mb: Metabase, col_id: int, cards: list) -> int:
    dash = next((d for d in mb.req("GET", "/dashboard")
                 if d["name"] == NOMBRE_TABLERO and not d.get("archived")), None)
    if dash is None:
        dash = mb.req("POST", "/dashboard", json={"name": NOMBRE_TABLERO, "collection_id": col_id})
    dashcards = [{
        "id": -1, "card_id": None, "row": 0, "col": 0, "size_x": ANCHO_GRILLA, "size_y": 4,
        "visualization_settings": {"virtual_card": {"name": None, "display": "text",
                                                    "visualization_settings": {},
                                                    "dataset_query": {}, "archived": False},
                                   "text": TEXTO_INTRO},
    }]
    fila, col, alto_fila = 4, 0, 0
    for i, c in enumerate(cards, start=2):
        if col + c["ancho"] > ANCHO_GRILLA:
            fila, col, alto_fila = fila + alto_fila, 0, 0
        dashcards.append({"id": -i, "card_id": c["id"], "row": fila, "col": col,
                          "size_x": c["ancho"], "size_y": c["alto"]})
        col += c["ancho"]
        alto_fila = max(alto_fila, c["alto"])
    mb.req("PUT", f"/dashboard/{dash['id']}", json={
        "dashcards": dashcards,
        "description": "Tablero del Lab 8 (CC3084). Generado por scripts/setup_metabase.py.",
    })
    return dash["id"]


def validar_y_exportar(mb: Metabase, dash_id: int, cards: list) -> bool:
    """Ejecuta cada tarjeta dentro de Metabase y guarda la definicion del tablero."""
    DIR_EVIDENCIA.mkdir(parents=True, exist_ok=True)
    ok = True
    for c in cards:
        inicio = time.perf_counter()
        r = mb.req("POST", f"/card/{c['id']}/query", json={})
        c["estado"] = r.get("status")
        c["filas"] = r.get("row_count")
        c["segundos"] = round(time.perf_counter() - inicio, 2)
        if c["estado"] != "completed":
            ok = False
            c["error"] = r.get("error")
        print(f"  {c['titulo']:34} {c['estado']:10} filas={c['filas']} {c['segundos']} s")
    definicion = mb.req("GET", f"/dashboard/{dash_id}")
    posicion = {dc["card_id"]: dc for dc in definicion["dashcards"] if dc.get("card_id")}
    resumen = {
        "tablero": definicion["name"], "id": dash_id,
        "url": f"http://localhost:3000/dashboard/{dash_id}",
        "tarjetas": [{
            "titulo": c["titulo"], "id": c["id"], "consulta": c["nombre"],
            "fila": posicion[c["id"]]["row"], "columna": posicion[c["id"]]["col"],
            "ancho": c["ancho"], "alto": c["alto"],
            "estado_en_metabase": c["estado"], "filas_resultado": c["filas"],
            "segundos": c["segundos"],
        } for c in cards],
    }
    (DIR_EVIDENCIA / "tablero.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sql", nargs="+", default=SQL_POR_DEFECTO)
    args = parser.parse_args()

    if not (RAIZ_PROYECTO / "data" / "processed" / "taxi.duckdb").exists():
        print("Falta data/processed/taxi.duckdb: ejecute antes scripts/build_database.py")
        return 1
    mb = Metabase(MB_URL)
    mb.esperar()
    configurar_inicial(mb)
    iniciar_sesion(mb)
    db_id = base_de_datos(mb)
    col_id = coleccion(mb)
    cards = tarjetas(mb, db_id, col_id, args.sql)
    dash_id = tablero(mb, col_id, cards)
    ok = validar_y_exportar(mb, dash_id, cards)
    print(f"\nTablero listo: http://localhost:3000/dashboard/{dash_id}")
    print(f"Usuario: {MB_EMAIL}  Contrasena: {MB_PASSWORD}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
