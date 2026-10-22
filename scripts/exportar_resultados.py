"""Exporta predicciones y metricas de los modelos del Laboratorio 1 para el tablero.

Reutiliza la misma logica del notebook (series mensuales Turista+Excursionista / via / tipo,
corte 2021-04-01, log1p para SARIMA, Holt-Winters, seasonal naive y Prophet). No define modelos nuevos.
Salida: data/predicciones.csv y data/metricas.csv
"""
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)

RAIZ = Path(__file__).resolve().parents[1]
CORTE = "2021-04-01"
M = 12

df = pd.read_csv(RAIZ / "Base_Migracion_2009-2026jun.csv", sep=";", encoding="utf-8-sig")
col_via = [c for c in df.columns if c.startswith("V") and c.endswith("a")][0]
df["fecha"] = pd.to_datetime(dict(year=df[[c for c in df.columns if c.startswith("A") and len(c) == 3][0]],
                                  month=df["Mes cod"], day=1))
rango = pd.date_range(df["fecha"].min(), df["fecha"].max(), freq="MS")

series = {"Total (Turista + Excursionista)": df["Tipo de Viajero"].isin(["Turista", "Excursionista"])}
for v in df[col_via].unique():
    series[f"Vía {v}"] = df[col_via] == v
for t in df["Tipo de Viajero"].unique():
    series[f"Tipo {t}"] = df["Tipo de Viajero"] == t


def construir(mask):
    return df[mask].groupby("fecha")["Viajero"].sum().reindex(rango, fill_value=0).astype(float)


def seasonal_naive(train, h):
    return np.tile(train.iloc[-M:].values, int(np.ceil(h / M)))[:h]


def sarima_log(train, h):
    """Mejor (menor AIC) entre los candidatos manuales del Lab 1; auto_arima no se re-ejecuta aqui."""
    y = np.log1p(train)
    mejor = None
    for order, sorder in [((1, 1, 1), (1, 1, 1, M)), ((0, 1, 1), (0, 1, 1, M))]:
        try:
            aj = SARIMAX(y, order=order, seasonal_order=sorder).fit(disp=False)
        except Exception:
            continue
        if mejor is None or aj.aic < mejor.aic:
            mejor = aj
    return np.expm1(mejor.get_forecast(h).predicted_mean.values)


def holt_winters(train, h):
    try:
        mod = ExponentialSmoothing(train, trend="add", seasonal="mul", seasonal_periods=M).fit()
    except ValueError:
        mod = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=M).fit()
    return mod.forecast(h).values


def prophet(train, h):
    pdf = train.reset_index()
    pdf.columns = ["ds", "y"]
    mod = Prophet(seasonality_mode="multiplicative", yearly_seasonality=True).fit(pdf)
    return mod.predict(mod.make_future_dataframe(h, freq="MS"))["yhat"].iloc[-h:].values


MODELOS = {"SARIMA": sarima_log, "Holt-Winters": holt_winters, "Prophet": prophet,
           "Seasonal naive": lambda tr, h: seasonal_naive(tr, h)}

filas, metricas = [], []
for nombre, mask in series.items():
    s = construir(mask)
    train, test = s[s.index < CORTE], s[s.index >= CORTE]
    h = len(test)
    for modelo, f in MODELOS.items():
        pred = np.clip(np.asarray(f(train, h), dtype=float), 0, None)
        err = test.values - pred
        metricas.append({"serie": nombre, "modelo": modelo, "MAE": np.abs(err).mean(),
                         "RMSE": np.sqrt((err ** 2).mean()), "sesgo": err.mean() * -1})
        filas.append(pd.DataFrame({"serie": nombre, "modelo": modelo, "fecha": test.index,
                                   "real": test.values, "prediccion": pred}))
    print("ok", nombre)

(RAIZ / "data").mkdir(exist_ok=True)
pd.concat(filas).round(1).to_csv(RAIZ / "data" / "predicciones.csv", index=False)
pd.DataFrame(metricas).round(1).to_csv(RAIZ / "data" / "metricas.csv", index=False)
