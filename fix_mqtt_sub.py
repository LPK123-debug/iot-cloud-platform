import os

filepath = r"C:\iot-cloud-platform\server\mqtt_handler\subscriber_cloud.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 修复 on_connect 回调，确保订阅成功
old_connect = '''def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT Broker 连接成功")
        client.subscribe("iot/device/+/sensor/all", qos=1)
        client.subscribe("iot/device/+/status", qos=1)
        print("[MQTT] 已连接并订阅设备主题")
    else:
        logger.error(f"MQTT 连接失败，错误码: {rc}")
        print(f"[MQTT] 连接失败，错误码: {rc}")'''

new_connect = '''def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT Broker 连接成功")
        print("[MQTT] Connected to HiveMQ Cloud!")

        # Subscribe with explicit QoS
        result1 = client.subscribe("iot/device/+/sensor/all", qos=1)
        result2 = client.subscribe("iot/device/+/status", qos=1)

        if result1[0] == 0 and result2[0] == 0:
            print("[MQTT] Subscribed to: iot/device/+/sensor/all")
            print("[MQTT] Subscribed to: iot/device/+/status")
            print("[MQTT] Waiting for device data...")
        else:
            print(f"[MQTT] Subscribe failed: {result1}, {result2}")
    else:
        logger.error(f"MQTT 连接失败，错误码: {rc}")
        print(f"[MQTT] Connection failed: {rc}")'''

content = content.replace(old_connect, new_connect)

# 添加更详细的日志到 on_message
old_message = '''def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))

        parts = topic.split('/')
        if len(parts) >= 4:
            device_id = parts[2]
            msg_type = parts[3]

            if msg_type == 'sensor' and len(parts) >= 5 and parts[4] == 'all':
                handle_sensor_data(device_id, payload)
            elif msg_type == 'status':
                handle_status_data(device_id, payload)

    except json.JSONDecodeError:
        logger.error(f"JSON 解析失败: {msg.payload}")
    except Exception as e:
        logger.error(f"消息处理失败: {e}")'''

new_message = '''def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8')
        print(f"[MQTT] Message received on: {topic}")
        print(f"[MQTT] Payload: {payload_str[:100]}...")

        payload = json.loads(payload_str)

        parts = topic.split('/')
        if len(parts) >= 4:
            device_id = parts[2]
            msg_type = parts[3]

            if msg_type == 'sensor' and len(parts) >= 5 and parts[4] == 'all':
                handle_sensor_data(device_id, payload)
            elif msg_type == 'status':
                handle_status_data(device_id, payload)

    except json.JSONDecodeError as e:
        print(f"[MQTT] JSON parse error: {e}")
        print(f"[MQTT] Raw payload: {msg.payload}")
    except Exception as e:
        print(f"[MQTT] Message processing error: {e}")'''

content = content.replace(old_message, new_message)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("subscriber_cloud.py updated with better logging")