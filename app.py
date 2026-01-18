import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

import pandas as pd
import json
import tempfile

st.set_page_config(page_title="Gym App", layout="centered")
st.title("🏋️ Gym App")

# Scopes de Google
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
    f.write(st.secrets["GOOGLE_CREDS_FILE"])
    f_path = f.name
creds = Credentials.from_service_account_file(f_path, scopes=scopes)

gc = gspread.authorize(creds)

# Abrir la hoja de cálculo
sheet_id = "1meqhq0cp-n46Iq0T2RFIEc6eiJ3QZlfigBDnm477qGI"
sh = gc.open_by_key(sheet_id)

@st.cache_data(ttl=30)  # cada 30 segundos vuelve a cargar
def cargar_datos():
    worksheet = sh.sheet1
    return pd.DataFrame(worksheet.get_all_records())

data = cargar_datos()
st.dataframe(data)

st.title("🏋️ Gym App: Rutinas por día (vacías)")

# Definir las columnas que tendrá cada tabla
columnas = ["Ejercicios", "Series", "Reps"]

# Crear un DataFrame vacío por cada día
dias = ["Día 1", "Día 2", "Día 3", "Día 4"]
tablas_dias = {dia: pd.DataFrame(columns=["Ejercicios", "Series", "Reps", "Material", "Posicion", "Agarre"]) for dia in dias}

tabs = st.tabs(dias)

for i, dia in enumerate(dias):
    with tabs[i]:
        st.subheader(f"Rutina {dia}")

        # Partimos de toda la base de datos
        ejercicios_filtrados = data.copy()

        # --- Filtros en columnas ---
        col1, col2 = st.columns(2)
        with col1:
            musculo = st.selectbox(
                "Filtrar por músculo", ["Todos"] + sorted(data["Músculo"].unique()), key=f"{dia}-musculo"
            )
            if musculo != "Todos":
                ejercicios_filtrados = ejercicios_filtrados[ejercicios_filtrados["Músculo"] == musculo]

        with col2:
            busqueda = st.text_input("Buscar ejercicio", key=f"{dia}-busqueda")
            if busqueda:
                ejercicios_filtrados = ejercicios_filtrados[
                    ejercicios_filtrados["Ejercicios"].str.contains(busqueda, case=False)
                ]
        # Si se usa búsqueda, resetear todos los filtros
        if busqueda:
            musculo = "Todos"
            material = "Todos"
            posicion = "Todos"
            agarre = "Todos"

        col3, col4, col5 = st.columns(3)
        posiciones = sorted(ejercicios_filtrados["Posicion"].unique())
        agarres = sorted(ejercicios_filtrados["Agarre"].unique())
        materiales = sorted(ejercicios_filtrados["Material"].unique())

        with col3:
            material = st.selectbox("Filtrar por material", ["Todos"] + materiales, key=f"{dia}-material")
            if material != "Todos":
                ejercicios_filtrados = ejercicios_filtrados[ejercicios_filtrados["Material"] == material]

        with col4:
            posicion = st.selectbox("Filtrar por posición", ["Todos"] + posiciones, key=f"{dia}-posicion")
            if posicion != "Todos":
                ejercicios_filtrados = ejercicios_filtrados[ejercicios_filtrados["Posicion"] == posicion]

        with col5:
            agarre = st.selectbox("Filtrar por agarre", ["Todos"] + agarres, key=f"{dia}-agarre")
            if agarre != "Todos":
                ejercicios_filtrados = ejercicios_filtrados[ejercicios_filtrados["Agarre"] == agarre]

        # Mostrar DataFrame filtrado dinámicamente
        st.dataframe(ejercicios_filtrados)

        # Mostrar botón solo si queda exactamente 1 fila
        if len(ejercicios_filtrados) == 1:
            fila = ejercicios_filtrados.iloc[0]
            ejercicio = fila["Ejercicios"]
            st.write(f"Ejercicio seleccionado: **{ejercicio}**")

            # Inputs de series y reps
            series = st.number_input("Series", min_value=1, max_value=10, value=3, key=f"{dia}-series")
            reps = st.number_input("Reps", min_value=1, max_value=50, value=10, key=f"{dia}-reps")

            # Botón para agregar a tabla final
            if st.button("Agregar a rutina", key=f"{dia}-agregar"):
                nueva_fila = pd.DataFrame([{
                    "Ejercicios": ejercicio,
                    "Series": series,
                    "Reps": reps,
                    "Material": fila["Material"],
                    "Posicion": fila["Posicion"],
                    "Agarre": fila["Agarre"]
                }])
                tablas_dias[dia] = pd.concat([tablas_dias[dia], nueva_fila], ignore_index=True)
        elif len(ejercicios_filtrados) > 1:
            st.info(f"{len(ejercicios_filtrados)} ejercicios encontrados. Refina los filtros o la búsqueda para poder agregar uno solo.")
        else:
            st.warning("No se encontraron ejercicios con esos filtros.")

        # Mostrar tabla final del día
        st.dataframe(tablas_dias[dia])


