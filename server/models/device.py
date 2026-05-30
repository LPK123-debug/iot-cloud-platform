from datetime import datetime
from database.db import get_db


class DeviceModel:

    @staticmethod
    def get_all():
        """获取所有设备"""
        db = get_db()
        rows = db.execute('SELECT * FROM devices ORDER BY created_at DESC').fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(device_id):
        """根据 device_id 获取设备"""
        db = get_db()
        row = db.execute('SELECT * FROM devices WHERE device_id=?', (device_id,)).fetchone()
        db.close()
        return dict(row) if row else None

    @staticmethod
    def create(device_id, name, description='', device_type='both'):
        """注册新设备"""
        db = get_db()
        db.execute(
            'INSERT INTO devices (device_id, name, description, device_type) VALUES (?,?,?,?)',
            (device_id, name, description, device_type)
        )
        db.commit()
        db.close()
        return True

    @staticmethod
    def update(device_id, **kwargs):
        """更新设备信息"""
        allowed = ['name', 'description', 'device_type']
        updates, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k}=?")
                values.append(v)

        if not updates:
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates.append("updated_at=?")
        values.append(now)
        values.append(device_id)

        db = get_db()
        db.execute(f"UPDATE devices SET {','.join(updates)} WHERE device_id=?", values)
        db.commit()
        db.close()
        return True

    @staticmethod
    def delete(device_id):
        """删除设备"""
        db = get_db()
        db.execute('DELETE FROM devices WHERE device_id=?', (device_id,))
        db.commit()
        db.close()
        return True

    @staticmethod
    def exists(device_id):
        """检查设备是否存在"""
        db = get_db()
        row = db.execute('SELECT 1 FROM devices WHERE device_id=?', (device_id,)).fetchone()
        db.close()
        return row is not None
