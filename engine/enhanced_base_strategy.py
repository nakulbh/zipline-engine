from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
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
        # Risk Parameters for Indian Markets (override in child classes)
        self.risk_params = {
            'max_leverage': 1.0,          # 1x portfolio value (SEBI regulations)
            'stop_loss_pct': 0.05,       # 5% trailing stop (Indian market volatility)
            'take_profit_pct': 0.15,      # 15% profit target
            'max_position_size': 0.08,    # 8% per position (more conservative)
            'daily_loss_limit': -0.03,    # -3% daily drawdown (circuit breakers)
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
        """Default commission/slippage model for Indian markets"""
        # For Indian markets - use direct model assignment (not us_equities parameter)
        set_commission(commission.PerTrade(cost=20.00))  # ₹20 per trade (typical Indian brokerage)
        set_slippage(slippage.VolumeShareSlippage(
            volume_limit=0.025,  # More conservative for Indian markets
            price_impact=0.05    # Lower impact than default
        ))
    
    def _setup_schedules(self):
        """Default daily rebalance (override timings as needed)"""
        schedule_function(
            func=self.rebalance,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(minutes=30)
        )  # Wait for liquidity
    
    def rebalance(self, context, data):
        """Orchestrates the entire trade workflow"""
        # Store data context for use in other methods
        self._current_data = data

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
        """Van Tharp-style position sizing with volatility scaling for Indian markets"""
        # Store data context for ATR calculation
        self._current_data = data

        price = data.current(asset, 'price')
        atr = self._get_atr(asset, window=20)

        # Dynamic stop based on 2x ATR
        stop_distance = 2 * atr if atr > 0 else 0.02  # Fallback to 2% if ATR fails
        risk_per_trade = context.portfolio.portfolio_value * 0.01  # 1% risk

        # Size = Risk / Stop Distance
        if stop_distance > 0:
            position_size = risk_per_trade / (stop_distance * price)
            max_size = min(
                abs(position_size),
                self.risk_params['max_position_size']
            )
        else:
            max_size = self.risk_params['max_position_size'] * 0.5  # Conservative fallback

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
        """Calculate Average True Range for volatility-based position sizing."""
        try:
            # Get historical OHLC data
            if hasattr(self, '_current_data') and self._current_data is not None:
                data = self._current_data

                # Try to get OHLC data
                try:
                    highs = data.history(asset, 'high', window + 1, '1d')
                    lows = data.history(asset, 'low', window + 1, '1d')
                    closes = data.history(asset, 'close', window + 1, '1d')
                except:
                    # Fallback to price data if OHLC not available
                    prices = data.history(asset, 'price', window + 1, '1d')
                    highs = lows = closes = prices

                if len(closes) < 2:
                    return 0.02  # 2% fallback for new assets

                # Calculate True Range
                prev_close = closes.shift(1)
                tr1 = highs - lows
                tr2 = abs(highs - prev_close)
                tr3 = abs(lows - prev_close)

                true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

                # Calculate ATR as simple moving average of True Range
                atr = true_range.rolling(window=window).mean().iloc[-1]

                # Return ATR as percentage of current price
                current_price = closes.iloc[-1]
                return atr / current_price if current_price > 0 else 0.02

            else:
                # Fallback when no data context available
                return 0.02  # 2% fallback

        except Exception as e:
            strategy_logger.warning(f"ATR calculation error for {asset.symbol}: {e}")
            return 0.02  # 2% fallback