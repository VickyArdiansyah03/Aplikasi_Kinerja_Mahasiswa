import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================= PAGE CONFIGURATION =======================
st.set_page_config(page_title="Aplikasi Prediksi Kinerja Mahasiswa", layout="centered", page_icon="🎓")

# ======================= GLOBAL WHITE BACKGROUND =======================
st.markdown("""
    <style>
    body {
        background-color: white !important;
    }
    .stApp {
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# ======================= LOAD DATA =======================
def load_mahasiswa_data():
    try:
        return pd.read_excel("data/Data_Mahasiswa.xlsx")
    except Exception as e:
        st.error(f"Gagal memuat data mahasiswa: {e}")
        return pd.DataFrame(columns=[
            "NIM", "Nama Mahasiswa", "Jurusan", "IPK",
            "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran",
            "Jumlah Tugas", "Skor Evaluasi Dosen Oleh Mahasiswa",
            "Waktu Masa Studi"
        ])

def load_dosen_data():
    try:
        return pd.read_excel("data/Data_Dosen.xlsx")
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

admin_users = ["admin1", "admin2"]

def login(nama, role):
    if role == "Mahasiswa" and not df_mahasiswa.empty and nama in df_mahasiswa["Nama Mahasiswa"].values:
        st.session_state.update({"logged_in": True, "user_role": "Mahasiswa", "user_name": nama})
        return True
    elif role == "Dosen" and nama in ["Dr. Ahmad", "Prof. Budi", "Dr. Siti", "Dr. Rina", "Ir.Bambang"]:
        st.session_state.update({"logged_in": True, "user_role": "Dosen", "user_name": nama})
        return True
    elif role == "Admin" and nama in admin_users:
        st.session_state.update({"logged_in": True, "user_role": "Admin", "user_name": nama})
        return True
    return False

def logout():
    st.session_state.update({"logged_in": False, "user_role": None, "user_name": None})

# ======================= LOGIN PAGE =======================
if not st.session_state["logged_in"]:
    st.markdown("""<div class="login-container">""", unsafe_allow_html=True)
    with st.form("login_form"):
        nama_user = st.text_input("🧑 Nama Lengkap", placeholder="Contoh: Ahmad Subari")
        role = st.selectbox("👥 Masuk Sebagai", ["Mahasiswa", "Dosen", "Admin"])
        submitted = st.form_submit_button("🚀 Login")

        if submitted:
            if login(nama_user, role):
                st.success(f"✅ Selamat datang, {nama_user}!")
                st.experimental_rerun()
            else:
                st.error("❌ Nama tidak ditemukan. Silakan periksa kembali.")
    st.markdown("""</div><div class="footer">© 2025 Sistem Prediksi Kinerja Mahasiswa</div>""", unsafe_allow_html=True)

# ======================= MAIN PAGE =======================
else:
    st.sidebar.markdown(f"### 👋 Selamat datang, {st.session_state['user_name']} ({st.session_state['user_role']})")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.experimental_rerun()

    st.title("🏠 Beranda Aplikasi Prediksi Kinerja Mahasiswa")

    role = st.session_state["user_role"]

    if role == "Mahasiswa":
        mahasiswa_data = df_mahasiswa[df_mahasiswa["Nama Mahasiswa"] == st.session_state["user_name"]]
        if not mahasiswa_data.empty:
            st.subheader("📄 Data Anda")
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

    elif role == "Dosen" or role == "Admin":
        st.markdown("## 📤 Upload / Tambah Data Mahasiswa")

        with st.expander("➕ Tambah Mahasiswa Secara Manual"):
            with st.form("form_tambah_mahasiswa"):
                nim_baru = st.text_input("NIM")
                nama_baru = st.text_input("Nama Mahasiswa")
                jurusan_baru = st.selectbox("Jurusan", ["Teknik Informatika", "Sistem Informasi", "Akuntansi", "Manajemen", "Teknik Elektro"])
                ipk_baru = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01)
                sks_baru = st.number_input("Jumlah SKS", min_value=0)
                nilai_mk_baru = st.number_input("Nilai Mata Kuliah (rata-rata)", min_value=0.0, max_value=100.0)
                hadir_baru = st.number_input("Jumlah Kehadiran", min_value=0)
                tugas_baru = st.number_input("Jumlah Tugas", min_value=0)
                skor_eval_baru = st.number_input("Skor Evaluasi Dosen oleh Mahasiswa", min_value=0.0, max_value=5.0, step=0.1)
                masa_studi_baru = st.number_input("Waktu Masa Studi (dalam semester)", min_value=0)

                submit_tambah = st.form_submit_button("Tambah Data")

                if submit_tambah:
                    new_data = pd.DataFrame([[
                        nim_baru, nama_baru, jurusan_baru, ipk_baru,
                        sks_baru, nilai_mk_baru, hadir_baru, tugas_baru,
                        skor_eval_baru, masa_studi_baru
                    ]], columns=[
                        "NIM", "Nama Mahasiswa", "Jurusan", "IPK",
                        "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran",
                        "Jumlah Tugas", "Skor Evaluasi Dosen Oleh Mahasiswa",
                        "Waktu Masa Studi"
                    ])
                    df_mahasiswa = pd.concat([df_mahasiswa, new_data], ignore_index=True)
                    st.success("✅ Data mahasiswa berhasil ditambahkan.")

        uploaded_file = st.file_uploader("📤 Atau upload file Excel (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file, engine='openpyxl')

                expected_cols = [
                    "NIM", "Nama Mahasiswa", "Jurusan", "IPK",
                    "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran",
                    "Jumlah Tugas", "Skor Evaluasi Dosen Oleh Mahasiswa", "Waktu Masa Studi"
                ]
                if all(col in df_upload.columns for col in expected_cols):
                    df_mahasiswa = df_upload
                    st.success("✅ Data mahasiswa berhasil diunggah.")
                else:
                    st.error("❌ Format kolom tidak sesuai. Pastikan semua kolom berikut ada:\n" + ", ".join(expected_cols))
            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")

        # Jika role dosen, filter jurusan sesuai dosen
        if role == "Dosen":
            jurusan_mapping = {
                "Dr. Ahmad": "Teknik Informatika",
                "Prof. Budi": "Sistem Informasi",
                "Dr. Siti": "Akuntansi",
                "Dr. Rina": "Manajemen",
                "Ir.Bambang": "Teknik Elektro"
            }
            jurusan = jurusan_mapping.get(st.session_state["user_name"])
            if jurusan:
                df_mahasiswa = df_mahasiswa[df_mahasiswa["Jurusan"] == jurusan]

        if not df_mahasiswa.empty:
            # Prediksi sederhana berdasarkan IPK
            df_mahasiswa['Prediksi'] = df_mahasiswa['IPK'].apply(lambda x: "Lulus" if x >= 2.50 else "Tidak Lulus")
            df_mahasiswa['Prob_Lulus'] = df_mahasiswa.apply(
                lambda row: 90.0 if row['Jurusan'] == "Teknik Informatika" and row['IPK'] >= 2.50 else
                            85.0 if row['IPK'] >= 2.50 else
                            20.0 if row['Jurusan'] == "Teknik Informatika" else 15.0, axis=1)
            df_mahasiswa['Prob_Tidak_Lulus'] = 100.0 - df_mahasiswa['Prob_Lulus']

            st.markdown("### 📋 Data Mahasiswa")
            st.dataframe(df_mahasiswa)

            st.markdown("#### 🔮 Prediksi Mahasiswa")
            st.dataframe(df_mahasiswa[['NIM', 'Nama Mahasiswa', 'Jurusan', 'IPK', 'Prediksi', 'Prob_Lulus', 'Prob_Tidak_Lulus']])

            st.markdown("#### 📊 Rata-rata Probabilitas")
            avg_lulus = df_mahasiswa['Prob_Lulus'].mean()
            avg_tidak = df_mahasiswa['Prob_Tidak_Lulus'].mean()

            fig, ax = plt.subplots()
            ax.pie([avg_lulus, avg_tidak], labels=["Lulus", "Tidak Lulus"], autopct='%1.1f%%', colors=["#4CAF50", "#FF0013"])
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("#### 📈 Statistik IPK")
            st.write(f"- Rata-rata IPK: **{df_mahasiswa['IPK'].mean():.2f}**")
            st.write(f"- Tertinggi: **{df_mahasiswa['IPK'].max():.2f}**")
            st.write(f"- Terendah: **{df_mahasiswa['IPK'].min():.2f}**")

            fig, ax = plt.subplots()
            ax.hist(df_mahasiswa["IPK"], bins=10, color="#4CAF50", edgecolor="black")
            ax.set_title("Distribusi IPK Mahasiswa")
            ax.set_xlabel("IPK")
            ax.set_ylabel("Jumlah Mahasiswa")
            st.pyplot(fig)
        else:
            st.warning("⚠️ Tidak ada data mahasiswa untuk ditampilkan.")
