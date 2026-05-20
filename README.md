# 🎓 Sistem Absensi Face Recognition

Sistem absensi otomatis berbasis pengenalan wajah (Face Recognition) yang terintegrasi penuh dalam satu aplikasi web Flask. Menggunakan OpenCV LBPH, Python 3.10, MySQL, WebSocket (Flask-SocketIO), dan mendukung integrasi perangkat keras ESP32.

---

## ✨ Fitur Utama

- 🎥 **Unified Web Application**: Kamera, pendaftaran mahasiswa, pengenalan wajah real-time, training model, dan dashboard admin terpadu dalam satu server Flask. Tidak memerlukan script terpisah!
- ⚡ **Real-Time WebSockets**: Streaming video dari webcam laptop/kamera ke dashboard web secara langsung dan responsif menggunakan Flask-SocketIO.
- 🛡️ **Anti-Spoofing Engine**: Mencegah kecurangan absensi menggunakan foto/layar HP dengan analisis tekstur wajah berbasis Local Binary Patterns (LBP).
- 🧠 **Background Model Training**: Pelatihan model pengenalan wajah (LBPH) dilakukan secara asinkron di background thread tanpa mengganggu jalannya aplikasi web Flask.
- 📆 **Sistem Penjadwalan Dinamis**: Dukungan manajemen Kelas, Mata Kuliah, dan Jadwal Kuliah lengkap dengan batas toleransi keterlambatan.
- 🕒 **Auto-Alpha Engine**: Background worker yang berjalan setiap 60 detik untuk menandai mahasiswa yang tidak hadir setelah jam mata kuliah berakhir secara otomatis menjadi `alpha`.
- 📝 **Absensi Manual & Izin**: Fitur pencatatan absensi manual oleh admin untuk mengubah status menjadi `Hadir`, `Terlambat`, `Izin`, `Sakit`, atau `Alpha` lengkap dengan form alasan/keterangan.
- 📊 **Rekapitulasi & Ekspor Laporan**: Fitur penyaringan absensi berdasarkan Kelas, Mata Kuliah, dan Rentang Tanggal, serta dapat diunduh dalam format **Excel (.xlsx)** atau **CSV**.
- 🔌 **Integrasi Perangkat Keras (ESP32)**: Opsional, menampilkan nama mahasiswa yang berhasil absen di LCD 16x2 I2C serta menyalakan LED indikator status (Hijau = Berhasil, Merah = Gagal/Duplikat).

---

## 🛠️ Teknologi & Stack

| Komponen | Teknologi |
|---|---|
| **Bahasa Pemrograman** | Python 3.10 |
| **Computer Vision** | OpenCV 4.8.1 (dengan `opencv-contrib-python` untuk LBPH) |
| **Web Framework** | Flask 3.0.3 |
| **Realtime Engine** | Flask-SocketIO 5.6.1 + WebSockets |
| **Database** | MySQL 8.0 (lokal atau cloud seperti Railway) |
| **Ekspor Excel** | openpyxl 3.1.5 |
| **Mikrokontroler** | ESP32 (Arduino IDE) + LCD 16x2 I2C + Dual LED |

---

## 📋 Persyaratan Sistem

- Python **3.10.x** (Wajib, LBPH Face Recognizer tidak stabil di versi 3.11+)
- MySQL Server 8.0+
- Webcam bawaan laptop atau USB External Camera
- Arduino IDE (Hanya jika menggunakan modul fisik ESP32)

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Persiapan Proyek

Clone repository ini ke mesin lokal Anda:
```bash
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. Membuat Virtual Environment (Wajib Python 3.10)

Aktifkan virtual environment sebelum melanjutkan:
```bash
# Windows
py -3.10 -m venv venv
venv\Scripts\activate

# Linux / macOS
python3.10 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install seluruh pustaka Python yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Sistem

Salin template berkas konfigurasi menjadi `config.py` dan sesuaikan nilainya (password database, port, dll.):
```bash
# Windows
copy config.example.py config.py

# Linux / macOS
cp config.example.py config.py
```
> [!IMPORTANT]
> Jangan pernah meng-commit berkas `config.py` ke repositori git karena berisi data kredensial penting.

### 5. Inisialisasi Database

Jalankan script migrasi otomatis untuk membuat database, seluruh tabel relasional, dan user admin pertama secara interaktif:
```bash
python run_migration.py
```

### 6. Uji Coba Kesiapan Sistem

Gunakan script diagnostik untuk memverifikasi apakah webcam, MySQL, dan seluruh pustaka OpenCV/LBPH sudah terpasang dengan benar:
```bash
python test_setup.py
```

---

## 💻 Cara Menjalankan Aplikasi

Setelah semua langkah instalasi di atas selesai dengan sukses, Anda hanya perlu menjalankan satu perintah untuk memulai seluruh sistem:

```bash
python app.py
```

Server akan aktif pada alamat:
- **Dashboard Web**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Halaman Login Admin**: masukkan kredensial yang Anda daftarkan saat menjalankan `run_migration.py`.

Semua aktivitas absensi wajah, pendaftaran wajah mahasiswa baru, training model, manajemen kelas, dan rekapitulasi data kini dapat dilakukan sepenuhnya melalui antarmuka web yang modern dan responsif.

---

## 🔌 Panduan Perangkat Keras ESP32 (Opsional)

Jika Anda ingin mengintegrasikan sistem dengan perangkat keras ESP32 untuk notifikasi visual di kelas fisik:
1. Hubungkan komponen LCD 16x2 I2C dan LED sesuai dengan panduan skema di berkas **[PANDUAN_ESP32.md](PANDUAN_ESP32.md)**.
2. Unggah file sketch **`esp32_absensi/esp32_absensi.ino`** ke board ESP32 Anda menggunakan Arduino IDE.
3. Ubah konfigurasi di `config.py` Anda:
   ```python
   ESP32_ENABLED = True
   ESP32_IP      = "192.168.x.x"  # IP Address ESP32 yang terhubung WiFi
   ```

---

## 📁 Struktur Folder Proyek

```
ProyekAbsensi/
├── app.py                    # Entry point server Flask & SocketIO
├── database.py               # Seluruh modul query & manipulasi MySQL
├── config.py                 # Konfigurasi parameter & kredensial aplikasi
├── config.example.py         # Template berkas konfigurasi untuk pengembang
├── run_migration.py          # Script interaktif pembuat database & admin
├── test_setup.py             # Script verifikasi kesiapan pustaka & perangkat
├── requirements.txt          # Daftar paket python pihak ketiga
├── PANDUAN_ESP32.md          # Panduan wiring & instruksi hardware ESP32
│
├── face/                     # Mesin utama Computer Vision
│   ├── recognition.py        # Prediksi wajah & anti-spoofing logic
│   ├── anti_spoofing.py      # Klasifikasi tekstur LBP wajah asli vs foto
│   └── trainer.py            # Modul latih model LBPH asinkron
│
├── esp32_absensi/
│   └── esp32_absensi.ino     # Sketch Arduino untuk perangkat keras ESP32
│
├── dataset/                  # Folder penyimpanan foto wajah mahasiswa (git-ignored)
├── models/                   # Folder hasil training model trainer.yml (git-ignored)
├── snapshots/                # Berkas tangkapan bukti absensi wajah (git-ignored)
│
├── templates/                # Berkas HTML template Jinja2
│   ├── base.html             # Layout global (Sidebar & Navbar)
│   ├── dashboard.html        # Live kamera web + absensi hari ini + kontrol kamera
│   ├── mahasiswa/            # Registrasi (ambil foto web) & daftar mahasiswa
│   ├── kelas/                # Manajemen data kelas mahasiswa
│   ├── matakuliah/           # Manajemen mata kuliah
│   ├── jadwal/               # Penjadwalan & batas toleransi terlambat
│   └── absensi/              # Rekapitulasi absensi & filter export data
│
└── static/                   # Aset statis client-side (CSS, JS)
```

---

## ⚠️ File Legacy yang Tidak Diperlukan Lagi

Sistem absensi ini kini berjalan sepenuhnya pada platform web. File-file CLI berikut di direktori utama **sudah tidak diperlukan lagi** untuk operasional harian dan dapat dihapus dengan aman untuk merapikan repositori:
- **`face_register.py`** (Digantikan oleh fitur registrasi mahasiswa interaktif berbasis web)
- **`face_recognize.py`** (Digantikan oleh mesin recognition terintegrasi di dashboard web menggunakan WebSockets)
- **`train_model.py`** (Digantikan oleh background training di panel dashboard web admin)

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah **MIT License** — bebas digunakan untuk keperluan edukasi maupun pengembangan akademis.