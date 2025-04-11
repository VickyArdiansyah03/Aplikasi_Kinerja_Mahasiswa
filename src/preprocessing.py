import pandas as pd

def preprocess_data(df):
    """
    Fungsi untuk melakukan preprocessing data mahasiswa.
    Melakukan encoding pada kolom 'Jurusan'.
    
    Parameters:
    - df: pandas DataFrame, berisi data mahasiswa
    
    Returns:
    - df: pandas DataFrame, data setelah preprocessing
    """
    # Mapping untuk encoding kolom jurusan
    jurusan_mapping = {
        "Teknik Informatika": 0,
        "Sistem Informasi": 1,
        "Manajemen": 2,
        "Akuntansi": 3,
        "Teknik Elektro": 4
    }

    # Encode kolom Jurusan
    df["Jurusan"] = df["Jurusan"].map(jurusan_mapping)

    # Jika ada nilai NaN setelah mapping, artinya ada jurusan yang tidak dikenali
    if df["Jurusan"].isnull().any():
        print("⚠️ Ada jurusan yang tidak dikenali dalam data!")

    return df

def predict(input_data):
    """
    Fungsi prediksi sederhana berdasarkan aturan IPK.
    IPK > 2: Lulus
    IPK <= 2: Tidak Lulus

    Parameters:
    - input_data: pandas DataFrame yang berisi kolom 'IPK'

    Returns:
    - predictions: list hasil prediksi ("Lulus" atau "Tidak Lulus")
    - probabilities: list probabilitas (dalam persentase) masing-masing prediksi
    """
    predictions = []
    probabilities = []

    for index, row in input_data.iterrows():
        ipk = row['IPK']
        if ipk > 2:
            pred = 'Lulus'
            prob = [0.0, 1.0]  # Prob Tidak Lulus, Lulus
        else:
            pred = 'Tidak Lulus'
            prob = [1.0, 0.0]
        
        predictions.append(pred)
        probabilities.append(prob)

    return predictions, probabilities

if __name__ == "__main__":
    # Path ke file terbaru
    data_path = r'D:/project machine23/data/Data_Mahasiswa.xlsx'
    
    # Baca data Excel
    df = pd.read_excel(data_path)

    print("Sebelum preprocessing:")
    print(df.head())

    # Preprocessing
    processed_df = preprocess_data(df)

    print("\nSetelah preprocessing:")
    print(processed_df.head())

    # Prediksi
    predictions, probabilities = predict(processed_df)

    # Tampilkan hasil prediksi
    for idx, (nama, nim, pred, prob) in enumerate(zip(df['Nama Mahasiswa'], df['NIM'], predictions, probabilities)):
        print(f"{idx+1}. Nama: {nama}, NIM: {nim}")
        print(f"   Prediksi: {pred}")
        print(f"   Probabilitas Lulus: {prob[1]*100:.2f}%, Tidak Lulus: {prob[0]*100:.2f}%\n")