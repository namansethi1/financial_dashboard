import talib
import pandas as pd


class IndicatorCalculator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def calculate_rsi(self, period: int = 14):
        """Calculate RSI for the given period."""
        return talib.RSI(self.df['Close'], timeperiod=period)

    def calculate_wavetrend(self, n1=10, n2=11):
        """Calculate WaveTrend (WT) indicator."""
        hlc3 = (self.df['High'] + self.df['Low'] + self.df['Close']) / 3
        esa = talib.EMA(hlc3, timeperiod=n1)
        d = talib.EMA(abs(hlc3 - esa), timeperiod=n1)
        ci = (hlc3 - esa) / (0.015 * d)
        wt1 = talib.EMA(ci, timeperiod=n2)
        wt2 = talib.SMA(wt1, timeperiod=4)
        return wt1, wt2  # Return both WaveTrend components as a tuple

    def calculate_cci(self, period: int = 20):
        """Calculate CCI for the given period."""
        return talib.CCI(self.df['High'], self.df['Low'], self.df['Close'], timeperiod=period)

    def calculate_adx(self, period: int = 20):
        """Calculate ADX for the given period."""
        return talib.ADX(self.df['High'], self.df['Low'], self.df['Close'], timeperiod=period)

    def compute_all_indicators(self):
        """Compute all required indicators and return updated DataFrame."""
        self.df['RSI_14'] = self.calculate_rsi(14)
        self.df['RSI_9'] = self.calculate_rsi(9)
        self.df['CCI_20'] = self.calculate_cci(20)
        self.df['ADX_20'] = self.calculate_adx(20)
        self.df['WT1'], self.df['WT2'] = self.calculate_wavetrend()  # Correct unpacking
        return self.df
