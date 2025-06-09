import os
from openpyxl import load_workbook
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# ======================= PAGE CONFIGURATION =======================
st.set_page_config(page_title="Aplikasi Prediksi Kinerja Mahasiswa", layout="centered", page_icon="🎓")

# ======================= LOAD DATA MAHASISWA & DOSEN =======================
def load_mahasiswa_data():
    try:
        df = pd.read_excel(r"data/Data_Mahasiswa.xlsx")
        return df
    except Exception as e:
        st.error(f"Gagal memuat data mahasiswa: {e}")
        return None

def load_dosen_data():
    try:
        df = pd.read_excel(r"data/Data_Dosen.xlsx")
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dosen: {e}")
        return None

df_mahasiswa = load_mahasiswa_data()
df_dosen = load_dosen_data()

# ======================= SESSION STATE =======================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
# Tambahan daftar admin
admin_users = ["admin1", "admin2"]

def login(nama, role):
    if role == "Mahasiswa" and df_mahasiswa is not None and nama in df_mahasiswa["Nama Mahasiswa"].values:
        st.session_state.update({"logged_in": True, "user_role": "Mahasiswa", "user_name": nama})
        return True
    elif role == "Dosen" and nama in ["Dr. Ahmad", "Prof. Budi", "Dr. Siti", "Dr. Rina", "Ir.Bambang"]:
        st.session_state.update({"logged_in": True, "user_role": "Dosen", "user_name": nama})
        return True
    elif role == "Admin" and nama in admin_users:
        st.session_state.update({"logged_in": True, "user_role": "Admin", "user_name": nama})
        return True
    return False

# ======================= FUNGSI LOGOUT =======================
def logout():
    st.session_state.update({"logged_in": False, "user_role": None, "user_name": None})

# ======================= HALAMAN LOGIN =======================
if not st.session_state["logged_in"]:
    with st.container():
        st.title("🔐 Login Prediksi Kinerja Mahasiswa")
        nama_user = st.text_input("🧑 Nama Lengkap")
        role = st.selectbox("👥 Masuk Sebagai", ["Mahasiswa", "Dosen", "Admin"])

        if st.button("🚀 Login"):
            if login(nama_user, role):
                st.success(f"✅ Selamat datang, {nama_user}!")
                st.rerun()
            else:
                st.error("❌ Nama tidak ditemukan!")

# ======================= HALAMAN MAHASISWA =======================
elif st.session_state["user_role"] == "Mahasiswa":
    st.sidebar.markdown("### 🔑 Akun Mahasiswa")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.subheader(f"🎓 Halo, {st.session_state['user_name']}")

    mahasiswa_data = df_mahasiswa[df_mahasiswa["Nama Mahasiswa"] == st.session_state["user_name"]]

    if not mahasiswa_data.empty:
        st.markdown("#### 📄 Data Anda")
        st.dataframe(mahasiswa_data)

        ipk = mahasiswa_data["IPK"].iloc[0]
        jurusan = mahasiswa_data["Jurusan"].iloc[0]

        if ipk >= 2.50:
            prediksi = "Lulus"
            prob_lulus = 90.0 if jurusan == "Teknik Informatika" else 85.0
        else:
            prediksi = "Tidak Lulus"
            prob_lulus = 20.0 if jurusan == "Teknik Informatika" else 15.0
        prob_tidak_lulus = 100.0 - prob_lulus

        st.markdown(f"### 🎯 Prediksi: *{prediksi}*")
        st.metric("✅ Probabilitas Lulus", f"{prob_lulus}%")
        st.metric("❌ Probabilitas Tidak Lulus", f"{prob_tidak_lulus}%")

        fig, ax = plt.subplots()
        ax.pie([prob_lulus, prob_tidak_lulus], labels=["Lulus", "Tidak Lulus"], autopct='%1.1f%%', colors=["#4CAF50", "#FF0013"])
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.warning("⚠ Data tidak ditemukan.")

# ======================= HALAMAN DOSEN =======================
elif st.session_state["user_role"] == "Dosen":
    st.sidebar.markdown("### 🔑 Akun Dosen")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.subheader(f"📚 Selamat datang, {st.session_state['user_name']}")
    st.markdown("Silakan upload file data mahasiswa (.xlsx):")

    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df_mahasiswa = pd.read_excel(uploaded_file, engine='openpyxl')

            jurusan_mapping = {
                "Dr. Ahmad": "Teknik Informatika",
                "Prof. Budi": "Sistem Informasi",
                "Dr. Siti": "Akuntansi",
                "Dr. Rina": "Manajemen",
                "Ir.Bambang": "Teknik Elektro"
            }

            jurusan = jurusan_mapping.get(st.session_state["user_name"])
            df_filtered = df_mahasiswa[df_mahasiswa["Jurusan"] == jurusan] if jurusan else pd.DataFrame()

            if not df_filtered.empty:
                st.markdown("### 🎓 Data Mahasiswa")
                st.dataframe(df_filtered)

                df_filtered['Prediksi'] = df_filtered['IPK'].apply(lambda x: "Lulus" if x >= 2.50 else "Tidak Lulus")
                df_filtered['Prob_Lulus'] = df_filtered.apply(
                    lambda row: 90.0 if row['Jurusan'] == "Teknik Informatika" and row['IPK'] >= 2.50 else
                                85.0 if row['IPK'] >= 2.50 else 20.0, axis=1)
                df_filtered['Prob_Tidak_Lulus'] = 100.0 - df_filtered['Prob_Lulus']

                st.markdown("#### 🔮 Prediksi Mahasiswa")
                st.dataframe(df_filtered[['Nama Mahasiswa', 'Jurusan', 'IPK', 'Prediksi', 'Prob_Lulus', 'Prob_Tidak_Lulus']])

                st.markdown("#### 📊 Rata-rata Probabilitas")
                avg_lulus = df_filtered['Prob_Lulus'].mean()
                avg_tidak = df_filtered['Prob_Tidak_Lulus'].mean()

                fig, ax = plt.subplots()
                ax.pie([avg_lulus, avg_tidak], labels=["Lulus", "Tidak Lulus"], autopct='%1.1f%%', colors=["#4CAF50", "#FF0013"])
                ax.axis('equal')
                st.pyplot(fig)

                st.markdown("#### 📈 Statistik IPK")
                st.write(f"- Rata-rata IPK: *{df_filtered['IPK'].mean():.2f}*")
                st.write(f"- Tertinggi: *{df_filtered['IPK'].max():.2f}*")
                st.write(f"- Terendah: *{df_filtered['IPK'].min():.2f}*")

                fig, ax = plt.subplots()
                ax.hist(df_filtered["IPK"], bins=10, color="#4CAF50", edgecolor="black")
                ax.set_title("Distribusi IPK Mahasiswa")
                ax.set_xlabel("IPK")
                ax.set_ylabel("Jumlah")
                st.pyplot(fig)
            else:
                st.warning("⚠ Tidak ada data mahasiswa untuk jurusan ini.")

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
    else:
        st.info("⬆ Silakan upload file Excel terlebih dahulu untuk melihat data.")

# ======================= HALAMAN ADMIN =======================
elif st.session_state["user_role"] == "Admin":
    # Generate NIM acak misalnya 8 digit
    nim = f"{random.randint(10000000, 99999999)}"
    
    # Sidebar configuration
    st.sidebar.markdown("### 🛠 Akun Admin")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    
    # Navigation options in sidebar
    st.sidebar.markdown("### 📊 Menu Admin")
    menu_option = st.sidebar.radio(
        "Pilih opsi:",
        ["📤 Upload Data", "➕ Tambah Data", "📊 Statistik"],
        index=0
    )
    
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.subheader(f"📊 Selamat datang Admin, {st.session_state['user_name']}")

    if menu_option == "📤 Upload Data":
        st.markdown("Silakan upload file data mahasiswa (.xlsx):")
        uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"], key="uploader")

        if uploaded_file is not None:
            try:
                df_mahasiswa = pd.read_excel(uploaded_file, engine='openpyxl')

                if not df_mahasiswa.empty:
                    st.markdown("### 🎓 Seluruh Data Mahasiswa")
                    st.dataframe(df_mahasiswa)

                    # Proses prediksi kelulusan
                    df_mahasiswa['Prediksi'] = df_mahasiswa['IPK'].apply(lambda x: "Lulus" if x >= 2.50 else "Tidak Lulus")
                    df_mahasiswa['Prob_Lulus'] = df_mahasiswa.apply(
                        lambda row: 90.0 if row['Jurusan'] == "Teknik Informatika" and row['IPK'] >= 2.50 else
                                    85.0 if row['IPK'] >= 2.50 else
                                    20.0 if row['Jurusan'] == "Teknik Informatika" else 15.0,
                        axis=1
                    )
                    df_mahasiswa['Prob_Tidak_Lulus'] = 100.0 - df_mahasiswa['Prob_Lulus']

                    st.markdown("#### 🔮 Prediksi Mahasiswa")
                    st.dataframe(df_mahasiswa[['Nama Mahasiswa', 'Jurusan', 'IPK', 'Prediksi', 'Prob_Lulus', 'Prob_Tidak_Lulus']])

                    # Visualisasi rata-rata probabilitas
                    st.markdown("#### 📊 Rata-rata Probabilitas")
                    avg_lulus = df_mahasiswa['Prob_Lulus'].mean()
                    avg_tidak = df_mahasiswa['Prob_Tidak_Lulus'].mean()

                    fig, ax = plt.subplots()
                    ax.pie([avg_lulus, avg_tidak], labels=["Lulus", "Tidak Lulus"], autopct='%1.1f%%', colors=["#4CAF50", "#FF0013"])
                    ax.axis('equal')
                    st.pyplot(fig)

                    # Statistik IPK
                    st.markdown("#### 📈 Statistik IPK")
                    st.write(f"- Rata-rata IPK: *{df_mahasiswa['IPK'].mean():.2f}*")
                    st.write(f"- IPK Tertinggi: *{df_mahasiswa['IPK'].max():.2f}*")
                    st.write(f"- IPK Terendah: *{df_mahasiswa['IPK'].min():.2f}*")

                    fig, ax = plt.subplots()
                    ax.hist(df_mahasiswa["IPK"], bins=10, color="#4CAF50", edgecolor="black")
                    ax.set_title("Distribusi IPK Mahasiswa")
                    ax.set_xlabel("IPK")
                    ax.set_ylabel("Jumlah Mahasiswa")
                    st.pyplot(fig)

                else:
                    st.warning("⚠ File kosong atau tidak mengandung data mahasiswa.")

            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")
        else:
            st.info("⬆ Silakan upload file Excel terlebih dahulu untuk melihat data.")

    elif menu_option == "➕ Tambah Data":
        st.markdown("## ➕ Tambah Data Mahasiswa Baru")
        
        with st.form("form_input", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nama = st.text_input("Nama Mahasiswa", key="nama")
                jurusan = st.selectbox("Jurusan", ["Teknik Informatika", "Sistem Informasi", "Akuntansi", "Teknik Elektro", "Manajemen"], key="jurusan")
                ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01, key="ipk")
                sks = st.number_input("SKS", min_value=1.0, max_value=200.0, step=10.0, key="sks")
                
            with col2:
                nilai_matkul = st.number_input("Nilai Mata Kuliah", min_value=0.01, max_value=100.00, step=0.10, key="nilai")
                kehadiran = st.number_input("Jumlah Kehadiran", min_value=1.0, max_value=20.0, step=1.0, key="kehadiran")
                tugas = st.number_input("Jumlah Tugas", min_value=1.0, max_value=20.0, step=1.0, key="tugas")
                penilaian_dosen = st.number_input("Skor Penilaian Dosen", min_value=1.0, max_value=5.00, step=0.1, key="penilaian")
                
            waktu_penyelesaian = st.number_input("Waktu Penyelesaian", min_value=1.0, max_value=5.0, step=1.0, key="waktu")
            
            submitted = st.form_submit_button("Simpan Data")

            if submitted:
                if nama and jurusan and ipk:
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
                
                    # load file excel
                    excel_path = "data/Data_Mahasiswa.xlsx"
                    if os.path.exists(excel_path):
                        existing_data = pd.read_excel(excel_path, engine="openpyxl")
                        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                    else:
                        updated_data = new_data

                    # Simpan data ke file Excel
                    try:
                        updated_data.to_excel(excel_path, index=False, engine="openpyxl")
                        st.success(f"✅ Data mahasiswa atas nama '{nama}' berhasil ditambahkan.")
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan data: {e}")
                else:
                    st.warning("⚠ Harap lengkapi seluruh field yang wajib (Nama, Jurusan, IPK).")

    elif menu_option == "📊 Statistik":
        st.markdown("## 📊 Statistik Data Mahasiswa")
        
        try:
            df_mahasiswa = pd.read_excel("data/Data_Mahasiswa.xlsx", engine='openpyxl')
            
            if not df_mahasiswa.empty:
                # Statistik umum
                st.markdown("### 📈 Statistik Umum")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Mahasiswa", len(df_mahasiswa))
                with col2:
                    st.metric("Rata-rata IPK", f"{df_mahasiswa['IPK'].mean():.2f}")
                with col3:
                    st.metric("IPK Tertinggi", f"{df_mahasiswa['IPK'].max():.2f}")
                
                # Distribusi Jurusan
                st.markdown("### 🏫 Distribusi Jurusan")
                jurusan_counts = df_mahasiswa['Jurusan'].value_counts()
                fig1, ax1 = plt.subplots()
                ax1.pie(jurusan_counts, labels=jurusan_counts.index, autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')
                st.pyplot(fig1)
                
                
            # IPK distribution by jurusan - using matplotlib instead of seaborn
            st.markdown("#### 📊 Distribusi IPK per Jurusan")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            
            # Group data by jurusan
            grouped_data = df_mahasiswa.groupby('Jurusan')['IPK'].apply(list)
            
            # Create boxplot manually
            positions = range(1, len(grouped_data) + 1)
            boxprops = dict(linestyle='-', linewidth=1.5, color='blue')
            medianprops = dict(linestyle='-', linewidth=2.5, color='red')
            
            bp = ax2.boxplot(grouped_data.values, positions=positions, patch_artist=True,
                            boxprops=boxprops, medianprops=medianprops)
            
            # Color the boxes
            for box in bp['boxes']:
                box.set(facecolor='lightblue')
            
            ax2.set_xticks(positions)
            ax2.set_xticklabels(grouped_data.index)
            ax2.set_xlabel('Jurusan')
            ax2.set_ylabel('IPK')
            ax2.set_title('Distribusi IPK per Jurusan')
            plt.xticks(rotation=45)
            st.pyplot(fig2)
            
            else:
                st.warning("Database mahasiswa kosong. Silakan tambah data terlebih dahulu.")
                
        except FileNotFoundError:
            st.error("File database mahasiswa tidak ditemukan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
