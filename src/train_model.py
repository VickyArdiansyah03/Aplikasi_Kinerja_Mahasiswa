import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load data
file_path = r"data/Data_Mahasiswa_Nama_NIM_Fix.xlsx"
df = pd.read_excel(file_path)

# Define target variable (classification: IPK >= 3.0 is High, otherwise Low)
df["IPK_Category"] = np.where(df["IPK"] >= 3.0, 1, 0)

# Select features
features = ["Jumlah SKS", "Nilai Mata Kuliah", "Jumlah Kehadiran", "Jumlah Tugas", "Skor Penilaian Dosen", "Waktu Penyelesaian", "CPL", "CPMK"]
X = df[features]
y = df["IPK_Category"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

# Print evaluation metrics
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-score: {f1:.2f}")
