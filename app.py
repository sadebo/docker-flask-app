from flask import Flask, jsonify, request
import redis, logging
from config import Config
from database import get_connection, init_db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB
init_db()

# Connect Redis
r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/")
def home():
    return jsonify({
        "app": Config.APP_NAME,
        "environment": Config.ENVIRONMENT,
        "message": "Welcome to Flask CRUD API on AKS with TLS 🚀"
    })

@app.route("/healthz")
def healthz():
    try:
        r.ping()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/items", methods=["GET"])
def list_items():
    cached = r.get("items")
    if cached:
        return jsonify({"source": "cache", "items": eval(cached)})

    conn = get_connection()
    items = conn.execute("SELECT * FROM items").fetchall()
    result = [dict(row) for row in items]
    conn.close()
    r.set("items", str(result), ex=30)
    return jsonify({"source": "db", "items": result})

@app.route("/items", methods=["POST"])
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
    r.delete("items")
    return jsonify({"message": f"Item '{name}' added successfully"}), 201

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    r.delete("items")
    return jsonify({"message": f"Item {item_id} deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
