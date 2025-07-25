# 📛 BaseStrategy Code Reference: Method-by-Method Analysis

## 🔍 Overview
This document provides detailed code-level analysis of every method in the BaseStrategy class, explaining the implementation logic, market concepts, and practical applications.

---

## 🏗️ Constructor: `__init__(self)`

### Purpose
Initializes the strategy framework with default risk parameters and state tracking structures.

### Code Analysis
```python
def __init__(self):
    # Risk Parameters (override in child classes)
    self.risk_params = {
        'max_leverage': 1.0,          # 1x portfolio value
        'stop_loss_pct': 0.08,       # 8% trailing stop
        'take_profit_pct': 0.20,      # 20% profit target
        'max_position_size': 0.1,     # 10% per position
        'daily_loss_limit': -0.05,    # -5% daily drawdown
        'trade_blacklist': set()      # Assets to avoid
    }
```

**Market Concept**: These parameters implement institutional-grade risk management:
- **Max Leverage (1.0)**: Conservative approach avoiding margin amplification
- **Stop Loss (8%)**: Based on typical market noise levels for daily strategies
- **Take Profit (20%)**: 2.5:1 reward-to-risk ratio for positive expectancy
- **Position Size (10%)**: Diversification across minimum 10 positions
- **Daily Loss Limit (5%)**: Circuit breaker for risk management

### State Tracking Initialization
```python
# State tracking
self.signals = {}                    # Current trading signals
self.positions = {}                  # Active position metadata
self.portfolio = {                   # Portfolio-level metrics
    'peak_value': None,
    'daily_pnl': 0
}

# Factor data for Alphalens analysis
self.factor_data = None
self.recorded_factors = {}
```

**Implementation Logic**: Separates concerns between signal generation, position management, and performance tracking for clean architecture.

---

## 🎯 Abstract Methods

### `select_universe(self, context) -> List[Asset]`

**Purpose**: Define the tradeable universe for the strategy.

**Market Concept**: Universe selection is crucial for strategy performance:
- **Liquidity Filtering**: Ensure sufficient trading volume
- **Sector Diversification**: Avoid concentration risk
- **Market Cap Considerations**: Large-cap vs small-cap characteristics

**Implementation Pattern**:
```python
def select_universe(self, context):
    """Example implementation"""
    # Method 1: Static universe
    return [symbol('SBIN'), symbol('RELIANCE'), symbol('HDFCBANK')]
    
    # Method 2: Dynamic filtering
    all_assets = context.asset_finder.retrieve_all()
    liquid_assets = [asset for asset in all_assets 
                    if self.is_liquid(asset, context)]
    return liquid_assets[:50]  # Top 50 by liquidity
```

### `generate_signals(self, context, data) -> Dict[Asset, float]`

**Purpose**: Core alpha generation logic producing target portfolio weights.

**Signal Interpretation**:
- **+1.0**: Maximum long conviction (100% of allowed position)
- **0.0**: Neutral/no position
- **-1.0**: Maximum short conviction (100% short position)

**Market Concepts Applied**:
```python
def generate_signals(self, context, data):
    """Multi-factor signal example"""
    signals = {}
    
    for asset in context.universe:
        # Technical factor: Momentum
        prices = data.history(asset, 'price', 20, '1d')
        momentum = (prices.iloc[-1] / prices.iloc[0]) - 1
        
        # Risk factor: Volatility
        returns = prices.pct_change().dropna()
        volatility = returns.std()
        
        # Combine factors with risk adjustment
        if momentum > 0.05 and volatility < 0.03:
            signal = min(0.8, momentum * 2)  # Cap at 80% conviction
        else:
            signal = 0.0
            
        signals[asset] = signal
        
        # Record for analysis
        self.record_factor('momentum', momentum, context)
        self.record_factor('volatility', volatility, context)
    
    return signals
```

---

## 🔧 Initialization Methods

### `initialize(self, context)`

**Purpose**: One-time setup called by Zipline at backtest start.

**Execution Flow**:
1. **Trading Costs Setup**: Commission and slippage models
2. **Schedule Configuration**: When to execute trading logic
3. **Universe Selection**: Define tradeable assets
4. **Benchmark Setting**: Performance comparison baseline

```python
def initialize(self, context):
    """Zipline setup (override if needed)"""
    strategy_logger.info("🔧 INITIALIZING STRATEGY")
    
    self.context = context
    
    # Critical setup sequence
    self._setup_trading_costs()    # Must come first
    self._setup_schedules()        # Define when to trade
    
    # Universe selection
    context.universe = self.select_universe(context)
    
    # Optional benchmark setting
    if hasattr(self, 'benchmark_symbol'):
        set_benchmark(symbol(self.benchmark_symbol))
```

**Market Concept**: Proper initialization prevents look-ahead bias and ensures realistic trading costs are applied.

### `_setup_trading_costs(self)`

**Purpose**: Configure realistic transaction costs for backtesting accuracy.

```python
def _setup_trading_costs(self):
    """Realistic trading costs for NSE/BSE"""
    # Commission: 0.1% per trade (typical Indian broker)
    set_commission(commission.PerTrade(cost=0.001))
    
    # Slippage: Volume-based market impact
    set_slippage(slippage.VolumeShareSlippage(
        volume_limit=0.1,    # Max 10% of volume
        price_impact=0.1     # 10% price impact coefficient
    ))
```

**Market Reality**: These parameters reflect actual trading costs in Indian markets:
- **Commission**: Includes brokerage, STT, and other charges
- **Slippage**: Models market impact from large orders

### `_setup_schedules(self)`

**Purpose**: Define when trading logic executes during market hours.

```python
def _setup_schedules(self):
    """Default daily rebalance (override timings as needed)"""
    schedule_function(
        self.rebalance,                    # Function to call
        date_rules.every_day(),            # When: Every trading day
        time_rules.market_open(minutes=30) # Time: 30 min after open
    )
```

**Market Timing Logic**: 
- **30-minute delay**: Avoids opening auction volatility
- **Daily frequency**: Balances signal freshness with transaction costs
- **Market hours**: Ensures sufficient liquidity for execution

---

## 📊 Risk Management Methods

### `_pre_trade_checks(self, context) -> bool`

**Purpose**: Gatekeeper function preventing trades during high-risk conditions.

```python
def _pre_trade_checks(self, context) -> bool:
    """Gatekeeper for all trading activity"""
    # 1. Leverage check
    if context.account.leverage > self.risk_params['max_leverage']:
        logging.warning(f"Leverage {context.account.leverage:.2f} exceeds limit")
        return False
        
    # 2. Daily loss breaker
    if self.portfolio['daily_pnl'] < self.risk_params['daily_loss_limit']:
        logging.warning(f"Daily loss limit hit: {self.portfolio['daily_pnl']:.2%}")
        return False
        
    # 3. Blackout period check
    if self._in_blackout_period():
        return False
        
    return True
```

**Risk Control Hierarchy**:
1. **Leverage Control**: Prevents excessive margin usage
2. **Loss Limits**: Circuit breaker for bad trading days
3. **Blackout Periods**: Avoids trading during high-risk events

### `_calculate_position_size(self, context, data, asset, target) -> float`

**Purpose**: Van Tharp-style position sizing with volatility adjustment.

```python
def _calculate_position_size(self, context, data, asset, target) -> float:
    """Van Tharp-style position sizing with volatility scaling"""
    # Store data context for ATR calculation
    self._current_data = data
    
    price = data.current(asset, 'price')
    atr = self._get_atr(asset, window=20)
    
    # Dynamic stop based on 2x ATR
    stop_distance = 2 * atr if atr > 0 else 0.02
    risk_per_trade = context.portfolio.portfolio_value * 0.01  # 1% risk
    
    # Position Size = Risk Amount / Stop Distance
    if stop_distance > 0:
        position_size = risk_per_trade / (stop_distance * price)
        max_size = min(abs(position_size), self.risk_params['max_position_size'])
    else:
        max_size = self.risk_params['max_position_size'] * 0.5
        
    return np.sign(target) * max_size
```

**Van Tharp Method Explained**:
1. **Fixed Risk**: Each trade risks 1% of portfolio
2. **Variable Position Size**: Adjusted for asset volatility
3. **Stop Distance**: Based on 2x ATR (market noise level)
4. **Result**: Consistent risk across all positions

**Market Application**: High volatility assets get smaller positions, low volatility assets get larger positions, normalizing risk exposure.

---

## 📈 Execution Methods

### `rebalance(self, context, data)`

**Purpose**: Main trading workflow orchestrator called on schedule.

```python
def rebalance(self, context, data):
    """Orchestrates the entire trade workflow"""
    # Store data context for use in other methods
    self._current_data = data
    
    # Risk management gate
    if not self._pre_trade_checks(context):
        return
        
    # Core trading workflow
    self.signals = self.generate_signals(context, data)  # Get signals
    self._execute_trades(context, data)                  # Place orders
    self._record_metrics(context)                        # Track performance
```

**Execution Sequence**:
1. **Data Context**: Store for use in helper methods
2. **Risk Gate**: Check if trading is allowed
3. **Signal Generation**: Get target positions
4. **Trade Execution**: Place orders with risk controls
5. **Metrics Recording**: Track performance and factors

### `_execute_trades(self, context, data)`

**Purpose**: Convert signals to actual orders with risk controls.

```python
def _execute_trades(self, context, data):
    """Risk-aware order execution"""
    executed_trades = 0
    
    for asset, target in self.signals.items():
        # Skip blacklisted assets
        if asset in self.risk_params['trade_blacklist']:
            continue
        
        # Calculate risk-adjusted position size
        size = self._calculate_position_size(context, data, asset, target)
        
        # Update stop losses for position management
        self._update_stop_losses(asset, size, data.current(asset, 'price'))
        
        # Execute if size is meaningful
        if abs(size) > 0.001:  # Minimum size threshold
            order_target_percent(asset, size)
            executed_trades += 1
            
    strategy_logger.info(f"✅ Executed {executed_trades} trades")
```

**Order Management Logic**:
- **Blacklist Filtering**: Avoid problematic assets
- **Size Calculation**: Risk-adjusted position sizing
- **Stop Loss Updates**: Maintain risk controls
- **Minimum Size**: Avoid tiny positions with high transaction costs

---

## 🧮 Technical Analysis Methods

### `_get_atr(self, asset, window=14) -> float`

**Purpose**: Calculate Average True Range for volatility measurement.

```python
def _get_atr(self, asset, window=14) -> float:
    """Calculate Average True Range for volatility-based position sizing."""
    try:
        if hasattr(self, '_current_data') and self._current_data is not None:
            data = self._current_data
            
            # Get OHLC data with fallback
            try:
                highs = data.history(asset, 'high', window + 1, '1d')
                lows = data.history(asset, 'low', window + 1, '1d')
                closes = data.history(asset, 'close', window + 1, '1d')
            except:
                # Fallback to price data if OHLC not available
                prices = data.history(asset, 'price', window + 1, '1d')
                highs = lows = closes = prices
            
            # Calculate True Range components
            prev_close = closes.shift(1)
            tr1 = highs - lows                    # Intraday range
            tr2 = abs(highs - prev_close)         # Gap up volatility
            tr3 = abs(lows - prev_close)          # Gap down volatility
            
            # True Range is maximum of three components
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR is simple moving average of True Range
            atr = true_range.rolling(window=window).mean().iloc[-1]
            
            # Return as percentage of current price
            current_price = closes.iloc[-1]
            return atr / current_price if current_price > 0 else 0.02
            
    except Exception as e:
        strategy_logger.warning(f"ATR calculation error for {asset.symbol}: {e}")
        return 0.02  # 2% fallback
```

**ATR Components Explained**:
1. **TR1 (High - Low)**: Normal intraday volatility
2. **TR2 (|High - Prev Close|)**: Measures gap-up scenarios
3. **TR3 (|Low - Prev Close|)**: Measures gap-down scenarios

**Market Application**: ATR captures volatility that simple standard deviation misses, especially gaps between trading sessions.

---

*This code reference provides implementation-level details for every critical method in the BaseStrategy framework, combining technical analysis with practical market applications.*
