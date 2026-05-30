from datetime import datetime
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
