import numpy as np


class DataUtilities:
    """Data processing and technical analysis utilities"""
    
    @staticmethod
    def calculate_technical_indicators(data, symbol, lookback_window=20):
        """Calculate common technical indicators"""
        prices = data.history(symbol, 'price', lookback_window, '1d')
        
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = prices.rolling(20).mean().iloc[-1]
        indicators['sma_50'] = prices.rolling(50).mean().iloc[-1] if len(prices) >= 50 else None
        indicators['ema_20'] = prices.ewm(span=20).mean().iloc[-1]
        
        # Volatility
        returns = prices.pct_change().dropna()
        indicators['volatility'] = returns.std() * np.sqrt(252)
        
        # RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
        
        return indicators
    
    @staticmethod
    def calculate_momentum_signals(data, symbol, lookback_periods=[5, 10, 20]):
        """Calculate momentum signals"""
        signals = {}
        
        for period in lookback_periods:
            prices = data.history(symbol, 'price', period + 1, '1d')
            if len(prices) > period:
                momentum = (prices.iloc[-1] / prices.iloc[0]) - 1
                signals[f'momentum_{period}d'] = momentum
        
        return signals
    
    @staticmethod
    def calculate_mean_reversion_signals(data, symbol, lookback_window=20):
        """Calculate mean reversion signals"""
        prices = data.history(symbol, 'price', lookback_window, '1d')
        
        if len(prices) < lookback_window:
            return {}
        
        mean_price = prices.mean()
        std_price = prices.std()
        current_price = prices.iloc[-1]
        
        # Z-score for mean reversion
        z_score = (current_price - mean_price) / std_price
        
        # Bollinger Bands
        upper_band = mean_price + (2 * std_price)
        lower_band = mean_price - (2 * std_price)
        
        return {
            'z_score': z_score,
            'bb_upper': upper_band,
            'bb_lower': lower_band,
            'bb_position': (current_price - lower_band) / (upper_band - lower_band)
        }
