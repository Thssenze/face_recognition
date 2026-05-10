# face_recognize.py — Engine Pengenalan Wajah Real-Time + Integrasi ESP32

import cv2
import numpy as np
import os
import requests
from database import get_user_by_id, catat_absensi
from config import (MODEL_PATH, CONFIDENCE_THRESHOLD, CAMERA_INDEX,
                    FLASK_PORT, ESP32_ENABLED, ESP32_IP, ESP32_PORT, ESP32_TIMEOUT)

def kirim_notifikasi(nama, nim, status):
    """
    Kirim hasil pengenalan ke:
    1. Flask server (untuk update dashboard real-time)
    2. ESP32 (untuk LCD & LED) — hanya jika ESP32_ENABLED = True
    """
    payload = {"nama": nama, "nim": nim, "status": status}

    # -- Kirim ke Flask dashboard --
    try:
        requests.post(
            f"http://127.0.0.1:{FLASK_PORT}/api/hasil-absensi",
            json=payload,
            timeout=2
        )
    except Exception:
        pass  # Flask mungkin belum jalan, tidak apa-apa

    # -- Kirim ke ESP32 (jika sudah tersedia) --
    if ESP32_ENABLED:
        try:
            resp = requests.post(
                f"http://{ESP32_IP}:{ESP32_PORT}/absensi",
                json=payload,
                timeout=ESP32_TIMEOUT
            )
            if resp.status_code == 200:
                print(f"[ESP32] Notifikasi terkirim → {status}")
            else:
                print(f"[ESP32] Respons tidak terduga: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[WARN] ESP32 tidak terjangkau di {ESP32_IP}:{ESP32_PORT}")
        except requests.exceptions.Timeout:
            print(f"[WARN] ESP32 timeout setelah {ESP32_TIMEOUT}s")
        except Exception as e:
            print(f"[WARN] Gagal kirim ke ESP32: {e}")

def cek_esp32():
    """Ping ESP32 untuk memastikan koneksi sebelum mulai."""
    if not ESP32_ENABLED:
        print("[INFO] ESP32 dinonaktifkan (ESP32_ENABLED = False di config.py)")
        return
    try:
        resp = requests.get(
            f"http://{ESP32_IP}:{ESP32_PORT}/ping",
            timeout=ESP32_TIMEOUT
        )
        if resp.status_code == 200:
            print(f"[OK] ESP32 terhubung di {ESP32_IP}:{ESP32_PORT}")
        else:
            print(f"[WARN] ESP32 merespons dengan status {resp.status_code}")
    except Exception:
        print(f"[WARN] ESP32 tidak terjangkau di {ESP32_IP} — pastikan:")
        print(f"       1. ESP32 sudah menyala dan terhubung WiFi")
        print(f"       2. IP di config.py sudah benar")
        print(f"       3. Laptop & ESP32 dalam jaringan WiFi yang sama")

def mulai_pengenalan():
    print("=" * 50)
    print("   SISTEM ABSENSI FACE RECOGNITION")
    print("=" * 50)

    # Validasi model tersedia
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model tidak ditemukan: {MODEL_PATH}")
        print("[INFO]  Jalankan 'python train_model.py' terlebih dahulu.")
        return

    # Cek koneksi ESP32
    cek_esp32()

    # Load model LBPH
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)
    print(f"[OK] Model LBPH dimuat dari {MODEL_PATH}")

    # Load detektor wajah Haar Cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    cam = cv2.VideoCapture(CAMERA_INDEX)
    cam.set(3, 640)
    cam.set(4, 480)

    if not cam.isOpened():
        print("[ERROR] Kamera tidak dapat dibuka.")
        return

    print("\n[INFO] Kamera aktif. Arahkan wajah ke kamera.")
    print(f"[INFO] Threshold confidence: {CONFIDENCE_THRESHOLD}")
    print(f"[INFO] ESP32: {'AKTIF (' + ESP32_IP + ')' if ESP32_ENABLED else 'NONAKTIF'}")
    print("[INFO] Tekan 'Q' untuk keluar.\n")

    # Cooldown: mencegah pencatatan berulang dalam waktu singkat
    cooldown       = {}      # {user_id: frame_counter}
    COOLDOWN_FRAME = 60      # ~2 detik pada 30fps
    frame_count    = 0

    # ============================================================
    # TAMBAHAN: Dictionary untuk mapping label model -> user_id DB
    # ============================================================
    # Load mapping dari file yang dibuat saat training
    label_map_path = MODEL_PATH.replace('.yml', '_labels.npy')
    id_map_path = MODEL_PATH.replace('.yml', '_ids.npy')
    
    label_to_user_id = {}
    if os.path.exists(label_map_path) and os.path.exists(id_map_path):
        labels = np.load(label_map_path, allow_pickle=True).item()
        ids = np.load(id_map_path, allow_pickle=True).item()
        # labels: {folder_name: label_number}
        # ids: {folder_name: user_id_database}
        for folder, label_num in labels.items():
            label_to_user_id[label_num] = ids[folder]
        print(f"[OK] Mapping label dimuat: {label_to_user_id}")
    else:
        print("[WARN] File mapping tidak ditemukan. Menggunakan prediksi langsung.")
        print("[WARN] Pastikan train_model.py menyimpan mapping label!")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("[ERROR] Kamera berhenti membaca frame.")
            break

        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            wajah_roi = gray[y:y+h, x:x+w]

            # Prediksi identitas
            label_pred, confidence = recognizer.predict(wajah_roi)

            # ============================================================
            # PERBAIKAN PENTING: Konversi label model ke user_id database
            # ============================================================
            user_id = label_to_user_id.get(label_pred, label_pred)
            
            # Log untuk debugging
            print(f"[DEBUG] Label prediksi: {label_pred}, User ID: {user_id}, Confidence: {confidence:.2f}")

            if confidence < CONFIDENCE_THRESHOLD:
                # ── WAJAH DIKENALI ──────────────────────────
                user = get_user_by_id(user_id)
                
                # ============================================================
                # PERBAIKAN: Validasi user ditemukan dan confidence cukup rendah
                # ============================================================
                if user and confidence < CONFIDENCE_THRESHOLD:
                    nama = user['nama']
                    nim  = user['nim']

                    # Cek cooldown agar tidak kirim berulang
                    if frame_count > cooldown.get(user_id, 0):
                        berhasil = catat_absensi(user_id, nama, nim)
                        cooldown[user_id] = frame_count + COOLDOWN_FRAME

                        if berhasil:
                            print(f"[ABSEN] {nama} | {nim} — BERHASIL DICATAT")
                            kirim_notifikasi(nama, nim, "berhasil")
                        else:
                            print(f"[INFO]  {nama} sudah absen hari ini.")
                            kirim_notifikasi(nama, nim, "duplikat")

                    # Tampilan: kotak HIJAU
                    label = f"{nama} ({confidence:.0f})"
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 0), 2)
                    cv2.rectangle(frame, (x, y-35), (x+w, y), (0, 200, 0), -1)
                    cv2.putText(frame, label, (x+5, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                else:
                    # User tidak ditemukan di database
                    label = f"ID {user_id} tidak terdaftar ({confidence:.0f})"
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
                    cv2.rectangle(frame, (x, y-35), (x+w, y), (0, 165, 255), -1)
                    cv2.putText(frame, label, (x+5, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            else:
                # ── WAJAH TIDAK DIKENALI ─────────────────────
                label = f"Tidak Dikenali ({confidence:.0f})"
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 200), 2)
                cv2.rectangle(frame, (x, y-35), (x+w, y), (0, 0, 200), -1)
                cv2.putText(frame, label, (x+5, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Info status di layar
        esp32_status = f"ESP32: {'ON ' + ESP32_IP if ESP32_ENABLED else 'OFF'}"
        cv2.putText(frame, "Sistem Absensi Face Recognition",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
        cv2.putText(frame, esp32_status,
                    (10, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        cv2.putText(frame, "Tekan Q untuk keluar",
                    (10, 472), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        cv2.imshow("Absensi — Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] Sistem dihentikan oleh pengguna.")
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    mulai_pengenalan()