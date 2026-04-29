# 🎓 Sistem Absensi Face Recognition

Sistem absensi otomatis berbasis pengenalan wajah menggunakan Python, OpenCV LBPH, Flask, MySQL, dan ESP32 (LCD 16x2 + LED indikator).

---

## ✨ Fitur

- Deteksi & pengenalan wajah real-time via webcam
- Pencatatan absensi otomatis ke database MySQL
- Pencegahan absensi ganda dalam satu hari
- Dashboard web real-time (auto-refresh 10 detik)
- Laporan absensi dengan filter rentang tanggal
- Export data ke CSV
- Manajemen user (tambah & hapus)
- Integrasi ESP32: LCD 16x2 menampilkan nama, LED indikator status

---

## 🛠️ Teknologi

| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.10 |
| Computer Vision | OpenCV 4.8 + LBPH Face Recognizer |
| Web Framework | Flask 3.0 |
| Database | MySQL 8.0 |
| Mikrokontroler | ESP32 + Arduino |
| Display | LCD 16x2 I2C |

---

## 📋 Persyaratan

- Python **3.10** (direkomendasikan, bukan 3.11+)
- MySQL Server 8.0+
- Webcam
- Arduino IDE (untuk ESP32)

---

## 🚀 Cara Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. Buat Virtual Environment dengan Python 3.10

```bash
# Windows
py -3.10 -m venv venv
venv\Scripts\activate

# Linux / macOS
python3.10 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfigurasi

```bash
# Salin template konfigurasi
copy config.example.py config.py     # Windows
cp config.example.py config.py       # Linux/macOS

# Edit config.py dan isi password MySQL, IP ESP32, dll.
```

### 5. Buat Database MySQL

Login ke MySQL lalu jalankan:

```sql
CREATE DATABASE absensi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE absensi_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    nim VARCHAR(20) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE absensi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nama VARCHAR(100),
    nim VARCHAR(20),
    tanggal DATE,
    waktu TIME,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 6. Jalankan Setup Otomatis

Script ini akan membuat folder, membuat tabel database, dan memverifikasi semua komponen sekaligus:

```bash
python setup.py
```

Semua item harus menampilkan `[OK]` sebelum melanjutkan.

---

## 📖 Cara Penggunaan

### Registrasi Wajah Baru

```bash
python face_register.py
```
Ikuti instruksi di layar. Ambil ±50 foto dengan variasi posisi wajah.

### Training Model

```bash
python train_model.py
```
Jalankan ulang setiap kali ada user baru didaftarkan.

### Menjalankan Sistem (2 CMD terpisah)

**CMD 1 — Dashboard:**
```bash
python app.py
# Buka browser: http://127.0.0.1:5000
```

**CMD 2 — Pengenalan Wajah:**
```bash
python face_recognize.py
```

---

## 🔌 Integrasi ESP32 (Opsional)

Lihat **[PANDUAN_ESP32.md](PANDUAN_ESP32.md)** untuk panduan lengkap wiring dan upload kode.

Setelah ESP32 terhubung, update `config.py`:
```python
ESP32_ENABLED = True
ESP32_IP      = "192.168.X.X"  # IP ESP32 Anda
```

---

## 📁 Struktur Folder

```
├── app.py                  # Flask server & dashboard
├── face_register.py        # Registrasi wajah baru
├── face_recognize.py       # Engine pengenalan real-time
├── train_model.py          # Training model LBPH
├── database.py             # Fungsi koneksi & query DB
├── config.example.py       # Template konfigurasi (salin → config.py)
├── setup.py                # Setup otomatis (jalankan sekali setelah clone)
├── requirements.txt        # Daftar library Python
├── PANDUAN_ESP32.md        # Panduan integrasi ESP32
├── esp32_absensi.ino       # Kode Arduino untuk ESP32
├── dataset/                # (dibuat otomatis) Foto wajah per user
└── models/                 # (dibuat otomatis) Model LBPH hasil training
```

---

## ⚠️ Catatan Penting

- File `config.py` **tidak diupload ke GitHub** karena berisi password
- Folder `dataset/` dan `models/` **tidak diupload** (privasi & ukuran)
- Gunakan **Python 3.10** — versi 3.12+ belum tentu kompatibel dengan OpenCV LBPH
- Pastikan laptop dan ESP32 terhubung ke **WiFi yang sama**

---

## 📄 Lisensi

MIT License — bebas digunakan untuk keperluan pendidikan.