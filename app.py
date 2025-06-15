import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Prediksi Kelulusan & Dashboard Prodi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "batch_results" not in st.session_state:
    st.session_state["batch_results"] = None
if "prodi_data" not in st.session_state:
    st.session_state["prodi_data"] = None
if "admin_excel_data" not in st.session_state:
    st.session_state["admin_excel_data"] = None
if "data_modified" not in st.session_state:
    st.session_state["data_modified"] = False
if "current_filename" not in st.session_state:
    st.session_state["current_filename"] = ""
if "original_filename" not in st.session_state:
    st.session_state["original_filename"] = ""
if "admin_activity_log" not in st.session_state:
    st.session_state["admin_activity_log"] = []

# Load sample data for prodi dashboard (in a real app, this would come from a database)
def load_sample_prodi_data():
    """Load sample data for prodi dashboard"""
    # Sample data for demonstration
    # In a real application, this would come from a database
    
    # Sample student transcripts
    transcript_data = {
        'NIM': ['12345678', '12345678', '12345678', '87654321', '87654321', '87654321'],
        'Nama': ['John Doe', 'John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Jane Smith'],
        'Kode_MK': ['MK101', 'MK102', 'MK103', 'MK101', 'MK102', 'MK103'],
        'Nama_MK': ['Pemrograman Dasar', 'Struktur Data', 'Basis Data', 
                    'Pemrograman Dasar', 'Struktur Data', 'Basis Data'],
        'SKS': [3, 3, 3, 3, 3, 3],
        'Nilai': ['A', 'B', 'A', 'B', 'C', 'A'],
        'Semester': [1, 2, 2, 1, 2, 2]
    }
    
    # Sample CPMK achievement data
    cpmk_data = {
        'Kode_MK': ['MK101', 'MK101', 'MK101', 'MK102', 'MK102', 'MK103', 'MK103'],
        'Nama_MK': ['Pemrograman Dasar', 'Pemrograman Dasar', 'Pemrograman Dasar',
                   'Struktur Data', 'Struktur Data', 'Basis Data', 'Basis Data'],
        'Kode_CPMK': ['CPMK1', 'CPMK2', 'CPMK3', 'CPMK1', 'CPMK2', 'CPMK1', 'CPMK2'],
        'Deskripsi_CPMK': [
            'Mampu membuat program sederhana', 
            'Mampu memahami struktur kontrol',
            'Mampu menggunakan fungsi',
            'Mampu mengimplementasikan struktur data linear',
            'Mampu menganalisis kompleksitas algoritma',
            'Mampu merancang basis data',
            'Mampu mengimplementasikan query SQL'
        ],
        'Pencapaian_Rata2': [85, 78, 82, 75, 70, 88, 85],
        'Target': [80, 80, 80, 75, 75, 85, 85]
    }
    
    # Sample CPL contribution data
    cpl_data = {
        'Kode_CPL': ['CPL1', 'CPL2', 'CPL3', 'CPL4'],
        'Deskripsi_CPL': [
            'Mampu mengembangkan perangkat lunak',
            'Mampu menganalisis kebutuhan sistem',
            'Mampu bekerja dalam tim',
            'Mampu berkomunikasi efektif'
        ],
        'Kontribusi_CPMK': [
            'CPMK1 (MK101), CPMK1 (MK102), CPMK1 (MK103)',
            'CPMK2 (MK101), CPMK2 (MK102)',
            'CPMK3 (MK101)',
            'CPMK2 (MK103)'
        ],
        'Tingkat_Pencapaian': [82, 76, 85, 83]
    }
    
    # Sample attendance data
    attendance_data = {
        'NIM': ['12345678', '12345678', '12345678', '87654321', '87654321', '87654321'],
        'Nama': ['John Doe', 'John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Jane Smith'],
        'Kode_MK': ['MK101', 'MK102', 'MK103', 'MK101', 'MK102', 'MK103'],
        'Nama_MK': ['Pemrograman Dasar', 'Struktur Data', 'Basis Data', 
                   'Pemrograman Dasar', 'Struktur Data', 'Basis Data'],
        'Pertemuan': [14, 14, 14, 14, 14, 14],
        'Hadir': [12, 10, 13, 11, 9, 12],
        'Persentase_Kehadiran': [86, 71, 93, 79, 64, 86]
    }
    
    # Sample academic performance data
    performance_data = {
        'Tahun': [2020, 2021, 2022, 2023],
        'Semester': [1, 2, 1, 2],
        'Jumlah_Mahasiswa': [120, 125, 130, 135],
        'IPK_Rata2': [3.2, 3.3, 3.4, 3.5],
        'Lulus_Tepat_Waktu': [75, 78, 80, 82],
        'Drop_Out': [5, 4, 3, 2]
    }
    
    return {
        'transkrip': pd.DataFrame(transcript_data),
        'cpmk': pd.DataFrame(cpmk_data),
        'cpl': pd.DataFrame(cpl_data),
        'kehadiran': pd.DataFrame(attendance_data),
        'kinerja': pd.DataFrame(performance_data)
    }

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
        (df_users[df_users.columns[1]].astype(str) == id_user)  # Kolom ke-2 = NIM/NIDN/Kode_Prodi
    ]
    
    if not user_row.empty:
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = user_row.iloc[0]["Nama Lengkap"]
        st.session_state["user_role"] = selected_role.capitalize()
        st.session_state["user_id"] = id_user
        
        # Load prodi data if logged in as prodi
        if selected_role == "prodi":
            st.session_state["prodi_data"] = load_sample_prodi_data()
        
        return True
    else:
        return False

def load_login_user_data(filepath, id_column="ID"):
    try:
        df = pd.read_excel(filepath)
        if id_column not in df.columns:
            st.warning(f"Kolom '{id_column}' tidak ditemukan.")
        return df
    except FileNotFoundError:
        st.error(f"File '{filepath}' tidak ditemukan.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data login: {e}")
        return pd.DataFrame()

def render_header():
    """Render header dengan info user dan logout"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🎓 Sistem Prediksi Kelulusan & Dashboard Prodi")
        st.caption(f"Selamat datang, *{st.session_state['user_name']}* ({st.session_state['user_role']})")
    
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            logout()
            st.rerun()

def logout():
    """Fungsi logout"""
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = ""
    st.session_state["user_role"] = ""
    st.session_state["batch_results"] = None
    st.session_state["prodi_data"] = None
    st.session_state["admin_excel_data"] = None
    st.session_state["data_modified"] = False
    st.session_state["current_filename"] = ""
    st.session_state["original_filename"] = ""
    st.session_state["admin_activity_log"] = []

# Cache untuk loading model
@st.cache_data
def load_model_and_encoders():
    """Load model dan encoder yang sudah dilatih"""
    try:
        # Load model
        with open('random_forest_graduation_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Load label encoder
        with open('jurusan_label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        # Load feature names
        with open('feature_names.pkl', 'rb') as f:
            feature_names = pickle.load(f)
        
        # Load jurusan mapping
        with open('jurusan_mapping.pkl', 'rb') as f:
            jurusan_mapping = pickle.load(f)
        
        return model, label_encoder, feature_names, jurusan_mapping
    
    except FileNotFoundError as e:
        st.error(f"File model tidak ditemukan: {e}")
        st.error("Pastikan file model sudah diupload ke direktori aplikasi")
        return None, None, None, None

def calculate_engineered_features(ipk, nilai_mk, kehadiran, tugas, jumlah_sks, lama_studi):
    """Hitung fitur-fitur yang di-engineer"""
    academic_performance = (ipk * 0.6) + (nilai_mk * 0.4 / 100)
    engagement_score = (kehadiran * 0.7) + (tugas * 0.3)
    study_efficiency = ipk / lama_studi if lama_studi > 0 else 0
    sks_per_semester = jumlah_sks / lama_studi if lama_studi > 0 else 0
    
    return academic_performance, engagement_score, study_efficiency, sks_per_semester

def get_student_data(nama, nim):
    df_users = load_login_user_data("login_mahasiswa.xlsx")
    user_row = df_users[
        (df_users["Nama Lengkap"].str.strip().str.lower() == nama.strip().lower()) &
        (df_users["NIM"].astype(str) == str(nim).strip())
    ]
    return user_row.iloc[0] if not user_row.empty else None

def predict_graduation(model, jurusan_encoded, ipk, jumlah_sks, nilai_mk, 
                      kehadiran, tugas, skor_evaluasi, lama_studi):
    """Fungsi untuk memprediksi kelulusan"""
    
    # Hitung fitur engineered
    academic_performance, engagement_score, study_efficiency, sks_per_semester = \
        calculate_engineered_features(ipk, nilai_mk, kehadiran, tugas, jumlah_sks, lama_studi)
    
    # Buat dataframe untuk prediksi
    data_prediksi = pd.DataFrame({
        'Jurusan': [jurusan_encoded],
        'IPK': [ipk],
        'Jumlah SKS': [jumlah_sks],
        'Nilai Mata Kuliah': [nilai_mk],
        'Jumlah Kehadiran': [kehadiran],
        'Jumlah Tugas': [tugas],
        'Skor Evaluasi Dosen oleh Mahasiswa': [skor_evaluasi],
        'Waktu Lama Studi (semester)': [lama_studi],
        'Academic_Performance': [academic_performance],
        'Engagement_Score': [engagement_score],
        'Study_Efficiency': [study_efficiency],
        'SKS_per_Semester': [sks_per_semester]
    })
    
    # Prediksi
    prediksi = model.predict(data_prediksi)[0]
    probabilitas = model.predict_proba(data_prediksi)[0]
    
    return {
        'prediksi': prediksi,
        'probabilitas_tidak_lulus': probabilitas[0],
        'probabilitas_lulus': probabilitas[1],
        'confidence': max(probabilitas),
        'academic_performance': academic_performance,
        'engagement_score': engagement_score,
        'study_efficiency': study_efficiency,
        'sks_per_semester': sks_per_semester
    }

def process_batch_data(df, model, jurusan_mapping):
    """Proses data batch untuk prediksi"""
    results = []
    
    for idx, row in df.iterrows():
        try:
            # Konversi jurusan ke encoded value
            jurusan_name = row['Jurusan']
            if jurusan_name not in jurusan_mapping:
                results.append({
                    'Index': idx,
                    'Nama Lengkap': row.get('Nama Lengkap', f'Mahasiswa_{idx}'),
                    'NIM': row.get('NIM', f'NIM_{idx}'),
                    'Jurusan': jurusan_name,
                    'Error': f'Jurusan "{jurusan_name}" tidak dikenal'
                })
                continue
            
            jurusan_encoded = jurusan_mapping[jurusan_name]
            
            # Ekstrak data
            ipk = float(row['IPK'])
            jumlah_sks = int(row['Jumlah_SKS'])
            nilai_mk = float(row['Nilai_Mata_Kuliah'])
            kehadiran = float(row['Jumlah_Kehadiran'])
            tugas = int(row['Jumlah_Tugas'])
            skor_evaluasi = float(row['Skor_Evaluasi'])
            lama_studi = int(row['Lama_Studi'])
            
            # Prediksi
            hasil = predict_graduation(
                model, jurusan_encoded, ipk, jumlah_sks, nilai_mk,
                kehadiran, tugas, skor_evaluasi, lama_studi
            )
            
            # Simpan hasil
            results.append({
                'Index': idx,
                'Nama Lengkap': row.get('Nama Lengkap', f'Mahasiswa_{idx}'),
                'NIM': row.get('NIM', f'NIM_{idx}'),
                'Jurusan': jurusan_name,
                'IPK': ipk,
                'Prediksi': 'LULUS' if hasil['prediksi'] == 1 else 'TIDAK LULUS',
                'Probabilitas_Lulus': hasil['probabilitas_lulus'],
                'Probabilitas_Tidak_Lulus': hasil['probabilitas_tidak_lulus'],
                'Confidence': hasil['confidence'],
                'Academic_Performance': hasil['academic_performance'],
                'Engagement_Score': hasil['engagement_score'],
                'Study_Efficiency': hasil['study_efficiency'],
                'SKS_per_Semester': hasil['sks_per_semester'],
                'Error': None
            })
            
        except Exception as e:
            results.append({
                'Index': idx,
                'Nama Lengkap': row.get('Nama Lengkap', f'Mahasiswa_{idx}'),
                'NIM': row.get('NIM', f'NIM_{idx}'),
                'Jurusan': row.get('Jurusan', 'Unknown'),
                'Error': str(e)
            })
    
    return pd.DataFrame(results)

def create_batch_summary_charts(df_results):
    """Buat chart summary untuk batch results"""
    # Filter data yang valid (tanpa error)
    valid_results = df_results[df_results['Error'].isna()]
    
    if len(valid_results) == 0:
        return None, None, None
    
    # Chart 1: Distribusi Prediksi
    prediksi_counts = valid_results['Prediksi'].value_counts()
    
    fig_pie = px.pie(
        values=prediksi_counts.values,
        names=prediksi_counts.index,
        title="Distribusi Prediksi Kelulusan",
        color_discrete_map={'LULUS': '#2E8B57', 'TIDAK LULUS': '#DC143C'}
    )
    
    # Chart 2: Distribusi per Jurusan
    # Prepare data for bar chart
    jurusan_prediksi = valid_results.groupby(['Jurusan', 'Prediksi']).size().reset_index(name='Count')
    
    fig_bar = px.bar(
        jurusan_prediksi,
        x='Jurusan',
        y='Count',
        color='Prediksi',
        title="Prediksi Kelulusan per Jurusan",
        color_discrete_map={'LULUS': '#2E8B57', 'TIDAK LULUS': '#DC143C'},
        barmode='group'
    )
    fig_bar.update_xaxes(tickangle=45)
    
    # Chart 3: Distribusi Confidence
    fig_hist = px.histogram(
        valid_results,
        x='Confidence',
        nbins=20,
        title="Distribusi Confidence Score",
        labels={'Confidence': 'Confidence Score', 'count': 'Jumlah Mahasiswa'}
    )
    
    return fig_pie, fig_bar, fig_hist

def create_sample_template():
    """Buat template Excel untuk batch upload"""
    sample_data = {
        'Nama Lengkap': ['John Doe', 'Jane Smith', 'Ahmad Rahman'],
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

def create_gauge_chart(value, title, max_val=1):
    """Membuat gauge chart untuk probabilitas"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.5], 'color': "lightgray"},
                {'range': [0.5, 1], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.5}}))
    
    fig.update_layout(height=300)
    return fig

def create_feature_radar_chart(academic_perf, engagement, study_eff, sks_per_sem):
    """Membuat radar chart untuk fitur-fitur engineered"""
    categories = ['Academic Performance', 'Engagement Score', 'Study Efficiency', 'SKS per Semester']
    
    # Normalisasi nilai untuk radar chart
    values = [
        min(academic_perf / 4.0, 1.0),  # Normalisasi academic performance
        min(engagement / 100, 1.0),     # Normalisasi engagement score
        min(study_eff / 0.5, 1.0),      # Normalisasi study efficiency
        min(sks_per_sem / 25, 1.0)      # Normalisasi SKS per semester
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Profil Mahasiswa'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        height=400
    )
    
    return fig

def render_login_page():
    """Render halaman login"""
    st.title("🔐 Login Sistem Akademik")
    st.markdown("---")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Masuk ke Sistem")
            
            with st.form("login_form"):
                nama_user = st.text_input("🧑 Nama Lengkap", placeholder="Masukkan nama lengkap")
                role = st.selectbox("👥 Masuk Sebagai", ["Mahasiswa", "Dosen", "Prodi", "Admin"])
                id_user = st.text_input("🆔 NIM/NIDN/Kode Prodi", placeholder="Masukkan ID Anda")
                
                submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                
                if submitted:
                    if login(nama_user, id_user, role):
                        st.success(f"✅ Selamat datang, {nama_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Nama atau ID tidak ditemukan di data pengguna.")
    
    # Informasi role
    st.markdown("---")
    st.markdown("### 📋 Akses Berdasarkan Role")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        👨‍🎓 Mahasiswa
        - Prediksi kelulusan pribadi
        - Melihat profil akademik
        - Transkrip nilai
        - Mendapat rekomendasi
        """)
    
    with col2:
        st.markdown("""
        👨‍🏫 Dosen
        - Prediksi untuk mahasiswa
        - Analisis mendalam
        - Tools evaluasi
        - Batch upload Excel
        """)
    
    with col3:
        st.markdown("""
        🏛 Prodi
        - Transkrip nilai mahasiswa
        - Laporan CPMK & CPL
        - Rekap nilai & absensi
        - Evaluasi kinerja akademik
        - Dashboard analitik
        """)
    
    with col4:
        st.markdown("""
        👨‍💼 Admin
        - Akses penuh sistem
        - Kelola data
        - Laporan statistik
        - Batch upload Excel
        """)

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
            "show_advanced_analysis": True,
            "show_admin_features": False,
            "show_batch_upload": False,
            "prediction_limit": None,
            "title_suffix": "- Mode Prodi",
            "show_excel_management": False
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

def render_batch_upload_interface():
    """Render interface untuk batch upload"""
    st.header("📂 Batch Upload & Prediksi")
    st.markdown("Upload file Excel berisi data mahasiswa untuk prediksi batch")
    
    # Load model
    model, label_encoder, feature_names, jurusan_mapping = load_model_and_encoders()
    
    if model is None:
        st.stop()
    
    # Template download
    st.subheader("📄 Download Template")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("💡 Download template Excel untuk memastikan format data yang benar")
        
        # Buat template
        template_df = create_sample_template()
        
        # Konversi ke Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='Template', index=False)
        
        st.download_button(
            label="📥 Download Template Excel",
            data=buffer.getvalue(),
            file_name=f"template_batch_prediksi_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    
    with col2:
        st.markdown("*Kolom yang diperlukan:*")
        required_columns = [
            "Nama Lengkap", "NIM", "Jurusan", "IPK", "Jumlah_SKS",
            "Nilai_Mata_Kuliah", "Jumlah_Kehadiran", "Jumlah_Tugas",
            "Skor_Evaluasi", "Lama_Studi"
        ]
        for col in required_columns:
            st.write(f"• {col}")
    
    # Upload file
    st.subheader("📤 Upload File Excel")
    uploaded_file = st.file_uploader(
        "Pilih file Excel (.xlsx)",
        type=['xlsx'],
        help="File Excel harus mengandung kolom sesuai template"
    )
    
    if uploaded_file is not None:
        try:
            # Baca file Excel
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File berhasil diupload! Ditemukan {len(df)} baris data")
            
            # Tampilkan preview data
            st.subheader("👀 Preview Data")
            st.dataframe(df.head(), use_container_width=True)
            
            # Validasi kolom
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Kolom yang hilang: {', '.join(missing_columns)}")
                return
            
            # Proses batch prediksi
            if st.button("🚀 Proses Batch Prediksi", type="primary"):
                with st.spinner("Memproses prediksi batch..."):
                    # Proses data
                    results_df = process_batch_data(df, model, jurusan_mapping)
                    
                    # Simpan hasil ke session state
                    st.session_state["batch_results"] = results_df
                    
                    st.success("✅ Batch prediksi selesai!")
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error membaca file: {str(e)}")
    
    # Tampilkan hasil jika ada
    if st.session_state["batch_results"] is not None:
        render_batch_results()

def render_batch_results():
    """Render hasil batch prediksi"""
    results_df = st.session_state["batch_results"]
    
    st.subheader("📊 Hasil Batch Prediksi")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_processed = len(results_df)
    valid_results = results_df[results_df['Error'].isna()]
    error_count = len(results_df[results_df['Error'].notna()])
    
    if len(valid_results) > 0:
        lulus_count = len(valid_results[valid_results['Prediksi'] == 'LULUS'])
        tidak_lulus_count = len(valid_results[valid_results['Prediksi'] == 'TIDAK LULUS'])
        avg_confidence = valid_results['Confidence'].mean()
    else:
        lulus_count = tidak_lulus_count = 0
        avg_confidence = 0
    
    with col1:
        st.metric("Total Diproses", total_processed)
    
    with col2:
        st.metric("Prediksi Lulus", lulus_count, delta=f"{lulus_count/len(valid_results)*100:.1f}%" if len(valid_results) > 0 else "0%")
    
    with col3:
        st.metric("Prediksi Tidak Lulus", tidak_lulus_count, delta=f"{tidak_lulus_count/len(valid_results)*100:.1f}%" if len(valid_results) > 0 else "0%")
    
    with col4:
        st.metric("Avg Confidence", f"{avg_confidence:.1%}" if avg_confidence > 0 else "0%")
    
    # Charts
    if len(valid_results) > 0:
        st.subheader("📈 Visualisasi Hasil")
        
        fig_pie, fig_bar, fig_hist = create_batch_summary_charts(results_df)
        
        if fig_pie is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.plotly_chart(fig_hist, use_container_width=True)
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed results
    st.subheader("📋 Hasil Detail")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        show_filter = st.selectbox(
            "Filter Results",
            ["Semua", "Hanya Lulus", "Hanya Tidak Lulus", "Hanya Error"]
        )
    
    with col2:
        if len(valid_results) > 0:
            jurusan_filter = st.selectbox(
                "Filter Jurusan",
                ["Semua"] + list(valid_results['Jurusan'].unique())
            )
        else:
            jurusan_filter = "Semua"
    
    # Apply filters
    filtered_df = results_df.copy()
    
    if show_filter == "Hanya Lulus":
        filtered_df = filtered_df[filtered_df['Prediksi'] == 'LULUS']
    elif show_filter == "Hanya Tidak Lulus":
        filtered_df = filtered_df[filtered_df['Prediksi'] == 'TIDAK LULUS']
    elif show_filter == "Hanya Error":
        filtered_df = filtered_df[filtered_df['Error'].notna()]
    
    if jurusan_filter != "Semua":
        filtered_df = filtered_df[filtered_df['Jurusan'] == jurusan_filter]
    
    # PERUBAHAN UTAMA: Hapus kolom Error untuk hasil yang sukses
    display_df = filtered_df.copy()
    
    # Jika bukan filter "Hanya Error", hilangkan kolom Error dari tampilan
    if show_filter != "Hanya Error":
        # Hanya tampilkan data yang tidak ada error
        display_df = display_df[display_df['Error'].isna()]
        # Hapus kolom Error dari tampilan
        if 'Error' in display_df.columns:
            display_df = display_df.drop(columns=['Error'])
    
    # Display filtered results
    st.dataframe(display_df, use_container_width=True)
    
    # Tampilkan pesan jika ada data dengan error (kecuali jika sedang filter error)
    if show_filter != "Hanya Error" and error_count > 0:
        st.warning(f"⚠️ {error_count} data mengalami error. Pilih filter 'Hanya Error' untuk melihat detail error.")
    
    # Download results
    if st.button("📥 Download Hasil ke Excel", type="secondary"):
        buffer = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Sheet 1: Hasil detail (tanpa error untuk data yang sukses)
            success_results = results_df[results_df['Error'].isna()].drop(columns=['Error'])
            error_results = results_df[results_df['Error'].notna()]
            
            # Sheet untuk hasil sukses
            if len(success_results) > 0:
                success_results.to_excel(writer, sheet_name='Hasil_Sukses', index=False)
            
            # Sheet untuk error (jika ada)
            if len(error_results) > 0:
                error_results.to_excel(writer, sheet_name='Data_Error', index=False)
            
            # Sheet 2: Summary
            if len(valid_results) > 0:
                summary_data = {
                    'Metrik': ['Total Diproses', 'Prediksi Lulus', 'Prediksi Tidak Lulus', 'Error Count', 'Avg Confidence'],
                    'Nilai': [total_processed, lulus_count, tidak_lulus_count, error_count, f"{avg_confidence:.1%}"]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name=f"hasil_batch_prediksi_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Clear results
    if st.button("🗑 Clear Results", type="secondary"):
        st.session_state["batch_results"] = None
        st.rerun()

def render_individual_prediction(model, jurusan_mapping, role_features):
    """Render interface prediksi individual"""
    st.sidebar.header("📝 Input Data Mahasiswa")

    if st.session_state["user_role"] == "Mahasiswa":
        user_data = get_student_data(
            st.session_state["user_name"],
            st.session_state.get("user_nim", ""),
        )

        if user_data is None:
            st.error("Data mahasiswa tidak ditemukan")
            st.stop()

        jurusan_selected = user_data["Jurusan"]
        jurusan_encoded = jurusan_mapping.get(jurusan_selected, 0)
        ipk = float(user_data["IPK"])
        jumlah_sks = int(user_data["Jumlah_SKS"])
        nilai_mk = float(user_data["Nilai_Mata_Kuliah"])
        kehadiran = float(user_data["Jumlah_Kehadiran"])
        tugas = int(user_data["Jumlah_Tugas"])
        skor_evaluasi = float(user_data["Skor_Evaluasi"])
        lama_studi = int(user_data["Lama_Studi"])

        # Tampilkan data mahasiswa di sidebar
        st.sidebar.markdown(f"**Nama:** {st.session_state['user_name']}")
        st.sidebar.markdown(f"**NIM:** {st.session_state.get('user_nim', '')}")
        st.sidebar.markdown(f"**Jurusan:** {jurusan_selected}")
        st.sidebar.markdown(f"**IPK:** {ipk}")
        st.sidebar.markdown(f"**SKS:** {jumlah_sks}")

    else:
        # Input manual untuk dosen/admin/prodi
        jurusan_selected = st.sidebar.selectbox(
            "Jurusan",
            options=list(jurusan_mapping.keys())
        )
        jurusan_encoded = jurusan_mapping[jurusan_selected]

        ipk = st.sidebar.slider(
            "IPK", min_value=0.0, max_value=4.0, value=3.0, step=0.1,
            help="Indeks Prestasi Kumulatif"
        )

        jumlah_sks = st.sidebar.number_input(
            "Jumlah SKS", min_value=0, max_value=200, value=144, step=1,
            help="Total SKS yang telah diambil"
        )

        nilai_mk = st.sidebar.slider(
            "Rata-rata Nilai Mata Kuliah", min_value=0, max_value=100, value=75, step=1,
            help="Nilai rata-rata mata kuliah dalam persentase"
        )

        kehadiran = st.sidebar.slider(
            "Persentase Kehadiran", min_value=0, max_value=100, value=85, step=1,
            help="Persentase kehadiran di kelas"
        )

        tugas = st.sidebar.number_input(
            "Jumlah Tugas Diselesaikan", min_value=0, max_value=50, value=15, step=1,
            help="Total tugas yang telah diselesaikan"
        )

        skor_evaluasi = st.sidebar.slider(
            "Skor Evaluasi Dosen", min_value=1.0, max_value=5.0, value=4.0, step=0.1,
            help="Skor evaluasi pengajaran oleh mahasiswa"
        )

        lama_studi = st.sidebar.number_input(
            "Lama Studi (Semester)", min_value=1, max_value=14, value=8, step=1,
            help="Jumlah semester yang telah ditempuh"
        )
        
        # Rekomendasi
        st.markdown("### 💡 Rekomendasi")
        if prediksi_label == "LULUS":
            st.success("""
            **Kamu berada di jalur yang tepat!**
            - Pertahankan IPK dan kehadiran
            - Fokus pada penyelesaian tugas akhir
            - Perbanyak pengalaman praktik melalui magang atau proyek
            """)
        else:
            st.error("""
            **Perlu peningkatan di beberapa aspek:**
            - Tingkatkan kehadiran di kelas
            - Perbaiki nilai mata kuliah yang rendah
            - Konsultasi dengan dosen wali untuk strategi studi
            - Manajemen waktu yang lebih baik
            """)
    
    # Tombol reset
    if st.button("🔄 Lakukan Prediksi Baru", type="secondary"):
        del st.session_state["prediction_result"]
        st.rerun()

def render_prodi_dashboard():
"""Render dashboard untuk prodi"""
if st.session_state["prodi_data"] is None:
st.error("Data prodi tidak tersedia")
return

data = st.session_state["prodi_data"]

st.header("📊 Dashboard Program Studi")
st.markdown("---")

# Tab untuk berbagai fitur
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Ringkasan", 
    "📚 Transkrip Nilai", 
    "🎯 CPMK & CPL", 
    "📊 Kinerja Akademik", 
    "🔄 Update Data"
])

with tab1:
    st.subheader("📈 Ringkasan Akademik")
    
    # Statistik utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Mahasiswa", 150)
    
    with col2:
        st.metric("IPK Rata-rata", 3.45)
    
    with col3:
        st.metric("Kelulusan Tepat Waktu", "78%")
    
    with col4:
        st.metric("Tingkat Retensi", "92%")
    
    # Grafik trend IPK
    st.subheader("Trend IPK per Semester")
    fig_ipk = px.line(
        data['kinerja'],
        x="Tahun",
        y="IPK_Rata2",
        color="Semester",
        markers=True,
        title="Perkembangan IPK Rata-rata"
    )
    st.plotly_chart(fig_ipk, use_container_width=True)
    
    # Distribusi nilai
    st.subheader("Distribusi Nilai")
    fig_dist = px.histogram(
        data['transkrip'],
        x="Nilai",
        color="Semester",
        barmode="group",
        title="Distribusi Nilai per Semester"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.subheader("📚 Data Transkrip Nilai")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        selected_nim = st.selectbox(
            "Pilih NIM",
            options=data['transkrip']['NIM'].unique()
        )
    
    with col2:
        selected_semester = st.selectbox(
            "Pilih Semester",
            options=["Semua"] + sorted(data['transkrip']['Semester'].unique().tolist())
        )
    
    # Filter data
    filtered_transkrip = data['transkrip'][data['transkrip']['NIM'] == selected_nim]
    if selected_semester != "Semua":
        filtered_transkrip = filtered_transkrip[filtered_transkrip['Semester'] == selected_semester]
    
    # Tampilkan data
    st.dataframe(filtered_transkrip, use_container_width=True)
    
    # Grafik nilai per semester
    st.subheader("Perkembangan Nilai per Semester")
    fig_nilai = px.line(
        filtered_transkrip,
        x="Semester",
        y="Nilai",
        color="Kode_MK",
        markers=True,
        title="Perkembangan Nilai per Mata Kuliah"
    )
    st.plotly_chart(fig_nilai, use_container_width=True)

with tab3:
    st.subheader("🎯 Pencapaian CPMK & CPL")
    
    # Pencapaian CPMK
    st.subheader("Pencapaian CPMK per Mata Kuliah")
    fig_cpmk = px.bar(
        data['cpmk'],
        x="Kode_CPMK",
        y="Pencapaian_Rata2",
        color="Kode_MK",
        barmode="group",
        text="Pencapaian_Rata2",
        title="Pencapaian Rata-rata CPMK"
    )
    fig_cpmk.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_cpmk, use_container_width=True)
    
    # Pencapaian CPL
    st.subheader("Pencapaian CPL")
    fig_cpl = px.bar(
        data['cpl'],
        x="Kode_CPL",
        y="Tingkat_Pencapaian",
        color="Kode_CPL",
        text="Tingkat_Pencapaian",
        title="Tingkat Pencapaian CPL"
    )
    fig_cpl.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_cpl, use_container_width=True)
    
    # Kontribusi CPMK ke CPL
    st.subheader("Kontribusi CPMK ke CPL")
    st.dataframe(data['cpl'][['Kode_CPL', 'Deskripsi_CPL', 'Kontribusi_CPMK']], use_container_width=True)

with tab4:
    st.subheader("📊 Kinerja Akademik")
    
    # Kehadiran
    st.subheader("Rekap Kehadiran")
    fig_kehadiran = px.box(
        data['kehadiran'],
        x="Kode_MK",
        y="Persentase_Kehadiran",
        color="Semester",
        title="Distribusi Persentase Kehadiran per Mata Kuliah"
    )
    st.plotly_chart(fig_kehadiran, use_container_width=True)
    
    # Kinerja akademik
    st.subheader("Kinerja Akademik per Tahun")
    fig_kinerja = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_kinerja.add_trace(
        go.Scatter(
            x=data['kinerja']['Tahun'].astype(str) + "-" + data['kinerja']['Semester'].astype(str),
            y=data['kinerja']['IPK_Rata2'],
            name="IPK Rata-rata"
        ),
        secondary_y=False
    )
    
    fig_kinerja.add_trace(
        go.Bar(
            x=data['kinerja']['Tahun'].astype(str) + "-" + data['kinerja']['Semester'].astype(str),
            y=data['kinerja']['Lulus_Tepat_Waktu'],
            name="% Lulus Tepat Waktu",
            opacity=0.5
        ),
        secondary_y=True
    )
    
    fig_kinerja.update_layout(
        title="Trend Kinerja Akademik",
        xaxis_title="Periode",
        yaxis_title="IPK Rata-rata",
        yaxis2_title="% Lulus Tepat Waktu"
    )
    
    st.plotly_chart(fig_kinerja, use_container_width=True)

with tab5:
    st.subheader("🔄 Update Data Prodi")
    
    # Upload file Excel baru
    uploaded_file = st.file_uploader(
        "Upload File Excel Data Terbaru",
        type=['xlsx'],
        help="File harus sesuai dengan format yang ditentukan"
    )
    
    if uploaded_file is not None:
        try:
            # Baca file Excel
            new_data = pd.read_excel(uploaded_file, sheet_name=None)
            
            # Validasi sheet yang diperlukan
            required_sheets = ['transkrip', 'cpmk', 'cpl', 'kehadiran', 'kinerja']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in new_data]
            
            if missing_sheets:
                st.error(f"Sheet berikut tidak ditemukan: {', '.join(missing_sheets)}")
            else:
                # Update data di session state
                st.session_state["prodi_data"] = {
                    'transkrip': new_data['transkrip'],
                    'cpmk': new_data['cpmk'],
                    'cpl': new_data['cpl'],
                    'kehadiran': new_data['kehadiran'],
                    'kinerja': new_data['kinerja']
                }
                
                st.success("Data berhasil diperbarui!")
                st.rerun()
        
        except Exception as e:
            st.error(f"Error membaca file: {str(e)}")

def render_admin_dashboard():
"""Render dashboard untuk admin"""
st.header("👨‍💼 Admin Dashboard")
st.markdown("---")

# Tab untuk berbagai fitur admin
tab1, tab2, tab3 = st.tabs([
    "📊 Statistik Sistem", 
    "📂 Kelola Data", 
    "📝 Log Aktivitas"
])

with tab1:
    st.subheader("📊 Statistik Pengguna Sistem")
    
    # Sample data - in a real app this would come from a database
    user_stats = {
        'Role': ['Mahasiswa', 'Dosen', 'Prodi', 'Admin'],
        'Jumlah': [1500, 85, 10, 3]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Pengguna", sum(user_stats['Jumlah']))
        st.metric("Mahasiswa Aktif", 1500)
        st.metric("Dosen Aktif", 85)
    
    with col2:
        fig_user = px.pie(
            user_stats,
            values='Jumlah',
            names='Role',
            title='Distribusi Pengguna'
        )
        st.plotly_chart(fig_user, use_container_width=True)
    
    # Aktivitas prediksi
    st.subheader("Aktivitas Prediksi")
    
    prediksi_stats = {
        'Hari': ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'],
        'Prediksi': [45, 78, 92, 65, 120, 15]
    }
    
    fig_prediksi = px.bar(
        prediksi_stats,
        x='Hari',
        y='Prediksi',
        title='Jumlah Prediksi per Hari'
    )
    st.plotly_chart(fig_prediksi, use_container_width=True)

with tab2:
    st.subheader("📂 Kelola Data Excel")
    
    # Upload file Excel
    uploaded_file = st.file_uploader(
        "Upload File Excel",
        type=['xlsx'],
        key="admin_upload"
    )
    
    if uploaded_file is not None:
        try:
            # Baca file Excel
            df = pd.read_excel(uploaded_file)
            st.session_state["admin_excel_data"] = df
            st.session_state["current_filename"] = uploaded_file.name
            st.session_state["original_filename"] = uploaded_file.name
            st.session_state["data_modified"] = False
            
            st.success(f"File {uploaded_file.name} berhasil diupload!")
            st.dataframe(df.head(), use_container_width=True)
        
        except Exception as e:
            st.error(f"Error membaca file: {str(e)}")
    
    # Edit data jika ada
    if st.session_state["admin_excel_data"] is not None:
        st.subheader("Edit Data")
        
        # Tampilkan nama file
        st.markdown(f"**File:** {st.session_state['current_filename']}")
        
        # Edit dataframe
        edited_df = st.data_editor(
            st.session_state["admin_excel_data"],
            num_rows="dynamic",
            use_container_width=True
        )
        
        # Tombol simpan
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Simpan Perubahan", type="primary"):
                st.session_state["admin_excel_data"] = edited_df
                st.session_state["data_modified"] = True
                st.success("Perubahan disimpan di memori!")
        
        with col2:
            new_filename = st.text_input(
                "Nama File Baru",
                value=st.session_state["current_filename"],
                help="Ganti nama file sebelum download"
            )
            
            if new_filename:
                st.session_state["current_filename"] = new_filename
        
        with col3:
            # Download file
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name=st.session_state["current_filename"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab3:
    st.subheader("📝 Log Aktivitas Admin")
    
    # Tombol clear log
    if st.button("🧹 Clear Log", type="secondary"):
        st.session_state["admin_activity_log"] = []
        st.rerun()
    
    # Tampilkan log
    if not st.session_state["admin_activity_log"]:
        st.info("Belum ada aktivitas yang tercatat")
    else:
        for log in reversed(st.session_state["admin_activity_log"]):
            st.markdown(f"""
            <div style='border-left: 3px solid #4a8fe7; padding-left: 10px; margin: 5px 0;'>
                <p style='margin: 0;'><strong>{log['timestamp']}</strong></p>
                <p style='margin: 0;'>{log['action']}</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Fungsi utama aplikasi"""
    if not st.session_state.get("logged_in", False):
        render_login_page()
    else:
        # Render header dengan info user
        render_header()

        # Dapatkan fitur berdasarkan role
        role_features = get_role_specific_features()

        # Load model dan encoders
        model, label_encoder, feature_names, jurusan_mapping = load_model_and_encoders()

        if model is None:
            st.error("Aplikasi tidak dapat berjalan tanpa model. Silakan hubungi administrator.")
            st.stop()

        # Tentukan tampilan berdasarkan role
        if st.session_state["user_role"] == "Prodi":
            render_prodi_dashboard()
        elif st.session_state["user_role"] == "Admin":
            render_admin_dashboard()
        else:
            # Mahasiswa atau Dosen
            st.header(f"🎓 Sistem Prediksi Kelulusan {role_features['title_suffix']}")

            # Tab untuk prediksi individual dan batch
            if role_features["show_batch_upload"]:
                tab1, tab2 = st.tabs(["🔍 Prediksi Individual", "📂 Batch Upload"])

                with tab1:
                    render_individual_prediction(model, jurusan_mapping, role_features)

                with tab2:
                    render_batch_upload_interface()
            else:
                render_individual_prediction(model, jurusan_mapping, role_features)


# Pemanggilan utama
if __name__ == "__main__":
    main()
