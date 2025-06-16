import streamlit as st
import pandas as pd
import datetime as datetime

def add_new_student_data(nama, nim, jurusan, ipk, jumlah_sks, nilai_mk, kehadiran, tugas, skor_evaluasi, lama_studi):
    """Tambah data mahasiswa baru ke dataset - FIXED VERSION"""
    
    # Pastikan ada data existing
    if "admin_excel_data" not in st.session_state:
        st.error("❌ Tidak ada data existing. Upload file Excel terlebih dahulu.")
        return False
    
    # Buat dictionary data baru
    new_data = {
        'Nama Lengkap': nama,
        'NIM': nim,
        'Role' : 'Mahasiswa',
        'Jurusan': jurusan,
        'IPK': ipk,
        'Jumlah_SKS': jumlah_sks,
        'Nilai_Mata_Kuliah': nilai_mk,
        'Jumlah_Kehadiran': kehadiran,
        'Jumlah_Tugas': tugas,
        'Skor_Evaluasi': skor_evaluasi,
        'Lama_Studi': lama_studi
    }
    
    try:
        # Ambil data existing
        existing_data = st.session_state["admin_excel_data"].copy()
        
        # Buat row baru
        new_row = pd.DataFrame([new_data])
        
        # Concatenate dengan data existing
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        
        # Update session state dengan data baru
        st.session_state["admin_excel_data"] = updated_data
        st.session_state["data_modified"] = True
        
        # Log activity
        if "admin_activity_log" not in st.session_state:
            st.session_state["admin_activity_log"] = []
        
        st.session_state["admin_activity_log"].append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'ADD_STUDENT',
            'details': f"Added student: {nama} (NIM: {nim})"
        })
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error menambah data: {str(e)}")
        return False

def create_summary_data(data):
    """Buat data summary untuk export"""
    summary_info = {
        'Metrik': [
            'Total Mahasiswa',
            'Jumlah Jurusan',
            'Rata-rata IPK',
            'Mahasiswa IPK > 3.0',
            'Rata-rata Kehadiran',
            'Tanggal Export'
        ],
        'Nilai': [
            len(data),
            data['Jurusan'].nunique() if 'Jurusan' in data.columns else 0,
            f"{data['IPK'].mean():.2f}" if 'IPK' in data.columns else 'N/A',
            len(data[data['IPK'] > 3.0]) if 'IPK' in data.columns else 0,
            f"{data['Jumlah_Kehadiran'].mean():.1f}%" if 'Jumlah_Kehadiran' in data.columns else 'N/A',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
    }
    
    return pd.DataFrame(summary_info)