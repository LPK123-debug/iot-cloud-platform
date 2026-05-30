import shutil, os

base = r"C:\iot-cloud-platform"

# 把 web 文件复制到 server/static
src = os.path.join(base, "web")
dst = os.path.join(base, "server", "static")
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(src, dst)
print("web -> server/static copied")

# 确认 index.html 存在
index = os.path.join(dst, "index.html")
if os.path.exists(index):
    print(f"index.html exists: {index}")
else:
    print("ERROR: index.html not found!")

# 列出 static 内容
for f in os.listdir(dst):
    print(f"  {f}")