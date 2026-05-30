import os

filepath = r"C:\iot-cloud-platform\render.yaml"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "81225862ede44a59b3b71c4455cb5f2",
    "8122586c2ede44a59b3b71c4455cb5f2"
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("render.yaml fixed!")