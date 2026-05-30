import os

filepath = r"C:\iot-cloud-platform\firmware\iot-esp8266\include\config.h"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('LPK', 'test123')
content = content.replace('12345678', 'test1234')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("WiFi changed to: test123 / test1234")