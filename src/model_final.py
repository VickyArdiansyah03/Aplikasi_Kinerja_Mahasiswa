import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class Model:
    def fit(self, X, y=None):
        return self

    def predict(self, X):
        return np.array([1 if ipk > 2 else 0 for ipk in X["IPK"]])


def preprocess_data(df):
    jurusan_mapping = {
        "Teknik Informatika": 0,
        "Sistem Informasi": 1,
        "Manajemen": 2,
        "Akuntansi": 3,
        "Teknik Elektro": 4
    }
    df["Jurusan"] = df["Jurusan"].map(jurusan_mapping)
    df.dropna(inplace=True)
    return df


if __name__ == '__main__':
    data_path = "data/Data_Mahasiswa_Nama_NIM_Fix.xlsx"
    model_save_path = "models/random_forest_model.pkl"

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {data_path}")
    
    df = pd.read_excel(data_path)
    df["Keterangan"] = df["Status (Lulus/Tidak)"]
    processed_df = preprocess_data(df)

    fitur_kolom = ["IPK", "Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran", 
                   "Jumlah Tugas", "Skor Penilaian Dosen", "Waktu Penyelesaian", "CPL", "CPMK"]
    X = processed_df[fitur_kolom]
    y = processed_df["Keterangan"].map({"Lulus": 1, "Tidak Lulus": 0})

    model = Model()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Simpan model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"✅ Model rule sederhana berhasil disimpan di {model_save_path}")

    # Evaluasi
    accuracy = accuracy_score(y, y_pred)
    print(f"🎯 Akurasi Model: {accuracy:.2f}")
    print("📌 Confusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\n📋 Classification Report:")
    print(classification_report(y, y_pred, target_names=["Tidak Lulus", "Lulus"]))
