import pandas as pd

from logic.indicators.indicators import IndicatorCalculator


# Tests for IndicatorCalculator
class TestIndicatorCalculator:
    def test_rsi_calculation(self):
        """Test RSI calculation with known values"""
        test_data = pd.DataFrame({
            "Close": [100, 101, 102, 101, 100] * 10
        })
        calculator = IndicatorCalculator(test_data)
        rsi = calculator.calculate_rsi(14)
        assert len(rsi) == len(test_data)
        assert 0 <= rsi.iloc[-1] <= 100

    def test_wavetrend_calculation(self):
        """Test WaveTrend calculation structure"""
        test_data = pd.DataFrame({
            "High": [100, 101, 102],
            "Low": [99, 100, 101],
            "Close": [100, 100.5, 101.5]
        })
        calculator = IndicatorCalculator(test_data)
        wt1, wt2 = calculator.calculate_wavetrend()
        assert len(wt1) == len(test_data)
        assert len(wt2) == len(test_data)
