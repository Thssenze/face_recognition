# PANDUAN INTEGRASI ESP32 — Sistem Absensi Face Recognition (OLED SSD1306)
> Baca panduan ini saat hardware ESP32, layar OLED SSD1306 I2C, dan LED sudah siap dirangkai.

---

## DAFTAR KOMPONEN YANG DIBUTUHKAN

| Komponen              | Jumlah | Keterangan                              |
|-----------------------|--------|-----------------------------------------|
| ESP32 Dev Board       | 1      | Versi 30-pin atau 38-pin                |
| OLED SSD1306 128x64   | 1      | Layar OLED I2C                          |
| LED Hijau             | 1      | Warna hijau (absensi berhasil)          |
| LED Merah             | 1      | Warna merah (gagal / sudah absen)       |
| Resistor 220Ω         | 2      | Untuk membatasi arus LED                |
| Breadboard            | 1      | Untuk merangkai komponen                |
| Kabel jumper          | 10+    | Male-to-male / Female-to-male           |
| Kabel USB             | 1      | Untuk upload kode dari laptop ke ESP32  |

---

## LANGKAH 1 — LIBRARY YANG WAJIB DIINSTALL (ARDUINO IDE)

Sebelum melakukan upload, pastikan Anda telah menginstal pustaka-pustaka berikut melalui **Library Manager** di Arduino IDE (`Ctrl+Shift+I` atau `Sketch -> Include Library -> Manage Libraries...`):

1. **Adafruit SSD1306** (oleh Adafruit)
2. **Adafruit GFX Library** (oleh Adafruit)
3. **ArduinoJson** (oleh Benoit Blanchon - disarankan menggunakan versi 7)

---

## LANGKAH 2 — SKEMA WIRING

### Koneksi Layar OLED SSD1306 ke ESP32

```
OLED SSD1306     ESP32
─────────────────────────
VCC          →   3.3V (atau 5V jika modul mendukung 5V)
GND          →   GND
SDA          →   GPIO 21 (SDA)
SCL          →   GPIO 22 (SCL)
```

### Koneksi LED ke ESP32

```
LED Hijau (+) → Resistor 220Ω → GPIO 26 → GND (kaki pendek LED)
LED Merah (+) → Resistor 220Ω → GPIO 27 → GND (kaki pendek LED)

Catatan:
- Kaki panjang LED = Anoda (+)
- Kaki pendek LED  = Katoda (−)
```

### Diagram Wiring Lengkap

```
                    ┌─────────────────────┐
                    │       ESP32          │
                    │                     │
    OLED SDA ───────┤ GPIO 21             │
    OLED SCL ───────┤ GPIO 22             │
    OLED VCC ───────┤ 3.3V           USB  │──── ke Laptop
    OLED GND ───────┤ GND                 │
                    │                     │
    LED Hijau ──R───┤ GPIO 26             │
    LED Merah ──R───┤ GPIO 27             │
    LED GND  ───────┤ GND                 │
                    └─────────────────────┘

    R = Resistor 220Ω
```

---

## LANGKAH 3 — CARI ALAMAT I2C OLED (BIASANYA 0x3C)

Sebagian besar modul OLED SSD1306 menggunakan alamat I2C **0x3C** secara default. Namun, jika layar tidak menyala setelah upload, Anda dapat memverifikasi alamatnya dengan meng-upload sketch I2C Scanner berikut ke ESP32:

```cpp
#include <Wire.h>

void setup() {
  Wire.begin(21, 22);
  Serial.begin(115200);
  Serial.println("\nScanning I2C...");

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
1. Upload sketch scanner di atas ke ESP32.
2. Buka **Serial Monitor** (Tools → Serial Monitor) dan set baud rate ke **115200**.
3. Jika alamat yang terdeteksi bukan `0x3C` (misal `0x3D`), buka file `esp32_absensi.ino` lalu ubah bagian:
   ```cpp
   #define SCREEN_ADDRESS 0x3C // Ganti dengan alamat hasil scan Anda
   ```

---

## LANGKAH 4 — UPLOAD KODE UTAMA KE ESP32

1. Sambungkan ESP32 ke laptop menggunakan kabel USB.
2. Buka folder proyek absensi dan buka file **`esp32_absensi/esp32_absensi.ino`** di Arduino IDE.
3. Pastikan konfigurasi WiFi pada kode sesuai dengan WiFi yang sedang Anda gunakan (laptop & ESP32 wajib berada dalam 1 jaringan WiFi):
   ```cpp
   const char* WIFI_SSID     = "BOUTY FAMILLY"; 
   const char* WIFI_PASSWORD = "Galang14";
   ```
4. Pilih board target: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
5. Pilih port COM yang terdeteksi: **Tools → Port → COMx** (misal COM3/COM4)
6. Klik tombol **Upload** (tanda panah kanan `→`).
   *(Tips: Jika muncul pesan `Connecting....`, tekan dan tahan tombol **BOOT** pada board ESP32 hingga proses penulisan flash dimulai)*

---

## LANGKAH 5 — CARI IP ADDRESS ESP32

Setelah upload selesai:
1. Tetap buka **Serial Monitor** (Baud rate: **115200**).
2. Tekan tombol **EN/RESET** di board ESP32.
3. Tunggu hingga muncul informasi status seperti:
   ```
   [OK] WiFi Terhubung!
   [INFO] IP Address ESP32: 192.168.1.15
   [INFO] HTTP Server aktif di port 80
   ```
4. **Catat IP Address tersebut** (layar OLED juga akan menampilkannya selama 3 detik setelah berhasil terkoneksi ke WiFi).

---

## LANGKAH 6 — INTEGRASI DENGAN FLASK (CONFIG.PY)

Buka file **`config.py`** di folder proyek Anda pada laptop, kemudian aktifkan dan isi IP ESP32 yang didapatkan:

```python
# === KONFIGURASI ESP32 ===
ESP32_ENABLED = True              # Ubah menjadi True untuk mengaktifkan
ESP32_IP      = "192.168.1.15"   # Masukkan IP ESP32 Anda di sini
ESP32_PORT    = 80
ESP32_TIMEOUT = 3
```

---

## LANGKAH 7 — VERIFIKASI PENGUJIAN

Sebelum menjalankan sistem penuh, Anda dapat menguji respons layar OLED & LED menggunakan command prompt (CMD) di laptop:

### 1. Uji Ping ke ESP32:
```cmd
curl http://192.168.1.15/ping
```
Hasil respons yang diharapkan:
```json
{"status":"ok","ip":"192.168.1.15"}
```

### 2. Kirim Data Absensi Manual (Uji OLED & LED):
```cmd
curl -X POST http://192.168.1.15/absensi -H "Content-Type: application/json" -d "{\"nama\":\"Galang Pratama\",\"nim\":\"210010203\",\"status\":\"berhasil\"}"
```
**Hasil pada Hardware:**
- Layar OLED menampilkan kotak border dengan header **"ABSENSI BERHASIL"**, baris nama **"Galang Pratama"**, NIM **"210010203"**, dan status **"Status: HADIR OK"**.
- LED Hijau menyala selama 3 detik, setelah itu layar kembali ke mode Standby ("SISTEM ABSENSI - HADAP KE KAMERA").

---

## TROUBLESHOOTING

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| Layar OLED tidak menyala sama sekali | Kabel VCC/GND atau SDA/SCL terbalik; alamat I2C tidak tepat. | Cek kembali perkabelan. Jalankan I2C scanner untuk memverifikasi alamat (misal `0x3D` atau `0x3C`). |
| Teks pada OLED terpotong | Nama mahasiswa terlalu panjang. | Kode secara otomatis membatasi nama maksimal 18 karakter agar pas dalam lebar layar OLED. |
| ESP32 gagal terhubung ke WiFi | SSID/Password salah atau frekuensi WiFi 5GHz (ESP32 hanya mendukung 2.4GHz). | Pastikan konfigurasi SSID/Password benar dan WiFi laptop diset ke 2.4GHz. |
| Pengiriman data dari Flask timeout | ESP32 dan laptop berada di jaringan WiFi berbeda. | Hubungkan laptop dan ESP32 ke router/hotspot yang sama. |
