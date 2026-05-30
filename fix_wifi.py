import os

filepath = r"C:\iot-cloud-platform\firmware\iot-esp8266\include\config.h"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('YOUR_WIFI_NAME', 'LPK')
content = content.replace('YOUR_WIFI_PASSWORD', '12345678')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("WiFi config updated!")
print("SSID: LPK")
print("Password: 12345678")