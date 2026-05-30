import os

filepath = r"C:\iot-cloud-platform\server\mqtt_handler\subscriber_cloud.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 修复：使用唯一 Client ID + 添加重连延迟
old_connect_func = '''def connect_mqtt():
    global mqtt_client

    mqtt_client = mqtt.Client(
        client_id=Config.MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311
    )

    # 设置用户名密码
    mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

    # 如果使用 TLS（HiveMQ Cloud 需要）
    if Config.MQTT_USE_TLS:
        mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        mqtt_client.tls_insecure_set(False)

    # 注册回调
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    try:
        mqtt_client.connect(
            Config.MQTT_BROKER_HOST,
            Config.MQTT_BROKER_PORT,
            Config.MQTT_KEEPALIVE
        )
        mqtt_client.loop_start()
        print(f"[MQTT] Connecting to {Config.MQTT_BROKER_HOST}:{Config.MQTT_BROKER_PORT}...")
    except Exception as e:
        logger.error(f"MQTT 连接失败: {e}")
        print(f"[MQTT] 连接失败: {e}")'''

new_connect_func = '''import uuid as _uuid

def connect_mqtt():
    global mqtt_client

    # Use unique client ID to avoid conflicts
    unique_id = Config.MQTT_CLIENT_ID + "_" + _uuid.uuid4().hex[:6]
    print(f"[MQTT] Client ID: {unique_id}")

    mqtt_client = mqtt.Client(
        client_id=unique_id,
        protocol=mqtt.MQTTv311
    )

    # Set username and password
    mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

    # Set TLS for HiveMQ Cloud
    if Config.MQTT_USE_TLS:
        mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        mqtt_client.tls_insecure_set(False)

    # Set reconnect delay
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)

    # Register callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    try:
        print(f"[MQTT] Connecting to {Config.MQTT_BROKER_HOST}:{Config.MQTT_BROKER_PORT}...")
        mqtt_client.connect(
            Config.MQTT_BROKER_HOST,
            Config.MQTT_BROKER_PORT,
            Config.MQTT_KEEPALIVE
        )
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"MQTT connect error: {e}")
        print(f"[MQTT] Connect failed: {e}")'''

content = content.replace(old_connect_func, new_connect_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed: unique client ID + reconnect delay")