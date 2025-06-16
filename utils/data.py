import pandas as pd
import streamlit as st

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
    
def get_student_data(nama, nim):
    df_users = load_login_user_data("login_mahasiswa.xlsx")
    user_row = df_users[
        (df_users["Nama Lengkap"].str.strip().str.lower() == nama.strip().lower()) &
        (df_users["NIM"].astype(str) == str(nim).strip())
    ]
    return user_row.iloc[0] if not user_row.empty else None

def create_sample_template():
    """Buat template Excel untuk batch upload"""
    sample_data = {
        'Nama Lengkap': ['4', 'Jane Smith', 'Ahmad Rahman'],
        'NIM': ['12345678', '87654321', '11223344'],
        'Role': ['Mahasiswa', 'Mahasiswa', 'Mahasiswa'],
        'Jurusan': ['Teknik Informatika', 'Manajemen', 'Akuntansi'],
        'IPK': [3.5, 2.8, 3.2],
        'Jumlah_SKS': [144, 144, 144],
        'Nilai_Mata_Kuliah': [85, 70, 80],
        'Jumlah_Kehadiran': [90, 65, 85],
        'Jumlah_Tugas': [20, 12, 18],
        'Skor_Evaluasi': [4.2, 3.5, 4.0],
        'Lama_Studi': [8, 10, 8]
    }
    
    return pd.DataFrame(sample_data)
