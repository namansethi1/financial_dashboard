import time
import asyncio
import streamlit as st
import plotly.graph_objects as go

from services.alpha_vantage_fetcher.alpha_vantage_fetcher import AlphaVantageFetcher
from logic.indicators.indicators import IndicatorCalculator
from services.yahoo_finance_fetcher.yahoo_finance_fetcher import YahooFinanceFetcher


class StockDataHandler:
    def __init__(self, ticker_symbol, interval, selected_indicators):
        self.ticker_symbol = ticker_symbol
        self.interval = interval
        self.selected_indicators = selected_indicators
        self.data_source = None  # Tracks whether AlphaVantage or Yahoo was used
        self.last_fetched_data = None  # Cache for faster subsequent calls

    async def fetch_stock_data(self):
        """Fetch stock data from AlphaVantage; fall back to Yahoo Finance if needed."""
        if self.last_fetched_data:
            return self.last_fetched_data

        # Initialize session state for the warning message
        if "alpha_vantage_fail" not in st.session_state:
            st.session_state["alpha_vantage_fail"] = False

        fetcher = AlphaVantageFetcher(self.ticker_symbol, self.interval)
        stock_data = await fetcher.fetch_intraday_data()

        if stock_data is None or stock_data.empty:
            if not st.session_state["alpha_vantage_fail"]:  # Show message only once
                st.warning(f"⚠️ No data found for {self.ticker_symbol} on AlphaVantage. Switching to Yahoo Finance.")
                st.session_state["alpha_vantage_fail"] = True  # Prevent duplicate messages

            yahoo_fetcher = YahooFinanceFetcher(self.ticker_symbol, self.interval)
            if not await yahoo_fetcher.validate_symbol():
                st.error(f"❌ Invalid symbol: {self.ticker_symbol}. Please enter a valid symbol.")
                st.stop()
            stock_data = await yahoo_fetcher.fetch_stock_data()

        self.last_fetched_data = stock_data
        return stock_data

    async def fetch_and_plot_data(self):
        """Fetch stock data, compute selected indicators, and plot the candlestick chart."""
        start_time = time.time()
        stock_data = await self.fetch_stock_data()

        if stock_data is None or stock_data.empty:
            st.warning(f"No data found for {self.ticker_symbol}.")
            return

        indicator_calculator = IndicatorCalculator(stock_data)
        tasks = []
        indicator_map = {}

        if "RSI 14" in self.selected_indicators:
            tasks.append(asyncio.to_thread(indicator_calculator.calculate_rsi, 14))
            indicator_map[len(tasks) - 1] = "RSI_14"

        if "RSI 9" in self.selected_indicators:
            tasks.append(asyncio.to_thread(indicator_calculator.calculate_rsi, 9))
            indicator_map[len(tasks) - 1] = "RSI_9"

        if "CCI 20" in self.selected_indicators:
            tasks.append(asyncio.to_thread(indicator_calculator.calculate_cci, 20))
            indicator_map[len(tasks) - 1] = "CCI_20"

        if "ADX 20" in self.selected_indicators:
            tasks.append(asyncio.to_thread(indicator_calculator.calculate_adx, 20))
            indicator_map[len(tasks) - 1] = "ADX_20"

        if "WaveTrend 1" in self.selected_indicators or "WaveTrend 2" in self.selected_indicators:
            tasks.append(asyncio.to_thread(indicator_calculator.calculate_wavetrend, 10, 11))
            indicator_map[len(tasks) - 1] = "WaveTrend"

        results = await asyncio.gather(*tasks)

        for i, key in indicator_map.items():
            if key == "WaveTrend":
                if results[i] and len(results[i]) == 2:
                    stock_data["WaveTrend_1"], stock_data["WaveTrend_2"] = results[i]
                else:
                    st.warning("⚠️ Error computing WaveTrend. Check input data.")
                    stock_data["WaveTrend_1"], stock_data["WaveTrend_2"] = None, None
            else:
                stock_data[key] = results[i] if results[i] is not None else None

        self.plot_stock_chart(stock_data)
        end_time = time.time()

    def plot_stock_chart(self, df):
        """Plot a candlestick chart (with indicators) using Plotly."""
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="Candlestick", increasing_line_color='green', decreasing_line_color='red'
        ))
        for indicator in self.selected_indicators:
            column_name = indicator.replace(" ", "_")
            if column_name in df:
                fig.add_trace(go.Scatter(x=df.index, y=df[column_name], mode='lines', name=indicator))
        fig.update_layout(title=f"{self.ticker_symbol} Stock Chart", xaxis_title="Time",
                          yaxis_title="Price", template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)
