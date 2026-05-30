from flask import Blueprint, jsonify, request
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
