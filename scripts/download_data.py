#!/usr/bin/env python3
"""Descarga los archivos Parquet del NYC TLC Trip Record Data.

Descarga los registros de viajes de taxis amarillos (yellow) y verdes (green)
para los anios configurados en ANIOS (o los indicados con --anio).

Fuente oficial de los datos:
    https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Uso:
    python scripts/download_data.py                       # todos los anios de ANIOS
    python scripts/download_data.py --anio 2026           # solo un anio
    python scripts/download_data.py --taxi yellow --anio 2024 2026

Los archivos se guardan en:
    data/raw/<tipo>/<anio>/<nombre-original>.parquet

Comportamiento:
  - La TLC publica cada mes con varias semanas de atraso, por lo que no todos
    los meses del anio en curso existen todavia. El script consulta al servidor
    que meses estan publicados en lugar de suponerlos.
  - Un archivo que ya existe localmente y es un Parquet valido no se vuelve a
    descargar (no se hace ninguna peticion de red por el).
  - Un archivo local corrupto (sin la firma PAR1 de Parquet) se descarga de nuevo.
  - La descarga se hace sobre un nombre temporal y solo se renombra al
    terminar, de modo que una interrupcion no deja archivos .parquet a medias.
  - El tamanio descargado se compara con el Content-Length informado por el
    servidor.
  - Un error de red al consultar si un mes esta publicado se reporta como
    fallo, no como "no publicado".

Cambios respecto al script original del docente: ver docs/02_descarga.md
"""

import argparse
import sys
from pathlib import Path

import requests

# Anios que forman parte del laboratorio. Para incorporar un anio nuevo basta
# con agregarlo aqui (o pasarlo con --anio); el resto del flujo no cambia.
ANIOS = (2024, 2025, 2026)
TIPOS_TAXI = ("yellow", "green")
URL_BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# Archivos de referencia (no dependen del anio). La tabla de zonas permite
# traducir PULocationID/DOLocationID a borough y nombre de zona.
AUXILIARES = {
    "taxi_zone_lookup.csv": "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",
}

# La ruta se resuelve respecto a la raiz del proyecto y no respecto al
# directorio desde el que se ejecuta el script.
RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
DIR_DESTINO = RAIZ_PROYECTO / "data" / "raw"

TIEMPO_ESPERA = 60          # segundos por peticion
INTENTOS = 3                # intentos por archivo antes de darse por vencido
BLOQUE = 1024 * 1024        # 1 MiB por bloque de descarga
SUFIJO_TEMPORAL = ".part"
FIRMA_PARQUET = b"PAR1"     # bytes iniciales y finales de todo archivo Parquet

# Respuestas con las que el servidor (CloudFront/S3) indica que un archivo no existe.
CODIGOS_NO_PUBLICADO = (403, 404)


def construir_nombre(tipo: str, anio: int, mes: int) -> str:
    """Nombre del archivo publicado por la TLC, p. ej. yellow_tripdata_2026-01.parquet."""
    return f"{tipo}_tripdata_{anio}-{mes:02d}.parquet"


def construir_url(tipo: str, anio: int, mes: int) -> str:
    """URL completa del archivo Parquet mensual."""
    return f"{URL_BASE}/{construir_nombre(tipo, anio, mes)}"


def ruta_destino(tipo: str, anio: int, mes: int) -> Path:
    """Ruta local donde se guarda el archivo."""
    return DIR_DESTINO / tipo / str(anio) / construir_nombre(tipo, anio, mes)


def es_parquet_valido(ruta: Path) -> bool:
    """Comprueba que el archivo empiece y termine con la firma PAR1."""
    try:
        if ruta.stat().st_size < 2 * len(FIRMA_PARQUET):
            return False
        with ruta.open("rb") as archivo:
            inicio = archivo.read(len(FIRMA_PARQUET))
            archivo.seek(-len(FIRMA_PARQUET), 2)
            fin = archivo.read(len(FIRMA_PARQUET))
    except OSError:
        return False
    return inicio == FIRMA_PARQUET and fin == FIRMA_PARQUET


def consultar_publicacion(url: str):
    """Consulta al servidor si el archivo existe (sin descargarlo).

    Devuelve una tupla (estado, detalle). estado es "publicado",
    "no_publicado" o "error"; detalle es el Content-Length cuando el archivo
    esta publicado y el motivo cuando hubo un error.
    """
    try:
        respuesta = requests.head(url, timeout=TIEMPO_ESPERA, allow_redirects=True)
    except requests.RequestException as error:
        return "error", str(error)
    if respuesta.ok:
        tamanio = respuesta.headers.get("Content-Length")
        return "publicado", int(tamanio) if tamanio else None
    if respuesta.status_code in CODIGOS_NO_PUBLICADO:
        return "no_publicado", None
    return "error", f"HTTP {respuesta.status_code}"


def formato_tamanio(n: float) -> str:
    for unidad in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unidad == "GiB":
            return f"{n:.1f} {unidad}"
        n /= 1024
    return f"{n:.1f} GiB"


def descargar_archivo(url: str, destino: Path, esperado=None, parquet=True) -> int:
    """Descarga `url` en `destino`. Devuelve la cantidad de bytes escritos."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + SUFIJO_TEMPORAL)

    ultimo_error = None
    for intento in range(1, INTENTOS + 1):
        try:
            with requests.get(url, stream=True, timeout=TIEMPO_ESPERA) as respuesta:
                respuesta.raise_for_status()
                escritos = 0
                with temporal.open("wb") as archivo:
                    for bloque in respuesta.iter_content(chunk_size=BLOQUE):
                        if bloque:
                            archivo.write(bloque)
                            escritos += len(bloque)
            if escritos == 0:
                raise requests.RequestException("el servidor devolvio un archivo vacio")
            if esperado is not None and escritos != esperado:
                raise requests.RequestException(
                    f"descarga incompleta: {escritos} de {esperado} bytes"
                )
            if parquet and not es_parquet_valido(temporal):
                raise requests.RequestException("el archivo descargado no es un Parquet valido")
            temporal.replace(destino)
            return escritos
        except requests.RequestException as error:
            ultimo_error = error
            temporal.unlink(missing_ok=True)
            if intento < INTENTOS:
                print(f"      intento {intento}/{INTENTOS} fallido ({error}); reintentando")

    raise requests.RequestException(f"no se pudo descargar {url}: {ultimo_error}")


def descargar(tipo: str, anio: int) -> dict:
    """Descarga todos los meses publicados de un tipo de taxi para un anio."""
    print(f"\n=== {tipo.upper()} {anio} ===")
    resumen = {"descargados": 0, "omitidos": 0, "no_publicados": [], "fallidos": []}

    for mes in range(1, 13):
        etiqueta = f"{anio}-{mes:02d}"
        destino = ruta_destino(tipo, anio, mes)

        if destino.exists():
            if es_parquet_valido(destino):
                print(f"  {etiqueta}  ya existe, se omite")
                resumen["omitidos"] += 1
                continue
            print(f"  {etiqueta}  existe pero esta corrupto; se descargara de nuevo")
            destino.unlink()

        url = construir_url(tipo, anio, mes)
        estado, detalle = consultar_publicacion(url)
        if estado == "no_publicado":
            print(f"  {etiqueta}  aun no publicado por la TLC")
            resumen["no_publicados"].append(etiqueta)
            continue
        if estado == "error":
            print(f"  {etiqueta}  ERROR al consultar el servidor: {detalle}")
            resumen["fallidos"].append(etiqueta)
            continue

        print(f"  {etiqueta}  descargando...")
        try:
            escritos = descargar_archivo(url, destino, esperado=detalle)
        except requests.RequestException as error:
            print(f"  {etiqueta}  ERROR: {error}")
            resumen["fallidos"].append(etiqueta)
        else:
            print(f"  {etiqueta}  listo ({formato_tamanio(escritos)}) -> {destino}")
            resumen["descargados"] += 1

    return resumen


def descargar_auxiliares() -> dict:
    """Descarga los archivos de referencia en data/raw/misc/ si no existen."""
    print("\n=== AUXILIARES ===")
    resumen = {"descargados": 0, "omitidos": 0, "no_publicados": [], "fallidos": []}
    for nombre, url in AUXILIARES.items():
        destino = DIR_DESTINO / "misc" / nombre
        if destino.exists() and destino.stat().st_size > 0:
            print(f"  {nombre}  ya existe, se omite")
            resumen["omitidos"] += 1
            continue
        estado, detalle = consultar_publicacion(url)
        if estado != "publicado":
            print(f"  {nombre}  ERROR: {estado} {detalle or ''}")
            resumen["fallidos"].append(nombre)
            continue
        try:
            escritos = descargar_archivo(url, destino, esperado=detalle, parquet=False)
        except requests.RequestException as error:
            print(f"  {nombre}  ERROR: {error}")
            resumen["fallidos"].append(nombre)
        else:
            print(f"  {nombre}  listo ({formato_tamanio(escritos)}) -> {destino}")
            resumen["descargados"] += 1
    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga los datos de taxis amarillos y verdes del NYC TLC."
    )
    parser.add_argument(
        "--taxi", choices=(*TIPOS_TAXI, "all"), default="all",
        help="tipo de taxi a descargar (por defecto: all)",
    )
    parser.add_argument(
        "--anio", type=int, nargs="+", default=list(ANIOS),
        help=f"anio(s) a descargar (por defecto: {' '.join(map(str, ANIOS))})",
    )
    argumentos = parser.parse_args()

    tipos = TIPOS_TAXI if argumentos.taxi == "all" else (argumentos.taxi,)
    anios = sorted(set(argumentos.anio))

    total = descargar_auxiliares()
    for anio in anios:
        for tipo in tipos:
            resumen = descargar(tipo, anio)
            total["descargados"] += resumen["descargados"]
            total["omitidos"] += resumen["omitidos"]
            total["no_publicados"] += [f"{tipo} {m}" for m in resumen["no_publicados"]]
            total["fallidos"] += [f"{tipo} {m}" for m in resumen["fallidos"]]

    print("\n" + "=" * 60)
    print(f"RESUMEN  (anios: {', '.join(map(str, anios))}; taxis: {', '.join(tipos)})")
    print("=" * 60)
    print(f"  descargados   : {total['descargados']}")
    print(f"  ya existian   : {total['omitidos']}")
    print(f"  no publicados : {len(total['no_publicados'])}")
    if total["no_publicados"]:
        print(f"      {', '.join(total['no_publicados'])}")
    print(f"  fallidos      : {len(total['fallidos'])}")
    if total["fallidos"]:
        print(f"      {', '.join(total['fallidos'])}")
    print("=" * 60)

    return 1 if total["fallidos"] else 0


if __name__ == "__main__":
    sys.exit(main())
