import asyncio
import yfinance as yf
import streamlit as st

from logging_config import yahoo_logger


class YahooFinanceFetcher:
    def __init__(self, ticker_symbol, interval):
        self.ticker_symbol = ticker_symbol
        self.interval = interval
        self.interval_map = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "60min": "60m",
        }
        yahoo_logger.info("Initialized YahooFinanceFetcher for ticker %s with interval %s", self.ticker_symbol,
                          self.interval)

    async def fetch_stock_data(self):
        try:
            yahoo_logger.info("Fetching Yahoo Finance data for ticker %s", self.ticker_symbol)
            ticker = yf.Ticker(self.ticker_symbol)
            yahoo_interval = self.interval_map.get(self.interval, "5m")  # Default to 5m if interval is invalid
            stock_data = await asyncio.to_thread(ticker.history, period="1d", interval=yahoo_interval)

            if stock_data.empty:
                yahoo_logger.warning("Fetched data is empty for ticker %s", self.ticker_symbol)
            else:
                yahoo_logger.info("Successfully fetched data for ticker %s", self.ticker_symbol)

            return stock_data
        except Exception as e:
            yahoo_logger.error("Failed to fetch data from Yahoo Finance for ticker %s: %s", self.ticker_symbol, str(e))
            st.error(f"❌ Failed to fetch data from Yahoo Finance: {str(e)}")
            return None

    async def validate_symbol(self):
        try:
            yahoo_logger.info("Validating symbol %s with Yahoo Finance", self.ticker_symbol)
            ticker = yf.Ticker(self.ticker_symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            if 'symbol' not in info or not info['symbol']:
                yahoo_logger.error("Validation failed for symbol %s", self.ticker_symbol)
                st.error(f"❌ Invalid symbol: {self.ticker_symbol}. Please enter a valid symbol.")
                return False
            yahoo_logger.info("Symbol %s validated successfully", self.ticker_symbol)
            return True
        except Exception as e:
            yahoo_logger.error("Error during symbol validation for %s: %s", self.ticker_symbol, str(e))
            st.error(f"❌ Invalid symbol: {self.ticker_symbol}. Please enter a valid symbol.")
            return False
