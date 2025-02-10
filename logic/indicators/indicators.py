import talib
import pandas as pd
from logging_config import logger


class IndicatorCalculator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        logger.info("IndicatorCalculator initialized with DataFrame shape: %s", self.df.shape)

    def calculate_rsi(self, period: int = 14):
        """Calculate RSI for the given period."""
        logger.info("Calculating RSI with period %d", period)
        try:
            result = talib.RSI(self.df['Close'], timeperiod=period)
            logger.debug("RSI calculated successfully.")
            return result
        except Exception as e:
            logger.error("Error calculating RSI: %s", e, exc_info=True)
            return None

    def calculate_wavetrend(self, n1=10, n2=11):
        """Calculate WaveTrend (WT) indicator."""
        logger.info("Calculating WaveTrend with parameters n1=%d, n2=%d", n1, n2)
        try:
            hlc3 = (self.df['High'] + self.df['Low'] + self.df['Close']) / 3
            esa = talib.EMA(hlc3, timeperiod=n1)
            d = talib.EMA(abs(hlc3 - esa), timeperiod=n1)
            ci = (hlc3 - esa) / (0.015 * d)
            wt1 = talib.EMA(ci, timeperiod=n2)
            wt2 = talib.SMA(wt1, timeperiod=4)
            logger.debug("WaveTrend indicators calculated successfully.")
            return wt1, wt2  # Return both WaveTrend components as a tuple
        except Exception as e:
            logger.error("Error calculating WaveTrend: %s", e, exc_info=True)
            return None, None

    def calculate_cci(self, period: int = 20):
        """Calculate CCI for the given period."""
        logger.info("Calculating CCI with period %d", period)
        try:
            result = talib.CCI(self.df['High'], self.df['Low'], self.df['Close'], timeperiod=period)
            logger.debug("CCI calculated successfully.")
            return result
        except Exception as e:
            logger.error("Error calculating CCI: %s", e, exc_info=True)
            return None

    def calculate_adx(self, period: int = 20):
        """Calculate ADX for the given period."""
        logger.info("Calculating ADX with period %d", period)
        try:
            result = talib.ADX(self.df['High'], self.df['Low'], self.df['Close'], timeperiod=period)
            logger.debug("ADX calculated successfully.")
            return result
        except Exception as e:
            logger.error("Error calculating ADX: %s", e, exc_info=True)
            return None

    def compute_all_indicators(self):
        """Compute all required indicators and return updated DataFrame."""
        logger.info("Computing all indicators.")
        try:
            self.df['RSI_14'] = self.calculate_rsi(14)
            self.df['RSI_9'] = self.calculate_rsi(9)
            self.df['CCI_20'] = self.calculate_cci(20)
            self.df['ADX_20'] = self.calculate_adx(20)
            wt1, wt2 = self.calculate_wavetrend()
            self.df['WT1'] = wt1
            self.df['WT2'] = wt2
            logger.info("All indicators computed successfully.")
            return self.df
        except Exception as e:
            logger.error("Error computing all indicators: %s", e, exc_info=True)
            return self.df
