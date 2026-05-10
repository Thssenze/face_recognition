# CONTEXT.MD — Sistem Absensi Face Recognition


## 1. GAMBARAN UMUM PROYEK

Sistem absensi otomatis berbasis pengenalan wajah (Face Recognition) yang terintegrasi penuh dalam satu aplikasi web Flask. Tidak ada script terpisah yang perlu dijalankan manual — semua fitur (kamera, pengenalan wajah, training, dashboard) berjalan di dalam satu aplikasi.

**Stack teknologi:**
- Backend        : Python 3.10, Flask 3.0
- Computer Vision: OpenCV 4.8 + LBPH Face Recognizer (opencv-contrib)
- Database       : MySQL 8.0 (lokal) / Railway MySQL (production)
- Frontend       : HTML + CSS + Vanilla JS (template Jinja2)
- Hardware       : ESP32 + LCD 16x2 I2C + LED Hijau & Merah
- Deploy         : Railway.app (dashboard + DB), Laptop (kamera + ESP32)

---

## 2. ATURAN UTAMA YANG TIDAK BOLEH DILANGGAR

1. **Python 3.10** — jangan gunakan 3.11, 3.12, atau 3.14. LBPH hanya stabil di 3.10.
2. **Virtual environment wajib aktif** sebelum menjalankan apapun.
3. **Jangan pernah commit `config.py`** ke GitHub — berisi password database.
4. **Jangan pernah commit folder `dataset/`** — berisi foto wajah (privasi).
5. **Jangan pernah commit folder `models/`** — file besar, dibuat ulang via training.
6. **Satu unique constraint absensi**: `(user_id, jadwal_id, tanggal)` — satu mahasiswa hanya bisa absen sekali per matakuliah per hari.
7. **Training model berjalan di background thread** — tidak boleh memblokir request Flask.
8. **Anti-spoofing wajib aktif** sebelum LBPH predict dijalankan.
9. **Semua halaman kecuali `/login` dan `/register`** harus dilindungi `@login_required`.
10. **Toleransi terlambat = 15 menit** setelah `jam_mulai` jadwal — nilai ini tersimpan di kolom `batas_terlambat` pada tabel jadwal.

---

## 3. STRUKTUR FOLDER PROYEK

```
ProyekAbsensi/
│
├── app.py                    # Entry point Flask, semua route
├── database.py               # Semua fungsi query database
├── config.py                 # Konfigurasi (TIDAK di-commit)
├── config.example.py         # Template config (di-commit)
├── setup.py                  # Setup otomatis setelah clone
├── requirements.txt
├── Procfile                  # Untuk deploy Railway
├── runtime.txt               # Versi Python untuk Railway
├── README.md
├── context.md                # File ini
│
├── face/
│   ├── __init__.py
│   ├── recognition.py        # Engine LBPH: predict, load model
│   ├── anti_spoofing.py      # Deteksi wajah asli vs foto
│   └── trainer.py            # Training LBPH dari dataset
│
├── snapshots/                # Foto bukti absensi (tidak di-commit)
│   └── .gitkeep
├── dataset/                  # Foto training per user (tidak di-commit)
│   └── .gitkeep
├── models/                   # Model LBPH (tidak di-commit)
│   └── .gitkeep
│
├── templates/
│   ├── base.html             # Layout utama (navbar, sidebar)
│   ├── login.html
│   ├── register_admin.html
│   ├── dashboard.html        # Live kamera + absen hari ini + % kehadiran
│   ├── mahasiswa/
│   │   ├── index.html        # Daftar semua mahasiswa
│   │   ├── register.html     # Form + ambil foto via kamera
│   │   └── edit.html         # Edit nama, NIM, kelas, foto ulang
│   ├── kelas/
│   │   ├── index.html        # Daftar kelas
│   │   ├── detail.html       # Detail kelas + daftar MK
│   │   └── form.html         # Buat/edit kelas
│   ├── matakuliah/
│   │   ├── index.html
│   │   └── form.html
│   ├── jadwal/
│   │   ├── index.html
│   │   └── form.html
│   ├── absensi/
│   │   ├── manual.html       # Override status oleh admin
│   │   └── rekap.html        # Filter kelas + tanggal + export
│   └── laporan/
│       └── index.html        # % kehadiran + grafik per kelas
│
└── static/
    ├── css/style.css
    └── js/
        ├── camera.js         # Streaming kamera ke dashboard via WebSocket
        └── dashboard.js      # Logic tombol ON/OFF kamera, update real-time
```

---

## 4. SKEMA DATABASE LENGKAP

### Tabel: `admin`
```sql
CREATE TABLE admin (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tabel: `kelas`
```sql
CREATE TABLE kelas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nama_kelas  VARCHAR(100) NOT NULL,
    angkatan    VARCHAR(10)  NOT NULL,
    dibuat_oleh INT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dibuat_oleh) REFERENCES admin(id)
);
```

### Tabel: `matakuliah`
```sql
CREATE TABLE matakuliah (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nama_mk  VARCHAR(100) NOT NULL,
    kode_mk  VARCHAR(20)  UNIQUE NOT NULL,
    kelas_id INT NOT NULL,
    sks      INT DEFAULT 2,
    FOREIGN KEY (kelas_id) REFERENCES kelas(id) ON DELETE CASCADE
);
```

### Tabel: `jadwal`
```sql
CREATE TABLE jadwal (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    matakuliah_id   INT NOT NULL,
    hari            ENUM('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu') NOT NULL,
    jam_mulai       TIME NOT NULL,
    jam_selesai     TIME NOT NULL,
    batas_terlambat TIME NOT NULL,
    FOREIGN KEY (matakuliah_id) REFERENCES matakuliah(id) ON DELETE CASCADE
);
-- batas_terlambat diisi otomatis: ADDTIME(jam_mulai, '00:15:00')
```

### Tabel: `users`
```sql
CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nama       VARCHAR(100) NOT NULL,
    nim        VARCHAR(20)  UNIQUE NOT NULL,
    kelas_id   INT NOT NULL,
    foto_path  VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kelas_id) REFERENCES kelas(id)
);
```

### Tabel: `absensi`
```sql
CREATE TABLE absensi (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT  NOT NULL,
    jadwal_id     INT  NOT NULL,
    tanggal       DATE NOT NULL,
    waktu_absen   TIME,
    status        ENUM('hadir','terlambat','izin','alpha') NOT NULL,
    snapshot_path VARCHAR(255),
    dibuat_manual BOOLEAN  DEFAULT FALSE,
    timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (jadwal_id) REFERENCES jadwal(id),
    UNIQUE KEY uq_absensi (user_id, jadwal_id, tanggal)
);
```

### Tabel: `spoofing_log`
```sql
CREATE TABLE spoofing_log (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    timestamp        DATETIME DEFAULT CURRENT_TIMESTAMP,
    snapshot_path    VARCHAR(255),
    confidence_score FLOAT
);
```

---

## 5. ALUR KERJA SETIAP FITUR

### 5.1 Register Admin
- Endpoint : `GET/POST /register`
- Hanya bisa register jika tabel `admin` masih kosong (0 record)
- Jika sudah ada admin, redirect ke `/login`
- Password di-hash dengan `werkzeug.security.generate_password_hash`

### 5.2 Login / Logout
- Endpoint  : `GET/POST /login`, `GET /logout`
- Gunakan Flask `session` dengan `session['admin_id']`
- Semua route selain `/login` dan `/register` wajib pakai decorator `@login_required`

### 5.3 Register Mahasiswa (via Web)
- Endpoint : `GET/POST /mahasiswa/register`
- Alur:
  1. Admin isi form: nama, NIM, pilih kelas
  2. Kamera web aktif di halaman (via JavaScript getUserMedia)
  3. Ambil 50 foto otomatis (capture frame tiap 200ms)
  4. Foto dikirim ke server via AJAX (base64 → decode → simpan ke dataset/)
  5. Setelah 50 foto tersimpan, trigger training di background thread
  6. Response JSON: {"status": "training", "message": "Training dimulai di background"}
- Training selesai → model trainer.yml diperbarui otomatis
- Mahasiswa langsung bisa dikenali tanpa restart app

### 5.4 Alur Absensi Otomatis (di dalam Dashboard)
```
Kamera ON (tombol di dashboard)
        ↓
Frame dikirim ke server via WebSocket setiap 500ms
        ↓
[Server] anti_spoofing.check(frame)
        ↓ lulus
[Server] recognition.predict(frame) → user_id, confidence
        ↓ confidence < 70
Ambil data user dari DB (nama, nim, kelas_id)
        ↓
Cari jadwal aktif:
  - hari = hari ini
  - jam_mulai <= sekarang <= jam_selesai + buffer 30 menit
        ↓
Cek duplikasi: SELECT dari absensi WHERE user_id + jadwal_id + tanggal
        ↓ belum ada
Tentukan status:
  - waktu <= batas_terlambat  →  "hadir"
  - waktu >  batas_terlambat  →  "terlambat"
        ↓
Simpan snapshot ke snapshots/{user_id}_{tanggal}_{waktu}.jpg
        ↓
INSERT ke tabel absensi
        ↓
Kirim HTTP POST ke ESP32: {nama, nim, status}
        ↓
Kirim response ke dashboard: update tabel absensi hari ini
```

### 5.5 Anti-Spoofing
- File     : `face/anti_spoofing.py`
- Metode   : Texture Analysis menggunakan Local Binary Pattern (LBP)
- Threshold: score > 0.7 = wajah asli, score <= 0.7 = foto/spoofing
- Jika spoofing: simpan snapshot, INSERT ke spoofing_log, tolak absensi

### 5.6 Rekap Absensi
- Endpoint : `GET /absensi/rekap`
- Parameter: `kelas_id`, `tanggal` (atau `dari` + `sampai`), `matakuliah_id` (opsional)
- Alpha otomatis: mahasiswa tanpa record pada jadwal aktif hari itu = alpha
- Export CSV  : `GET /absensi/export?kelas_id=X&tanggal=Y`
- Export Excel: `GET /absensi/export?format=xlsx&kelas_id=X&tanggal=Y`

### 5.7 Persentase Kehadiran
- Formula:
  % hadir     = (jumlah "hadir")     / total_pertemuan * 100
  % terlambat = (jumlah "terlambat") / total_pertemuan * 100
  % izin      = (jumlah "izin")      / total_pertemuan * 100
  % alpha     = (jumlah "alpha" + tidak hadir) / total_pertemuan * 100
- Ditampilkan di dashboard (hari ini) dan halaman laporan (per periode)

### 5.8 ESP32 Integration
- ESP32 menerima HTTP POST di endpoint `/absensi`
- Payload  : {"nama": "...", "nim": "...", "status": "berhasil/duplikat/gagal"}
- LCD       : nama baris 1, NIM + status baris 2
- LED hijau : hadir / terlambat
- LED merah : duplikat / tidak dikenali
- Config    : ESP32_ENABLED, ESP32_IP, ESP32_PORT di config.py

---

## 6. API ENDPOINTS LENGKAP

| Method     | URL                        | Fungsi                            | Auth |
|------------|----------------------------|-----------------------------------|------|
| GET/POST   | /login                     | Login admin                       | No   |
| GET/POST   | /register                  | Register admin (sekali saja)      | No   |
| GET        | /logout                    | Logout                            | Yes  |
| GET        | /                          | Dashboard utama                   | Yes  |
| WebSocket  | /ws/camera                 | Stream frame kamera               | Yes  |
| POST       | /api/camera/toggle         | ON/OFF kamera                     | Yes  |
| GET        | /mahasiswa                 | Daftar mahasiswa                  | Yes  |
| GET/POST   | /mahasiswa/register        | Register mahasiswa baru           | Yes  |
| GET/POST   | /mahasiswa/edit/<id>       | Edit data mahasiswa               | Yes  |
| DELETE     | /mahasiswa/hapus/<id>      | Hapus mahasiswa                   | Yes  |
| POST       | /api/foto/upload           | Upload foto training (AJAX)       | Yes  |
| POST       | /api/training/start        | Mulai training background         | Yes  |
| GET        | /kelas                     | Daftar kelas                      | Yes  |
| GET/POST   | /kelas/tambah              | Tambah kelas baru                 | Yes  |
| GET/POST   | /kelas/edit/<id>           | Edit kelas                        | Yes  |
| DELETE     | /kelas/hapus/<id>          | Hapus kelas                       | Yes  |
| GET        | /kelas/<id>/matakuliah     | MK per kelas                      | Yes  |
| GET/POST   | /matakuliah/tambah         | Tambah MK                         | Yes  |
| GET/POST   | /jadwal                    | Daftar jadwal                     | Yes  |
| GET/POST   | /jadwal/tambah             | Tambah jadwal                     | Yes  |
| GET/POST   | /absensi/manual            | Input absensi manual              | Yes  |
| GET        | /absensi/rekap             | Rekap + filter kelas & tanggal    | Yes  |
| GET        | /absensi/export            | Export CSV / Excel                | Yes  |
| GET        | /laporan                   | Laporan + persentase kehadiran    | Yes  |
| POST       | /api/absensi/proses        | Proses hasil recognition          | Yes  |
| GET        | /api/absensi/hari-ini      | Data absensi real-time (JSON)     | Yes  |

---

## 7. KONFIGURASI (config.py)

```python
# Salin dari config.example.py — jangan commit file ini

DB_CONFIG = {
    'host'    : 'localhost',
    'port'    : 3306,
    'user'    : 'root',
    'password': 'ISI_PASSWORD_ANDA',
    'database': 'absensi_db'
}

DATASET_PATH            = 'dataset'
MODEL_PATH              = 'models/trainer.yml'
SNAPSHOT_PATH           = 'snapshots'
CONFIDENCE_THRESHOLD    = 70
FOTO_PER_USER           = 50
CAMERA_INDEX            = 0
TOLERANSI_MENIT         = 15

FLASK_HOST              = '0.0.0.0'
FLASK_PORT              = 5000
FLASK_SECRET_KEY        = 'ISI_SECRET_KEY_RANDOM_PANJANG'

ESP32_ENABLED           = False
ESP32_IP                = '192.168.X.X'
ESP32_PORT              = 80
ESP32_TIMEOUT           = 3

ANTI_SPOOFING_THRESHOLD = 0.7
```

---

## 8. DEPENDENCIES (requirements.txt)

```
numpy==1.26.4
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
Flask==3.0.3
flask-cors==4.0.0
Werkzeug==3.0.3
mysql-connector-python==8.3.0
Pillow==10.3.0
requests==2.31.0
openpyxl==3.1.2
gunicorn==22.0.0
python-dotenv==1.0.1
flask-socketio==5.3.6
gevent==24.2.1
gevent-websocket==0.10.1
```

---

## 9. PEMBAGIAN TUGAS (REKOMENDASI)

| Anggota | Tanggung Jawab |
|---------|----------------|
| A | Database schema + database.py + setup.py |
| B | Auth (login/register) + Manajemen kelas/MK/jadwal |
| C | Face recognition engine + anti-spoofing + trainer |
| D | Dashboard + live kamera + WebSocket |
| E | Rekap absensi + laporan + export CSV/Excel |
| Semua | Review, testing, deploy Railway |

---

## 10. URUTAN PENGERJAAN (WAJIB DIIKUTI)

```
Tahap 1  →  Database migration (semua tabel baru)
Tahap 2  →  config.py + database.py (semua fungsi query)
Tahap 3  →  Login & Register admin
Tahap 4  →  Manajemen kelas + matakuliah + jadwal
Tahap 5  →  Register mahasiswa via web + foto + auto-training
Tahap 6  →  Engine face recognition + anti-spoofing (face/)
Tahap 7  →  Dashboard + live kamera + WebSocket + absensi otomatis
Tahap 8  →  Rekap absensi + filter kelas/tanggal + export
Tahap 9  →  Laporan + persentase kehadiran
Tahap 10 →  Absensi manual admin
Tahap 11 →  Integrasi ESP32 (jika hardware sudah ada)
Tahap 12 →  Deploy Railway
```

---

## 11. CATATAN DEPLOY (RAILWAY)

**Yang di-deploy ke Railway:**
- app.py + semua templates + static files
- MySQL database Railway
- Folder snapshots/ (foto bukti absensi)

**Yang tetap di laptop:**
- Kamera fisik (webcam)
- ESP32
- face recognition engine (kirim data ke Railway via HTTP)

**File khusus deploy:**
```
# Procfile
web: gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app

# runtime.txt
python-3.10.14
```

**Environment variables di Railway:**
```
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=absensi_db
FLASK_SECRET_KEY=...
ESP32_ENABLED=false
```

---

## 12. KONVENSI KODE

- Bahasa komentar        : Indonesia
- Nama variabel/fungsi   : snake_case
- Nama tabel DB          : snake_case, bahasa Indonesia
- Semua fungsi DB        : ada di database.py — tidak boleh query langsung di app.py
- Semua konfigurasi      : ada di config.py — tidak boleh hardcode nilai di file lain
- Error handling         : semua fungsi DB wajib pakai try/except, return None jika gagal
- Response API           : selalu JSON format {"status": "ok/error", "data": ..., "pesan": ...}

---

## 13. DAFTAR HALAMAN UNTUK DESAIN UI (GOOGLE STITCH)

Urutan prioritas desain:

| No | Halaman             | URL                     | Keterangan |
|----|---------------------|-------------------------|------------|
| 1  | Dashboard           | /                       | Halaman utama — paling kompleks |
| 2  | Login               | /login                  | Form sederhana |
| 3  | Register Admin      | /register               | Form sederhana |
| 4  | Register Mahasiswa  | /mahasiswa/register     | Form + live kamera |
| 5  | Daftar Mahasiswa    | /mahasiswa              | Tabel + search |
| 6  | Edit Mahasiswa      | /mahasiswa/edit/<id>    | Form edit |
| 7  | Manajemen Kelas     | /kelas                  | Tabel + CRUD |
| 8  | Detail Kelas        | /kelas/<id>/matakuliah  | MK per kelas |
| 9  | Manajemen Jadwal    | /jadwal                 | Tabel jadwal per MK |
| 10 | Rekap Absensi       | /absensi/rekap          | Filter + tabel + export |
| 11 | Absensi Manual      | /absensi/manual         | Form override status |
| 12 | Laporan             | /laporan                | Grafik + persentase |

