# API Reference Documentation

## Overview

This document provides detailed API reference for all classes, methods, and functions in the NSE Backtesting Engine. Use this as a comprehensive reference when developing trading strategies.

## Table of Contents

1. [BaseStrategy Class](#basestrategy-class)
2. [EnhancedZiplineRunner Class](#enhancedziplinerunner-class)
3. [Utility Functions](#utility-functions)
4. [Constants & Enums](#constants--enums)
5. [Data Structures](#data-structures)

## BaseStrategy Class

### Class Definition

```python
class BaseStrategy:
    """
    Base class for all trading strategies in the NSE Backtesting Engine.
    Provides comprehensive risk management, logging, and integration with Zipline.
    """
```

### Constructor

#### `__init__(self)`

**Description**: Initialize the base strategy with default risk parameters and logging.

**Parameters**: None

**Attributes Initialized**:
- `risk_params`: Dictionary of risk management parameters
- `signals`: Dictionary to store current signals
- `positions`: Dictionary to track position information
- `portfolio`: Dictionary for portfolio state tracking
- `factor_data`: Storage for factor data
- `recorded_factors`: Dictionary of recorded factors

**Example**:
```python
class MyStrategy(BaseStrategy):
    def __init__(self, custom_param=10):
        super().__init__()
        self.custom_param = custom_param
        
        # Customize risk parameters
        self.risk_params.update({
            'max_position_size': 0.15,
            'stop_loss_pct': 0.08
        })
```

### Abstract Methods (Must Implement)

#### `select_universe(self, context)`

**Description**: Define the trading universe (assets to trade).

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context object

**Returns**: `List[zipline.assets.Asset]` - List of assets to trade

**Example**:
```python
def select_universe(self, context):
    nse_symbols = ['SBIN', 'RELIANCE', 'TCS']
    return [symbol(sym) for sym in nse_symbols]
```

#### `generate_signals(self, context, data)`

**Description**: Generate trading signals for each asset in the universe.

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context object
- `data` (zipline.protocol.BarData): Market data interface

**Returns**: `Dict[Asset, float]` - Dictionary mapping assets to signal strengths (-1 to 1)

**Signal Strength Guidelines**:
- `1.0`: Strong buy signal
- `0.5`: Moderate buy signal
- `0.0`: No signal/neutral
- `-0.5`: Moderate sell signal
- `-1.0`: Strong sell signal

**Example**:
```python
def generate_signals(self, context, data):
    signals = {}
    for asset in context.universe:
        prices = data.history(asset, 'price', 20, '1d')
        signal = self.calculate_my_signal(prices)
        signals[asset] = max(-1.0, min(1.0, signal))  # Normalize
    return signals
```

### Utility Methods

#### `record_factor(self, factor_name, factor_value, context=None)`

**Description**: Record factor data for Alphalens analysis.

**Parameters**:
- `factor_name` (str): Name of the factor
- `factor_value` (float): Current factor value
- `context` (zipline.TradingAlgorithm, optional): Zipline context

**Returns**: None

**Example**:
```python
def generate_signals(self, context, data):
    for asset in context.universe:
        momentum = self.calculate_momentum(asset, data)
        self.record_factor('momentum', momentum, context)
        # ... rest of signal logic
```

#### `_calculate_position_size(self, context, data, asset, target_weight)`

**Description**: Calculate position size based on risk parameters and current portfolio state.

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context
- `data` (zipline.protocol.BarData): Market data
- `asset` (zipline.assets.Asset): Asset to calculate position for
- `target_weight` (float): Target weight from signal

**Returns**: `float` - Position size as fraction of portfolio

**Override Example**:
```python
def _calculate_position_size(self, context, data, asset, target_weight):
    base_size = super()._calculate_position_size(context, data, asset, target_weight)
    
    # Custom volatility adjustment
    prices = data.history(asset, 'price', 20, '1d')
    volatility = prices.pct_change().std() * (252 ** 0.5)
    vol_adjustment = min(1.0, 0.20 / volatility)
    
    return base_size * vol_adjustment
```

### Lifecycle Methods (Automatically Called)

#### `initialize(self, context)`

**Description**: Initialize strategy when backtest starts.

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context

**Called**: Once at the beginning of backtest

**Default Behavior**:
- Sets up trading universe
- Configures trading costs
- Schedules rebalancing and recording

#### `rebalance(self, context, data)`

**Description**: Execute portfolio rebalancing based on current signals.

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context
- `data` (zipline.protocol.BarData): Market data

**Called**: At scheduled rebalancing intervals (default: daily)

**Default Behavior**:
- Generates signals using `generate_signals()`
- Calculates position sizes
- Places orders
- Updates position tracking

#### `record_vars(self, context, data)`

**Description**: Record variables for analysis and monitoring.

**Parameters**:
- `context` (zipline.TradingAlgorithm): Zipline context
- `data` (zipline.protocol.BarData): Market data

**Called**: Daily (after market close)

**Default Behavior**:
- Records portfolio metrics
- Records custom variables
- Updates performance tracking

### Risk Parameters

#### Default Risk Parameters

```python
self.risk_params = {
    'max_leverage': 1.0,           # Maximum portfolio leverage
    'stop_loss_pct': 0.05,         # Stop loss percentage (5%)
    'take_profit_pct': 0.10,       # Take profit percentage (10%)
    'max_position_size': 0.10,     # Maximum position size (10%)
    'daily_loss_limit': -0.05,     # Daily loss limit (-5%)
    'trade_blacklist': set()       # Blacklisted assets
}
```

#### Risk Parameter Descriptions

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `max_leverage` | float | Maximum portfolio leverage | 1.0 |
| `stop_loss_pct` | float | Stop loss threshold (0-1) | 0.05 |
| `take_profit_pct` | float | Take profit threshold (0-1) | 0.10 |
| `max_position_size` | float | Max position as fraction of portfolio | 0.10 |
| `daily_loss_limit` | float | Daily loss circuit breaker | -0.05 |
| `trade_blacklist` | set | Assets to avoid trading | empty set |

## EnhancedZiplineRunner Class

### Class Definition

```python
class EnhancedZiplineRunner:
    """
    Enhanced wrapper around Zipline with comprehensive logging,
    analysis, and integration with Pyfolio and Alphalens.
    """
```

### Constructor

#### `__init__(self, strategy, bundle, start_date, end_date, **kwargs)`

**Description**: Initialize the runner with strategy and configuration.

**Parameters**:
- `strategy` (BaseStrategy): Trading strategy instance
- `bundle` (str): Data bundle name
- `start_date` (str|datetime): Backtest start date
- `end_date` (str|datetime): Backtest end date

**Optional Parameters**:
- `capital_base` (float): Starting capital (default: 100000)
- `benchmark_symbol` (str): Benchmark asset symbol (default: None)
- `data_frequency` (str): 'minute' or 'daily' (default: 'minute')
- `trading_calendar` (str): Trading calendar name (default: 'XBOM')

**Example**:
```python
runner = EnhancedZiplineRunner(
    strategy=MyStrategy(),
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2023-01-01',
    capital_base=100000,
    benchmark_symbol='SBIN'
)
```

### Core Methods

#### `run(self)`

**Description**: Execute the backtest.

**Parameters**: None

**Returns**: `zipline.utils.run_algo.BacktestResult` - Zipline backtest results

**Raises**:
- `ValueError`: Invalid configuration parameters
- `Exception`: Various execution errors

**Example**:
```python
try:
    results = runner.run()
    print(f"Final portfolio value: {results.portfolio_value.iloc[-1]}")
except Exception as e:
    print(f"Backtest failed: {e}")
```

#### `analyze(self, results_dir)`

**Description**: Perform comprehensive analysis of backtest results.

**Parameters**:
- `results_dir` (str): Directory to save analysis results

**Returns**: None

**Creates**:
- Pyfolio tear sheets (PNG files)
- CSV exports (results, trades, orders)
- Performance statistics (TXT file)
- Alphalens analysis (if factor data available)

**Example**:
```python
import os
results_dir = 'backtest_results/my_strategy'
os.makedirs(results_dir, exist_ok=True)
runner.analyze(results_dir)
```

#### `create_enhanced_pyfolio_analysis(self, results_dir, live_start_date=None, save_plots=True, save_csv=True)`

**Description**: Create enhanced Pyfolio analysis with comprehensive CSV export and plot saving.

**Parameters**:
- `results_dir` (str): Directory to save analysis results
- `live_start_date` (str|datetime, optional): Date when live trading started for out-of-sample analysis
- `save_plots` (bool): Whether to save plots as PNG files (default: True)
- `save_csv` (bool): Whether to save comprehensive CSV data (default: True)

**Returns**: None

**Creates**:
- Enhanced Pyfolio tear sheet (PNG)
- Performance statistics (CSV)
- Returns series (CSV)
- Risk metrics (CSV)
- Rolling performance metrics (CSV)
- Monthly/annual returns (CSV)
- Drawdown analysis (CSV)
- Round trips analysis (CSV, if transactions available)
- Underwater drawdown data (CSV)
- Rolling Sharpe ratio (CSV)

**Example**:
```python
# Basic enhanced analysis
runner.create_enhanced_pyfolio_analysis('results')

# With out-of-sample analysis
runner.create_enhanced_pyfolio_analysis(
    results_dir='results',
    live_start_date='2020-01-01',  # Out-of-sample period
    save_plots=True,
    save_csv=True
)
```

### Internal Methods

#### `_setup_algorithm(self, strategy)`

**Description**: Configure Zipline algorithm with strategy.

**Parameters**:
- `strategy` (BaseStrategy): Strategy to configure

**Returns**: Configured algorithm function

**Note**: Internal method, not typically called directly.

#### `_create_basic_analysis(self, results_dir)`

**Description**: Create basic performance charts when Pyfolio fails.

**Parameters**:
- `results_dir` (str): Directory for output files

**Returns**: None

**Note**: Fallback analysis method.

## Utility Functions

### Data Access Helpers

#### `get_safe_history(data, asset, field, periods, frequency)`

**Description**: Safely access historical data with error handling.

**Parameters**:
- `data` (zipline.protocol.BarData): Market data interface
- `asset` (zipline.assets.Asset): Asset to get data for
- `field` (str): Data field ('price', 'volume', etc.)
- `periods` (int): Number of periods
- `frequency` (str): Data frequency ('1d', '1m', etc.)

**Returns**: `pandas.Series` or `None` if data unavailable

**Example**:
```python
def calculate_signal(self, asset, data):
    prices = get_safe_history(data, asset, 'price', 20, '1d')
    if prices is None:
        return 0.0
    return self.my_calculation(prices)
```

### Technical Indicators

#### `calculate_sma(prices, window)`

**Description**: Calculate Simple Moving Average.

**Parameters**:
- `prices` (pandas.Series): Price series
- `window` (int): Moving average window

**Returns**: `float` - Current SMA value

#### `calculate_rsi(prices, period=14)`

**Description**: Calculate Relative Strength Index.

**Parameters**:
- `prices` (pandas.Series): Price series
- `period` (int): RSI calculation period

**Returns**: `float` - Current RSI value (0-100)

#### `calculate_bollinger_bands(prices, window=20, num_std=2)`

**Description**: Calculate Bollinger Bands.

**Parameters**:
- `prices` (pandas.Series): Price series
- `window` (int): Moving average window
- `num_std` (float): Number of standard deviations

**Returns**: `tuple` - (middle_band, upper_band, lower_band)

## Constants & Enums

### Signal Constants

```python
STRONG_BUY = 1.0
MODERATE_BUY = 0.5
NEUTRAL = 0.0
MODERATE_SELL = -0.5
STRONG_SELL = -1.0
```

### Risk Management Constants

```python
DEFAULT_MAX_LEVERAGE = 1.0
DEFAULT_STOP_LOSS = 0.05
DEFAULT_TAKE_PROFIT = 0.10
DEFAULT_MAX_POSITION = 0.10
```

### Data Frequency Constants

```python
MINUTE_DATA = 'minute'
DAILY_DATA = 'daily'
```

## Data Structures

### Signal Dictionary

```python
signals = {
    Asset('SBIN'): 0.8,      # Strong buy
    Asset('RELIANCE'): -0.3,  # Weak sell
    Asset('TCS'): 0.0         # Neutral
}
```

### Risk Parameters Dictionary

```python
risk_params = {
    'max_leverage': 1.0,
    'stop_loss_pct': 0.05,
    'take_profit_pct': 0.10,
    'max_position_size': 0.10,
    'daily_loss_limit': -0.05,
    'trade_blacklist': {'BADSTOCK'}
}
```

### Portfolio State Dictionary

```python
portfolio_state = {
    'peak_value': 125000.0,
    'daily_pnl': 2500.0,
    'current_positions': {
        Asset('SBIN'): {
            'entry_price': 450.0,
            'stop_loss': 427.5,
            'take_profit': 495.0
        }
    }
}
```

## Error Handling

### Common Exceptions

#### `StrategyError`

**Description**: Raised when strategy implementation is invalid.

**Common Causes**:
- Missing required methods
- Invalid signal values
- Configuration errors

#### `DataError`

**Description**: Raised when data access fails.

**Common Causes**:
- Bundle not found
- Date range issues
- Missing asset data

#### `RiskError`

**Description**: Raised when risk limits are violated.

**Common Causes**:
- Excessive leverage
- Position size violations
- Daily loss limits exceeded

### Error Handling Example

```python
try:
    results = runner.run()
except StrategyError as e:
    print(f"Strategy implementation error: {e}")
except DataError as e:
    print(f"Data access error: {e}")
except RiskError as e:
    print(f"Risk management error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Memory Usage

- Use `del` to clean up large data structures
- Limit historical data lookback periods
- Consider using daily data for long backtests

### Execution Speed

- Batch data access when possible
- Cache expensive calculations
- Minimize loops in signal generation

### Best Practices

1. **Always validate inputs** before processing
2. **Handle missing data gracefully**
3. **Use appropriate data types** (float64 for prices)
4. **Implement proper error handling**
5. **Document your custom methods**

## Version Information

- **Engine Version**: 1.0.0
- **Zipline Version**: Compatible with Zipline 1.4+
- **Python Version**: Requires Python 3.7+
- **Dependencies**: pandas, numpy, matplotlib, pyfolio, alphalens

For more information, see:
- [BaseStrategy Documentation](./BaseStrategy.md)
- [ZiplineRunner Documentation](./ZiplineRunner.md)
- [Strategy Writing Guide](./StrategyWritingGuide.md)
