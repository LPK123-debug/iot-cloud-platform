import os
code = """import logging, os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from database.init_db import init_database
from mqtt_handler.subscriber import connect_mqtt
from routes.device_routes import device_bp
from routes.sensor_routes import sensor_bp
from routes.control_routes import control_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

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

    return app

if __name__ == "__main__":
    print("=" * 50)
    print("   IoT Cloud Platform")
    print("=" * 50)
    print("[1/3] Init database...")
    init_database()
    print("[2/3] Connect MQTT...")
    connect_mqtt()
    print("[3/3] Start Flask...")
    print("  Dashboard: http://127.0.0.1:5000")
    print("  Health:    http://127.0.0.1:5000/api/health")
    print("=" * 50)
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
"""
with open(r"C:\iot-cloud-platform\server\app.py", "w", encoding="utf-8") as f:
    f.write(code)
print("app.py updated")