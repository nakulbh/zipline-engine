"""
Volume Spike Reversal Strategy

Concept: Sudden spike in volume indicates possible exhaustion of current trend and reversal.

Entry Logic:
1. Identify candle where volume > 2× average volume of last N candles (e.g., 20)
2. Combine with price reversal pattern (e.g., pin bar, engulfing)
3. Trade in the opposite direction

Exit: Fixed target (e.g., ATR-based) or trailing stop
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, record
from engine.base_strategy import BaseStrategy


def volume_spike(volume_series, window=20, factor=2):
    """
    Identify volume spikes.
    
    Args:
        volume_series: pandas Series of volume data
        window: Rolling window for average volume calculation
        factor: Multiplier for volume spike detection
    
    Returns:
        Boolean series indicating volume spikes
    """
    avg_vol = volume_series.rolling(window=window, min_periods=window).mean()
    return volume_series > (avg_vol * factor)


def calculate_atr(high, low, close, window=14):
    """
    Calculate Average True Range for volatility-based targets.
    
    Args:
        high, low, close: Price series
        window: ATR calculation window
    
    Returns:
        ATR series
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=window, min_periods=window).mean()


def detect_pin_bar(open_price, high, low, close, threshold=0.7):
    """
    Detect pin bar reversal pattern.
    
    Args:
        open_price, high, low, close: Price series
        threshold: Minimum ratio for pin bar identification
    
    Returns:
        Series with 1 for bullish pin bar, -1 for bearish pin bar, 0 for no pattern
    """
    body = abs(close - open_price)
    candle_range = high - low
    
    # Avoid division by zero
    candle_range = candle_range.replace(0, np.nan)
    
    upper_shadow = high - np.maximum(open_price, close)
    lower_shadow = np.minimum(open_price, close) - low
    
    # Bullish pin bar (long lower shadow)
    bullish_pin = (
        (lower_shadow / candle_range >= threshold) &
        (body / candle_range <= 0.3) &
        (close > open_price)  # Close above open
    )
    
    # Bearish pin bar (long upper shadow)
    bearish_pin = (
        (upper_shadow / candle_range >= threshold) &
        (body / candle_range <= 0.3) &
        (close < open_price)  # Close below open
    )
    
    signals = pd.Series(0, index=close.index)
    signals[bullish_pin] = 1
    signals[bearish_pin] = -1
    
    return signals


def detect_engulfing_pattern(open_price, high, low, close):
    """
    Detect engulfing candlestick pattern.
    
    Returns:
        Series with 1 for bullish engulfing, -1 for bearish engulfing, 0 for no pattern
    """
    prev_open = open_price.shift(1)
    prev_close = close.shift(1)
    
    # Bullish engulfing: current candle engulfs previous bearish candle
    bullish_engulfing = (
        (prev_close < prev_open) &  # Previous candle was bearish
        (close > open_price) &      # Current candle is bullish
        (open_price < prev_close) & # Current open below previous close
        (close > prev_open)         # Current close above previous open
    )
    
    # Bearish engulfing: current candle engulfs previous bullish candle
    bearish_engulfing = (
        (prev_close > prev_open) &  # Previous candle was bullish
        (close < open_price) &      # Current candle is bearish
        (open_price > prev_close) & # Current open above previous close
        (close < prev_open)         # Current close below previous open
    )
    
    signals = pd.Series(0, index=close.index)
    signals[bullish_engulfing] = 1
    signals[bearish_engulfing] = -1
    
    return signals


class VolumeSpikeReversalStrategy(BaseStrategy):
    """
    Volume Spike Reversal Strategy Implementation
    
    This strategy identifies potential trend reversals based on:
    1. Volume spikes (volume > 2x average)
    2. Reversal candlestick patterns (pin bars, engulfing)
    3. Trades in the opposite direction of the spike
    """
    
    def _initialize_strategy(self, context):
        """Initialize strategy parameters."""
        # Strategy parameters
        self.stocks = self.params.get('stocks', [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'NFLX', 'AMD', 'CRM'
        ])
        
        # Volume spike parameters
        self.volume_window = self.params.get('volume_window', 20)
        self.volume_factor = self.params.get('volume_factor', 2.0)
        
        # Pattern detection parameters
        self.pin_bar_threshold = self.params.get('pin_bar_threshold', 0.7)
        self.use_pin_bars = self.params.get('use_pin_bars', True)
        self.use_engulfing = self.params.get('use_engulfing', True)
        
        # Position sizing and risk management
        self.max_positions = self.params.get('max_positions', 5)
        self.position_size = self.params.get('position_size', 0.1)  # 10% per position
        
        # ATR parameters for targets and stops
        self.atr_window = self.params.get('atr_window', 14)
        self.atr_target_multiplier = self.params.get('atr_target_multiplier', 2.0)
        self.atr_stop_multiplier = self.params.get('atr_stop_multiplier', 1.0)
        
        # Holding period
        self.max_hold_days = self.params.get('max_hold_days', 10)
        
        # Track positions and entry details
        self.positions_data = {}
        self.entry_dates = {}
        
        self.logger.info(f"Volume Spike Reversal Strategy initialized")
        self.logger.info(f"Stocks: {self.stocks}")
        self.logger.info(f"Volume window: {self.volume_window}, factor: {self.volume_factor}")
        
    def _initialize_universe(self, context):
        """Initialize trading universe."""
        try:
            self.universe = [symbol(stock) for stock in self.stocks]
            self.logger.info(f"Universe initialized with {len(self.universe)} stocks")
        except Exception as e:
            self.logger.error(f"Error initializing universe: {e}")
            self.universe = []
    
    def _handle_strategy_data(self, context, data):
        """Main strategy logic - executed daily."""
        current_date = context.get_datetime()
        
        # Check exit conditions for existing positions
        self._check_exit_conditions(context, data, current_date)
        
        # Look for new entry signals
        self._scan_for_entries(context, data, current_date)
    
    def _scan_for_entries(self, context, data, current_date):
        """Scan for new entry opportunities."""
        # Don't open new positions if we're at max capacity
        current_positions = len([pos for pos in context.portfolio.positions.values() 
                               if pos.amount != 0])
        
        if current_positions >= self.max_positions:
            return
        
        for asset in self.universe:
            # Skip if we already have a position in this asset
            if asset in context.portfolio.positions and context.portfolio.positions[asset].amount != 0:
                continue
            
            # Skip if asset is not tradeable
            if not self.is_asset_tradeable(data, asset):
                continue
            
            # Get historical data
            try:
                history_data = data.history(
                    asset, 
                    ['open', 'high', 'low', 'close', 'volume'], 
                    self.volume_window + 5,  # Extra bars for calculations
                    '1d'
                )
                
                if len(history_data) < self.volume_window + 1:
                    continue
                
                # Detect volume spike
                volume_spikes = volume_spike(
                    history_data['volume'], 
                    window=self.volume_window, 
                    factor=self.volume_factor
                )
                
                # Check if there was a volume spike in the latest candle
                if not volume_spikes.iloc[-1]:
                    continue
                
                # Detect reversal patterns
                reversal_signal = 0
                
                if self.use_pin_bars:
                    pin_signals = detect_pin_bar(
                        history_data['open'], 
                        history_data['high'], 
                        history_data['low'], 
                        history_data['close'],
                        threshold=self.pin_bar_threshold
                    )
                    if pin_signals.iloc[-1] != 0:
                        reversal_signal = pin_signals.iloc[-1]
                
                if self.use_engulfing and reversal_signal == 0:
                    engulfing_signals = detect_engulfing_pattern(
                        history_data['open'], 
                        history_data['high'], 
                        history_data['low'], 
                        history_data['close']
                    )
                    if engulfing_signals.iloc[-1] != 0:
                        reversal_signal = engulfing_signals.iloc[-1]
                
                # Enter position if we have both volume spike and reversal pattern
                if reversal_signal != 0:
                    self._enter_position(context, data, asset, reversal_signal, history_data, current_date)
                    
            except Exception as e:
                self.logger.error(f"Error processing {asset}: {e}")
                continue
    
    def _enter_position(self, context, data, asset, signal, history_data, current_date):
        """Enter a new position."""
        try:
            # Calculate ATR for stop loss and target
            atr = calculate_atr(
                history_data['high'], 
                history_data['low'], 
                history_data['close'], 
                window=self.atr_window
            )
            current_atr = atr.iloc[-1]
            current_price = data.current(asset, 'close')
            
            if pd.isna(current_atr) or current_atr <= 0:
                self.logger.warning(f"Invalid ATR for {asset}, skipping entry")
                return
            
            # Calculate stop loss and target based on ATR
            if signal > 0:  # Bullish reversal - go long
                direction = 'long'
                stop_loss = current_price - (current_atr * self.atr_stop_multiplier)
                target_price = current_price + (current_atr * self.atr_target_multiplier)
                position_percent = self.position_size
            else:  # Bearish reversal - go short
                direction = 'short'
                stop_loss = current_price + (current_atr * self.atr_stop_multiplier)
                target_price = current_price - (current_atr * self.atr_target_multiplier)
                position_percent = -self.position_size
            
            # Place the order
            order_id = self.safe_order_target_percent(context, asset, position_percent)
            
            if order_id:
                # Store position data for exit management
                self.positions_data[asset] = {
                    'direction': direction,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'target_price': target_price,
                    'atr': current_atr,
                    'signal': signal
                }
                self.entry_dates[asset] = current_date
                
                self.logger.info(
                    f"Entered {direction} position in {asset} at ${current_price:.2f}, "
                    f"Target: ${target_price:.2f}, Stop: ${stop_loss:.2f}, ATR: ${current_atr:.2f}"
                )
                
        except Exception as e:
            self.logger.error(f"Error entering position for {asset}: {e}")
    
    def _check_exit_conditions(self, context, data, current_date):
        """Check exit conditions for existing positions."""
        positions_to_close = []
        
        for asset in context.portfolio.positions:
            position = context.portfolio.positions[asset]
            
            # Skip if no position
            if position.amount == 0:
                continue
            
            # Skip if we don't have tracking data (shouldn't happen)
            if asset not in self.positions_data:
                continue
            
            try:
                current_price = data.current(asset, 'close')
                position_data = self.positions_data[asset]
                entry_date = self.entry_dates.get(asset)
                
                # Check maximum holding period
                if entry_date:
                    days_held = (current_date - entry_date).days
                    if days_held >= self.max_hold_days:
                        positions_to_close.append((asset, 'max_hold_time'))
                        continue
                
                # Check stop loss and target conditions
                direction = position_data['direction']
                stop_loss = position_data['stop_loss']
                target_price = position_data['target_price']
                
                if direction == 'long':
                    if current_price <= stop_loss:
                        positions_to_close.append((asset, 'stop_loss'))
                    elif current_price >= target_price:
                        positions_to_close.append((asset, 'target_reached'))
                else:  # short
                    if current_price >= stop_loss:
                        positions_to_close.append((asset, 'stop_loss'))
                    elif current_price <= target_price:
                        positions_to_close.append((asset, 'target_reached'))
                        
            except Exception as e:
                self.logger.error(f"Error checking exit conditions for {asset}: {e}")
                positions_to_close.append((asset, 'error'))
        
        # Close positions that meet exit criteria
        for asset, reason in positions_to_close:
            self._close_position(context, asset, reason)
    
    def _close_position(self, context, asset, reason):
        """Close a position and clean up tracking data."""
        try:
            # Close the position
            order_id = self.safe_order_target_percent(context, asset, 0)
            
            if order_id:
                position_data = self.positions_data.get(asset, {})
                entry_price = position_data.get('entry_price', 0)
                direction = position_data.get('direction', 'unknown')
                
                # Get current price for P&L calculation
                try:
                    current_price = context.portfolio.positions[asset].last_sale_price
                    if direction == 'long':
                        pnl_pct = (current_price - entry_price) / entry_price * 100
                    else:
                        pnl_pct = (entry_price - current_price) / entry_price * 100
                except:
                    pnl_pct = 0
                
                self.logger.info(
                    f"Closed {direction} position in {asset} due to {reason}, "
                    f"Entry: ${entry_price:.2f}, Exit: ${current_price:.2f}, "
                    f"P&L: {pnl_pct:.2f}%"
                )
                
                # Clean up tracking data
                if asset in self.positions_data:
                    del self.positions_data[asset]
                if asset in self.entry_dates:
                    del self.entry_dates[asset]
                    
        except Exception as e:
            self.logger.error(f"Error closing position for {asset}: {e}")
    
    def rebalance_portfolio(self, context, data):
        """Rebalancing logic - not used in this strategy as positions are managed in handle_data."""
        # This strategy manages positions dynamically in _handle_strategy_data
        # No periodic rebalancing needed
        pass
    
    def _record_strategy_metrics(self, context):
        """Record strategy-specific metrics."""
        try:
            # Count positions by direction
            long_positions = 0
            short_positions = 0
            total_unrealized_pnl = 0
            
            for asset in context.portfolio.positions:
                position = context.portfolio.positions[asset]
                if position.amount == 0:
                    continue
                    
                if asset in self.positions_data:
                    direction = self.positions_data[asset]['direction']
                    if direction == 'long':
                        long_positions += 1
                    else:
                        short_positions += 1
                    
                    # Calculate unrealized P&L
                    entry_price = self.positions_data[asset]['entry_price']
                    current_price = position.last_sale_price
                    position_value = abs(position.amount) * current_price
                    
                    if direction == 'long':
                        pnl = (current_price - entry_price) / entry_price * position_value
                    else:
                        pnl = (entry_price - current_price) / entry_price * position_value
                    
                    total_unrealized_pnl += pnl
            
            # Record metrics
            record(
                long_positions=long_positions,
                short_positions=short_positions,
                total_positions=long_positions + short_positions,
                unrealized_pnl=total_unrealized_pnl,
                max_positions_used=len(self.positions_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error recording strategy metrics: {e}")


# Example configuration for Volume Spike Reversal Strategy
VOLUME_SPIKE_CONFIG = {
    'stocks': [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
        'META', 'NVDA', 'NFLX', 'AMD', 'CRM',
        'JPM', 'BAC', 'WMT', 'JNJ', 'PG'
    ],
    'volume_window': 20,
    'volume_factor': 2.0,
    'pin_bar_threshold': 0.7,
    'use_pin_bars': True,
    'use_engulfing': True,
    'max_positions': 5,
    'position_size': 0.1,  # 10% per position
    'atr_window': 14,
    'atr_target_multiplier': 2.0,
    'atr_stop_multiplier': 1.0,
    'max_hold_days': 10,
    'rebalance_frequency': 'never',  # Strategy manages positions dynamically
    'max_portfolio_leverage': 1.0,
    'commission_model': 'per_share',
    'commission_cost': 0.005,
    'commission_min': 1.0,
    'slippage_model': 'volume_share',
    'slippage_volume_limit': 0.025,
    'slippage_price_impact': 0.1,
    'benchmark': 'SPY',
    'cancel_unfilled_orders': True,
    'max_errors': 20
}


if __name__ == "__main__":
    # Example usage
    print("Volume Spike Reversal Strategy defined.")
    print("Use with ZiplineBacktestEngine:")
    print("\nstrategy = VolumeSpikeReversalStrategy(VOLUME_SPIKE_CONFIG)")
    print("engine = ZiplineBacktestEngine(strategy=strategy, capital_base=100000)")
    print("results = engine.run('2020-01-01', '2023-12-31')")