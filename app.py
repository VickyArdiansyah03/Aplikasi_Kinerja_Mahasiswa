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

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "batch_results" not in st.session_state:
    st.session_state["batch_results"] = None

def login(nama_user, role):
    """Fungsi login sederhana berdasarkan nama dan role"""
    if nama_user.strip():  # Cek apakah nama tidak kosong
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = nama_user
        st.session_state["user_role"] = role
        return True
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
                    'Nama': row.get('Nama', f'Mahasiswa_{idx}'),
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
                'Nama': row.get('Nama', f'Mahasiswa_{idx}'),
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
                'Nama': row.get('Nama', f'Mahasiswa_{idx}'),
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
    jurusan_prediksi = valid_results.groupby(['Jurusan', 'Prediksi']).size().unstack(fill_value=0)
    
    fig_bar = px.bar(
        jurusan_prediksi.reset_index(),
        x='Jurusan',
        y=['LULUS', 'TIDAK LULUS'],
        title="Prediksi Kelulusan per Jurusan",
        color_discrete_map={'LULUS': '#2E8B57', 'TIDAK LULUS': '#DC143C'}
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
        'Nama': ['John Doe', 'Jane Smith', 'Ahmad Rahman'],
        'NIM': ['12345678', '87654321', '11223344'],
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
    st.title("🔐 Login Prediksi Kelulusan Mahasiswa")
    st.markdown("---")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Masuk ke Sistem")
            
            with st.form("login_form"):
                nama_user = st.text_input("🧑 Nama Lengkap", placeholder="Masukkan nama lengkap Anda")
                role = st.selectbox("👥 Masuk Sebagai", ["Mahasiswa", "Dosen", "Admin"])
                
                submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                
                if submitted:
                    if login(nama_user, role):
                        st.success(f"✅ Selamat datang, {nama_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Nama tidak boleh kosong!")
    
    # Informasi role
    st.markdown("---")
    st.markdown("### 📋 Akses Berdasarkan Role")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        *👨‍🎓 Mahasiswa*
        - Prediksi kelulusan pribadi
        - Melihat profil akademik
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
        *👨‍💼 Admin*
        - Akses penuh sistem
        - Kelola data
        - Laporan statistik
        - *Batch upload Excel*
        """)

def render_header():
    """Render header dengan info user dan logout"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🎓 Sistem Prediksi Kelulusan Mahasiswa")
        st.caption(f"Selamat datang, *{st.session_state['user_name']}* ({st.session_state['user_role']})")
    
    with col2:
        if st.button("🚪 Logout", type="secondary"):
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
            "title_suffix": "- Mode Mahasiswa"
        }
    elif role == "Dosen":
        return {
            "show_advanced_analysis": True,
            "show_admin_features": False,
            "show_batch_upload": True,
            "prediction_limit": 10,
            "title_suffix": "- Mode Dosen"
        }
    else:  # Admin
        return {
            "show_advanced_analysis": True,
            "show_admin_features": True,
            "show_batch_upload": True,
            "prediction_limit": None,
            "title_suffix": "- Mode Admin"
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
            "Nama", "NIM", "Jurusan", "IPK", "Jumlah_SKS",
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
    
    # Display filtered results
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download results
    if st.button("📥 Download Hasil ke Excel", type="secondary"):
        buffer = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Sheet 1: Hasil detail
            results_df.to_excel(writer, sheet_name='Hasil_Detail', index=False)
            
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

def render_prediction_interface():
    """Render interface prediksi berdasarkan role"""
    # Load model dan encoder
    model, label_encoder, feature_names, jurusan_mapping = load_model_and_encoders()
    
    if model is None:
        st.stop()
    
    # Render header
    render_header()
    st.markdown("---")
    
    # Get role-specific features
    role_features = get_role_specific_features()
    
    # Tab layout untuk admin dan dosen
    if role_features["show_batch_upload"]:
        tab1, tab2 = st.tabs(["🎯 Prediksi Individual", "📂 Batch Upload"])
        
        with tab1:
            render_individual_prediction(model, jurusan_mapping, role_features)
        
        with tab2:
            render_batch_upload_interface()
    else:
        render_individual_prediction(model, jurusan_mapping, role_features)

def render_individual_prediction(model, jurusan_mapping, role_features):
    """Render interface prediksi individual"""
    # Sidebar untuk input
    st.sidebar.header("📝 Input Data Mahasiswa")
    
    # Role-specific sidebar info
    if st.session_state["user_role"] == "Mahasiswa":
        st.sidebar.info("💡 Anda dapat melakukan prediksi untuk diri sendiri")
    elif st.session_state["user_role"] == "Dosen":
        st.sidebar.info("🎯 Mode Dosen: Akses analisis mendalam tersedia")
    else:
        st.sidebar.info("⚡ Mode Admin: Akses penuh sistem")
    
    # Input fields
    with st.sidebar:
        # Jurusan
        jurusan_options = list(jurusan_mapping.keys())
        jurusan_selected = st.selectbox("Jurusan", jurusan_options)
        jurusan_encoded = jurusan_mapping[jurusan_selected]
        
        # IPK
        ipk = st.slider("IPK", min_value=0.0, max_value=4.0, value=3.0, step=0.01)
        
        # Jumlah SKS
        jumlah_sks = st.number_input("Jumlah SKS", min_value=100, max_value=200, value=144)
        
        # Nilai Mata Kuliah
        nilai_mk = st.slider("Nilai Mata Kuliah (rata-rata)", min_value=0, max_value=100, value=75)
        
        # Jumlah Kehadiran
        kehadiran = st.slider("Jumlah Kehadiran (%)", min_value=0, max_value=100, value=80)
        
        # Jumlah Tugas
        tugas = st.number_input("Jumlah Tugas", min_value=0, max_value=50, value=15)
        
        # Skor Evaluasi Dosen
        skor_evaluasi = st.slider("Skor Evaluasi Dosen", min_value=1.0, max_value=5.0, value=3.5, step=0.1)
        
        # Lama Studi
        lama_studi = st.number_input("Waktu Lama Studi (semester)", min_value=6, max_value=16, value=8)
        
        # Tombol prediksi
        predict_button = st.button("🔮 Prediksi Kelulusan", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Hasil Prediksi")
        
        if predict_button:
            # Lakukan prediksi
            hasil = predict_graduation(
                model, jurusan_encoded, ipk, jumlah_sks, nilai_mk,
                kehadiran, tugas, skor_evaluasi, lama_studi
            )
            
            # Tampilkan hasil utama
            if hasil['prediksi'] == 1:
                st.success("✅ *LULUS*")
                if st.session_state["user_role"] == "Mahasiswa":
                    st.balloons()
            else:
                st.error("❌ *TIDAK LULUS*")
            
            # Probabilitas
            col_prob1, col_prob2 = st.columns(2)
            
            with col_prob1:
                st.metric(
                    "Probabilitas Lulus", 
                    f"{hasil['probabilitas_lulus']:.1%}",
                    delta=f"Confidence: {hasil['confidence']:.1%}"
                )
            
            with col_prob2:
                st.metric(
                    "Probabilitas Tidak Lulus", 
                    f"{hasil['probabilitas_tidak_lulus']:.1%}"
                )
            
            # Gauge charts
            st.subheader("📈 Visualisasi Probabilitas")
            
            col_gauge1, col_gauge2 = st.columns(2)
            
            with col_gauge1:
                fig_lulus = create_gauge_chart(
                    hasil['probabilitas_lulus'], 
                    "Probabilitas Lulus"
                )
                st.plotly_chart(fig_lulus, use_container_width=True)
            
            with col_gauge2:
                fig_tidak_lulus = create_gauge_chart(
                    hasil['probabilitas_tidak_lulus'], 
                    "Probabilitas Tidak Lulus"
                )
                st.plotly_chart(fig_tidak_lulus, use_container_width=True)
            
            # Advanced analysis untuk Dosen dan Admin
            if role_features["show_advanced_analysis"]:
                st.subheader("🔧 Analisis Fitur (Mode Lanjutan)")
                
                col_feat1, col_feat2, col_feat3, col_feat4 = st.columns(4)
                
                with col_feat1:
                    st.metric("Academic Performance", f"{hasil['academic_performance']:.3f}")
                
                with col_feat2:
                    st.metric("Engagement Score", f"{hasil['engagement_score']:.1f}")
                
                with col_feat3:
                    st.metric("Study Efficiency", f"{hasil['study_efficiency']:.3f}")
                
                with col_feat4:
                    st.metric("SKS per Semester", f"{hasil['sks_per_semester']:.1f}")
                
                # Radar chart
                st.subheader("🎯 Profil Mahasiswa")
                fig_radar = create_feature_radar_chart(
                    hasil['academic_performance'],
                    hasil['engagement_score'],
                    hasil['study_efficiency'],
                    hasil['sks_per_semester']
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Rekomendasi
            st.subheader("💡 Rekomendasi")
            
            if hasil['prediksi'] == 0:  # Tidak lulus
                st.warning("*Perlu Perbaikan:*")
                recommendations = []
                
                if ipk < 3.0:
                    recommendations.append("📚 Tingkatkan IPK dengan belajar lebih giat")
                
                if kehadiran < 80:
                    recommendations.append("🏫 Tingkatkan kehadiran kuliah")
                
                if tugas < 15:
                    recommendations.append("📝 Lebih aktif mengerjakan tugas")
                
                if hasil['study_efficiency'] < 0.35:
                    recommendations.append("⏰ Optimalkan manajemen waktu belajar")
                
                for rec in recommendations:
                    st.write(f"• {rec}")
                
                # Rekomendasi khusus Dosen
                if st.session_state["user_role"] == "Dosen":
                    st.info("*Rekomendasi untuk Dosen:*")
                    st.write("• 🎯 Berikan bimbingan ekstra pada mahasiswa")
                    st.write("• 📞 Lakukan konseling akademik")
                    st.write("• 📋 Monitor progress secara berkala")
            
            else:  # Lulus
                st.success("*Pertahankan Performa:*")
                st.write("• 🎯 Pertahankan IPK yang baik")
                st.write("• 📈 Terus tingkatkan engagement di kelas")
                st.write("• 🏆 Siapkan diri untuk wisuda!")
    
    with col2:
        st.header("ℹ Informasi Data")
        
        # User info
        st.subheader("👤 Info Pengguna:")
        st.write(f"*Nama:* {st.session_state['user_name']}")
        st.write(f"*Role:* {st.session_state['user_role']}")
        
        # Tampilkan data input
        st.subheader("📝 Input Data:")
        input_data = {
            "Jurusan": jurusan_selected,
            "IPK": ipk,
            "Jumlah SKS": jumlah_sks,
            "Nilai Mata Kuliah": nilai_mk,
            "Kehadiran (%)": kehadiran,
            "Jumlah Tugas": tugas,
            "Skor Evaluasi": skor_evaluasi,
            "Lama Studi": f"{lama_studi} semester"
        }
        
        for key, value in input_data.items():
            st.write(f"{key}:** {value}")
        
        # Model info
        st.subheader("🤖 Model Info:")
        st.write("*Algorithm:* Random Forest")
        st.write("*Features:* 12 fitur")
        st.write("*Balancing:* SMOTE")
        
        # Feature importance (contoh)
        st.subheader("🔍 Fitur Penting:")
        st.write("1. IPK")
        st.write("2. Academic Performance")
        st.write("3. Study Efficiency")
        st.write("4. Nilai Mata Kuliah")
        st.write("5. Engagement Score")
        
        # Admin features
        if role_features["show_admin_features"]:
            st.subheader("⚙ Admin Tools:")
            st.write("• Model Statistics")
            st.write("• User Management")
            st.write("• System Logs")
            st.write("• Data Export")
            
        # Batch upload hint untuk dosen/admin
        if role_features["show_batch_upload"]:
            st.subheader("📂 Batch Processing:")
            st.info("💡 Gunakan tab 'Batch Upload' untuk memproses banyak mahasiswa sekaligus")

# Main App
def main():
    """Fungsi utama aplikasi"""
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        render_prediction_interface()

# Jalankan aplikasi
if __name__ == "__main__":
    main()
