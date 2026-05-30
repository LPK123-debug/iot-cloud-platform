import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = 'iot-cloud-secret-2024'
    DEBUG = True
    MQTT_BROKER_HOST = '127.0.0.1'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = 'admin'
    MQTT_PASSWORD = 'iot@2024'
    MQTT_KEEPALIVE = 60
    MQTT_CLIENT_ID = 'iot_server'
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'iot_platform.db')
    SENSOR_REPORT_INTERVAL = 10
    CONTROL_TIMEOUT = 5
    DATA_RETENTION_DAYS = 30
    MAX_DEVICES = 50
