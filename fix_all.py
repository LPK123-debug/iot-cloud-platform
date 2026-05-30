import os, shutil

base = r"C:\iot-cloud-platform\server"

# Step 1: Copy config_cloud.py to config.py
shutil.copy(os.path.join(base, "config_cloud.py"), os.path.join(base, "config.py"))
print("[1] config_cloud.py -> config.py (done)")

# Step 2: Rewrite subscriber_cloud.py with fixed code
sub_content = '''import json
import logging
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt
from config import Config
from database.db import get_db

logger = logging.getLogger(__name__)
mqtt_client = None


def connect_mqtt():
    global mqtt_client
    import uuid
    unique_id = Config.MQTT_CLIENT_ID + "_" + uuid.uuid4().hex[:6]
    print(f"[MQTT] Client ID: {unique_id}")

    mqtt_client = mqtt.Client(client_id=unique_id, protocol=mqtt.MQTTv311)
    mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

    if Config.MQTT_USE_TLS:
        mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        mqtt_client.tls_insecure_set(False)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    try:
        print(f"[MQTT] Connecting to {Config.MQTT_BROKER_HOST}:{Config.MQTT_BROKER_PORT}")
        mqtt_client.connect(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"[MQTT] Connect error: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] *** CONNECTED SUCCESSFULLY ***")
        (r1, m1) = client.subscribe("iot/device/+/sensor/all", qos=1)
        (r2, m2) = client.subscribe("iot/device/+/status", qos=1)
        print(f"[MQTT] Subscribe: sensor={r1} mid={m1}, status={r2} mid={m2}")
    else:
        print(f"[MQTT] Connect FAILED rc={rc}")


def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Disconnected rc={rc}")


def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode("utf-8")
        print(f"[MQTT] >>> {topic}: {payload_str[:200]}")

        payload = json.loads(payload_str)
        parts = topic.split("/")
        if len(parts) >= 4:
            device_id = parts[2]
            msg_type = parts[3]
            if msg_type == "sensor" and len(parts) >= 5 and parts[4] == "all":
                handle_sensor_data(device_id, payload)
            elif msg_type == "status":
                handle_status_data(device_id, payload)
    except Exception as e:
        print(f"[MQTT] Message error: {e}")


def handle_sensor_data(device_id, payload):
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
        print(f"[DB] Error: {e}")


def handle_status_data(device_id, payload):
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
        print(f"[DB] Error: {e}")


def publish_control(device_id, relay_id, action):
    global mqtt_client
    if mqtt_client is None:
        return False
    topic = f"iot/device/{device_id}/control/{relay_id}"
    payload = json.dumps({
        "command": action,
        "request_id": f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    result = mqtt_client.publish(topic, payload, qos=1)
    return result.rc == mqtt.MQTT_ERR_SUCCESS
'''
with open(os.path.join(base, "mqtt_handler", "subscriber_cloud.py"), "w", encoding="utf-8") as f:
    f.write(sub_content)
print("[2] subscriber_cloud.py rewritten (done)")

# Step 3: Copy to subscriber.py so db.py and control_routes.py get correct imports
shutil.copy(os.path.join(base, "mqtt_handler", "subscriber_cloud.py"), os.path.join(base, "mqtt_handler", "subscriber.py"))
print("[3] subscriber_cloud.py -> subscriber.py (done)")

# Step 4: Also copy config_cloud.py to config.py (already done in step 1)
print("[4] All imports now point to cloud versions")

# Verify
print("\n--- Verification ---")
with open(os.path.join(base, "config.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"config.py has HiveMQ host: {'8122586c2ede' in c}")

with open(os.path.join(base, "mqtt_handler", "subscriber.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"subscriber.py has CONNECTED SUCCESSFULLY: {'CONNECTED SUCCESSFULLY' in c}")

with open(os.path.join(base, "mqtt_handler", "subscriber_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"subscriber_cloud.py has CONNECTED SUCCESSFULLY: {'CONNECTED SUCCESSFULLY' in c}")

with open(os.path.join(base, "database", "db.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"db.py imports config: {'from config import' in c}")

print("\nAll fixed!")