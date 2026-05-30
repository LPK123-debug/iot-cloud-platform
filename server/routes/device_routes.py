from flask import Blueprint, jsonify, request
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
