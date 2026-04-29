# config.example.py — TEMPLATE KONFIGURASI
# =====================================================
# CARA PAKAI:
# 1. Salin file ini, rename menjadi config.py
# 2. Isi semua nilai yang bertanda  <-- GANTI INI
# 3. Jangan pernah upload config.py ke GitHub!
# =====================================================

# === KONFIGURASI DATABASE ===
DB_CONFIG = {
    'host'    : 'localhost',
    'port'    : 3306,
    'user'    : 'root',
    'password': 'GANTI_PASSWORD_MYSQL_ANDA',   # <-- GANTI INI
    'database': 'absensi_db'
}

# === KONFIGURASI SISTEM ===
DATASET_PATH         = 'dataset'
MODEL_PATH           = 'models/trainer.yml'
CONFIDENCE_THRESHOLD = 70
FOTO_PER_USER        = 50
CAMERA_INDEX         = 0    # 0 = webcam bawaan, 1 = webcam eksternal

# === KONFIGURASI FLASK ===
FLASK_HOST  = '0.0.0.0'
FLASK_PORT  = 5000
FLASK_DEBUG = True

# === KONFIGURASI ESP32 ===
ESP32_ENABLED = False          # Ganti True jika ESP32 sudah tersedia
ESP32_IP      = '192.168.X.X' # <-- GANTI dengan IP ESP32 Anda
ESP32_PORT    = 80
ESP32_TIMEOUT = 3
