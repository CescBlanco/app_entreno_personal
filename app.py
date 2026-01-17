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

worksheet = sh.sheet1
data = pd.DataFrame(worksheet.get_all_records())

st.dataframe(data)

