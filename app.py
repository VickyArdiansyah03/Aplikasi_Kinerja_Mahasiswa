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
                
                # Distribusi IPK
                st.markdown("### 📊 Distribusi IPK")
                fig2, ax2 = plt.subplots()
                ax2.hist(df_mahasiswa['IPK'], bins=10, color='skyblue', edgecolor='black')
                ax2.set_xlabel('IPK')
                ax2.set_ylabel('Jumlah Mahasiswa')
                st.pyplot(fig2)
                
            else:
                st.warning("Database mahasiswa kosong. Silakan tambah data terlebih dahulu.")
                
        except FileNotFoundError:
            st.error("File database mahasiswa tidak ditemukan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
