import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Kelulusan Mahasiswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'cpmk_data' not in st.session_state:
    st.session_state.cpmk_data = {
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

if 'cpl_data' not in st.session_state:
    st.session_state.cpl_data = {
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

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "batch_results" not in st.session_state:
    st.session_state["batch_results"] = None

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
        (df_users[df_users.columns[1]].astype(str) == id_user)  # Kolom ke-2 = NIM atau NIDN
    ]
    
    if not user_row.empty:
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = user_row.iloc[0]["Nama Lengkap"]
        st.session_state["user_role"] = selected_role.capitalize()
        st.session_state["user_nim"] = id_user
        st.session_state["df_users"] = df_users  
        return True
    else:
        return False

def logout():
    """Fungsi logout"""
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = ""
    st.session_state["user_role"] = ""
    st.session_state["batch_results"] = None

# Cache untuk loading model
@st.cache_data
def load_model_and_encoders():
    """Load model dan encoder yang sudah dilatih"""
    try:
        # Load model
        with open('random_forest_graduation_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Load label encoder
        with open('prodi_label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        # Load feature names
        with open('feature_names.pkl', 'rb') as f:
            feature_names = pickle.load(f)
        
        # Load prodi mapping
        with open('prodi_mapping.pkl', 'rb') as f:
            prodi_mapping = pickle.load(f)
        
        return model, label_encoder, feature_names, prodi_mapping
    
    except FileNotFoundError as e:
        st.error(f"File model tidak ditemukan: {e}")
        st.error("Pastikan file model sudah diupload ke direktori aplikasi")
        return None, None, None, None
    
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

def calculate_engineered_features(ipk, nilai_mk, kehadiran, tugas, jumlah_sks, lama_studi):
    """Hitung fitur-fitur yang di-engineer"""
    academic_performance = (ipk * 0.6) + (nilai_mk * 0.4 / 100)
    engagement_score = (kehadiran * 0.7) + (tugas * 0.3)
    study_efficiency = ipk / lama_studi if lama_studi > 0 else 0
    sks_per_semester = jumlah_sks / lama_studi if lama_studi > 0 else 0
    
    return academic_performance, engagement_score, study_efficiency, sks_per_semester

def get_student_data(nama, nim):
    if "df_users" not in st.session_state:
        st.error("Data pengguna belum dimuat. Silakan login kembali.")
        return None
    
    df_users = st.session_state["df_users"]

    user_row = df_users[
        (df_users["Nama Lengkap"].str.strip().str.lower() == nama.strip().lower()) &
        (df_users["NIM"].astype(str) == str(nim).strip())
    ]
    
    if not user_row.empty:
        required_columns = ["Nama Lengkap", "NIM", "Prodi", "IPK", "Jumlah_SKS", 
                            "Nilai_Mata_Kuliah", "Jumlah_Kehadiran", "Jumlah_Tugas", 
                            "Skor_Evaluasi", "Lama_Studi"]
        
        missing_columns = [col for col in required_columns if col not in df_users.columns]
        
        if missing_columns:
            st.error(f"Kolom yang hilang di file Excel: {', '.join(missing_columns)}")
            return None
        
        return user_row.iloc[0].to_dict()
    
    return None




def predict_graduation(model, prodi_encoded, ipk, jumlah_sks, nilai_mk, 
                      kehadiran, tugas, skor_evaluasi, lama_studi):
    """Fungsi untuk memprediksi kelulusan"""
    
    # Hitung fitur engineered
    academic_performance, engagement_score, study_efficiency, sks_per_semester = \
        calculate_engineered_features(ipk, nilai_mk, kehadiran, tugas, jumlah_sks, lama_studi)
    
    # Buat dataframe untuk prediksi
    data_prediksi = pd.DataFrame({
        'Prodi': [prodi_encoded],
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

def process_batch_data(df, model, prodi_mapping):
    """Proses data batch untuk prediksi"""
    results = []
    
    for idx, row in df.iterrows():
        try:
            # Konversi prodi ke encoded value   
            prodi_name = row['Prodi']
            if prodi_name not in prodi_mapping:
                results.append({
                    'Index': idx,
                    'Nama Lengkap': row.get('Nama Lengkap', f'Mahasiswa_{idx}'),
                    'NIM': row.get('NIM', f'NIM_{idx}'),
                    'Prodi': prodi_name,
                    'Error': f'Prodi "{prodi_name}" tidak dikenal'
                })
                continue
            
            prodi_encoded = prodi_mapping[prodi_name]
            
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
                model, prodi_encoded, ipk, jumlah_sks, nilai_mk,
                kehadiran, tugas, skor_evaluasi, lama_studi
            )
            
            # Simpan hasil
            results.append({
                'Index': idx,
                'Nama Lengkap': row.get('Nama Lengkap', f'Mahasiswa_{idx}'),
                'NIM': row.get('NIM', f'NIM_{idx}'),
                'Prodi': prodi_name,
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
                'Prodi': row.get('Prodi', 'Unknown'),
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
    
    # Chart 2: Distribusi per Prodi
    # Prepare data for bar chart
    prodi_prediksi = valid_results.groupby(['Prodi', 'Prediksi']).size().reset_index(name='Count')
    
    fig_bar = px.bar(
        prodi_prediksi,
        x='Prodi',
        y='Count',
        color='Prediksi',
        title="Prediksi Kelulusan per prodi",
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
        'Nama Lengkap': ['4', 'Jane Smith', 'Ahmad Rahman'],
        'NIM': ['12345678', '87654321', '11223344'],
        'Role': ['Mahasiswa', 'Mahasiswa', 'Mahasiswa'],
        'Prodi': ['Teknik Informatika', 'Manajemen', 'Akuntansi'],  # ← ubah dari 'prodi'
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
    st.title("🔐 Login Prediksi Kelulusan Mahasiswa")
    st.markdown("---")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Masuk ke Sistem")
            
            with st.form("login_form"):
                nama_user = st.text_input("🧑 Nama Lengkap", placeholder="Masukkan nama lengkap")
                role = st.selectbox("👥 Masuk Sebagai", ["Mahasiswa", "Dosen", "Admin", "Prodi"])
                id_user = st.text_input("🆔 NIM/NIDN", placeholder="Masukkan NIM/NIDN Anda")
                
                submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                
                if submitted:
                    if login(nama_user, id_user, role):
                        st.success(f"✅ Selamat datang, {nama_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Nama atau NIM tidak ditemukan di data pengguna.")
    
    # Informasi role
    st.markdown("---")
    st.markdown("### 📋 Akses Berdasarkan Role")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        👨‍🎓 Mahasiswa
        - Prediksi kelulusan pribadi
        - Melihat profil akademik
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
        👨‍💼 Admin
        - Akses penuh sistem
        - Kelola data
        - Laporan statistik
        - Batch upload Excel
        """)

    with col4:
        st.markdown("""
        📚 Prodi
        - Transkrip nilai mahasiswa
        - Laporan CPMK & CPL
        - Rekap nilai & absensi
        - Evaluasi kinerja akademik
        - Dashboard analitik
        """)

def render_prodi_dashboard():
    """Render dashboard khusus prodi"""
    role_features = get_role_specific_features()
    if role_features.get("can_input_cpl_cpmk"):
        # st.button("Tambah Data CPL/CPMK")    
        render_header(context="prodi_dashboard")
        st.markdown("---")
        
        # Load prodi data
        if "prodi_data" not in st.session_state:
            st.session_state["prodi_data"] = load_sample_prodi_data()
        
        prodi_data = st.session_state["prodi_data"]
        # Menu navigasi prodi
        menu_options = [
            "📊 Dashboard Utama",
            "📝 Transkrip Nilai Mahasiswa",
            "🎯 Laporan Ketercapaian CPMK",
            "📈 Kontribusi CPMK terhadap CPL",
            "✅ Rekap Nilai & Absensi",
            "Input Data CPL/CPMK"
        ]
        
        selected_menu = st.sidebar.selectbox("Menu Prodi", menu_options)
        
        if selected_menu == "📊 Dashboard Utama":
            render_prodi_main_dashboard(prodi_data)
        elif selected_menu == "📝 Transkrip Nilai Mahasiswa":
            render_transkrip_nilai(prodi_data)
        elif selected_menu == "🎯 Laporan Ketercapaian CPMK":
            render_cpmk_report(prodi_data)
        elif selected_menu == "📈 Kontribusi CPMK terhadap CPL":
            render_cpl_contribution(prodi_data)
        elif selected_menu == "✅ Rekap Nilai & Absensi":
            render_rekap_nilai_absensi(prodi_data)
        elif selected_menu == "📌 Evaluasi Kinerja Akademik":
            render_evaluasi_kinerja(prodi_data)
        elif selected_menu == "Input Data CPL/CPMK":
            render_input_cpl_cpmk()

def render_input_cpl_cpmk():
    st.header("Input CPL dan CPMK")

    with st.form("form_cpl_cpmk"):
        input_jenis = st.selectbox("Jenis Data", ["CPMK", "CPL"])
        kode = st.text_input("Kode", placeholder="Contoh: CPMK1 atau CPL1")
        deskripsi = st.text_area("Deskripsi")
        
        if input_jenis == "CPMK":
            kode_mk = st.text_input("Kode Mata Kuliah", placeholder="Contoh: MK101")
            mata_kuliah = st.text_input("Mata Kuliah Terkait", placeholder="Contoh: Pemrograman Dasar")
            target = st.slider("Target Pencapaian (%)", 0, 100, 80)
        else:
            kontribusi = st.text_area("Kontribusi CPMK", placeholder="Contoh: CPMK1 (MK101), CPMK2 (MK102)")

        submitted = st.form_submit_button("💾 Simpan")

        if submitted:
            # Validasi input
            if not kode.strip():
                st.error("❌ Kode harus diisi!")
                return
            
            if not deskripsi.strip():
                st.error("❌ Deskripsi harus diisi!")
                return

            if input_jenis == "CPMK":
                # Validasi untuk CPMK
                if not kode_mk.strip():
                    st.error("❌ Kode Mata Kuliah harus diisi!")
                    return
                
                if not mata_kuliah.strip():
                    st.error("❌ Nama Mata Kuliah harus diisi!")
                    return

                # Cek duplikasi CPMK
                existing_cpmk = [(mk, cpmk) for mk, cpmk in zip(
                    st.session_state.cpmk_data['Kode_MK'], 
                    st.session_state.cpmk_data['Kode_CPMK']
                )]
                
                if (kode_mk, kode) in existing_cpmk:
                    st.error(f"❌ CPMK {kode} untuk mata kuliah {kode_mk} sudah ada!")
                    return
    
                st.session_state.cpmk_data['Kode_MK'].append(kode_mk)
                st.session_state.cpmk_data['Nama_MK'].append(mata_kuliah)
                st.session_state.cpmk_data['Kode_CPMK'].append(kode)
                st.session_state.cpmk_data['Deskripsi_CPMK'].append(deskripsi)
                st.session_state.cpmk_data['Pencapaian_Rata2'].append(0)  # Default 0
                st.session_state.cpmk_data['Target'].append(target)

                st.success(f"✅ CPMK {kode} untuk mata kuliah {mata_kuliah} berhasil disimpan!")

            else:
                # Validasi untuk CPL
                if not kontribusi.strip():
                    st.error("❌ Kontribusi CPMK harus diisi!")
                    return
                
                # Cek duplikasi CPL
                if kode in st.session_state.cpl_data['Kode_CPL']:
                    st.error(f"❌ CPL {kode} sudah ada!")
                    return

                # Simpan data CPL
                st.session_state.cpl_data['Kode_CPL'].append(kode)
                st.session_state.cpl_data['Deskripsi_CPL'].append(deskripsi)
                st.session_state.cpl_data['Kontribusi_CPMK'].append(kontribusi)
                st.session_state.cpl_data['Tingkat_Pencapaian'].append(0)  # Default 0

                st.success(f"✅ CPL {kode} berhasil disimpan!")
    
    # Tampilkan data yang sudah tersimpan
    if st.session_state.cpmk_data['Kode_CPMK'] or st.session_state.cpl_data['Kode_CPL']:
        st.subheader("📋 Data Tersimpan")
        
        # Tampilkan data CPMK
        if st.session_state.cpmk_data['Kode_CPMK']:
            st.write("*Data CPMK:*")
            import pandas as pd
            df_cpmk = pd.DataFrame(st.session_state.cpmk_data)
            st.dataframe(df_cpmk, use_container_width=True)
        
        # Tampilkan data CPL
        if st.session_state.cpl_data['Kode_CPL']:
            st.write("*Data CPL:*")
            import pandas as pd
            df_cpl = pd.DataFrame(st.session_state.cpl_data)
            st.dataframe(df_cpl, use_container_width=True)

def render_prodi_main_dashboard(prodi_data):
    """Render dashboard utama prodi"""
    st.header(f"📊 Dashboard Prodi - {st.session_state['user_name']}")
    
    # Ringkasan statistik
    st.subheader("📌 Ringkasan Statistik")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_mahasiswa = prodi_data['transkrip']['NIM'].nunique()
        st.metric("Total Mahasiswa", total_mahasiswa)
    
    with col2:
        avg_ipk = prodi_data['kinerja']['IPK_Rata2'].mean()
        st.metric("IPK Rata-rata", f"{avg_ipk:.2f}")
    
    with col3:
        lulus_tepat_waktu = prodi_data['kinerja']['Lulus_Tepat_Waktu'].mean()
        st.metric("Lulus Tepat Waktu", f"{lulus_tepat_waktu:.1f}%")
    
    with col4:
        avg_attendance = prodi_data['kehadiran']['Persentase_Kehadiran'].mean()
        st.metric("Rata-rata Kehadiran", f"{avg_attendance:.1f}%")
    
    # Visualisasi data
    st.subheader("📈 Trend Kinerja Akademik")
    
    # IPK Trend
    fig_ipk = px.line(
        prodi_data['kinerja'],
        x='Tahun',
        y='IPK_Rata2',
        title='Trend IPK Rata-rata per Tahun',
        markers=True
    )
    fig_ipk.update_layout(yaxis_range=[2.5, 4.0])
    
    # Lulus Tepat Waktu Trend
    fig_lulus = px.line(
        prodi_data['kinerja'],
        x='Tahun',
        y='Lulus_Tepat_Waktu',
        title='Persentase Lulus Tepat Waktu',
        markers=True
    )
    fig_lulus.update_layout(yaxis_range=[50, 100])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_ipk, use_container_width=True)
    with col2:
        st.plotly_chart(fig_lulus, use_container_width=True)
    
    # Distribusi Nilai
    st.subheader("📊 Distribusi Nilai Mahasiswa")
    
    # Hitung distribusi nilai
    nilai_counts = prodi_data['transkrip']['Nilai'].value_counts().reset_index()
    nilai_counts.columns = ['Nilai', 'Jumlah']
    
    fig_nilai = px.bar(
        nilai_counts,
        x='Nilai',
        y='Jumlah',
        title='Distribusi Nilai',
        color='Nilai',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    st.plotly_chart(fig_nilai, use_container_width=True)
    
    # Pencapaian CPMK
    st.subheader("🎯 Pencapaian CPMK Terkini")
    
    cpmk_summary = prodi_data['cpmk'].groupby('Nama_MK').agg({
        'Pencapaian_Rata2': 'mean',
        'Target': 'mean'
    }).reset_index()
    
    fig_cpmk = go.Figure()
    
    fig_cpmk.add_trace(go.Bar(
        x=cpmk_summary['Nama_MK'],
        y=cpmk_summary['Pencapaian_Rata2'],
        name='Pencapaian',
        marker_color='#4CAF50'
    ))
    
    fig_cpmk.add_trace(go.Scatter(
        x=cpmk_summary['Nama_MK'],
        y=cpmk_summary['Target'],
        name='Target',
        mode='lines+markers',
        line=dict(color='red', width=2)
    ))
    
    fig_cpmk.update_layout(
        title='Pencapaian vs Target CPMK per Mata Kuliah',
        xaxis_title='Mata Kuliah',
        yaxis_title='Nilai',
        yaxis_range=[0, 100],
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_cpmk, use_container_width=True)

def render_transkrip_nilai(prodi_data):
    """Render halaman transkrip nilai mahasiswa"""
    st.header("📝 Transkrip Nilai Mahasiswa")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        selected_nim = st.selectbox(
            "Pilih NIM Mahasiswa",
            options=prodi_data['transkrip']['NIM'].unique(),
            format_func=lambda x: f"{x} - {prodi_data['transkrip'][prodi_data['transkrip']['NIM'] == x]['Nama'].iloc[0]}"
        )
    
    with col2:
        selected_semester = st.selectbox(
            "Filter Semester",
            options=["Semua"] + sorted(prodi_data['transkrip']['Semester'].unique())
        )
    
    # Filter data
    filtered_data = prodi_data['transkrip'][prodi_data['transkrip']['NIM'] == selected_nim]
    
    if selected_semester != "Semua":
        filtered_data = filtered_data[filtered_data['Semester'] == selected_semester]
    
    # Tampilkan data mahasiswa
    mahasiswa_info = filtered_data.iloc[0]
    
    st.subheader(f"📋 Profil Akademik - {mahasiswa_info['Nama']} (NIM: {mahasiswa_info['NIM']})")
    
    # Hitung IPK (contoh sederhana)
    nilai_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0}
    filtered_data['Nilai_Angka'] = filtered_data['Nilai'].map(nilai_map)
    ipk = (filtered_data['Nilai_Angka'] * filtered_data['SKS']).sum() / filtered_data['SKS'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total SKS", filtered_data['SKS'].sum())
    with col2:
        st.metric("IPK", f"{ipk:.2f}")
    with col3:
        nilai_a = len(filtered_data[filtered_data['Nilai'] == 'A'])
        st.metric("Nilai A", nilai_a)
    
    # Tampilkan transkrip
    st.subheader("📜 Transkrip Nilai")
    
    # Sort by semester
    transkrip_display = filtered_data.sort_values('Semester')
    
    # Convert to grade points for visualization
    transkrip_display['Nilai_Poin'] = transkrip_display['Nilai'].map(nilai_map)
    
    # Tampilkan tabel
    st.dataframe(
        transkrip_display[['Kode_MK', 'Nama_MK', 'SKS', 'Nilai', 'Semester']],
        use_container_width=True,
        hide_index=True
    )
    
    # Visualisasi performa per semester
    st.subheader("📈 Grafik Perkembangan Akademik")
    
    fig = px.bar(
        transkrip_display,
        x='Semester',
        y='Nilai_Poin',
        color='Nama_MK',
        title='Nilai per Semester',
        labels={'Nilai_Poin': 'Nilai (dalam angka)'},
        hover_data=['Nama_MK', 'Nilai'],
        height=400
    )
    
    fig.update_layout(yaxis_range=[0, 4])
    st.plotly_chart(fig, use_container_width=True)
    
    # Download transkrip
    st.subheader("📥 Export Data")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        transkrip_display.to_excel(writer, sheet_name='Transkrip', index=False)
    
    st.download_button(
        label="📥 Download Transkrip (Excel)",
        data=buffer,
        file_name=f"transkrip_{mahasiswa_info['NIM']}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def render_cpmk_report(prodi_data):
    """Render laporan ketercapaian CPMK"""
    st.header("🎯 Laporan Ketercapaian CPMK per Mata Kuliah")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
       selected_mk = st.selectbox(
    "Pilih Mata Kuliah",
    options=["Semua"] + list(prodi_data['kehadiran']['Nama_MK'].unique())
)

    
    with col2:
        threshold = st.slider(
            "Threshold Pencapaian (%)",
            min_value=0,
            max_value=100,
            value=75,
            help="Nilai minimal untuk dianggap tercapai"
        )
    
    # Filter data
    if selected_mk == "Semua":
        filtered_cpmk = prodi_data['cpmk']
    else:
        filtered_cpmk = prodi_data['cpmk'][prodi_data['cpmk']['Nama_MK'] == selected_mk]
    
    # Hitung status pencapaian
    filtered_cpmk['Status'] = filtered_cpmk['Pencapaian_Rata2'] >= threshold
    filtered_cpmk['Status'] = filtered_cpmk['Status'].map({True: 'Tercapai', False: 'Belum Tercapai'})
    
    # Tampilkan data
    st.subheader("📋 Data Ketercapaian CPMK")
    st.dataframe(
        filtered_cpmk,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualisasi
    st.subheader("📊 Grafik Ketercapaian CPMK")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart pencapaian vs target
        fig_bar = px.bar(
            filtered_cpmk,
            x='Kode_CPMK',
            y=['Pencapaian_Rata2', 'Target'],
            barmode='group',
            title='Pencapaian vs Target CPMK',
            labels={'value': 'Nilai', 'variable': 'Kategori'},
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart status pencapaian
        status_counts = filtered_cpmk['Status'].value_counts().reset_index()
        fig_pie = px.pie(
            status_counts,
            values='count',
            names='Status',
            title='Status Pencapaian CPMK',
            color='Status',
            color_discrete_map={'Tercapai': '#4CAF50', 'Belum Tercapai': '#F44336'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Analisis
    st.subheader("🔍 Analisis Ketercapaian")
    
    tercapai = len(filtered_cpmk[filtered_cpmk['Status'] == 'Tercapai'])
    total_cpmk = len(filtered_cpmk)
    persentase_tercapai = (tercapai / total_cpmk) * 100
    
    st.metric(
        "Persentase CPMK Tercapai", 
        f"{persentase_tercapai:.1f}%",
        delta=f"{tercapai} dari {total_cpmk} CPMK"
    )
    
    # Rekomendasi untuk CPMK yang belum tercapai
    if not filtered_cpmk[filtered_cpmk['Status'] == 'Belum Tercapai'].empty:
        st.warning("⚠ Beberapa CPMK Belum Tercapai:")
        for idx, row in filtered_cpmk[filtered_cpmk['Status'] == 'Belum Tercapai'].iterrows():
            gap = row['Target'] - row['Pencapaian_Rata2']
            st.write(f"""
            - {row['Kode_CPMK']}: {row['Deskripsi_CPMK']}  
              Pencapaian: {row['Pencapaian_Rata2']}% (Target: {row['Target']}%, Gap: {gap:.1f}%)  
              💡 Rekomendasi: Perbaikan metode pembelajaran dan evaluasi untuk CPMK ini
            """)

def render_cpl_contribution(prodi_data):
    """Render laporan kontribusi CPMK terhadap CPL"""
    st.header("📈 Kontribusi CPMK terhadap CPL")
    
    # Tampilkan data CPL
    st.subheader("📋 Data Capaian Pembelajaran Lulusan (CPL)")
    
    # Hitung rata-rata pencapaian per CPL
    cpl_display = prodi_data['cpl'].copy()
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart pencapaian CPL
        fig_bar = px.bar(
            cpl_display,
            x='Kode_CPL',
            y='Tingkat_Pencapaian',
            color='Kode_CPL',
            title='Tingkat Pencapaian CPL',
            labels={'Tingkat_Pencapaian': 'Pencapaian (%)'},
            height=400
        )
        fig_bar.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Sunburst chart kontribusi CPMK ke CPL
        # Buat mapping dari data
        cpmk_cpl = []
        for _, row in cpl_display.iterrows():
            contributions = row['Kontribusi_CPMK'].split(',')
            for contrib in contributions:
                contrib = contrib.strip()
                if '(' in contrib:
                    cpmk = contrib.split('(')[0].strip()
                    mk = contrib.split('(')[1].replace(')', '').strip()
                    cpmk_cpl.append({
                        'CPL': row['Kode_CPL'],
                        'CPMK': cpmk,
                        'MK': mk,
                        'Pencapaian': row['Tingkat_Pencapaian']
                    })
        
        if cpmk_cpl:  # Hanya buat chart jika ada data
            df_sunburst = pd.DataFrame(cpmk_cpl)
            
            fig_sunburst = px.sunburst(
                df_sunburst,
                path=['CPL', 'MK', 'CPMK'],
                values=[1]*len(df_sunburst),  # Equal size untuk semua
                title='Hubungan CPMK ke CPL',
                height=500
            )
            st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Tampilkan detail CPL
    st.subheader("📝 Detail Kontribusi CPMK ke CPL")
    
    for _, row in cpl_display.iterrows():
        with st.expander(f"{row['Kode_CPL']}: {row['Deskripsi_CPL']}"):
            st.write(f"Tingkat Pencapaian: {row['Tingkat_Pencapaian']}%")
            st.write("Kontribusi CPMK:")
            
            contributions = row['Kontribusi_CPMK'].split(',')
            for contrib in contributions:
                contrib = contrib.strip()
                st.write(f"- {contrib}")
            
            # Analisis
            if row['Tingkat_Pencapaian'] < 75:
                st.error("🔴 Pencapaian di bawah standar (minimal 75%)")
                st.write("""
                Rekomendasi Perbaikan:
                - Evaluasi kontribusi CPMK terkait
                - Perbaikan metode pembelajaran
                - Penyesuaian bobot kontribusi
                """)
            elif row['Tingkat_Pencapaian'] < 85:
                st.warning("🟡 Pencapaian memadai tetapi masih bisa ditingkatkan")
            else:
                st.success("🟢 Pencapaian sangat baik")

def render_rekap_nilai_absensi(prodi_data):
    """Render rekap nilai dan absensi"""
    st.header("✅ Rekap Nilai dan Absensi")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        selected_mk = st.selectbox(
            "Pilih Mata Kuliah",
            options=["Semua"] + list(prodi_data['kehadiran']['Nama_MK'].unique())
        )
        
    with col2:
        attendance_threshold = st.slider(
            "Threshold Kehadiran Minimal (%)",
            min_value=0,
            max_value=100,
            value=75,
            help="Batas minimal kehadiran untuk dianggap memenuhi syarat"
        )
    
    # Filter data
    if selected_mk == "Semua":
        filtered_attendance = prodi_data['kehadiran']
        filtered_grades = prodi_data['transkrip']
    else:
        filtered_attendance = prodi_data['kehadiran'][prodi_data['kehadiran']['Nama_MK'] == selected_mk]
        filtered_grades = prodi_data['transkrip'][prodi_data['transkrip']['Nama_MK'] == selected_mk]
    
    # Gabungkan data nilai dan absensi
    merged_data = pd.merge(
        filtered_grades,
        filtered_attendance,
        on=['NIM', 'Nama', 'Kode_MK', 'Nama_MK'],
        how='left'
    )
    
    # Hitung status kehadiran
    merged_data['Status_Kehadiran'] = merged_data['Persentase_Kehadiran'] >= attendance_threshold
    merged_data['Status_Kehadiran'] = merged_data['Status_Kehadiran'].map({True: 'Memenuhi', False: 'Tidak Memenuhi'})
    
    # Tampilkan data
    st.subheader("📋 Data Nilai dan Kehadiran")
    st.dataframe(
        merged_data,
        use_container_width=True,
        column_order=['NIM', 'Nama', 'Kode_MK', 'Nama_MK', 'Nilai', 'Persentase_Kehadiran', 'Status_Kehadiran'],
        hide_index=True
    )
    
    # Visualisasi
    st.subheader("📊 Analisis Hubungan Kehadiran dan Nilai")
    
    # Convert grades to points for correlation analysis
    nilai_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0}
    merged_data['Nilai_Poin'] = merged_data['Nilai'].map(nilai_map)
    
    # Scatter plot
    fig_scatter = px.scatter(
        merged_data,
        x='Persentase_Kehadiran',
        y='Nilai_Poin',
        color='Status_Kehadiran',
        title='Hubungan Kehadiran dan Nilai',
        labels={'Persentase_Kehadiran': 'Kehadiran (%)', 'Nilai_Poin': 'Nilai (dalam angka)'},
        hover_data=['Nama', 'Nilai'],
        color_discrete_map={'Memenuhi': '#4CAF50', 'Tidak Memenuhi': '#F44336'}
    )
    
    fig_scatter.update_layout(
        yaxis=dict(tickvals=[0, 1, 2, 3, 4], ticktext=['E', 'D', 'C', 'B', 'A']),
        yaxis_range=[-0.5, 4.5]
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Hitung korelasi
    correlation = merged_data['Persentase_Kehadiran'].corr(merged_data['Nilai_Poin'])
    
    # Box plot per nilai
    fig_box = px.box(
        merged_data,
        x='Nilai',
        y='Persentase_Kehadiran',
        title='Distribusi Kehadiran per Nilai',
        color='Nilai'
    )
    
    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Korelasi Kehadiran-Nilai",
            f"{correlation:.2f}",
            help="Nilai mendekati 1 menunjukkan korelasi positif yang kuat"
        )
    
    with col2:
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Analisis
    st.subheader("🔍 Temuan Utama")
    
    # Mahasiswa dengan kehadiran rendah tapi nilai baik
    anomaly = merged_data[
        (merged_data['Status_Kehadiran'] == 'Tidak Memenuhi') & 
        (merged_data['Nilai'].isin(['A', 'B']))
    ]
    
    if not anomaly.empty:
        st.warning(f"⚠ {len(anomaly)} mahasiswa memiliki kehadiran rendah tetapi nilai baik:")
        st.dataframe(
            anomaly[['NIM', 'Nama', 'Nama_MK', 'Nilai', 'Persentase_Kehadiran']],
            use_container_width=True,
            hide_index=True
        )
        st.write("""
        Interpretasi:
        - Kemungkinan mahasiswa mampu belajar mandiri
        - Atau perlu pemeriksaan validitas data kehadiran
        """)
    
    # Mahasiswa dengan kehadiran baik tapi nilai buruk
    anomaly2 = merged_data[
        (merged_data['Status_Kehadiran'] == 'Memenuhi') & 
        (merged_data['Nilai'].isin(['D', 'E']))
    ]
    
    if not anomaly2.empty:
        st.error(f"❌ {len(anomaly2)} mahasiswa hadir tetapi masih kesulitan:")
        st.dataframe(
            anomaly2[['NIM', 'Nama', 'Nama_MK', 'Nilai', 'Persentase_Kehadiran']],
            use_container_width=True,
            hide_index=True
        )
        st.write("""
        Rekomendasi:
        - Perlu pendekatan pembelajaran berbeda
        - Konseling akademik
        - Evaluasi metode pengajaran
        """)

def render_evaluasi_kinerja(prodi_data):
    """Render evaluasi kinerja akademik kolektif"""
    st.header("📌 Evaluasi Kinerja Akademik Prodi")
    
    # Ringkasan statistik
    st.subheader("📊 Indikator Kinerja Utama")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_ipk = prodi_data['kinerja']['IPK_Rata2'].mean()
        st.metric("IPK Rata-rata", f"{avg_ipk:.2f}")
    
    with col2:
        lulus_tepat_waktu = prodi_data['kinerja']['Lulus_Tepat_Waktu'].mean()
        st.metric("Lulus Tepat Waktu", f"{lulus_tepat_waktu:.1f}%")
    
    with col3:
        drop_out = prodi_data['kinerja']['Drop_Out'].mean()
        st.metric("Tingkat Drop Out", f"{drop_out:.1f}%")
    
    # Trend kinerja
    st.subheader("📈 Trend Kinerja per Tahun")
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    
    # IPK Trend
    fig.add_trace(
        go.Scatter(
            x=prodi_data['kinerja']['Tahun'],
            y=prodi_data['kinerja']['IPK_Rata2'],
            name='IPK Rata-rata',
            mode='lines+markers'
        ),
        row=1, col=1
    )
    
    # Lulus Tepat Waktu Trend
    fig.add_trace(
        go.Scatter(
            x=prodi_data['kinerja']['Tahun'],
            y=prodi_data['kinerja']['Lulus_Tepat_Waktu'],
            name='Lulus Tepat Waktu (%)',
            mode='lines+markers'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="Trend Kinerja Akademik",
        showlegend=True
    )
    
    fig.update_yaxes(title_text="IPK", row=1, col=1)
    fig.update_yaxes(title_text="Persentase", row=2, col=1)
    fig.update_xaxes(title_text="Tahun", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Benchmarking
    st.subheader("🏆 Benchmarking dengan Standar")
    
    benchmark_data = {
        'Indikator': ['IPK Rata-rata', 'Lulus Tepat Waktu', 'Tingkat Drop Out'],
        'Nilai Prodi': [avg_ipk, lulus_tepat_waktu, drop_out],
        'Standar Nasional': [3.0, 70, 5],
        'Standar Universitas': [3.25, 75, 3]
    }
    
    benchmark_df = pd.DataFrame(benchmark_data)
    
    # Tampilkan tabel benchmark
    st.dataframe(
        benchmark_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualisasi benchmark
    fig_bench = go.Figure()
    
    fig_bench.add_trace(go.Bar(
        x=benchmark_df['Indikator'],
        y=benchmark_df['Nilai Prodi'],
        name='Prodi Kita',
        marker_color='#4CAF50'
    ))
    
    fig_bench.add_trace(go.Bar(
        x=benchmark_df['Indikator'],
        y=benchmark_df['Standar Universitas'],
        name='Standar Universitas',
        marker_color='#FFC107'
    ))
    
    fig_bench.add_trace(go.Bar(
        x=benchmark_df['Indikator'],
        y=benchmark_df['Standar Nasional'],
        name='Standar Nasional',
        marker_color='#F44336'
    ))
    
    fig_bench.update_layout(
        barmode='group',
        title='Perbandingan dengan Standar',
        yaxis_title='Nilai'
    )
    
    st.plotly_chart(fig_bench, use_container_width=True)
    
    # Analisis SWOT
    st.subheader("🔍 Analisis SWOT Prodi")
    
    swot_col1, swot_col2 = st.columns(2)
    
    with swot_col1:
        st.markdown("""
        💪 Kekuatan (Strengths):
        - IPK rata-rata di atas standar nasional
        - Tingkat kelulusan tepat waktu yang baik
        - Sistem monitoring akademik yang terintegrasi
        
        🛑 Kelemahan (Weaknesses):
        - Beberapa CPMK belum mencapai target
        - Variasi pencapaian antar mata kuliah
        """)
    
    with swot_col2:
        st.markdown("""
        🚀 Peluang (Opportunities):
        - Peningkatan metode pembelajaran
        - Kolaborasi dengan industri
        - Program sertifikasi tambahan
        
        ⚠ Ancaman (Threats):
        - Persaingan dengan prodi sejenis
        - Perubahan kurikulum nasional
        """)
    
    # Rekomendasi perbaikan
    st.subheader("📝 Rekomendasi Perbaikan")
    
    recommendations = [
        "Meningkatkan kualitas pengajaran untuk mata kuliah dengan pencapaian CPMK rendah",
        "Program pendampingan bagi mahasiswa dengan IPK di bawah 3.0",
        "Evaluasi sistem penilaian untuk memastikan keselarasan dengan CPL",
        "Peningkatan sistem monitoring kehadiran dan partisipasi mahasiswa",
        "Pengembangan program magang dan kolaborasi industri"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

def render_header(context="default"):
    """Render header dengan info user dan logout"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🎓 Sistem Prediksi Kelulusan Mahasiswa")
        st.caption(f"Selamat datang, {st.session_state['user_name']} ({st.session_state['user_role']})")
    
    with col2:
        logout_key = f"logout_button_{context}"
        if st.button("🚪 Logout", type="secondary", key=logout_key):
            logout()
            st.rerun()

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

def render_batch_upload_interface():
    """Render interface untuk batch upload"""
    st.header("📂 Batch Upload & Prediksi")
    st.markdown("Upload file Excel berisi data mahasiswa untuk prediksi batch")
    
    # Load model
    model, label_encoder, feature_names, prodi_mapping = load_model_and_encoders()
    
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
        st.markdown("Kolom yang diperlukan:")
        required_columns = [
            "Nama Lengkap", "NIM", "Prodi", "IPK", "Jumlah_SKS",
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
            if st.button("🚀 Proses Batch Prediksi", type="primary", key="proses_batch_prediksi"):
                with st.spinner("Memproses prediksi batch..."):
                    # Proses data
                    results_df = process_batch_data(df, model, prodi_mapping)
                    
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
            prodi_filter = st.selectbox(
                "Filter Prodi",
                ["Semua"] + list(valid_results['Prodi'].unique())
            )
        else:
            prodi_filter = "Semua"
    
    # Apply filters
    filtered_df = results_df.copy()
    
    if show_filter == "Hanya Lulus":
        filtered_df = filtered_df[filtered_df['Prediksi'] == 'LULUS']
    elif show_filter == "Hanya Tidak Lulus":
        filtered_df = filtered_df[filtered_df['Prediksi'] == 'TIDAK LULUS']
    elif show_filter == "Hanya Error":
        filtered_df = filtered_df[filtered_df['Error'].notna()]
    
    if prodi_filter != "Semua":
        filtered_df = filtered_df[filtered_df['Prodi'] == prodi_filter]
    
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
        st.warning(f"⚠ {error_count} data mengalami error. Pilih filter 'Hanya Error' untuk melihat detail error.")
    
    # Download results
    if st.button("📥 Download Hasil ke Excel", type="secondary", key="Download"):
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
    if st.button("🗑 Clear Results", type="secondary", key="Clear"):
        st.session_state["batch_results"] = None
        st.rerun()

def render_prediction_interface():
    """Render interface prediksi berdasarkan role"""
    # Load model dan encoder
    model, label_encoder, feature_names, prodi_mapping = load_model_and_encoders()
    
    if model is None:
        st.stop()
    
    # Render header
    render_header(context="prediction_interface")
    st.markdown("---")
    
    # Get role-specific features
    role_features = get_role_specific_features()
    
    # Tab layout untuk admin dan dosen
    if role_features["show_batch_upload"]:
        if role_features.get("show_excel_management"):
            tab1, tab2, tab3 = st.tabs(["🎯 Prediksi Individual", "📂 Batch Upload", "📊 Kelola Excel"])
            with tab1:
                render_individual_prediction(model, prodi_mapping, role_features)
            with tab2:
                render_batch_upload_interface()
            with tab3:
                render_admin_excel_management()
        else:
            tab1, tab2 = st.tabs(["🎯 Prediksi Individual", "📂 Batch Upload"])
            with tab1:
                render_individual_prediction(model, prodi_mapping, role_features)
            with tab2:
                render_batch_upload_interface()
    else:
        render_individual_prediction(model, prodi_mapping, role_features)
    
    if st.session_state["user_role"] == "Prodi":
        # Menu khusus untuk Prodi
        menu_options = ["🏠 Dashboard", "📋 Manajemen CPL/CPMK"]
        selected_menu = st.sidebar.selectbox("📋 Menu Navigasi", menu_options)
        
        if selected_menu == "🏠 Dashboard":
            render_prodi_dashboard()
        elif selected_menu == "📋 Manajemen CPL/CPMK":
            # Cek fitur CPL/CPMK
            if role_features.get("can_input_cpl_cpmk", False):
                show_cpl_cpmk_management()
            else:
                st.error("❌ Fitur tidak tersedia untuk role Anda.")
        elif selected_menu == "📊 Laporan":
            render_prodi_reports()

def render_individual_prediction(model, prodi_mapping, role_features):
    """Render interface prediksi individual"""
    # Sidebar untuk input
    st.sidebar.header("📝 Input Data Mahasiswa")
    
    # Role-specific sidebar info
    if st.session_state["user_role"] == "Mahasiswa":
        # st.sidebar.info("💡 Anda dapat melakukan prediksi untuk diri sendiri")
        user_data = get_student_data(
            st.session_state["user_name"],
            st.session_state.get("user_nim", ""),
        )

        if user_data is None:
            st.error("Data mahasiswa tidak ditemukan")
            st.stop()

        # Pastikan semua kolom yang diperlukan ada dalam user_data
        required_columns = ["Prodi", "IPK", "Jumlah_SKS", "Nilai_Mata_Kuliah", 
                          "Jumlah_Kehadiran", "Jumlah_Tugas", "Skor_Evaluasi", "Lama_Studi"]
        
        # Cek kolom yang ada di user_data
        missing_columns = [col for col in required_columns if col not in user_data]
        
        if missing_columns:
            st.error(f"Data mahasiswa tidak lengkap. Kolom yang hilang: {', '.join(missing_columns)}")
            st.stop()

        try:
            prodi_selected = user_data["Prodi"]
            prodi_encoded = prodi_mapping.get(prodi_selected, 0)
            ipk = float(user_data["IPK"])
            jumlah_sks = int(user_data["Jumlah_SKS"])
            nilai_mk = float(user_data["Nilai_Mata_Kuliah"])
            kehadiran = float(user_data["Jumlah_Kehadiran"])
            tugas = int(user_data["Jumlah_Tugas"])
            skor_evaluasi = float(user_data["Skor_Evaluasi"])
            lama_studi = int(user_data["Lama_Studi"])
        except (KeyError, ValueError) as e:
            st.error(f"Error membaca data mahasiswa: {str(e)}")
            st.stop()

        with st.sidebar:
            st.subheader("📋 Data Mahasiswa (Dari Sistem)")
            st.info("Data diambil dari sistem, tidak dapat diubah.")
            st.write(f"*Prodi:* {prodi_selected}")
            st.write(f"*IPK:* {ipk}")
            st.write(f"*Jumlah SKS:* {jumlah_sks}")
            st.write(f"*Nilai Mata Kuliah:* {nilai_mk}")
            st.write(f"*Kehadiran (%):* {kehadiran}")
            st.write(f"*Jumlah Tugas:* {tugas}")
            st.write(f"*Skor Evaluasi:* {skor_evaluasi}")
            st.write(f"*Lama Studi:* {lama_studi} semester")
        
        predict_button = st.sidebar.button("🔮 Prediksi Kelulusan", type="primary")
    
    elif st.session_state["user_role"] == "Prodi":
        st.sidebar.info("Anda login sebagai prodi")
        with st.sidebar:
            predict_button = False
            prodi_selected = False
            ipk = False
            jumlah_sks = False
            nilai_mk = False
            kehadiran = False
            tugas = False
            skor_evaluasi = False
            lama_studi = False

    else:
        with st.sidebar:
            if st.session_state["user_role"] == "Dosen":
                st.sidebar.info("🎯 Mode Dosen: Akses analisis mendalam tersedia")
            else:
                st.sidebar.info("⚡ Mode Admin: Akses penuh sistem")

            prodi_options = list(prodi_mapping.keys())
            prodi_selected = st.selectbox("Prodi", prodi_options)
            prodi_encoded = prodi_mapping[prodi_selected]
        
            # IPK
            ipk = st.slider("IPK", min_value=0.0, max_value=4.0, value=3.0, step=0.01)
            
            # Jumlah SKS
            jumlah_sks = st.number_input("Jumlah SKS", min_value=100, max_value=200, value=144)
            
            # Nilai Mata Kuliah
            nilai_mk = st.slider("Nilai Mata Kuliah (rata-rata)", min_value=0, max_value=100, value=75)
            
            # Jumlah Kehadiran
            kehadiran = st.slider("Jum
