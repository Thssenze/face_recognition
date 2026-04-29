# train_model.py — Melatih Model LBPH dari Dataset Wajah

import cv2
import numpy as np
import os
from PIL import Image
from config import DATASET_PATH, MODEL_PATH

def ambil_data_training(dataset_path):
    """
    Baca semua foto dari folder dataset.
    Nama folder format: {user_id}_{nama}
    Return: list wajah (numpy array) dan list ID
    """
    wajah_list = []
    id_list    = []

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Folder dataset tidak ditemukan: {dataset_path}")
        return [], []

    for folder_name in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        try:
            user_id = int(folder_name.split("_")[0])
        except ValueError:
            print(f"[SKIP] Folder tidak dikenali: {folder_name}")
            continue

        for file_name in os.listdir(folder_path):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            img_path = os.path.join(folder_path, file_name)
            try:
                img    = Image.open(img_path).convert('L')  # grayscale
                img_np = np.array(img, 'uint8')
                wajah_list.append(img_np)
                id_list.append(user_id)
            except Exception as e:
                print(f"[SKIP] Gagal membaca {img_path}: {e}")

    return wajah_list, id_list

def latih_model():
    print("=" * 45)
    print("   TRAINING MODEL LBPH")
    print("=" * 45)

    print("\n[INFO] Membaca dataset wajah...")
    wajah_list, id_list = ambil_data_training(DATASET_PATH)

    if len(wajah_list) == 0:
        print("[ERROR] Tidak ada data wajah ditemukan.")
        print("[INFO]  Jalankan 'python face_register.py' terlebih dahulu.")
        return

    jumlah_user = len(set(id_list))
    print(f"[INFO] Total foto   : {len(wajah_list)}")
    print(f"[INFO] Total user   : {jumlah_user}")
    print(f"\n[INFO] Melatih model LBPH, harap tunggu...")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(wajah_list, np.array(id_list))

    # Pastikan folder models ada
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    recognizer.write(MODEL_PATH)

    print(f"[SUKSES] Model berhasil disimpan ke: {MODEL_PATH}")
    print(f"[INFO]   {jumlah_user} wajah berhasil dilatih.")
    print(f"\n[INFO]   Jalankan 'python face_recognize.py' untuk mulai absensi.\n")

if __name__ == "__main__":
    latih_model()