import aiohttp
import asyncio
import pandas as pd
import os
import logging
import yfinance as yf
from diskcache import Cache
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaVantageFetcher")

class AlphaVantageFetcher:
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

    def __init__(self, ticker: str, interval: str = "5min"):
        self.ticker = ticker
        self.interval = interval
        self.cache = Cache("./cache")
        self.semaphore = asyncio.Semaphore(3)

    async def _fetch(self, session: aiohttp.ClientSession, url: str):
        async with self.semaphore:
            retries = 3
            delay = 5

            for attempt in range(retries):
                try:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        data = await response.json()

                        if "Note" in data:  # API rate limit hit
                            logger.warning("Rate limit hit, retrying in %s seconds...", delay)
                            time.sleep(delay)
                            delay *= 2
                            continue

                        return data
                except aiohttp.ClientError as e:
                    logger.error("Network error: %s", e)
                    return None

        return None

    async def fetch_intraday_data(self):
        """Fetch stock data with caching. Falls back to Yahoo Finance if AlphaVantage fails."""
        cache_key = f"{self.ticker}_intraday"
        cached_data = self.cache.get(cache_key)

        if cached_data is not None:
            logger.info("Using cached data for %s", self.ticker)
            return cached_data

        # Fetch from AlphaVantage
        url = (f"{self.BASE_URL}?function=TIME_SERIES_INTRADAY&symbol={self.ticker}&"
               f"interval={self.interval}&apikey={self.API_KEY}&outputsize=compact")

        async with aiohttp.ClientSession() as session:
            data = await self._fetch(session, url)

            if data and f"Time Series ({self.interval})" in data:
                df = pd.DataFrame.from_dict(data[f"Time Series ({self.interval})"], orient='index', dtype=float)
                df = df.rename(columns={ "1. open": "Open", "2. high": "High", "3. low": "Low", "4. close": "Close", "5. volume": "Volume" })
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                self.cache.set(cache_key, df, expire=600)
                return df

        # If AlphaVantage fails, fall back to Yahoo Finance
        logger.warning("AlphaVantage data not available, switching to Yahoo Finance...")
        try:
            stock = yf.Ticker(self.ticker)
            df = stock.history(period="1d", interval=self.interval)

            if df.empty:
                logger.error("Yahoo Finance data also unavailable for %s", self.ticker)
                return pd.DataFrame()

            self.cache.set(cache_key, df, expire=600)
            return df

        except Exception as e:
            logger.error("Failed to fetch data from Yahoo Finance: %s", str(e))
            return pd.DataFrame()
