from flask import Flask, jsonify, request, render_template
import redis, logging
from config import Config
from database import get_connection, init_db
from prometheus_flask_exporter import PrometheusMetrics




app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

metrics = PrometheusMetrics(app)
metrics.info("app_info", "Application info", version="2.0.0")

init_db()
try:
    r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
    r.ping()
    redis_ok = True
except Exception as e:
    print(f"⚠️ Redis not reachable: {e}")
    r = None
    redis_ok = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/")
def home():
    conn = get_connection()
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    result = [dict(row) for row in items]
    return render_template(
        "index.html",
        app_name=Config.APP_NAME,
        environment=Config.ENVIRONMENT,
        items=result
    )

@app.route("/healthz")
def healthz():
    if redis_ok:
        return jsonify({"status": "healthy"}), 200
    return jsonify({"status": "degraded", "message": "Redis unavailable"}), 200

@app.route("/api/items", methods=["GET"])
def list_items():
    conn = get_connection()
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    result = [dict(row) for row in items]
    return jsonify(result)

@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.get_json()
    name = data.get("name")
    desc = data.get("description", "")
    if not name:
        return jsonify({"error": "name is required"}), 400
    conn = get_connection()
    conn.execute("INSERT INTO items (name, description) VALUES (?, ?)", (name, desc))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Item '{name}' added successfully"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    logging.info(f"Starting {Config.APP_NAME} in {Config.ENVIRONMENT} mode")