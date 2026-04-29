# test_setup.py

import requests


print("=== TES PERSIAPAN SISTEM ABSENSI ===\n")

# Tes 1: NumPy
try:
    import numpy as np
    print(f"[OK] NumPy {np.__version__}")
except: print("[GAGAL] NumPy")

# Tes 2: OpenCV
try:
    import cv2
    print(f"[OK] OpenCV {cv2.__version__}")
except: print("[GAGAL] OpenCV")

# Tes 3: LBPH Face Recognizer
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("[OK] LBPH Face Recognizer tersedia")
except: print("[GAGAL] LBPH — pastikan opencv-contrib-python terinstall")

# Tes 4: Webcam
try:
    cam = cv2.VideoCapture(0)
    if cam.isOpened():
        print("[OK] Webcam terdeteksi")
        cam.release()
    else:
        print("[PERINGATAN] Webcam tidak terdeteksi")
except: print("[GAGAL] Webcam")

# Tes 5: Flask
try:
    import flask
    print(f"[OK] Flask {flask.__version__}")
except: print("[GAGAL] Flask")

# Tes 6: MySQL
try:
    import mysql.connector
    from config import DB_CONFIG
    conn = mysql.connector.connect(**DB_CONFIG)
    if conn.is_connected():
        print("[OK] Koneksi MySQL berhasil")
        conn.close()
except Exception as e:
    print(f"[GAGAL] MySQL — {e}")

# Tes 7: Pillow
try:
    from PIL import Image
    print("[OK] Pillow tersedia")
except: print("[GAGAL] Pillow")

# Tes 8: requests
try:
    import requests
    print(f"[OK] Flask {requests.__version__}")
except: print("[GAGAL] requests")

print("\n=== TES SELESAI ===")