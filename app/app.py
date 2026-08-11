import os

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppassword"),
    )


@app.route("/")
def home():
    return jsonify({
        "application": "devops-challenge-api",
        "status": "running"
    })


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
