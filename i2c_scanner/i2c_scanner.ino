#include <Wire.h>

void setup() {
  Wire.begin(21, 22); // SDA=GPIO21, SCL=GPIO22
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== SCANNING I2C PHYSICAL ===");

  int count = 0;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Perangkat ditemukan di alamat: 0x");
      Serial.println(addr, HEX);
      count++;
    }
  }
  if (count == 0) {
    Serial.println("TIDAK ADA PERANGKAT I2C YANG TERDETEKSI!");
  }
  Serial.println("Scan selesai.");
}

void loop() {
  // Diam saja setelah scan selesai
  delay(1000);
}
