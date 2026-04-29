/*
 * ============================================================
 *  SISTEM ABSENSI FACE RECOGNITION — ESP32 RECEIVER
 *  Hardware : ESP32 Dev Board
 *             LCD 16x2 + Modul I2C (PCF8574, alamat 0x27)
 *             LED Hijau → GPIO 26
 *             LED Merah  → GPIO 27
 *
 *  Fungsi   : Menerima HTTP POST dari Flask (laptop),
 *             menampilkan nama & NIM di LCD,
 *             menyalakan LED sesuai status absensi.
 * ============================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// ── KONFIGURASI — SESUAIKAN SEBELUM UPLOAD ───────────────────
const char* WIFI_SSID     = "NAMA_WIFI_ANDA";   // Ganti dengan nama WiFi
const char* WIFI_PASSWORD = "PASSWORD_WIFI";     // Ganti dengan password WiFi
// ─────────────────────────────────────────────────────────────

// ── PIN DEFINITION ────────────────────────────────────────────
#define PIN_LED_HIJAU  26
#define PIN_LED_MERAH  27
#define LCD_ADDRESS    0x27   // Coba 0x3F jika LCD tidak menyala
#define LCD_COLS       16
#define LCD_ROWS       2
// ─────────────────────────────────────────────────────────────

WebServer        server(80);
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);

// Durasi nyala LED & tampilan LCD (milidetik)
const unsigned long DURASI_BERHASIL = 3000;
const unsigned long DURASI_DUPLIKAT = 2000;
const unsigned long DURASI_GAGAL    = 2000;

// Waktu kapan LCD & LED harus direset ke standby
unsigned long waktu_reset = 0;
bool          sedang_tampil = false;

// ── SETUP ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Inisialisasi LED
  pinMode(PIN_LED_HIJAU, OUTPUT);
  pinMode(PIN_LED_MERAH, OUTPUT);
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, LOW);

  // Inisialisasi LCD
  Wire.begin(21, 22);   // SDA=GPIO21, SCL=GPIO22
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sistem  Absensi");
  lcd.setCursor(0, 1);
  lcd.print("Menghubungkan...");

  // Koneksi WiFi
  Serial.println("\n[INFO] Menghubungkan ke WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int coba = 0;
  while (WiFi.status() != WL_CONNECTED && coba < 20) {
    delay(500);
    Serial.print(".");
    coba++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[OK] WiFi Terhubung!");
    Serial.print("[INFO] IP Address ESP32: ");
    Serial.println(WiFi.localIP());

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Terhubung!");
    lcd.setCursor(0, 1);
    // Tampilkan IP (potong jika terlalu panjang)
    String ip = WiFi.localIP().toString();
    lcd.print(ip.substring(0, 16));
    delay(3000);
    tampil_standby();
  } else {
    Serial.println("\n[ERROR] Gagal terhubung ke WiFi!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi GAGAL!");
    lcd.setCursor(0, 1);
    lcd.print("Cek SSID/Pass");
    // Nyalakan LED merah sebagai indikator error
    digitalWrite(PIN_LED_MERAH, HIGH);
  }

  // Daftarkan endpoint HTTP
  server.on("/absensi",    HTTP_POST, handle_absensi);
  server.on("/ping",       HTTP_GET,  handle_ping);
  server.on("/",           HTTP_GET,  handle_root);
  server.onNotFound(handle_not_found);

  server.begin();
  Serial.println("[INFO] HTTP Server aktif di port 80");
  Serial.println("[INFO] Endpoint: POST /absensi");
}

// ── LOOP ──────────────────────────────────────────────────────
void loop() {
  server.handleClient();

  // Reset LCD & LED ke standby setelah durasi habis
  if (sedang_tampil && millis() > waktu_reset) {
    sedang_tampil = false;
    digitalWrite(PIN_LED_HIJAU, LOW);
    digitalWrite(PIN_LED_MERAH, LOW);
    tampil_standby();
  }

  // Reconnect WiFi jika terputus
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] WiFi terputus, mencoba reconnect...");
    WiFi.reconnect();
    delay(3000);
  }
}

// ── HANDLER: POST /absensi ────────────────────────────────────
/*
 * Format JSON yang diterima dari Flask:
 * {
 *   "nama"   : "Budi Santoso",
 *   "nim"    : "12345678",
 *   "status" : "berhasil"   // atau "duplikat" atau "gagal"
 * }
 */
void handle_absensi() {
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"error\":\"Body kosong\"}");
    return;
  }

  String body = server.arg("plain");
  Serial.println("[INFO] Data diterima: " + body);

  // Parse JSON
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, body);
  if (err) {
    Serial.println("[ERROR] JSON tidak valid: " + String(err.c_str()));
    server.send(400, "application/json", "{\"error\":\"JSON tidak valid\"}");
    return;
  }

  String nama   = doc["nama"]   | "Unknown";
  String nim    = doc["nim"]    | "--------";
  String status = doc["status"] | "gagal";

  // Potong nama agar muat di LCD 16 karakter
  if (nama.length() > 16) nama = nama.substring(0, 16);
  if (nim.length()  > 16) nim  = nim.substring(0, 16);

  Serial.println("[INFO] Nama   : " + nama);
  Serial.println("[INFO] NIM    : " + nim);
  Serial.println("[INFO] Status : " + status);

  // Tampilkan di LCD & nyalakan LED
  if (status == "berhasil") {
    tampil_berhasil(nama, nim);
  } else if (status == "duplikat") {
    tampil_duplikat(nama);
  } else {
    tampil_gagal();
  }

  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

// ── HANDLER: GET /ping ────────────────────────────────────────
void handle_ping() {
  String json = "{\"status\":\"ok\",\"ip\":\"" + WiFi.localIP().toString() + "\"}";
  server.send(200, "application/json", json);
}

// ── HANDLER: GET / ────────────────────────────────────────────
void handle_root() {
  String html = "<h2>ESP32 Absensi Server</h2>";
  html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
  html += "<p>Status: Online</p>";
  html += "<p>Endpoint: POST /absensi</p>";
  server.send(200, "text/html", html);
}

// ── HANDLER: Not Found ────────────────────────────────────────
void handle_not_found() {
  server.send(404, "application/json", "{\"error\":\"Endpoint tidak ditemukan\"}");
}

// ── TAMPILAN LCD ──────────────────────────────────────────────

void tampil_standby() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Siap Absensi    ");
  lcd.setCursor(0, 1);
  lcd.print("Hadap ke Kamera ");
}

void tampil_berhasil(String nama, String nim) {
  // Matikan LED merah, nyalakan LED hijau
  digitalWrite(PIN_LED_MERAH, LOW);
  digitalWrite(PIN_LED_HIJAU, HIGH);

  lcd.clear();
  lcd.setCursor(0, 0);

  // Baris 1: nama (max 16 karakter)
  String baris1 = nama;
  while (baris1.length() < 16) baris1 += " ";
  lcd.print(baris1.substring(0, 16));

  // Baris 2: NIM + centang
  lcd.setCursor(0, 1);
  String baris2 = nim + " OK";
  while (baris2.length() < 16) baris2 += " ";
  lcd.print(baris2.substring(0, 16));

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_BERHASIL;

  Serial.println("[LCD] Tampil BERHASIL: " + nama + " | " + nim);
}

void tampil_duplikat(String nama) {
  // LED merah kedip singkat
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, HIGH);

  lcd.clear();
  lcd.setCursor(0, 0);
  String baris1 = nama;
  while (baris1.length() < 16) baris1 += " ";
  lcd.print(baris1.substring(0, 16));

  lcd.setCursor(0, 1);
  lcd.print("Sudah Absen!    ");

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_DUPLIKAT;

  Serial.println("[LCD] Tampil DUPLIKAT: " + nama);
}

void tampil_gagal() {
  // LED merah menyala
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, HIGH);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Wajah Tidak     ");
  lcd.setCursor(0, 1);
  lcd.print("Dikenali!       ");

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_GAGAL;

  Serial.println("[LCD] Tampil GAGAL / tidak dikenali");
}
