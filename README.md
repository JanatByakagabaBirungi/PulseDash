# PulseDash

PulseDash is a concurrent API aggregation dashboard built in Python using Flask and SQLite3. It concurrently aggregates live weather metrics from Open-Meteo and curated technical headlines from the Hacker News Firebase API, caches results per location, monitors network latency, and exposes an audit log of previous snapshots.

## Features

- **Concurrent I/O:** Leverages `concurrent.futures.ThreadPoolExecutor` to run API calls in parallel, bounded only by the slowest external service.
- **Latency & Performance Telemetry:** Records round-trip network response times (`latency_ms`) using high-precision timers for every API execution.
- **Multi-Location Weather:** Dynamic city selection (London, New York, Tokyo, Paris, Nairobi) mapping directly to geocoordinates.
- **WMO Weather Interpretation:** Translates raw numerical weather codes into human-readable conditions and descriptive icons.
- **SQLite Cache & Historical Persistence:** Retains snapshots across cities with a 10-minute Time-To-Live (TTL) cache to prevent rate limiting, plus an audit trail at `/history`.
- **Zero API Keys:** Operates out of the box using public APIs without registration keys or secrets.

## Tech Stack

- **Backend:** Python 3, Flask, Requests
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Jinja2 Templates

## Getting Started

### Prerequisites
- Python 3.10+ installed

=======
### Installation
>>>>>>> 778f6e4ae3467394473e0ae7f3390e19afbd9c40
1. Clone the repository:
   ```bash
   git clone [https://github.com/JanatByakagabaBirungi/PulseDash.git](https://github.com/JanatByakagabaBirungi/PulseDash.git)
   cd PulseDash

# notes
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# python app.py

# OR
# python -m venv venv
# venv\Scripts\activate
# pip install -r requirements.txt
# python app.py

