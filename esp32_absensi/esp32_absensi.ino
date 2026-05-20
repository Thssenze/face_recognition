/*
 * ============================================================
 *  SISTEM ABSENSI FACE RECOGNITION — ESP32 RECEIVER (OLED)
 *  Hardware : ESP32 Dev Board
 *             OLED SSD1306 (128x64) I2C (SDA=GPIO21, SCL=GPIO22)
 *             LED Hijau → GPIO 26
 *             LED Merah  → GPIO 27
 *
 *  Fungsi   : Menerima HTTP POST dari Flask (laptop),
 *             menampilkan nama, NIM, & status di OLED SSD1306,
 *             menyalakan LED sesuai status absensi.
 * ============================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// ── KONFIGURASI — SESUAIKAN SEBELUM UPLOAD ───────────────────
const char* WIFI_SSID     = "BOUTY FAMILLY";   // SSID WiFi
const char* WIFI_PASSWORD = "Galang14";        // Password WiFi
// ─────────────────────────────────────────────────────────────

// ── PIN DEFINITION ────────────────────────────────────────────
#define PIN_LED_HIJAU  26
#define PIN_LED_MERAH  27

// ── OLED SSD1306 CONFIGURATION ────────────────────────────────
#define SCREEN_WIDTH   128  // Lebar layar OLED (pixel)
#define SCREEN_HEIGHT   64  // Tinggi layar OLED (pixel)
#define OLED_RESET      -1  // Share reset pin dengan ESP32
#define SCREEN_ADDRESS 0x3C // Alamat I2C OLED (biasanya 0x3C)
// ─────────────────────────────────────────────────────────────

WebServer        server(80);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Durasi nyala LED & tampilan OLED (milidetik)
const unsigned long DURASI_BERHASIL = 3000;
const unsigned long DURASI_DUPLIKAT = 2000;
const unsigned long DURASI_GAGAL    = 2000;

// Waktu kapan OLED & LED harus direset ke standby
unsigned long waktu_reset = 0;
bool          sedang_tampil = false;

// Deklarasi fungsi tampilan
void tampil_standby();
void tampil_berhasil(String nama, String nim);
void tampil_duplikat(String nama);
void tampil_gagal();

// ── SETUP ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Inisialisasi LED
  pinMode(PIN_LED_HIJAU, OUTPUT);
  pinMode(PIN_LED_MERAH, OUTPUT);
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, LOW);

  // Inisialisasi I2C & OLED
  Wire.begin(21, 22);   // SDA=GPIO21, SCL=GPIO22
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("[ERROR] Alokasi SSD1306 gagal! Cek alamat I2C atau wiring."));
  } else {
    Serial.println(F("[OK] OLED SSD1306 Berhasil diinisialisasi"));
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    
    // Tampilan awal menghubungkan WiFi
    display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
    display.setCursor(8, 12);
    display.println("SISTEM ABSENSI");
    display.setCursor(8, 28);
    display.println("Menghubungkan...");
    display.setCursor(8, 44);
    display.print("SSID: ");
    display.print(WIFI_SSID);
    display.display();
  }

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

    display.clearDisplay();
    display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
    display.drawLine(4, 18, 123, 18, SSD1306_WHITE);
    
    display.setCursor(8, 6);
    display.print("WiFi Connected!");
    
    display.setCursor(8, 26);
    display.print("IP Address:");
    display.setCursor(8, 42);
    display.print(WiFi.localIP().toString());
    display.display();
    
    delay(3000);
    tampil_standby();
  } else {
    Serial.println("\n[ERROR] Gagal terhubung ke WiFi!");
    display.clearDisplay();
    display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
    display.setCursor(8, 12);
    display.println("Koneksi WiFi Gagal!");
    display.setCursor(8, 28);
    display.println("Cek SSID/Password");
    display.display();
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

  // Reset OLED & LED ke standby setelah durasi habis
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

  // Parse JSON (Kompatibel dengan ArduinoJson v7)
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, body);
  if (err) {
    Serial.println("[ERROR] JSON tidak valid: " + String(err.c_str()));
    server.send(400, "application/json", "{\"error\":\"JSON tidak valid\"}");
    return;
  }

  String nama   = doc["nama"]   | "Unknown";
  String nim    = doc["nim"]    | "--------";
  String status = doc["status"] | "gagal";

  Serial.println("[INFO] Nama   : " + nama);
  Serial.println("[INFO] NIM    : " + nim);
  Serial.println("[INFO] Status : " + status);

  // Tampilkan di OLED & nyalakan LED
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
  html += "<p>OLED: SSD1306 Active</p>";
  html += "<p>Endpoint: POST /absensi</p>";
  server.send(200, "text/html", html);
}

// ── HANDLER: Not Found ────────────────────────────────────────
void handle_not_found() {
  server.send(404, "application/json", "{\"error\":\"Endpoint tidak ditemukan\"}");
}

// ── TAMPILAN OLED SSD1306 ─────────────────────────────────────

void tampil_standby() {
  display.clearDisplay();
  
  // Gambar border tipis luar
  display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
  display.drawLine(4, 20, 123, 20, SSD1306_WHITE);
  
  // Header
  display.setTextSize(1);
  display.setCursor(20, 6);
  display.print("SISTEM ABSENSI");
  
  // Instruksi
  display.setCursor(18, 28);
  display.print("HADAP KE KAMERA");
  
  // Status Standby
  display.setCursor(35, 46);
  display.print("[ READY ]");
  
  display.display();
}

void tampil_berhasil(String nama, String nim) {
  // Matikan LED merah, nyalakan LED hijau
  digitalWrite(PIN_LED_MERAH, LOW);
  digitalWrite(PIN_LED_HIJAU, HIGH);

  display.clearDisplay();
  
  // Border
  display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
  display.drawLine(4, 18, 123, 18, SSD1306_WHITE);

  // Header status
  display.setTextSize(1);
  display.setCursor(16, 6);
  display.print("ABSENSI BERHASIL");

  // Nama (potong jika terlalu panjang, max 18 karakter untuk muat di 1 baris)
  if (nama.length() > 18) nama = nama.substring(0, 18);
  display.setCursor(8, 24);
  display.print(nama);

  // NIM
  if (nim.length() > 18) nim = nim.substring(0, 18);
  display.setCursor(8, 36);
  display.print(nim);

  // Status Kehadiran
  display.setCursor(8, 48);
  display.print("Status: HADIR OK");

  display.display();

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_BERHASIL;

  Serial.println("[OLED] Tampil BERHASIL: " + nama + " | " + nim);
}

void tampil_duplikat(String nama) {
  // Nyalakan LED merah
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, HIGH);

  display.clearDisplay();
  
  // Border
  display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
  display.drawLine(4, 18, 123, 18, SSD1306_WHITE);

  // Header status
  display.setTextSize(1);
  display.setCursor(20, 6);
  display.print("SUDAH ABSENSI");

  // Nama
  if (nama.length() > 18) nama = nama.substring(0, 18);
  display.setCursor(8, 24);
  display.print(nama);

  // Pesan peringatan
  display.setCursor(8, 38);
  display.print("Anda sudah terdata");
  display.setCursor(8, 48);
  display.print("hari ini!");

  display.display();

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_DUPLIKAT;

  Serial.println("[OLED] Tampil DUPLIKAT: " + nama);
}

void tampil_gagal() {
  // Nyalakan LED merah
  digitalWrite(PIN_LED_HIJAU, LOW);
  digitalWrite(PIN_LED_MERAH, HIGH);

  display.clearDisplay();
  
  // Border
  display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
  display.drawLine(4, 18, 123, 18, SSD1306_WHITE);

  // Header status
  display.setTextSize(1);
  display.setCursor(20, 6);
  display.print("ABSENSI GAGAL");

  // Pesan peringatan
  display.setCursor(14, 28);
  display.print("Wajah Tidak");
  display.setCursor(14, 40);
  display.print("Dikenali!");

  display.display();

  sedang_tampil = true;
  waktu_reset   = millis() + DURASI_GAGAL;

  Serial.println("[OLED] Tampil GAGAL / tidak dikenali");
}
