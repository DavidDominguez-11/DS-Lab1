# Evidencia del tablero (Metabase)

Tablero **"Taxis NYC - Indicadores"** (coleccion "Lab 8 - DuckDB") en <http://localhost:3000>,
generado por `scripts/setup_metabase.py` sobre `data/processed/taxi.duckdb` con los datos de
2024, 2025 y enero-agosto 2026 (121 M de registros, 114.5 M viajes validos).

| Captura | Contenido |
|---|---|
| [tablero_parte1.jpg](tablero_parte1.jpg) | Texto de contexto, KPI K1-K4, I1 viajes por dia, I2 ingreso mensual |
| [tablero_parte2.jpg](tablero_parte2.jpg) | I3 precio del viaje, I4 metodo de pago, I5 propina, I6 velocidad por hora |
| [tablero_parte3.jpg](tablero_parte3.jpg) | I7 demanda por hora, I8 top zonas, I9 aeropuertos, I10 cargo CBD |
| [tablero_parte4.jpg](tablero_parte4.jpg) | I11 registros invalidos, I12 origen de la solicitud, E1 resumen anual, E2-E3 |
| [tablero_parte5.jpg](tablero_parte5.jpg) | E2 variacion interanual, E3 cuota green, E4-E5 velocidad, E6-E7 |
| [tablero_parte6.jpg](tablero_parte6.jpg) | E6 composicion del pago, E7 sin dato de pago por proveedor, E8 aeropuertos |

[`tablero.json`](tablero.json): definicion exportada del tablero (id, posicion y tamano de cada
tarjeta, consulta de origen) y el resultado de ejecutar cada tarjeta dentro de Metabase
(`completed`, filas devueltas y segundos).
