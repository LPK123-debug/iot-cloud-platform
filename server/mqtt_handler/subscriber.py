import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from config import Config
from database.db import get_db

logger = logging.getLogger(__name__)

# 全局 MQTT 客户端实例
mqtt_client = None


def connect_mqtt():
    """连接 MQTT Broker 并订阅设备主题"""
    global mqtt_client

    mqtt_client = mqtt.Client(
        client_id=Config.MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311
    )
    mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

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
        print("[MQTT] 连接成功，已订阅设备主题")
    except Exception as e:
        logger.error(f"MQTT 连接失败: {e}")
        print(f"[MQTT] 连接失败: {e}")


def on_connect(client, userdata, flags, rc):
    """连接成功回调"""
    if rc == 0:
        logger.info("MQTT Broker 连接成功")
        # 订阅所有设备的传感器数据和状态
        client.subscribe("iot/device/+/sensor/all", qos=1)
        client.subscribe("iot/device/+/status", qos=1)
        logger.info("已订阅: iot/device/+/sensor/all, iot/device/+/status")
    else:
        logger.error(f"MQTT 连接失败，错误码: {rc}")


def on_disconnect(client, userdata, rc):
    """断开连接回调"""
    logger.warning(f"MQTT 连接断开，错误码: {rc}")


def on_message(client, userdata, msg):
    """收到消息回调"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))

        # 解析主题: iot/device/{device_id}/sensor/all 或 iot/device/{device_id}/status
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
        logger.error(f"消息处理失败: {e}")


def handle_sensor_data(device_id, payload):
    """处理传感器数据，存入数据库"""
    try:
        db = get_db()
        cursor = db.cursor()

        temperature = payload.get('temperature')
        humidity = payload.get('humidity')
        light = payload.get('light')
        timestamp = payload.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        cursor.execute(
            'INSERT INTO sensor_data (device_id, temperature, humidity, light, timestamp) VALUES (?,?,?,?,?)',
            (device_id, temperature, humidity, light, timestamp)
        )

        # 更新设备最后在线时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            'UPDATE devices SET last_seen=?, updated_at=? WHERE device_id=?',
            (timestamp, now, device_id)
        )

        db.commit()
        db.close()
        logger.info(f"[传感器] {device_id}: 温度={temperature}°C 湿度={humidity}% 光照={light}lux")

    except Exception as e:
        logger.error(f"传感器数据存储失败: {e}")


def handle_status_data(device_id, payload):
    """处理设备状态消息"""
    try:
        status = payload.get('status', 'unknown')
        ip = payload.get('ip', '')
        rssi = payload.get('wifi_rssi', 0)
        relay1 = payload.get('relay1', '')
        relay2 = payload.get('relay2', '')

        db = get_db()
        cursor = db.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 只更新 relay 状态（如果设备回报了的话）
        update_fields = [
            'status=?', 'ip_address=?', 'wifi_rssi=?',
            'last_seen=?', 'updated_at=?'
        ]
        update_values = [status, ip, rssi, now, now]

        if relay1:
            update_fields.append('relay1_state=?')
            update_values.append(relay1)
        if relay2:
            update_fields.append('relay2_state=?')
            update_values.append(relay2)

        update_values.append(device_id)
        sql = f"UPDATE devices SET {','.join(update_fields)} WHERE device_id=?"
        cursor.execute(sql, update_values)

        db.commit()
        db.close()
        logger.info(f"[状态] {device_id}: {status}")

    except Exception as e:
        logger.error(f"设备状态更新失败: {e}")


def publish_control(device_id, relay_id, action):
    """发布控制命令到设备"""
    global mqtt_client

    if mqtt_client is None:
        logger.error("MQTT 客户端未初始化")
        return False

    topic = f"iot/device/{device_id}/control/{relay_id}"
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{device_id}"
    payload = json.dumps({
        "command": action,
        "request_id": request_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    try:
        result = mqtt_client.publish(topic, payload, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"[控制] 发送: {device_id}/{relay_id} -> {action}")
            return True
        else:
            logger.error(f"[控制] 发送失败: {result.rc}")
            return False
    except Exception as e:
        logger.error(f"[控制] 异常: {e}")
        return False
