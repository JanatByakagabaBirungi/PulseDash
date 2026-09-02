import concurrent.futures
import json
import logging
from typing import Dict, Any, Tuple
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def fetch_weather() -> Dict[str, Any]:
    """Fetches current weather for London using Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.5085,
        "longitude": -0.1257,
        "current_weather": True
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json().get("current_weather", {})
        return {
            "status": "success",
            "temperature": f"{data.get('temperature', 'N/A')}°C",
            "wind_speed": f"{data.get('windspeed', 'N/A')} km/h",
            "condition_code": data.get("weathercode", 0)
        }
    except requests.RequestException as e:
        logging.error(f"Weather fetch error: {e}")
        return {"status": "error", "message": "Weather unavailable"}

def fetch_news() -> Dict[str, Any]:
    """Fetches top 4 stories from Hacker News."""
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
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
        return {"status": "success", "stories": stories}
    except requests.RequestException as e:
        logging.error(f"News fetch error: {e}")
        return {"status": "error", "message": "Headlines unavailable", "stories": []}

def aggregate_data() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Runs weather and news fetches concurrently."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_weather = executor.submit(fetch_weather)
        f_news = executor.submit(fetch_news)
        return f_weather.result(), f_news.result()

if __name__ == "__main__":
    weather, news = aggregate_data()
    print(json.dumps({"weather": weather, "news": news}, indent=4))