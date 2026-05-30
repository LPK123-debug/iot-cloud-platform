import os
from config import Config
from database.db import get_db


def init_database():
    """创建数据库表（如果不存在）"""

    # 确保 database 目录存在
    db_dir = os.path.dirname(Config.DATABASE_PATH)
    os.makedirs(db_dir, exist_ok=True)

    db = get_db()
    cursor = db.cursor()

    # 设备表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id       TEXT NOT NULL UNIQUE,
            name            TEXT NOT NULL,
            description     TEXT DEFAULT '',
            device_type     TEXT DEFAULT 'both',
            status          TEXT DEFAULT 'offline',
            relay1_state    TEXT DEFAULT 'off',
            relay2_state    TEXT DEFAULT 'off',
            ip_address      TEXT DEFAULT '',
            wifi_rssi       INTEGER DEFAULT 0,
            last_seen       TEXT DEFAULT '',
            created_at      TEXT DEFAULT (datetime('now','localtime')),
            updated_at      TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    # 传感器数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id       TEXT NOT NULL,
            temperature     REAL DEFAULT NULL,
            humidity        REAL DEFAULT NULL,
            light           REAL DEFAULT NULL,
            timestamp       TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    # 控制日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS control_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id       TEXT NOT NULL,
            relay_id        TEXT NOT NULL,
            command         TEXT NOT NULL,
            result          TEXT DEFAULT 'pending',
            request_id      TEXT DEFAULT '',
            operator        TEXT DEFAULT 'web',
            timestamp       TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    # 索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_id ON devices(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_dev ON sensor_data(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_data(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ctrl_dev ON control_logs(device_id)')

    db.commit()
    db.close()
    print("[数据库] 初始化完成")
