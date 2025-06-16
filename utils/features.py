import streamlit as st
import pandas as pd
import numpy as np
from utils.prediction import process_batch_data, load_model_and_encoders, create_batch_summary_charts
from utils.data import create_sample_template
from app import get_student_data, predict_graduation, create_gauge_chart, create_feature_radar_chart, handle_data_change, export_to_csv, export_to_excel, export_to_json, log_export_activity
from utils.auth import logout
from dashboard.admin import add_new_student_data
import plotly.express as px
import io
from datetime import datetime

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

def render_excel_upload_view(jurusan_mapping):
    """Render interface upload dan view Excel"""
    st.subheader("📁 Upload & Lihat Data Excel")
    
    # Upload file
    uploaded_file = st.file_uploader(
        "Upload file Excel untuk diedit",
        type=['xlsx'],
        key="admin_excel_upload",
        help="Up" \
        "load file Excel yang akan diedit/ditambahkan datanya"
    )
    
    if uploaded_file is not None:
        try:
            # Hanya baca file jika belum ada atau file berbeda
            if ("admin_excel_data" not in st.session_state or 
                st.session_state.get("current_filename") != uploaded_file.name):
                
                # Baca file Excel
                df = pd.read_excel(uploaded_file)
                
                # Simpan ke session state
                st.session_state["admin_excel_data"] = df.copy()
                st.session_state["original_filename"] = uploaded_file.name
                st.session_state["current_filename"] = uploaded_file.name
                st.session_state["data_modified"] = False
                
                st.success(f"✅ File '{uploaded_file.name}' berhasil diupload! Ditemukan {len(df)} baris data")
            
            # Ambil data dari session state
            current_data = st.session_state["admin_excel_data"]
            
            # Tampilkan data dengan opsi edit
            st.subheader("📋 Data Saat Ini")
            
            # Search dan filter
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Cari berdasarkan Nama/NIM", key="search_excel")
            with col2:
                if 'Jurusan' in current_data.columns:
                    jurusan_filter = st.selectbox(
                        "Filter Jurusan", 
                        ["Semua"] + list(current_data['Jurusan'].unique()),
                        key="filter_jurusan_excel"
                    )
                else:
                    jurusan_filter = "Semua"
            
            # Apply filters untuk display
            display_data = current_data.copy()
            filter_applied = False
            
            if search_term:
                if 'Nama Lengkap' in current_data.columns and 'NIM' in current_data.columns:
                    display_data = current_data[
                        (current_data['Nama Lengkap'].str.contains(search_term, case=False, na=False)) |
                        (current_data['NIM'].astype(str).str.contains(search_term, case=False, na=False))
                    ]
                elif 'Nama Lengkap' in current_data.columns:
                    display_data = current_data[current_data['Nama Lengkap'].str.contains(search_term, case=False, na=False)]
                filter_applied = True
            
            if jurusan_filter != "Semua" and 'Jurusan' in current_data.columns:
                display_data = display_data[display_data['Jurusan'] == jurusan_filter]
                filter_applied = True
            
            # Peringatan jika filter aktif
            if filter_applied:
                st.warning("⚠️ Filter aktif! Edit data mungkin tidak tersimpan dengan benar. Hapus filter untuk edit yang aman.")
            
            # Pilihan edit mode
            edit_mode = st.radio(
                "Mode Edit:",
                ["View Only", "Edit Mode"],
                horizontal=True,
                help="Pilih 'Edit Mode' untuk mengedit data. Pastikan tidak ada filter aktif."
            )
            
            if edit_mode == "Edit Mode" and not filter_applied:
                # Edit mode - gunakan seluruh data
                st.info("✏️ Mode Edit Aktif - Anda dapat mengedit data di bawah ini")
                
                edited_df = st.data_editor(
                    st.session_state["admin_excel_data"],
                    use_container_width=True,
                    num_rows="dynamic",
                    key="excel_data_editor",
                    on_change=handle_data_change
                )
                
                # Simpan perubahan ke session state
                if not edited_df.equals(st.session_state["admin_excel_data"]):
                    st.session_state["admin_excel_data"] = edited_df.copy()
                    st.session_state["data_modified"] = True
                    st.success("✅ Perubahan data tersimpan!")
                
            else:
                # View mode - tampilkan data yang sudah difilter
                st.dataframe(display_data, use_container_width=True)
            
            # Status indikator
            if st.session_state.get("data_modified", False):
                st.info("📝 Data telah dimodifikasi. Jangan lupa untuk export data yang sudah diubah!")
                
                # Tombol untuk reset perubahan
                if st.button("🔄 Reset ke Data Asli", type="secondary"):
                    if st.session_state.get("original_filename"):
                        # Baca ulang file asli
                        # Note: Ini memerlukan file asli masih tersedia
                        st.session_state["data_modified"] = False
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error membaca file: {str(e)}")
    
    else:
        st.info("📤 Silakan upload file Excel untuk mulai mengelola data")

def render_add_data_form(jurusan_mapping):
    """Render form untuk menambah data baru"""
    st.subheader("➕ Tambah Data Mahasiswa Baru")
    
    # Cek apakah ada data Excel yang sudah diupload
    if "admin_excel_data" not in st.session_state or st.session_state["admin_excel_data"] is None:
        st.warning("⚠️ Silakan upload file Excel terlebih dahulu di tab 'Upload & View'")
        return
    
    # Form untuk data baru
    with st.form("add_new_student_form"):
        st.markdown("### 📝 Input Data Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nama_baru = st.text_input("Nama Lengkap", placeholder="Masukkan nama mahasiswa")
            nim_baru = st.text_input("NIM", placeholder="Masukkan NIM mahasiswa")
            jurusan_baru = st.selectbox("Jurusan", list(jurusan_mapping.keys()))
            ipk_baru = st.number_input("IPK", min_value=0.0, max_value=4.0, value=3.0, step=0.01)
            jumlah_sks_baru = st.number_input("Jumlah SKS", min_value=100, max_value=200, value=144)
        
        with col2:
            nilai_mk_baru = st.number_input("Nilai Mata Kuliah", min_value=0, max_value=100, value=75)
            kehadiran_baru = st.number_input("Jumlah Kehadiran (%)", min_value=0, max_value=100, value=80)
            tugas_baru = st.number_input("Jumlah Tugas", min_value=0, max_value=50, value=15)
            skor_evaluasi_baru = st.number_input("Skor Evaluasi", min_value=1.0, max_value=5.0, value=3.5, step=0.1)
            lama_studi_baru = st.number_input("Lama Studi (semester)", min_value=6, max_value=16, value=8)
        
        # Tombol submit
        submitted = st.form_submit_button("➕ Tambah Data", type="primary")
        
        if submitted:
            if not nama_baru or not nim_baru:
                st.error("❌ Nama dan NIM harus diisi!")
            else:
                # Validasi NIM unik
                existing_data = st.session_state["admin_excel_data"]
                if 'NIM' in existing_data.columns and nim_baru in existing_data['NIM'].astype(str).values:
                    st.error(f"❌ NIM {nim_baru} sudah ada dalam data!")
                else:
                    # Tambah data baru
                    add_new_student_data(
                        nama_baru, nim_baru, jurusan_baru, ipk_baru, jumlah_sks_baru,
                        nilai_mk_baru, kehadiran_baru, tugas_baru, skor_evaluasi_baru, lama_studi_baru
                    )
                    st.success(f"✅ Data mahasiswa {nama_baru} berhasil ditambahkan!")
                    # st.rerun()
    
    # Tampilkan preview data yang sudah ada
    if st.session_state["admin_excel_data"] is not None:
        st.subheader("📊 Preview Data Terkini")
        st.info(f"Total data: {len(st.session_state['admin_excel_data'])} mahasiswa")
        st.dataframe(st.session_state["admin_excel_data"].tail(), use_container_width=True)

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

def render_export_data_interface():
    """Render interface untuk export data - FIXED VERSION"""
    st.subheader("📥 Export Data")
    
    # Cek apakah ada data untuk di-export
    if "admin_excel_data" not in st.session_state or st.session_state["admin_excel_data"] is None:
        st.warning("⚠️ Tidak ada data untuk di-export. Silakan upload file Excel terlebih dahulu.")
        return
    
    # Pastikan menggunakan data terbaru dari session state
    data_to_export = st.session_state["admin_excel_data"].copy()
    
    # Informasi data
    st.info(f"📊 Data siap export: {len(data_to_export)} baris")
    
    # Status modifikasi
    if st.session_state.get("data_modified", False):
        st.success("✅ Data telah dimodifikasi dan siap untuk di-export dengan perubahan terbaru!")
    else:
        st.info("ℹ️ Data belum dimodifikasi - akan export data asli")
    
    # Preview data
    with st.expander("👀 Preview Data yang akan di-export"):
        st.dataframe(data_to_export, use_container_width=True)
    
    # Opsi export
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Opsi Export")
        
        # Pilihan format
        export_format = st.radio(
            "Format Export",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
            index=0
        )
        
        # Pilihan sheet (untuk Excel)
        if export_format == "Excel (.xlsx)":
            include_summary = st.checkbox("Tambahkan sheet summary", value=True)
            include_statistics = st.checkbox("Tambahkan sheet statistik", value=True)
        
        # Nama file
        original_name = st.session_state.get("original_filename", "data_mahasiswa")
        default_filename = f"updated_{original_name.replace('.xlsx', '')}"
        
        filename = st.text_input(
            "Nama file (tanpa ekstensi)", 
            value=default_filename
        )
    
    with col2:
        st.markdown("### 📊 Statistik Data")
        
        # Tampilkan statistik singkat
        if 'Jurusan' in data_to_export.columns:
            jurusan_counts = data_to_export['Jurusan'].value_counts()
            st.write("**Distribusi Jurusan:**")
            for jurusan, count in jurusan_counts.items():
                st.write(f"• {jurusan}: {count} mahasiswa")
        
        if 'IPK' in data_to_export.columns:
            st.write("**Statistik IPK:**")
            st.write(f"• Rata-rata: {data_to_export['IPK'].mean():.2f}")
            st.write(f"• Minimum: {data_to_export['IPK'].min():.2f}")
            st.write(f"• Maksimum: {data_to_export['IPK'].max():.2f}")
    
    # Tombol export
    if st.button("📥 Export Data", type="primary", use_container_width=True):
        try:
            # Pastikan menggunakan data terbaru
            export_data = st.session_state["admin_excel_data"].copy()
            
            if export_format == "Excel (.xlsx)":
                buffer = export_to_excel(
                    export_data, 
                    filename, 
                    include_summary, 
                    include_statistics
                )
                file_extension = ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            elif export_format == "CSV (.csv)":
                buffer = export_to_csv(export_data)
                file_extension = ".csv"
                mime_type = "text/csv"
            
            else:  # JSON
                buffer = export_to_json(export_data)
                file_extension = ".json"
                mime_type = "application/json"
            
            # Download button
            st.download_button(
                label=f"📥 Download {export_format}",
                data=buffer,
                file_name=f"{filename}{file_extension}",
                mime=mime_type,
                type="primary"
            )
            
            # Log activity
            log_export_activity(filename, export_format, len(export_data))
            
            # Reset status modifikasi setelah export
            st.session_state["data_modified"] = False
            
            st.success(f"✅ Data berhasil diekspor! File: {filename}{file_extension}")
            
        except Exception as e:
            st.error(f"❌ Error saat export: {str(e)}")
            st.error("Detail error untuk debugging:")
            st.code(str(e))

def render_admin_excel_management():
    """Render interface untuk admin mengelola data Excel"""
    st.header("📊 Admin - Kelola Data Excel")
    st.markdown("Upload, edit, dan kelola data mahasiswa dalam format Excel")
    
    # Load model untuk validasi
    model, label_encoder, feature_names, jurusan_mapping = load_model_and_encoders()
    
    if model is None:
        st.stop()
    
    # Tab untuk berbagai fungsi admin
    tab1, tab2, tab3 = st.tabs(["📤 Upload & View", "➕ Tambah Data", "📥 Export Data"])
    
    with tab1:
        render_excel_upload_view(jurusan_mapping)
    
    with tab2:
        render_add_data_form(jurusan_mapping)
    
    with tab3:
        render_export_data_interface()

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
        if role_features.get("show_excel_management"):
            tab1, tab2, tab3 = st.tabs(["🎯 Prediksi Individual", "📂 Batch Upload", "📊 Kelola Excel"])
            with tab1:
                render_individual_prediction(model, jurusan_mapping, role_features)
            with tab2:
                render_batch_upload_interface()
            with tab3:
                render_admin_excel_management()
        else:
            tab1, tab2 = st.tabs(["🎯 Prediksi Individual", "📂 Batch Upload"])
            with tab1:
                render_individual_prediction(model, jurusan_mapping, role_features)
            with tab2:
                render_batch_upload_interface()
    else:
        render_individual_prediction(model, jurusan_mapping, role_features)

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

        jurusan_selected = user_data["Jurusan"]
        jurusan_encoded = jurusan_mapping.get(jurusan_selected, 0)
        ipk = float(user_data["IPK"])
        # st.write("User data:", user_data)
        jumlah_sks = int(user_data["Jumlah_SKS"])
        nilai_mk = float(user_data["Nilai_Mata_Kuliah"])
        kehadiran = float(user_data["Jumlah_Kehadiran"])
        tugas = int(user_data["Jumlah_Tugas"])
        skor_evaluasi = float(user_data["Skor_Evaluasi"])
        lama_studi = int(user_data["Lama_Studi"])

        with st.sidebar:
            st.subheader("📋 Data Mahasiswa (Dari Sistem)")
            st.info("Data diambil dari sistem, tidak dapat diubah.")
            st.write(f"**Jurusan:** {jurusan_selected}")
            st.write(f"**IPK:** {ipk}")
            st.write(f"**Jumlah SKS:** {jumlah_sks}")
            st.write(f"**Nilai Mata Kuliah:** {nilai_mk}")
            st.write(f"**Kehadiran (%):** {kehadiran}")
            st.write(f"**Jumlah Tugas:** {tugas}")
            st.write(f"**Skor Evaluasi:** {skor_evaluasi}")
            st.write(f"**Lama Studi:** {lama_studi} semester")
        
        predict_button = st.sidebar.button("🔮 Prediksi Kelulusan", type="primary")
    
    else:
        with st.sidebar:
            if st.session_state["user_role"] == "Dosen":
                st.sidebar.info("🎯 Mode Dosen: Akses analisis mendalam tersedia")
            else:
                st.sidebar.info("⚡ Mode Admin: Akses penuh sistem")

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

def create_statistics_data(data):
    """Buat data statistik untuk export"""
    stats_list = []
    
    # Statistik untuk kolom numerik
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        stats_list.append({
            'Kolom': col,
            'Mean': data[col].mean(),
            'Median': data[col].median(),
            'Std': data[col].std(),
            'Min': data[col].min(),
            'Max': data[col].max(),
            'Count': data[col].count()
        })
    
    return pd.DataFrame(stats_list)

def render_admin_activity_log():
    """Render log aktivitas admin"""
    st.subheader("📋 Log Aktivitas Admin")
    
    if "admin_activity_log" not in st.session_state or not st.session_state["admin_activity_log"]:
        st.info("Belum ada aktivitas yang tercatat.")
        return
    
    # Tampilkan log dalam dataframe
    log_df = pd.DataFrame(st.session_state["admin_activity_log"])
    
    # Reverse order untuk menampilkan yang terbaru di atas
    log_df = log_df.iloc[::-1].reset_index(drop=True)
    
    st.dataframe(log_df, use_container_width=True)
    
    # Tombol clear log
    if st.button("🗑 Clear Log", type="secondary"):
        st.session_state["admin_activity_log"] = []
        st.rerun()
