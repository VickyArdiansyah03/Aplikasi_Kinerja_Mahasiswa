import streamlit as st
from utils.data import load_login_user_data
import pandas as pd

@st.cache_data
def load_login_user_data(filename, id_column="NIM"):
    try:
        df = pd.read_excel(filename)
        if id_column not in df.columns:
            raise ValueError("Kolom ID tidak ditemukan di file Excel")
        return df
    except Exception as e:
        st.error(f"Gagal memuat data login: {e}")
        return pd.DataFrame(columns=["Nama Lengkap", id_column])
 
def login(nama_user, id_user, selected_role):
    nama_user = nama_user.strip().lower()
    id_user = str(id_user).strip()
    selected_role = selected_role.lower()

    # Admin: hardcode
    if nama_user == "admin" and id_user == "00000" and selected_role == "admin":
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = "Admin"
        st.session_state["user_role"] = "Admin"
        st.session_state["user_id"] = "00000"
        return True

    # Mahasiswa
    if selected_role == "mahasiswa":
        df_users = load_login_user_data("login_mahasiswa.xlsx", id_column="NIM")
    elif selected_role == "dosen":
        df_users = load_login_user_data("login_dosen.xlsx", id_column="NIDN")
    elif selected_role == "prodi":
        df_users = load_login_user_data("login_prodi.xlsx", id_column="Kode_Prodi")
    else:
        return False
    
    # Cari user di file
    user_row = df_users[
        (df_users["Nama Lengkap"].str.strip().str.lower() == nama_user) &
        (df_users[df_users.columns[1]].astype(str) == id_user)  # Kolom ke-2 = NIM atau NIDN
    ]
    
    if not user_row.empty:
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = user_row.iloc[0]["Nama Lengkap"]
        st.session_state["user_role"] = selected_role.capitalize()
        st.session_state["user_nim"] = id_user
        return True
    else:
        return False

def logout():
    """Fungsi logout"""
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = ""
    st.session_state["user_role"] = ""
    st.session_state["batch_results"] = None

def get_role_specific_features():
    """Mendapatkan fitur berdasarkan role"""
    role = st.session_state["user_role"]
    
    if role == "Mahasiswa":
        return {
            "show_advanced_analysis": False,
            "show_admin_features": False,
            "show_batch_upload": False,
            "prediction_limit": 3,
            "title_suffix": "- Mode Mahasiswa",
            "show_excel_management": False
        }
    elif role == "Dosen":
        return {
            "show_advanced_analysis": True,
            "show_admin_features": False,
            "show_batch_upload": True,
            "prediction_limit": 10,
            "title_suffix": "- Mode Dosen",
            "show_excel_management": False
        }
    elif role == "Prodi":
        return {
            "show_advanced_analysis": False,
            "show_admin_features": False,
            "show_batch_upload": False,
            "prediction_limit": False,
            "title_suffix": "- Mode Prodi",
            "show_excel_management": False,
            "can_input_cpl_cpmk": True
        }
    else:  # Admin
        return {
            "show_advanced_analysis": True,
            "show_admin_features": True,
            "show_batch_upload": True,
            "prediction_limit": None,
            "title_suffix": "- Mode Admin",
            "show_excel_management": True
        }
 