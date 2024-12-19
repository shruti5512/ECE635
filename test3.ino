#include <WiFi.h>
#include <time.h>
#include "BluetoothSerial.h"

// WiFi credentials
const char* ssid = "1L_Brandywine";
const char* password = "Xfinity@1L";

// NTP server configuration
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;
const int daylightOffset_sec = 0;

// Bluetooth configuration
BluetoothSerial BT;
const char* btDeviceName = "ESP32_2";  // For second ESP32, change accordingly

// Pin configuration for LM393 sound sensor
const int soundSensorPin = 34;  // LM393 connected to pin 34

void setup() {
  Serial.begin(115200);
  BT.begin(btDeviceName);
  Serial.println("Bluetooth started. Waiting for connection...");

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Configure NTP and synchronize time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  delay(2000);  // Allow time for synchronization

  // Verify NTP synchronization
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time from NTP");
    return;
  }
  Serial.println("NTP time synchronized");

  // Configure the sound sensor pin as input
  pinMode(soundSensorPin, INPUT);
}

void sendTimestamp() {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  String timestamp = String(tv.tv_sec) + "." + String(tv.tv_usec);
  String message = "t1: " + timestamp;
  Serial.println("Sending: " + message);
  BT.println(message);
}

void loop() {
  // Check the sound sensor for a LOW signal indicating sound detection
  if (digitalRead(soundSensorPin) == LOW) {
    sendTimestamp();
      // Small delay to prevent multiple rapid sends for a single sound event
  }
  delay(500);
}
