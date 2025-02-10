# Financial Dashboard & Historical Data Downloader

[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)

A real-time financial dashboard that fetches stock market data using **Alpha Vantage** and falls back to **Yahoo Finance** when necessary. The application efficiently handles API rate limits and leverages **disk caching** to optimize performance.

[GitHub Repository](https://github.com/namansethi1/financial_dashboard)

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Async & Caching](#async--caching)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Real-time stock market data retrieval.
- Asynchronous requests to prevent blocking operations.
- Caching using **diskcache** for performance optimization.
- API rate limit handling with intelligent retries.
- Securely manages API keys using `config.py` and `secrets.json`.

---

## Requirements

- Python 3.12.9
- Required dependencies are listed in `requirements.txt`.

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/namansethi1/financial_dashboard.git
    cd financial_dashboard
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

### API Key Setup

This project uses **`config.py` and `secrets.json`** for API key management:
- Create a `secrets.json` file in the root directory with the following structure:

    ```json
    {
        "ALPHA_VANTAGE_API_KEY": "your-api-key"
    }
    ```

- Ensure `secrets.json` is included in `.gitignore` so it is not exposed when forking the repository.
- `config.py` is responsible for loading secrets safely.

---

## Usage

1. Run the application:
    ```bash
    python main.py
    ```

2. Available indicators:
    - Intraday Stock Prices
    - Moving Averages (SMA, EMA)
    - Relative Strength Index (RSI)
    - Bollinger Bands
    - MACD (Moving Average Convergence Divergence)

---

## Async & Caching

### Asynchronous Data Fetching

The project uses **`asyncio` and `aiohttp`** to fetch data without blocking execution. This ensures that multiple requests can run concurrently.

Example:
```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    print("Data fetched!")

asyncio.run(fetch_data())
```

### Disk Caching

Instead of fetching data repeatedly, **diskcache** is used to cache API responses for 10 minutes. This prevents excessive API calls and speeds up performance.

Example:
```python
from diskcache import Cache

cache = Cache("./cache")

def get_cached_data(key):
    return cache.get(key)

def set_cached_data(key, value, expire=600):
    cache.set(key, value, expire=expire)
```

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork this repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.

---

## License

[MIT License](LICENSE)

---

## Acknowledgements

Thanks to:
- **Alpha Vantage** for providing financial data.
- **Yahoo Finance** as a fallback data source.
- **diskcache** for improving performance with caching.

---
