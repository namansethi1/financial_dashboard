import pytest
from unittest.mock import Mock

from services.yahoo_finance_fetcher.yahoo_finance_fetcher import YahooFinanceFetcher


@pytest.mark.asyncio
class TestYahooFinanceFetcher:
    async def test_valid_symbol(self, mocker):
        """Test valid symbol validation"""
        mock_ticker = Mock()
        mock_ticker.info = {"symbol": "AAPL"}
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        fetcher = YahooFinanceFetcher("AAPL", "5min")
        result = await fetcher.validate_symbol()
        assert result is True

    async def test_invalid_symbol(self, mocker):
        """Test invalid symbol validation"""
        mock_ticker = Mock()
        mock_ticker.info = {}
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        fetcher = YahooFinanceFetcher("INVALID", "5min")
        result = await fetcher.validate_symbol()
        assert result is False
