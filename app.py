import sqlite3
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Import the aggregator module
from aggregator import aggregate_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
DB_FILE = "pulsedash.db"
CACHE_TTL_MINUTES = 10

# --- DATABASE SETUP ---

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                weather_json TEXT NOT NULL,
                news_json TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# --- CACHE & PERSISTENCE LAYER ---

def get_latest_data(force_refresh: bool = False) -> Tuple[Dict[str, Any], bool]:
    """Retrieves data from SQLite cache if fresh, otherwise runs aggregate_data()."""
    now = datetime.now(timezone.utc)
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, weather_json, news_json FROM snapshots ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row and not force_refresh:
            record_time = datetime.fromisoformat(row["timestamp"])
            if now - record_time < timedelta(minutes=CACHE_TTL_MINUTES):
                logging.info("Serving response from SQLite Cache.")
                return {
                    "timestamp": row["timestamp"],
                    "weather": json.loads(row["weather_json"]),
                    "news": json.loads(row["news_json"])
                }, True

    logging.info("Cache miss or forced refresh. Querying external APIs via aggregator...")
    weather_data, news_data = aggregate_data()
    timestamp_str = now.isoformat()
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots (timestamp, weather_json, news_json)
            VALUES (?, ?, ?)
        """, (timestamp_str, json.dumps(weather_data), json.dumps(news_data)))
        conn.commit()

    return {
        "timestamp": timestamp_str,
        "weather": weather_data,
        "news": news_data
    }, False

# --- WEB ROUTES ---

@app.route("/")
def index():
    data, is_cached = get_latest_data(force_refresh=False)
    return render_template("index.html", data=data, is_cached=is_cached, ttl=CACHE_TTL_MINUTES)

@app.route("/refresh", methods=["POST"])
def refresh():
    get_latest_data(force_refresh=True)
    return redirect(url_for("index"))

@app.route("/api/data")
def api_data():
    force = request.args.get("force", "false").lower() == "true"
    data, is_cached = get_latest_data(force_refresh=force)
    return jsonify({"cached": is_cached, "payload": data})

if __name__ == "__main__":
    app.run(debug=True, port=5000)