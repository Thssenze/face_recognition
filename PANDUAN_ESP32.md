# PANDUAN INTEGRASI ESP32 — Sistem Absensi Face Recognition (LCD 16x2 I2C)
> Baca panduan ini saat hardware ESP32, layar LCD 16x2 dengan backpack I2C, dan LED sudah siap dirangkai.

---

## DAFTAR KOMPONEN YANG DIBUTUHKAN

| Komponen              | Jumlah | Keterangan                              |
|-----------------------|--------|-----------------------------------------|
| ESP32 Dev Board       | 1      | Versi 30-pin atau 38-pin                |
| LCD 16x2 I2C          | 1      | Layar LCD 16x2 dengan Backpack I2C soldered |
| LED Hijau             | 1      | Warna hijau (absensi berhasil)          |
| LED Merah             | 1      | Warna merah (gagal / sudah absen)       |
| Resistor 220Ω         | 2      | Untuk membatasi arus LED                |
| Breadboard            | 1      | Untuk merangkai komponen                |
| Kabel jumper          | 10+    | Male-to-male / Female-to-male           |
| Kabel USB             | 1      | Untuk upload kode dari laptop ke ESP32  |

---

## LANGKAH 1 — LIBRARY YANG WAJIB DIINSTALL (ARDUINO IDE)

Sebelum melakukan upload, pastikan Anda telah menginstal pustaka-pustaka berikut melalui **Library Manager** di Arduino IDE (`Ctrl+Shift+I` atau `Sketch -> Include Library -> Manage Libraries...`):

1. **LiquidCrystal I2C** (oleh Frank de Brabander)
2. **ArduinoJson** (oleh Benoit Blanchon - disarankan menggunakan versi 7)

---

## LANGKAH 2 — SKEMA WIRING

### Koneksi Layar LCD 16x2 I2C ke ESP32

> [!NOTE]
> Layar LCD 16x2 memerlukan suplai daya **5V** untuk menghasilkan kecerahan karakter backlight yang optimal. Hubungkan VCC LCD ke pin **VIN** atau **5V** pada board ESP32.

```
LCD 16x2 I2C     ESP32
─────────────────────────
VCC          →   VIN (atau 5V)
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
     LCD SDA ───────┤ GPIO 21             │
     LCD SCL ───────┤ GPIO 22             │
     LCD VCC ───────┤ VIN (5V)       USB  │──── ke Laptop
     LCD GND ───────┤ GND                 │
                    │                     │
    LED Hijau ──R───┤ GPIO 26             │
    LED Merah ──R───┤ GPIO 27             │
    LED GND  ───────┤ GND                 │
                    └─────────────────────┘

    R = Resistor 220Ω
```

---

## LANGKAH 3 — CARI ALAMAT I2C LCD (BIASANYA 0x27 ATAU 0x3F)

Sebagian besar modul backpack LCD I2C menggunakan alamat I2C **0x27** atau **0x3F** secara default. Namun, jika layar tidak menampilkan teks setelah upload, Anda dapat memverifikasi alamatnya dengan meng-upload sketch I2C Scanner berikut ke ESP32:

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
3. Jika alamat yang terdeteksi bukan `0x27` (misal `0x3F`), buka file `esp32_absensi.ino` lalu ubah bagian:
   ```cpp
   #define LCD_ADDRESS 0x27 // Ganti dengan alamat hasil scan Anda jika berbeda
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
4. **Catat IP Address tersebut** (layar LCD 16x2 juga akan menampilkannya selama 3 detik setelah berhasil terkoneksi ke WiFi).

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

Sebelum menjalankan sistem penuh, Anda dapat menguji respons layar LCD & LED menggunakan command prompt (CMD) atau PowerShell di laptop:

### 1. Uji Ping ke ESP32:
```cmd
curl http://192.168.1.15/ping
```
Hasil respons yang diharapkan:
```json
{"status":"ok","ip":"192.168.1.15"}
```

### 2. Kirim Data Absensi Manual (Uji LCD & LED):
```cmd
curl -X POST http://192.168.1.15/absensi -H "Content-Type: application/json" -d "{\"nama\":\"Galang Pratama\",\"nim\":\"210010203\",\"status\":\"berhasil\"}"
```
**Hasil pada Hardware:**
- Layar LCD 16x2 menampilkan baris pertama: **"Galang Pratama"**, dan baris kedua: **"210010203 - HADIR"**.
- LED Hijau menyala selama 3 detik, setelah itu layar kembali ke mode Standby ("SISTEM ABSENSI / HADAP KE KAMERA").

---

## TROUBLESHOOTING

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| Layar LCD menyala biru tapi **tidak ada karakter/tulisan** | Kontras LCD belum diatur. | Putar sekrup kecil berwarna kuning/kuningan (**potensiometer**) di bagian belakang modul backpack I2C LCD menggunakan obeng kecil sampai karakter muncul dengan jelas. |
| Layar LCD tidak menyala sama sekali | Kabel VCC/GND atau SDA/SCL terbalik atau kurang kencang. | Cek kembali perkabelan. Pastikan pin VCC masuk ke 5V/VIN agar backlight menyala. |
| Karakter di LCD berantakan atau terpotong | Nama mahasiswa melebihi 16 karakter. | Kode program secara otomatis memotong (*substring*) nama mahasiswa menjadi maksimal 16 karakter agar pas dalam lebar kolom LCD. |
| ESP32 gagal terhubung ke WiFi | SSID/Password salah atau frekuensi WiFi 5GHz. | ESP32 hanya mendukung jaringan WiFi 2.4GHz. Pastikan konfigurasi SSID/Password benar dan WiFi laptop diset ke frekuensi 2.4GHz. |
| Pengiriman data dari Flask timeout | ESP32 dan laptop berada di jaringan WiFi berbeda. | Hubungkan laptop dan ESP32 ke router/hotspot/tethering yang sama. |
