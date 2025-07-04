# Enhanced Trading Strategy Framework

## Overview

This enhanced framework for zipline-reloaded makes strategy development incredibly simple and powerful. Instead of writing hundreds of lines of boilerplate code, you can focus on your strategy logic while the framework handles:

- **Risk Management**: Automatic position sizing, stop losses, take profits, drawdown limits
- **Technical Analysis**: Comprehensive technical indicators, momentum signals, mean reversion
- **Performance Analysis**: Automated pyfolio tearsheets, risk metrics, performance reports
- **Factor Analysis**: Integrated alphalens analysis for factor research
- **Portfolio Management**: Advanced portfolio optimization and regime detection
- **Data Handling**: Robust data processing and cleaning utilities

## Quick Start

### 1. Basic Strategy Template

```python
from engine.enhanced_base_strategy import BaseStrategy, TradingConfig
from engine.enhanced_zipline_runner import EnhancedTradingEngine

class MyStrategy(BaseStrategy):
    def define_universe(self, context, data):
        return [symbol('AAPL'), symbol('MSFT'), symbol('GOOGL')]
    
    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            if not data.can_trade(asset):
                continue
            
            # Get momentum using framework utilities
            momentum = self.data_utilities.calculate_momentum_signals(data, asset)
            
            if momentum.get('momentum_5d', 0) > 0.02:  # 2% momentum
                signals[asset] = {
                    'signal_type': SignalType.ENTRY_LONG,
                    'strength': 1.0,
                    'entry_price': data.current(asset, 'price')
                }
        
        return signals

# Configuration
config = TradingConfig(
    start_date="2020-01-01",
    end_date="2023-12-31",
    capital_base=100000,
    max_position_size=0.2,  # 20% max per position
    generate_tearsheet=True
)

# Run backtest
strategy = MyStrategy(config)
engine = EnhancedTradingEngine(config)
results = engine.run_complete_analysis(strategy)
```

### 2. Enhanced Configuration

The `TradingConfig` class provides comprehensive configuration options:

```python
config = TradingConfig(
    # Basic settings
    start_date="2020-01-01",
    end_date="2023-12-31",
    capital_base=100000.0,
    data_frequency="minute",  # or "daily"
    
    # Risk management
    max_position_size=0.20,           # 20% max per position
    max_total_exposure=1.0,           # 100% total exposure
    max_leverage=1.0,                 # No leverage
    stop_loss_pct=0.02,               # 2% stop loss
    take_profit_pct=0.06,             # 6% take profit
    max_drawdown_limit=0.10,          # 10% max drawdown
    
    # Position sizing
    position_sizing_method="volatility_target",  # or "equal_weight", "kelly"
    volatility_target=0.15,           # 15% target volatility
    
    # Advanced analysis
    generate_tearsheet=True,
    generate_factor_analysis=True,
    save_results=True,
    
    # Output
    output_dir="./results",
    log_level="INFO"
)
```

## Framework Components

### 1. Enhanced Base Strategy

The `BaseStrategy` class provides:

#### Available Utilities:
- `self.data_utilities`: Technical analysis and data processing
- `self.risk_manager`: Risk management and position sizing
- `self.signal_generator`: Signal generation utilities
- `self.scheduling_utilities`: Advanced scheduling functions

#### Key Methods to Override:
- `define_universe()`: Define your trading universe
- `generate_signals()`: Core strategy logic
- `setup_strategy()`: Strategy-specific initialization
- `schedule_functions()`: Custom scheduling

### 2. Data Utilities

#### Technical Indicators:
```python
# Get comprehensive technical indicators
indicators = self.data_utilities.calculate_technical_indicators(data, symbol)
# Returns: sma_20, sma_50, ema_20, rsi, macd, bollinger_bands, atr, etc.

# Get momentum signals
momentum = self.data_utilities.calculate_momentum_signals(data, symbol)
# Returns: momentum_5d, momentum_10d, momentum_20d, etc.

# Get mean reversion signals
reversion = self.data_utilities.calculate_mean_reversion_signals(data, symbol)
# Returns: z_score, bb_upper, bb_lower, bb_position
```

#### Advanced Utilities:
```python
from utils.strategy_utils import get_technical_indicators, get_risk_metrics

# Technical indicators with TA-Lib support
indicators = get_technical_indicators(prices, volumes)

# Risk metrics
risk_metrics = get_risk_metrics(returns)

# Market regime detection
regime = detect_market_regime(prices, regime_type='trend')
```

### 3. Signal Generation

#### Built-in Signal Generators:
```python
# Momentum signals
momentum_signals = self.signal_generator.generate_momentum_signals(context, data, symbols)

# Mean reversion signals
reversion_signals = self.signal_generator.generate_mean_reversion_signals(context, data, symbols)

# ORB signals
orb_signals = self.signal_generator.generate_orb_signals(context, data, symbol, orb_high, orb_low)
```

#### Signal Structure:
```python
signals = {
    symbol: {
        'signal_type': SignalType.ENTRY_LONG,  # or ENTRY_SHORT, EXIT_LONG, EXIT_SHORT
        'strength': 0.8,                       # Signal strength (0-1)
        'entry_price': 100.0,                  # Entry price
        'stop_loss': 95.0,                     # Optional stop loss
        'take_profit': 110.0                   # Optional take profit
    }
}
```

### 4. Risk Management

#### Automatic Risk Management:
- **Position Sizing**: Volatility-based, equal weight, or Kelly criterion
- **Stop Losses**: Automatic stop loss execution
- **Take Profits**: Automatic take profit execution
- **Drawdown Limits**: Portfolio-level drawdown protection
- **Leverage Control**: Maximum leverage limits

#### Risk Metrics:
```python
# Access risk metrics
risk_metrics = self.risk_manager.risk_metrics
print(f"Current drawdown: {risk_metrics.current_drawdown:.2%}")
print(f"Max drawdown: {risk_metrics.max_drawdown:.2%}")
```

### 5. Performance Analysis

#### Automated Analysis:
- **Pyfolio Tearsheets**: Comprehensive performance analysis
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Calmar ratio, VaR, CVaR
- **Drawdown Analysis**: Detailed drawdown periods and recovery
- **Transaction Analysis**: Trade analysis and costs

#### Custom Analysis:
```python
# Run complete analysis
results = engine.run_complete_analysis(strategy)

# Access specific analysis
performance_stats = engine.analyze_performance()
factor_analysis = engine.analyze_factors()
```

### 6. Advanced Features

#### Market Regime Detection:
```python
from utils.strategy_utils import detect_market_regime

# Detect different market regimes
trend_regime = detect_market_regime(prices, 'trend')
volatility_regime = detect_market_regime(prices, 'volatility')
momentum_regime = detect_market_regime(prices, 'momentum')
```

#### Portfolio Optimization:
```python
from utils.strategy_utils import optimize_portfolio

# Optimize portfolio weights
optimal_weights = optimize_portfolio(returns, method='mean_variance')
```

## Strategy Examples

### 1. Simple ORB Strategy

```python
class SimpleORBStrategy(BaseStrategy):
    def __init__(self, config, orb_minutes=30):
        super().__init__(config)
        self.orb_minutes = orb_minutes
        self.orb_data = {}
    
    def setup_strategy(self, context):
        context.universe = [symbol('BAJFINANCE')]
        
    def schedule_functions(self, context):
        # Use enhanced scheduling utilities
        self.scheduling_utilities.schedule_orb_strategy(
            self.establish_orb, self.check_breakout, self.close_positions, context
        )
    
    def establish_orb(self, context, data):
        # Framework handles the heavy lifting
        for symbol in context.universe:
            bars = data.history(symbol, ['high', 'low'], self.orb_minutes, '1m')
            if len(bars) >= self.orb_minutes:
                self.orb_data[symbol] = {
                    'high': bars['high'].max(),
                    'low': bars['low'].min(),
                    'established': True
                }
    
    def check_breakout(self, context, data):
        for symbol in context.universe:
            if symbol in self.orb_data and self.orb_data[symbol]['established']:
                # Use framework signal generator
                signals = self.signal_generator.generate_orb_signals(
                    context, data, symbol, 
                    self.orb_data[symbol]['high'], 
                    self.orb_data[symbol]['low']
                )
                if signals:
                    self.execute_trades(context, data, signals)
    
    def generate_signals(self, context, data):
        return {}  # ORB signals generated in check_breakout
```

### 2. Multi-Factor Strategy

```python
class MultiFactorStrategy(BaseStrategy):
    def define_universe(self, context, data):
        return [symbol('AAPL'), symbol('MSFT'), symbol('GOOGL'), symbol('AMZN')]
    
    def generate_signals(self, context, data):
        signals = {}
        
        for asset in context.universe:
            if not data.can_trade(asset):
                continue
            
            # Get multiple factors
            momentum = self.data_utilities.calculate_momentum_signals(data, asset)
            technical = self.data_utilities.calculate_technical_indicators(data, asset)
            reversion = self.data_utilities.calculate_mean_reversion_signals(data, asset)
            
            # Combine factors
            momentum_score = momentum.get('momentum_20d', 0)
            rsi_score = 50 - technical.get('rsi', 50)  # Contrarian RSI
            mean_reversion_score = -reversion.get('z_score', 0)  # Contrarian
            
            # Weighted composite score
            composite_score = (
                0.4 * momentum_score + 
                0.3 * rsi_score / 50 + 
                0.3 * mean_reversion_score / 2
            )
            
            if composite_score > 0.02:  # Long signal
                signals[asset] = {
                    'signal_type': SignalType.ENTRY_LONG,
                    'strength': min(composite_score, 1.0),
                    'entry_price': data.current(asset, 'price')
                }
            elif composite_score < -0.02:  # Short signal
                signals[asset] = {
                    'signal_type': SignalType.ENTRY_SHORT,
                    'strength': min(abs(composite_score), 1.0),
                    'entry_price': data.current(asset, 'price')
                }
        
        return signals
```

### 3. Regime-Based Strategy

```python
class RegimeBasedStrategy(BaseStrategy):
    def generate_signals(self, context, data):
        signals = {}
        
        for asset in context.universe:
            if not data.can_trade(asset):
                continue
            
            # Get price history for regime detection
            prices = data.history(asset, 'price', 50, '1d')
            
            # Detect market regime
            from utils.strategy_utils import detect_market_regime
            trend_regime = detect_market_regime(prices, 'trend')
            vol_regime = detect_market_regime(prices, 'volatility')
            
            current_trend = trend_regime.iloc[-1]
            current_vol = vol_regime.iloc[-1]
            
            # Strategy logic based on regime
            if current_trend == 1 and current_vol == 0:  # Trending, low vol
                # Use momentum strategy
                momentum = self.data_utilities.calculate_momentum_signals(data, asset)
                if momentum.get('momentum_10d', 0) > 0.03:
                    signals[asset] = {
                        'signal_type': SignalType.ENTRY_LONG,
                        'strength': 0.8,
                        'entry_price': data.current(asset, 'price')
                    }
            
            elif current_trend == 0 and current_vol == 1:  # Ranging, high vol
                # Use mean reversion strategy
                reversion = self.data_utilities.calculate_mean_reversion_signals(data, asset)
                z_score = reversion.get('z_score', 0)
                if z_score < -1.5:  # Oversold
                    signals[asset] = {
                        'signal_type': SignalType.ENTRY_LONG,
                        'strength': 0.6,
                        'entry_price': data.current(asset, 'price')
                    }
        
        return signals
```

## Best Practices

### 1. Strategy Development
- Start with the `strategy_template.py` as a base
- Focus on the `generate_signals()` method for your core logic
- Use the framework utilities for technical analysis
- Let the framework handle risk management and position sizing

### 2. Configuration
- Set appropriate risk limits (`max_position_size`, `max_drawdown_limit`)
- Choose the right position sizing method for your strategy
- Enable tearsheet generation for comprehensive analysis

### 3. Testing and Validation
- Use the enhanced analytics for thorough backtesting
- Check the generated tearsheets for performance insights
- Validate your strategy across different market conditions

### 4. Performance Optimization
- Use the built-in signal generators when possible
- Leverage the technical indicators utilities
- Monitor the automated risk management system

## Output Structure

When you run a backtest, the framework generates:

```
results/
├── data/
│   ├── raw_results.pkl
│   ├── returns.csv
│   ├── performance_analysis.pkl
│   └── factor_analysis.pkl
├── figures/
│   └── (various performance charts)
├── tearsheets/
│   ├── comprehensive_tearsheet.png
│   ├── custom_tearsheet.png
│   └── simple_tearsheet.png
├── factor_analysis/
│   └── (factor tearsheets)
├── risk_analysis/
│   └── (risk analysis reports)
└── reports/
    └── summary_report.json
```

## Advanced Usage

### Custom Technical Indicators
```python
from utils.strategy_utils import TechnicalIndicators

class MyStrategy(BaseStrategy):
    def generate_signals(self, context, data):
        for asset in context.universe:
            prices = data.history(asset, 'price', 100, '1d')
            
            # Use advanced technical indicators
            indicators = TechnicalIndicators.calculate_comprehensive_indicators(prices)
            
            # Custom indicator logic
            if indicators['rsi'] < 30 and indicators['macd'] > indicators['macd_signal']:
                # Generate signal
                pass
```

### Portfolio Optimization
```python
from utils.strategy_utils import optimize_portfolio

class OptimizedStrategy(BaseStrategy):
    def generate_signals(self, context, data):
        # Get returns for portfolio optimization
        returns_data = {}
        for asset in context.universe:
            returns = data.history(asset, 'price', 50, '1d').pct_change()
            returns_data[asset] = returns
        
        returns_df = pd.DataFrame(returns_data)
        
        # Optimize weights
        optimal_weights = optimize_portfolio(returns_df, method='mean_variance')
        
        # Generate rebalancing signals
        signals = {}
        for asset, weight in optimal_weights.items():
            signals[asset] = {
                'signal_type': SignalType.REBALANCE,
                'strength': weight,
                'entry_price': data.current(asset, 'price')
            }
        
        return signals
```

## Migration from Original ORB Strategy

Original ORB strategy had ~300 lines of code. With the enhanced framework:

**Before (Original):**
```python
class ORBStrategy:
    def __init__(self, config):
        self.config = config
        # ... 50+ lines of initialization
    
    def initialize(self, context):
        # ... 30+ lines of zipline setup
    
    def establish_orb(self, context, data):
        # ... 40+ lines of ORB calculation
    
    def check_breakout(self, context, data):
        # ... 30+ lines of breakout logic
    
    def enter_position(self, context, data, entry_price, position_type):
        # ... 50+ lines of position management
    
    def handle_data(self, context, data):
        # ... 20+ lines of position monitoring
    
    def manage_position(self, context, data):
        # ... 30+ lines of risk management
    
    # ... more methods
```

**After (Enhanced Framework):**
```python
class SimpleORBStrategy(BaseStrategy):
    def setup_strategy(self, context):
        context.universe = [symbol('BAJFINANCE')]
    
    def schedule_functions(self, context):
        self.scheduling_utilities.schedule_orb_strategy(
            self.establish_orb, self.check_breakout, self.close_positions, context
        )
    
    def establish_orb(self, context, data):
        # 10 lines of ORB calculation
    
    def check_breakout(self, context, data):
        # 5 lines using framework signal generator
    
    def generate_signals(self, context, data):
        return {}  # ORB signals handled in check_breakout
```

**Result:** ~50 lines instead of 300+ lines, with more features and better risk management!

## Summary

The enhanced framework provides:

1. **Simplified Strategy Development**: Focus on logic, not boilerplate
2. **Comprehensive Risk Management**: Built-in position sizing and risk controls
3. **Advanced Analytics**: Automated performance and factor analysis
4. **Rich Utilities**: Technical indicators, regime detection, portfolio optimization
5. **Professional Output**: Tearsheets, reports, and analysis

This framework leverages the full power of:
- **zipline-reloaded 3.1**: Event-driven backtesting
- **pyfolio-reloaded**: Performance analysis and tearsheets
- **alphalens-reloaded**: Factor analysis and research

You can now build sophisticated trading strategies with minimal code while getting institutional-quality analysis and risk management!
