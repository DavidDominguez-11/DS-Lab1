# Ejercicio 2 — Sistema de descarga

## 2.1 Análisis del script original

El script `scripts/download_data.py` entregado por el docente ya sabía descargar un mes
y omitir archivos existentes, pero tenía las siguientes limitaciones:

| # | Parte del script original | Problema |
|---|---|---|
| 1 | `ANIO = 2026` usado dentro de `construir_nombre`, `construir_url`, `ruta_destino`, `descargar` y los mensajes | El año está fijo en todo el código. Incorporar 2024 o 2025 obligaría a duplicar o reescribir funciones. |
| 2 | `esta_publicado()` devuelve `False` ante **cualquier** excepción de red | Una caída de red se reporta como "aún no publicado por la TLC", así que el resumen podría decir 0 fallidos con un dataset incompleto. |
| 3 | El servidor responde **403** (no 404) para meses no publicados | Funcionaba por accidente (`respuesta.ok` es falso), pero no distinguía 403/404 de un error 5xx. |
| 4 | `descargar_archivo()` solo valida que se escribieron más de 0 bytes | Una conexión cortada a la mitad que termine sin excepción dejaría un Parquet truncado. |
| 5 | "Ya existe" = `st_size > 0` | Un archivo corrupto o truncado se considera válido para siempre y nunca se repara. |
| 6 | `DIR_DESTINO = Path("data/raw")` | Relativo al directorio de trabajo: ejecutarlo desde `scripts/` o desde un notebook crea `scripts/data/raw/...`. |
| 7 | Sin forma de verificar el resultado | No había manera de demostrar que lo descargado coincide con lo publicado. |

## 2.2–2.4 y 2.6 Cambios realizados

| Cambio | Motivo |
|---|---|
| `ANIO` → tupla `ANIOS = (2026,)` y argumento `--anio` (acepta varios) | Año como parámetro de todas las funciones (`construir_nombre(tipo, anio, mes)`, etc.). Agregar un año = agregar un número. |
| `esta_publicado()` → `consultar_publicacion()` que devuelve `("publicado", content_length)`, `("no_publicado", None)` para 403/404 o `("error", motivo)` | Los errores de red cuentan como **fallidos** (código de salida 1), no como "no publicados". |
| Se compara el tamaño descargado con el `Content-Length` del servidor | Detecta descargas incompletas; se reintenta hasta 3 veces. |
| Validación de la firma `PAR1` al inicio y al final del archivo (`es_parquet_valido`) | Detecta archivos truncados/corruptos, tanto recién descargados como ya existentes. |
| Si un archivo local existe pero es inválido, se borra y se vuelve a descargar | Auto-reparación sin intervención manual. |
| `DIR_DESTINO` se calcula desde `Path(__file__)` | El script funciona igual sin importar desde dónde se ejecute. |
| Nuevo `scripts/verify_data.py` | Verificación independiente de completitud que genera `docs/inventario_datos.md`. |

Lo que **se conservó** del original: escritura a un archivo `.part` con renombrado atómico,
reintentos, consulta al servidor de qué meses existen (en lugar de suponerlos) y omisión
de archivos existentes **sin hacer peticiones de red** por ellos.

## 2.5 Ejecución

```bash
docker compose exec lab python scripts/download_data.py
```

Evidencia en `docs/evidencia/`:

- `descarga_2026_primera_ejecucion.log`: 16 descargados, 8 no publicados (sep–dic 2026), 0 fallidos.
- `descarga_2026_segunda_ejecucion.log`: 0 descargados, **16 ya existían** → no se re-descarga nada.
- `descarga_2026_archivo_corrupto.log`: se truncó a mano `green_tripdata_2026-03.parquet`
  a 1000 bytes; el script lo detectó ("existe pero está corrupto"), lo volvió a descargar
  y omitió los otros 7 meses.

## 2.7 ¿Cómo se determinó que la descarga está completa?

Con `scripts/verify_data.py`, que cruza **tres fuentes independientes** para cada
tipo × año × mes:

1. **Servidor TLC**: petición `HEAD` → ¿está publicado? ¿cuál es su `Content-Length`?
2. **Disco local**: ¿existe el archivo? ¿cuántos bytes pesa?
3. **DuckDB**: `parquet_file_metadata()` → ¿se puede leer el pie del Parquet? ¿cuántas filas declara?

Un mes es **ok** solo si está publicado, existe, el tamaño coincide byte a byte con el
servidor y DuckDB lo lee. Si la TLC responde 403 y no hay archivo local, el mes es
"no publicado" (esperado para sep–dic 2026). Cualquier otro caso es un problema.

Resultado (ver `docs/inventario_datos.md`):

| Taxi | Año | Meses publicados | Meses locales OK | Filas |
|---|---|---:|---:|---:|
| yellow | 2026 | 8 | 8 | 29,703,355 |
| green | 2026 | 8 | 8 | 337,114 |

**Estado: COMPLETO** — 16 de 16 archivos publicados (enero–agosto 2026) presentes e íntegros.

Como la TLC sigue publicando meses, "completo" significa *completo respecto a lo publicado
en la fecha de verificación* (2026-10-05). Basta volver a ejecutar ambos scripts para
incorporar septiembre cuando aparezca.
