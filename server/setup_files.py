import os

files = {}

files['requirements.txt'] = '''Flask==3.0.0
paho-mqtt==1.6.1
flask-cors==4.0.0
'''

files['database/__init__.py'] = ''

files['database/db.py'] = '''import sqlite3
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
'''

files['database/init_db.py'] = '''import os
from config import Config
from database.db import get_db

def init_database():
    db_dir = os.path.dirname(Config.DATABASE_PATH)
    os.makedirs(db_dir, exist_ok=True)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            device_type TEXT DEFAULT 'both',
            status TEXT DEFAULT 'offline',
            relay1_state TEXT DEFAULT 'off',
            relay2_state TEXT DEFAULT 'off',
            ip_address TEXT DEFAULT '',
            wifi_rssi INTEGER DEFAULT 0,
            last_seen TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL DEFAULT NULL,
            humidity REAL DEFAULT NULL,
            light REAL DEFAULT NULL,
            timestamp TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            relay_id TEXT NOT NULL,
            command TEXT NOT NULL,
            result TEXT DEFAULT 'pending',
            request_id TEXT DEFAULT '',
            operator TEXT DEFAULT 'web',
            timestamp TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_id ON devices(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_dev ON sensor_data(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_data(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ctrl_dev ON control_logs(device_id)')
    db.commit()
    db.close()
    print("[database] init OK")
'''

files['mqtt_handler/__init__.py'] = ''

files['mqtt_handler/subscriber.py'] = '''import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from config import Config
from database.db import get_db

logger = logging.getLogger(__name__)
mqtt_client = None

def connect_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(client_id=Config.MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    try:
        mqtt_client.connect(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        mqtt_client.loop_start()
        print("[MQTT] connected")
    except Exception as e:
        print(f"[MQTT] connect failed: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("iot/device/+/sensor/all", qos=1)
        client.subscribe("iot/device/+/status", qos=1)
        print("[MQTT] subscribed to device topics")

def on_disconnect(client, userdata, rc):
    print(f"[MQTT] disconnected: {rc}")

def on_message(client, userdata, msg):
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
    except Exception as e:
        print(f"[MQTT] message error: {e}")

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
        print(f"[SENSOR] db error: {e}")

def handle_status_data(device_id, payload):
    try:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            'UPDATE devices SET status=?, ip_address=?, wifi_rssi=?, last_seen=?, updated_at=? WHERE device_id=?',
            (payload.get('status','unknown'), payload.get('ip',''), payload.get('wifi_rssi',0), now, now, device_id)
        )
        db.commit()
        db.close()
        print(f"[STATUS] {device_id}: {payload.get('status')}")
    except Exception as e:
        print(f"[STATUS] db error: {e}")

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

files['models/__init__.py'] = ''

files['models/device.py'] = '''from datetime import datetime
from database.db import get_db

class DeviceModel:
    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute("SELECT * FROM devices ORDER BY created_at DESC").fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(device_id):
        db = get_db()
        row = db.execute("SELECT * FROM devices WHERE device_id=?", (device_id,)).fetchone()
        db.close()
        return dict(row) if row else None

    @staticmethod
    def create(device_id, name, description='', device_type='both'):
        db = get_db()
        db.execute("INSERT INTO devices (device_id, name, description, device_type) VALUES (?,?,?,?)",
                   (device_id, name, description, device_type))
        db.commit()
        db.close()

    @staticmethod
    def update(device_id, **kwargs):
        allowed = ['name', 'description', 'device_type']
        updates, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k}=?")
                values.append(v)
        if not updates:
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates.append("updated_at=?")
        values.append(now)
        values.append(device_id)
        db = get_db()
        db.execute(f"UPDATE devices SET {','.join(updates)} WHERE device_id=?", values)
        db.commit()
        db.close()

    @staticmethod
    def delete(device_id):
        db = get_db()
        db.execute("DELETE FROM devices WHERE device_id=?", (device_id,))
        db.commit()
        db.close()

    @staticmethod
    def exists(device_id):
        db = get_db()
        row = db.execute("SELECT 1 FROM devices WHERE device_id=?", (device_id,)).fetchone()
        db.close()
        return row is not None
'''

files['models/sensor_data.py'] = '''from database.db import get_db

class SensorDataModel:
    @staticmethod
    def get_latest(device_id):
        db = get_db()
        row = db.execute("SELECT * FROM sensor_data WHERE device_id=? ORDER BY timestamp DESC LIMIT 1", (device_id,)).fetchone()
        db.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_latest():
        db = get_db()
        rows = db.execute("""
            SELECT s.* FROM sensor_data s
            INNER JOIN (SELECT device_id, MAX(timestamp) as max_time FROM sensor_data GROUP BY device_id) latest
            ON s.device_id = latest.device_id AND s.timestamp = latest.max_time
        """).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_history(device_id, start=None, end=None, limit=100):
        db = get_db()
        query = "SELECT * FROM sensor_data WHERE device_id=?"
        params = [device_id]
        if start:
            query += " AND timestamp>=?"
            params.append(start)
        if end:
            query += " AND timestamp<=?"
            params.append(end)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = db.execute(query, params).fetchall()
        db.close()
        return [dict(r) for r in rows]
'''

files['routes/__init__.py'] = ''

files['routes/device_routes.py'] = '''from flask import Blueprint, jsonify, request
from models.device import DeviceModel

device_bp = Blueprint('device', __name__)

@device_bp.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        return jsonify({"code": 200, "message": "success", "data": DeviceModel.get_all()})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@device_bp.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    try:
        device = DeviceModel.get_by_id(device_id)
        if device is None:
            return jsonify({"code": 404, "message": "not found"}), 404
        return jsonify({"code": 200, "message": "success", "data": device})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@device_bp.route('/api/devices', methods=['POST'])
def create_device():
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        name = data.get('name')
        if not device_id or not name:
            return jsonify({"code": 400, "message": "device_id and name required"}), 400
        if DeviceModel.exists(device_id):
            return jsonify({"code": 409, "message": "device_id exists"}), 409
        DeviceModel.create(device_id, name, data.get('description',''), data.get('device_type','both'))
        return jsonify({"code": 201, "message": "created", "data": {"device_id": device_id}})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@device_bp.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    try:
        if not DeviceModel.exists(device_id):
            return jsonify({"code": 404, "message": "not found"}), 404
        DeviceModel.update(device_id, **request.get_json())
        return jsonify({"code": 200, "message": "updated"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@device_bp.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        if not DeviceModel.exists(device_id):
            return jsonify({"code": 404, "message": "not found"}), 404
        DeviceModel.delete(device_id)
        return jsonify({"code": 200, "message": "deleted"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
'''

files['routes/sensor_routes.py'] = '''from flask import Blueprint, jsonify, request
from models.sensor_data import SensorDataModel

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/api/sensors/all/latest', methods=['GET'])
def get_all_latest():
    try:
        return jsonify({"code": 200, "message": "success", "data": SensorDataModel.get_all_latest()})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@sensor_bp.route('/api/sensors/<device_id>/latest', methods=['GET'])
def get_latest(device_id):
    try:
        data = SensorDataModel.get_latest(device_id)
        if data is None:
            return jsonify({"code": 404, "message": "no data"}), 404
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@sensor_bp.route('/api/sensors/<device_id>/history', methods=['GET'])
def get_history(device_id):
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        limit = request.args.get('limit', 100, type=int)
        return jsonify({"code": 200, "message": "success", "data": SensorDataModel.get_history(device_id, start, end, limit)})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
'''

files['routes/control_routes.py'] = '''from flask import Blueprint, jsonify, request
from datetime import datetime
from database.db import get_db
from mqtt_handler.subscriber import publish_control
from models.device import DeviceModel

control_bp = Blueprint('control', __name__)

@control_bp.route('/api/control/<device_id>/relay/<relay_id>', methods=['POST'])
def control_relay(device_id, relay_id):
    try:
        if not DeviceModel.exists(device_id):
            return jsonify({"code": 404, "message": "device not found"}), 404
        if relay_id not in ['relay1', 'relay2']:
            return jsonify({"code": 400, "message": "relay_id must be relay1 or relay2"}), 400
        data = request.get_json()
        action = data.get('action')
        if action not in ['on', 'off', 'toggle']:
            return jsonify({"code": 400, "message": "action must be on/off/toggle"}), 400
        success = publish_control(device_id, relay_id, action)
        db = get_db()
        db.execute("INSERT INTO control_logs (device_id, relay_id, command, result, request_id) VALUES (?,?,?,?,?)",
                   (device_id, relay_id, action, 'success' if success else 'failed',
                    f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))
        if action in ['on', 'off']:
            db.execute(f"UPDATE devices SET {relay_id}_state=?, updated_at=? WHERE device_id=?",
                       (action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device_id))
        db.commit()
        db.close()
        if success:
            return jsonify({"code": 200, "message": "sent", "data": {"device_id": device_id, "relay": relay_id, "action": action}})
        return jsonify({"code": 500, "message": "mqtt send failed"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

@control_bp.route('/api/logs/control', methods=['GET'])
def get_control_logs():
    try:
        device_id = request.args.get('device_id')
        limit = request.args.get('limit', 50, type=int)
        db = get_db()
        if device_id:
            rows = db.execute("SELECT * FROM control_logs WHERE device_id=? ORDER BY timestamp DESC LIMIT ?", (device_id, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM control_logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        db.close()
        return jsonify({"code": 200, "message": "success", "data": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
'''

files['app.py'] = '''import logging
from flask import Flask
from flask_cors import CORS
from config import Config
from database.init_db import init_database
from mqtt_handler.subscriber import connect_mqtt
from routes.device_routes import device_bp
from routes.sensor_routes import sensor_bp
from routes.control_routes import control_bp

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    app.register_blueprint(device_bp)
    app.register_blueprint(sensor_bp)
    app.register_blueprint(control_bp)

    @app.route('/api/health')
    def health():
        return {"code": 200, "status": "running", "message": "IoT platform OK"}

    return app

if __name__ == '__main__':
    print("=" * 50)
    print("   IoT Cloud Platform")
    print("=" * 50)
    print("[1/3] Init database...")
    init_database()
    print("[2/3] Connect MQTT...")
    connect_mqtt()
    print("[3/3] Start Flask...")
    print("  Health: http://127.0.0.1:5000/api/health")
    print("  Devices: http://127.0.0.1:5000/api/devices")
    print("=" * 50)
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
'''

base = os.getcwd()
for filepath, content in files.items():
    full_path = os.path.join(base, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.lstrip('\n'))
    print(f"  created: {filepath}")

print("\nAll files created!")
