import sqlite3
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, List
from flask import Flask, render_template, jsonify, request, redirect, url_for

from aggregator import aggregate_data, CITY_COORDINATES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
DB_FILE = "pulsedash.db"
CACHE_TTL_MINUTES = 10

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                city TEXT NOT NULL DEFAULT 'London',
                weather_json TEXT NOT NULL,
                news_json TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

def get_latest_data(city: str = "London", force_refresh: bool = False) -> Tuple[Dict[str, Any], bool]:
    """Retrieves cached data per city if still valid; otherwise fetches live."""
    now = datetime.now(timezone.utc)
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, weather_json, news_json FROM snapshots WHERE city = ? ORDER BY id DESC LIMIT 1",
            (city,)
        )
        row = cursor.fetchone()
        
        if row and not force_refresh:
            record_time = datetime.fromisoformat(row["timestamp"])
            if now - record_time < timedelta(minutes=CACHE_TTL_MINUTES):
                logging.info(f"Serving response for {city} from SQLite cache.")
                return {
                    "timestamp": row["timestamp"],
                    "city": city,
                    "weather": json.loads(row["weather_json"]),
                    "news": json.loads(row["news_json"])
                }, True

    logging.info(f"Cache miss for {city}. Querying external APIs...")
    weather_data, news_data = aggregate_data(city)
    timestamp_str = now.isoformat()
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots (timestamp, city, weather_json, news_json)
            VALUES (?, ?, ?, ?)
        """, (timestamp_str, city, json.dumps(weather_data), json.dumps(news_data)))
        conn.commit()

    return {
        "timestamp": timestamp_str,
        "city": city,
        "weather": weather_data,
        "news": news_data
    }, False

def get_snapshot_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Fetches recent snapshot records for the audit view."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, city, weather_json, news_json
            FROM snapshots
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        history = []
        for r in rows:
            history.append({
                "id": r["id"],
                "timestamp": r["timestamp"][:19].replace("T", " "),
                "city": r["city"],
                "weather": json.loads(r["weather_json"]),
                "news": json.loads(r["news_json"])
            })
        return history

# --- ROUTES ---

@app.route("/")
def index():
    selected_city = request.args.get("city", "London")
    if selected_city not in CITY_COORDINATES:
        selected_city = "London"
        
    data, is_cached = get_latest_data(city=selected_city, force_refresh=False)
    return render_template(
        "index.html", 
        data=data, 
        is_cached=is_cached, 
        ttl=CACHE_TTL_MINUTES,
        cities=list(CITY_COORDINATES.keys()),
        current_city=selected_city
    )

@app.route("/refresh", methods=["POST"])
def refresh():
    city = request.form.get("city", "London")
    get_latest_data(city=city, force_refresh=True)
    return redirect(url_for("index", city=city))

@app.route("/history")
def history():
    records = get_snapshot_history()
    return render_template("history.html", records=records)

@app.route("/api/data")
def api_data():
    city = request.args.get("city", "London")
    force = request.args.get("force", "false").lower() == "true"
    data, is_cached = get_latest_data(city=city, force_refresh=force)
    return jsonify({"cached": is_cached, "payload": data})

if __name__ == "__main__":
    app.run(debug=True, port=5000)