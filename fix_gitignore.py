import os

filepath = r"C:\iot-cloud-platform\.gitignore"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 去掉 server/static/ 的忽略规则
    if "server/static" in line or "static/" in line:
        continue
    new_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(".gitignore fixed - server/static/ no longer ignored")