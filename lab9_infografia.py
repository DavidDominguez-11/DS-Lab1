"""Lab 9 - Infografia. Requiere haber corrido lab9_datos.py (genera lab9_datos.pkl).
Salidas: Lab9_Infografia.png (2200x3400 px) y Lab9_Infografia.pdf (11x17 in, 1 pagina)."""
import pickle
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle

D = pickle.load(open('lab9_datos.pkl', 'rb'))
NAVY, TEAL, ACC, GRAY, INK, BG, LIGHT = '#1F3A5F', '#2A9D8F', '#C2410C', '#5B6470', '#1B2430', '#FAFAF7', '#E3E6EA'
names = {f.name for f in fm.fontManager.ttflist}
plt.rcParams['font.family'] = next((f for f in ['Segoe UI', 'Calibri', 'DejaVu Sans'] if f in names), 'DejaVu Sans')
TEAL_TXT, RMSE_TXT = '#1F7A70', '#5F7594'   # versiones oscuras para texto pequeno (contraste >= 4.5:1)
W, H, M = 11.0, 17.0, 0.55
fig = plt.figure(figsize=(W, H), facecolor=BG)


def SH(y):
    return y - 0.2 if 6.0 <= y < 16.5 else y


def ax_in(x, y, w, h):
    """Ejes en pulgadas, medidos desde la esquina superior izquierda."""
    return fig.add_axes([x / W, 1 - (SH(y) + h) / H, w / W, h / H])


def txt(x, y, s, **kw):
    kw.setdefault('color', INK)
    kw.setdefault('va', 'top')
    return fig.text(x / W, 1 - SH(y) / H, s, **kw)


def rect(x, y, w, h, **kw):
    fig.add_artist(Rectangle((x / W, 1 - (y + h) / H), w / W, h / H, **kw))


def clean(ax, left=True):
    for s in ['top', 'right'] + ([] if left else ['left']):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_color(GRAY)
    ax.spines['bottom'].set_color(GRAY)
    ax.tick_params(colors=GRAY, labelsize=8.5)
    ax.set_facecolor(BG)


def titulo(y, s, sub=None):
    txt(M, y, s, fontsize=14.5, fontweight='bold', color=NAVY)
    if sub:
        txt(M, y + 0.30, sub, fontsize=9, color=GRAY)


an, tot, tabla, cuad = D['anual'], D['tot'], D['tabla'], D['cuad']
v09, v19, v20, v25 = an[2009], an[2019], an[2020], an[2025]
via = D['via']

# ============ BLOQUE 1: titular + KPIs ============
rect(0, 0, W, 3.2, fc=NAVY, ec='none')
txt(M, 0.30, 'Guatemala 2009–2026: crecimos 120%,\nel COVID nos borró 74% en un año\ny aún no recuperamos el nivel de 2019',
    fontsize=25, fontweight='bold', color='white', linespacing=1.12)
txt(M, 1.55, 'Radiografía de 17 años de flujo migratorio: qué nos enseñó la crisis y qué anticipar para el turismo.',
    fontsize=11, color='#DCE3EC')
kp = [(f'{v19 / 1e6:.2f} M', 'viajeros en 2019,\nel máximo histórico', NAVY),
      (f'+{(v19 / v09 - 1) * 100:.0f}%', f'crecimiento 2009→2019\n({v09 / 1e6:.2f} M → {v19 / 1e6:.2f} M)', NAVY),
      (f'{(v20 / v19 - 1) * 100:.0f}%', f'caída de 2020 vs 2019\n({v20 / 1e6:.2f} M viajeros)', ACC),
      (f'{v25 / v19 * 100:.0f}%', f'nivel de 2025 vs 2019\n({v25 / 1e6:.2f} M viajeros)', ACC)]
gap = 0.2
cw = (W - 2 * M - 3 * gap) / 4
for i, (big, lab, c) in enumerate(kp):
    x = M + i * (cw + gap)
    rect(x, 2.0, cw, 1.0, fc='white', ec='none')
    rect(x, 2.0, 0.07, 1.0, fc=c, ec='none')
    txt(x + 0.22, 2.04, big, fontsize=30, fontweight='bold', color=c)
    txt(x + 0.22, 2.66, lab, fontsize=8.5, color=GRAY, linespacing=1.2)
txt(M, 3.06, 'Viajeros = Turista + Excursionista (serie consistente en todo el periodo). 2025 es el último año completo.', fontsize=7.5, color='#B8C4D4')

# ============ BLOQUE 2: panorama ============
titulo(3.42, '1 · Dos décadas en una línea: crecer, caer, volver a empezar', 'Viajeros por mes, 2009 – junio 2026 · eje vertical desde cero')
ax = ax_in(M, 3.95, W - 2 * M, 1.9)
clean(ax)
ax.plot(tot.index, tot.values / 1e3, color=NAVY, lw=1.5)
ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-03-31'), color=ACC, alpha=.10, lw=0)
ax.axvline(pd.Timestamp('2021-04-01'), color=GRAY, lw=1, ls=':')
ax.set_ylim(0, 540)
ax.set_xlim(tot.index.min(), tot.index.max())
ax.set_ylabel('Miles de viajeros / mes', color=GRAY, fontsize=8.5)
ax.grid(axis='y', color=LIGHT, lw=.8)
ax.set_axisbelow(True)
ann = dict(fontsize=8.5, color=INK, arrowprops=dict(arrowstyle='-', color=GRAY, lw=.8))
pico = tot.idxmax()
ax.annotate(f'Pico histórico, dic-2019:\n{tot.max() / 1e3:,.0f} mil viajeros', (pico, tot.max() / 1e3), (pd.Timestamp('2014-06-01'), 440), ha='center', **ann)
mn = tot.loc['2020-01-01':'2021-12-01'].idxmin()
ax.annotate(f'Cierre de fronteras (mar-2020).\nMínimo may-2020: {tot[mn]:,.0f}', (mn, tot[mn] / 1e3), (pd.Timestamp('2016-10-01'), 120), ha='center', **ann)
ax.annotate('Reapertura 2022: 3.23 M\nen el año, casi 3× el de 2021', (pd.Timestamp('2022-04-01'), tot['2022-04-01'] / 1e3), (pd.Timestamp('2023-06-01'), 60), ha='center', **ann)
ax.text(pd.Timestamp('2021-05-01'), 535, 'Inicio del periodo de prueba (abr-2021)', fontsize=7.5, color=GRAY, va='top')
ax.text(pd.Timestamp('2026-06-01'), 400, 'Ene–jun 2026:\n1.58 M, −3% vs\nene–jun 2025', fontsize=8, color=ACC, ha='right', fontweight='bold')
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# ============ BLOQUE 3: estacionalidad, vias y mercados ============
titulo(6.3, '2 · Cuándo y por dónde llegan', 'Los picos coinciden con vacaciones y pagos laborales; la tierra pesa más que el aire')
txt(M, 6.95, 'Estacionalidad mensual (promedio 2010–2019)', fontsize=9.5, fontweight='bold')
ax = ax_in(M + 0.5, 7.25, 4.4, 1.45)
clean(ax)
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
e = D['est'].values
ax.bar(range(12), e, color=[ACC if i == 11 else (TEAL if e[i] > 1.04 else '#B9C3CF') for i in range(12)], width=.72)
ax.axhline(1, color=INK, lw=1)
ax.set_xticks(range(12))
ax.set_xticklabels(meses)
ax.set_ylim(0, 1.75)
ax.set_yticks([0, .5, 1, 1.5])
ax.set_ylabel('Índice (1.0 = media)', fontsize=8, color=GRAY)
for i in [1, 2, 3, 6, 8, 11]:
    ax.text(i, e[i] + .03, f'{e[i]:.2f}', ha='center', fontsize=8, fontweight='bold' if i == 11 else 'normal', color=ACC if i == 11 else INK)
ax.text(10.2, 1.5, 'Dic: +33%\n(aguinaldo)', ha='center', va='bottom', fontsize=7.5, color=ACC, fontweight='bold', linespacing=1.1)
ax.text(2.5, 1.3, 'Semana Santa', ha='center', fontsize=7.5, color=TEAL_TXT, fontweight='bold')
ax.text(5.6, 1.45, 'Jul: vacaciones\ny Bono 14', ha='center', fontsize=7.5, color=TEAL_TXT, fontweight='bold', linespacing=1.1)
ax.text(1, .08, 'valle', ha='center', fontsize=7.5, color=GRAY)
ax.text(8, .08, 'valle', ha='center', fontsize=7.5, color=GRAY)

xr = M + 5.25
wr = W - M - xr
txt(xr, 6.95, 'Vía de ingreso (millones de viajeros, 2009–2026)', fontsize=9.5, fontweight='bold')
ax = ax_in(xr + 0.85, 7.25, wr - 1.6, 0.8)
clean(ax, left=False)
vv = (via.reindex(['Terrestre', 'Aérea', 'Marítima']) / 1e6)
ax.barh(range(3), vv.values, color=[NAVY, NAVY, '#9AA7B6'], height=.62)
ax.invert_yaxis()
ax.set_yticks(range(3))
ax.set_yticklabels(vv.index, fontsize=9, color=INK)
ax.set_xlim(0, 36)
ax.set_xticks([])
ax.spines['bottom'].set_visible(False)
for i, v in enumerate(vv.values):
    ax.text(v + .5, i, f'{v:.1f} M' + ('*' if i == 2 else ''), va='center', fontsize=9, fontweight='bold')
txt(xr, 8.12, 'Principales países de residencia (millones)', fontsize=9.5, fontweight='bold')
ax = ax_in(xr + 1.65, 8.4, wr - 2.4, 0.85)
clean(ax, left=False)
pp = (D['pais'] / 1e6).head(5)
lab = [p.replace('Estados Unidos de América', 'Estados Unidos').replace('Guatemala', 'Guatemala (resid.)') for p in pp.index]
ax.barh(range(5), pp.values, color=TEAL, height=.62)
ax.invert_yaxis()
ax.set_yticks(range(5))
ax.set_yticklabels(lab, fontsize=8.5, color=INK)
ax.set_xlim(0, 19)
ax.set_xticks([])
ax.spines['bottom'].set_visible(False)
for i, v in enumerate(pp.values):
    ax.text(v + .3, i, f'{v:.1f} M', va='center', fontsize=8.5, fontweight='bold')
txt(M, 9.12, '*Vía marítima: los cruceros se registran como "Cruceristas", no como Turista/Excursionista; por eso su cifra es mínima aquí.', fontsize=7.3, color=GRAY)

# --- cuadrante comparativo ---
txt(M, 9.4, 'Cuadrante comparativo: ¿qué serie destaca en cada aspecto?', fontsize=11, fontweight='bold', color=NAVY)
txt(M, 9.66, '8 series del Laboratorio 1 (entrenamiento 2009–mar 2021). Naranja = serie ganadora de la columna.', fontsize=8.5, color=GRAY)
ax = ax_in(M, 9.95, W - 2 * M, 1.75)
ax.axis('off')
ax.set_xlim(0, 1)
ax.set_ylim(0, 9.4)
hdr = ['Serie', '¿Más estacional?\n(fuerza 0–1)', '¿Mayor crecimiento?\n(% anual pre-COVID)', '¿Más volátil?\n(desv. residual, log)', '¿Más golpeada?\n(2020 vs 2019, %)']
xs = [0.0, 0.26, 0.44, 0.63, 0.82]
cws = [0.26, 0.18, 0.19, 0.19, 0.18]
for j, hh in enumerate(hdr):
    ax.text(0.005 if j == 0 else xs[j] + cws[j] / 2, 8.75, hh, ha='left' if j == 0 else 'center', va='center', fontsize=8, fontweight='bold', linespacing=1.1)
keys = [('Estacionalidad', 'max'), ('Crecimiento', 'max'), ('Volatilidad', 'max'), ('Caida', 'min')]
for r, row in cuad.iterrows():
    yy = 7.55 - r
    ax.text(0.005, yy, row['Serie'], va='center', fontsize=8.5)
    for c, (k, mode) in enumerate(keys):
        col = cuad[k]
        win = (col.idxmax() if mode == 'max' else col.idxmin()) == r
        rng = (col - col.min()) / (col.max() - col.min())
        inten = rng[r] if mode == 'max' else 1 - rng[r]
        base = np.array(matplotlib.colors.to_rgb(TEAL))
        fcol = tuple(1 - (1 - base) * (0.10 + 0.40 * inten))
        x = xs[c + 1]
        ax.add_patch(Rectangle((x + .004, yy - .46), cws[c + 1] - .008, .92, fc=ACC if win else fcol, ec='none'))
        v = row[k]
        s = {'Estacionalidad': f'{v:.3f}', 'Crecimiento': f'{v:+.2f}', 'Volatilidad': f'{v:.3f}', 'Caida': f'{v:+.1f}'}[k]
        if (k == 'Crecimiento' and row['Serie'] == 'Tipo Viajero') or (k == 'Caida' and row['Serie'] in ('Tipo Viajero', 'Tipo Cruceristas')):
            s += '*'
        ax.text(x + cws[c + 1] / 2, yy, s, ha='center', va='center', fontsize=8.5, color='white' if win else INK, fontweight='bold' if win else 'normal')
txt(M, 11.78, 'En una frase: Cruceristas y la vía Marítima son los más estacionales y volátiles; Terrestre y Excursionista, los más golpeados (−73.6% y −75.7%).',
    fontsize=8.5, fontweight='bold')
txt(M, 12.0, '*"Viajero" cambió de definición en 2022–23 y "Cruceristas" dejó de reportarse: esas cifras reflejan en parte el cambio de reporte, no solo la pandemia.', fontsize=7.3, color=GRAY)

# ============ BLOQUE 4: modelos y pronostico ============
titulo(12.45, '3 · Qué modelo acierta más y qué esperar', 'Cinco algoritmos, un mismo conjunto de prueba: abr-2021 a jun-2026 (63 meses)')
NB = {'Prophet': (113358.9, 119739.5)}   # cifras del notebook (Prophet no es determinista entre ejecuciones)
tb = tabla.copy()
for k, (a, b) in NB.items():
    tb.loc[tb.Modelo == k, ['MAE', 'RMSE']] = (a, b)
tb = tb.sort_values('RMSE').reset_index(drop=True)
txt(M, 13.12, 'Error de predicción (viajeros por mes; menor es mejor)', fontsize=9.5, fontweight='bold')
ax = ax_in(M + 1.75, 13.55, 2.35, 1.3)
clean(ax, left=False)
yy = np.arange(len(tb))
hg = .38
ax.barh(yy - hg / 2, tb.MAE / 1e3, height=hg, color=NAVY)
ax.barh(yy + hg / 2, tb.RMSE / 1e3, height=hg, color='#8FA3BD')
for i, r in tb.iterrows():
    ax.text(r.MAE / 1e3 + 4, i - hg / 2, f'{r.MAE:,.0f}', va='center', fontsize=7.5)
    ax.text(r.RMSE / 1e3 + 4, i + hg / 2, f'{r.RMSE:,.0f}', va='center', fontsize=7.5)
ax.set_yticks(yy)
ax.set_yticklabels(tb.Modelo, fontsize=8.5)
ax.invert_yaxis()
ax.set_xlim(0, 330)
ax.set_xticks([])
ax.spines['bottom'].set_visible(False)
ax.get_yticklabels()[0].set_color(ACC)
ax.get_yticklabels()[0].set_fontweight('bold')
txt(M, 13.35, '■ MAE: error medio', fontsize=8, color=NAVY)
txt(M + 1.6, 13.35, '■ RMSE: castiga errores grandes', fontsize=8, color=RMSE_TXT)
txt(M, 15.1, 'Gana Prophet (error medio ≈113 mil viajeros/mes): se adapta a\ncambios de tendencia. SARIMA, el modelo clásico, extrapola\nel pasado y queda último.', fontsize=8.3, linespacing=1.25)

xr = M + 4.55
wr = W - M - xr
txt(xr, 13.12, 'Modelo ganador (Prophet) vs. lo ocurrido', fontsize=9.5, fontweight='bold')
ax = ax_in(xr + 0.55, 13.45, wr - 0.55, 1.35)
clean(ax)
st, fc = D['s_te'], D['fc']
ax.fill_between(fc.index, fc.yhat_lower / 1e3, fc.yhat_upper / 1e3, color=ACC, alpha=.18, lw=0)
ax.plot(st.index, st.values / 1e3, color=NAVY, lw=1.7)
ax.plot(fc.index, fc.yhat / 1e3, color=ACC, lw=1.7, ls='--')
ax.set_ylim(0, 540)
ax.grid(axis='y', color=LIGHT, lw=.8)
ax.set_axisbelow(True)
ax.set_ylabel('Miles / mes', fontsize=8, color=GRAY)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.text(pd.Timestamp('2021-05-01'), 360, 'Real (observado)', color=NAVY, fontsize=9, fontweight='bold')
ax.text(pd.Timestamp('2022-09-01'), 470, 'Pronóstico Prophet (Estimación)', color=ACC, fontsize=8.5, fontweight='bold', ha='center')
i0 = int(len(fc) * 0.62)
ax.annotate('Banda de Estimación:\nintervalo de confianza 80%', (fc.index[i0], fc.yhat_upper.iloc[i0] / 1e3), (pd.Timestamp('2025-06-01'), 480),
            fontsize=8, color=ACC, ha='center', arrowprops=dict(arrowstyle='-', color=ACC, lw=.8))
cov = ((st.values >= fc.yhat_lower.values) & (st.values <= fc.yhat_upper.values)).mean() * 100
txt(xr, 15.1, f'Ojo: la banda de Estimación contiene solo el {cov:.0f}% de los meses reales. Los modelos se\nentrenaron con datos hasta mar-2021 y no vieron la reapertura: úsese como\nreferencia, no como garantía.', fontsize=8.3, color=GRAY, linespacing=1.25)

# ============ BLOQUE 5: recomendaciones + pie ============
terr = via['Terrestre'] / via.sum() * 100
cr = cuad.set_index('Serie')
titulo(15.65, '4 · Qué hacer: recomendaciones para INGUAT')
recs = [
    f'Priorizar fronteras terrestres: concentran el {terr:.0f}% de los ingresos y crecieron {cr.loc["Vía Terrestre", "Crecimiento"]:.1f}% anual antes del COVID.',
    f'Calendarizar personal y capacidad: diciembre rinde +33% sobre la media, con Semana Santa y julio arriba; promover feb y sep (valles).',
    f'Plan propio para cruceros: caían {abs(cr.loc["Vía Marítima", "Crecimiento"]):.1f}% anual desde antes del COVID y son los más volátiles; usar pronóstico simple (seasonal naive).',
    f'Pronosticar con Prophet y vigilar mes a mes: la banda cubre solo {cov:.0f}% de lo real; el dato observado debe corregir la proyección.',
    f'Tratar la recuperación como incompleta: 2025 está {100 - v25 / v19 * 100:.0f}% bajo 2019 y ene–jun 2026 está 3% bajo 2025; reactivar mercados lejanos (EE. UU.) por la vía aérea.']
for i, r in enumerate(recs):
    y = 16.0 + i * 0.0
txt(M, 16.0, '\n'.join(f'{i + 1}.  {r}' for i, r in enumerate(recs)), fontsize=8, linespacing=1.3)
rect(0, 16.62, W, 0.38, fc=NAVY, ec='none')
txt(M, 16.66, 'Fuente: Base de Migración 2009–jun 2026, INGUAT/IGM. Análisis: Laboratorio 1, CC3084 Data Science, UVG. Métricas MAE/RMSE del Laboratorio 1. Datos con fines académicos.',
    fontsize=6.8, color='white')
txt(M, 16.82, 'Autores: David Dominguez (23712) · Gabriel Bran (23590) · Luis Padilla (23663)   ·   Color: azul = lo observado · naranja = anomalía y proyección (Estimación) · verde azulado = patrones estacionales.',
    fontsize=6.8, color='#DCE3EC')

fig.savefig('Lab9_Infografia.png', dpi=200, facecolor=BG)
fig.savefig('Lab9_Infografia.pdf', facecolor=BG)
print('ok')
