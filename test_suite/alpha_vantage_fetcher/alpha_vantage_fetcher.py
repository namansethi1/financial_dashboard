import pytest
import pandas as pd
from unittest.mock import AsyncMock, Mock

from services.alpha_vantage_fetcher.alpha_vantage_fetcher import AlphaVantageFetcher


# Tests for AlphaVantageFetcher
@pytest.mark.asyncio
class TestAlphaVantageFetcher:
    async def test_fetch_intraday_data_cached(self, mocker):
        """Test that cached data is returned when available"""
        mock_cache = Mock()
        mock_cache.get.return_value = pd.DataFrame({"Close": [100]})

        fetcher = AlphaVantageFetcher("AAPL", "5min")
        fetcher.cache = mock_cache

        result = await fetcher.fetch_intraday_data()
        assert not result.empty
        mock_cache.get.assert_called_once_with("AAPL_intraday")

    async def test_api_failure_fallbacks_to_yahoo(self, mocker):
        """Test fallback to Yahoo Finance when AlphaVantage fails"""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value={})))))

        mock_yf = Mock()
        mock_yf.history.return_value = pd.DataFrame({"Close": [100]})
        mocker.patch("yfinance.Ticker", return_value=mock_yf)

        fetcher = AlphaVantageFetcher("TATASTEEL.NS", "5min")
        result = await fetcher.fetch_intraday_data()

        assert not result.empty
        assert mock_yf.history.called
