"""Lab 9 - calculo de todas las cifras de la infografia (mismas definiciones que Lab1_Series_de_Tiempo.ipynb)."""
import warnings, logging, pickle
import numpy as np, pandas as pd
warnings.filterwarnings('ignore'); logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet

df = pd.read_csv('Base_Migracion_2009-2026jun.csv', sep=';', encoding='utf-8-sig')
df['fecha'] = pd.to_datetime(df['Año'].astype(str) + '-' + df['Mes cod'].astype(str) + '-01')
TE = ['Turista', 'Excursionista']
corte = '2021-04-01'
tr, te = df[df.fecha < corte], df[df.fecha >= corte]
rtr = pd.date_range(tr.fecha.min(), tr.fecha.max(), freq='MS')
rte = pd.date_range(te.fecha.min(), te.fecha.max(), freq='MS')

def serie(d, filtro, rango):
    s = d[filtro(d)].groupby('fecha')['Viajero'].sum().reindex(rango, fill_value=0)
    s.index.freq = 'MS'; return s

def metricas(r, p):
    r, p = np.asarray(r), np.asarray(p)
    return np.mean(np.abs(r-p)), np.sqrt(np.mean((r-p)**2))

def sn(train, h, m=12): return np.tile(train.iloc[-m:].values, int(np.ceil(h/m)))[:h]

def metricas_comp(s, nombre):
    sl = np.log1p(s); dec = seasonal_decompose(sl, model='additive', period=12)
    res = dec.resid.dropna(); seas = dec.seasonal.loc[res.index]
    fe = max(0, 1 - np.var(res)/np.var(seas+res))
    pre = sl.loc['2009-01-01':'2019-12-01']; sl_ = np.polyfit(np.arange(len(pre)), pre.values, 1)[0]
    m19 = s.loc['2019-01-01':'2019-12-01'].mean(); m20 = s.loc['2020-01-01':'2020-12-01'].mean()
    return {'Serie': nombre, 'Estacionalidad': round(fe,3), 'Crecimiento': round((np.exp(sl_*12)-1)*100,2),
            'Volatilidad': round(np.std(res),4), 'Caida': round((m20-m19)/m19*100,1)}

# --- serie total y modelos (12.h - 12.j) ---
s_tr = serie(tr, lambda d: d['Tipo de Viajero'].isin(TE), rtr)
s_te = serie(te, lambda d: d['Tipo de Viajero'].isin(TE), rte)
h = len(s_te)
sar = SARIMAX(np.log1p(s_tr), order=(2,1,0), seasonal_order=(1,1,0,12),
              enforce_stationarity=True, enforce_invertibility=True).fit(disp=False)
p_sar = np.expm1(sar.get_forecast(steps=h).predicted_mean)
hw = ExponentialSmoothing(s_tr, trend='add', seasonal='mul', seasonal_periods=12).fit()
ses = ExponentialSmoothing(s_tr, trend=None, seasonal=None).fit()
pdf = s_tr.reset_index(); pdf.columns = ['ds','y']
pr = Prophet(seasonality_mode='multiplicative', yearly_seasonality=True); pr.fit(pdf)
fc = pr.predict(pr.make_future_dataframe(periods=h, freq='MS')).set_index('ds').iloc[-h:]
preds = {'Prophet': fc['yhat'].values, 'Holt-Winters': hw.forecast(h).values,
         'Suav. exp. simple': ses.forecast(h).values, 'Seasonal naive': sn(s_tr, h),
         'SARIMA(2,1,0)(1,1,0)[12]': p_sar.values}
tabla = pd.DataFrame([{'Modelo': k, **dict(zip(['MAE','RMSE'], np.round(metricas(s_te.values, v),1)))}
                      for k, v in preds.items()]).sort_values('RMSE').reset_index(drop=True)

# --- cuadrante (15.1): 8 series de entrenamiento ---
filas = [metricas_comp(s_tr, 'Total (T+E)')]
for v in ['Aérea','Terrestre','Marítima']:
    filas.append(metricas_comp(serie(tr, lambda d, v=v: d['Vía']==v, rtr), f'Vía {v}'))
for t in ['Turista','Excursionista','Cruceristas','Viajero']:
    filas.append(metricas_comp(serie(tr, lambda d, t=t: d['Tipo de Viajero']==t, rtr), f'Tipo {t}'))
cuad = pd.DataFrame(filas)

# --- cifras directas del CSV ---
tot = df[df['Tipo de Viajero'].isin(TE)].groupby('fecha')['Viajero'].sum()
anual = tot.groupby(tot.index.year).sum()
tot_via = df[df['Tipo de Viajero'].isin(TE)].groupby('Vía')['Viajero'].sum()
tot_pais = df[df['Tipo de Viajero'].isin(TE)].groupby('País')['Viajero'].sum().nlargest(6)
est = tot.loc['2010':'2019']; est = est.groupby(est.index.month).mean(); est = est/est.mean()

out = dict(tabla=tabla, cuad=cuad, tot=tot, anual=anual, via=tot_via, pais=tot_pais, est=est,
           s_te=s_te, fc=fc[['yhat','yhat_lower','yhat_upper']], s_tr=s_tr)
pickle.dump(out, open('lab9_datos.pkl','wb'))
print(tabla.to_string()); print(cuad.to_string()); print(anual.round(0).to_string())
print(tot_via.round(0)); print(tot_pais.round(0)); print(est.round(3).to_string())
cov = ((s_te.values>=fc.yhat_lower.values)&(s_te.values<=fc.yhat_upper.values)).mean(); print('cobertura banda 80%:',cov)
