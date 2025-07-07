# Strategy Writing Guide

## Overview

This comprehensive guide teaches you how to write effective trading strategies using the NSE Backtesting Engine. From basic concepts to advanced patterns, this guide covers everything you need to create professional-grade trading strategies.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Strategy Architecture](#strategy-architecture)
3. [Basic Strategy Patterns](#basic-strategy-patterns)
4. [Advanced Techniques](#advanced-techniques)
5. [Best Practices](#best-practices)
6. [Testing & Validation](#testing--validation)
7. [Common Pitfalls](#common-pitfalls)
8. [Performance Optimization](#performance-optimization)

## Getting Started

### Prerequisites

Before writing strategies, ensure you understand:
- **Python Programming**: Object-oriented programming, pandas, numpy
- **Financial Markets**: Basic trading concepts, technical analysis
- **Zipline Framework**: Data access, order management, portfolio concepts

### Basic Strategy Template

Every strategy follows this basic template:

```python
from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record

class MyStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        
        # Customize risk parameters
        self.risk_params.update({
            'max_position_size': 0.10,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.10
        })

    def select_universe(self, context):
        """Define trading universe"""
        return [symbol('SBIN'), symbol('RELIANCE')]

    def generate_signals(self, context, data):
        """Generate trading signals"""
        signals = {}
        for asset in context.universe:
            # Your signal logic here
            signals[asset] = self.calculate_signal(asset, data)
        return signals

    def calculate_signal(self, asset, data):
        """Custom signal calculation"""
        # Implement your trading logic
        return 0.0  # Return signal between -1 and 1
```

## Strategy Architecture

### Core Components

#### 1. **Initialization (`__init__`)**
- Set strategy parameters
- Configure risk management
- Initialize state variables

#### 2. **Universe Selection (`select_universe`)**
- Define which assets to trade
- Can be static or dynamic
- Should return list of Zipline Asset objects

#### 3. **Signal Generation (`generate_signals`)**
- Core trading logic
- Generate signals for each asset
- Return dictionary of {asset: signal_strength}

#### 4. **Helper Methods**
- Custom calculations
- Technical indicators
- Data processing functions

### Data Flow

```
Market Data → Signal Generation → Risk Management → Order Execution → Portfolio Update
     ↑              ↓                    ↓              ↓              ↓
Universe ← Strategy Logic ← Risk Params ← Position Size ← Performance
```

## Basic Strategy Patterns

### Pattern 1: Trend Following

```python
class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=30):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def select_universe(self, context):
        return [symbol('SBIN'), symbol('RELIANCE'), symbol('TCS')]

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.long_window + 1, '1d')
            
            if len(prices) >= self.long_window:
                short_ma = prices.tail(self.short_window).mean()
                long_ma = prices.tail(self.long_window).mean()
                
                # Trend following logic
                if short_ma > long_ma * 1.02:  # 2% threshold
                    signals[asset] = 1.0  # Strong buy
                elif short_ma < long_ma * 0.98:  # 2% threshold
                    signals[asset] = -1.0  # Strong sell
                else:
                    signals[asset] = 0.0  # No signal
            else:
                signals[asset] = 0.0
                
        return signals
```

### Pattern 2: Mean Reversion

```python
class MeanReversionStrategy(BaseStrategy):
    def __init__(self, lookback=20, threshold=2.0):
        super().__init__()
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.lookback + 1, '1d')
            
            if len(prices) >= self.lookback:
                current_price = prices.iloc[-1]
                mean_price = prices.tail(self.lookback).mean()
                std_price = prices.tail(self.lookback).std()
                
                # Z-score calculation
                z_score = (current_price - mean_price) / std_price
                
                # Mean reversion logic
                if z_score > self.threshold:
                    signals[asset] = -1.0  # Sell (price too high)
                elif z_score < -self.threshold:
                    signals[asset] = 1.0   # Buy (price too low)
                else:
                    signals[asset] = 0.0   # No signal
            else:
                signals[asset] = 0.0
                
        return signals
```

### Pattern 3: Momentum Strategy

```python
class MomentumStrategy(BaseStrategy):
    def __init__(self, momentum_period=12, min_momentum=0.05):
        super().__init__()
        self.momentum_period = momentum_period
        self.min_momentum = min_momentum

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.momentum_period + 1, '1d')
            
            if len(prices) >= self.momentum_period + 1:
                # Calculate momentum
                momentum = (prices.iloc[-1] / prices.iloc[-self.momentum_period-1]) - 1
                
                # Record momentum for analysis
                self.record_factor('momentum', momentum, context)
                
                # Momentum logic
                if momentum > self.min_momentum:
                    signals[asset] = min(1.0, momentum * 5)  # Scale momentum
                elif momentum < -self.min_momentum:
                    signals[asset] = max(-1.0, momentum * 5)  # Scale momentum
                else:
                    signals[asset] = 0.0
            else:
                signals[asset] = 0.0
                
        return signals
```

## Advanced Techniques

### Multi-Timeframe Analysis

```python
class MultiTimeframeStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.short_period = 5
        self.medium_period = 20
        self.long_period = 50

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            # Get sufficient data for longest period
            prices = data.history(asset, 'price', self.long_period + 10, '1d')
            
            if len(prices) >= self.long_period:
                # Calculate multiple timeframe signals
                short_signal = self.calculate_short_term_signal(prices)
                medium_signal = self.calculate_medium_term_signal(prices)
                long_signal = self.calculate_long_term_signal(prices)
                
                # Combine signals with weights
                combined_signal = (
                    short_signal * 0.5 +
                    medium_signal * 0.3 +
                    long_signal * 0.2
                )
                
                signals[asset] = max(-1.0, min(1.0, combined_signal))
            else:
                signals[asset] = 0.0
                
        return signals

    def calculate_short_term_signal(self, prices):
        # Short-term momentum
        return (prices.iloc[-1] / prices.iloc[-self.short_period] - 1) * 10

    def calculate_medium_term_signal(self, prices):
        # Medium-term trend
        sma = prices.tail(self.medium_period).mean()
        return 1.0 if prices.iloc[-1] > sma else -1.0

    def calculate_long_term_signal(self, prices):
        # Long-term trend
        sma = prices.tail(self.long_period).mean()
        return 1.0 if prices.iloc[-1] > sma else -1.0
```

### Dynamic Universe Selection

```python
class DynamicUniverseStrategy(BaseStrategy):
    def __init__(self, universe_size=10):
        super().__init__()
        self.universe_size = universe_size
        self.all_assets = [
            symbol('SBIN'), symbol('RELIANCE'), symbol('TCS'),
            symbol('INFY'), symbol('HDFCBANK'), symbol('ICICIBANK'),
            symbol('WIPRO'), symbol('LT'), symbol('MARUTI')
        ]

    def select_universe(self, context):
        # Dynamic universe based on liquidity/volume
        if hasattr(context, 'current_date'):
            return self.select_top_liquid_assets(context)
        else:
            return self.all_assets[:self.universe_size]

    def select_top_liquid_assets(self, context):
        # This would be called during rebalancing
        # Select assets based on recent volume/liquidity
        return self.all_assets[:self.universe_size]  # Simplified

    def generate_signals(self, context, data):
        # Your signal generation logic here
        signals = {}
        for asset in context.universe:
            signals[asset] = self.calculate_signal(asset, data)
        return signals
```

### Factor-Based Strategy

```python
class FactorStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.lookback = 30

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            prices = data.history(asset, 'price', self.lookback + 10, '1d')
            
            if len(prices) >= self.lookback:
                # Calculate multiple factors
                momentum_factor = self.calculate_momentum_factor(prices)
                value_factor = self.calculate_value_factor(prices)
                volatility_factor = self.calculate_volatility_factor(prices)
                
                # Record factors for Alphalens analysis
                self.record_factor('momentum', momentum_factor, context)
                self.record_factor('value', value_factor, context)
                self.record_factor('volatility', volatility_factor, context)
                
                # Combine factors
                combined_score = (
                    momentum_factor * 0.4 +
                    value_factor * 0.4 +
                    volatility_factor * 0.2
                )
                
                signals[asset] = max(-1.0, min(1.0, combined_score))
            else:
                signals[asset] = 0.0
                
        return signals

    def calculate_momentum_factor(self, prices):
        # 12-1 momentum (skip last month)
        if len(prices) >= 252:  # Need at least 1 year of data
            return (prices.iloc[-22] / prices.iloc[-252]) - 1
        return 0.0

    def calculate_value_factor(self, prices):
        # Simple value proxy using price level
        recent_high = prices.tail(252).max() if len(prices) >= 252 else prices.max()
        current_price = prices.iloc[-1]
        return (recent_high - current_price) / recent_high

    def calculate_volatility_factor(self, prices):
        # Volatility factor (negative for low vol preference)
        returns = prices.pct_change().dropna()
        if len(returns) >= 20:
            volatility = returns.tail(20).std() * (252 ** 0.5)  # Annualized
            return -volatility  # Negative because we prefer low volatility
        return 0.0
```

## Best Practices

### 1. **Signal Design**

#### Signal Strength Guidelines
```python
# Good signal design
def generate_signals(self, context, data):
    signals = {}
    for asset in context.universe:
        raw_signal = self.calculate_raw_signal(asset, data)
        
        # Normalize signal to [-1, 1] range
        normalized_signal = max(-1.0, min(1.0, raw_signal))
        
        # Apply confidence threshold
        if abs(normalized_signal) < 0.1:  # Minimum confidence
            normalized_signal = 0.0
            
        signals[asset] = normalized_signal
    return signals
```

#### Avoid Look-Ahead Bias
```python
# BAD - Uses future data
def bad_signal(self, prices):
    future_price = prices.iloc[-1]  # This is tomorrow's price!
    current_price = prices.iloc[-2]
    return 1.0 if future_price > current_price else -1.0

# GOOD - Uses only past data
def good_signal(self, prices):
    current_price = prices.iloc[-1]
    yesterday_price = prices.iloc[-2]
    return 1.0 if current_price > yesterday_price else -1.0
```

### 2. **Risk Management**

#### Position Sizing
```python
def _calculate_position_size(self, context, data, asset, target_weight):
    base_size = super()._calculate_position_size(context, data, asset, target_weight)
    
    # Adjust for volatility
    prices = data.history(asset, 'price', 20, '1d')
    if len(prices) >= 20:
        volatility = prices.pct_change().std() * (252 ** 0.5)
        vol_adjustment = min(1.0, 0.15 / volatility)  # Target 15% volatility
        base_size *= vol_adjustment
    
    return base_size
```

#### Stop Loss Implementation
```python
def __init__(self):
    super().__init__()
    self.risk_params.update({
        'stop_loss_pct': 0.05,      # 5% stop loss
        'take_profit_pct': 0.15,    # 15% take profit
        'trailing_stop': True       # Enable trailing stops
    })
```

### 3. **Data Handling**

#### Robust Data Access
```python
def get_safe_history(self, data, asset, field, periods, frequency):
    """Safely get historical data with error handling"""
    try:
        history = data.history(asset, field, periods, frequency)
        if history.empty or len(history) < periods // 2:
            return None
        return history
    except Exception as e:
        self.logger.warning(f"Data access failed for {asset}: {e}")
        return None
```

#### Handle Missing Data
```python
def generate_signals(self, context, data):
    signals = {}
    for asset in context.universe:
        prices = self.get_safe_history(data, asset, 'price', 30, '1d')
        
        if prices is not None and len(prices) >= 20:
            signals[asset] = self.calculate_signal(prices)
        else:
            signals[asset] = 0.0  # No signal for insufficient data
            
    return signals
```

## Testing & Validation

### Unit Testing Your Strategy

```python
import unittest
import pandas as pd
from strategies.my_strategy import MyStrategy

class TestMyStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MyStrategy(param1=10, param2=20)

    def test_signal_calculation(self):
        # Create test data
        prices = pd.Series([100, 101, 102, 103, 104])
        
        # Test signal calculation
        signal = self.strategy.calculate_signal_from_prices(prices)
        
        # Assert expected behavior
        self.assertGreater(signal, 0)  # Should be positive for uptrend
        self.assertLessEqual(abs(signal), 1.0)  # Should be normalized

    def test_risk_parameters(self):
        # Test risk parameter validation
        self.assertLessEqual(self.strategy.risk_params['max_position_size'], 1.0)
        self.assertGreater(self.strategy.risk_params['stop_loss_pct'], 0)

if __name__ == '__main__':
    unittest.main()
```

### Backtesting Validation

```python
# Test multiple time periods
def validate_strategy():
    strategy = MyStrategy()
    
    test_periods = [
        ('2018-01-01', '2019-01-01'),  # Bull market
        ('2019-01-01', '2020-01-01'),  # Normal market
        ('2020-01-01', '2021-01-01'),  # Volatile market
    ]
    
    results = {}
    for start, end in test_periods:
        runner = EnhancedZiplineRunner(
            strategy=strategy,
            bundle='nse-local-minute-bundle',
            start_date=start,
            end_date=end
        )
        results[f"{start}_{end}"] = runner.run()
    
    return results
```

## Common Pitfalls

### 1. **Look-Ahead Bias**
```python
# WRONG - Using future information
def bad_strategy(self, context, data):
    prices = data.history(symbol('SBIN'), 'price', 10, '1d')
    future_return = prices.iloc[-1] / prices.iloc[-2] - 1  # This is tomorrow!
    return 1.0 if future_return > 0 else -1.0

# CORRECT - Using only past information
def good_strategy(self, context, data):
    prices = data.history(symbol('SBIN'), 'price', 10, '1d')
    past_return = prices.iloc[-2] / prices.iloc[-3] - 1  # Yesterday's return
    return 1.0 if past_return > 0 else -1.0
```

### 2. **Overfitting**
```python
# WRONG - Too many parameters
class OverfittedStrategy(BaseStrategy):
    def __init__(self, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
        # Too many parameters = overfitting risk
        pass

# CORRECT - Simple, robust parameters
class RobustStrategy(BaseStrategy):
    def __init__(self, lookback=20, threshold=0.02):
        # Simple, meaningful parameters
        pass
```

### 3. **Insufficient Data Handling**
```python
# WRONG - No data validation
def bad_signal(self, data, asset):
    prices = data.history(asset, 'price', 20, '1d')
    return prices.mean()  # What if prices is empty?

# CORRECT - Proper data validation
def good_signal(self, data, asset):
    prices = data.history(asset, 'price', 20, '1d')
    if len(prices) < 10:  # Minimum data requirement
        return 0.0
    return prices.mean()
```

## Performance Optimization

### 1. **Efficient Data Access**
```python
# GOOD - Batch data access
def generate_signals(self, context, data):
    # Get data for all assets at once
    all_prices = {}
    for asset in context.universe:
        all_prices[asset] = data.history(asset, 'price', 30, '1d')
    
    # Process signals
    signals = {}
    for asset, prices in all_prices.items():
        signals[asset] = self.calculate_signal(prices)
    
    return signals
```

### 2. **Caching Calculations**
```python
class OptimizedStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.calculation_cache = {}

    def get_cached_indicator(self, asset, data, indicator_name):
        cache_key = f"{asset}_{indicator_name}_{data.current_dt}"
        
        if cache_key not in self.calculation_cache:
            self.calculation_cache[cache_key] = self.calculate_indicator(asset, data)
        
        return self.calculation_cache[cache_key]
```

### 3. **Memory Management**
```python
def generate_signals(self, context, data):
    signals = {}
    
    for asset in context.universe:
        # Process one asset at a time for large universes
        prices = data.history(asset, 'price', 30, '1d')
        signals[asset] = self.calculate_signal(prices)
        
        # Clear large objects
        del prices
    
    return signals
```

## Next Steps

1. **Start Simple**: Begin with basic trend-following or mean-reversion strategies
2. **Test Thoroughly**: Validate your strategy across different market conditions
3. **Iterate**: Gradually add complexity and sophistication
4. **Monitor Performance**: Use comprehensive logging and analysis
5. **Stay Updated**: Keep learning about new techniques and market dynamics

For more information, see:
- [BaseStrategy Documentation](./BaseStrategy.md)
- [ZiplineRunner Documentation](./ZiplineRunner.md)
- [API Reference](./APIReference.md)
