import json
import logging
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt
from config_cloud import Config
from database.db import get_db

logger = logging.getLogger(__name__)
mqtt_client = None


import uuid as _uuid

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
        print(f"[MQTT] Connect failed: {e}")


def on_connect(client, userdata, flags, rc):
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
        print(f"[MQTT] Connection failed: {rc}")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"MQTT 连接意外断开，错误码: {rc}")
        print(f"[MQTT] 连接断开: {rc}")


def on_message(client, userdata, msg):
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
        print(f"[MQTT] Message processing error: {e}")


def handle_sensor_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            'INSERT INTO sensor_data (device_id, temperature, humidity, light, timestamp) VALUES (?,?,?,?,?)',
            (device_id, payload.get('temperature'), payload.get('humidity'),
             payload.get('light'), payload.get('timestamp', now))
        )
        db.execute('UPDATE devices SET last_seen=?, updated_at=? WHERE device_id=?', (now, now, device_id))
        db.commit()
        db.close()
        print(f"[SENSOR] {device_id}: T={payload.get('temperature')} H={payload.get('humidity')} L={payload.get('light')}")
    except Exception as e:
        logger.error(f"传感器数据存储失败: {e}")


def handle_status_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            'UPDATE devices SET status=?, ip_address=?, wifi_rssi=?, last_seen=?, updated_at=? WHERE device_id=?',
            (payload.get('status', 'unknown'), payload.get('ip', ''), payload.get('wifi_rssi', 0), now, now, device_id)
        )
        db.commit()
        db.close()
        print(f"[STATUS] {device_id}: {payload.get('status')}")
    except Exception as e:
        logger.error(f"设备状态更新失败: {e}")


def publish_control(device_id, relay_id, action):
    global mqtt_client

    if mqtt_client is None:
        logger.error("MQTT 客户端未初始化")
        return False

    topic = f"iot/device/{device_id}/control/{relay_id}"
    payload = json.dumps({
        "command": action,
        "request_id": f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    result = mqtt_client.publish(topic, payload, qos=1)
    return result.rc == mqtt.MQTT_ERR_SUCCESS