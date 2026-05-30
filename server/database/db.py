import sqlite3
from config import Config


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
