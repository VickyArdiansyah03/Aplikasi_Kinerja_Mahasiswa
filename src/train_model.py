import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def preprocess_data(df):
    """
    Fungsi untuk melakukan preprocessing data mahasiswa.
    Melakukan encoding pada kolom 'Jurusan'.
    """
    jurusan_mapping = {
        "Teknik Informatika": 0,
        "Sistem Informasi": 1,
        "Manajemen": 2,
        "Akuntansi": 3,
        "Teknik Elektro": 4
    }

    df["Jurusan"] = df["Jurusan"].map(jurusan_mapping)
    df.dropna(inplace=True)  # Menghapus data yang memiliki nilai NaN
    
    return df

def train_model(X_train, y_train, model_save_path):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"✅ Model berhasil disimpan di {model_save_path}")
    return model

if __name__ == '__main__':
    data_path = "data/Data_Mahasiswa.xlsx"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {data_path}")
    
    df = pd.read_excel(data_path)
    df["Keterangan"] = df.apply(lambda row: "Lulus" if row["IPK"] >= 2.50 and row["Jumlah SKS"] >= 110 else "Tidak Lulus", axis=1)
    processed_df = preprocess_data(df)
    
    fitur_kolom = ["IPK", "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran", "Jumlah Tugas", "Skor Penilaian Dosen", "Waktu Penyelesaian"]
    X = processed_df[fitur_kolom]
    y = processed_df["Keterangan"].map({"Lulus": 1, "Tidak Lulus": 0})
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model_save_path = "models/random_forest_model.pkl"
    trained_model = train_model(X_train, y_train, model_save_path)
    
    y_pred = trained_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Akurasi Model: {accuracy:.2f}")
