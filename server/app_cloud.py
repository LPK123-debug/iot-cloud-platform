import logging
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config_cloud import Config
from database.init_db import init_database
from mqtt_handler.subscriber_cloud import connect_mqtt
from routes.device_routes import device_bp
from routes.sensor_routes import sensor_bp
from routes.control_routes import control_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# 确保数据目录存在
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

# 静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def create_app():
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
    app.config.from_object(Config)
    CORS(app)
    app.register_blueprint(device_bp)
    app.register_blueprint(sensor_bp)
    app.register_blueprint(control_bp)

    @app.route("/api/health")
    def health():
        return {"code": 200, "status": "running", "message": "IoT platform OK"}

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.route("/api/debug/mqtt")
    def debug_mqtt():
        from mqtt_handler import subscriber_cloud as sub
        st = "connected" if sub.mqtt_client and sub.mqtt_client.is_connected() else "disconnected"
        return {"mqtt_status": st, "client_exists": sub.mqtt_client is not None}

    @app.route("/api/debug/db")
    def debug_db():
        from database.db import get_db
        db = get_db()
        devices = db.execute("SELECT * FROM devices").fetchall()
        sensors = db.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5").fetchall()
        db.close()
        return {"devices": [dict(d) for d in devices], "latest_sensors": [dict(s) for s in sensors]}

    return app


if __name__ == "__main__":
    print("=" * 50)
    print("   IoT Cloud Platform (Cloud Version)")
    print("=" * 50)
    print("[1/3] Init database...")
    init_database()
    print("[2/3] Connect to HiveMQ Cloud...")
    connect_mqtt()
    print("[3/3] Start Flask...")
    print("=" * 50)

    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)