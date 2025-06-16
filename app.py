import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.auth import login
from utils.auth import logout
from utils.prediction import render_batch_upload_interface
from utils.dashboard.admin import create_summary_data
from utils.features import create_statistics_data, render_admin_excel_management, render_admin_activity_log, render_prediction_interface

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

    with col4:
        st.markdown("""
        *📚 Prodi*
        - Transkrip nilai mahasiswa
        - Laporan CPMK & CPL
        - Rekap nilai & absensi
        - Evaluasi kinerja akademik
        - Dashboard analitik
        """)

def export_to_excel(data, filename, include_summary=True, include_statistics=True):
    """Export data ke format Excel dengan multiple sheets"""
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Sheet utama - data mahasiswa
        data.to_excel(writer, sheet_name='Data_Mahasiswa', index=False)
        
        # Sheet summary
        if include_summary:
            summary_data = create_summary_data(data)
            summary_data.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet statistik
        if include_statistics:
            stats_data = create_statistics_data(data)
            stats_data.to_excel(writer, sheet_name='Statistik', index=False)
        
        # Sheet metadata
        metadata = create_metadata_sheet()
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    return buffer.getvalue()

def export_to_csv(data):
    """Export data ke format CSV"""
    buffer = io.StringIO()
    data.to_csv(buffer, index=False)
    return buffer.getvalue().encode('utf-8')

def export_to_json(data):
    """Export data ke format JSON"""
    json_data = data.to_json(orient='records', indent=2)
    return json_data.encode('utf-8')

def create_metadata_sheet():
    """Buat sheet metadata"""
    metadata_info = {
        'Property': [
            'Export Date',
            'Export Time',
            'Exported By',
            'System Version',
            'File Format',
            'Total Records'
        ],
        'Value': [
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
            st.session_state.get('user_name', 'Admin'),
            'Student Prediction System v1.0',
            'Excel (.xlsx)',
            len(st.session_state.get("admin_excel_data", []))
        ]
    }
    
    return pd.DataFrame(metadata_info)

def log_export_activity(filename, format_type, record_count):
    """Log aktivitas export"""
    if "admin_activity_log" not in st.session_state:
        st.session_state["admin_activity_log"] = []
    
    st.session_state["admin_activity_log"].append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': 'EXPORT_DATA',
        'details': f"Exported {record_count} records to {filename} ({format_type})"
    })

# Fungsi untuk mengintegrasikan dengan menu utama admin
def render_admin_dashboard():
    """Render dashboard khusus admin dengan fitur Excel management"""
    st.header("👨‍💼 Admin Dashboard")
    
    # Menu admin
    admin_menu = st.selectbox(
        "Pilih Menu Admin",
        [
            "📊 Kelola Data Excel",
            "🎯 Prediksi Batch",
            "📋 Log Aktivitas",
            "⚙️ Pengaturan Sistem"
        ]
    )
    
    if admin_menu == "📊 Kelola Data Excel":
        render_admin_excel_management()
    elif admin_menu == "🎯 Prediksi Batch":
        render_batch_upload_interface()
    elif admin_menu == "📋 Log Aktivitas":
        render_admin_activity_log()
    elif admin_menu == "⚙️ Pengaturan Sistem":
        st.info("Fitur pengaturan sistem akan segera hadir")

def handle_data_change():
    """Callback untuk handle perubahan data"""
    st.session_state["data_modified"] = True

# Main App
def main():
    """Fungsi utama aplikasi"""
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        render_prediction_interface()

if __name__ == "__main__":
    main()
