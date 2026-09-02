# PulseDash

A concurrent API aggregation dashboard built with Python and Flask. PulseDash queries the Open-Meteo and Hacker News Firebase APIs in parallel, caches responses inside an SQLite database to avoid rate-limiting, and delivers the data via a responsive web interface and JSON API.

## Features

- **Concurrent I/O:** Uses `concurrent.futures.ThreadPoolExecutor` to execute multiple network calls simultaneously.
- **Data Caching & Persistence:** Automatically caches API snapshots to a local SQLite database with a configurable 10-minute Time-To-Live (TTL).
- **Fault-Tolerant:** Individual API failures do not halt the application; fallbacks gracefully alert the interface.
- **REST Endpoint:** Includes an `/api/data` route that serves cached or freshly computed JSON.
- **Zero API Keys Required:** Runs entirely on open, registration-free public APIs.

## Tech Stack

- **Backend:** Python 3, Flask, Requests
- **Database:** SQLite3
- **Frontend:** Jinja2, Semantic HTML5, Vanilla CSS

## Getting Started

### Prerequisites
- Python 3.10+ installed

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/pulsedash.git
   cd pulsedash
