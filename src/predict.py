import pandas as pd

def preprocess_data(df):
    """
    Fungsi preprocessing sederhana, bisa dikembangkan sesuai kebutuhan.
    Saat ini hanya melakukan pemrosesan dasar, misalnya normalisasi / encoding jika diperlukan.
    """
    # Di sini bisa tambahkan preprocessing lain kalau butuh
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

    # Preprocess data jika perlu
    processed_data = preprocess_data(df)

    # Prediksi
    predictions, probabilities = predict(processed_data)

    # Tampilkan hasil prediksi
    for idx, (nama, nim, pred, prob) in enumerate(zip(df['Nama Mahasiswa'], df['NIM'], predictions, probabilities)):
        print(f"{idx+1}. Nama: {nama}, NIM: {nim}")
        print(f"   Prediksi: {pred}")
        print(f"   Probabilitas Lulus: {prob[1]*100:.2f}%, Tidak Lulus: {prob[0]*100:.2f}%\n")
