# DS-Lab10

## Laboratorio 10 – Observatorio de Turismo (tablero)

```
pip install -r requirements_tablero.txt
streamlit run tablero/app.py
```

- `tablero/app.py`: tablero Streamlit + Plotly (3 páginas, 10 visualizaciones, 2 pares enlazados).
- `data/`: predicciones y métricas de los modelos del Lab 1 (`scripts/exportar_resultados.py`) y del Lab 2 (`scripts/exportar_lstm.py`, ejecuta el notebook de la rama `lab2`).
- `docs/Documento_de_Diseno.docx`: documento de diseño (se regenera con `scripts/generar_documento.py`; exportar a PDF desde Word).
