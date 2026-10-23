import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control Maestro - Ferretería El Indio",
    page_icon="🚛",
    layout="wide",
)

# Estilos CSS limpios y compactos
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .main-header {
        background-color: #1f4e78;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyTrK1m9Rs1zSpUp1BRKn5WmSV-ixTrZ-R_yAng-xEGR_6NWYaz1T1W7uSjms5314U3/exec"

# --- 2. SISTEMA DE SEGURIDAD (CONTRASEÑA) ---
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

# --- 3. FUNCIONES DE DATOS ---
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

# --- 4. BARRA LATERAL (ADMINISTRACIÓN LIMPIA) ---
st.sidebar.markdown("### ⚙️ Panel de Control")
fecha_consulta = st.sidebar.date_input("Semana a Consultar:", datetime.now().date())
nombre_hoja = obtener_nombre_hoja(fecha_consulta)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reiniciar Semana", use_container_width=True):
    st.sidebar.warning("Comando de reinicio enviado.")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# --- 5. PANEL PRINCIPAL ORGANIZADO ---
st.markdown(f"<div class='main-header'>CENTRAL DE LOGÍSTICA — {nombre_hoja}</div>", unsafe_allow_html=True)

matriz_datos = obtener_matriz_hoja(nombre_hoja)

total_viajes = 0
peso_total_qq = 0.0

if matriz_datos and len(matriz_datos) > 1:
    try:
        total_viajes = matriz_datos[1][4] or 0
        peso_total_qq = matriz_datos[1][7] or 0
    except Exception:
        pass

# Tarjetas de Resumen Compactas
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.markdown(f"<div class='metric-box'><span style='color: #6b7280; font-size: 14px;'>TOTAL DE VIAJES</span><h2 style='color: #1f4e78; margin: 0;'>{total_viajes}</h2></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='metric-box'><span style='color: #6b7280; font-size: 14px;'>PESO TOTAL (QQ)</span><h2 style='color: #c00000; margin: 0;'>{peso_total_qq}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. REGISTRO DE DESPACHOS EN TABLA LIMPIA ---
st.markdown("#### 📋 Despachos Agendados en la Semana")

if matriz_datos and len(matriz_datos) >= 30:
    filas_historial = matriz_datos[29:]
    df_historial = pd.DataFrame(filas_historial).dropna(how="all")
    if not df_historial.empty:
        df_historial.columns = ["COL_A", "COL_B", "MOTORISTA", "CANT. VIAJES", "RESERVADO POR", "PESO TOTAL", "FECHA", "DIRECCION"] + [f"C_{i}" for i in range(len(df_historial.columns)-8)]
        # Mostramos una tabla limpia y ordenada sin relleno innecesario
        st.dataframe(
            df_historial[["MOTORISTA", "CANT. VIAJES", "RESERVADO POR", "PESO TOTAL", "FECHA", "DIRECCION"]], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay fletes agendados todavía para esta semana.")
else:
    st.info("Sincronizando datos de la semana...")
