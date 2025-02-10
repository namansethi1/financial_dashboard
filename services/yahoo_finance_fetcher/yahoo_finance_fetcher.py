import asyncio
import yfinance as yf
import streamlit as st


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

    async def fetch_stock_data(self):
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            yahoo_interval = self.interval_map.get(self.interval, "5m")  # Default to 5m if interval is invalid
            stock_data = await asyncio.to_thread(ticker.history, period="1d", interval=yahoo_interval)
            return stock_data
        except Exception as e:
            st.error(f"❌ Failed to fetch data from Yahoo Finance: {str(e)}")
            return None

    async def validate_symbol(self):
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            if 'symbol' not in info or not info['symbol']:
                st.error(f"❌ Invalid symbol: {self.ticker_symbol}. Please enter a valid symbol.")
                return False
            return True
        except Exception:
            st.error(f"❌ Invalid symbol: {self.ticker_symbol}. Please enter a valid symbol.")
            return False
