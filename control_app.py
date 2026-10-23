import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA (ICONO EJECUTIVO) ---
st.set_page_config(
    page_title="Control Maestro - Ferretería El Indio",
    page_icon="👔",
    layout="wide",
)

# Estilos CSS limpios y ejecutivos
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-header {
        background-color: #1f4e78;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 15px;
    }
    .metric-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .time-slot {
        background-color: #e2e8f0;
        padding: 6px;
        font-weight: bold;
        color: #1e293b;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 5px;
        text-align: center;
    }
    .status-free {
        background-color: #dcfce7;
        color: #166534;
        padding: 6px;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #86efac;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyTrK1m9Rs1zSpUp1BRKn5WmSV-ixTrZ-R_yAng-xEGR_6NWYaz1T1W7uSjms5314U3/exec"

# --- 2. ACCESO SEGURIDAD ---
PASSWORD_CORRECTA = "elindio2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h3 style='text-align: center; color: #1f4e78; margin-top: 50px;'>🔒 Control Maestro - Acceso Restringido</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        clave = st.text_input("Contraseña de administrador:", type="password")
        if st.button("Ingresar", use_container_width=True, type="primary"):
            if clave == PASSWORD_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    st.stop()

# --- 3. FUNCIONES DE APOYO ---
def obtener_nombre_hoja(fecha_obj):
    lunes = fecha_obj - timedelta(days=fecha_obj.weekday())
    sabado = lunes + timedelta(days=5)
    meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    return f"SEMANA {lunes.day}-{sabado.day} {meses[lunes.month - 1]}"

def obtener_matriz_hoja(nombre_hoja):
    try:
        response = requests.get(f"{WEB_APP_URL}?action=getData&sheet={nombre_hoja}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

# --- 4. BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Panel de Control")
fecha_consulta = st.sidebar.date_input("Semana a Consultar:", datetime.now().date())
nombre_hoja = obtener_nombre_hoja(fecha_consulta)

st.sidebar.markdown("---")

# Botón de Reiniciar Semana conectado al Backend
if st.sidebar.button("🔄 Reiniciar Semana", use_container_width=True, type="primary"):
    try:
        with st.spinner("Reiniciando semana en el servidor..."):
            response = requests.get(f"{WEB_APP_URL}?action=reset&sheet={nombre_hoja}", timeout=15)
            if response.status_code == 200:
                st.sidebar.success(f"¡La {nombre_hoja} ha sido reiniciada!")
                st.rerun()
            else:
                st.sidebar.error("No se pudo conectar con el servidor.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# --- 5. PANEL PRINCIPAL ---
st.markdown(f"<div class='main-header'>CENTRAL DE LOGÍSTICA — {nombre_hoja}</div>", unsafe_allow_html=True)

matriz_datos = obtener_matriz_hoja(nombre_hoja)

total_viajes = 0
peso_total_qq = 0.0
df_historial = pd.DataFrame()

if matriz_datos and len(matriz_datos) >= 30:
    filas_historial = matriz_datos[29:]
    df_historial = pd.DataFrame(filas_historial).dropna(how="all")
    if not df_historial.empty:
        df_historial.columns = ["COL_A", "COL_B", "MOTORISTA", "CANT. VIAJES", "RESERVADO POR", "PESO TOTAL", "FECHA", "DIRECCION"] + [f"C_{i}" for i in range(len(df_historial.columns)-8)]
        
        # Calculamos totales automáticamente desde los registros
        total_viajes = len(df_historial)
        for val in df_historial["PESO TOTAL"]:
            try:
                num_str = str(val).split("qq")[0].strip().replace(",", "")
                peso_total_qq += float(num_str)
            except:
                pass

# Tarjetas métricas actualizadas
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.markdown(f"<div class='metric-box'><span style='color: #64748b; font-size: 13px; font-weight: bold;'>TOTAL DE VIAJES</span><h2 style='color: #1f4e78; margin: 0;'>{total_viajes}</h2></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='metric-box'><span style='color: #64748b; font-size: 13px; font-weight: bold;'>PESO TOTAL (QQ)</span><h2 style='color: #b91c1c; margin: 0;'>{peso_total_qq:.2f}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. CUADRO VISUAL DE DISPONIBILIDAD (PESTAÑAS POR DÍA) ---
st.markdown("#### 📅 Disponibilidad de Espacio por Día")

dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO"]
tabs = st.tabs([f"📌 {d}" for d in dias])

for idx_dia, tab in enumerate(tabs):
    nombre_dia = dias[idx_dia]
    with tab:
        st.caption(f"Horarios y cupos disponibles para el día **{nombre_dia}**")
        
        col_m, col_t = st.columns(2)
        
        with col_m:
            st.markdown("##### 🌅 Mañana")
            for h in ["8:00 a.m.", "10:00 a.m."]:
                st.markdown(f"<div class='time-slot'>⏱️ {h}</div>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns(5)
                for c_idx, col in enumerate([c1, c2, c3, c4, c5]):
                    with col:
                        st.markdown(f"<div class='status-free'>Camión {c_idx+1}<br><small>Libre</small></div>", unsafe_allow_html=True)

        with col_t:
            st.markdown("##### 🌆 Tarde")
            if nombre_dia != "SÁBADO":
                for h in ["2:30 p.m.", "4:30 p.m."]:
                    st.markdown(f"<div class='time-slot'>⏱️ {h}</div>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    for c_idx, col in enumerate([c1, c2, c3, c4, c5]):
                        with col:
                            st.markdown(f"<div class='status-free'>Camión {c_idx+1}<br><small>Libre</small></div>", unsafe_allow_html=True)
            else:
                st.info("🚫 Tarde no laborable")

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- 7. TABLA DE REGISTROS DE DESPACHO ---
st.markdown("#### 📋 Despachos Agendados en la Semana")

if not df_historial.empty:
    st.dataframe(
        df_historial[["MOTORISTA", "CANT. VIAJES", "RESERVADO POR", "PESO TOTAL", "FECHA", "DIRECCION"]], 
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No hay fletes agendados aún para esta semana.")
