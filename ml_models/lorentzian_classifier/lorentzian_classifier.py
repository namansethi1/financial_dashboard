import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator, ClassifierMixin


class LorentzianClassifier(BaseEstimator, ClassifierMixin):
    """
    Basic Lorentzian Classification implementation for price pattern recognition
    """
    def __init__(self, n_neighbors=5, lookback=14):
        self.n_neighbors = n_neighbors
        self.lookback = lookback
        self.X_train = None
        self.y_train = None

    def _lorentzian_distance(self, a, b):
        """Calculate Lorentzian distance between two vectors"""
        return np.sum(np.log(1 + np.abs(a - b)))

    def fit(self, X, y):
        """Store training data"""
        self.X_train = X[-self.lookback:]  # Use most recent patterns
        self.y_train = y[-self.lookback:]
        return self

    def predict(self, X):
        """Predict using Lorentzian distance"""
        if self.X_train is None:
            raise ValueError("Classifier not fitted yet")
        distances = cdist(X, self.X_train, metric=self._lorentzian_distance)
        nearest_indices = np.argsort(distances, axis=1)[:, :self.n_neighbors]
        neighbor_classes = self.y_train[nearest_indices]
        return np.sign(np.mean(neighbor_classes, axis=1))


class IndicatorCalculator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.lc_model = LorentzianClassifier(n_neighbors=5, lookback=14)

    def calculate_rsi(self, period=14):
        """Relative Strength Index (RSI) calculation"""
        delta = self.df['Close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
        avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-10)  # Avoid division by zero
        return 100 - (100 / (1 + rs))

    def calculate_cci(self, period=20):
        """Commodity Channel Index (CCI) calculation"""
        typical_price = (self.df['Close'] + self.df['High'] + self.df['Low']) / 3
        mean_typical_price = typical_price.rolling(window=period, min_periods=1).mean()
        mean_deviation = (typical_price - mean_typical_price).abs().rolling(window=period, min_periods=1).mean()
        return (typical_price - mean_typical_price) / (0.015 * mean_deviation + 1e-10)

    def calculate_adx(self, period=20):
        """Average Directional Index (ADX) calculation"""
        high_diff = self.df['High'].diff()
        low_diff = self.df['Low'].diff()
        plus_dm = pd.Series(np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0), index=self.df.index)
        minus_dm = pd.Series(np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0), index=self.df.index)
        atr = (self.df['High'] - self.df['Low']).rolling(window=period, min_periods=1).mean()
        plus_di = 100 * (plus_dm.rolling(window=period, min_periods=1).mean() / (atr + 1e-10))
        minus_di = 100 * (minus_dm.rolling(window=period, min_periods=1).mean() / (atr + 1e-10))
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        return dx.rolling(window=period, min_periods=1).mean()

    def calculate_wavetrend(self, period=10):
        """WaveTrend oscillator calculation"""
        typical_price = (self.df['Close'] + self.df['High'] + self.df['Low']) / 3
        ema1 = typical_price.ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        wt1 = ema1 - ema2
        wt2 = wt1.ewm(span=4, adjust=False).mean()
        return wt1, wt2

    def add_ml_features(self):
        """Create features for ML model (do not drop rows here)"""
        self.df['Returns'] = self.df['Close'].pct_change()
        self.df['Label'] = np.where(self.df['Returns'].shift(-1) > 0, 1, -1)
        return self.df

    def compute_ml_predictions(self):
        """Compute Lorentzian Classification predictions"""
        # Add the features (but do not drop rows yet)
        df_temp = self.add_ml_features()
        # Now drop NaNs only for the columns needed for ML
        df_clean = df_temp.dropna(subset=['Returns', 'Label', 'RSI_14', 'CCI_20', 'ADX_20', 'WT1'])
        print("Total feature rows:", len(df_clean))
        if df_clean.empty:
            print("⚠️ No valid data left after cleaning NaNs!")
            return self.df

        features = df_clean[['RSI_14', 'CCI_20', 'ADX_20', 'WT1']]
        labels = df_clean['Label']

        split_idx = int(len(features) * 0.8)
        X_train, X_test = features[:split_idx], features[split_idx:]
        y_train, y_test = labels[:split_idx], labels[split_idx:]

        if X_test.empty:
            print("⚠️ Warning: X_test is empty! No predictions will be made.")
            return self.df

        self.lc_model.fit(X_train.values, y_train.values)
        predictions = self.lc_model.predict(X_test.values)
        self.df.loc[X_test.index, 'LC_Prediction'] = predictions
        return self.df

    def compute_all_indicators(self):
        """Compute all indicators including ML predictions"""
        self.df['RSI_14'] = self.calculate_rsi(14)
        self.df['RSI_9'] = self.calculate_rsi(9)
        self.df['CCI_20'] = self.calculate_cci(20)
        self.df['ADX_20'] = self.calculate_adx(20)
        self.df['WT1'], self.df['WT2'] = self.calculate_wavetrend()
        self.compute_ml_predictions()
        return self.df

# === Testing & Execution ===

np.random.seed(42)
# Generate synthetic stock data (200 rows for a better training sample)
dates = pd.date_range(start="2024-01-01", periods=200, freq="D")
close_prices = np.cumsum(np.random.randn(200) * 2 + 100)
df = pd.DataFrame({
    'Date': dates,
    'Close': close_prices,
    'High': close_prices + np.random.rand(200) * 2,
    'Low': close_prices - np.random.rand(200) * 2
})
df.set_index('Date', inplace=True)

# Run IndicatorCalculator
indicator_calculator = IndicatorCalculator(df)
df_with_indicators = indicator_calculator.compute_all_indicators()
print(df_with_indicators.tail(10))
