#!/usr/bin/env bash
# Regenera todos los resultados principales del laboratorio desde cero.
#
# Se ejecuta en la COMPUTADORA (no dentro del contenedor), desde la raiz del
# repositorio, con Docker en ejecucion:
#
#     bash scripts/run_all.sh               # todo excepto el benchmark
#     bash scripts/run_all.sh --benchmark   # incluye el benchmark (~15 min mas)
#
# Funciona en Linux, macOS y Git Bash en Windows.
set -euo pipefail
export MSYS_NO_PATHCONV=1          # Git Bash: no convertir rutas /workspace/...
cd "$(dirname "$0")/.."

run() { echo; echo ">>> $*"; docker compose exec -T lab "$@"; }

echo ">>> Levantando el ambiente"
docker compose up -d --build

# 1. Datos (Ej. 2, 5, 8)
run python scripts/download_data.py
run python scripts/verify_data.py

# 2. Exploracion y EDA directo sobre Parquet (Ej. 3, 4, 5, 8)
run python scripts/sqlrun.py sql/03_exploracion.sql --md docs/resultados/03_exploracion.md
run python scripts/sqlrun.py sql/04_eda.sql --md docs/resultados/04_eda_3anios.md
run python scripts/sqlrun.py sql/05_validacion_incorporacion.sql --md docs/resultados/05_validacion_2025.md

# 3. Base materializada (Ej. 6). Metabase se detiene mientras se reemplaza el
#    archivo: en discos de Windows montados no se puede reemplazar un archivo abierto.
docker compose stop metabase
run python scripts/build_database.py
docker compose start metabase

# 4. Indicadores y evolucion sobre la base (Ej. 7, 8) + tablero de Metabase
run python scripts/sqlrun.py sql/07_indicadores.sql --db data/processed/taxi.duckdb --md docs/resultados/07_indicadores_3anios.md
run python scripts/sqlrun.py sql/08_evolucion.sql --db data/processed/taxi.duckdb --md docs/resultados/08_evolucion.md
run python scripts/setup_metabase.py --sql sql/07_indicadores.sql sql/08_evolucion.sql

# 5. Benchmark opcional (Ej. 6); Metabase detenido para no competir por CPU/RAM
if [[ "${1:-}" == "--benchmark" ]]; then
    docker compose stop metabase
    run python scripts/benchmark.py
    docker compose start metabase
fi

# 6. Notebooks con sus graficas (docs/figuras/)
for nb in 03_exploracion 04_eda 06_benchmark 08_tres_anios; do
    run jupyter nbconvert --to notebook --execute --inplace "notebooks/${nb}.ipynb"
done

echo
echo "Listo. Tablero: http://localhost:3000  (admin@lab8.local / Lab8-DuckDB-2026)"
