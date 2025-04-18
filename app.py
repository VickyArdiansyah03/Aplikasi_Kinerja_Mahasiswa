import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

        st.markdown(f"### 🎯 Prediksi: **{prediksi}**")
        st.metric("✅ Probabilitas Lulus", f"{prob_lulus}%")
        st.metric("❌ Probabilitas Tidak Lulus", f"{prob_tidak_lulus}%")

        fig, ax = plt.subplots()
        ax.pie([prob_lulus, prob_tidak_lulus], labels=["Lulus", "Tidak Lulus"], autopct='%1.1f%%', colors=["#4CAF50", "#FF0013"])
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data tidak ditemukan.")

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
                st.write(f"- Rata-rata IPK: **{df_filtered['IPK'].mean():.2f}**")
                st.write(f"- Tertinggi: **{df_filtered['IPK'].max():.2f}**")
                st.write(f"- Terendah: **{df_filtered['IPK'].min():.2f}**")

                fig, ax = plt.subplots()
                ax.hist(df_filtered["IPK"], bins=10, color="#4CAF50", edgecolor="black")
                ax.set_title("Distribusi IPK Mahasiswa")
                ax.set_xlabel("IPK")
                ax.set_ylabel("Jumlah")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Tidak ada data mahasiswa untuk jurusan ini.")

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
    else:
        st.info("⬆️ Silakan upload file Excel terlebih dahulu untuk melihat data.")

# ======================= HALAMAN ADMIN (Baru Ditambahkan) =======================
# ======================= HALAMAN ADMIN (Baru Ditambahkan) =======================
elif st.session_state["user_role"] == "Admin":
    st.sidebar.markdown("### 🛠️ Akun Admin")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.subheader(f"📊 Selamat datang Admin, {st.session_state['user_name']}")
    st.markdown("Silakan upload file data mahasiswa (.xlsx):")

    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

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
                st.write(f"- Rata-rata IPK: **{df_mahasiswa['IPK'].mean():.2f}**")
                st.write(f"- IPK Tertinggi: **{df_mahasiswa['IPK'].max():.2f}**")
                st.write(f"- IPK Terendah: **{df_mahasiswa['IPK'].min():.2f}**")

                fig, ax = plt.subplots()
                ax.hist(df_mahasiswa["IPK"], bins=10, color="#4CAF50", edgecolor="black")
                ax.set_title("Distribusi IPK Mahasiswa")
                ax.set_xlabel("IPK")
                ax.set_ylabel("Jumlah Mahasiswa")
                st.pyplot(fig)

            else:
                st.warning("⚠️ File kosong atau tidak mengandung data mahasiswa.")

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
    else:
        st.info("⬆️ Silakan upload file Excel terlebih dahulu untuk melihat data.")
