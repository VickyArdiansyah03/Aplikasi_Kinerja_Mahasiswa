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

def logout():
    """Fungsi logout"""
    st.session_state["logged_in"] = False
    st.session_state["user_name"] = ""
    st.session_state["user_role"] = ""
    st.session_state["batch_results"] = None
    st.session_state["prodi_data"] = None

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

# [Previous functions remain the same until render_login_page]

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
        *👨‍🎓 Mahasiswa*
        - Prediksi kelulusan pribadi
        - Melihat profil akademik
        - Transkrip nilai
        - Mendapat rekomendasi
        """)
    
    with col2:
        st.markdown("""
        *👨‍🏫 Dosen*
        - Prediksi untuk mahasiswa
        - Analisis mendalam
        - Tools evaluasi
        - *Batch upload Excel*
        """)
    
    with col3:
        st.markdown("""
        *🏛 Prodi*
        - Transkrip nilai mahasiswa
        - Laporan CPMK & CPL
        - Rekap nilai & absensi
        - Evaluasi kinerja akademik
        - Dashboard analitik
        """)
    
    with col4:
        st.markdown("""
        *👨‍💼 Admin*
        - Akses penuh sistem
        - Kelola data
        - Laporan statistik
        - *Batch upload Excel*
        """)

def render_prodi_dashboard():
    """Render dashboard khusus prodi"""
    render_header()
    st.markdown("---")
    
    # Load prodi data
    prodi_data = st.session_state["prodi_data"]
    
    # Menu navigasi prodi
    menu_options = [
        "📊 Dashboard Utama",
        "📝 Transkrip Nilai Mahasiswa",
        "🎯 Laporan Ketercapaian CPMK",
        "📈 Kontribusi CPMK terhadap CPL",
        "✅ Rekap Nilai & Absensi",
        "📌 Evaluasi Kinerja Akademik"
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
        st.warning("⚠️ Beberapa CPMK Belum Tercapai:")
        for idx, row in filtered_cpmk[filtered_cpmk['Status'] == 'Belum Tercapai'].iterrows():
            gap = row['Target'] - row['Pencapaian_Rata2']
            st.write(f"""
            - **{row['Kode_CPMK']}**: {row['Deskripsi_CPMK']}  
              *Pencapaian: {row['Pencapaian_Rata2']}% (Target: {row['Target']}%, Gap: {gap:.1f}%)*  
              💡 **Rekomendasi**: Perbaikan metode pembelajaran dan evaluasi untuk CPMK ini
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
            st.write(f"**Tingkat Pencapaian:** {row['Tingkat_Pencapaian']}%")
            st.write("**Kontribusi CPMK:**")
            
            contributions = row['Kontribusi_CPMK'].split(',')
            for contrib in contributions:
                contrib = contrib.strip()
                st.write(f"- {contrib}")
            
            # Analisis
            if row['Tingkat_Pencapaian'] < 75:
                st.error("🔴 Pencapaian di bawah standar (minimal 75%)")
                st.write("""
                **Rekomendasi Perbaikan:**
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
        st.warning(f"⚠️ {len(anomaly)} mahasiswa memiliki kehadiran rendah tetapi nilai baik:")
        st.dataframe(
            anomaly[['NIM', 'Nama', 'Nama_MK', 'Nilai', 'Persentase_Kehadiran']],
            use_container_width=True,
            hide_index=True
        )
        st.write("""
        **Interpretasi:**
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
        **Rekomendasi:**
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
        **💪 Kekuatan (Strengths):**
        - IPK rata-rata di atas standar nasional
        - Tingkat kelulusan tepat waktu yang baik
        - Sistem monitoring akademik yang terintegrasi
        
        **🛑 Kelemahan (Weaknesses):**
        - Beberapa CPMK belum mencapai target
        - Variasi pencapaian antar mata kuliah
        """)
    
    with swot_col2:
        st.markdown("""
        **🚀 Peluang (Opportunities):**
        - Peningkatan metode pembelajaran
        - Kolaborasi dengan industri
        - Program sertifikasi tambahan
        
        **⚠️ Ancaman (Threats):**
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

# [Previous functions remain the same until main()]

def main():
    """Fungsi utama aplikasi"""
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        if st.session_state["user_role"] == "Prodi":
            render_prodi_dashboard()
        else:
            render_prediction_interface()

# Jalankan aplikasi
if __name__ == "__main__":
    main()
