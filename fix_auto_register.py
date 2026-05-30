import os

filepath = r"C:\iot-cloud-platform\server\mqtt_handler\subscriber.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_status = '''def handle_status_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE devices SET status=?, ip_address=?, wifi_rssi=?, last_seen=?, updated_at=? WHERE device_id=?",
            (payload.get("status", "unknown"), payload.get("ip", ""),
             payload.get("wifi_rssi", 0), now, now, device_id)
        )
        db.commit()
        db.close()
        print(f"[DB] Status: {device_id} -> {payload.get('status')}")
    except Exception as e:
        print(f"[DB] Error: {e}")'''

new_status = '''def handle_status_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if device exists, auto-register if not
        existing = db.execute("SELECT 1 FROM devices WHERE device_id=?", (device_id,)).fetchone()
        if not existing:
            db.execute(
                "INSERT INTO devices (device_id, name, description, device_type) VALUES (?,?,?,?)",
                (device_id, f"Device {device_id}", "Auto-registered", "both")
            )
            print(f"[DB] Auto-registered device: {device_id}")

        # Build update with relay states if present
        relay1 = payload.get("relay1", "")
        relay2 = payload.get("relay2", "")

        db.execute(
            "UPDATE devices SET status=?, ip_address=?, wifi_rssi=?, last_seen=?, updated_at=?, relay1_state=?, relay2_state=? WHERE device_id=?",
            (payload.get("status", "unknown"), payload.get("ip", ""),
             payload.get("wifi_rssi", 0), now, now,
             relay1 if relay1 else "off", relay2 if relay2 else "off",
             device_id)
        )
        db.commit()
        db.close()
        print(f"[DB] Status: {device_id} -> {payload.get('status')}")
    except Exception as e:
        print(f"[DB] Error: {e}")'''

content = content.replace(old_status, new_status)

# Also fix handle_sensor_data to auto-register
old_sensor = '''def handle_sensor_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO sensor_data (device_id, temperature, humidity, light, timestamp) VALUES (?,?,?,?,?)",
            (device_id, payload.get("temperature"), payload.get("humidity"),
             payload.get("light"), payload.get("timestamp", now))
        )
        db.execute("UPDATE devices SET last_seen=?, updated_at=? WHERE device_id=?", (now, now, device_id))
        db.commit()
        db.close()
        print(f"[DB] Stored: {device_id} T={payload.get('temperature')} H={payload.get('humidity')} L={payload.get('light')}")
    except Exception as e:
        print(f"[DB] Error: {e}")'''

new_sensor = '''def handle_sensor_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Auto-register device if not exists
        existing = db.execute("SELECT 1 FROM devices WHERE device_id=?", (device_id,)).fetchone()
        if not existing:
            db.execute(
                "INSERT INTO devices (device_id, name, description, device_type) VALUES (?,?,?,?)",
                (device_id, f"Device {device_id}", "Auto-registered", "both")
            )
            print(f"[DB] Auto-registered device: {device_id}")

        db.execute(
            "INSERT INTO sensor_data (device_id, temperature, humidity, light, timestamp) VALUES (?,?,?,?,?)",
            (device_id, payload.get("temperature"), payload.get("humidity"),
             payload.get("light"), payload.get("timestamp", now))
        )
        db.execute("UPDATE devices SET status=?, last_seen=?, updated_at=? WHERE device_id=?", ("online", now, now, device_id))
        db.commit()
        db.close()
        print(f"[DB] Stored: {device_id} T={payload.get('temperature')} H={payload.get('humidity')} L={payload.get('light')}")
    except Exception as e:
        print(f"[DB] Error: {e}")'''

content = content.replace(old_sensor, new_sensor)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Also update subscriber_cloud.py
shutil.copy = __import__("shutil").copy
shutil.copy(filepath, filepath.replace("subscriber.py", "subscriber_cloud.py"))

print("Fixed: auto-register devices on first message")