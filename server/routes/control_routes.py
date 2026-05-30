from flask import Blueprint, jsonify, request
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
