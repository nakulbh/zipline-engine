"""
Comprehensive Strategy Utilities
This module provides advanced utilities for strategy development including:
- Technical indicators
- Risk management tools
- Signal processing
- Market regime detection
- Portfolio optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings

# Technical analysis
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    warnings.warn("TA-Lib not available. Using custom implementations.")

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Advanced technical indicators"""
    
    @staticmethod
    def calculate_comprehensive_indicators(prices: pd.Series, volumes: Optional[pd.Series] = None) -> Dict:
        """Calculate comprehensive technical indicators"""
        indicators = {}
        
        # Price-based indicators
        if TALIB_AVAILABLE:
            # Use TA-Lib for better performance
            indicators.update(TechnicalIndicators._calculate_talib_indicators(prices, volumes))
        else:
            # Use custom implementations
            indicators.update(TechnicalIndicators._calculate_custom_indicators(prices, volumes))
        
        return indicators
    
    @staticmethod
    def _calculate_talib_indicators(prices: pd.Series, volumes: Optional[pd.Series] = None) -> Dict:
        """Calculate indicators using TA-Lib"""
        indicators = {}
        price_array = prices.values
        
        # Trend indicators
        indicators['sma_20'] = talib.SMA(price_array, timeperiod=20)[-1]
        indicators['sma_50'] = talib.SMA(price_array, timeperiod=50)[-1]
        indicators['ema_20'] = talib.EMA(price_array, timeperiod=20)[-1]
        indicators['ema_50'] = talib.EMA(price_array, timeperiod=50)[-1]
        
        # Momentum indicators
        indicators['rsi'] = talib.RSI(price_array, timeperiod=14)[-1]
        indicators['macd'], indicators['macd_signal'], indicators['macd_hist'] = talib.MACD(price_array)
        indicators['macd'] = indicators['macd'][-1]
        indicators['macd_signal'] = indicators['macd_signal'][-1]
        indicators['macd_hist'] = indicators['macd_hist'][-1]
        
        # Volatility indicators
        indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = talib.BBANDS(price_array)
        indicators['bb_upper'] = indicators['bb_upper'][-1]
        indicators['bb_middle'] = indicators['bb_middle'][-1]
        indicators['bb_lower'] = indicators['bb_lower'][-1]
        
        indicators['atr'] = talib.ATR(price_array, price_array, price_array, timeperiod=14)[-1]
        
        # Volume indicators (if available)
        if volumes is not None:
            volume_array = volumes.values
            indicators['ad'] = talib.AD(price_array, price_array, price_array, volume_array)[-1]
            indicators['obv'] = talib.OBV(price_array, volume_array)[-1]
        
        return indicators
    
    @staticmethod
    def _calculate_custom_indicators(prices: pd.Series, volumes: Optional[pd.Series] = None) -> Dict:
        """Calculate indicators using custom implementations"""
        indicators = {}
        
        # Trend indicators
        indicators['sma_20'] = prices.rolling(20).mean().iloc[-1]
        indicators['sma_50'] = prices.rolling(50).mean().iloc[-1]
        indicators['ema_20'] = prices.ewm(span=20).mean().iloc[-1]
        indicators['ema_50'] = prices.ewm(span=50).mean().iloc[-1]
        
        # RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
        
        # MACD
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        indicators['macd'] = macd.iloc[-1]
        indicators['macd_signal'] = macd_signal.iloc[-1]
        indicators['macd_hist'] = (macd - macd_signal).iloc[-1]
        
        # Bollinger Bands
        sma_20 = prices.rolling(20).mean()
        std_20 = prices.rolling(20).std()
        indicators['bb_upper'] = (sma_20 + 2 * std_20).iloc[-1]
        indicators['bb_middle'] = sma_20.iloc[-1]
        indicators['bb_lower'] = (sma_20 - 2 * std_20).iloc[-1]
        
        # ATR approximation
        high_low = prices.rolling(2).max() - prices.rolling(2).min()
        indicators['atr'] = high_low.rolling(14).mean().iloc[-1]
        
        return indicators
    
    @staticmethod
    def calculate_momentum_indicators(prices: pd.Series, periods: List[int] = [5, 10, 20, 50]) -> Dict:
        """Calculate momentum indicators for multiple periods"""
        momentum = {}
        
        for period in periods:
            if len(prices) > period:
                momentum[f'momentum_{period}d'] = (prices.iloc[-1] / prices.iloc[-period-1]) - 1
                momentum[f'roc_{period}d'] = (prices.iloc[-1] - prices.iloc[-period-1]) / prices.iloc[-period-1]
        
        return momentum
    
    @staticmethod
    def calculate_volatility_indicators(prices: pd.Series, returns: pd.Series) -> Dict:
        """Calculate volatility indicators"""
        volatility = {}
        
        # Realized volatility
        volatility['realized_vol'] = returns.std() * np.sqrt(252)
        
        # GARCH-like volatility
        volatility['ewm_vol'] = returns.ewm(span=30).std() * np.sqrt(252)
        
        # Rolling volatility
        volatility['rolling_vol_30d'] = returns.rolling(30).std() * np.sqrt(252)
        
        # Parkinson volatility (high-low based)
        if len(prices) > 1:
            high_low_ratio = np.log(prices.rolling(2).max() / prices.rolling(2).min())
            volatility['parkinson_vol'] = np.sqrt(high_low_ratio.rolling(30).var() * 252 / (4 * np.log(2)))
        
        return volatility


class RiskMetrics:
    """Advanced risk management metrics"""
    
    @staticmethod
    def calculate_value_at_risk(returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Value at Risk"""
        if len(returns) == 0:
            return 0.0
        return np.percentile(returns.dropna(), confidence_level * 100)
    
    @staticmethod
    def calculate_conditional_var(returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = RiskMetrics.calculate_value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def calculate_maximum_drawdown(returns: pd.Series) -> Dict:
        """Calculate detailed maximum drawdown metrics"""
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.cummax()
        drawdown = cum_returns / running_max - 1
        
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        # Find the peak before the maximum drawdown
        peak_idx = cum_returns.loc[:max_dd_idx].idxmax()
        
        # Find the recovery point
        recovery_idx = None
        if max_dd_idx < cum_returns.index[-1]:
            recovery_series = cum_returns.loc[max_dd_idx:]
            recovery_candidates = recovery_series[recovery_series >= cum_returns.loc[peak_idx]]
            if len(recovery_candidates) > 0:
                recovery_idx = recovery_candidates.index[0]
        
        return {
            'max_drawdown': max_dd,
            'max_drawdown_date': max_dd_idx,
            'peak_date': peak_idx,
            'recovery_date': recovery_idx,
            'drawdown_duration': (max_dd_idx - peak_idx).days if isinstance(max_dd_idx, pd.Timestamp) else None,
            'recovery_duration': (recovery_idx - max_dd_idx).days if recovery_idx and isinstance(recovery_idx, pd.Timestamp) else None
        }
    
    @staticmethod
    def calculate_risk_adjusted_metrics(returns: pd.Series, risk_free_rate: float = 0.02) -> Dict:
        """Calculate comprehensive risk-adjusted metrics"""
        if len(returns) == 0:
            return {}
        
        annual_returns = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        
        metrics = {
            'sharpe_ratio': (annual_returns - risk_free_rate) / annual_vol if annual_vol != 0 else 0,
            'sortino_ratio': (annual_returns - risk_free_rate) / (returns[returns < 0].std() * np.sqrt(252)) if len(returns[returns < 0]) > 0 else 0,
            'calmar_ratio': annual_returns / abs(RiskMetrics.calculate_maximum_drawdown(returns)['max_drawdown']) if RiskMetrics.calculate_maximum_drawdown(returns)['max_drawdown'] != 0 else 0,
            'var_95': RiskMetrics.calculate_value_at_risk(returns, 0.05),
            'cvar_95': RiskMetrics.calculate_conditional_var(returns, 0.05),
            'skewness': stats.skew(returns.dropna()),
            'kurtosis': stats.kurtosis(returns.dropna()),
            'downside_deviation': returns[returns < 0].std() * np.sqrt(252)
        }
        
        return metrics


class SignalProcessing:
    """Advanced signal processing utilities"""
    
    @staticmethod
    def apply_signal_filters(signals: pd.Series, filter_type: str = 'ema', window: int = 5) -> pd.Series:
        """Apply filters to reduce signal noise"""
        if filter_type == 'ema':
            return signals.ewm(span=window).mean()
        elif filter_type == 'sma':
            return signals.rolling(window).mean()
        elif filter_type == 'median':
            return signals.rolling(window).median()
        else:
            return signals
    
    @staticmethod
    def calculate_signal_strength(signals: pd.Series, method: str = 'z_score') -> pd.Series:
        """Calculate signal strength using various methods"""
        if method == 'z_score':
            return (signals - signals.mean()) / signals.std()
        elif method == 'percentile':
            return signals.rank(pct=True)
        elif method == 'minmax':
            return (signals - signals.min()) / (signals.max() - signals.min())
        else:
            return signals
    
    @staticmethod
    def detect_regime_changes(prices: pd.Series, window: int = 50) -> pd.Series:
        """Detect market regime changes"""
        returns = prices.pct_change().dropna()
        
        # Calculate rolling statistics
        rolling_mean = returns.rolling(window).mean()
        rolling_std = returns.rolling(window).std()
        
        # Identify regime changes based on volatility clusters
        volatility_threshold = rolling_std.quantile(0.75)
        high_vol_regime = rolling_std > volatility_threshold
        
        return high_vol_regime.astype(int)
    
    @staticmethod
    def calculate_signal_correlation(signals_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """Calculate correlation matrix of signals"""
        signals_df = pd.DataFrame(signals_dict)
        return signals_df.corr()


class PortfolioOptimization:
    """Portfolio optimization utilities"""
    
    @staticmethod
    def calculate_optimal_weights(returns: pd.DataFrame, method: str = 'mean_variance') -> pd.Series:
        """Calculate optimal portfolio weights"""
        if method == 'mean_variance':
            return PortfolioOptimization._mean_variance_optimization(returns)
        elif method == 'risk_parity':
            return PortfolioOptimization._risk_parity_optimization(returns)
        elif method == 'minimum_variance':
            return PortfolioOptimization._minimum_variance_optimization(returns)
        else:
            # Equal weights
            return pd.Series(1/len(returns.columns), index=returns.columns)
    
    @staticmethod
    def _mean_variance_optimization(returns: pd.DataFrame) -> pd.Series:
        """Mean-variance optimization (simplified)"""
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # Inverse covariance matrix
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            ones = np.ones(len(mean_returns))
            
            # Tangency portfolio weights
            weights = inv_cov @ mean_returns
            weights = weights / weights.sum()
            
            return pd.Series(weights, index=returns.columns)
        except np.linalg.LinAlgError:
            # Fallback to equal weights
            return pd.Series(1/len(returns.columns), index=returns.columns)
    
    @staticmethod
    def _risk_parity_optimization(returns: pd.DataFrame) -> pd.Series:
        """Risk parity optimization (simplified)"""
        # Use inverse volatility weighting as approximation
        volatilities = returns.std()
        inv_vol_weights = 1 / volatilities
        weights = inv_vol_weights / inv_vol_weights.sum()
        
        return weights
    
    @staticmethod
    def _minimum_variance_optimization(returns: pd.DataFrame) -> pd.Series:
        """Minimum variance optimization"""
        cov_matrix = returns.cov()
        
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            ones = np.ones(len(returns.columns))
            
            weights = inv_cov @ ones
            weights = weights / weights.sum()
            
            return pd.Series(weights, index=returns.columns)
        except np.linalg.LinAlgError:
            # Fallback to equal weights
            return pd.Series(1/len(returns.columns), index=returns.columns)


class MarketRegimeDetector:
    """Market regime detection utilities"""
    
    @staticmethod
    def detect_trend_regime(prices: pd.Series, window: int = 20) -> pd.Series:
        """Detect trend regime (trending vs. ranging)"""
        returns = prices.pct_change().dropna()
        
        # Calculate trend strength using ADX-like measure
        price_changes = prices.diff()
        rolling_std = price_changes.rolling(window).std()
        rolling_mean = price_changes.rolling(window).mean()
        
        trend_strength = abs(rolling_mean) / rolling_std
        
        # Classify regime
        trend_threshold = trend_strength.quantile(0.6)
        regime = (trend_strength > trend_threshold).astype(int)
        
        return regime
    
    @staticmethod
    def detect_volatility_regime(returns: pd.Series, window: int = 30) -> pd.Series:
        """Detect volatility regime (low vs. high volatility)"""
        rolling_vol = returns.rolling(window).std()
        
        vol_threshold = rolling_vol.quantile(0.7)
        high_vol_regime = (rolling_vol > vol_threshold).astype(int)
        
        return high_vol_regime
    
    @staticmethod
    def detect_momentum_regime(prices: pd.Series, window: int = 20) -> pd.Series:
        """Detect momentum regime"""
        momentum = (prices / prices.shift(window)) - 1
        
        # Positive momentum regime
        momentum_regime = (momentum > 0).astype(int)
        
        return momentum_regime


class AdvancedDataUtils:
    """Advanced data processing utilities"""
    
    @staticmethod
    def clean_price_data(prices: pd.Series, max_change: float = 0.2) -> pd.Series:
        """Clean price data by removing outliers"""
        returns = prices.pct_change()
        
        # Remove extreme price changes
        mask = abs(returns) > max_change
        cleaned_prices = prices.copy()
        cleaned_prices[mask] = np.nan
        
        # Forward fill missing values
        cleaned_prices = cleaned_prices.fillna(method='ffill')
        
        return cleaned_prices
    
    @staticmethod
    def calculate_factor_scores(data: pd.DataFrame, factors: List[str]) -> pd.DataFrame:
        """Calculate factor scores using PCA"""
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data[factors])
        
        # Apply PCA
        pca = PCA(n_components=min(len(factors), 3))
        factor_scores = pca.fit_transform(scaled_data)
        
        # Create DataFrame
        factor_df = pd.DataFrame(
            factor_scores,
            index=data.index,
            columns=[f'Factor_{i+1}' for i in range(factor_scores.shape[1])]
        )
        
        return factor_df
    
    @staticmethod
    def calculate_rolling_correlations(data: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """Calculate rolling correlations between assets"""
        correlations = {}
        
        for i, col1 in enumerate(data.columns):
            for j, col2 in enumerate(data.columns):
                if i < j:  # Avoid duplicate pairs
                    corr_key = f"{col1}_{col2}"
                    correlations[corr_key] = data[col1].rolling(window).corr(data[col2])
        
        return pd.DataFrame(correlations)
    
    @staticmethod
    def detect_structural_breaks(prices: pd.Series, window: int = 50) -> pd.Series:
        """Detect structural breaks in price series"""
        returns = prices.pct_change().dropna()
        
        # Calculate rolling statistics
        rolling_mean = returns.rolling(window).mean()
        rolling_std = returns.rolling(window).std()
        
        # Detect breaks using CUSUM-like statistic
        cumulative_deviation = (returns - rolling_mean.shift(1)).cumsum()
        normalized_cusum = cumulative_deviation / rolling_std.shift(1)
        
        # Identify structural breaks
        break_threshold = 2.0
        breaks = abs(normalized_cusum) > break_threshold
        
        return breaks.astype(int)


# Utility functions for easy access
def get_technical_indicators(prices: pd.Series, volumes: Optional[pd.Series] = None) -> Dict:
    """Get comprehensive technical indicators"""
    return TechnicalIndicators.calculate_comprehensive_indicators(prices, volumes)


def get_risk_metrics(returns: pd.Series) -> Dict:
    """Get comprehensive risk metrics"""
    return RiskMetrics.calculate_risk_adjusted_metrics(returns)


def optimize_portfolio(returns: pd.DataFrame, method: str = 'mean_variance') -> pd.Series:
    """Optimize portfolio weights"""
    return PortfolioOptimization.calculate_optimal_weights(returns, method)


def detect_market_regime(prices: pd.Series, regime_type: str = 'trend') -> pd.Series:
    """Detect market regime"""
    if regime_type == 'trend':
        return MarketRegimeDetector.detect_trend_regime(prices)
    elif regime_type == 'volatility':
        returns = prices.pct_change().dropna()
        return MarketRegimeDetector.detect_volatility_regime(returns)
    elif regime_type == 'momentum':
        return MarketRegimeDetector.detect_momentum_regime(prices)
    else:
        raise ValueError("Invalid regime type. Choose from 'trend', 'volatility', 'momentum'")


# Example usage and testing
if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0, 0.02, 252)), index=dates)
    returns = prices.pct_change().dropna()
    
    print("Testing Technical Indicators:")
    indicators = get_technical_indicators(prices)
    for key, value in indicators.items():
        print(f"{key}: {value:.4f}")
    
    print("\nTesting Risk Metrics:")
    risk_metrics = get_risk_metrics(returns)
    for key, value in risk_metrics.items():
        print(f"{key}: {value:.4f}")
    
    print("\nTesting Market Regime Detection:")
    trend_regime = detect_market_regime(prices, 'trend')
    vol_regime = detect_market_regime(prices, 'volatility')
    momentum_regime = detect_market_regime(prices, 'momentum')
    
    print(f"Trend regime changes: {trend_regime.diff().abs().sum()}")
    print(f"Volatility regime changes: {vol_regime.diff().abs().sum()}")
    print(f"Momentum regime changes: {momentum_regime.diff().abs().sum()}")
