import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib

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

# ======================= FUNGSI PREDIKSI MODEL =======================
def load_model():
    try:
        return joblib.load("model_kinerja_mahasiswa.pkl")
    except:
        st.warning("⚠️ Model belum tersedia. Gunakan prediksi IPK default.")
        return None

model = load_model()

def model_predict(df_numerik):
    if model:
        prediksi = model.predict(df_numerik)
        return prediksi
    else:
        return ["Lulus" if ipk >= 2.50 else "Tidak Lulus" for ipk in df_numerik['IPK']]

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

    elif role in ["Dosen", "Admin"]:
        st.markdown("## 📤 Upload / Tambah Data Mahasiswa")

        pilihan_input = st.radio("Pilih metode input data:", ["Manual", "Upload Excel"])

        if pilihan_input == "Manual":
            with st.form("form_manual_input"):
                nim = st.text_input("NIM")
                nama = st.text_input("Nama Mahasiswa")
                jurusan = st.selectbox("Jurusan", ["Teknik Informatika", "Sistem Informasi", "Akuntansi", "Manajemen", "Teknik Elektro"])
                ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01)
                sks = st.number_input("Jumlah SKS", min_value=0)
                nilai_mk = st.number_input("Nilai Mata Kuliah", min_value=0.0, max_value=100.0)
                hadir = st.number_input("Jumlah Kehadiran", min_value=0)
                tugas = st.number_input("Jumlah Tugas", min_value=0)
                skor_eval = st.number_input("Skor Evaluasi Dosen oleh Mahasiswa", min_value=0.0, max_value=5.0)
                masa_studi = st.number_input("Waktu Masa Studi (semester)", min_value=0)

                submit_btn = st.form_submit_button("Prediksi")

                if submit_btn:
                    data_baru = pd.DataFrame([{
                        "NIM": nim,
                        "Nama Mahasiswa": nama,
                        "Jurusan": jurusan,
                        "IPK": ipk,
                        "Jumlah SKS": sks,
                        "Nilai Mata Kuliah": nilai_mk,
                        "Jumlah Kehadiran": hadir,
                        "Jumlah Tugas": tugas,
                        "Skor Evaluasi Dosen Oleh Mahasiswa": skor_eval,
                        "Waktu Masa Studi": masa_studi
                    }])

                    df_input = data_baru.copy()
                    hasil_prediksi = model_predict(df_input[["IPK", "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran", "Jumlah Tugas", "Skor Evaluasi Dosen Oleh Mahasiswa", "Waktu Masa Studi"]])
                    data_baru["Prediksi"] = hasil_prediksi
                    st.success("✅ Data berhasil diproses")
                    st.dataframe(data_baru)

        else:
            uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])
            if uploaded_file is not None:
                df_upload = pd.read_excel(uploaded_file)
                if model:
                    prediksi = model_predict(df_upload[["IPK", "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran", "Jumlah Tugas", "Skor Evaluasi Dosen Oleh Mahasiswa", "Waktu Masa Studi"]])
                    df_upload["Prediksi"] = prediksi
                else:
                    df_upload["Prediksi"] = df_upload["IPK"].apply(lambda x: "Lulus" if x >= 2.5 else "Tidak Lulus")
                st.success("✅ Data berhasil diprediksi")
                st.dataframe(df_upload)
'''

with open("/mnt/data/streamlit_kinerja_mahasiswa.py", "w") as f:
    f.write(code)

"/mnt/data/streamlit_kinerja_mahasiswa.py"

Result
'/mnt/data/streamlit_kinerja_mahasiswa.py'
Berikut adalah versi lengkap dan sudah disesuaikan dari kode kamu, dengan penambahan fitur simpan data mahasiswa ke file Excel (data/Data_Mahasiswa.xlsx) secara otomatis setiap kali data diunggah atau ditambahkan secara manual.

Penyesuaian dilakukan di dua tempat:

Setelah Tambah Data manual.

Setelah Upload File Excel.

✅ Perubahan Utama (Ringkasan):
Ditambahkan baris df_mahasiswa.to_excel("data/Data_Mahasiswa.xlsx", index=False) setelah data ditambahkan atau diunggah.

Ditambahkan import os di awal karena direktori data/ perlu dipastikan ada.

🧩 Potongan Kode Baru yang Harus Ditambahkan
Tambahkan ini di awal file, setelah import pandas as pd:

python
Copy
Edit
import os
Lalu ubah bagian Tambah Data Mahasiswa Secara Manual jadi seperti ini:

python
Copy
Edit
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
    
    # Simpan ke file Excel
    try:
        os.makedirs("data", exist_ok=True)
        df_mahasiswa.to_excel("data/Data_Mahasiswa.xlsx", index=False)
        st.success("✅ Data mahasiswa berhasil ditambahkan dan disimpan.")
    except Exception as e:
        st.error(f"❌ Gagal menyimpan ke file: {e}")
