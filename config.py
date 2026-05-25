# config.py — Konfigurasi Terpusat Sistem Absensi
# JANGAN COMMIT FILE INI KE GITHUB (berisi password)

import os

# === KONFIGURASI DATABASE ===
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'absensi_db')
}

# === KONFIGURASI SISTEM ===
DATASET_PATH            = 'dataset'
MODEL_PATH              = 'models/trainer.yml'
SNAPSHOT_PATH           = 'snapshots'
CONFIDENCE_THRESHOLD    = 55
FOTO_PER_USER           = 50
CAMERA_INDEX            = 0
TOLERANSI_MENIT         = 15

# === KONFIGURASI FLASK ===
FLASK_HOST       = '0.0.0.0'
FLASK_PORT       = int(os.environ.get('PORT', 5000))
FLASK_DEBUG      = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
FLASK_SECRET_KEY = os.environ.get('SECRET_KEY', 'ganti-dengan-secret-key-random-panjang-anda')

# === KONFIGURASI ESP32 ===
ESP32_ENABLED = True
# ESP32_IP dan PORT tidak diperlukan lagi karena ESP32 yang akan memanggil server (Polling)

# === KONFIGURASI ANTI-SPOOFING ===
# Threshold 0.0-1.0: semakin rendah semakin toleran (0.5 untuk webcam biasa)
ANTI_SPOOFING_THRESHOLD = 0.5
# Set False untuk menonaktifkan cek spoofing saat development/testing
ANTI_SPOOFING_ENABLED   = False