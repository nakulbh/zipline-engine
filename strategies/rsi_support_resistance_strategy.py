"""
RSI Support/Resistance Strategy

This strategy combines RSI signals with Support/Resistance levels for stop loss placement.
The strategy:

1. Calculates RSI over a specified period (default 14 days)
2. Identifies key Support and Resistance levels using pivot points
3. Generates buy signals when RSI < 30 (oversold) near support
4. Generates sell signals when RSI > 70 (overbought) near resistance
5. Sets stop losses below support levels (for longs) or above resistance (for shorts)
6. Uses resistance levels as profit targets for longs, support levels for shorts

Author: NSE Backtesting Engine
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record, order_target_percent, get_datetime
import pandas as pd
import numpy as np
import logging

# Create logger for RSI S/R strategy
rsi_sr_logger = logging.getLogger('rsi_sr_strategy')
rsi_sr_logger.setLevel(logging.INFO)


class RSISupportResistanceStrategy(BaseStrategy):
    """
    RSI strategy with Support/Resistance based stop losses and profit targets.
    
    Parameters:
    - rsi_period: Period for RSI calculation (default: 14)
    - oversold_threshold: RSI level considered oversold (default: 30)
    - overbought_threshold: RSI level considered overbought (default: 70)
    - lookback_period: Period to look back for S/R levels (default: 20)
    - min_touches: Minimum touches required for valid S/R level (default: 2)
    - sr_tolerance: Price tolerance for S/R level identification (default: 0.02 = 2%)
    """
    
    def __init__(self, rsi_period=14, oversold_threshold=30, overbought_threshold=70, 
                 lookback_period=20, min_touches=2, sr_tolerance=0.02):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.lookback_period = lookback_period
        self.min_touches = min_touches
        self.sr_tolerance = sr_tolerance
        
        # Enhanced risk parameters for S/R trading (more conservative)
        self.risk_params.update({
            'max_position_size': 0.08,    # 8% per position (reduced from 12%)
            'stop_loss_pct': 0.03,        # 3% fallback stop (tighter)
            'take_profit_pct': 0.10,      # 10% fallback profit target (reduced)
            'max_leverage': 0.6,          # 60% max leverage (reduced from 90%)
        })
        
        # Strategy-specific tracking
        self.rsi_history = {}
        self.support_levels = {}      # {asset: [price_levels]}
        self.resistance_levels = {}   # {asset: [price_levels]}
        self.sr_history = {}          # Track S/R level history

    def select_universe(self, context):
        """
        Select NSE stocks for RSI S/R trading.
        Focus on liquid stocks with clear support/resistance patterns.
        """
        nse_symbols = [
            'SBIN',       # State Bank of India
            'HDFCBANK',   # HDFC Bank
            'BAJFINANCE', # Bajaj Finance
        ]
        
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            rsi_sr_logger.info(f"Selected universe: {len(universe)} assets")
            return universe
        except Exception:
            return [symbol('SBIN')]

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI - same as original strategy"""
        if len(prices) < period + 1:
            return 50
        
        delta = prices.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def identify_support_resistance(self, prices, highs=None, lows=None):
        """
        Identify Support and Resistance levels using pivot point analysis.
        
        Args:
            prices: Price series (close prices)
            highs: High prices (optional, uses prices if not provided)
            lows: Low prices (optional, uses prices if not provided)
            
        Returns:
            tuple: (support_levels, resistance_levels)
        """
        if highs is None:
            highs = prices
        if lows is None:
            lows = prices
            
        if len(prices) < self.lookback_period:
            return [], []
        
        support_levels = []
        resistance_levels = []
        
        # Find local minima (potential support) and maxima (potential resistance)
        for i in range(2, len(prices) - 2):
            # Local minimum (support)
            if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
                support_levels.append(lows.iloc[i])
            
            # Local maximum (resistance)
            if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
                resistance_levels.append(highs.iloc[i])
        
        # Cluster similar levels together
        support_levels = self._cluster_levels(support_levels, prices.iloc[-1])
        resistance_levels = self._cluster_levels(resistance_levels, prices.iloc[-1])
        
        # Filter levels by minimum touches
        support_levels = self._validate_levels(support_levels, lows, is_support=True)
        resistance_levels = self._validate_levels(resistance_levels, highs, is_support=False)
        
        return support_levels, resistance_levels

    def _cluster_levels(self, levels, current_price):
        """Group similar price levels together"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_price <= self.sr_tolerance:
                current_cluster.append(level)
            else:
                # Average the cluster
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Add the last cluster
        clustered.append(np.mean(current_cluster))
        
        return clustered

    def _validate_levels(self, levels, price_series, is_support=True):
        """Validate S/R levels by counting touches"""
        validated_levels = []
        
        for level in levels:
            touches = 0
            for price in price_series:
                if is_support:
                    # Count touches near support (price came close to level from above)
                    if abs(price - level) / level <= self.sr_tolerance and price >= level * 0.98:
                        touches += 1
                else:
                    # Count touches near resistance (price came close to level from below)
                    if abs(price - level) / level <= self.sr_tolerance and price <= level * 1.02:
                        touches += 1
            
            if touches >= self.min_touches:
                validated_levels.append(level)
        
        return validated_levels

    def get_nearest_support_resistance(self, current_price, support_levels, resistance_levels):
        """Find the nearest support below and resistance above current price"""
        # Find nearest support below current price
        supports_below = [s for s in support_levels if s < current_price]
        nearest_support = max(supports_below) if supports_below else None
        
        # Find nearest resistance above current price
        resistances_above = [r for r in resistance_levels if r > current_price]
        nearest_resistance = min(resistances_above) if resistances_above else None
        
        return nearest_support, nearest_resistance

    def generate_signals(self, context, data) -> dict:
        """
        Generate RSI signals enhanced with Support/Resistance analysis.
        """
        signals = {}

        for asset in context.universe:
            try:
                # Get historical data
                history_length = max(self.rsi_period + 10, self.lookback_period + 10)
                prices = data.history(asset, 'price', history_length, '1d')

                # Try to get OHLC data for better S/R analysis
                try:
                    highs = data.history(asset, 'high', history_length, '1d')
                    lows = data.history(asset, 'low', history_length, '1d')
                except:
                    highs = prices
                    lows = prices

                if len(prices) < self.rsi_period + 1:
                    signals[asset] = 0.0
                    continue

                # Calculate RSI
                current_rsi = self.calculate_rsi(prices, self.rsi_period)
                current_price = prices.iloc[-1]

                # Debug: Log RSI values
                rsi_sr_logger.debug(f"{asset.symbol}: RSI={current_rsi:.1f}, Price=₹{current_price:.2f}")

                # Store RSI history
                if asset not in self.rsi_history:
                    self.rsi_history[asset] = []
                self.rsi_history[asset].append(current_rsi)
                if len(self.rsi_history[asset]) > 50:
                    self.rsi_history[asset] = self.rsi_history[asset][-50:]

                # Identify Support/Resistance levels
                support_levels, resistance_levels = self.identify_support_resistance(prices, highs, lows)

                # Debug: Log S/R levels
                rsi_sr_logger.debug(f"{asset.symbol}: Found {len(support_levels)} supports, {len(resistance_levels)} resistances")

                # Store S/R levels for position management
                self.support_levels[asset] = support_levels
                self.resistance_levels[asset] = resistance_levels

                # Find nearest S/R levels
                nearest_support, nearest_resistance = self.get_nearest_support_resistance(
                    current_price, support_levels, resistance_levels)

                # Debug: Log nearest levels
                if nearest_support or nearest_resistance:
                    support_str = f"₹{nearest_support:.2f}" if nearest_support else "None"
                    resistance_str = f"₹{nearest_resistance:.2f}" if nearest_resistance else "None"
                    rsi_sr_logger.debug(f"{asset.symbol}: Nearest Support={support_str}, Resistance={resistance_str}")

                # Generate signals based on RSI + S/R confluence
                signal_strength = 0.0
                signal_reason = "No signal"

                # Generate signals with confluence preference but allow some RSI-only signals
                # Long signal: RSI oversold
                if current_rsi <= self.oversold_threshold:
                    if nearest_support and abs(current_price - nearest_support) / current_price <= 0.03:  # 3% tolerance
                        # Strong signal when RSI oversold AND near support
                        signal_strength = min(0.8, (self.oversold_threshold - current_rsi) / 10 + 0.3)
                        signal_reason = f"Strong Buy: RSI {current_rsi:.1f} + near support ₹{nearest_support:.2f}"
                    elif current_rsi <= 25:  # Very oversold - allow without confluence
                        signal_strength = min(0.5, (25 - current_rsi) / 10 + 0.2)
                        signal_reason = f"Moderate Buy: Very oversold RSI {current_rsi:.1f}"
                    else:
                        # Weak RSI signal without confluence
                        signal_strength = 0.0
                        signal_reason = f"No Buy: RSI {current_rsi:.1f} needs confluence or <25"

                # Short signal: RSI overbought
                elif current_rsi >= self.overbought_threshold:
                    if nearest_resistance and abs(current_price - nearest_resistance) / current_price <= 0.03:  # 3% tolerance
                        # Strong signal when RSI overbought AND near resistance
                        signal_strength = -min(0.8, (current_rsi - self.overbought_threshold) / 10 + 0.3)
                        signal_reason = f"Strong Sell: RSI {current_rsi:.1f} + near resistance ₹{nearest_resistance:.2f}"
                    elif current_rsi >= 75:  # Very overbought - allow without confluence
                        signal_strength = -min(0.5, (current_rsi - 75) / 10 + 0.2)
                        signal_reason = f"Moderate Sell: Very overbought RSI {current_rsi:.1f}"
                    else:
                        # Weak RSI signal without confluence
                        signal_strength = 0.0
                        signal_reason = f"No Sell: RSI {current_rsi:.1f} needs confluence or >75"

                # Log signal generation (including zero signals for debugging)
                if abs(signal_strength) > 0.01:
                    rsi_sr_logger.info(f"{asset.symbol}: {signal_reason} → Signal: {signal_strength:.3f}")
                else:
                    rsi_sr_logger.debug(f"{asset.symbol}: {signal_reason} → No signal")

                signals[asset] = signal_strength

                # Record factors for analysis
                self.record_factor('rsi', current_rsi, context)
                self.record_factor('nearest_support', nearest_support or 0, context)
                self.record_factor('nearest_resistance', nearest_resistance or 0, context)
                self.record_factor('support_distance',
                                 abs(current_price - nearest_support) / current_price if nearest_support else 1.0, context)
                self.record_factor('resistance_distance',
                                 abs(current_price - nearest_resistance) / current_price if nearest_resistance else 1.0, context)
                self.record_factor('signal_strength', abs(signal_strength), context)

                # Record current data
                record(
                    prices=current_price,
                    rsi_value=current_rsi,
                    support_level=nearest_support or 0,
                    resistance_level=nearest_resistance or 0
                )

            except Exception as e:
                rsi_sr_logger.warning(f"Signal generation error for {asset.symbol}: {e}")
                signals[asset] = 0.0
                continue

        return signals

    def rebalance(self, context, data):
        """Override rebalance to include S/R-based stop/profit checks"""
        # Store current data context
        self._current_data = data

        # Check existing positions against S/R levels
        self.check_sr_stops_profits(context, data)

        # Proceed with normal rebalancing
        super().rebalance(context, data)

    def check_sr_stops_profits(self, context, data):
        """
        Check positions against Support/Resistance levels for stops and profits.
        """
        positions_to_close = []

        for asset in list(self.positions.keys()):
            if asset not in context.portfolio.positions or context.portfolio.positions[asset].amount == 0:
                positions_to_close.append(asset)
                continue

            try:
                current_price = data.current(asset, 'price')
                position_info = self.positions[asset]
                current_position = context.portfolio.positions[asset]

                is_long = current_position.amount > 0

                # Check S/R-based stops and profits
                if is_long:
                    # Long position: stop below support, profit at resistance
                    if 'sr_stop_loss' in position_info and current_price <= position_info['sr_stop_loss']:
                        rsi_sr_logger.info(f"🛑 S/R Stop loss triggered for {asset.symbol}: "
                                         f"{current_price:.2f} <= {position_info['sr_stop_loss']:.2f}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

                    elif 'sr_take_profit' in position_info and current_price >= position_info['sr_take_profit']:
                        rsi_sr_logger.info(f"🎯 S/R Take profit triggered for {asset.symbol}: "
                                         f"{current_price:.2f} >= {position_info['sr_take_profit']:.2f}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

                    # Fallback percentage-based stops
                    elif current_price <= position_info.get('fallback_stop', 0):
                        rsi_sr_logger.info(f"🛑 Fallback stop triggered for {asset.symbol}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

                else:
                    # Short position: stop above resistance, profit at support
                    if 'sr_stop_loss' in position_info and current_price >= position_info['sr_stop_loss']:
                        rsi_sr_logger.info(f"🛑 S/R Stop loss triggered for {asset.symbol}: "
                                         f"{current_price:.2f} >= {position_info['sr_stop_loss']:.2f}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

                    elif 'sr_take_profit' in position_info and current_price <= position_info['sr_take_profit']:
                        rsi_sr_logger.info(f"🎯 S/R Take profit triggered for {asset.symbol}: "
                                         f"{current_price:.2f} <= {position_info['sr_take_profit']:.2f}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

                    # Fallback percentage-based stops
                    elif current_price >= position_info.get('fallback_stop', float('inf')):
                        rsi_sr_logger.info(f"🛑 Fallback stop triggered for {asset.symbol}")
                        order_target_percent(asset, 0)
                        positions_to_close.append(asset)

            except Exception as e:
                rsi_sr_logger.warning(f"Error checking S/R stops for {asset.symbol}: {e}")
                continue

        # Clean up closed positions
        for asset in positions_to_close:
            self.positions.pop(asset, None)

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Calculate position size based on Support/Resistance risk.
        """
        try:
            current_price = data.current(asset, 'price')

            # Get S/R levels for this asset
            support_levels = self.support_levels.get(asset, [])
            resistance_levels = self.resistance_levels.get(asset, [])

            # Find risk based on distance to S/R levels
            if target_weight > 0:  # Long position
                # Risk is distance to nearest support below
                supports_below = [s for s in support_levels if s < current_price]
                if supports_below:
                    nearest_support = max(supports_below)
                    risk_distance = (current_price - nearest_support) / current_price
                    risk_type = f"S/R (support at ₹{nearest_support:.2f})"
                else:
                    # No support found, use percentage-based risk
                    risk_distance = self.risk_params['stop_loss_pct']
                    risk_type = "Fallback percentage"
            else:  # Short position
                # Risk is distance to nearest resistance above
                resistances_above = [r for r in resistance_levels if r > current_price]
                if resistances_above:
                    nearest_resistance = min(resistances_above)
                    risk_distance = (nearest_resistance - current_price) / current_price
                    risk_type = f"S/R (resistance at ₹{nearest_resistance:.2f})"
                else:
                    # No resistance found, use percentage-based risk
                    risk_distance = self.risk_params['stop_loss_pct']
                    risk_type = "Fallback percentage"

            # Position sizing: Risk 1% of portfolio per trade (reduced from 1.5%)
            portfolio_value = context.portfolio.portfolio_value
            risk_per_trade = portfolio_value * 0.01  # 1% risk

            # Calculate position size based on risk distance
            if risk_distance > 0 and risk_distance < 0.15:  # Cap risk distance at 15%
                position_size = risk_per_trade / (risk_distance * portfolio_value)
            else:
                # Use conservative fallback for extreme risk distances
                position_size = self.risk_params['max_position_size'] * 0.3

            # Apply maximum position size limit
            final_size = min(abs(position_size), self.risk_params['max_position_size'])

            # Additional safety: reduce size for weak signals
            signal_strength = abs(target_weight)
            if signal_strength < 0.3:  # Very weak signal
                final_size *= 0.3  # Reduce position size significantly
            elif signal_strength < 0.5:  # Moderate signal
                final_size *= 0.7  # Reduce position size moderately

            # Apply target weight direction
            final_size = np.sign(target_weight) * final_size

            # Enhanced logging
            rsi_sr_logger.info(f"Position sizing for {asset.symbol}: "
                             f"Price=₹{current_price:.2f}, Risk={risk_distance:.2%} ({risk_type}), "
                             f"Signal={signal_strength:.3f}, Raw size={position_size:.3f}, Final size={final_size:.3f}")

            # Safety check for extreme position sizes
            if abs(final_size) > 0.2:  # More than 20%
                rsi_sr_logger.warning(f"Large position size for {asset.symbol}: {final_size:.1%} - capping to 15%")
                final_size = np.sign(final_size) * 0.15

            return final_size

        except Exception as e:
            rsi_sr_logger.warning(f"Position sizing error for {asset.symbol}: {e}")
            return np.sign(target_weight) * min(0.08, self.risk_params['max_position_size'])

    def _update_stop_losses(self, asset, size, price):
        """
        Set Support/Resistance based stops and profit targets.
        """
        if size == 0:
            self.positions.pop(asset, None)
            return

        try:
            # Get S/R levels for this asset
            support_levels = self.support_levels.get(asset, [])
            resistance_levels = self.resistance_levels.get(asset, [])

            if size > 0:  # Long position
                # Stop loss: Below nearest support
                supports_below = [s for s in support_levels if s < price]
                if supports_below:
                    nearest_support = max(supports_below)
                    # Set stop slightly below support to avoid false breaks
                    sr_stop_loss = nearest_support * 0.995  # 0.5% below support
                else:
                    sr_stop_loss = None

                # Take profit: At nearest resistance
                resistances_above = [r for r in resistance_levels if r > price]
                if resistances_above:
                    nearest_resistance = min(resistances_above)
                    # Set profit slightly below resistance for easier execution
                    sr_take_profit = nearest_resistance * 0.995  # 0.5% below resistance
                else:
                    sr_take_profit = None

                # Fallback stops
                fallback_stop = price * (1 - self.risk_params['stop_loss_pct'])
                fallback_profit = price * (1 + self.risk_params['take_profit_pct'])

            else:  # Short position
                # Stop loss: Above nearest resistance
                resistances_above = [r for r in resistance_levels if r > price]
                if resistances_above:
                    nearest_resistance = min(resistances_above)
                    # Set stop slightly above resistance
                    sr_stop_loss = nearest_resistance * 1.005  # 0.5% above resistance
                else:
                    sr_stop_loss = None

                # Take profit: At nearest support
                supports_below = [s for s in support_levels if s < price]
                if supports_below:
                    nearest_support = max(supports_below)
                    # Set profit slightly above support
                    sr_take_profit = nearest_support * 1.005  # 0.5% above support
                else:
                    sr_take_profit = None

                # Fallback stops
                fallback_stop = price * (1 + self.risk_params['stop_loss_pct'])
                fallback_profit = price * (1 - self.risk_params['take_profit_pct'])

            # Store position information
            position_info = {
                'entry_price': price,
                'fallback_stop': fallback_stop,
                'fallback_profit': fallback_profit,
                'entry_time': get_datetime()
            }

            # Add S/R levels if available
            if sr_stop_loss:
                position_info['sr_stop_loss'] = sr_stop_loss
            if sr_take_profit:
                position_info['sr_take_profit'] = sr_take_profit

            self.positions[asset] = position_info

            # Log position setup
            stop_type = "S/R" if sr_stop_loss else "Fallback"
            profit_type = "S/R" if sr_take_profit else "Fallback"

            rsi_sr_logger.info(f"📊 Position set for {asset.symbol}: Entry={price:.2f}, "
                             f"Stop={sr_stop_loss or fallback_stop:.2f} ({stop_type}), "
                             f"Profit={sr_take_profit or fallback_profit:.2f} ({profit_type})")

        except Exception as e:
            rsi_sr_logger.warning(f"Error setting S/R stops for {asset.symbol}: {e}")
            # Fallback to base class method
            super()._update_stop_losses(asset, size, price)

    def _record_metrics(self, context):
        """
        Record enhanced metrics including S/R analysis.
        """
        try:
            # Base metrics
            super()._record_metrics(context)

            if hasattr(self, '_current_data'):
                data = self._current_data

                # S/R strategy specific metrics
                total_support_levels = sum(len(levels) for levels in self.support_levels.values())
                total_resistance_levels = sum(len(levels) for levels in self.resistance_levels.values())

                # Count positions using S/R vs fallback stops
                sr_stop_positions = sum(1 for pos in self.positions.values() if 'sr_stop_loss' in pos)
                sr_profit_positions = sum(1 for pos in self.positions.values() if 'sr_take_profit' in pos)

                # Calculate average RSI
                avg_rsi = 0
                rsi_count = 0
                for asset in context.universe:
                    if asset in self.rsi_history and len(self.rsi_history[asset]) > 0:
                        avg_rsi += self.rsi_history[asset][-1]
                        rsi_count += 1

                avg_rsi = avg_rsi / rsi_count if rsi_count > 0 else 50

                # Record enhanced metrics
                record(
                    # S/R metrics
                    total_support_levels=total_support_levels,
                    total_resistance_levels=total_resistance_levels,
                    sr_stop_positions=sr_stop_positions,
                    sr_profit_positions=sr_profit_positions,

                    # RSI metrics
                    avg_rsi=avg_rsi,
                    rsi_oversold_signals=sum(1 for asset in context.universe
                                           if asset in self.rsi_history and
                                           len(self.rsi_history[asset]) > 0 and
                                           self.rsi_history[asset][-1] <= self.oversold_threshold),
                    rsi_overbought_signals=sum(1 for asset in context.universe
                                             if asset in self.rsi_history and
                                             len(self.rsi_history[asset]) > 0 and
                                             self.rsi_history[asset][-1] >= self.overbought_threshold),

                    # Position quality metrics
                    positions_with_sr_stops=len([pos for pos in self.positions.values() if 'sr_stop_loss' in pos]),
                    positions_with_sr_profits=len([pos for pos in self.positions.values() if 'sr_take_profit' in pos]),
                )

        except Exception as e:
            rsi_sr_logger.warning(f"Error recording enhanced metrics: {e}")


# Example usage and backtesting
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import os

    print("🎯 RSI Support/Resistance Strategy Backtest")
    print("=" * 60)

    # Create strategy instance
    strategy = RSISupportResistanceStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70,
        lookback_period=20,      # Look back 20 days for S/R levels
        min_touches=2,           # Require at least 2 touches for valid S/R
        sr_tolerance=0.02        # 2% tolerance for S/R level identification
    )

    print(f"📊 Strategy Parameters:")
    print(f"   RSI Period: {strategy.rsi_period}")
    print(f"   Oversold Threshold: {strategy.oversold_threshold}")
    print(f"   Overbought Threshold: {strategy.overbought_threshold}")
    print(f"   S/R Lookback Period: {strategy.lookback_period}")
    print(f"   Minimum S/R Touches: {strategy.min_touches}")
    print(f"   S/R Tolerance: {strategy.sr_tolerance:.1%}")
    print()

    # Create runner with NSE data
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=200000,
        benchmark_symbol='NIFTY50'
    )

    print("🚀 Running backtest...")
    results = runner.run()

    # Create results directory
    results_dir = 'backtest_results/rsi_support_resistance'
    os.makedirs(results_dir, exist_ok=True)

    print("📈 Analyzing results...")
    runner.analyze(results_dir)

    print("✅ Backtest and analysis complete!")
    print(f"📁 Results saved to: {results_dir}")
