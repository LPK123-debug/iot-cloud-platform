from flask import Blueprint, jsonify, request
from models.sensor_data import SensorDataModel

sensor_bp = Blueprint('sensor', __name__)


@sensor_bp.route('/api/sensors/all/latest', methods=['GET'])
def get_all_latest():
    """获取所有设备最新数据"""
    try:
        data = SensorDataModel.get_all_latest()
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@sensor_bp.route('/api/sensors/<device_id>/latest', methods=['GET'])
def get_latest(device_id):
    """获取单个设备最新数据"""
    try:
        data = SensorDataModel.get_latest(device_id)
        if data is None:
            return jsonify({"code": 404, "message": "暂无数据"}), 404
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@sensor_bp.route('/api/sensors/<device_id>/history', methods=['GET'])
def get_history(device_id):
    """获取设备历史数据"""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        limit = request.args.get('limit', 100, type=int)

        data = SensorDataModel.get_history(device_id, start, end, limit)
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
