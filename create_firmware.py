import os

base = r"C:\iot-cloud-platform\firmware\iot-esp8266"
os.makedirs(os.path.join(base, "src"), exist_ok=True)
os.makedirs(os.path.join(base, "include"), exist_ok=True)

files = {}

files["platformio.ini"] = """; PlatformIO Configuration
; IoT ESP8266 Device

[env:nodemcuv2]
platform = espressif8266
board = nodemcuv2
framework = arduino
monitor_speed = 115200
upload_speed = 115200

; Required libraries
lib_deps =
    knolleary/PubSubClient@^2.8
    bblanchon/ArduinoJson@^6.21.0
    adafruit/DHT sensor library@^1.4.0
    adafruit/Adafruit Unified Sensor@^1.1.0
    claws/BH1750@^1.3.0
"""

files["include/config.h"] = r"""#ifndef CONFIG_H
#define CONFIG_H

// ===== WiFi Configuration =====
#define WIFI_SSID       "YOUR_WIFI_NAME"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD"

// ===== MQTT Configuration (HiveMQ Cloud) =====
#define MQTT_HOST       "8122586c2ede44a59b3b71c4455cb5f2.s1.eu.hivemq.cloud"
#define MQTT_PORT       8883
#define MQTT_USER       "iotadmin"
#define MQTT_PASS       "Li2223841219"

// ===== Device Configuration =====
#define DEVICE_ID       "dev001"
#define REPORT_INTERVAL 10000   // Data report interval (ms)

// ===== Pin Definitions =====
#define PIN_DHT         4       // D2 = GPIO4
#define PIN_RELAY1      14      // D5 = GPIO14
#define PIN_RELAY2      12      // D6 = GPIO12
#define PIN_LED         2       // D4 = GPIO2 (built-in LED)

// ===== MQTT Topics =====
#define TOPIC_SENSOR    "iot/device/" DEVICE_ID "/sensor/all"
#define TOPIC_STATUS    "iot/device/" DEVICE_ID "/status"
#define TOPIC_RELAY1    "iot/device/" DEVICE_ID "/control/relay1"
#define TOPIC_RELAY2    "iot/device/" DEVICE_ID "/control/relay2"

#endif
"""

files["src/main.cpp"] = r"""#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <BH1750.h>
#include <Wire.h>
#include "config.h"

// ===== Global Objects =====
WiFiClientSecure espClient;
PubSubClient mqtt(espClient);
DHT dht(PIN_DHT, DHT22);
BH1750 lightSensor;

// ===== State Variables =====
unsigned long lastReport = 0;
bool relay1State = false;
bool relay2State = false;

// ===== Function Declarations =====
void setupWiFi();
void connectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void reportSensorData();
void reportStatus();
void setRelay(int pin, bool state, const char* relayName);
void blinkLED(int times, int delayMs);

// ===== WiFi Setup =====
void setupWiFi() {
    Serial.printf("\n[WiFi] Connecting to %s", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] Connected! IP: %s", WiFi.localIP().toString().c_str());
        Serial.printf("[WiFi] RSSI: %d dBm\n", WiFi.RSSI());
        blinkLED(3, 200);
    } else {
        Serial.println("\n[WiFi] Connection failed! Restarting...");
        ESP.restart();
    }
}

// ===== MQTT Callback =====
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Parse message
    char message[256];
    memcpy(message, payload, length);
    message[length] = '\0';

    Serial.printf("[MQTT] Received: %s -> %s\n", topic, message);

    // Parse JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
        Serial.printf("[MQTT] JSON parse error: %s\n", error.c_str());
        return;
    }

    const char* command = doc["command"];
    if (command == nullptr) return;

    // Handle relay commands
    if (strcmp(topic, TOPIC_RELAY1) == 0) {
        if (strcmp(command, "on") == 0) setRelay(PIN_RELAY1, true, "relay1");
        else if (strcmp(command, "off") == 0) setRelay(PIN_RELAY1, false, "relay1");
        else if (strcmp(command, "toggle") == 0) setRelay(PIN_RELAY1, !relay1State, "relay1");
    }
    else if (strcmp(topic, TOPIC_RELAY2) == 0) {
        if (strcmp(command, "on") == 0) setRelay(PIN_RELAY2, true, "relay2");
        else if (strcmp(command, "off") == 0) setRelay(PIN_RELAY2, false, "relay2");
        else if (strcmp(command, "toggle") == 0) setRelay(PIN_RELAY2, !relay2State, "relay2");
    }
}

// ===== MQTT Connection =====
void connectMQTT() {
    if (mqtt.connected()) return;

    Serial.printf("[MQTT] Connecting to %s:%d...\n", MQTT_HOST, MQTT_PORT);

    // Set TLS (skip certificate verification for testing)
    espClient.setInsecure();

    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    mqtt.setBufferSize(512);

    // Set Last Will and Testament
    String willTopic = String("iot/device/") + DEVICE_ID + "/status";
    String willMessage = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"status\":\"offline\"}";

    if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASS,
                     willTopic.c_str(), 1, true, willMessage.c_str())) {
        Serial.println("[MQTT] Connected!");

        // Subscribe to control topics
        mqtt.subscribe(TOPIC_RELAY1, 1);
        mqtt.subscribe(TOPIC_RELAY2, 1);
        Serial.println("[MQTT] Subscribed to control topics");

        // Report online status
        reportStatus();
        blinkLED(5, 100);
    } else {
        Serial.printf("[MQTT] Failed, rc=%d. Retry in 5s...\n", mqtt.state());
        delay(5000);
    }
}

// ===== Report Sensor Data =====
void reportSensorData() {
    // Read sensors
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float light = lightSensor.readLightLevel();

    // Check for sensor errors
    if (isnan(temperature)) temperature = 0.0;
    if (isnan(humidity)) humidity = 0.0;
    if (light < 0) light = 0.0;

    // Build JSON
    StaticJsonDocument<300> doc;
    doc["device_id"] = DEVICE_ID;
    doc["temperature"] = round(temperature * 10.0) / 10.0;
    doc["humidity"] = round(humidity * 10.0) / 10.0;
    doc["light"] = round(light);
    doc["uptime"] = millis() / 1000;

    char buffer[300];
    serializeJson(doc, buffer);

    // Publish
    if (mqtt.publish(TOPIC_SENSOR, buffer, false)) {
        Serial.printf("[Sensor] T=%.1f H=%.1f L=%.0f\n", temperature, humidity, light);
    } else {
        Serial.println("[Sensor] Publish failed!");
    }
}

// ===== Report Status =====
void reportStatus() {
    StaticJsonDocument<300> doc;
    doc["device_id"] = DEVICE_ID;
    doc["status"] = "online";
    doc["relay1"] = relay1State ? "on" : "off";
    doc["relay2"] = relay2State ? "on" : "off";
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["ip"] = WiFi.localIP().toString();

    char buffer[300];
    serializeJson(doc, buffer);

    mqtt.publish(TOPIC_STATUS, buffer, true);
}

// ===== Set Relay State =====
void setRelay(int pin, bool state, const char* relayName) {
    digitalWrite(pin, state ? HIGH : LOW);

    if (strcmp(relayName, "relay1") == 0) {
        relay1State = state;
    } else {
        relay2State = state;
    }

    Serial.printf("[Relay] %s -> %s\n", relayName, state ? "ON" : "OFF");
    digitalWrite(PIN_LED, state ? LOW : HIGH);  // LED indicator

    // Report new status
    reportStatus();
}

// ===== LED Blink =====
void blinkLED(int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(PIN_LED, LOW);
        delay(delayMs);
        digitalWrite(PIN_LED, HIGH);
        delay(delayMs);
    }
}

// ===== Setup =====
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n================================");
    Serial.println("  IoT ESP8266 Device");
    Serial.printf("  Device ID: %s\n", DEVICE_ID);
    Serial.println("================================");

    // Init pins
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_RELAY1, OUTPUT);
    pinMode(PIN_RELAY2, OUTPUT);
    digitalWrite(PIN_LED, HIGH);
    digitalWrite(PIN_RELAY1, LOW);
    digitalWrite(PIN_RELAY2, LOW);

    // Init I2C and BH1750
    Wire.begin(0, 2);  // SDA=GPIO0(D3), SCL=GPIO2(D4)
    lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
    Serial.println("[Sensor] BH1750 initialized");

    // Init DHT22
    dht.begin();
    Serial.println("[Sensor] DHT22 initialized");

    // Connect WiFi
    setupWiFi();

    // Connect MQTT
    connectMQTT();

    Serial.println("[System] Ready! Reporting every 10 seconds.");
    Serial.println("================================\n");
}

// ===== Main Loop =====
void loop() {
    // Maintain WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        setupWiFi();
    }

    // Maintain MQTT connection
    if (!mqtt.connected()) {
        connectMQTT();
    }
    mqtt.loop();

    // Report sensor data at interval
    unsigned long now = millis();
    if (now - lastReport >= REPORT_INTERVAL) {
        lastReport = now;
        reportSensorData();
    }
}
"""

for fp, ct in files.items():
    full = os.path.join(base, fp)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(ct.lstrip("\n"))
    print(f"  created: {fp}")

print("\nFirmware files created!")
print(f"\nProject location: {base}")