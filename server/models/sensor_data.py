from database.db import get_db


class SensorDataModel:

    @staticmethod
    def get_latest(device_id):
        """获取设备最新一条传感器数据"""
        db = get_db()
        row = db.execute(
            'SELECT * FROM sensor_data WHERE device_id=? ORDER BY timestamp DESC LIMIT 1',
            (device_id,)
        ).fetchone()
        db.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_latest():
        """获取所有设备的最新数据"""
        db = get_db()
        rows = db.execute('''
            SELECT s.* FROM sensor_data s
            INNER JOIN (
                SELECT device_id, MAX(timestamp) as max_time
                FROM sensor_data GROUP BY device_id
            ) latest ON s.device_id = latest.device_id AND s.timestamp = latest.max_time
        ''').fetchall()
        db.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_history(device_id, start=None, end=None, limit=100):
        """获取设备历史数据"""
        db = get_db()
        query = 'SELECT * FROM sensor_data WHERE device_id=?'
        params = [device_id]

        if start:
            query += ' AND timestamp>=?'
            params.append(start)
        if end:
            query += ' AND timestamp<=?'
            params.append(end)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        rows = db.execute(query, params).fetchall()
        db.close()
        return [dict(r) for r in rows]
