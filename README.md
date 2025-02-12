# Financial Dashboard & Historical Data Downloader

[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)

<a name="1"></a>
## Project Overview  
A Python-based Streamlit application that provides:  
- 📊 Real-time stock monitoring with technical indicators  
- 📥 Historical data download capability  
- 🔄 **Automatic fallback to Yahoo Finance** (due to **Alpha Vantage's Indian stock restrictions**)  
- ⚠️ **TA-Lib smoothing factor issue**: Indicator values may **not exactly match** those on trading platforms.  

###  **Key Components**  

🔹 **Streamlit Frontend** – Interactive UI for real-time stock tracking 📈  
🔹 **Yahoo Finance Integration** – Reliable market data source 🏦  
🔹 **TA-Lib Technical Indicators** – Advanced technical analysis 📊  
🔹 **Async Data Fetching** – Lightning-fast updates ⚡  
🔹 **Caching System** – Optimized performance & reduced API calls 🏎️  


---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dockerization](#Dockerization)
- [Async & Caching](#async--caching)
- [Logging](#logging)
- [Testing](#testing)
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
## Project Structure

```
📦 Project Root  
├── 📂 cache                      # Stores cached data for faster access  
├── 📂 constants                  # Contains constants like stock symbols  
│   ├── __init__.py  
│   ├── nifty_50_stock_symbols.py  
├── 📂 data_fetchers               # Handles fetching stock market data  
│   ├── 📂 stock_data_handler  
│   │   ├── __init__.py  
│   │   ├── stock_data_handler.py  
├── 📂 libs                        # Library functions  
├── 📂 logic                       # Core business logic  
│   ├── 📂 cache                   # Caching utilities  
│   ├── 📂 download_data           # Handles data downloading  
│   │   ├── __init__.py  
│   │   ├── download_data.py  
│   ├── 📂 indicators              # Implements TA-Lib indicators  
│   │   ├── __init__.py  
│   │   ├── indicators.py  
│   ├── 📂 tmp                     # Temporary storage  
├── 📂 logs                        # Stores application logs  
├── 📂 ml_models                   # Machine learning models  
│   ├── 📂 lorentzian_classifier  
│   │   ├── __init__.py  
│   │   ├── lorentzian_classifier.py  
├── 📂 services                    # API and data services  
│   ├── 📂 alpha_vantage_fetcher   # Fetches data from Alpha Vantage  
│   │   ├── 📂 cache  
│   │   ├── 📂 nifty_cache  
│   │   ├── __init__.py  
│   │   ├── alpha_vantage_fetcher.py  
│   ├── 📂 yahoo_finance_fetcher   # Fetches data from Yahoo Finance  
│   │   ├── __init__.py  
│   │   ├── yahoo_finance_fetcher.py  
├── 📂 test_suite                  # Contains unit and integration tests  
├── 📂 tmp                         # Temporary files  
├── 📂 utils                       # Utility functions  
├── 📂 venv                        # Virtual environment (excluded from repo)  
├── .gitignore                     # Git ignore file  
├── app.py                         # Main application entry point  
├── DockerFile                     # Docker file for contarization 
├── config.py                      # Configuration settings  
├── logging_config.py              # Logging configuration  
├── README.md                      # Project documentation  
├── requirements.txt               # Dependencies list  
├── secrets.json                   # API keys and secrets (excluded from repo)  
```

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
    streamlit run app.py
    ```

2. Available indicators:
    - Intraday Stock Prices
    - Moving Averages (SMA, EMA)
    - Relative Strength Index (RSI)
    - Bollinger Bands
    - MACD (Moving Average Convergence Divergence)

---

### **Dockerization**  

This project supports containerization using Docker. It simplifies the process of setting up and running the application in different environments.

#### **Docker Setup**

1. **Building the Docker Image**  
   To build the Docker image, run the following command:
   ```bash
   docker build -t financial-dashboard .
   ```

2. **Running the Application in a Container**  
   Once the image is built, you can run the container using this command:
   ```bash
   docker run -p 8501:8501 financial-dashboard
   ```

3. **Accessing the Application**  
   After running the container, access the application in your browser by visiting:  
   `http://localhost:8501`


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

## Logging

This project uses Python's built-in logging module, configured in `logging_config.py`, to record important application events. The logs are automatically written to rotating log files in the `logs` directory, ensuring that they don't grow indefinitely. The following log files are maintained:

- **General Logs:** All application events are logged to `logs/general.log`.
- **Alpha Vantage Logs:** Events related to fetching data from Alpha Vantage are logged to `logs/alpha_vantage.log`.
- **Yahoo Finance Logs:** Events related to fetching data from Yahoo Finance are logged to `logs/yahoo_finance.log`.

You can customize the log file locations, maximum file sizes, and backup counts by modifying the settings in `logging_config.py`.


---
## Testing

This project uses **pytest** for testing. The tests ensure that:
- API fallback to Yahoo Finance works when Alpha Vantage fails.
- Cached data is returned correctly.

Example test:
```python
import pytest
import pandas as pd
from unittest.mock import AsyncMock, Mock
from services.alpha_vantage_fetcher.alpha_vantage_fetcher import AlphaVantageFetcher

@pytest.mark.asyncio
class TestAlphaVantageFetcher:
    async def test_fetch_intraday_data_cached(self, mocker):
        mock_cache = Mock()
        mock_cache.get.return_value = pd.DataFrame({"Close": [100]})

        fetcher = AlphaVantageFetcher("AAPL", "5min")
        fetcher.cache = mock_cache

        result = await fetcher.fetch_intraday_data()
        assert not result.empty
        mock_cache.get.assert_called_once_with("AAPL_intraday")
```
To run tests:
```bash
pytest
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
