/*
 * ============================================================
 *  SISTEM ABSENSI FACE RECOGNITION — ESP32 POLLING (LCD 16x2 I2C)
 *  Hardware : ESP32 Dev Board
 *             LCD 16x2 dengan Backpack I2C (SDA=GPIO21, SCL=GPIO22)
 *             LED Hijau → GPIO 26
 *             LED Merah  → GPIO 27
 *
 *  Fungsi   : Menggunakan metode POLLING. ESP32 secara proaktif
 *             meminta (GET) data dari server Flask di Cloud/Lokal.
 * ============================================================
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// ── KONFIGURASI — SESUAIKAN SEBELUM UPLOAD ───────────────────
const char* WIFI_SSID     = "MERCUSYS_6934";   // SSID WiFi
const char* WIFI_PASSWORD = "Labmr1202_";      // Password WiFi

// URL Endpoint API Polling di Server Flask Anda (Railway / Lokal)
// Ganti bagian host dengan URL Railway atau IP Lokal Anda
// Contoh jika Railway: "https://absensi-production.up.railway.app/api/esp32/poll"
const char* FLASK_URL     = "https://faceabsensi.up.railway.app/api/esp32/poll";

// ── PIN DEFINITION ────────────────────────────────────────────
#define PIN_LED_HIJAU  26
#define PIN_LED_MERAH  27

// ── LCD I2C CONFIGURATION ─────────────────────────────────────
#define LCD_ADDRESS     0x27 
#define LCD_COLUMNS     16
#define LCD_ROWS        2
// ─────────────────────────────────────────────────────────────

LiquidCrystal_I2C  lcd(LCD_ADDRESS, LCD_COLUMNS, LCD_ROWS);

// Timer untuk polling dan reset layar
unsigned long last_poll_time = 0;
const unsigned long POLL_INTERVAL   = 1000; // Tarik data setiap 1 detik
const unsigned long TAMPIL_DURATION = 3000; // Berapa lama notif tampil (ms)

unsigned long waktu_reset = 0;
bool          sedang_tampil = false;

// Deklarasi fungsi tampilan
void tampil_standby();
void tampil_berhasil(String nama, String nim);
void tampil_gagal(String pesan1, String pesan2);

// ── SETUP ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Inisialisasi LED
  pinMode(PIN_LED_HIJAU, OUTPUT);
  pinMode(PIN_LED_MERAH, OUTPUT);
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, LOW);

  // Inisialisasi LCD
  Wire.begin(21, 22);   
  lcd.init();
  lcd.backlight();
  lcd.clear();

  // Layar Boot
  lcd.setCursor(0, 0);
  lcd.print("SISTEM ABSENSI");
  lcd.setCursor(0, 1);
  lcd.print("Connecting WiFi ");

  // Koneksi WiFi
  Serial.println("\n[INFO] Menghubungkan ke WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int coba = 0;
  while (WiFi.status() != WL_CONNECTED && coba < 20) {
    delay(500);
    Serial.print(".");
    lcd.setCursor(14 + (coba % 2), 1);
    lcd.print(".");
    coba++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[OK] WiFi Terhubung!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected!");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP().toString());
    delay(3000);
    tampil_standby();
  } else {
    Serial.println("\n[ERROR] Gagal terhubung ke WiFi!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Conn Failed");
    lcd.setCursor(0, 1);
    lcd.print("Check SSID/Pass");
    digitalWrite(PIN_LED_MERAH, HIGH);
  }
}

// ── LOOP ──────────────────────────────────────────────────────
void loop() {
  // Reconnect WiFi jika putus
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(3000);
    return;
  }

  // Cek apakah sudah waktunya polling ke server (dan tidak sedang menampilkan data)
  if (!sedang_tampil && millis() - last_poll_time >= POLL_INTERVAL) {
    last_poll_time = millis();
    poll_server();
  }

  // Kembalikan layar ke mode standby setelah durasi notifikasi selesai
  if (sedang_tampil && millis() > waktu_reset) {
    sedang_tampil = false;
    digitalWrite(PIN_LED_HIJAU, LOW);
    digitalWrite(PIN_LED_MERAH, LOW);
    tampil_standby();
  }
}

// ── FUNGSI POLLING ────────────────────────────────────────────
void poll_server() {
  WiFiClientSecure client;
  client.setInsecure(); // Mengabaikan validasi SSL certificate (karena Railway pakai HTTPS)
  
  HTTPClient http;
  http.begin(client, FLASK_URL);
  
  // Timeout 5 detik agar koneksi HTTPS yang lebih berat punya waktu
  http.setTimeout(5000);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    // {"status":"ok","data":{"nama":"...","nim":"...","status":"berhasil"}}
    // {"status":"empty","data":null}
    
    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, payload);
    
    if (!err && doc["status"] == "ok") {
      JsonObject data = doc["data"];
      String nama   = data["nama"]   | "Unknown";
      String nim    = data["nim"]    | "--------";
      String status = data["status"] | "gagal";

      Serial.println("[INFO] Data ditarik: " + nama + " | " + status);
      
      if (status == "berhasil") {
        tampil_berhasil(nama, nim);
      } else if (status == "duplikat") {
        tampil_gagal(nama, "SUDAH ABSEN OK! ");
      } else {
        tampil_gagal("ABSENSI GAGAL", "TIDAK DIKENALI");
      }
    }
  } else if (httpCode < 0) {
    Serial.println("[ERROR] Server tidak dapat dijangkau: " + http.errorToString(httpCode));
  }
  
  http.end();
}

// ── TAMPILAN LCD 16x2 ─────────────────────────────────────────

void tampil_standby() {
  lcd.clear();
  lcd.setCursor(1, 0);
  lcd.print("SISTEM ABSENSI");
  lcd.setCursor(0, 1);
  lcd.print("HADAP KE KAMERA ");
}

void tampil_berhasil(String nama, String nim) {
  digitalWrite(PIN_LED_MERAH, LOW);
  digitalWrite(PIN_LED_HIJAU, HIGH);

  lcd.clear();
  if (nama.length() > 16) nama = nama.substring(0, 16);
  lcd.setCursor(0, 0);
  lcd.print(nama);

  String line2 = nim;
  if (line2.length() + 8 <= 16) {
    line2 += " - HADIR";
  } else {
    line2 = line2.substring(0, 16);
  }
  lcd.setCursor(0, 1);
  lcd.print(line2);

  sedang_tampil = true;
  waktu_reset   = millis() + TAMPIL_DURATION;
}

void tampil_gagal(String pesan1, String pesan2) {
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, HIGH);

  lcd.clear();
  if (pesan1.length() > 16) pesan1 = pesan1.substring(0, 16);
  lcd.setCursor(0, 0);
  lcd.print(pesan1);

  if (pesan2.length() > 16) pesan2 = pesan2.substring(0, 16);
  lcd.setCursor(0, 1);
  lcd.print(pesan2);

  sedang_tampil = true;
  waktu_reset   = millis() + TAMPIL_DURATION;
}
