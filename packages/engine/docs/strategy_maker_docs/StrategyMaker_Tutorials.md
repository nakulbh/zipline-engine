# Strategy Maker Tutorials and Examples

## Tutorial 1: Building Your First Strategy

### Simple Moving Average Crossover Strategy

This tutorial walks through creating a basic moving average crossover strategy from scratch.

#### Step 1: Strategy Design

**Hypothesis**: When a short-term moving average crosses above a long-term moving average, it signals an uptrend and we should buy. When it crosses below, we should sell.

**Parameters**:
- Short window: 10 days
- Long window: 30 days
- Universe: Top 5 NSE stocks by market cap

#### Step 2: Implementation

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol
import numpy as np
import pandas as pd

class SimpleSMAStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=30):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        
        # Customize risk parameters for this strategy
        self.risk_params.update({
            'max_position_size': 0.20,  # 20% per position
            'stop_loss_pct': 0.05,      # 5% stop loss
            'take_profit_pct': 0.15,    # 15% take profit
        })
    
    def select_universe(self, context):
        """Select top NSE stocks"""
        return [
            symbol('RELIANCE'),
            symbol('HDFCBANK'), 
            symbol('INFY'),
            symbol('SBIN'),
            symbol('BAJFINANCE')
        ]
    
    def generate_signals(self, context, data):
        """Generate SMA crossover signals"""
        signals = {}
        
        for asset in context.universe:
            try:
                # Get price history
                prices = data.history(asset, 'price', self.long_window + 5, '1d')
                
                if len(prices) < self.long_window:
                    signals[asset] = 0.0
                    continue
                
                # Calculate moving averages
                short_ma = prices.tail(self.short_window).mean()
                long_ma = prices.tail(self.long_window).mean()
                
                # Previous day's moving averages for crossover detection
                prev_short_ma = prices.iloc[-(self.short_window+1):-1].mean()
                prev_long_ma = prices.iloc[-(self.long_window+1):-1].mean()
                
                # Detect crossover
                if short_ma > long_ma and prev_short_ma <= prev_long_ma:
                    # Golden cross - buy signal
                    signals[asset] = 1.0
                elif short_ma < long_ma and prev_short_ma >= prev_long_ma:
                    # Death cross - sell signal
                    signals[asset] = -1.0
                else:
                    # No crossover - hold current position
                    signals[asset] = 0.0
                    
            except Exception as e:
                self.logger.warning(f"Error calculating SMA for {asset.symbol}: {e}")
                signals[asset] = 0.0
        
        return signals
```

#### Step 3: Backtesting

```python
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

# Create strategy instance
strategy = SimpleSMAStrategy(short_window=10, long_window=30)

# Create runner
runner = EnhancedZiplineRunner(
    strategy=strategy,
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2023-01-01',
    capital_base=100000,
    benchmark_symbol='NIFTY50'
)

# Run backtest
results = runner.run()

# Analyze results
runner.analyze_results(results)
```

#### Step 4: Results Analysis

The backtest will generate comprehensive performance metrics including:
- Total return and annualized return
- Sharpe ratio and maximum drawdown
- Win rate and average win/loss
- Detailed transaction log

## Tutorial 2: RSI Mean Reversion Strategy

### Building a More Advanced Strategy

This tutorial demonstrates a more sophisticated strategy using RSI for mean reversion signals.

#### Strategy Logic

**Entry Rules**:
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)

**Exit Rules**:
- Exit long positions when RSI > 50
- Exit short positions when RSI < 50

#### Implementation

```python
from utils.strategy_utils import TechnicalIndicators

class RSIMeanReversionStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold=30, overbought=70, exit_neutral=50):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.exit_neutral = exit_neutral
        
        # Risk parameters for mean reversion
        self.risk_params.update({
            'max_position_size': 0.15,
            'stop_loss_pct': 0.04,
            'take_profit_pct': 0.08,
        })
    
    def select_universe(self, context):
        """Select liquid NSE stocks suitable for mean reversion"""
        return [
            symbol('RELIANCE'), symbol('HDFCBANK'), symbol('INFY'),
            symbol('SBIN'), symbol('BAJFINANCE'), symbol('MARUTI'),
            symbol('ASIANPAINT'), symbol('NESTLEIND')
        ]
    
    def generate_signals(self, context, data):
        """Generate RSI-based mean reversion signals"""
        signals = {}
        
        for asset in context.universe:
            try:
                # Get price history
                prices = data.history(asset, 'price', self.rsi_period + 10, '1d')
                
                if len(prices) < self.rsi_period + 1:
                    signals[asset] = 0.0
                    continue
                
                # Calculate RSI
                rsi = TechnicalIndicators.calculate_rsi(prices, self.rsi_period)
                current_rsi = rsi.iloc[-1]
                
                # Get current position
                current_position = context.portfolio.positions[asset].amount
                
                # Generate signals based on RSI and current position
                if current_position == 0:  # No current position
                    if current_rsi < self.oversold:
                        signals[asset] = 1.0  # Buy oversold
                    elif current_rsi > self.overbought:
                        signals[asset] = -1.0  # Sell overbought
                    else:
                        signals[asset] = 0.0
                        
                elif current_position > 0:  # Long position
                    if current_rsi > self.exit_neutral:
                        signals[asset] = 0.0  # Exit long
                    else:
                        signals[asset] = 1.0  # Hold long
                        
                else:  # Short position
                    if current_rsi < self.exit_neutral:
                        signals[asset] = 0.0  # Exit short
                    else:
                        signals[asset] = -1.0  # Hold short
                        
            except Exception as e:
                self.logger.warning(f"Error calculating RSI for {asset.symbol}: {e}")
                signals[asset] = 0.0
        
        return signals
```

## Tutorial 3: Multi-Factor Strategy

### Combining Multiple Signals

This tutorial shows how to combine multiple factors for more robust signal generation.

#### Strategy Components

1. **Momentum Factor**: 20-day price momentum
2. **Mean Reversion Factor**: RSI-based signals
3. **Volatility Factor**: Prefer low volatility stocks
4. **Volume Factor**: Confirm signals with volume

#### Implementation

```python
class MultiFactorStrategy(BaseStrategy):
    def __init__(self, momentum_period=20, rsi_period=14, vol_period=30):
        super().__init__()
        self.momentum_period = momentum_period
        self.rsi_period = rsi_period
        self.vol_period = vol_period
        
        # Factor weights
        self.factor_weights = {
            'momentum': 0.3,
            'mean_reversion': 0.3,
            'volatility': 0.2,
            'volume': 0.2
        }
        
        self.risk_params.update({
            'max_position_size': 0.12,
            'stop_loss_pct': 0.06,
        })
    
    def select_universe(self, context):
        return [
            symbol('RELIANCE'), symbol('HDFCBANK'), symbol('INFY'),
            symbol('SBIN'), symbol('BAJFINANCE'), symbol('MARUTI'),
            symbol('ASIANPAINT'), symbol('NESTLEIND'), symbol('DRREDDY'),
            symbol('BHARTIARTL')
        ]
    
    def generate_signals(self, context, data):
        """Generate multi-factor signals"""
        signals = {}
        
        for asset in context.universe:
            try:
                # Get sufficient price and volume history
                history_length = max(self.momentum_period, self.rsi_period, self.vol_period) + 10
                prices = data.history(asset, 'price', history_length, '1d')
                volumes = data.history(asset, 'volume', history_length, '1d')
                
                if len(prices) < history_length - 5:
                    signals[asset] = 0.0
                    continue
                
                # Factor 1: Momentum
                momentum = (prices.iloc[-1] / prices.iloc[-self.momentum_period]) - 1
                momentum_signal = np.tanh(momentum * 10)  # Normalize
                
                # Factor 2: Mean Reversion (RSI)
                rsi = TechnicalIndicators.calculate_rsi(prices, self.rsi_period)
                current_rsi = rsi.iloc[-1]
                if current_rsi < 30:
                    rsi_signal = (30 - current_rsi) / 30
                elif current_rsi > 70:
                    rsi_signal = (70 - current_rsi) / 30
                else:
                    rsi_signal = 0.0
                
                # Factor 3: Volatility (prefer low volatility)
                returns = prices.pct_change().dropna()
                volatility = returns.tail(self.vol_period).std()
                vol_signal = -np.tanh(volatility * 50)  # Negative because we prefer low vol
                
                # Factor 4: Volume confirmation
                avg_volume = volumes.tail(20).mean()
                recent_volume = volumes.tail(5).mean()
                volume_signal = np.tanh((recent_volume / avg_volume - 1) * 2)
                
                # Combine factors
                combined_signal = (
                    self.factor_weights['momentum'] * momentum_signal +
                    self.factor_weights['mean_reversion'] * rsi_signal +
                    self.factor_weights['volatility'] * vol_signal +
                    self.factor_weights['volume'] * volume_signal
                )
                
                # Ensure signal is in valid range
                signals[asset] = np.clip(combined_signal, -1.0, 1.0)
                
            except Exception as e:
                self.logger.warning(f"Error in multi-factor calculation for {asset.symbol}: {e}")
                signals[asset] = 0.0
        
        return signals
```

## Tutorial 4: Custom Risk Management

### Implementing Advanced Risk Controls

This tutorial demonstrates how to implement custom risk management beyond the default framework.

#### Custom Risk Strategy

```python
class CustomRiskStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        
        # Custom risk parameters
        self.risk_params.update({
            'max_position_size': 0.10,
            'max_sector_exposure': 0.30,  # Custom parameter
            'correlation_limit': 0.70,    # Custom parameter
            'volatility_target': 0.15,    # Custom parameter
        })
        
        # Track sector exposures
        self.sector_map = {
            'RELIANCE': 'Energy',
            'HDFCBANK': 'Banking',
            'SBIN': 'Banking',
            'INFY': 'IT',
            'BAJFINANCE': 'Financial Services'
        }
    
    def select_universe(self, context):
        return [symbol(s) for s in self.sector_map.keys()]
    
    def _custom_risk_checks(self, context, proposed_signals):
        """Custom risk checks beyond default framework"""
        adjusted_signals = proposed_signals.copy()
        
        # Check sector concentration
        sector_exposures = {}
        for asset, signal in proposed_signals.items():
            sector = self.sector_map.get(asset.symbol, 'Unknown')
            if sector not in sector_exposures:
                sector_exposures[sector] = 0
            sector_exposures[sector] += abs(signal) * self.risk_params['max_position_size']
        
        # Reduce signals if sector exposure too high
        for sector, exposure in sector_exposures.items():
            if exposure > self.risk_params['max_sector_exposure']:
                reduction_factor = self.risk_params['max_sector_exposure'] / exposure
                for asset, signal in adjusted_signals.items():
                    if self.sector_map.get(asset.symbol) == sector:
                        adjusted_signals[asset] *= reduction_factor
        
        return adjusted_signals
    
    def generate_signals(self, context, data):
        """Generate signals with custom risk management"""
        # Basic momentum signals
        raw_signals = {}
        
        for asset in context.universe:
            try:
                prices = data.history(asset, 'price', 21, '1d')
                if len(prices) >= 20:
                    momentum = (prices.iloc[-1] / prices.iloc[-20]) - 1
                    raw_signals[asset] = np.tanh(momentum * 5)
                else:
                    raw_signals[asset] = 0.0
            except:
                raw_signals[asset] = 0.0
        
        # Apply custom risk checks
        final_signals = self._custom_risk_checks(context, raw_signals)
        
        return final_signals
```

## Tutorial 5: Strategy Optimization

### Parameter Optimization and Walk-Forward Analysis

This tutorial shows how to optimize strategy parameters systematically.

#### Optimization Framework

```python
import itertools
from datetime import datetime, timedelta

class StrategyOptimizer:
    def __init__(self, strategy_class, bundle, start_date, end_date):
        self.strategy_class = strategy_class
        self.bundle = bundle
        self.start_date = start_date
        self.end_date = end_date
        
    def optimize_parameters(self, param_grid, metric='sharpe_ratio'):
        """Optimize strategy parameters using grid search"""
        results = []
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for combination in itertools.product(*param_values):
            params = dict(zip(param_names, combination))
            
            try:
                # Create strategy with these parameters
                strategy = self.strategy_class(**params)
                
                # Run backtest
                runner = EnhancedZiplineRunner(
                    strategy=strategy,
                    bundle=self.bundle,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    capital_base=100000
                )
                
                backtest_results = runner.run()
                
                # Extract performance metric
                performance = self._extract_metric(backtest_results, metric)
                
                results.append({
                    'params': params,
                    'performance': performance,
                    'results': backtest_results
                })
                
            except Exception as e:
                print(f"Error with parameters {params}: {e}")
                continue
        
        # Sort by performance
        results.sort(key=lambda x: x['performance'], reverse=True)
        return results
    
    def _extract_metric(self, results, metric):
        """Extract performance metric from backtest results"""
        if metric == 'sharpe_ratio':
            returns = results.returns
            return returns.mean() / returns.std() * np.sqrt(252)
        elif metric == 'total_return':
            return (results.portfolio_value.iloc[-1] / results.portfolio_value.iloc[0]) - 1
        elif metric == 'max_drawdown':
            cumulative = (1 + results.returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        else:
            raise ValueError(f"Unknown metric: {metric}")

# Usage example
optimizer = StrategyOptimizer(
    strategy_class=SimpleSMAStrategy,
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2022-01-01'
)

param_grid = {
    'short_window': [5, 10, 15, 20],
    'long_window': [30, 40, 50, 60]
}

optimization_results = optimizer.optimize_parameters(param_grid, metric='sharpe_ratio')

# Print best parameters
best_params = optimization_results[0]['params']
best_performance = optimization_results[0]['performance']
print(f"Best parameters: {best_params}")
print(f"Best Sharpe ratio: {best_performance:.3f}")
```

## Best Practices Summary

### Strategy Development

1. **Start Simple**: Begin with basic strategies and add complexity gradually
2. **Validate Assumptions**: Test each component of your strategy logic independently
3. **Handle Errors Gracefully**: Implement comprehensive error handling for data issues
4. **Document Your Logic**: Comment your code thoroughly for future maintenance

### Risk Management

1. **Always Use Position Limits**: Never risk more than you can afford to lose
2. **Implement Stop Losses**: Protect against large losses with automatic exits
3. **Diversify**: Don't concentrate all risk in similar assets or strategies
4. **Monitor Correlations**: Be aware of hidden correlations that increase risk

### Backtesting

1. **Use Realistic Assumptions**: Include transaction costs and slippage
2. **Avoid Look-Ahead Bias**: Only use information available at decision time
3. **Test Multiple Periods**: Validate performance across different market conditions
4. **Walk-Forward Analysis**: Use rolling optimization to avoid overfitting

### Performance Analysis

1. **Risk-Adjusted Metrics**: Focus on Sharpe ratio, not just returns
2. **Drawdown Analysis**: Understand maximum losses and recovery periods
3. **Factor Attribution**: Understand what drives your strategy's performance
4. **Out-of-Sample Testing**: Reserve data for final validation

These tutorials provide a solid foundation for developing sophisticated trading strategies using the Strategy Maker framework. Start with the simple examples and gradually incorporate more advanced techniques as your understanding deepens.
