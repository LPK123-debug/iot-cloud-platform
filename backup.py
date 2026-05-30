import zipfile
import os

project = r"C:\iot-cloud-platform"
backup_file = r"C:\iot-cloud-platform\iot-platform-backup.zip"

files_to_backup = []
for root, dirs, filenames in os.walk(project):
    skip = False
    for excl in ["venv", ".pio", "mosquitto", "__pycache__", "static", ".git"]:
        if excl in root:
            skip = True
            break
    if skip:
        continue
    for f in filenames:
        if f.endswith((".pyc", ".pyo", ".zip")):
            continue
        full = os.path.join(root, f)
        arcname = os.path.relpath(full, project)
        files_to_backup.append((full, arcname))

with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
    for full, arcname in files_to_backup:
        zf.write(full, arcname)
        print(f"  added: {arcname}")

print(f"\nBackup saved: {backup_file}")
print(f"Total files: {len(files_to_backup)}")