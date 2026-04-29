# face_register.py — Registrasi Wajah Pengguna Baru

import cv2
import os
from database import tambah_user, nim_sudah_ada
from config import DATASET_PATH, FOTO_PER_USER, CAMERA_INDEX

def registrasi_wajah():
    print("=" * 45)
    print("   REGISTRASI PENGGUNA BARU")
    print("=" * 45)

    # Input data user
    nama = input("Masukkan Nama Lengkap : ").strip()
    nim  = input("Masukkan NIM          : ").strip()

    if not nama or not nim:
        print("[ERROR] Nama dan NIM tidak boleh kosong.")
        return

    if nim_sudah_ada(nim):
        print(f"[ERROR] NIM {nim} sudah terdaftar di database.")
        return

    # Simpan ke database, dapatkan ID
    user_id = tambah_user(nama, nim)
    print(f"\n[INFO] User terdaftar dengan ID: {user_id}")

    # Buat folder dataset untuk user ini
    folder_user = os.path.join(DATASET_PATH, f"{user_id}_{nama.replace(' ', '_')}")
    os.makedirs(folder_user, exist_ok=True)

    # Muat detektor wajah Haar Cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    cam = cv2.VideoCapture(CAMERA_INDEX)
    cam.set(3, 640)  # lebar frame
    cam.set(4, 480)  # tinggi frame

    print(f"\n[INFO] Kamera aktif. Mengambil {FOTO_PER_USER} foto wajah...")
    print("[INFO] Hadapkan wajah ke kamera. Gerakkan sedikit ke kiri/kanan/atas/bawah.")
    print("[INFO] Tekan 'Q' untuk membatalkan.\n")

    jumlah_foto = 0

    while jumlah_foto < FOTO_PER_USER:
        ret, frame = cam.read()
        if not ret:
            print("[ERROR] Kamera tidak dapat membaca frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            jumlah_foto += 1

            # Simpan foto wajah (grayscale, di-crop)
            wajah_crop = gray[y:y+h, x:x+w]
            nama_file  = os.path.join(folder_user, f"{jumlah_foto}.jpg")
            cv2.imwrite(nama_file, wajah_crop)

            # Tampilkan kotak & progress di layar
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Foto: {jumlah_foto}/{FOTO_PER_USER}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

        status = f"Mengambil foto... {jumlah_foto}/{FOTO_PER_USER}"
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Nama: {nama} | NIM: {nim}", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Registrasi Wajah — Tekan Q untuk batal", frame)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            print("\n[INFO] Registrasi dibatalkan oleh pengguna.")
            break

    cam.release()
    cv2.destroyAllWindows()

    if jumlah_foto >= FOTO_PER_USER:
        print(f"\n[SUKSES] {jumlah_foto} foto berhasil disimpan.")
        print(f"[INFO]   Folder: {folder_user}")
        print(f"[INFO]   Jalankan 'python train_model.py' untuk melatih ulang model.\n")
    else:
        print(f"\n[PERINGATAN] Hanya {jumlah_foto} foto yang tersimpan (kurang dari {FOTO_PER_USER}).")

if __name__ == "__main__":
    registrasi_wajah()