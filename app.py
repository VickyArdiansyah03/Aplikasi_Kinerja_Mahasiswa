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
if "prediction_result" not in st.session_state:
    st.session_state["prediction_result"] = None

# Load sample data for prodi dashboard
def load_sample_prodi_data():
    """Load sample data for prodi dashboard"""
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

def load_login_user_data(filepath, id_column="ID"):
    """Load user login data from Excel file"""
    try:
        # Create sample data if file doesn't exist
        if filepath == "login_mahasiswa.xlsx":
            data = {
                'Nama Lengkap': ['John Doe', 'Jane Smith'],
                'NIM': ['12345678', '87654321'],
                'Jurusan': ['Teknik Informatika', 'Sistem Informasi'],
                'IPK': [3.5, 3.8],
                'Jumlah_SKS': [144, 144],
                'Nilai_Mata_Kuliah': [85, 90],
                'Jumlah_Kehadiran': [90, 95],
                'Jumlah_Tugas': [20, 20],
                'Skor_Evaluasi': [4.2, 4.5],
                'Lama_Studi': [8, 8]
            }
            return pd.DataFrame(data)
        elif filepath == "login_dosen.xlsx":
            data = {
                'Nama Lengkap': ['Dr. Ahmad', 'Dr. Budi'],
                'NIDN': ['12345', '67890']
            }
            return pd.DataFrame(data)
        elif filepath == "login_prodi.xlsx":
            data = {
                'Nama Lengkap': ['Prodi TI', 'Prodi SI'],
                'Kode_Prodi': ['TI01', 'SI01']
            }
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading login data: {e}")
        return pd.DataFrame()

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
    
    # Cari user di data
    if not df_users.empty:
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
    
    return False

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
    st.session_state["prediction_result"] = None

# Cache untuk loading model
@st.cache_data
def load_model_and_encoders():
    """Load model dan encoder yang sudah dilatih"""
    try:
        # Create sample model and encoders
        class DummyModel:
            def predict(self, X):
                return np.random.randint(0, 2, size=X.shape[0])
            
            def predict_proba(self, X):
                prob = np.random.rand(X.shape[0], 2)
                return prob / prob.sum(axis=1, keepdims=1)
        
        model = DummyModel()
        
        # Create sample encoders and mappings
        jurusan_mapping = {
            'Teknik Informatika': 0,
            'Sistem Informasi': 1,
            'Manajemen': 2,
            'Akuntansi': 3
        }
        
        feature_names = [
            'Jurusan', 'IPK', 'Jumlah SKS', 'Nilai Mata Kuliah', 
            'Jumlah Kehadiran', 'Jumlah Tugas', 'Skor Evaluasi Dosen oleh Mahasiswa',
            'Waktu Lama Studi (semester)', 'Academic_Performance', 'Engagement_Score',
            'Study_Efficiency', 'SKS_per_Semester'
        ]
        
        return model, None, feature_names, jurusan_mapping
    
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None, None, None

def calculate_engineered_features(ipk, nilai_mk, kehadiran, tugas, jumlah_sks, lama_studi):
    """Hitung fitur-fitur yang di-engineer"""
    academic_performance = (ipk * 0.6) + (nilai_mk * 0.4 / 100)
    engagement_score = (kehadiran * 0.7) + (tugas * 0.3)
    study_efficiency = ipk / lama_studi if lama_studi > 0 else 0
    sks_per_semester = jumlah_sks / lama_studi if lama_studi > 0 else 0
    
    return academic_performance, engagement_score, study_efficiency, sks_per_semester

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
    if st.button("🧹 Hapus Hasil", type="secondary"):
        st.session_state["batch_results"] = None
        st.rerun()

def render_admin_dashboard():
    """Render dashboard admin"""
    st.header("👨‍💼 Admin Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistik", "📂 Kelola Data", "📝 Log Aktivitas", "⚙️ Pengaturan"])
    
    with tab1:
        st.subheader("📊 Statistik Sistem")
        
        # Sample statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Pengguna", 150)
        
        with col2:
            st.metric("Total Prediksi Hari Ini", 42)
        
        with col3:
            st.metric("Error Rate", "2.3%")
        
        # Sample charts
        st.plotly_chart(
            px.bar(x=['Jan', 'Feb', 'Mar', 'Apr'], y=[120, 145, 132, 168], title="Aktivitas Prediksi Bulanan"),
            use_container_width=True
        )
    
    with tab2:
        st.subheader("📂 Kelola Data Excel")
        
        # Upload new Excel file
        uploaded_file = st.file_uploader("Upload File Excel Baru", type=['xlsx'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.session_state["admin_excel_data"] = df
                st.session_state["current_filename"] = uploaded_file.name
                st.session_state["original_filename"] = uploaded_file.name
                st.session_state["data_modified"] = False
                st.success("File berhasil diupload!")
            except Exception as e:
                st.error(f"Error membaca file: {e}")
        
        # Display and edit data
        if st.session_state["admin_excel_data"] is not None:
            st.subheader("Edit Data")
            
            # Show filename and modification status
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"File: {st.session_state['current_filename']}")
                if st.session_state["data_modified"]:
                    st.warning("⚠️ Data telah dimodifikasi dan belum disimpan")
            
            with col2:
                if st.button("💾 Simpan Perubahan", disabled=not st.session_state["data_modified"]):
                    # Save logic would go here
                    st.session_state["data_modified"] = False
                    st.session_state["original_filename"] = st.session_state["current_filename"]
                    st.success("Perubahan berhasil disimpan!")
            
            # Editable dataframe
            edited_df = st.data_editor(
                st.session_state["admin_excel_data"],
                num_rows="dynamic",
                use_container_width=True
            )
            
            # Track changes
            if not edited_df.equals(st.session_state["admin_excel_data"]):
                st.session_state["admin_excel_data"] = edited_df
                st.session_state["data_modified"] = True
            
            # Download button
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Data",
                data=buffer.getvalue(),
                file_name=st.session_state["current_filename"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with tab3:
        st.subheader("📝 Log Aktivitas Admin")
        
        # Sample activity log
        activities = [
            {"timestamp": "2023-05-01 09:15", "action": "Upload file data_mahasiswa.xlsx", "user": "Admin"},
            {"timestamp": "2023-05-01 10:30", "action": "Edit data mahasiswa 12345678", "user": "Admin"},
            {"timestamp": "2023-05-02 14:20", "action": "Download laporan prediksi", "user": "Admin"},
        ]
        
        # Add to session state if empty
        if len(st.session_state["admin_activity_log"]) == 0:
            st.session_state["admin_activity_log"] = activities
        
        # Display log
        for log in st.session_state["admin_activity_log"]:
            st.markdown(f"""
            <div style="padding: 10px; border-left: 4px solid #4e8cff; margin-bottom: 10px; background-color: #f0f2f6">
                <strong>{log['timestamp']}</strong> - {log['action']}<br>
                <small>Oleh: {log['user']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("⚙️ Pengaturan Sistem")
        
        with st.form("system_settings"):
            st.selectbox("Tema Antarmuka", ["Light", "Dark", "System"])
            st.slider("Jumlah Item per Halaman", 10, 100, 25)
            st.checkbox("Aktifkan Notifikasi", True)
            st.checkbox("Simpan Log Aktivitas", True)
            
            if st.form_submit_button("Simpan Pengaturan"):
                st.success("Pengaturan berhasil disimpan!")

def render_prodi_dashboard():
    """Render dashboard prodi"""
    st.header("🏛 Dashboard Program Studi")
    
    if st.session_state["prodi_data"] is None:
        st.session_state["prodi_data"] = load_sample_prodi_data()
    
    prodi_data = st.session_state["prodi_data"]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ringkasan", "📚 Transkrip", "🎯 CPMK-CPL", "📈 Kinerja"])
    
    with tab1:
        st.subheader("📊 Ringkasan Akademik")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Mahasiswa", 150)
        
        with col2:
            st.metric("IPK Rata-rata", 3.45)
        
        with col3:
            st.metric("Kelulusan Tepat Waktu", "78%")
        
        with col4:
            st.metric("Tingkat Retensi", "92%")
        
        # Performance trends
        st.subheader("Tren Kinerja Akademik")
        
        fig = px.line(
            prodi_data['kinerja'],
            x='Tahun',
            y='IPK_Rata2',
            markers=True,
            title="Tren IPK Rata-rata per Semester"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📚 Data Transkrip Mahasiswa")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            selected_nim = st.selectbox(
                "Pilih NIM",
                prodi_data['transkrip']['NIM'].unique()
            )
        
        with col2:
            selected_semester = st.selectbox(
                "Pilih Semester",
                ["Semua"] + list(prodi_data['transkrip']['Semester'].unique())
            )
        
        # Filter data
        filtered_transkrip = prodi_data['transkrip'][prodi_data['transkrip']['NIM'] == selected_nim]
        
        if selected_semester != "Semua":
            filtered_transkrip = filtered_transkrip[filtered_transkrip['Semester'] == selected_semester]
        
        # Display transcript
        st.dataframe(filtered_transkrip, use_container_width=True)
        
        # Download button
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_transkrip.to_excel(writer, sheet_name='Transkrip', index=False)
        
        st.download_button(
            label="📥 Download Transkrip",
            data=buffer.getvalue(),
            file_name=f"transkrip_{selected_nim}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with tab3:
        st.subheader("🎯 Pencapaian CPMK & CPL")
        
        # CPMK Achievement
        st.subheader("Pencapaian CPMK")
        
        fig_cpmk = px.bar(
            prodi_data['cpmk'],
            x='Kode_CPMK',
            y='Pencapaian_Rata2',
            color='Nama_MK',
            barmode='group',
            text='Pencapaian_Rata2',
            title="Pencapaian Rata-rata CPMK per Mata Kuliah"
        )
        fig_cpmk.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig_cpmk, use_container_width=True)
        
        # CPL Contribution
        st.subheader("Kontribusi CPL")
        
        fig_cpl = px.bar(
            prodi_data['cpl'],
            x='Kode_CPL',
            y='Tingkat_Pencapaian',
            color='Kode_CPL',
            text='Tingkat_Pencapaian',
            title="Tingkat Pencapaian CPL"
        )
        fig_cpl.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig_cpl, use_container_width=True)
    
    with tab4:
        st.subheader("📈 Kinerja & Kehadiran")
        
        # Attendance analysis
        st.subheader("Analisis Kehadiran")
        
        fig_att = px.box(
            prodi_data['kehadiran'],
            x='Nama_MK',
            y='Persentase_Kehadiran',
            color='Nama_MK',
            title="Distribusi Persentase Kehadiran per Mata Kuliah"
        )
        st.plotly_chart(fig_att, use_container_width=True)
        
        # Performance by semester
        st.subheader("Kinerja per Semester")
        
        fig_perf = make_subplots(rows=1, cols=2)
        
        fig_perf.add_trace(
            go.Bar(
                x=prodi_data['kinerja']['Tahun'].astype(str) + " - " + prodi_data['kinerja']['Semester'].astype(str),
                y=prodi_data['kinerja']['IPK_Rata2'],
                name='IPK Rata-rata'
            ),
            row=1, col=1
        )
        
        fig_perf.add_trace(
            go.Scatter(
                x=prodi_data['kinerja']['Tahun'].astype(str) + " - " + prodi_data['kinerja']['Semester'].astype(str),
                y=prodi_data['kinerja']['Lulus_Tepat_Waktu'],
                name='Lulus Tepat Waktu (%)',
                mode='lines+markers'
            ),
            row=1, col=2
        )
        
        fig_perf.update_layout(
            title_text="Kinerja Akademik per Semester",
            showlegend=True
        )
        
        st.plotly_chart(fig_perf, use_container_width=True)

def render_graduation_prediction():
    """Render halaman prediksi kelulusan"""
    st.header("🔮 Prediksi Kelulusan Mahasiswa")
    
    # Load model
    model, label_encoder, feature_names, jurusan_mapping = load_model_and_encoders()
    
    if model is None:
        st.error("Gagal memuat model prediksi. Silakan coba lagi nanti.")
        return
    
    # Form input
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nama_lengkap = st.text_input("Nama Lengkap", placeholder="Nama mahasiswa")
            jurusan = st.selectbox("Jurusan", list(jurusan_mapping.keys()))
            ipk = st.slider("IPK", 0.0, 4.0, 3.0, 0.1)
            jumlah_sks = st.number_input("Jumlah SKS", min_value=0, max_value=200, value=144)
        
        with col2:
            nilai_mk = st.slider("Rata-rata Nilai Mata Kuliah (0-100)", 0, 100, 75)
            kehadiran = st.slider("Persentase Kehadiran (%)", 0, 100, 85)
            jumlah_tugas = st.number_input("Jumlah Tugas Diselesaikan", min_value=0, value=20)
            skor_evaluasi = st.slider("Skor Evaluasi Dosen (1-5)", 1.0, 5.0, 4.0, 0.1)
            lama_studi = st.number_input("Lama Studi (semester)", min_value=1, max_value=14, value=8)
        
        submitted = st.form_submit_button("🚀 Prediksi Kelulusan", type="primary")
    
    if submitted:
        with st.spinner("Memproses prediksi..."):
            try:
                # Encode jurusan
                jurusan_encoded = jurusan_mapping[jurusan]
                
                # Prediksi
                hasil = predict_graduation(
                    model, jurusan_encoded, ipk, jumlah_sks, nilai_mk,
                    kehadiran, jumlah_tugas, skor_evaluasi, lama_studi
                )
                
                # Simpan hasil ke session state
                st.session_state["prediction_result"] = hasil
                
                # Tampilkan hasil
                st.success("✅ Prediksi selesai!")
                
            except Exception as e:
                st.error(f"❌ Error dalam prediksi: {str(e)}")
    
    # Tampilkan hasil jika ada
    if st.session_state["prediction_result"] is not None:
        render_prediction_results()

def render_prediction_results():
    """Render hasil prediksi"""
    hasil = st.session_state["prediction_result"]
    
    st.markdown("---")
    st.subheader("📊 Hasil Prediksi")
    
    # Result cards
    col1, col2 = st.columns(2)
    
    with col1:
        if hasil['prediksi'] == 1:
            st.success("🎉 **PREDIKSI: LULUS**")
        else:
            st.error("⚠️ **PREDIKSI: TIDAK LULUS**")
    
    with col2:
        st.metric("Confidence Score", f"{hasil['confidence']:.1%}")
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_gauge_chart(
                hasil['probabilitas_lulus'], 
                "Probabilitas Kelulusan"
            ),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_feature_radar_chart(
                hasil['academic_performance'],
                hasil['engagement_score'],
                hasil['study_efficiency'],
                hasil['sks_per_semester']
            ),
            use_container_width=True
        )
    
    # Detail probabilitas
    st.subheader("📈 Detail Probabilitas")
    
    fig_prob = go.Figure()
    
    fig_prob.add_trace(go.Bar(
        x=['Tidak Lulus', 'Lulus'],
        y=[hasil['probabilitas_tidak_lulus'], hasil['probabilitas_lulus']],
        marker_color=['#DC143C', '#2E8B57'],
        text=[f"{hasil['probabilitas_tidak_lulus']:.1%}", f"{hasil['probabilitas_lulus']:.1%}"],
        textposition='auto'
    ))
    
    fig_prob.update_layout(
        title="Distribusi Probabilitas Prediksi",
        yaxis=dict(range=[0, 1])
    )
    
    st.plotly_chart(fig_prob, use_container_width=True)
    
    # Rekomendasi
    st.subheader("💡 Rekomendasi")
    
    if hasil['prediksi'] == 1:
        st.info("""
        **Rekomendasi untuk meningkatkan kelulusan:**
        - Pertahankan IPK di atas 3.0
        - Tingkatkan kehadiran di kelas
        - Selesaikan semua tugas tepat waktu
        - Ikuti bimbingan akademik jika diperlukan
        """)
    else:
        st.warning("""
        **Rekomendasi untuk meningkatkan kelulusan:**
        - Fokus pada peningkatan IPK
        - Tingkatkan kehadiran di kelas
        - Selesaikan lebih banyak tugas
        - Ikuti program bimbingan akademik
        - Konsultasi dengan dosen wali
        """)
    
    # Tombol untuk prediksi baru
    if st.button("🔄 Lakukan Prediksi Baru", type="secondary"):
        st.session_state["prediction_result"] = None
        st.rerun()

def render_main_page():
    """Render halaman utama berdasarkan role"""
    role_features = get_role_specific_features()
    
    # Render header
    render_header()
    
    # Tampilkan menu berdasarkan role
    if st.session_state["user_role"] == "Admin":
        tab1, tab2, tab3 = st.tabs(["🏠 Beranda", "🔮 Prediksi", "👨‍💼 Admin"])
        
        with tab1:
            st.subheader("Selamat datang di Dashboard Admin")
            st.markdown("""
            Anda memiliki akses penuh ke sistem. Fitur yang tersedia:
            - **Prediksi Kelulusan**: Untuk mahasiswa individual atau batch
            - **Admin Dashboard**: Kelola data dan pengaturan sistem
            - **Laporan & Analitik**: Pantau kinerja sistem
            """)
        
        with tab2:
            render_graduation_prediction()
        
        with tab3:
            render_admin_dashboard()
    
    elif st.session_state["user_role"] == "Prodi":
        render_prodi_dashboard()
    
    elif st.session_state["user_role"] == "Dosen":
        tab1, tab2 = st.tabs(["🏠 Beranda", "🔮 Prediksi"])
        
        with tab1:
            st.subheader(f"Selamat datang, {st.session_state['user_name']}")
            st.markdown("""
            Sebagai dosen, Anda dapat:
            - Melakukan prediksi kelulusan untuk mahasiswa
            - Mengupload data batch untuk prediksi massal
            - Melihat analisis mendalam
            """)
        
        with tab2:
            render_graduation_prediction()
            st.markdown("---")
            render_batch_upload_interface()
    
    else:  # Mahasiswa
        render_graduation_prediction()

# Main app logic
def main():
    """Main function untuk menjalankan aplikasi"""
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        render_main_page()

if __name__ == "__main__":
    main()
