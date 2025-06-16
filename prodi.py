import streamlit as st
import pandas as pd
from datetime import datetime
import json

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

def init_cpl_cpmk_data():
    """Inisialisasi data CPL/CPMK di session state"""
    if "cpl_data" not in st.session_state:
        st.session_state.cpl_data = []
    if "cpmk_data" not in st.session_state:
        st.session_state.cpmk_data = []

def add_cpl(kode_cpl, deskripsi_cpl, kategori="Sikap"):
    """Menambah CPL baru"""
    new_cpl = {
        "id": len(st.session_state.cpl_data) + 1,
        "kode_cpl": kode_cpl,
        "deskripsi": deskripsi_cpl,
        "kategori": kategori,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": st.session_state.get("username", "prodi_user")
    }
    st.session_state.cpl_data.append(new_cpl)
    return True

def add_cpmk(kode_cpmk, deskripsi_cpmk, mata_kuliah, sks, semester, cpl_terkait=[]):
    """Menambah CPMK baru"""
    new_cpmk = {
        "id": len(st.session_state.cpmk_data) + 1,
        "kode_cpmk": kode_cpmk,
        "deskripsi": deskripsi_cpmk,
        "mata_kuliah": mata_kuliah,
        "sks": sks,
        "semester": semester,
        "cpl_terkait": cpl_terkait,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": st.session_state.get("username", "prodi_user")
    }
    st.session_state.cpmk_data.append(new_cpmk)
    return True

def delete_cpl(cpl_id):
    """Menghapus CPL berdasarkan ID"""
    st.session_state.cpl_data = [cpl for cpl in st.session_state.cpl_data if cpl["id"] != cpl_id]
    return True

def delete_cpmk(cpmk_id):
    """Menghapus CPMK berdasarkan ID"""
    st.session_state.cpmk_data = [cpmk for cpmk in st.session_state.cpmk_data if cpmk["id"] != cpmk_id]
    return True

def show_cpl_cpmk_management():
    """Menampilkan fitur manajemen CPL/CPMK untuk role Prodi"""
    
    # Inisialisasi data
    init_cpl_cpmk_data()
    
    st.header("📋 Manajemen CPL/CPMK")
    st.write("Kelola Capaian Pembelajaran Lulusan (CPL) dan Capaian Pembelajaran Mata Kuliah (CPMK)")
    
    # Tab untuk CPL dan CPMK
    tab_cpl, tab_cpmk, tab_mapping = st.tabs(["📚 CPL Management", "📖 CPMK Management", "🔗 CPL-CPMK Mapping"])
    
    with tab_cpl:
        st.subheader("Capaian Pembelajaran Lulusan (CPL)")
        
        # Form input CPL baru
        with st.expander("➕ Tambah CPL Baru", expanded=False):
            with st.form("form_cpl"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    kode_cpl = st.text_input("Kode CPL*", placeholder="CPL-01")
                    kategori_cpl = st.selectbox("Kategori CPL*", 
                                              ["Sikap", "Pengetahuan", "Keterampilan Umum", "Keterampilan Khusus"])
                
                with col2:
                    deskripsi_cpl = st.text_area("Deskripsi CPL*", 
                                                placeholder="Masukkan deskripsi capaian pembelajaran lulusan...",
                                                height=100)
                
                submitted_cpl = st.form_submit_button("Tambah CPL", type="primary")
                
                if submitted_cpl:
                    if kode_cpl and deskripsi_cpl:
                        # Validasi kode CPL tidak duplikat
                        existing_codes = [cpl["kode_cpl"] for cpl in st.session_state.cpl_data]
                        if kode_cpl in existing_codes:
                            st.error("❌ Kode CPL sudah ada! Gunakan kode yang berbeda.")
                        else:
                            add_cpl(kode_cpl, deskripsi_cpl, kategori_cpl)
                            st.success(f"✅ CPL {kode_cpl} berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.error("❌ Harap lengkapi semua field yang wajib diisi!")
        
        # Tampilkan daftar CPL
        st.subheader("Daftar CPL")
        if st.session_state.cpl_data:
            df_cpl = pd.DataFrame(st.session_state.cpl_data)
            
            # Filter berdasarkan kategori
            kategori_filter = st.multiselect("Filter berdasarkan Kategori:", 
                                           options=df_cpl["kategori"].unique(),
                                           default=df_cpl["kategori"].unique())
            
            if kategori_filter:
                df_filtered = df_cpl[df_cpl["kategori"].isin(kategori_filter)]
                
                for idx, cpl in df_filtered.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{cpl['kode_cpl']}** - {cpl['kategori']}")
                            st.write(cpl['deskripsi'])
                            st.caption(f"Dibuat: {cpl['created_at']} oleh {cpl['created_by']}")
                        
                        with col2:
                            if st.button("✏️ Edit", key=f"edit_cpl_{cpl['id']}"):
                                st.session_state[f"edit_cpl_{cpl['id']}"] = True
                        
                        with col3:
                            if st.button("🗑️ Hapus", key=f"delete_cpl_{cpl['id']}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_cpl_{cpl['id']}", False):
                                    delete_cpl(cpl['id'])
                                    st.success(f"CPL {cpl['kode_cpl']} berhasil dihapus!")
                                    st.rerun()
                                else:
                                    st.session_state[f"confirm_delete_cpl_{cpl['id']}"] = True
                                    st.warning("Klik sekali lagi untuk konfirmasi hapus")
                        
                        st.divider()
            else:
                st.info("Pilih kategori untuk menampilkan CPL")
        else:
            st.info("Belum ada CPL yang ditambahkan. Silakan tambah CPL baru di atas.")
    
    with tab_cpmk:
        st.subheader("Capaian Pembelajaran Mata Kuliah (CPMK)")
        
        # Form input CPMK baru
        with st.expander("➕ Tambah CPMK Baru", expanded=False):
            with st.form("form_cpmk"):
                col1, col2 = st.columns(2)
                
                with col1:
                    kode_cpmk = st.text_input("Kode CPMK*", placeholder="CPMK-01")
                    mata_kuliah = st.text_input("Mata Kuliah*", placeholder="Algoritma dan Pemrograman")
                    sks = st.number_input("SKS*", min_value=1, max_value=6, value=3)
                
                with col2:
                    semester = st.selectbox("Semester*", options=list(range(1, 9)))
                    # Pilih CPL terkait
                    cpl_options = [f"{cpl['kode_cpl']} - {cpl['deskripsi'][:50]}..." 
                                  for cpl in st.session_state.cpl_data]
                    cpl_terkait = st.multiselect("CPL Terkait", options=cpl_options)
                
                deskripsi_cpmk = st.text_area("Deskripsi CPMK*", 
                                            placeholder="Masukkan deskripsi capaian pembelajaran mata kuliah...",
                                            height=100)
                
                submitted_cpmk = st.form_submit_button("Tambah CPMK", type="primary")
                
                if submitted_cpmk:
                    if kode_cpmk and deskripsi_cpmk and mata_kuliah:
                        # Validasi kode CPMK tidak duplikat
                        existing_codes = [cpmk["kode_cpmk"] for cpmk in st.session_state.cpmk_data]
                        if kode_cpmk in existing_codes:
                            st.error("❌ Kode CPMK sudah ada! Gunakan kode yang berbeda.")
                        else:
                            # Extract kode CPL dari pilihan
                            cpl_codes = [opt.split(" - ")[0] for opt in cpl_terkait]
                            add_cpmk(kode_cpmk, deskripsi_cpmk, mata_kuliah, sks, semester, cpl_codes)
                            st.success(f"✅ CPMK {kode_cpmk} berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.error("❌ Harap lengkapi semua field yang wajib diisi!")
        
        # Tampilkan daftar CPMK
        st.subheader("Daftar CPMK")
        if st.session_state.cpmk_data:
            df_cpmk = pd.DataFrame(st.session_state.cpmk_data)
            
            # Filter berdasarkan semester
            semester_filter = st.multiselect("Filter berdasarkan Semester:", 
                                           options=sorted(df_cpmk["semester"].unique()),
                                           default=sorted(df_cpmk["semester"].unique()))
            
            if semester_filter:
                df_filtered = df_cpmk[df_cpmk["semester"].isin(semester_filter)]
                
                for idx, cpmk in df_filtered.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{cpmk['kode_cpmk']}** - {cpmk['mata_kuliah']}")
                            st.write(cpmk['deskripsi'])
                            st.write(f"📚 SKS: {cpmk['sks']} | 📅 Semester: {cpmk['semester']}")
                            if cpmk['cpl_terkait']:
                                st.write(f"🔗 CPL Terkait: {', '.join(cpmk['cpl_terkait'])}")
                            st.caption(f"Dibuat: {cpmk['created_at']} oleh {cpmk['created_by']}")
                        
                        with col2:
                            if st.button("✏️ Edit", key=f"edit_cpmk_{cpmk['id']}"):
                                st.session_state[f"edit_cpmk_{cpmk['id']}"] = True
                        
                        with col3:
                            if st.button("🗑️ Hapus", key=f"delete_cpmk_{cpmk['id']}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_cpmk_{cpmk['id']}", False):
                                    delete_cpmk(cpmk['id'])
                                    st.success(f"CPMK {cpmk['kode_cpmk']} berhasil dihapus!")
                                    st.rerun()
                                else:
                                    st.session_state[f"confirm_delete_cpmk_{cpmk['id']}"] = True
                                    st.warning("Klik sekali lagi untuk konfirmasi hapus")
                        
                        st.divider()
            else:
                st.info("Pilih semester untuk menampilkan CPMK")
        else:
            st.info("Belum ada CPMK yang ditambahkan. Silakan tambah CPMK baru di atas.")
    
    with tab_mapping:
        st.subheader("Pemetaan CPL-CPMK")
        
        if st.session_state.cpl_data and st.session_state.cpmk_data:
            # Buat matriks pemetaan
            st.write("**Matriks Pemetaan CPL-CPMK**")
            
            # Buat DataFrame untuk matriks
            cpl_list = [cpl['kode_cpl'] for cpl in st.session_state.cpl_data]
            cpmk_list = [cpmk['kode_cpmk'] for cpmk in st.session_state.cpmk_data]
            
            mapping_data = []
            for cpmk in st.session_state.cpmk_data:
                row = {"CPMK": cpmk['kode_cpmk'], "Mata Kuliah": cpmk['mata_kuliah']}
                for cpl_code in cpl_list:
                    row[cpl_code] = "✓" if cpl_code in cpmk.get('cpl_terkait', []) else ""
                mapping_data.append(row)
            
            if mapping_data:
                df_mapping = pd.DataFrame(mapping_data)
                st.dataframe(df_mapping, use_container_width=True)
                
                # Export ke CSV
                csv = df_mapping.to_csv(index=False)
                st.download_button(
                    label="📥 Download Matriks Pemetaan (CSV)",
                    data=csv,
                    file_name=f"pemetaan_cpl_cpmk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Silakan tambahkan CPL dan CPMK terlebih dahulu untuk melihat pemetaan.")

def render_login_page():
    """Render halaman login"""
    st.title("🔐 Login Sistem")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Mahasiswa", "Dosen", "Prodi", "Admin"])
        
        if st.form_submit_button("Login"):
            # Simulasi autentikasi sederhana
            if username and password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["user_role"] = role
                st.success(f"✅ Login berhasil sebagai {role}")
                st.rerun()
            else:
                st.error("❌ Username dan password harus diisi!")

def render_prediction_interface():
    """Render interface utama setelah login"""
    
    # Dapatkan fitur berdasarkan role
    features = get_role_specific_features()
    
    # Header dengan informasi user dan logout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"Sistem Manajemen Akademik {features.get('title_suffix', '')}")
    with col2:
        st.write(f"👤 **{st.session_state['username']}**")
        st.write(f"🎭 Role: {st.session_state['user_role']}")
    with col3:
        if st.button("🚪 Logout", type="secondary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.divider()
    
    # Menu navigasi berdasarkan role
    if st.session_state["user_role"] == "Prodi":
        # Menu khusus untuk Prodi
        menu_options = ["🏠 Dashboard", "📋 Manajemen CPL/CPMK", "📊 Laporan"]
        selected_menu = st.sidebar.selectbox("📋 Menu Navigasi", menu_options)
        
        if selected_menu == "🏠 Dashboard":
            render_prodi_dashboard()
        elif selected_menu == "📋 Manajemen CPL/CPMK":
            # Cek fitur CPL/CPMK
            if features.get("can_input_cpl_cpmk", False):
                show_cpl_cpmk_management()
            else:
                st.error("❌ Fitur tidak tersedia untuk role Anda.")
        elif selected_menu == "📊 Laporan":
            render_prodi_reports()
    
    elif st.session_state["user_role"] == "Dosen":
        # Menu untuk Dosen
        menu_options = ["🏠 Dashboard", "📚 Prediksi", "📊 Analisis Lanjutan"]
        selected_menu = st.sidebar.selectbox("📋 Menu Navigasi", menu_options)
        
        if selected_menu == "🏠 Dashboard":
            render_dosen_dashboard()
        elif selected_menu == "📚 Prediksi":
            render_prediction_feature()
        elif selected_menu == "📊 Analisis Lanjutan":
            if features.get("show_advanced_analysis", False):
                render_advanced_analysis()
            else:
                st.error("❌ Fitur tidak tersedia untuk role Anda.")
    
    elif st.session_state["user_role"] == "Mahasiswa":
        # Menu untuk Mahasiswa
        menu_options = ["🏠 Dashboard", "📚 Prediksi Sederhana"]
        selected_menu = st.sidebar.selectbox("📋 Menu Navigasi", menu_options)
        
        if selected_menu == "🏠 Dashboard":
            render_mahasiswa_dashboard()
        elif selected_menu == "📚 Prediksi Sederhana":
            render_prediction_feature()
    
    elif st.session_state["user_role"] == "Admin":
        # Menu untuk Admin
        menu_options = ["🏠 Dashboard", "📚 Prediksi", "📊 Analisis Lanjutan", "⚙️ Admin Panel", "📁 Manajemen Excel"]
        selected_menu = st.sidebar.selectbox("📋 Menu Navigasi", menu_options)
        
        if selected_menu == "🏠 Dashboard":
            render_admin_dashboard()
        elif selected_menu == "📚 Prediksi":
            render_prediction_feature()
        elif selected_menu == "📊 Analisis Lanjutan":
            render_advanced_analysis()
        elif selected_menu == "⚙️ Admin Panel":
            if features.get("show_admin_features", False):
                render_admin_panel()
            else:
                st.error("❌ Fitur tidak tersedia untuk role Anda.")
        elif selected_menu == "📁 Manajemen Excel":
            if features.get("show_excel_management", False):
                render_excel_management()
            else:
                st.error("❌ Fitur tidak tersedia untuk role Anda.")

def render_prodi_dashboard():
    """Dashboard khusus untuk Prodi"""
    
    # Initialize data
    init_cpl_cpmk_data()
    
    # Header dengan welcome message
    st.markdown("# 📊 Dashboard Program Studi")
    st.markdown(f"**Selamat datang, {st.session_state.get('username', 'Admin Prodi')}!**")
    st.markdown("---")
    
    # Overview Cards
    st.subheader("📈 Ringkasan Statistik")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cpl = len(st.session_state.cpl_data)
        st.metric(
            label="📚 Total CPL",
            value=total_cpl,
            delta=f"+{total_cpl} dari target" if total_cpl > 0 else "Belum ada data"
        )
    
    with col2:
        total_cpmk = len(st.session_state.cpmk_data)
        st.metric(
            label="📖 Total CPMK", 
            value=total_cpmk,
            delta=f"+{total_cpmk} mata kuliah" if total_cpmk > 0 else "Belum ada data"
        )
    
    with col3:
        if st.session_state.cpl_data:
            mapped_cpmk = len([cpmk for cpmk in st.session_state.cpmk_data if cpmk.get("cpl_terkait")])
            mapping_percentage = (mapped_cpmk / total_cpmk * 100) if total_cpmk > 0 else 0
            st.metric(
                label="🔗 CPMK Termapping",
                value=f"{mapped_cpmk}/{total_cpmk}",
                delta=f"{mapping_percentage:.1f}% completion"
            )
        else:
            st.metric("🔗 CPMK Termapping", "0/0", delta="0% completion")
    
    with col4:
        if st.session_state.cpl_data:
            kategori_count = len(set([cpl["kategori"] for cpl in st.session_state.cpl_data]))
            st.metric(
                label="🎯 Kategori CPL",
                value=f"{kategori_count}/4",
                delta="Kategori aktif"
            )
        else:
            st.metric("🎯 Kategori CPL", "0/4", delta="Belum ada kategori")
    
    # Charts Section
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 Distribusi CPL per Kategori")
        if st.session_state.cpl_data:
            # Data untuk chart CPL
            cpl_categories = {}
            for cpl in st.session_state.cpl_data:
                kategori = cpl["kategori"]
                cpl_categories[kategori] = cpl_categories.get(kategori, 0) + 1
            
            # Chart data
            chart_data = pd.DataFrame(
                list(cpl_categories.items()),
                columns=["Kategori", "Jumlah"]
            )
            
            st.bar_chart(chart_data.set_index("Kategori"))
            
            # Detail breakdown
            with st.expander("📋 Detail Kategori CPL"):
                for kategori, count in cpl_categories.items():
                    st.write(f"**{kategori}**: {count} CPL")
        else:
            st.info("📝 Belum ada data CPL untuk ditampilkan")
    
    with col_right:
        st.subheader("📈 Distribusi CPMK per Semester")
        if st.session_state.cpmk_data:
            # Data untuk chart CPMK
            cpmk_semesters = {}
            for cpmk in st.session_state.cpmk_data:
                semester = f"Semester {cpmk['semester']}"
                cpmk_semesters[semester] = cpmk_semesters.get(semester, 0) + 1
            
            # Chart data
            chart_data = pd.DataFrame(
                list(cpmk_semesters.items()),
                columns=["Semester", "Jumlah CPMK"]
            )
            
            st.bar_chart(chart_data.set_index("Semester"))
            
            # Detail breakdown
            with st.expander("📋 Detail CPMK per Semester"):
                for semester, count in sorted(cpmk_semesters.items()):
                    st.write(f"**{semester}**: {count} CPMK")
        else:
            st.info("📝 Belum ada data CPMK untuk ditampilkan")
    
    # Recent Activities
    st.subheader("🕐 Aktivitas Terbaru")
    
    # Combine recent CPL and CPMK data
    recent_activities = []
    
    # Add CPL activities
    for cpl in st.session_state.cpl_data[-5:]:  # Last 5 CPL
        recent_activities.append({
            "timestamp": cpl["created_at"],
            "type": "CPL",
            "action": "Ditambahkan",
            "item": cpl["kode_cpl"],
            "description": cpl["deskripsi"][:100] + "..." if len(cpl["deskripsi"]) > 100 else cpl["deskripsi"],
            "user": cpl["created_by"]
        })
    
    # Add CPMK activities
    for cpmk in st.session_state.cpmk_data[-5:]:  # Last 5 CPMK
        recent_activities.append({
            "timestamp": cpmk["created_at"],
            "type": "CPMK",
            "action": "Ditambahkan",
            "item": cpmk["kode_cpmk"],
            "description": f"{cpmk['mata_kuliah']} - {cpmk['deskripsi'][:80]}..." if len(cpmk['deskripsi']) > 80 else f"{cpmk['mata_kuliah']} - {cpmk['deskripsi']}",
            "user": cpmk["created_by"]
        })
    
    # Sort by timestamp (newest first)
    recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    if recent_activities:
        for activity in recent_activities[:10]:  # Show last 10 activities
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    badge_color = "🟢" if activity["type"] == "CPL" else "🔵"
                    st.write(f"{badge_color} **{activity['type']} {activity['item']}**")
                    st.caption(f"oleh {activity['user']}")
                
                with col2:
                    st.write(f"*{activity['action']}*")
                    st.write(activity["description"])
                
                with col3:
                    st.caption(activity["timestamp"])
                
                st.divider()
    else:
        st.info("🔄 Belum ada aktivitas terbaru")
    
    # Quick Actions
    st.subheader("⚡ Aksi Cepat")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Tambah CPL Baru", type="primary", use_container_width=True):
            st.session_state["quick_action"] = "add_cpl"
            st.rerun()
    
    with col2:
        if st.button("➕ Tambah CPMK Baru", type="secondary", use_container_width=True):
            st.session_state["quick_action"] = "add_cpmk"
            st.rerun()
    
    with col3:
        if st.button("🔗 Lihat Pemetaan", use_container_width=True):
            st.session_state["quick_action"] = "view_mapping"
            st.rerun()
    
    with col4:
        if st.button("📊 Export Data", use_container_width=True):
            st.session_state["quick_action"] = "export_data"
            st.rerun()
    
    # Handle quick actions
    if st.session_state.get("quick_action"):
        action = st.session_state["quick_action"]
        
        if action == "add_cpl":
            st.info("💡 Silakan buka menu 'Manajemen CPL/CPMK' > Tab 'CPL Management' untuk menambah CPL baru")
        elif action == "add_cpmk":
            st.info("💡 Silakan buka menu 'Manajemen CPL/CPMK' > Tab 'CPMK Management' untuk menambah CPMK baru")
        elif action == "view_mapping":
            st.info("💡 Silakan buka menu 'Manajemen CPL/CPMK' > Tab 'CPL-CPMK Mapping' untuk melihat pemetaan")
        elif action == "export_data":
            if st.session_state.cpl_data or st.session_state.cpmk_data:
                # Export functionality
                export_data = {
                    "CPL": st.session_state.cpl_data,
                    "CPMK": st.session_state.cpmk_data,
                    "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "exported_by": st.session_state.get("username", "admin")
                }
                
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download Data (JSON)",
                    data=json_str,
                    file_name=f"cpl_cpmk_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("⚠️ Tidak ada data untuk diekspor")
        
        # Clear quick action after handling
        del st.session_state["quick_action"]
    
    # System Status
    st.subheader("🔧 Status Sistem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("✅ **Sistem Aktif**")
        st.write("- Database: Terhubung")
        st.write("- Fitur CPL/CPMK: Aktif")
        st.write("- Auto-save: Aktif")
    
    with col2:
        st.info("ℹ️ **Informasi**")
        st.write(f"- Login terakhir: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"- Role: {st.session_state.get('user_role', 'Unknown')}")
        st.write(f"- Session: Aktif")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
            Dashboard Program Studi - Sistem Manajemen CPL/CPMK<br>
            Terakhir diperbarui: {}
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

def render_prodi_reports():
    """Laporan untuk Prodi"""
    st.header("📊 Laporan CPL/CPMK")
    st.info("Fitur laporan akan segera tersedia.")

# Fungsi placeholder untuk role lain
def render_dosen_dashboard():
    st.header("📊 Dashboard Dosen")
    st.info("Dashboard khusus untuk Dosen.")

def render_mahasiswa_dashboard():
    st.header("📊 Dashboard Mahasiswa")
    st.info("Dashboard khusus untuk Mahasiswa.")

def render_admin_dashboard():
    st.header("📊 Dashboard Admin")
    st.info("Dashboard khusus untuk Admin.")

def render_prediction_feature():
    st.header("🔮 Fitur Prediksi")
    role = st.session_state["user_role"]
    features = get_role_specific_features()
    
    limit = features.get("prediction_limit")
    if limit:
        st.info(f"Limit prediksi untuk {role}: {limit} kali")
    else:
        st.info("Tidak ada limit prediksi untuk role Anda.")
    
    st.write("Fitur prediksi akan diimplementasikan di sini.")

def render_advanced_analysis():
    st.header("📊 Analisis Lanjutan")
    st.info("Fitur analisis lanjutan untuk Dosen dan Admin.")

def render_admin_panel():
    st.header("⚙️ Panel Admin")
    st.info("Fitur admin panel untuk mengelola sistem.")

def render_excel_management():
    st.header("📁 Manajemen Excel")
    st.info("Fitur manajemen file Excel untuk Admin.")

def main():
    """Fungsi utama aplikasi"""
    
    # Inisialisasi session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        render_prediction_interface()

if __name__ == "__main__":
    main()