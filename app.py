import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================= PAGE CONFIGURATION =======================
st.set_page_config(page_title="Aplikasi Prediksi Kinerja Mahasiswa", layout="centered", page_icon="🎓")

# ======================= LOAD DATA =======================
def load_mahasiswa_data():
    try:
        return pd.read_excel("data/Data_Mahasiswa.xlsx")
    except Exception as e:
        st.error(f"Gagal memuat data mahasiswa: {e}")
        return None

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

def logout():
    st.session_state.update({"logged_in": False, "user_role": None, "user_name": None})

# ======================= LOGIN PAGE (LIGHT MODE) =======================
if not st.session_state["logged_in"]:
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            padding: 2rem;
            margin: 3rem auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
            font-family: 'Segoe UI', sans-serif;
        }
        .login-title {
            color: #222;
            text-align: center;
            font-size: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .login-subtitle {
            text-align: center;
            color: #555;
            margin-bottom: 2rem;
            font-size: 1rem;
        }
        .footer {
            text-align: center;
            color: #999;
            font-size: 0.8rem;
            margin-top: 3rem;
        }
        div.stButton > button {
            background-color: #3498db;
            color: white;
            font-weight: 600;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #2980b9;
        }
        </style>

        <div class="login-container">
            <div class="login-title">🎓 Login Aplikasi Prediksi</div>
            <div class="login-subtitle">Silakan login untuk melanjutkan</div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
        </div>
        <div class="footer">© 2025 Sistem Prediksi Kinerja Mahasiswa</div>
    """, unsafe_allow_html=True)

# ======================= MAIN PAGE =======================
else:
    st.sidebar.markdown(f"### 👋 Selamat datang, {st.session_state['user_name']} ({st.session_state['user_role']})")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.experimental_rerun()

    st.title("🏠 Beranda Aplikasi Prediksi Kinerja Mahasiswa")
    st.markdown("""
    Selamat datang di aplikasi prediksi kinerja mahasiswa. 
    Aplikasi ini memungkinkan mahasiswa, dosen, dan admin untuk:

    - 📊 Melihat data IPK mahasiswa
    - 🔮 Melihat prediksi kelulusan berdasarkan IPK dan jurusan
    - 📈 Menampilkan visualisasi distribusi IPK
    - 🛠️ Upload dan analisis data mahasiswa (.xlsx)
    """)

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
        uploaded_file = st.file_uploader("📤 Upload file data mahasiswa (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            try:
                df_mahasiswa = pd.read_excel(uploaded_file, engine='openpyxl')

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

                if df_mahasiswa.empty:
                    st.warning("⚠️ Tidak ada data mahasiswa untuk ditampilkan.")
                else:
                    st.markdown("### 📋 Data Mahasiswa")
                    st.dataframe(df_mahasiswa)

                    df_mahasiswa['Prediksi'] = df_mahasiswa['IPK'].apply(lambda x: "Lulus" if x >= 2.50 else "Tidak Lulus")
                    df_mahasiswa['Prob_Lulus'] = df_mahasiswa.apply(
                        lambda row: 90.0 if row['Jurusan'] == "Teknik Informatika" and row['IPK'] >= 2.50 else
                                    85.0 if row['IPK'] >= 2.50 else
                                    20.0 if row['Jurusan'] == "Teknik Informatika" else 15.0, axis=1)
                    df_mahasiswa['Prob_Tidak_Lulus'] = 100.0 - df_mahasiswa['Prob_Lulus']

                    st.markdown("#### 🔮 Prediksi Mahasiswa")
                    st.dataframe(df_mahasiswa[['Nama Mahasiswa', 'Jurusan', 'IPK', 'Prediksi', 'Prob_Lulus', 'Prob_Tidak_Lulus']])

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
            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")
        else:
            st.info("⬆️ Silakan upload file Excel terlebih dahulu.")
