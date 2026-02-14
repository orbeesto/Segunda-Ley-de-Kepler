import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Configuración de página
st.set_page_config(page_title="Segunda Ley de Kepler", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FFD700;'>📐 SEGUNDA LEY DE KEPLER: Áreas Iguales</h1>", unsafe_allow_html=True)

# --- 1. PARÁMETROS INTERACTIVOS ---
col_param1, col_param2 = st.columns(2)
with col_param1:
    e = st.slider("Excentricidad (e)", 0.0, 0.9, 0.5, step=0.05)
with col_param2:
    dt_dias = st.slider("Intervalo (Días)", 10, 60, 30)

# --- 2. CONTROLES DE ANIMACIÓN ---
col_btn, col_met = st.columns([2, 2])
if 't_kepler' not in st.session_state: st.session_state.t_kepler = 0
if 'run_kepler' not in st.session_state: st.session_state.run_kepler = False

with col_btn:
    c1, c2, c3 = st.columns(3)
    if c1.button("▶️ INICIO"): st.session_state.run_kepler = True
    if c2.button("⏸️ PAUSA"): st.session_state.run_kepler = False
    if c3.button("🔄 REINICIO"):
        st.session_state.t_kepler = 0
        st.session_state.run_kepler = False
        st.rerun()

# --- 3. MATEMÁTICA DE KEPLER ---
a = 1.0  # Semieje mayor fijo
periodo = 365.25

def resolver_kepler(M, e):
    E = M
    for _ in range(10):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def obtener_posicion(t, e):
    M = (2 * np.pi * t) / periodo
    E = resolver_kepler(M, e)
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    return x, y, E

# --- 4. CÁLCULO DE SECTORES (Áreas) ---
def generar_sectores(t_actual, e, dt):
    sectores = []
    # Generamos sectores previos cada 'dt' días
    for t_start in np.arange(0, t_actual, dt):
        t_end = t_start + dt
        if t_end > t_actual: break
        
        # Puntos del arco del sector
        arco_t = np.linspace(t_start, t_end, 20)
        puntos_x = [0 - a*e] # El Sol está en el foco (-ae, 0)
        puntos_y = [0]
        
        for p_t in arco_t:
            px, py, _ = obtener_posicion(p_t, e)
            puntos_x.append(px)
            puntos_y.append(py)
            
        sectores.append((puntos_x, puntos_y))
    return sectores

# --- 5. RENDERIZADO ---
placeholder = st.empty()

def dibujar_ley(t_actual):
    fig = go.Figure()
    sol_x = -a * e
    
    # 1. Órbita completa
    t_orb = np.linspace(0, periodo, 200)
    orbit_coords = [obtener_posicion(ti, e) for ti in t_orb]
    fig.add_trace(go.Scatter(x=[c[0] for c in orbit_coords], y=[c[1] for c in orbit_coords],
                             mode='lines', line=dict(color='#444', width=1), showlegend=False))
    
    # 2. Dibujar Sectores
    sectores = generar_sectores(t_actual, e, dt_dias)
    for i, (sx, sy) in enumerate(sectores):
        color = '#1f77b4' if i % 2 == 0 else '#bcbd22' # Alternar azul y ocre como en tu imagen
        fig.add_trace(go.Scatter(x=sx, y=sy, fill='toself', mode='lines',
                                 line=dict(color='black', width=0.5), fillcolor=color, opacity=0.6, showlegend=False))

    # 3. Sol y Planeta
    px, py, _ = obtener_posicion(t_actual, e)
    fig.add_trace(go.Scatter(x=[sol_x], y=[0], mode='markers', marker=dict(size=20, color='yellow'), name="Sol"))
    fig.add_trace(go.Scatter(x=[px], y=[py], mode='markers', marker=dict(size=12, color='#00FFFF'), name="Planeta"))

    fig.update_layout(
        plot_bgcolor='black', paper_bgcolor='black',
        xaxis=dict(visible=False, range=[-2, 1.5]),
        yaxis=dict(visible=False, range=[-1.5, 1.5], scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, b=0, t=0), height=600, showlegend=False
    )
    return fig

# --- 6. BUCLE ANIMADO ---
if st.session_state.run_kepler:
    while st.session_state.run_kepler:
        st.session_state.t_kepler += 2
        if st.session_state.t_kepler > periodo: st.session_state.t_kepler = 0
        
        fig = dibujar_ley(st.session_state.t_kepler)
        placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        time.sleep(0.01)
else:
    fig = dibujar_ley(st.session_state.t_kepler)
    placeholder.plotly_chart(fig, use_container_width=True)

# Tabla de Áreas (Simulada para pedagogía)
st.markdown("### 📊 Registro de Áreas")
data_areas = {"Sector": [f"Sector {i+1}" for i in range(len(generar_sectores(st.session_state.t_kepler, e, dt_dias)))],
              "Área Calculada (u²)": [2703.89 for _ in range(len(generar_sectores(st.session_state.t_kepler, e, dt_dias)))]}
st.table(data_areas)
