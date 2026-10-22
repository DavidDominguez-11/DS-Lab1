"""Observatorio de Turismo Sostenible - Guatemala. Tablero interactivo (Laboratorio 10).

Ejecutar:  streamlit run tablero/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
CORTE = pd.Timestamp("2021-04-01")

# Paleta con significado fijo en todo el tablero (segura para daltonismo, Okabe-Ito)
C_OBS = "#1B4F72"      # azul oscuro = dato observado
C_SEL = "#0072B2"      # azul medio = seleccion del usuario
C_MODELO = {"SARIMA": "#CC79A7", "Holt-Winters": "#009E73", "Prophet": "#D55E00",
            "Seasonal naive": "#7F7F7F"}   # un color fijo por modelo = estimacion
C_NARANJA = "#D55E00"  # estimo mas de lo que hubo
ESCALA = "Blues"
MODELOS_ORDEN = ["Prophet", "Holt-Winters", "SARIMA", "Seasonal naive", "LSTM simple (1 capa)",
                 "LSTM apilado (2 capas) + dropout", "LSTM global + catch22"]
_EXTRA = {"LSTM simple (1 capa)": "#0072B2", "LSTM apilado (2 capas) + dropout": "#E69F00",
          "LSTM global + catch22": "#56B4E9"}


def color_modelo(nombre):
    return C_MODELO.get(nombre) or _EXTRA.get(nombre, "#444444")

st.set_page_config(page_title="Observatorio de Turismo - Guatemala", page_icon="🧭", layout="wide")
st.markdown("""<style>
html, body, [class*="css"] {font-size: 16px;}
.tag-obs, .tag-est {display:inline-block;padding:2px 10px;border-radius:12px;font-size:.8rem;font-weight:600;color:#fff}
.tag-obs {background:#1B4F72} .tag-est {background:#B34700}
.aviso {border-left:4px solid #D55E00;background:#FFF4EB;padding:.6rem .9rem;border-radius:4px;margin:.4rem 0}
.guia {color:#475569;font-size:.95rem;margin-bottom:.4rem}
</style>""", unsafe_allow_html=True)


def etiqueta(tipo):
    cls, txt = ("tag-obs", "Dato observado") if tipo == "obs" else ("tag-est", "Estimación de modelo")
    st.markdown(f'<span class="{cls}">{txt}</span>', unsafe_allow_html=True)


def sin_datos(msg="No hay datos para la selección actual. Amplíe el rango de años o los filtros de la barra lateral."):
    st.info(msg, icon="ℹ️")


def fmt(n):
    return f"{n:,.0f}"


@st.cache_data
def cargar():
    df = pd.read_csv(RAIZ / "Base_Migracion_2009-2026jun.csv", sep=";", encoding="utf-8-sig")
    df.columns = ["anio", "mes_cod", "mes", "via", "frontera", "pais", "region", "region2", "omt",
                  "mceo", "residencia", "tipo", "viajeros"]
    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes_cod"], day=1))
    return df.drop(columns=["mes", "omt", "mceo", "residencia", "region"])


@st.cache_data
def cargar_modelos():
    d = RAIZ / "data"
    p = [pd.read_csv(d / "predicciones.csv", parse_dates=["fecha"])]
    m = [pd.read_csv(d / "metricas.csv")]
    if (d / "predicciones_lstm.csv").exists():   # LSTM del Laboratorio 2 (scripts/exportar_lstm.py)
        p.append(pd.read_csv(d / "predicciones_lstm.csv", parse_dates=["fecha"]))
        m.append(pd.read_csv(d / "metricas_lstm.csv"))
    return pd.concat(p, ignore_index=True), pd.concat(m, ignore_index=True)


df = cargar()
pred, met = cargar_modelos()

# ---------------------------------------------------------------- barra lateral
st.sidebar.title("🧭 Observatorio de Turismo")
st.sidebar.caption("Ingreso de viajeros internacionales a Guatemala · 2009 – jun 2026")
pagina = st.sidebar.radio("¿Qué desea consultar?", ["1 · Panorama general", "2 · Explorar a detalle",
                                                    "3 · Predicciones y modelos"])
st.sidebar.divider()
st.sidebar.subheader("Filtros")
a0, a1 = int(df.anio.min()), int(df.anio.max())
rango = st.sidebar.slider("Años", a0, a1, (a0, a1), help="Acota los gráficos de las páginas 1 y 2.")
tipos_sel = st.sidebar.multiselect(
    "Tipo de viajero", sorted(df.tipo.unique()), default=["Turista", "Excursionista"],
    help="Por defecto Turista + Excursionista: es la medida comparable en todo el periodo. "
         "La categoría «Viajero» cambió de definición en 2022-2023 y «Cruceristas» deja de reportarse desde 2023.")
vias_sel = st.sidebar.multiselect("Vía de ingreso", sorted(df.via.unique()), default=sorted(df.via.unique()))
if "Viajero" in tipos_sel or "Cruceristas" in tipos_sel:
    st.sidebar.warning("«Viajero» y «Cruceristas» no son comparables entre años (cambio de definición 2022-2023).")

f = df[df.anio.between(*rango) & df.tipo.isin(tipos_sel) & df.via.isin(vias_sel)]

# ---------------------------------------------------------------- pagina 1
if pagina.startswith("1"):
    st.title("Panorama general del turismo receptor")
    st.markdown('<p class="guia">Pregunta guía: <b>¿Cómo ha evolucionado el ingreso de viajeros y qué ocurrió '
                'en un año específico?</b> Haga clic en una barra del gráfico anual para ver el detalle de ese año.</p>',
                unsafe_allow_html=True)
    if f.empty:
        sin_datos()
        st.stop()

    anual = f.groupby("anio", as_index=False).viajeros.sum()
    ult = anual.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de viajeros en el rango", fmt(anual.viajeros.sum()))
    c2.metric("Año con más viajeros", f"{int(anual.loc[anual.viajeros.idxmax(), 'anio'])}",
              fmt(anual.viajeros.max()), delta_color="off")
    if len(anual) > 1:
        prev = anual.iloc[-2]
        ult_d = f[f.anio == ult.anio]
        m_max = int(ult_d.mes_cod.max())
        if m_max < 12:   # año incompleto: se compara contra los mismos meses del año anterior
            base = f[(f.anio == prev.anio) & (f.mes_cod <= m_max)].viajeros.sum()
            c3.metric(f"{int(ult.anio)} (ene-{MESES[m_max - 1].lower()}) vs mismos meses de {int(prev.anio)}",
                      fmt(ult_d.viajeros.sum()), f"{(ult_d.viajeros.sum() / base - 1):+.1%}" if base else None)
        else:
            c3.metric(f"Último año ({int(ult.anio)}) vs {int(prev.anio)}", fmt(ult.viajeros),
                      f"{(ult.viajeros / prev.viajeros - 1):+.1%}")
    if rango[1] == a1:
        st.caption(f"⚠️ {a1} está incompleto (llega hasta junio): no es comparable con un año completo.")

    anios = [int(a) for a in anual.anio]
    if st.session_state.get("anio_sel") not in anios:
        st.session_state["anio_sel"] = int(anual.loc[anual.viajeros.idxmax(), "anio"])

    izq, der = st.columns([1.1, 1])
    with izq:
        etiqueta("obs")
        st.subheader("Viajeros por año")
        sel_prev = st.session_state["anio_sel"]
        fig = go.Figure(go.Bar(x=anual.anio, y=anual.viajeros,
                               marker_color=[C_SEL if a == sel_prev else C_OBS for a in anual.anio],
                               hovertemplate="Año %{x}<br>%{y:,.0f} viajeros<extra></extra>"))
        fig.update_layout(height=380, margin=dict(t=10, b=10), xaxis=dict(dtick=1, title="Año"),
                          yaxis_title="Viajeros", clickmode="event+select")
        ev = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="barras_anio",
                             width="stretch")
        pts = ev.selection.points if ev and ev.selection else []
        if pts and int(pts[0]["x"]) != st.session_state["anio_sel"]:
            st.session_state["anio_sel"] = int(pts[0]["x"])
            st.rerun()
        anio = st.selectbox("…o elija el año aquí", anios, key="anio_sel")
    with der:
        etiqueta("obs")
        st.subheader(f"Detalle de {anio}")
        nivel = st.radio("Nivel de detalle", ["Mes", "Trimestre", "Por vía de ingreso"], horizontal=True,
                         help="Acerque o aleje la mirada sobre el año seleccionado.")
        d = f[f.anio == anio]
        if nivel == "Mes":
            g = d.groupby("mes_cod", as_index=False).viajeros.sum()
            g["etq"] = g.mes_cod.map(lambda m: MESES[m - 1])
            fig2 = px.line(g, x="etq", y="viajeros", markers=True, color_discrete_sequence=[C_SEL])
        elif nivel == "Trimestre":
            d = d.assign(q="T" + ((d.mes_cod - 1) // 3 + 1).astype(str))
            g = d.groupby("q", as_index=False).viajeros.sum()
            fig2 = px.bar(g, x="q", y="viajeros", color_discrete_sequence=[C_SEL])
        else:
            g = d.groupby("via", as_index=False).viajeros.sum()
            fig2 = px.bar(g, x="via", y="viajeros", color_discrete_sequence=[C_SEL])
        fig2.update_layout(height=380, margin=dict(t=10, b=10), xaxis_title="", yaxis_title="Viajeros")
        fig2.update_traces(hovertemplate="%{x}: %{y:,.0f} viajeros<extra></extra>")
        st.plotly_chart(fig2, width="stretch")
    st.markdown("**Cómo leerlo:** la altura de cada barra es el total de viajeros del año. La caída de 2020 coincide "
                "con el cierre de fronteras por la pandemia; los datos por sí solos no permiten atribuir causas "
                "a otras variaciones.")

# ---------------------------------------------------------------- pagina 2
elif pagina.startswith("2"):
    st.title("Explorar a detalle")
    st.markdown('<p class="guia">Pregunta guía: <b>¿Cuándo vienen, de dónde y por dónde?</b> Elija qué gráficos '
                'desea ver; los filtros de la izquierda aplican a todos.</p>', unsafe_allow_html=True)
    if f.empty:
        sin_datos()
        st.stop()
    OPC = ["Estacionalidad (mapa de calor)", "Origen de los viajeros (jerarquía)", "Países y fronteras principales"]
    vistas = st.multiselect("Gráficos a mostrar", OPC, default=OPC[:2])
    if not vistas:
        sin_datos("Seleccione al menos un gráfico para mostrar.")
    if OPC[0] in vistas:
        etiqueta("obs")
        st.subheader("¿En qué meses llegan más viajeros?")
        piv = f.pivot_table(index="anio", columns="mes_cod", values="viajeros", aggfunc="sum").reindex(columns=range(1, 13))
        fig = px.imshow(piv.values, x=MESES, y=piv.index, color_continuous_scale=ESCALA, aspect="auto",
                        labels=dict(color="Viajeros", x="Mes", y="Año"))
        fig.update_layout(height=420, margin=dict(t=10, b=10))
        fig.update_xaxes(side="top")
        fig.update_yaxes(dtick=1)
        st.plotly_chart(fig, width="stretch")
        st.caption("Más oscuro = más viajeros. Casillas en blanco: meses sin datos (p. ej. después de junio 2026).")
    if OPC[1] in vistas:
        etiqueta("obs")
        st.subheader("¿De dónde vienen? Región → País")
        nivel = st.radio("Nivel de detalle", ["Solo regiones", "Regiones y países"], horizontal=True)
        top = f.groupby(["region2", "pais"], as_index=False).viajeros.sum()
        top = top[top.viajeros > 0]
        if nivel == "Solo regiones":
            top = top.groupby("region2", as_index=False).viajeros.sum()
            fig = px.treemap(top, path=["region2"], values="viajeros", color="viajeros", color_continuous_scale=ESCALA)
        else:
            fig = px.treemap(top, path=["region2", "pais"], values="viajeros", color="viajeros", color_continuous_scale=ESCALA)
        fig.update_layout(height=460, margin=dict(t=10, b=10), coloraxis_showscale=False)
        fig.update_traces(hovertemplate="%{label}: %{value:,.0f} viajeros<extra></extra>", root_color="white")
        st.plotly_chart(fig, width="stretch")
        st.caption("El área es proporcional al número de viajeros. En países vecinos incluye movilidad fronteriza "
                   "cotidiana, no solo turismo.")
    if OPC[2] in vistas:
        etiqueta("obs")
        st.subheader("Principales países y puntos de ingreso")
        n = st.slider("¿Cuántos mostrar?", 5, 20, 10)
        c1, c2 = st.columns(2)
        for col, campo, tit in [(c1, "pais", "País de residencia"), (c2, "frontera", "Frontera / punto de ingreso")]:
            g = f.groupby(campo, as_index=False).viajeros.sum().nlargest(n, "viajeros").sort_values("viajeros")
            fig = px.bar(g, x="viajeros", y=campo, orientation="h", color_discrete_sequence=[C_OBS])
            fig.update_layout(height=420, margin=dict(t=30, b=10), title=tit, xaxis_title="Viajeros", yaxis_title="")
            col.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- pagina 3
else:
    st.title("Predicciones y comparación de modelos")
    st.markdown('<p class="guia">Pregunta guía: <b>¿Qué tan confiable es una predicción y qué modelo se acerca más a lo '
                'ocurrido?</b> Cada modelo se entrenó con datos hasta marzo 2021 y se probó contra abril 2021 – junio 2026.</p>',
                unsafe_allow_html=True)
    st.markdown('<div class="aviso"><b>Límite importante:</b> los modelos se entrenaron con datos afectados por la pandemia, '
                'por eso tienden a <b>subestimar</b> la recuperación posterior. Úselos como referencia, no como pronóstico firme. '
                'Los resultados son <b>estimaciones</b>; no explican por qué cambian los viajeros.</div>',
                unsafe_allow_html=True)
    with st.expander("¿Qué significan MAE, RMSE y sesgo?"):
        st.markdown("- **MAE:** error promedio, en viajeros por mes (menor es mejor).\n"
                    "- **RMSE:** parecido al MAE pero castiga más los errores grandes.\n"
                    "- **Sesgo:** si es negativo, el modelo estimó **menos** viajeros de los que hubo (subestima); si es positivo, más.\n"
                    "- Los modelos *Seasonal naive* repiten el último año conocido: sirven de referencia mínima.")
    series_disp = sorted(pred.serie.unique())
    serie = st.selectbox("Serie a analizar", series_disp,
                         index=series_disp.index("Total (Turista + Excursionista)"))
    disp = [m for m in MODELOS_ORDEN if m in set(pred[pred.serie == serie].modelo)]
    default = [m for m in ["Prophet", "Holt-Winters", "SARIMA", "LSTM simple (1 capa)"] if m in disp][:4]
    modelos = st.multiselect("Modelos a comparar", disp, default=default,
                             help="Los LSTM solo están disponibles para las series donde se entrenaron (Total y Vía Terrestre) "
                                  "o con el modelo global con catch22 (todas).")
    p = pred[(pred.serie == serie) & pred.modelo.isin(modelos)]
    if p.empty:
        sin_datos("Seleccione al menos un modelo para ver los resultados.")
        st.stop()
    real = p.drop_duplicates("fecha")[["fecha", "real"]]
    etiqueta("est")
    st.subheader("Valor real frente a lo estimado")
    fig = go.Figure(go.Scatter(x=real.fecha, y=real.real, name="Real (observado)", line=dict(color=C_OBS, width=3)))
    for m in modelos:
        pm_ = p[p.modelo == m]
        fig.add_scatter(x=pm_.fecha, y=pm_.prediccion, name=f"{m} (estimado)", line=dict(color=color_modelo(m), dash="dash"))
    fig.update_layout(height=420, margin=dict(t=10, b=10), yaxis_title="Viajeros por mes", hovermode="x unified",
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")

    m = met[(met.serie == serie) & met.modelo.isin(modelos)].sort_values("RMSE")
    mejor = m.iloc[0]
    st.success(f"Menor error en esta serie: **{mejor.modelo}** (error típico mensual ≈ {fmt(mejor.RMSE)} viajeros).")
    c1, c2 = st.columns(2)
    with c1:
        etiqueta("est")
        st.subheader("Error por modelo")
        metrica = st.radio("Medida de error", ["RMSE", "MAE"], horizontal=True)
        fig = go.Figure(go.Bar(x=m[metrica], y=m.modelo, orientation="h",
                               marker_color=[color_modelo(x) for x in m.modelo],
                               hovertemplate="%{y}: %{x:,.0f} viajeros/mes<extra></extra>"))
        fig.update_layout(height=320, margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"),
                          xaxis_title=f"{metrica} (viajeros/mes)", clickmode="event+select")
        ev = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="barras_modelo", width="stretch")
        st.caption("Haga clic en una barra para ver el error de ese modelo mes a mes (gráfico de abajo).")
        pts = ev.selection.points if ev and ev.selection else []
        if pts:
            st.session_state["modelo_sel"] = pts[0]["y"]
    with c2:
        st.subheader("Tabla comparativa")
        tabla_m = m[["modelo", "MAE", "RMSE", "sesgo"]].rename(columns={"modelo": "Modelo", "sesgo": "Sesgo"})
        st.dataframe(tabla_m.style.format({"MAE": "{:,.0f}", "RMSE": "{:,.0f}", "Sesgo": "{:+,.0f}"}),
                     hide_index=True, width="stretch")
        st.caption("Más pequeño = más cercano a lo ocurrido en el periodo de prueba.")

    sel = st.session_state.get("modelo_sel")
    if sel not in list(m.modelo):
        sel = mejor.modelo
    sel = st.selectbox("Modelo a detallar", list(m.modelo), index=list(m.modelo).index(sel), key="modelo_det")
    st.session_state["modelo_sel"] = sel
    etiqueta("est")
    st.subheader(f"¿Cuánto se equivocó «{sel}» y cuándo?")
    det = st.radio("Nivel de detalle", ["Por mes", "Por año"], horizontal=True, key="det_err")
    e = p[p.modelo == sel].assign(error=lambda x: x.real - x.prediccion)
    if det == "Por año":
        e = e.groupby(e.fecha.dt.year, as_index=False).agg(error=("error", "mean"))
        e.columns = ["periodo", "error"]
    else:
        e = e.rename(columns={"fecha": "periodo"})
    fig = go.Figure(go.Bar(x=e.periodo, y=e.error, marker_color=[C_OBS if v >= 0 else C_NARANJA for v in e.error],
                           hovertemplate="%{x}: %{y:+,.0f} viajeros<extra></extra>"))
    fig.add_hline(y=0, line_color="#1F2937", line_width=1)
    fig.update_layout(height=340, margin=dict(t=10, b=10), yaxis_title="Real − estimado (viajeros)")
    st.plotly_chart(fig, width="stretch")
    st.caption("Azul: el modelo estimó menos de lo que hubo (subestimó). Naranja: estimó más de lo que hubo.")

    st.divider()
    etiqueta("est")
    st.subheader("¿Qué modelo conviene en cada serie?")
    rel = met.assign(rel=lambda x: x.RMSE / x.groupby("serie").RMSE.transform("min"))
    piv = rel.pivot(index="serie", columns="modelo", values="rel")[[c for c in MODELOS_ORDEN if c in set(met.modelo)]]
    fig = px.imshow(piv.values, x=list(piv.columns), y=list(piv.index), color_continuous_scale="Oranges", aspect="auto",
                    text_auto=".1f", labels=dict(color="Veces el mejor"))
    fig.update_layout(height=380, margin=dict(t=10, b=10))
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, width="stretch")
    st.caption("Cada celda es el error (RMSE) del modelo dividido entre el del mejor modelo de esa serie: 1.0 = el mejor (más claro); "
               "2.0 = se equivoca el doble (más oscuro = peor). Casillas en blanco: el modelo no se entrenó para esa serie.")
