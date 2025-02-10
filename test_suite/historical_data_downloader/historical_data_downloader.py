import pytest
import pandas as pd
from unittest.mock import Mock

from logic.download_data.download_data import HistoricalDataDownloader
from logic.indicators.indicators import IndicatorCalculator


@pytest.mark.asyncio
class TestHistoricalDataDownloader:
    async def test_successful_data_fetch(self, mocker):
        """Test successful historical data retrieval"""
        mock_data = pd.DataFrame({"Close": [100]})
        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_data
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        downloader = HistoricalDataDownloader("AAPL", "2020-01-01", "2020-01-05")
        result = await downloader.fetch_historical_data()
        assert not result.empty

    async def test_calculate_indicators(self):
        """Test indicator calculations"""
        test_data = pd.DataFrame({
            "Open": [100], "High": [101],
            "Low": [99], "Close": [100.5],
            "Volume": [100000]
        })
        calculator = IndicatorCalculator(test_data)
        result = calculator.compute_all_indicators()

        assert "RSI_14" in result.columns
        assert "WT1" in result.columns
