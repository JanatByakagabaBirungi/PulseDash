import concurrent.futures
import json
import logging
import time
from typing import Dict, Any, Tuple
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Supported city coordinate presets
CITY_COORDINATES = {
    "London": (51.5085, -0.1257),
    "New York": (40.7128, -74.0060),
    "Tokyo": (35.6762, 139.6503),
    "Paris": (48.8566, 2.3522),
    "Nairobi": (-1.2921, 36.8219),
}

WMO_CODE_MAP = {
    0: "Clear Sky ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing Rime Fog 🌫️",
    51: "Light Drizzle 🌦️",
    53: "Moderate Drizzle 🌦️",
    55: "Dense Drizzle 🌧️",
    61: "Slight Rain 🌧️",
    63: "Moderate Rain 🌧️",
    65: "Heavy Rain 🌧️",
    71: "Slight Snow 🌨️",
    73: "Moderate Snow 🌨️",
    75: "Heavy Snow ❄️",
    80: "Rain Showers 🌦️",
    81: "Moderate Showers 🌧️",
    82: "Violent Showers ⛈️",
    95: "Thunderstorm ⛈️",
}

def decode_weather(code: int) -> str:
    return WMO_CODE_MAP.get(code, "Unknown Condition 🌡️")

def fetch_weather(city: str = "London") -> Dict[str, Any]:
    """Fetches real-time weather metrics and calculates request latency."""
    lat, lon = CITY_COORDINATES.get(city, CITY_COORDINATES["London"])
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    
    start_time = time.perf_counter()
    try:
        res = requests.get(url, params=params, timeout=5)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
        res.raise_for_status()
        
        current = res.json().get("current_weather", {})
        weather_code = current.get("weathercode", 0)
        
        return {
            "status": "success",
            "city": city,
            "temperature": f"{current.get('temperature', 'N/A')}°C",
            "wind_speed": f"{current.get('windspeed', 'N/A')} km/h",
            "condition": decode_weather(weather_code),
            "latency_ms": latency_ms
        }
    except requests.RequestException as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
        logging.error(f"Weather fetch error for {city}: {e}")
        return {
            "status": "error",
            "city": city,
            "message": "Weather service unreachable",
            "latency_ms": latency_ms
        }

def fetch_news() -> Dict[str, Any]:
    """Fetches top 4 stories from Hacker News and calculates cumulative latency."""
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    start_time = time.perf_counter()
    
    try:
        res = requests.get(top_stories_url, timeout=5)
        res.raise_for_status()
        top_ids = res.json()[:4]
        
        stories = []
        for sid in top_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
            item_res = requests.get(item_url, timeout=5)
            if item_res.status_code == 200:
                item_data = item_res.json()
                stories.append({
                    "title": item_data.get("title", "Untitled"),
                    "url": item_data.get("url", "https://news.ycombinator.com"),
                    "score": item_data.get("score", 0)
                })
                
        latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
        return {"status": "success", "stories": stories, "latency_ms": latency_ms}
    except requests.RequestException as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
        logging.error(f"News fetch error: {e}")
        return {
            "status": "error",
            "message": "Headlines unavailable",
            "stories": [],
            "latency_ms": latency_ms
        }

def aggregate_data(city: str = "London") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Runs weather and news fetches concurrently."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_weather = executor.submit(fetch_weather, city)
        f_news = executor.submit(fetch_news)
        return f_weather.result(), f_news.result()

if __name__ == "__main__":
    weather, news = aggregate_data("London")
    print(json.dumps({"weather": weather, "news": news}, indent=4))