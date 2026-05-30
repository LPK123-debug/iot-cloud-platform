import os

filepath = r"C:\iot-cloud-platform\server\config_cloud.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 修复错误的 MQTT 地址
content = content.replace(
    "81225862ede44a59b3b71c4455cb5f2",
    "8122586c2ede44a59b3b71c4455cb5f2"
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("MQTT host fixed!")
print("Correct host: 8122586c2ede44a59b3b71c4455cb5f2.s1.eu.hivemq.cloud")