from flask import Blueprint, jsonify, request
from models.device import DeviceModel

device_bp = Blueprint('device', __name__)


@device_bp.route('/api/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表"""
    try:
        devices = DeviceModel.get_all()
        return jsonify({"code": 200, "message": "success", "data": devices})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@device_bp.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """获取单个设备详情"""
    try:
        device = DeviceModel.get_by_id(device_id)
        if device is None:
            return jsonify({"code": 404, "message": "设备不存在"}), 404
        return jsonify({"code": 200, "message": "success", "data": device})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@device_bp.route('/api/devices', methods=['POST'])
def create_device():
    """注册新设备"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        name = data.get('name')

        if not device_id or not name:
            return jsonify({"code": 400, "message": "device_id 和 name 不能为空"}), 400

        if DeviceModel.exists(device_id):
            return jsonify({"code": 409, "message": "设备ID已存在"}), 409

        description = data.get('description', '')
        device_type = data.get('device_type', 'both')
        DeviceModel.create(device_id, name, description, device_type)

        return jsonify({"code": 201, "message": "设备注册成功", "data": {"device_id": device_id}})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@device_bp.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备信息"""
    try:
        if not DeviceModel.exists(device_id):
            return jsonify({"code": 404, "message": "设备不存在"}), 404
        data = request.get_json()
        DeviceModel.update(device_id, **data)
        return jsonify({"code": 200, "message": "更新成功"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@device_bp.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """删除设备"""
    try:
        if not DeviceModel.exists(device_id):
            return jsonify({"code": 404, "message": "设备不存在"}), 404
        DeviceModel.delete(device_id)
        return jsonify({"code": 200, "message": "删除成功"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
