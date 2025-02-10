import asyncio
import pandas as pd
import yfinance as yf
from io import BytesIO
import traceback

from logic.indicators.indicators import IndicatorCalculator
from logging_config import logger


class HistoricalDataDownloader:
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"Initialized HistoricalDataDownloader for {self.symbol} from {self.start_date} to {self.end_date}")

    async def fetch_yahoo_finance_data(self):
        """Fetch historical stock data from Yahoo Finance asynchronously."""
        logger.info(f"Fetching data for {self.symbol} from Yahoo Finance...")
        try:
            ticker = yf.Ticker(self.symbol)
            historical_data = await asyncio.to_thread(
                ticker.history, start=self.start_date, end=self.end_date
            )
            if historical_data.empty:
                logger.warning(f"No data available for {self.symbol} from Yahoo Finance.")
                return None
            logger.info("Yahoo Finance data fetched successfully.")
            return historical_data
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance: {e}\n{traceback.format_exc()}")
            return None

    async def fetch_historical_data(self):
        """Fetch and validate historical data."""
        historical_data = await self.fetch_yahoo_finance_data()
        if historical_data is None or historical_data.empty:
            raise ValueError(f"No historical data found for {self.symbol} from Yahoo Finance.")
        return historical_data

    def calculate_indicators(self, historical_data: pd.DataFrame):
        """Compute technical indicators."""
        if "Close" not in historical_data.columns:
            logger.error("Error: 'Close' column missing. Cannot compute indicators.")
            return historical_data
        logger.info("Calculating technical indicators...")
        indicator_calculator = IndicatorCalculator(historical_data)
        return indicator_calculator.compute_all_indicators()

    async def generate_excel_file(self):
        """Fetches historical data, computes indicators, and writes to an Excel file."""
        logger.info("Generating Excel file with historical data and indicators...")
        try:
            historical_data = await self.fetch_historical_data()
            data_with_indicators = self.calculate_indicators(historical_data)
            if data_with_indicators is None:
                logger.error("Failed to compute indicators.")
                return None

            # Remove timezone information from the index, if present
            if hasattr(data_with_indicators.index, 'tz') and data_with_indicators.index.tz is not None:
                data_with_indicators.index = data_with_indicators.index.tz_localize(None)
            # Remove timezone from any datetime columns
            for col in data_with_indicators.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
                data_with_indicators[col] = data_with_indicators[col].dt.tz_localize(None)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                data_with_indicators.to_excel(writer, sheet_name='Historical Data', index=True)
            output.seek(0)
            logger.info("Excel file generation complete.")
            return output.getvalue()
        except Exception as e:
            logger.error(f"An error occurred during Excel generation: {e}\n{traceback.format_exc()}")
            return None
