# BaseStrategy Documentation

## Overview

The `BaseStrategy` class is the foundation for all trading strategies in the NSE Backtesting Engine. It provides a comprehensive framework with built-in risk management, logging, position management, and integration with Zipline's algorithmic trading platform.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Features](#core-features)
3. [Risk Management](#risk-management)
4. [Usage Guide](#usage-guide)
5. [Method Reference](#method-reference)
6. [Examples](#examples)

## Architecture

The `BaseStrategy` class follows a template method pattern where:
- **Base class** provides common functionality (risk management, logging, execution)
- **Derived classes** implement strategy-specific logic (`generate_signals`, `select_universe`)

```python
from engine.enhanced_base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def select_universe(self, context):
        # Define your trading universe
        pass
    
    def generate_signals(self, context, data):
        # Generate trading signals
        pass
```

## Core Features

### 1. **Automated Risk Management**
- **Position Sizing**: Automatic calculation based on portfolio size and risk parameters
- **Stop Loss**: Configurable stop-loss levels with automatic execution
- **Take Profit**: Profit-taking levels with automatic position closure
- **Leverage Control**: Maximum leverage limits to prevent over-exposure
- **Daily Loss Limits**: Circuit breakers to halt trading on excessive losses

### 2. **Comprehensive Logging**
- **Strategy-level logging**: Detailed execution logs with timestamps
- **Trade logging**: Every order and execution logged with context
- **Performance tracking**: Real-time portfolio metrics and statistics
- **Error handling**: Graceful error handling with detailed error logs

### 3. **Position Management**
- **Portfolio tracking**: Real-time position and portfolio value monitoring
- **Order management**: Intelligent order placement and execution
- **Rebalancing**: Automatic portfolio rebalancing based on signals
- **Cash management**: Efficient cash allocation and margin management

### 4. **Factor Recording**
- **Alphalens Integration**: Built-in factor recording for quantitative analysis
- **Custom factors**: Easy recording of custom factors and indicators
- **Performance attribution**: Track factor performance over time

## Risk Management

### Risk Parameters

The strategy includes comprehensive risk management through configurable parameters:

```python
self.risk_params = {
    'max_leverage': 1.0,           # Maximum portfolio leverage
    'stop_loss_pct': 0.05,         # 5% stop loss
    'take_profit_pct': 0.10,       # 10% take profit
    'max_position_size': 0.10,     # 10% max per position
    'daily_loss_limit': -0.05,     # 5% daily loss limit
    'trade_blacklist': set()       # Blacklisted assets
}
```

### Automatic Risk Controls

1. **Position Sizing**: Automatically calculates safe position sizes
2. **Stop Loss Execution**: Monitors positions and executes stop losses
3. **Leverage Monitoring**: Prevents excessive leverage
4. **Blacklist Management**: Automatically blacklists problematic assets
5. **Circuit Breakers**: Halts trading on excessive losses

## Usage Guide

### Step 1: Create Your Strategy Class

```python
from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol

class MyTradingStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        
        # Customize risk parameters
        self.risk_params.update({
            'max_position_size': 0.15,  # 15% per position
            'stop_loss_pct': 0.08,      # 8% stop loss
        })
```

### Step 2: Implement Required Methods

```python
def select_universe(self, context):
    """Define your trading universe"""
    return [symbol('SBIN'), symbol('RELIANCE'), symbol('TCS')]

def generate_signals(self, context, data):
    """Generate trading signals"""
    signals = {}
    for asset in context.universe:
        # Your signal generation logic here
        signal_strength = self.calculate_signal(asset, data)
        signals[asset] = signal_strength
    return signals
```

### Step 3: Add Custom Logic (Optional)

```python
def calculate_signal(self, asset, data):
    """Custom signal calculation"""
    # Get price data
    prices = data.history(asset, 'price', 20, '1d')
    
    # Calculate indicators
    sma_short = prices.tail(5).mean()
    sma_long = prices.tail(20).mean()
    
    # Generate signal
    if sma_short > sma_long:
        return 1.0  # Buy signal
    elif sma_short < sma_long:
        return -1.0  # Sell signal
    else:
        return 0.0  # No signal
```

## Method Reference

### Core Methods (Must Implement)

#### `select_universe(self, context)`
**Purpose**: Define the trading universe (list of assets to trade)
**Returns**: List of Zipline Asset objects
**Example**:
```python
def select_universe(self, context):
    nse_symbols = ['SBIN', 'RELIANCE', 'TCS', 'INFY']
    return [symbol(sym) for sym in nse_symbols]
```

#### `generate_signals(self, context, data)`
**Purpose**: Generate trading signals for each asset
**Parameters**:
- `context`: Zipline context object with portfolio state
- `data`: Zipline data object for accessing market data
**Returns**: Dictionary of {asset: signal_strength} where signal_strength is between -1 and 1
**Example**:
```python
def generate_signals(self, context, data):
    signals = {}
    for asset in context.universe:
        # Your signal logic here
        signals[asset] = self.my_signal_calculation(asset, data)
    return signals
```

### Utility Methods (Available to Use)

#### `record_factor(self, factor_name, factor_value, context=None)`
**Purpose**: Record factor data for Alphalens analysis
**Parameters**:
- `factor_name`: Name of the factor (e.g., 'momentum', 'value')
- `factor_value`: Current factor value
- `context`: Zipline context (optional)

#### `_calculate_position_size(self, context, data, asset, target_weight)`
**Purpose**: Calculate safe position size based on risk parameters
**Returns**: Position size as fraction of portfolio
**Note**: Can be overridden for custom position sizing logic

#### `_should_trade(self, context, asset)`
**Purpose**: Check if asset should be traded (not blacklisted, etc.)
**Returns**: Boolean indicating if trading is allowed

### Lifecycle Methods (Automatically Called)

#### `initialize(self, context)`
**Purpose**: Initialize strategy (called once at start)
**Use**: Set up trading costs, schedules, universe

#### `rebalance(self, context, data)`
**Purpose**: Execute rebalancing (called at scheduled intervals)
**Use**: Generate signals and execute trades

#### `record_vars(self, context, data)`
**Purpose**: Record variables for analysis (called daily)
**Use**: Track custom metrics and performance

## Examples

### Example 1: Simple Moving Average Strategy

```python
class SMAStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def select_universe(self, context):
        return [symbol('SBIN'), symbol('RELIANCE')]

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.long_window + 1, '1d')
            if len(prices) >= self.long_window:
                short_ma = prices.tail(self.short_window).mean()
                long_ma = prices.tail(self.long_window).mean()
                
                if short_ma > long_ma:
                    signals[asset] = 1.0  # Buy
                else:
                    signals[asset] = -1.0  # Sell
            else:
                signals[asset] = 0.0  # No signal
        return signals
```

### Example 2: RSI Mean Reversion Strategy

```python
class RSIStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def calculate_rsi(self, prices):
        delta = prices.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=self.rsi_period).mean()
        avg_losses = losses.rolling(window=self.rsi_period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.rsi_period + 10, '1d')
            if len(prices) >= self.rsi_period + 1:
                rsi = self.calculate_rsi(prices)
                
                # Record factor for analysis
                self.record_factor('rsi', rsi, context)
                
                if rsi <= self.oversold:
                    signals[asset] = 1.0  # Oversold - Buy
                elif rsi >= self.overbought:
                    signals[asset] = -1.0  # Overbought - Sell
                else:
                    signals[asset] = 0.0  # Neutral
            else:
                signals[asset] = 0.0
        return signals
```

## Best Practices

### 1. **Signal Generation**
- Keep signals between -1 and 1 for consistency
- Use 0 for no signal/neutral position
- Implement proper error handling for data issues

### 2. **Risk Management**
- Always set appropriate risk parameters for your strategy
- Test stop-loss and take-profit levels thoroughly
- Monitor leverage and position sizes

### 3. **Performance**
- Record relevant factors for analysis
- Use efficient data access patterns
- Avoid look-ahead bias in signal generation

### 4. **Testing**
- Test with different market conditions
- Validate signal logic with historical data
- Monitor strategy performance metrics

## Integration with Zipline

The BaseStrategy integrates seamlessly with Zipline's algorithmic trading framework:

- **Data Access**: Use `data.history()` and `data.current()` for market data
- **Order Placement**: Automatic order management through `order_target_percent()`
- **Portfolio Management**: Access portfolio state through `context.portfolio`
- **Scheduling**: Automatic scheduling of rebalancing and recording

## Next Steps

1. **Read the ZiplineRunner Documentation** for execution details
2. **Check the Strategy Writing Guide** for advanced patterns
3. **Review example strategies** for implementation patterns
4. **Test your strategy** with historical data before live trading

For more information, see:
- [ZiplineRunner Documentation](./ZiplineRunner.md)
- [Strategy Writing Guide](./StrategyWritingGuide.md)
- [API Reference](./APIReference.md)
