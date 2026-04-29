# PANDUAN INTEGRASI ESP32 — Sistem Absensi Face Recognition
> Baca panduan ini saat hardware ESP32, LCD 16x2 I2C, dan LED sudah tiba.

---

## DAFTAR KOMPONEN YANG DIBUTUHKAN

| Komponen              | Jumlah | Keterangan                              |
|-----------------------|--------|-----------------------------------------|
| ESP32 Dev Board       | 1      | Versi 30-pin atau 38-pin                |
| LCD 16x2 + Modul I2C  | 1      | Modul I2C biasanya sudah disolder       |
| LED Hijau             | 1      | Warna hijau (absensi berhasil)          |
| LED Merah             | 1      | Warna merah (gagal / sudah absen)       |
| Resistor 220Ω         | 2      | Untuk membatasi arus LED                |
| Breadboard            | 1      | Untuk merangkai komponen                |
| Kabel jumper          | 10+    | Male-to-male                            |
| Kabel USB             | 1      | Untuk upload kode ke ESP32              |

---

## LANGKAH 1 — SKEMA WIRING

### Koneksi LCD 16x2 I2C ke ESP32

```
LCD I2C          ESP32
─────────────────────────
VCC      →   3.3V (atau 5V jika LCD tidak menyala di 3.3V)
GND      →   GND
SDA      →   GPIO 21
SCL      →   GPIO 22
```

### Koneksi LED ke ESP32

```
LED Hijau (+) → Resistor 220Ω → GPIO 26 → GND (kaki pendek LED)
LED Merah (+) → Resistor 220Ω → GPIO 27 → GND (kaki pendek LED)

Kaki panjang LED = Anoda (+)
Kaki pendek LED  = Katoda (−)
```

### Diagram Wiring Lengkap

```
                    ┌─────────────────────┐
                    │       ESP32          │
                    │                     │
    LCD SDA ────────┤ GPIO 21             │
    LCD SCL ────────┤ GPIO 22             │
    LCD VCC ────────┤ 3.3V           USB  │──── ke Laptop
    LCD GND ────────┤ GND                 │
                    │                     │
    LED Hijau ──R───┤ GPIO 26             │
    LED Merah ──R───┤ GPIO 27             │
    LED GND  ───────┤ GND                 │
                    └─────────────────────┘

    R = Resistor 220Ω
```

---

## LANGKAH 2 — CARI ALAMAT I2C LCD (WAJIB DILAKUKAN PERTAMA)

Setiap modul I2C memiliki alamat yang berbeda (biasanya **0x27** atau **0x3F**).
Jalankan sketch berikut di Arduino IDE untuk mendeteksi alamat LCD Anda:

```cpp
#include <Wire.h>

void setup() {
  Wire.begin(21, 22);
  Serial.begin(115200);
  Serial.println("Scanning I2C...");

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Perangkat ditemukan di alamat: 0x");
      Serial.println(addr, HEX);
    }
  }
  Serial.println("Scan selesai.");
}

void loop() {}
```

**Cara menjalankan:**
1. Upload sketch di atas ke ESP32
2. Buka Serial Monitor (Tools → Serial Monitor)
3. Set baud rate ke **115200**
4. Catat alamat yang muncul, contoh: `0x27`

**Jika alamat yang ditemukan bukan 0x27**, buka file `esp32_absensi.ino` dan ubah baris:
```cpp
#define LCD_ADDRESS    0x27   // Ganti dengan alamat hasil scan
```

---

## LANGKAH 3 — KONFIGURASI KODE ARDUINO

Buka file **`esp32_absensi.ino`** di Arduino IDE, lalu ubah 2 baris ini:

```cpp
const char* WIFI_SSID     = "NAMA_WIFI_ANDA";   // ← Ganti nama WiFi
const char* WIFI_PASSWORD = "PASSWORD_WIFI";     // ← Ganti password WiFi
```

Pastikan WiFi yang digunakan **sama** dengan WiFi yang dipakai laptop.

---

## LANGKAH 4 — UPLOAD KODE KE ESP32

1. Sambungkan ESP32 ke laptop via kabel USB
2. Buka Arduino IDE
3. Pilih board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
4. Pilih port: **Tools → Port → COMx** (pilih port yang muncul)
5. Klik tombol **Upload** (→)
6. Tunggu hingga muncul: `Done uploading`

**Jika muncul error saat upload**, tekan dan tahan tombol **BOOT** di ESP32
saat muncul tulisan `Connecting....` di Arduino IDE, lalu lepas setelah upload dimulai.

---

## LANGKAH 5 — CARI IP ADDRESS ESP32

Setelah upload selesai:
1. Buka **Serial Monitor** (Tools → Serial Monitor)
2. Set baud rate ke **115200**
3. Tekan tombol **EN/RESET** di ESP32
4. Tunggu hingga muncul output seperti:

```
[OK] WiFi Terhubung!
[INFO] IP Address ESP32: 192.168.1.20
[INFO] HTTP Server aktif di port 80
```

**Catat IP Address ESP32** — contoh: `192.168.1.20`

LCD juga akan menampilkan IP tersebut selama 3 detik saat pertama menyala.

---

## LANGKAH 6 — UPDATE CONFIG.PY DI LAPTOP

Buka file **`config.py`** di `C:\ProyekAbsensi\`, ubah bagian ESP32:

```python
# === KONFIGURASI ESP32 ===
ESP32_ENABLED = True              # ← Ganti False menjadi True
ESP32_IP      = "192.168.1.20"   # ← Ganti dengan IP ESP32 hasil langkah 5
ESP32_PORT    = 80
ESP32_TIMEOUT = 3
```

---

## LANGKAH 7 — UJI KONEKSI

Pastikan ESP32 sudah menyala dan terhubung WiFi, lalu buka CMD di laptop:

### Tes ping ESP32:
```cmd
curl http://192.168.1.20/ping
```
Hasil yang diharapkan:
```json
{"status":"ok","ip":"192.168.1.20"}
```

### Tes kirim data absensi manual:
```cmd
curl -X POST http://192.168.1.20/absensi ^
  -H "Content-Type: application/json" ^
  -d "{\"nama\":\"Test User\",\"nim\":\"12345678\",\"status\":\"berhasil\"}"
```
Jika berhasil: LCD menampilkan nama & NIM, LED hijau menyala 3 detik.

---

## LANGKAH 8 — JALANKAN SISTEM LENGKAP

Buka **3 CMD** secara bersamaan, masing-masing aktifkan venv:

### CMD 1 — Flask Server (Dashboard):
```cmd
cd C:\ProyekAbsensi
venv\Scripts\activate
python app.py
```

### CMD 2 — Face Recognition Engine:
```cmd
cd C:\ProyekAbsensi
venv\Scripts\activate
python face_recognize.py
```

### CMD 3 — (Opsional) Monitor log real-time:
```cmd
cd C:\ProyekAbsensi
venv\Scripts\activate
curl http://127.0.0.1:5000/api/log
```

---

## ALUR KERJA SISTEM LENGKAP

```
Wajah masuk frame kamera
        ↓
Haar Cascade mendeteksi wajah
        ↓
LBPH predict → confidence < 70?
        ↓
   YA (dikenali)              TIDAK (tidak dikenali)
        ↓                              ↓
Ambil nama & NIM dari DB        LED Merah menyala
        ↓                       LCD: "Wajah Tidak Dikenali"
Sudah absen hari ini?
   ↓              ↓
  BELUM          SUDAH
   ↓              ↓
INSERT DB     Kirim "duplikat"
   ↓              ↓
Kirim "berhasil"  LED Merah
   ↓              LCD: "Sudah Absen"
LED Hijau menyala
LCD: Nama + NIM + OK
Dashboard otomatis update
```

---

## CHECKLIST PENGUJIAN AKHIR

- [ ] LCD menyala dan menampilkan "Siap Absensi"
- [ ] IP ESP32 muncul di Serial Monitor saat pertama boot
- [ ] `curl /ping` ke ESP32 merespons `{"status":"ok"}`
- [ ] Kirim data manual via curl → LCD & LED merespons
- [ ] `ESP32_ENABLED = True` dan IP sudah diupdate di config.py
- [ ] Jalankan `face_recognize.py` → saat wajah dikenali, ESP32 merespons
- [ ] LED hijau menyala saat absensi berhasil
- [ ] LED merah menyala saat wajah tidak dikenali atau sudah absen
- [ ] Dashboard di browser terupdate otomatis

---

## TROUBLESHOOTING

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| LCD tidak menyala | Alamat I2C salah | Jalankan I2C Scanner, ubah LCD_ADDRESS |
| LCD menyala tapi kosong | Kontras terlalu rendah | Putar potensio di belakang modul I2C |
| ESP32 gagal konek WiFi | SSID/password salah | Cek kembali di kode, re-upload |
| IP ESP32 tidak muncul | WiFi belum terhubung | Pastikan SSID & password benar |
| curl ping timeout | Beda jaringan WiFi | Pastikan laptop & ESP32 1 jaringan |
| LED tidak menyala | Pin salah / resistor | Cek wiring, pastikan GPIO 26 & 27 |
| Upload gagal | Driver CH340 belum ada | Install driver CP210x atau CH340 |

---

## CATATAN TAMBAHAN

**Menambah user baru setelah sistem berjalan:**
```cmd
python face_register.py    ← daftarkan wajah baru
python train_model.py      ← latih ulang model
(face_recognize.py dan esp32 tidak perlu diubah)
```

**Jika ingin mengubah durasi LED menyala**, buka `esp32_absensi.ino`:
```cpp
const unsigned long DURASI_BERHASIL = 3000;  // 3 detik (dalam milidetik)
const unsigned long DURASI_DUPLIKAT = 2000;  // 2 detik
const unsigned long DURASI_GAGAL    = 2000;  // 2 detik
```
Ubah nilai, lalu re-upload ke ESP32.
