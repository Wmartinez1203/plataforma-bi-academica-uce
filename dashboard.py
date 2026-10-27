import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Plataforma de Inteligencia Académica | UCE",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main { background-color: #0b0f19; }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .header-badge {
        background: #2563eb;
        color: #ffffff;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .kpi-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover { border-color: #38bdf8; transform: translateY(-2px); }
    .kpi-label { color: #94a3b8; font-size: 11.5px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { color: #f8fafc; font-size: 25px; font-weight: 700; }
    .kpi-subtext { color: #64748b; font-size: 11px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    fact = pd.read_csv("data/processed/fact_rendimiento_academico.csv")
    oferta = pd.read_csv("data/processed/dim_oferta.csv")
    asig = pd.read_csv("data/processed/dim_asignatura.csv")
    doc = pd.read_csv("data/processed/dim_docente.csv")
    est = pd.read_csv("data/processed/dim_estudiante.csv")
    
    df = fact.merge(oferta, on="oferta_id", how="left")
    df = df.merge(asig, on="asignatura_id", how="left")
    df = df.merge(doc, on="docente_id", how="left")
    df = df.merge(est, on="estudiante_id", how="left")
    return df, oferta, asig, doc

df_raw, oferta_raw, asig_raw, doc_raw = load_data()

st.markdown("""
<div class="header-box">
    <span class="header-badge">UCE • FACULTAD DE INGENIERÍA Y CIENCIAS APLICADAS • ISI</span>
    <h2 style="color:#f8fafc; margin:8px 0 4px 0; font-size:22px;">Plataforma Analítica y Motor de Exploración de Rendimiento Académico</h2>
    <p style="color:#94a3b8; margin:0; font-size:13px;">Caso 3: Modelo Dimensional, Trazabilidad Operacional y Detección de Vulnerabilidad</p>
</div>
""", unsafe_allow_html=True)

# BARRA LATERAL: MOTOR DE BÚSQUEDA PROFESIONAL Y FILTROS
with st.sidebar:
    st.markdown("### 🔎 Motor de Búsqueda Avanzada")
    search_query = st.text_input("Búsqueda global (Materia, Código, Estudiante)", placeholder="Ej. ISI101, Cálculo, M00001...")
    
    st.divider()
    st.markdown("### 🎛️ Filtros Multidimensionales")
    
    periodos = ["Todos"] + sorted(list(df_raw["periodo_id"].dropna().astype(str).unique()))
    sel_periodo = st.selectbox("Período Lectivo", periodos)

    areas = ["Todas"] + sorted(list(df_raw["area"].dropna().astype(str).unique()))
    sel_area = st.selectbox("Área de Conocimiento", areas)

    semestres = ["Todos"] + sorted(list(df_raw["semestre"].dropna().unique()))
    sel_semestre = st.selectbox("Semestre Curricular", semestres)

    jornadas = ["Todos"] + sorted(list(df_raw["jornada"].dropna().unique()))
    sel_jornada = st.selectbox("Jornada", jornadas)

    intentos = ["Todos"] + sorted(list(df_raw["intento"].dropna().unique()))
    sel_intento = st.selectbox("Intento de Matrícula", intentos)

    st.markdown("#### 🎯 Rangos de Rendimiento")
    rango_nota = st.slider("Filtrar por Rango de Nota Final (/20)", 0.0, 20.0, (0.0, 20.0), 0.5)
    solo_vulnerables = st.checkbox("Ver solo casos en Alerta Temprana")

# Filtrado reactivo de datos
df_filtered = df_raw.copy()

if search_query:
    q = search_query.strip().lower()
    df_filtered = df_filtered[
        df_filtered["nombre"].astype(str).str.lower().str.contains(q) |
        df_filtered["codigo"].astype(str).str.lower().str.contains(q) |
        df_filtered["estudiante_id"].astype(str).str.lower().str.contains(q) |
        df_filtered["matricula_id"].astype(str).str.lower().str.contains(q)
    ]

if sel_periodo != "Todos":
    df_filtered = df_filtered[df_filtered["periodo_id"].astype(str) == str(sel_periodo)]
if sel_area != "Todas":
    df_filtered = df_filtered[df_filtered["area"] == sel_area]
if sel_semestre != "Todos":
    df_filtered = df_filtered[df_filtered["semestre"] == sel_semestre]
if sel_jornada != "Todos":
    df_filtered = df_filtered[df_filtered["jornada"] == sel_jornada]
if sel_intento != "Todos":
    df_filtered = df_filtered[df_filtered["intento"] == sel_intento]

# Filtro de rango de nota y vulnerabilidad
df_filtered = df_filtered[
    (df_filtered["nota_final"].isna()) | 
    ((df_filtered["nota_final"] >= rango_nota[0]) & (df_filtered["nota_final"] <= rango_nota[1]))
]

if solo_vulnerables:
    df_filtered = df_filtered[df_filtered["alerta_vulnerabilidad"] == 1]

evaluados = df_filtered[~df_filtered["es_retiro_o_anulado"]]

def aplicar_tema(fig):
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0", size=11),
        title_font=dict(size=13.5, color="#f8fafc"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="#1f2937", zerolinecolor="#1f2937"),
        yaxis=dict(gridcolor="#1f2937", zerolinecolor="#1f2937"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# Pestañas
tab_ejecutiva, tab_diagnostico, tab_auditoria = st.tabs([
    "📊 Vista Ejecutiva de Cohortes", 
    "🔬 Diagnóstico y Búsqueda Detallada", 
    "🛡️ Auditoría Operativa y Sobrecupos"
])

# 1. VISTA EJECUTIVA
with tab_ejecutiva:
    total_mat = len(df_filtered)
    total_eval = len(evaluados)
    total_aprob = evaluados["es_aprobado"].sum() if total_eval > 0 else 0
    tasa_aprob = (total_aprob / total_eval * 100) if total_eval > 0 else 0
    tasa_retiro = (df_filtered["es_retiro_o_anulado"].sum() / total_mat * 100) if total_mat > 0 else 0
    prom_nota = evaluados["nota_final"].mean() if total_eval > 0 else 0
    tasa_vuln = (evaluados["alerta_vulnerabilidad"].sum() / total_eval * 100) if total_eval > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Matrículas Totales</div><div class="kpi-value">{total_mat:,}</div><div class="kpi-subtext">Registros filtrados</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">Tasa de Aprobación</div><div class="kpi-value" style="color:#38bdf8;">{tasa_aprob:.2f}%</div><div class="kpi-subtext">{total_aprob:,} aprobados</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">Tasa de Deserción</div><div class="kpi-value" style="color:#f59e0b;">{tasa_retiro:.2f}%</div><div class="kpi-subtext">Retirados/anulados</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">Promedio de Nota</div><div class="kpi-value">{prom_nota:.2f} <span style="font-size:13px;color:#94a3b8;">/ 20</span></div><div class="kpi-subtext">Escala oficial</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="kpi-card"><div class="kpi-label">Vulnerabilidad</div><div class="kpi-value" style="color:#ef4444;">{tasa_vuln:.1f}%</div><div class="kpi-subtext">Alerta temprana</div></div>', unsafe_allow_html=True)

    st.write("")
    col_e1, col_e2 = st.columns([1.1, 0.9])
    
    with col_e1:
        trend = evaluados.groupby("periodo_id").agg(
            aprobados=("es_aprobado", "sum"),
            total=("matricula_id", "count"),
            nota_media=("nota_final", "mean")
        ).reset_index()
        
        if len(trend) > 0:
            trend["periodo_id"] = trend["periodo_id"].astype(str)
            trend["tasa_aprob"] = (trend["aprobados"] / trend["total"]) * 100
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(x=trend["periodo_id"], y=trend["tasa_aprob"], name="% Aprobación", marker_color="#2563eb", opacity=0.85))
            fig_trend.add_trace(go.Scatter(x=trend["periodo_id"], y=trend["nota_media"], name="Nota Promedio (/20)", yaxis="y2", mode="lines+markers", line=dict(color="#38bdf8", width=3)))
            fig_trend.update_layout(title="Evolución de Aprobación y Rendimiento por Período", yaxis=dict(title="% Aprobación", range=[0, 100]), yaxis2=dict(title="Nota (/20)", overlaying="y", side="right", range=[0, 20]), xaxis=dict(type="category"))
            st.plotly_chart(aplicar_tema(fig_trend), use_container_width=True)
        else:
            st.info("Sin registros suficientes para graficar tendencia.")

    with col_e2:
        dif = evaluados.groupby(["codigo", "nombre"]).agg(total=("matricula_id", "count"), reprobados=("es_reprobado", "sum")).reset_index()
        if len(dif) > 0:
            dif["tasa_reprob"] = (dif["reprobados"] / dif["total"]) * 100
            top_dif = dif.sort_values(by="tasa_reprob", ascending=True).tail(6)
            fig_bar = px.bar(top_dif, x="tasa_reprob", y="nombre", orientation="h", title="Top Asignaturas Filtro (% Reprobación)", labels={"tasa_reprob": "% Reprobación", "nombre": ""}, color="tasa_reprob", color_continuous_scale=["#f59e0b", "#ef4444"], text_auto=".1f")
            fig_bar.update_layout(coloraxis_showscale=False)
            st.plotly_chart(aplicar_tema(fig_bar), use_container_width=True)
        else:
            st.info("Sin datos para asignaturas críticas.")

# 2. VISTA DE DIAGNÓSTICO Y BÚSQUEDA DETALLADA
with tab_diagnostico:
    st.markdown("#### Búsqueda Granular y Diagnóstico de Rendimiento")
    col_d1, col_d2 = st.columns([1.1, 0.9])
    
    with col_d1:
        valid_diag = evaluados[evaluados["asistencia_pct"] >= 0]
        n_valid = len(valid_diag)
        if n_valid > 0:
            sample_diag = valid_diag.sample(min(1200, n_valid), random_state=42)
            fig_scatter = px.scatter(sample_diag, x="asistencia_pct", y="nota_final", color="estado_academico", opacity=0.65, title=f"Dispersión: Asistencia vs Calificación Final (Muestra N={len(sample_diag)})", labels={"asistencia_pct": "% Asistencia", "nota_final": "Nota Final (/20)"}, color_discrete_map={"Aprobado": "#10b981", "Reprobado": "#ef4444"})
            fig_scatter.add_hline(y=14.0, line_dash="dash", line_color="#94a3b8", annotation_text="Aprobado (14.0)")
            st.plotly_chart(aplicar_tema(fig_scatter), use_container_width=True)
            st.caption("ℹ️ *Sustentación al Tribunal:* Correlación lineal r = 0.206. Se describe asociación positiva sin inferir causalidad determinista.")
        else:
            st.info("Sin registros de asistencia válidos bajo este criterio de búsqueda.")

    with col_d2:
        comp_intento = evaluados.groupby("intento").agg(total=("matricula_id", "count"), aprobados=("es_aprobado", "sum")).reset_index()
        if len(comp_intento) > 0:
            comp_intento["tasa_aprob"] = (comp_intento["aprobados"] / comp_intento["total"]) * 100
            comp_intento["intento_label"] = comp_intento["intento"].apply(lambda x: f"Intento {x}")
            fig_intento = px.bar(comp_intento, x="intento_label", y="tasa_aprob", text_auto=".1f", title="Tasa de Aprobación por Intento de Matrícula", labels={"intento_label": "", "tasa_aprob": "% Aprobación"}, color="tasa_aprob", color_continuous_scale=["#3b82f6", "#10b981"])
            fig_intento.update_layout(coloraxis_showscale=False)
            st.plotly_chart(aplicar_tema(fig_intento), use_container_width=True)
        else:
            st.info("Sin registros de intentos.")

    st.markdown("#### 📋 Matriz de Registros Encontrados con Filtros / Búsqueda")
    tabla_busqueda = df_filtered[[
        "matricula_id", "estudiante_id", "periodo_id", "codigo", "nombre", 
        "intento", "nota_primer_parcial", "nota_segundo_parcial", "nota_final", "asistencia_pct", "estado_academico"
    ]].sort_values(by="nota_final", ascending=True)

    st.dataframe(
        tabla_busqueda.head(200),
        column_config={
            "matricula_id": "Matrícula ID",
            "estudiante_id": "Estudiante",
            "periodo_id": "Período",
            "codigo": "Código",
            "nombre": "Asignatura",
            "intento": "Int.",
            "nota_primer_parcial": st.column_config.NumberColumn("P1", format="%.2f"),
            "nota_segundo_parcial": st.column_config.NumberColumn("P2", format="%.2f"),
            "nota_final": st.column_config.NumberColumn("Nota Final", format="%.2f"),
            "asistencia_pct": st.column_config.ProgressColumn("Asistencia", format="%.0f%%", min_value=0, max_value=100),
            "estado_academico": "Estado"
        },
        use_container_width=True,
        hide_index=True
    )
    
    csv_data = tabla_busqueda.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar cohorte filtrada en CSV (Para Dirección de Carrera / Bienestar)",
        data=csv_data,
        file_name="cohorte_academica_filtrada.csv",
        mime="text/csv"
    )

# 3. AUDITORÍA DE SOBRECUPOS
with tab_auditoria:
    st.markdown("#### Auditoría Operativa de Conciliación de Cupos")
    conteo_oferta = df_raw.groupby("oferta_id").size().reset_index(name="estudiantes_inscritos")
    oferta_comp = oferta_raw.merge(conteo_oferta, on="oferta_id", how="left").fillna({"estudiantes_inscritos": 0})
    oferta_comp = oferta_comp.merge(asig_raw[["asignatura_id", "codigo", "nombre", "area", "semestre"]], on="asignatura_id", how="left")

    if sel_periodo != "Todos":
        oferta_comp = oferta_comp[oferta_comp["periodo_id"].astype(str) == str(sel_periodo)]
    if sel_area != "Todas":
        oferta_comp = oferta_comp[oferta_comp["area"] == sel_area]
    if sel_semestre != "Todos":
        oferta_comp = oferta_comp[oferta_comp["semestre"] == sel_semestre]

    oferta_comp["diferencia_cupo"] = oferta_comp["estudiantes_inscritos"] - oferta_comp["cupo"]
    oferta_comp["porcentaje_ocupacion"] = (oferta_comp["estudiantes_inscritos"] / oferta_comp["cupo"]) * 100
    oferta_comp["estado_seccion"] = oferta_comp["diferencia_cupo"].apply(
        lambda x: "🚨 Sobrecupo" if x > 0 else ("🟡 Lleno (100%)" if x == 0 else "🟢 Cupos Libres")
    )

    secciones_totales = len(oferta_comp)
    secciones_sobrecupo = len(oferta_comp[oferta_comp["diferencia_cupo"] > 0])
    pct_sobrecupo = (secciones_sobrecupo / secciones_totales * 100) if secciones_totales > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="kpi-card"><div class="kpi-label">Secciones Ofertadas</div><div class="kpi-value">{secciones_totales:,}</div><div class="kpi-subtext">Paralelos analizados</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="kpi-card"><div class="kpi-label">Secciones en Sobrecupo</div><div class="kpi-value" style="color:#ef4444;">{secciones_sobrecupo:,}</div><div class="kpi-subtext">{pct_sobrecupo:.1f}% de la oferta</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="kpi-card"><div class="kpi-label">Cupos Planificados</div><div class="kpi-value">{oferta_comp["cupo"].sum():,}</div><div class="kpi-subtext">Capacidad teórica</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="kpi-card"><div class="kpi-label">Matrículas Efectivas</div><div class="kpi-value" style="color:#38bdf8;">{oferta_comp["estudiantes_inscritos"].sum():,}</div><div class="kpi-subtext">Demanda real</div></div>', unsafe_allow_html=True)

    st.write("")
    tabla_critica = oferta_comp[oferta_comp["diferencia_cupo"] > 0][[
        "oferta_id", "periodo_id", "codigo", "nombre", "paralelo", "jornada",
        "cupo", "estudiantes_inscritos", "diferencia_cupo", "porcentaje_ocupacion"
    ]].sort_values(by="diferencia_cupo", ascending=False)

    st.dataframe(
        tabla_critica,
        column_config={
            "oferta_id": "ID Sección",
            "periodo_id": "Período",
            "codigo": "Código",
            "nombre": "Asignatura",
            "paralelo": "Par.",
            "jornada": "Jornada",
            "cupo": st.column_config.NumberColumn("Cupo", format="%d"),
            "estudiantes_inscritos": st.column_config.NumberColumn("Inscritos", format="%d"),
            "diferencia_cupo": st.column_config.NumberColumn("Exceso", format="+%d"),
            "porcentaje_ocupacion": st.column_config.NumberColumn("Ocupación", format="%.1f%%")
        },
        use_container_width=True,
        hide_index=True
    )
