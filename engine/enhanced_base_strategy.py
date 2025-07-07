from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np
from zipline.api import (
    order_target_percent, record, symbol, get_datetime,
    schedule_function, date_rules, time_rules, get_open_orders,
    cancel_order, order, order_target, get_order, set_commission,
    set_slippage
)
from zipline.assets import Asset
from zipline.finance import commission, slippage
import logging

# Create logger for strategy execution
strategy_logger = logging.getLogger('strategy')
strategy_logger.setLevel(logging.INFO)

class BaseStrategy(ABC):
    """Complete strategy template with risk management and execution logic"""
    
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

        # State tracking
        self.signals = {}
        self.positions = {}  # {symbol: {'entry_price': 100, 'stop_loss': 92}}
        self.portfolio = {
            'peak_value': None,
            'daily_pnl': 0
        }

        # Factor data for Alphalens analysis
        self.factor_data = None
        self.recorded_factors = {}

        # Initialize strategy logging
        strategy_logger.info(f"🎯 Initializing strategy: {self.__class__.__name__}")
        strategy_logger.info(f"⚙️  Risk Parameters: {self.risk_params}")

    # ------------ Core Methods (Must Implement) ------------ #
    @abstractmethod
    def select_universe(self, context) -> List[Asset]:
        """Define tradeable assets (override this)"""
        pass
    
    @abstractmethod
    def generate_signals(self, context, data) -> Dict[Asset, float]:
        """
        Return target weights {-1.0 to 1.0} 
        Example: {'AAPL': 0.5, 'TSLA': -0.3}
        """
        pass
    
    # ------------ Optional Customization ------------ #
    def initialize(self, context):
        """Zipline setup (override if needed)"""
        strategy_logger.info("🔧 INITIALIZING STRATEGY")
        strategy_logger.info("-" * 30)

        self.context = context

        strategy_logger.info("💰 Setting up trading costs...")
        self._setup_trading_costs()

        strategy_logger.info("📅 Setting up trading schedules...")
        self._setup_schedules()

        strategy_logger.info("🌐 Selecting trading universe...")
        context.universe = self.select_universe(context)
        strategy_logger.info(f"   ✅ Universe size: {len(context.universe) if hasattr(context, 'universe') else 'Unknown'}")

        # Set benchmark if specified
        if hasattr(self, 'benchmark_symbol') and self.benchmark_symbol:
            strategy_logger.info(f"📊 Setting benchmark: {self.benchmark_symbol}")
            try:
                from zipline.api import set_benchmark, symbol
                set_benchmark(symbol(self.benchmark_symbol))
                strategy_logger.info(f"   ✅ Benchmark set to {self.benchmark_symbol}")
            except Exception as e:
                strategy_logger.warning(f"   ⚠️  Failed to set benchmark {self.benchmark_symbol}: {e}")

        strategy_logger.info("✅ Strategy initialization completed!")
        strategy_logger.info("=" * 50)
        
    def before_trading_start(self, context, data):
        """Pre-market checks (override if needed)"""
        current_date = get_datetime().strftime('%Y-%m-%d')
        strategy_logger.debug(f"📅 Pre-market checks for {current_date}")
        self._update_risk_metrics(context)
    
    # ------------ Built-In Execution Logic ------------ #
    def _setup_trading_costs(self):
        """Default commission/slippage model"""
        set_commission(commission.PerTrade(cost=5.00))  # $5 per trade
        set_slippage(slippage.VolumeShareSlippage(
            volume_limit=0.1, 
            price_impact=0.1
        ))
    
    def _setup_schedules(self):
        """Default daily rebalance (override timings as needed)"""
        schedule_function(
            self.rebalance,
            date_rules.every_day(),
            time_rules.market_open(minutes=30)
          )  # Wait for liquidity
    
    def rebalance(self, context, data):
        """Orchestrates the entire trade workflow"""
        if not self._pre_trade_checks(context):
            return
            
        self.signals = self.generate_signals(context, data)
        self._execute_trades(context, data)
        self._record_metrics(context)
    
    # ------------ Risk Management System ------------ #
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
            
        # 3. Blackout period (example: FOMC days)
        if self._in_blackout_period():
            return False
            
        return True
    
    def _execute_trades(self, context, data):
        """Risk-aware order execution"""
        if self.signals:
            strategy_logger.info(f"💱 Executing {len(self.signals)} trade signals...")

        executed_trades = 0
        for asset, target in self.signals.items():
            if asset in self.risk_params['trade_blacklist']:
                strategy_logger.warning(f"⚠️  Skipping blacklisted asset: {asset.symbol}")
                continue

            # Calculate position size with volatility scaling
            size = self._calculate_position_size(context, data, asset, target)

            # Apply stops
            self._update_stop_losses(asset, size, data.current(asset, 'price'))

            # Execute if size is meaningful
            if abs(size) > 0.001:
                order_target_percent(asset, size)
                executed_trades += 1
                strategy_logger.info(f"   📈 {asset.symbol}: Target {size:.1%} (Signal: {target:.3f})")
            else:
                strategy_logger.debug(f"   ⏭️  {asset.symbol}: Size too small ({size:.4f})")

        if executed_trades > 0:
            strategy_logger.info(f"✅ Executed {executed_trades} trades")

    def record_factor(self, factor_name: str, factor_value: float, context=None):
        """
        Record factor data for Alphalens analysis.

        Args:
            factor_name: Name of the factor (e.g., 'momentum', 'mean_reversion')
            factor_value: Current factor value
            context: Zipline context (optional, for additional recording)
        """
        # Store in internal tracking
        current_time = get_datetime()
        if factor_name not in self.recorded_factors:
            self.recorded_factors[factor_name] = {}

        self.recorded_factors[factor_name][current_time] = factor_value

        # Also record in Zipline for extraction later
        if context is not None:
            record(**{f"factor_{factor_name}": factor_value})

        strategy_logger.debug(f"📊 Recorded factor '{factor_name}': {factor_value:.4f}")

    def _calculate_position_size(self, context, data, asset, target) -> float:
        """Van Tharp-style position sizing with volatility scaling"""
        price = data.current(asset, 'price')
        atr = self._get_atr(asset, window=20)  # Implement your ATR calculation
        
        # Dynamic stop based on 2x ATR
        stop_distance = 2 * atr / price  
        risk_per_trade = context.portfolio.portfolio_value * 0.01  # 1% risk
        
        # Size = Risk / Stop Distance
        max_size = min(
            abs(risk_per_trade / stop_distance),
            self.risk_params['max_position_size']
        )
        return np.sign(target) * max_size
    
    def _update_stop_losses(self, asset, size, price):
        """Trailing stop logic"""
        if size == 0:
            self.positions.pop(asset, None)
        elif size > 0:  # Long position
            self.positions[asset] = {
                'stop_loss': price * (1 - self.risk_params['stop_loss_pct']),
                'take_profit': price * (1 + self.risk_params['take_profit_pct'])
            }
        else:  # Short position
            self.positions[asset] = {
                'stop_loss': price * (1 + self.risk_params['stop_loss_pct']),
                'take_profit': price * (1 - self.risk_params['take_profit_pct'])
            }
    
    # ------------ Metrics & Logging ------------ #
    def _record_metrics(self, context):
        """Track key performance stats"""
        record(
            leverage=context.account.leverage,
            drawdown=self._calculate_drawdown(context),
            positions=len(context.portfolio.positions),
            daily_pnl=self.portfolio['daily_pnl']
        )

    def _update_risk_metrics(self, context):
        """Update daily PnL and drawdown"""
        # Update peak portfolio value
        if self.portfolio['peak_value'] is None:
            self.portfolio['peak_value'] = context.portfolio.portfolio_value
        else:
            self.portfolio['peak_value'] = max(
                self.portfolio['peak_value'],
                context.portfolio.portfolio_value
            )
            
        # Calculate daily PnL
        self.portfolio['daily_pnl'] = (
            context.portfolio.portfolio_value / context.portfolio.starting_cash
        ) - 1

    def _calculate_drawdown(self, context) -> float:
        """Calculates the current drawdown from the peak portfolio value."""
        if self.portfolio['peak_value'] is None or self.portfolio['peak_value'] == 0:
            return 0.0
        return (
            (context.portfolio.portfolio_value - self.portfolio['peak_value']) /
            self.portfolio['peak_value']
        )

    def _in_blackout_period(self) -> bool:
        """Check for trading restrictions (e.g., earnings, FOMC)."""
        # Example: Avoid trading on FOMC announcement days
        # fmc_dates = [...] 
        # return get_datetime().date() in fmc_dates
        return False

    def _get_atr(self, asset, window=14) -> float:
        """Placeholder for Average True Range calculation."""
        # In a real scenario, you would use historical data to compute ATR
        # For this example, we'll return a mock value.
        # Replace with your actual ATR implementation.
        # Example: data.history(asset, 'high', window, '1d'), etc.
        return 0.01 # Mock value, replace with real calculation