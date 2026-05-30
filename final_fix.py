import os, shutil

base = r"C:\iot-cloud-platform\server"

# Step 1: Copy subscriber.py to subscriber_cloud.py
shutil.copy(
    os.path.join(base, "mqtt_handler", "subscriber.py"),
    os.path.join(base, "mqtt_handler", "subscriber_cloud.py")
)
print("[1] subscriber.py -> subscriber_cloud.py (done)")

# Step 2: Add debug endpoints to app_cloud.py
with open(os.path.join(base, "app_cloud.py"), "r", encoding="utf-8") as f:
    content = f.read()

if "debug/mqtt" not in content:
    old = "    return app"
    new = '''    @app.route("/api/debug/mqtt")
    def debug_mqtt():
        from mqtt_handler import subscriber_cloud as sub
        st = "connected" if sub.mqtt_client and sub.mqtt_client.is_connected() else "disconnected"
        return {"mqtt_status": st, "client_exists": sub.mqtt_client is not None}

    @app.route("/api/debug/db")
    def debug_db():
        from database.db import get_db
        db = get_db()
        devices = db.execute("SELECT * FROM devices").fetchall()
        sensors = db.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5").fetchall()
        db.close()
        return {"devices": [dict(d) for d in devices], "latest_sensors": [dict(s) for s in sensors]}

    return app'''
    content = content.replace(old, new)
    with open(os.path.join(base, "app_cloud.py"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[2] Debug endpoints added to app_cloud.py")
else:
    print("[2] Debug endpoints already exist")

# Step 3: Verify
with open(os.path.join(base, "mqtt_handler", "subscriber_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\n[Verify] subscriber_cloud.py:")
    print(f"  has auto-register: {'Auto-registered' in c}")
    print(f"  has CONNECTED SUCCESSFULLY: {'CONNECTED SUCCESSFULLY' in c}")
    print(f"  size: {len(c)} bytes")

with open(os.path.join(base, "app_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\n[Verify] app_cloud.py:")
    print(f"  has debug/mqtt: {'debug/mqtt' in c}")
    print(f"  has debug/db: {'debug/db' in c}")
    print(f"  size: {len(c)} bytes")

print("\nAll fixed!")