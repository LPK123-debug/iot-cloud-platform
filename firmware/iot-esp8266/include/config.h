#ifndef CONFIG_H
#define CONFIG_H

// ===== WiFi Configuration =====
#define WIFI_SSID       "test123"
#define WIFI_PASSWORD   "test1234"

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
