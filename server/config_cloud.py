import os


class Config:
    # 项目根目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Flask 配置
    SECRET_KEY = os.environ.get("SECRET_KEY", "iot-cloud-secret-2024")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

    # MQTT 配置 - HiveMQ Cloud
    MQTT_BROKER_HOST = os.environ.get("MQTT_HOST", "8122586c2ede44a59b3b71c4455cb5f2.s1.eu.hivemq.cloud")
    MQTT_BROKER_PORT = int(os.environ.get("MQTT_PORT", "8883"))
    MQTT_USERNAME = os.environ.get("MQTT_USER", "iotadmin")
    MQTT_PASSWORD = os.environ.get("MQTT_PASS", "Li2223841219")
    MQTT_KEEPALIVE = 60
    MQTT_CLIENT_ID = "iot_server_cloud"
    MQTT_USE_TLS = True  # 启用 TLS 加密连接

    # 数据库路径（Render 可能重启，使用临时目录）
    DATABASE_PATH = os.path.join(BASE_DIR, "data", "iot_platform.db")

    # 业务配置
    SENSOR_REPORT_INTERVAL = 10
    CONTROL_TIMEOUT = 5
    DATA_RETENTION_DAYS = 30
    MAX_DEVICES = 50