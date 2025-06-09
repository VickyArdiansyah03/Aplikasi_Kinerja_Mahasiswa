# ======================= HALAMAN DOSEN =======================
elif st.session_state["user_role"] == "Dosen":
    st.sidebar.markdown("### 🔑 Akun Dosen")
    st.sidebar.write(f"👤 {st.session_state['user_name']}")
    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()

    st.subheader(f"📚 Selamat datang, {st.session_state['user_name']}")
    st.markdown("Silakan upload file data mahasiswa (.xlsx atau .csv):")

    uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            # Check file extension
            if uploaded_file.name.endswith('.xlsx'):
                df_mahasiswa = pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.csv'):
                df_mahasiswa = pd.read_csv(uploaded_file)
            else:
                st.error("Format file tidak didukung. Harap upload file Excel (.xlsx) atau CSV (.csv)")
                st.stop()

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
                st.write(f"- Rata-rata IPK: {df_filtered['IPK'].mean():.2f}")
                st.write(f"- Tertinggi: {df_filtered['IPK'].max():.2f}")
                st.write(f"- Terendah: {df_filtered['IPK'].min():.2f}")

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
        st.info("⬆ Silakan upload file Excel (.xlsx) atau CSV (.csv) terlebih dahulu untuk melihat data.")

# ======================= HALAMAN ADMIN =======================
elif st.session_state["user_role"] == "Admin":
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
        st.markdown("Silakan upload file data mahasiswa (.xlsx atau .csv):")
        uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"], key="uploader")

        if uploaded_file is not None:
            try:
                # Check file extension
                if uploaded_file.name.endswith('.xlsx'):
                    df_mahasiswa = pd.read_excel(uploaded_file, engine='openpyxl')
                elif uploaded_file.name.endswith('.csv'):
                    df_mahasiswa = pd.read_csv(uploaded_file)
                else:
                    st.error("Format file tidak didukung. Harap upload file Excel (.xlsx) atau CSV (.csv)")
                    st.stop()

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
                    st.write(f"- Rata-rata IPK: {df_mahasiswa['IPK'].mean():.2f}")
                    st.write(f"- IPK Tertinggi: {df_mahasiswa['IPK'].max():.2f}")
                    st.write(f"- IPK Terendah: {df_mahasiswa['IPK'].min():.2f}")

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
            st.info("⬆ Silakan upload file Excel (.xlsx) atau CSV (.csv) terlebih dahulu untuk melihat data.")
