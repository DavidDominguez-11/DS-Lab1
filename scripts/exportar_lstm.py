"""Ejecuta el notebook del Laboratorio 2 (rama lab2) y exporta las predicciones de los LSTM para el tablero.

No define modelos nuevos: ejecuta las celdas del notebook (LSTM con tuneo para Total y Via Terrestre, y el
LSTM global con catch22) y agrega al final una celda que guarda las predicciones sobre el conjunto de prueba.

Uso:  python scripts/exportar_lstm.py ruta/al/Lab2_Deep_Learning_CC3084.ipynb
Salida: data/predicciones_lstm.csv y data/metricas_lstm.csv
Requiere un kernel "dslab10" (python -m ipykernel install --user --name dslab10) con: torch, pycatch22, scikit-learn, scipy, seaborn, nbformat, nbclient, ipykernel
"""
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parents[1]
nb_ruta = Path(sys.argv[1])
ULTIMA_CELDA = 50  # la celda 50 es la ultima que se necesita (LSTM global sobre Total)

CELDA_EXPORT = '''
import pandas as pd, numpy as np
def _nombre(s):
    s = s.replace("Total (obligatoria)", "Total (Turista + Excursionista)")
    return s.replace("Via ", "V\\u00eda ")
filas = []
def _agregar(serie, modelo, pred_serie):
    real = series_test[serie]
    pred = pd.Series(np.asarray(pred_serie, dtype=float), index=real.index).clip(lower=0)
    filas.append(pd.DataFrame({"serie": _nombre(serie), "modelo": modelo, "fecha": real.index,
                               "real": real.values, "prediccion": pred.values}))
for serie, res in [("Total (obligatoria)", resultados_total), ("Via Terrestre", resultados_terrestre)]:
    for arq, r in res.items():
        _agregar(serie, arq, r["pred_test"].values)
for serie in series_train:
    scaled, scaler = preparar_escalador(series_train[serie])
    vec = matriz_z_train.loc[serie].values.astype(np.float32)
    p = pronosticar_recursivo(modelo_final_214, scaled[-LOOKBACK_GLOBAL:], len(series_test[serie]), catch22_vec=vec)
    _agregar(serie, "LSTM global + catch22", desescalar(scaler, p))
out = pd.concat(filas)
out.round(1).to_csv(SALIDA_PRED, index=False)
err = out.assign(e=out.real - out.prediccion)
m = err.groupby(["serie", "modelo"]).e.agg(MAE=lambda x: x.abs().mean(), RMSE=lambda x: np.sqrt((x**2).mean()),
                                           sesgo=lambda x: -x.mean()).reset_index()
m.round(1).to_csv(SALIDA_MET, index=False)
print(m.round(0))
'''

nb = nbformat.read(nb_ruta, as_version=4)
celdas = [c for i, c in enumerate(nb.cells) if c.cell_type == "code" and i <= ULTIMA_CELDA]
# pycatch22 >= 1.0 renombro varias caracteristicas respecto a la version del notebook (0.4.x); se traducen los nombres.
RENOMBRAR = {
    "CO_FirstCrossing_acf_1e_pointOfCrossing": "CO_f1ecac",
    "CO_HistogramAMI_even_5bin_ami2": "CO_HistogramAMI_even_2_5",
    "MD_pNN_pnn40": "MD_hrv_classic_pnn40",
    "SB_TransitionMatrix_quantile_3_ac_sumdiagcov": "SB_TransitionMatrix_3ac_sumdiagcov",
    "FC_LocalSimple_mean1_taurat": "FC_LocalSimple_mean1_tauresrat",
    "SP_Summaries_fft_area_5_1": "SP_Summaries_welch_rect_area_5_1",
    "SP_Summaries_fft_wq_50": "SP_Summaries_welch_rect_centroid",
    "FC_LocalSimple_mean3_stde": "FC_LocalSimple_mean3_stderr",
}
for c in celdas:
    if "dict(zip(resultado['names']" in c.source:
        c.source = c.source.replace("dict(zip(resultado['names']",
                                    f"dict(zip([{RENOMBRAR!r}.get(n, n) for n in resultado['names']]")
destino = RAIZ / "data"
pre = (f'SALIDA_PRED = r"{destino / "predicciones_lstm.csv"}"\n'
       f'SALIDA_MET = r"{destino / "metricas_lstm.csv"}"\n')
nb.cells = celdas + [nbformat.v4.new_code_cell(pre + CELDA_EXPORT)]

with tempfile.TemporaryDirectory() as tmp:
    for f in ("train_raw.csv", "test_raw.csv"):
        shutil.copy(RAIZ / f, tmp)
    NotebookClient(nb, timeout=3000, kernel_name="dslab10", resources={"metadata": {"path": tmp}}).execute()
print("exportado en", destino)
