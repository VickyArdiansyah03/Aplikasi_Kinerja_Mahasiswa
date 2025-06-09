import os
from openpyxl import load_workbook
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np

# ======================= PAGE CONFIGURATION =======================
st.set_page_config(
    page_title="Aplikasi Prediksi Kinerja Mahasiswa", 
    layout="centered", 
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# ======================= LOAD DATA MAHASISWA & DOSEN =======================
def load_mahasiswa_data():
    try:
        if os.path.exists("data/Data_Mahasiswa.xlsx"):
            df = pd.read_excel("data/Data_Mahasiswa.xlsx")
            # Ensure required columns exist
            required_columns = ['NIM', 'Nama Mahasiswa', 'Jurusan', 'IPK']
            if all(col in df.columns for col in required_columns):
                return df
            else:
                st.error("File data mahasiswa tidak memiliki kolom yang diperlukan.")
                return None
        else:
            st.warning("File data mahasiswa tidak ditemukan.")
            return pd.DataFrame(columns=['NIM', 'Nama Mahasiswa', 'Jurusan', 'IPK', 'Jumlah SKS', 
                                       'Nilai Mata Kuliah', 'Jumlah Kehadiran', 'Jumlah Tugas',
                                       'Skor Penilaian Dosen', 'Waktu Penyelesaian'])
    except Exception as e:
        st.error(f"Gagal memuat data mahasiswa: {str(e)}")
        return None

def load_dosen_data():
    try:
        if os.path.exists("data/Data_Dosen.xlsx"):
            df = pd.read_excel("data/Data_Dosen.xlsx")
            return df
        else:
            st.warning("File data dosen tidak ditemukan.")
            return pd.DataFrame(columns=['Nama Dosen', 'Jurusan'])
    except Exception as e:
        st.error(f"Gagal memuat data dosen: {str(e)}")
        return None

# Load data
df_mahasiswa = load_mahasiswa_data()
df_dosen = load_dosen_data()

# ======================= SESSION STATE =======================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

# Admin users
admin_users = ["admin1", "admin2"]

# Dosen data
dosen_list = ["Dr. Ahmad", "Prof. Budi", "Dr. Siti", "Dr. Rina", "Ir.Bambang"]

def login(nama, role):
    try:
        nama = nama.strip()
        if not nama:
            st.error("Nama tidak boleh kosong")
            return False
            
        if role == "Mahasiswa":
            if df_mahasiswa is not None and not df_mahasiswa.empty:
                if nama in df_mahasiswa["Nama Mahasiswa"].values:
                    st.session_state.update({
                        "logged_in": True, 
                        "user_role": "Mahasiswa", 
                        "user_name": nama
                    })
                    return True
                else:
                    st.error("Nama mahasiswa tidak ditemukan")
                    return False
            else:
                st.error("Database mahasiswa kosong atau tidak ditemukan")
                return False
                
        elif role == "Dosen":
            if nama in dosen_list:
                st.session_state.update({
                    "logged_in": True, 
                    "user_role": "Dosen", 
                    "user_name": nama
                })
                return True
            else:
                st.error("Nama dosen tidak valid")
                return False
                
        elif role == "Admin":
            if nama in admin_users:
                st.session_state.update({
                    "logged_in": True, 
                    "user_role": "Admin", 
                    "user_name": nama
                })
                return True
            else:
                st.error("Kredensial admin tidak valid")
                return False
                
        return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False

# ======================= FUNGSI LOGOUT =======================
def logout():
    st.session_state.update({
        "logged_in": False, 
        "user_role": None, 
        "user_name": None
    })
    st.rerun()

# ======================= HALAMAN LOGIN =======================
if not st.session_state["logged_in"]:
    with st.container():
        st.title("🔐 Login Prediksi Kinerja Mahasiswa")
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://via.placeholder.com/150", width=150)
        with col2:
            nama_user = st.text_input("🧑 Nama Lengkap", key="nama_login")
            role = st.selectbox(
                "👥 Masuk Sebagai", 
                ["Mahasiswa", "Dosen", "Admin"],
                key="role_login"
            )

        if st.button("🚀 Login", key="btn_login"):
            if login(nama_user, role):
                st.success(f"✅ Selamat datang, {nama_user}!")
                st.rerun()

# ======================= HALAMAN MAHASISWA =======================
elif st.session_state["user_role"] == "Mahasiswa":
    # Sidebar
    st.sidebar.markdown("### 🔑 Akun Mahasiswa")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout", key="logout_mhs"):
        logout()
    
    # Main content
    st.subheader(f"🎓 Halo, {st.session_state['user_name']}")
    st.markdown("---")
    
    if df_mahasiswa is not None and not df_mahasiswa.empty:
        mahasiswa_data = df_mahasiswa[df_mahasiswa["Nama Mahasiswa"] == st.session_state["user_name"]]
        
        if not mahasiswa_data.empty:
            # Display student data
            with st.expander("📄 Data Saya"):
                st.dataframe(mahasiswa_data.style.highlight_max(axis=0, color='lightgreen'), use_container_width=True)
            
            # Get student details
            ipk = mahasiswa_data["IPK"].iloc[0]
            jurusan = mahasiswa_data["Jurusan"].iloc[0]
            
            # Prediction logic
            if ipk >= 2.50:
                prediksi = "Lulus"
                prob_lulus = 90.0 if jurusan == "Teknik Informatika" else 85.0
            else:
                prediksi = "Tidak Lulus"
                prob_lulus = 20.0 if jurusan == "Teknik Informatika" else 15.0
            prob_tidak_lulus = 100.0 - prob_lulus
            
            # Display prediction
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🎯 Prediksi Kelulusan", prediksi)
            with col2:
                st.metric("📊 IPK Saat Ini", f"{ipk:.2f}")
            
            # Metrics
            st.markdown("### Probabilitas Kelulusan")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Probabilitas Lulus", f"{prob_lulus:.1f}%", delta=f"+{prob_lulus-50:.1f}%" if prob_lulus > 50 else f"{prob_lulus-50:.1f}%")
            with col2:
                st.metric("❌ Probabilitas Tidak Lulus", f"{prob_tidak_lulus:.1f}%", delta=f"+{prob_tidak_lulus-50:.1f}%" if prob_tidak_lulus > 50 else f"{prob_tidak_lulus-50:.1f}%")
            
            # Visualization
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(["Lulus", "Tidak Lulus"], [prob_lulus, prob_tidak_lulus], color=["#4CAF50", "#FF5252"])
            ax.set_xlim(0, 100)
            ax.set_title("Probabilitas Kelulusan")
            st.pyplot(fig)
            
            # Additional metrics
            st.markdown("### 📈 Statistik Tambahan")
            if "Jumlah SKS" in mahasiswa_data.columns:
                sks = mahasiswa_data["Jumlah SKS"].iloc[0]
                st.progress(int(sks/144*100), f"Progress SKS: {sks}/144 ({sks/144*100:.1f}%)")
            
        else:
            st.warning("⚠ Data tidak ditemukan untuk mahasiswa ini.")
    else:
        st.error("Database mahasiswa tidak tersedia.")

# ======================= HALAMAN DOSEN =======================
elif st.session_state["user_role"] == "Dosen":
    # Sidebar
    st.sidebar.markdown("### 🔑 Akun Dosen")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout", key="logout_dosen"):
        logout()
    
    # Main content
    st.subheader(f"📚 Selamat datang, {st.session_state['user_name']}")
    st.markdown("---")
    
    # Jurusan mapping
    jurusan_mapping = {
        "Dr. Ahmad": "Teknik Informatika",
        "Prof. Budi": "Sistem Informasi",
        "Dr. Siti": "Akuntansi",
        "Dr. Rina": "Manajemen",
        "Ir.Bambang": "Teknik Elektro"
    }
    
    current_jurusan = jurusan_mapping.get(st.session_state["user_name"], "Unknown")
    st.markdown(f"**Jurusan Anda:** {current_jurusan}")
    
    # File upload
    uploaded_file = st.file_uploader("📤 Upload file Excel data mahasiswa", type=["xlsx"], key="upload_dosen")
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Check required columns
            required_columns = ['Nama Mahasiswa', 'Jurusan', 'IPK']
            if not all(col in df_uploaded.columns for col in required_columns):
                st.error("File yang diupload tidak memiliki kolom yang diperlukan (Nama Mahasiswa, Jurusan, IPK)")
            else:
                # Filter by department
                df_filtered = df_uploaded[df_uploaded["Jurusan"] == current_jurusan]
                
                if not df_filtered.empty:
                    # Display data
                    with st.expander("🎓 Data Mahasiswa", expanded=True):
                        st.dataframe(df_filtered.style.background_gradient(subset=['IPK'], cmap='YlGn'), use_container_width=True)
                    
                    # Add predictions
                    df_filtered['Prediksi'] = np.where(df_filtered['IPK'] >= 2.50, "Lulus", "Tidak Lulus")
                    df_filtered['Prob_Lulus'] = np.where(
                        (df_filtered['Jurusan'] == "Teknik Informatika") & (df_filtered['IPK'] >= 2.50), 90.0,
                        np.where(df_filtered['IPK'] >= 2.50, 85.0, 
                                np.where(df_filtered['Jurusan'] == "Teknik Informatika", 20.0, 15.0))
                    df_filtered['Prob_Tidak_Lulus'] = 100.0 - df_filtered['Prob_Lulus']
                    
                    # Show predictions
                    st.markdown("#### 🔮 Prediksi Kelulusan")
                    st.dataframe(df_filtered[['Nama Mahasiswa', 'Jurusan', 'IPK', 'Prediksi', 'Prob_Lulus', 'Prob_Tidak_Lulus']]
                                .sort_values('IPK', ascending=False)
                                .style.background_gradient(subset=['IPK'], cmap='YlGn'))
                    
                    # Statistics
                    st.markdown("#### 📊 Statistik Kelulusan")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Mahasiswa", len(df_filtered))
                    with col2:
                        st.metric("Rata-rata IPK", f"{df_filtered['IPK'].mean():.2f}")
                    with col3:
                        st.metric("Persentase Lulus", f"{len(df_filtered[df_filtered['Prediksi'] == 'Lulus'])/len(df_filtered)*100:.1f}%")
                    
                    # Visualizations
                    st.markdown("#### 📈 Visualisasi Data")
                    
                    tab1, tab2 = st.tabs(["Distribusi IPK", "Probabilitas Kelulusan"])
                    
                    with tab1:
                        fig1, ax1 = plt.subplots(figsize=(10, 4))
                        ax1.hist(df_filtered["IPK"], bins=np.arange(0, 4.1, 0.5), color='#4CAF50', edgecolor='black')
                        ax1.set_title("Distribusi IPK Mahasiswa")
                        ax1.set_xlabel("IPK")
                        ax1.set_ylabel("Jumlah Mahasiswa")
                        st.pyplot(fig1)
                    
                    with tab2:
                        fig2, ax2 = plt.subplots(figsize=(8, 4))
                        labels = ['Lulus', 'Tidak Lulus']
                        sizes = [
                            len(df_filtered[df_filtered['Prediksi'] == 'Lulus']),
                            len(df_filtered[df_filtered['Prediksi'] == 'Tidak Lulus'])
                        ]
                        colors = ['#4CAF50', '#FF5252']
                        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                        ax2.axis('equal')
                        st.pyplot(fig2)
                    
                else:
                    st.warning(f"⚠ Tidak ada data mahasiswa untuk jurusan {current_jurusan}.")
        
        except Exception as e:
            st.error(f"❌ Gagal memproses file: {str(e)}")
    else:
        st.info("⬆ Silakan upload file Excel data mahasiswa untuk melihat analisis.")

# ======================= HALAMAN ADMIN =======================
elif st.session_state["user_role"] == "Admin":
    # Sidebar
    st.sidebar.markdown("### 🛠 Akun Admin")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    
    # Navigation
    st.sidebar.markdown("### 📊 Menu Admin")
    menu_option = st.sidebar.radio(
        "Pilih opsi:",
        ["📤 Upload Data", "➕ Tambah Data", "📊 Statistik", "🔍 Cari Data"],
        index=0
    )
    
    if st.sidebar.button("🚪 Logout", key="logout_admin"):
        logout()
    
    # Main content
    st.subheader(f"📊 Selamat datang Admin, {st.session_state['user_name']}")
    st.markdown("---")
    
    # Menu options
    if menu_option == "📤 Upload Data":
        st.markdown("### 📤 Upload Data Mahasiswa")
        st.markdown("Silakan upload file Excel data mahasiswa:")
        
        uploaded_file = st.file_uploader("Pilih file Excel", type=["xlsx"], key="upload_admin")
        
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_excel(uploaded_file, engine='openpyxl')
                
                # Check required columns
                required_columns = ['NIM', 'Nama Mahasiswa', 'Jurusan', 'IPK']
                if not all(col in df_uploaded.columns for col in required_columns):
                    st.error("File harus memiliki kolom: NIM, Nama Mahasiswa, Jurusan, IPK")
                else:
                    # Show preview
                    st.markdown("#### Preview Data")
                    st.dataframe(df_uploaded.head())
                    
                    # Save option
                    if st.button("💾 Simpan Data", key="save_data"):
                        try:
                            # Save to Excel
                            df_uploaded.to_excel("data/Data_Mahasiswa.xlsx", index=False)
                            st.success("✅ Data berhasil disimpan!")
                            st.balloons()
                            # Reload data
                            df_mahasiswa = load_mahasiswa_data()
                        except Exception as e:
                            st.error(f"❌ Gagal menyimpan data: {str(e)}")
            
            except Exception as e:
                st.error(f"❌ Gagal membaca file: {str(e)}")
    
    elif menu_option == "➕ Tambah Data":
        st.markdown("### ➕ Tambah Data Mahasiswa Baru")
        
        with st.form("form_tambah_data", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nim = st.text_input("NIM", value=f"{random.randint(10000000, 99999999)}", key="nim")
                nama = st.text_input("Nama Mahasiswa*", key="nama")
                jurusan = st.selectbox(
                    "Jurusan*", 
                    ["Teknik Informatika", "Sistem Informasi", "Akuntansi", "Teknik Elektro", "Manajemen"], 
                    key="jurusan"
                )
                ipk = st.number_input(
                    "IPK*", 
                    min_value=0.0, 
                    max_value=4.0, 
                    step=0.01, 
                    format="%.2f",
                    key="ipk"
                )
                
            with col2:
                sks = st.number_input("Jumlah SKS", min_value=0, max_value=200, value=100, key="sks")
                nilai_matkul = st.number_input("Nilai Mata Kuliah", min_value=0.0, max_value=100.0, value=75.0, key="nilai")
                kehadiran = st.number_input("Jumlah Kehadiran", min_value=0, max_value=20, value=15, key="kehadiran")
                tugas = st.number_input("Jumlah Tugas", min_value=0, max_value=20, value=10, key="tugas")
                
            penilaian_dosen = st.slider("Skor Penilaian Dosen", 1.0, 5.0, 3.5, 0.1, key="penilaian")
            waktu_penyelesaian = st.selectbox(
                "Waktu Penyelesaian", 
                ["Cepat", "Normal", "Lambat"], 
                key="waktu"
            )
            
            submitted = st.form_submit_button("💾 Simpan Data")
            
            if submitted:
                if not nama or not jurusan:
                    st.warning("⚠ Harap isi Nama dan Jurusan!")
                else:
                    new_data = pd.DataFrame([{
                        "NIM": nim,
                        "Nama Mahasiswa": nama,
                        "Jurusan": jurusan,
                        "IPK": ipk,
                        "Jumlah SKS": sks,
                        "Nilai Mata Kuliah": nilai_matkul,
                        "Jumlah Kehadiran": kehadiran,
                        "Jumlah Tugas": tugas,
                        "Skor Penilaian Dosen": penilaian_dosen,
                        "Waktu Penyelesaian": waktu_penyelesaian,
                    }])
                    
                    try:
                        # Load existing data
                        if os.path.exists("data/Data_Mahasiswa.xlsx"):
                            existing_data = pd.read_excel("data/Data_Mahasiswa.xlsx")
                            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                        else:
                            updated_data = new_data
                        
                        # Save updated data
                        updated_data.to_excel("data/Data_Mahasiswa.xlsx", index=False)
                        st.success(f"✅ Data mahasiswa {nama} berhasil ditambahkan!")
                        st.balloons()
                        # Reload data
                        df_mahasiswa = load_mahasiswa_data()
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan data: {str(e)}")
    
    elif menu_option == "📊 Statistik":
        st.markdown("### 📊 Statistik Data Mahasiswa")
        
        if df_mahasiswa is not None and not df_mahasiswa.empty:
            # Overall statistics
            st.markdown("#### 📈 Statistik Umum")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mahasiswa", len(df_mahasiswa))
            with col2:
                st.metric("Rata-rata IPK", f"{df_mahasiswa['IPK'].mean():.2f}")
            with col3:
                st.metric("IPK Tertinggi", f"{df_mahasiswa['IPK'].max():.2f}")
            
            # Department distribution
            st.markdown("#### 🏫 Distribusi Jurusan")
            jurusan_counts = df_mahasiswa['Jurusan'].value_counts()
            
            tab1, tab2 = st.tabs(["Diagram Pie", "Diagram Batang"])
            
            with tab1:
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                ax1.pie(jurusan_counts, 
                       labels=jurusan_counts.index, 
                       autopct='%1.1f%%',
                       startangle=90,
                       colors=plt.cm.Pastel1.colors)
                ax1.axis('equal')
                ax1.set_title("Distribusi Mahasiswa per Jurusan")
                st.pyplot(fig1)
            
            with tab2:
                fig2, ax2 = plt.subplots(figsize=(10, 4))
                jurusan_counts.plot(kind='bar', color=plt.cm.Pastel1.colors, ax=ax2)
                ax2.set_title("Jumlah Mahasiswa per Jurusan")
                ax2.set_xlabel("Jurusan")
                ax2.set_ylabel("Jumlah Mahasiswa")
                plt.xticks(rotation=45)
                st.pyplot(fig2)
            
            # IPK distribution
            st.markdown("#### 📊 Distribusi IPK")
            
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            ax3.hist(df_mahasiswa['IPK'], 
                    bins=np.arange(0, 4.1, 0.25), 
                    color='skyblue', 
                    edgecolor='black')
            ax3.set_title("Distribusi IPK Semua Mahasiswa")
            ax3.set_xlabel("IPK")
            ax3.set_ylabel("Jumlah Mahasiswa")
            st.pyplot(fig3)
            
            # IPK by department
            st.markdown("#### 📚 IPK per Jurusan")
            
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            departments = df_mahasiswa['Jurusan'].unique()
            
            # Create boxplot data
            boxplot_data = []
            for dept in departments:
                boxplot_data.append(df_mahasiswa[df_mahasiswa['Jurusan'] == dept]['IPK'])
            
            # Plot boxplot
            bp = ax4.boxplot(boxplot_data, 
                           patch_artist=True,
                           labels=departments)
            
            # Customize colors
            colors = plt.cm.Pastel1.colors
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax4.set_title("Distribusi IPK per Jurusan")
            ax4.set_ylabel("IPK")
            plt.xticks(rotation=45)
            st.pyplot(fig4)
            
        else:
            st.warning("Database mahasiswa kosong. Silakan tambah data terlebih dahulu.")
    
    elif menu_option == "🔍 Cari Data":
        st.markdown("### 🔍 Cari Data Mahasiswa")
        
        search_option = st.radio(
            "Cari berdasarkan:",
            ["NIM", "Nama Mahasiswa", "Jurusan"],
            horizontal=True
        )
        
        search_query = st.text_input(f"Masukkan {search_option}")
        
        if st.button("🔎 Cari"):
            if df_mahasiswa is not None and not df_mahasiswa.empty:
                if search_query:
                    if search_option == "NIM":
                        result = df_mahasiswa[df_mahasiswa['NIM'].astype(str).str.contains(search_query, case=False)]
                    elif search_option == "Nama Mahasiswa":
                        result = df_mahasiswa[df_mahasiswa['Nama Mahasiswa'].str.contains(search_query, case=False)]
                    else:
                        result = df_mahasiswa[df_mahasiswa['Jurusan'].str.contains(search_query, case=False)]
                    
                    if not result.empty:
                        st.dataframe(result.style.highlight_max(subset=['IPK'], color='lightgreen'), use_container_width=True)
                        
                        # Show statistics for the search results
                        st.markdown("#### 📊 Statistik Hasil Pencarian")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Jumlah Mahasiswa", len(result))
                            st.metric("Rata-rata IPK", f"{result['IPK'].mean():.2f}")
                        with col2:
                            st.metric("IPK Tertinggi", f"{result['IPK'].max():.2f}")
                            st.metric("IPK Terendah", f"{result['IPK'].min():.2f}")
                    else:
                        st.warning("Tidak ditemukan data yang sesuai.")
                else:
                    st.warning("Silakan masukkan kata kunci pencarian.")
            else:
                st.warning("Database mahasiswa kosong.")
