import os
base = r"C:\iot-cloud-platform\server"

print("=== File Check ===")

# 1. Check app_cloud.py has debug endpoints
with open(os.path.join(base, "app_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"app_cloud.py size: {len(c)} bytes")
    print(f"  has debug/mqtt: {'debug/mqtt' in c}")
    print(f"  has debug/db: {'debug/db' in c}")
    print(f"  has config_cloud: {'config_cloud' in c}")
    print(f"  has subscriber_cloud: {'subscriber_cloud' in c}")

# 2. Check subscriber_cloud.py has auto-register
with open(os.path.join(base, "mqtt_handler", "subscriber_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\nsubscriber_cloud.py size: {len(c)} bytes")
    print(f"  has auto-register: {'Auto-registered' in c}")
    print(f"  has CONNECTED SUCCESSFULLY: {'CONNECTED SUCCESSFULLY' in c}")
    print(f"  has handle_status_data: {'handle_status_data' in c}")

# 3. Check subscriber.py matches
with open(os.path.join(base, "mqtt_handler", "subscriber.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\nsubscriber.py size: {len(c)} bytes")
    print(f"  has auto-register: {'Auto-registered' in c}")
    print(f"  matches subscriber_cloud: {c == open(os.path.join(base, 'mqtt_handler', 'subscriber_cloud.py'), 'r', encoding='utf-8').read()}")

# 4. Check config.py
with open(os.path.join(base, "config.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\nconfig.py has HiveMQ: {'8122586c2ede' in c}")
    print(f"  has USE_TLS: {'MQTT_USE_TLS' in c}")

# 5. Check config_cloud.py
with open(os.path.join(base, "config_cloud.py"), "r", encoding="utf-8") as f:
    c = f.read()
    print(f"\nconfig_cloud.py has HiveMQ: {'8122586c2ede' in c}")
    print(f"  has USE_TLS: {'MQTT_USE_TLS' in c}")