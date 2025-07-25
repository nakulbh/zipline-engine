# 📛 BaseStrategy Market Concepts: Trading Theory and Implementation

## 🔍 Overview
This document explains the fundamental market concepts, trading theories, and quantitative finance principles implemented in the BaseStrategy framework. Each concept is linked to specific code implementations and practical applications.

---

## 💰 Position Sizing Theory

### Van Tharp Position Sizing Method

**Core Philosophy**: "It's not whether you're right or wrong, but how much money you make when you're right and how much you lose when you're wrong."

**Mathematical Foundation**:
```
Position Size = (Account Risk × Account Value) / (Entry Price × Stop Distance)
```

**Implementation in BaseStrategy**:
```python
def _calculate_position_size(self, context, data, asset, target) -> float:
    price = data.current(asset, 'price')
    atr = self._get_atr(asset, window=20)
    
    # Risk 1% of portfolio per trade
    risk_per_trade = context.portfolio.portfolio_value * 0.01
    
    # Stop distance based on 2x ATR (market noise)
    stop_distance = 2 * atr if atr > 0 else 0.02
    
    # Calculate position size
    position_size = risk_per_trade / (stop_distance * price)
    
    return min(abs(position_size), self.risk_params['max_position_size'])
```

**Market Reality**: This approach ensures:
- **Consistent Risk**: Each trade risks the same dollar amount
- **Volatility Adjustment**: Smaller positions in volatile assets
- **Drawdown Control**: Limits maximum portfolio loss

### Kelly Criterion Alternative

**Theory**: Optimal position sizing based on win rate and average win/loss ratio.

**Formula**: f* = (bp - q) / b
- f* = fraction of capital to wager
- b = odds received (reward/risk ratio)
- p = probability of winning
- q = probability of losing (1-p)

**Practical Limitation**: Requires accurate probability estimates, which are difficult in financial markets.

**BaseStrategy Approach**: Uses fixed 1% risk per trade as a conservative alternative to Kelly, avoiding the need for probability estimation.

---

## 📊 Volatility Measurement

### Average True Range (ATR)

**Purpose**: Measure market volatility accounting for gaps between trading sessions.

**Components**:
1. **True Range 1**: Current High - Current Low (intraday volatility)
2. **True Range 2**: |Current High - Previous Close| (gap up volatility)
3. **True Range 3**: |Current Low - Previous Close| (gap down volatility)

**True Range = MAX(TR1, TR2, TR3)**

**ATR = Simple Moving Average of True Range over N periods**

**Code Implementation**:
```python
def _get_atr(self, asset, window=14) -> float:
    # Get OHLC data
    highs = data.history(asset, 'high', window + 1, '1d')
    lows = data.history(asset, 'low', window + 1, '1d')
    closes = data.history(asset, 'close', window + 1, '1d')
    
    # Calculate True Range components
    prev_close = closes.shift(1)
    tr1 = highs - lows                    # Intraday range
    tr2 = abs(highs - prev_close)         # Gap up
    tr3 = abs(lows - prev_close)          # Gap down
    
    # True Range is maximum of three
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR is moving average of True Range
    atr = true_range.rolling(window=window).mean().iloc[-1]
    
    # Return as percentage of price for normalization
    return atr / closes.iloc[-1]
```

**Market Applications**:
- **Stop Loss Placement**: Set stops at 2x ATR to avoid market noise
- **Position Sizing**: Normalize risk across different volatility regimes
- **Volatility Filtering**: Avoid trading during extreme volatility periods

### Standard Deviation vs ATR

**Standard Deviation**:
- Measures dispersion of returns
- Assumes normal distribution
- Doesn't account for gaps

**ATR Advantages**:
- Captures gap risk
- More robust to outliers
- Better for stop-loss placement
- Reflects actual trading risk

---

## 🎯 Risk Management Framework

### Multi-Layer Risk Control

**Layer 1: Portfolio Level**
```python
# Maximum leverage constraint
if context.account.leverage > self.risk_params['max_leverage']:
    return False  # Stop all trading

# Daily loss limit (circuit breaker)
if self.portfolio['daily_pnl'] < self.risk_params['daily_loss_limit']:
    return False  # Stop trading for the day
```

**Layer 2: Position Level**
```python
# Maximum position size (diversification)
max_size = min(position_size, self.risk_params['max_position_size'])

# Asset blacklist (avoid problematic securities)
if asset in self.risk_params['trade_blacklist']:
    continue  # Skip this asset
```

**Layer 3: Trade Level**
```python
# Stop loss (limit downside)
stop_loss = entry_price * (1 - self.risk_params['stop_loss_pct'])

# Take profit (lock in gains)
take_profit = entry_price * (1 + self.risk_params['take_profit_pct'])
```

### Risk-Adjusted Returns

**Sharpe Ratio**: (Return - Risk-free Rate) / Standard Deviation
- Measures return per unit of risk
- Higher is better
- Typical good values: 1.0-2.0

**Maximum Drawdown**: Largest peak-to-trough decline
- Measures worst-case scenario
- Critical for position sizing
- Should be limited to acceptable levels

**Implementation**:
```python
def _calculate_drawdown(self, context) -> float:
    """Calculate current drawdown from peak"""
    if self.portfolio['peak_value'] is None:
        return 0.0
    
    current_value = context.portfolio.portfolio_value
    peak_value = self.portfolio['peak_value']
    
    return (current_value - peak_value) / peak_value
```

---

## 📈 Signal Generation Theory

### Factor-Based Approach

**Single Factor Example** (Momentum):
```python
def calculate_momentum(self, prices, window=20):
    """Calculate price momentum factor"""
    return (prices.iloc[-1] / prices.iloc[-window]) - 1
```

**Multi-Factor Combination**:
```python
def generate_signals(self, context, data):
    signals = {}
    
    for asset in context.universe:
        prices = data.history(asset, 'price', 60, '1d')
        
        # Factor 1: Momentum
        momentum = self.calculate_momentum(prices, 20)
        
        # Factor 2: Mean Reversion
        mean_reversion = self.calculate_mean_reversion(prices, 10)
        
        # Factor 3: Volatility
        volatility = prices.pct_change().std()
        
        # Combine factors with weights
        signal = (0.4 * momentum + 
                 0.3 * mean_reversion + 
                 0.3 * (1/volatility))  # Prefer low volatility
        
        # Normalize to [-1, 1] range
        signals[asset] = np.tanh(signal)
    
    return signals
```

### Signal Strength Interpretation

**Continuous Scale** (-1.0 to +1.0):
- **+1.0**: Maximum long conviction (100% of allowed position)
- **+0.5**: Moderate long conviction (50% of allowed position)
- **0.0**: Neutral (no position)
- **-0.5**: Moderate short conviction (50% short position)
- **-1.0**: Maximum short conviction (100% short position)

**Advantages**:
- Allows for position sizing based on conviction
- Enables gradual position adjustments
- Reflects uncertainty in predictions

---

## 🔄 Rebalancing Theory

### Frequency Considerations

**Daily Rebalancing** (BaseStrategy default):
- **Pros**: Fresh signals, responsive to market changes
- **Cons**: Higher transaction costs, more noise

**Weekly/Monthly Rebalancing**:
- **Pros**: Lower costs, focuses on persistent signals
- **Cons**: Slower response to market changes

**Implementation**:
```python
def _setup_schedules(self):
    """Configure rebalancing frequency"""
    # Daily rebalancing (default)
    schedule_function(
        self.rebalance,
        date_rules.every_day(),
        time_rules.market_open(minutes=30)
    )
    
    # Alternative: Weekly rebalancing
    # schedule_function(
    #     self.rebalance,
    #     date_rules.week_start(),
    #     time_rules.market_open(minutes=30)
    # )
```

### Transaction Cost Optimization

**Cost Components**:
1. **Commission**: Fixed cost per trade
2. **Bid-Ask Spread**: Market maker profit
3. **Market Impact**: Price movement from large orders
4. **Slippage**: Execution price vs expected price

**BaseStrategy Implementation**:
```python
def _setup_trading_costs(self):
    """Realistic trading costs"""
    # Commission: 0.1% per trade (typical Indian broker)
    set_commission(commission.PerTrade(cost=0.001))
    
    # Slippage: Volume-based market impact
    set_slippage(slippage.VolumeShareSlippage(
        volume_limit=0.1,    # Max 10% of daily volume
        price_impact=0.1     # Linear price impact
    ))
```

---

## 🧠 Behavioral Finance Considerations

### Common Cognitive Biases

**Confirmation Bias**: Seeking information that confirms existing beliefs
- **Solution**: Systematic signal generation, backtesting

**Loss Aversion**: Feeling losses more acutely than equivalent gains
- **Solution**: Predetermined stop losses, position sizing

**Overconfidence**: Overestimating prediction accuracy
- **Solution**: Conservative position sizing, diversification

**Anchoring**: Over-relying on first piece of information
- **Solution**: Multiple factor analysis, regular rebalancing

### Systematic Approach Benefits

**BaseStrategy Framework Addresses**:
1. **Removes Emotion**: Automated execution based on rules
2. **Consistent Application**: Same logic applied to all assets
3. **Risk Control**: Systematic position sizing and stop losses
4. **Performance Tracking**: Objective measurement of results

---

## 📊 Performance Attribution

### Factor Analysis

**Purpose**: Understand what drives strategy returns

**Implementation**:
```python
def record_factor(self, factor_name: str, factor_value: float, context=None):
    """Record factor data for analysis"""
    current_time = get_datetime()
    
    # Store internally
    if factor_name not in self.recorded_factors:
        self.recorded_factors[factor_name] = {}
    
    self.recorded_factors[factor_name][current_time] = factor_value
    
    # Record in Zipline for extraction
    if context is not None:
        record(**{f"factor_{factor_name}": factor_value})
```

**Analysis Applications**:
- **Factor Exposure**: How much return comes from each factor
- **Risk Attribution**: Which factors contribute to volatility
- **Performance Attribution**: Decompose returns by source

### Benchmark Comparison

**Relative Performance Metrics**:
- **Alpha**: Excess return vs benchmark
- **Beta**: Sensitivity to market movements
- **Information Ratio**: Alpha / Tracking Error
- **Tracking Error**: Standard deviation of excess returns

**Implementation**:
```python
def initialize(self, context):
    # Set benchmark for comparison
    if hasattr(self, 'benchmark_symbol'):
        set_benchmark(symbol(self.benchmark_symbol))
```

---

*This document provides the theoretical foundation for understanding the market concepts implemented in the BaseStrategy framework, bridging academic finance theory with practical trading implementation.*
