# Strategy Maker Code Reference

## BaseStrategy Class Reference

### Class Definition

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
from zipline.assets import Asset
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies in the NSE Backtesting Engine.
    
    This class provides the foundational infrastructure for algorithmic trading
    strategies including risk management, position sizing, execution logic,
    and performance tracking.
    """
```

### Constructor

```python
def __init__(self):
    """
    Initialize the base strategy with default risk parameters and state tracking.
    
    Sets up:
    - Risk management parameters
    - Position tracking dictionaries
    - Portfolio state variables
    - Factor data storage for analysis
    - Strategy logging configuration
    """
```

### Risk Parameters

```python
self.risk_params = {
    'max_leverage': 1.0,          # Maximum portfolio leverage (1x = 100% of capital)
    'stop_loss_pct': 0.08,       # Trailing stop loss percentage (8%)
    'take_profit_pct': 0.20,      # Profit target percentage (20%)
    'max_position_size': 0.1,     # Maximum position size (10% of portfolio)
    'daily_loss_limit': -0.05,    # Daily loss circuit breaker (-5%)
    'trade_blacklist': set()      # Assets to avoid trading
}
```

### Abstract Methods (Must Implement)

#### select_universe

```python
@abstractmethod
def select_universe(self, context) -> List[Asset]:
    """
    Define the tradeable universe for the strategy.
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context containing portfolio and account information
    
    Returns:
    --------
    List[Asset]
        List of Zipline Asset objects representing tradeable securities
    
    Example:
    --------
    def select_universe(self, context):
        return [
            symbol('RELIANCE'),
            symbol('HDFCBANK'),
            symbol('INFY')
        ]
    """
    pass
```

#### generate_signals

```python
@abstractmethod
def generate_signals(self, context, data) -> Dict[Asset, float]:
    """
    Generate trading signals for each asset in the universe.
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    data : zipline.protocol.BarData
        Current and historical market data
    
    Returns:
    --------
    Dict[Asset, float]
        Dictionary mapping assets to signal strengths in range [-1.0, 1.0]
        where:
        - 1.0 = Maximum long position
        - 0.0 = No position
        - -1.0 = Maximum short position
    
    Example:
    --------
    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            # Calculate your signal logic here
            signal_value = calculate_my_signal(asset, data)
            signals[asset] = np.clip(signal_value, -1.0, 1.0)
        return signals
    """
    pass
```

### Core Methods

#### initialize

```python
def initialize(self, context):
    """
    Zipline initialization method called once at strategy start.
    
    Sets up:
    - Trading costs and slippage models
    - Rebalancing schedules
    - Universe selection
    - Initial logging
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    """
```

#### rebalance

```python
def rebalance(self, context, data):
    """
    Main trading logic orchestrator called at each rebalance interval.
    
    Workflow:
    1. Perform pre-trade risk checks
    2. Generate trading signals
    3. Execute trades with risk controls
    4. Record performance metrics
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    data : zipline.protocol.BarData
        Current market data
    """
```

### Risk Management Methods

#### _pre_trade_checks

```python
def _pre_trade_checks(self, context) -> bool:
    """
    Comprehensive pre-trade risk validation.
    
    Checks:
    - Portfolio leverage limits
    - Daily loss limits
    - Market blackout periods
    - Asset blacklist compliance
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    
    Returns:
    --------
    bool
        True if all risk checks pass, False otherwise
    """
```

#### _calculate_position_size

```python
def _calculate_position_size(self, context, data, asset, target) -> float:
    """
    Calculate position size using volatility-based risk management.
    
    Uses Van Tharp position sizing methodology:
    - Risk per trade = 1% of portfolio value
    - Stop distance = 2x ATR
    - Position size = Risk / (Stop distance × Price)
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    data : zipline.protocol.BarData
        Current market data
    asset : zipline.assets.Asset
        The asset to size
    target : float
        Target signal strength [-1.0, 1.0]
    
    Returns:
    --------
    float
        Position size as fraction of portfolio value
    """
```

#### _update_stop_losses

```python
def _update_stop_losses(self, asset, position_size, current_price):
    """
    Update trailing stop losses for active positions.
    
    Parameters:
    -----------
    asset : zipline.assets.Asset
        The asset to update stops for
    position_size : float
        Current position size
    current_price : float
        Current market price
    """
```

### Utility Methods

#### _get_atr

```python
def _get_atr(self, asset, window=20) -> float:
    """
    Calculate Average True Range for volatility measurement.
    
    Parameters:
    -----------
    asset : zipline.assets.Asset
        Asset to calculate ATR for
    window : int
        Lookback period for ATR calculation
    
    Returns:
    --------
    float
        Average True Range value
    """
```

#### _in_blackout_period

```python
def _in_blackout_period(self) -> bool:
    """
    Check if current time is in a trading blackout period.
    
    Common blackout periods:
    - FOMC meeting days
    - Earnings announcement days
    - Major economic releases
    
    Returns:
    --------
    bool
        True if in blackout period, False otherwise
    """
```

#### _record_metrics

```python
def _record_metrics(self, context):
    """
    Record strategy performance metrics for analysis.
    
    Records:
    - Portfolio value and returns
    - Position counts and concentrations
    - Risk metrics and drawdowns
    - Factor exposures for Alphalens
    
    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        The Zipline algorithm context
    """
```

## TechnicalIndicators Class Reference

### Trend Indicators

#### calculate_sma

```python
@staticmethod
def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average.
    
    Parameters:
    -----------
    prices : pd.Series
        Price series
    window : int
        Moving average window
    
    Returns:
    --------
    pd.Series
        Simple moving average values
    """
```

#### calculate_ema

```python
@staticmethod
def calculate_ema(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Parameters:
    -----------
    prices : pd.Series
        Price series
    window : int
        EMA window (span)
    
    Returns:
    --------
    pd.Series
        Exponential moving average values
    """
```

#### calculate_macd

```python
@staticmethod
def calculate_macd(prices: pd.Series, fast=12, slow=26, signal=9) -> Dict[str, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Parameters:
    -----------
    prices : pd.Series
        Price series
    fast : int
        Fast EMA period
    slow : int
        Slow EMA period
    signal : int
        Signal line EMA period
    
    Returns:
    --------
    Dict[str, pd.Series]
        Dictionary containing 'macd', 'signal', and 'histogram' series
    """
```

### Momentum Indicators

#### calculate_rsi

```python
@staticmethod
def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index.
    
    Parameters:
    -----------
    prices : pd.Series
        Price series
    window : int
        RSI calculation window
    
    Returns:
    --------
    pd.Series
        RSI values (0-100 scale)
    """
```

#### calculate_stochastic

```python
@staticmethod
def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
    """
    Calculate Stochastic Oscillator.
    
    Parameters:
    -----------
    high : pd.Series
        High price series
    low : pd.Series
        Low price series
    close : pd.Series
        Close price series
    k_window : int
        %K calculation window
    d_window : int
        %D smoothing window
    
    Returns:
    --------
    Dict[str, pd.Series]
        Dictionary containing '%K' and '%D' series
    """
```

### Volatility Indicators

#### calculate_atr

```python
@staticmethod
def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                 window: int = 14) -> pd.Series:
    """
    Calculate Average True Range.
    
    Parameters:
    -----------
    high : pd.Series
        High price series
    low : pd.Series
        Low price series
    close : pd.Series
        Close price series
    window : int
        ATR calculation window
    
    Returns:
    --------
    pd.Series
        Average True Range values
    """
```

#### calculate_bollinger_bands

```python
@staticmethod
def calculate_bollinger_bands(prices: pd.Series, window: int = 20, 
                            num_std: float = 2.0) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Parameters:
    -----------
    prices : pd.Series
        Price series
    window : int
        Moving average window
    num_std : float
        Number of standard deviations for bands
    
    Returns:
    --------
    Dict[str, pd.Series]
        Dictionary containing 'upper', 'middle', and 'lower' band series
    """
```

## RiskMetrics Class Reference

### Risk-Adjusted Returns

#### calculate_sharpe_ratio

```python
@staticmethod
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for risk-adjusted performance.
    
    Parameters:
    -----------
    returns : pd.Series
        Return series
    risk_free_rate : float
        Annual risk-free rate
    
    Returns:
    --------
    float
        Sharpe ratio
    """
```

#### calculate_sortino_ratio

```python
@staticmethod
def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0.0) -> float:
    """
    Calculate Sortino ratio focusing on downside risk.
    
    Parameters:
    -----------
    returns : pd.Series
        Return series
    target_return : float
        Target return threshold
    
    Returns:
    --------
    float
        Sortino ratio
    """
```

### Drawdown Analysis

#### calculate_max_drawdown

```python
@staticmethod
def calculate_max_drawdown(returns: pd.Series) -> Dict[str, Union[float, pd.Timestamp]]:
    """
    Calculate maximum drawdown and related metrics.
    
    Parameters:
    -----------
    returns : pd.Series
        Return series
    
    Returns:
    --------
    Dict[str, Union[float, pd.Timestamp]]
        Dictionary containing max_drawdown, start_date, end_date, recovery_date
    """
```

## PortfolioOptimization Class Reference

### Mean Variance Optimization

#### calculate_optimal_weights

```python
@staticmethod
def calculate_optimal_weights(returns: pd.DataFrame, method: str = 'mean_variance') -> pd.Series:
    """
    Calculate optimal portfolio weights using specified method.
    
    Parameters:
    -----------
    returns : pd.DataFrame
        Asset return matrix
    method : str
        Optimization method ('mean_variance', 'risk_parity', 'minimum_variance')
    
    Returns:
    --------
    pd.Series
        Optimal portfolio weights
    """
```

### Risk Parity

#### _risk_parity_optimization

```python
@staticmethod
def _risk_parity_optimization(returns: pd.DataFrame) -> pd.Series:
    """
    Calculate risk parity portfolio weights.
    
    Parameters:
    -----------
    returns : pd.DataFrame
        Asset return matrix
    
    Returns:
    --------
    pd.Series
        Risk parity weights
    """
```
