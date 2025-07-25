"""
RSI Mean Reversion Strategy

This strategy uses the Relative Strength Index (RSI) to identify overbought and oversold conditions
for mean reversion trading. The strategy:

1. Calculates RSI over a specified period (default 14 days)
2. Generates buy signals when RSI < 30 (oversold)
3. Generates sell signals when RSI > 70 (overbought)
4. Uses position sizing based on RSI strength
5. Records multiple factors for Alphalens analysis

Author: NSE Backtesting Engine
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record, order_target_percent, get_open_orders, cancel_order, get_datetime
import pandas as pd
import numpy as np
import logging

# Create logger for RSI strategy
rsi_logger = logging.getLogger('rsi_strategy')
rsi_logger.setLevel(logging.INFO)


class RSIMeanReversionStrategy(BaseStrategy):
    """
    RSI-based mean reversion strategy for NSE stocks.
    
    Parameters:
    - rsi_period: Period for RSI calculation (default: 14)
    - oversold_threshold: RSI level considered oversold (default: 30)
    - overbought_threshold: RSI level considered overbought (default: 70)
    - position_scaling: Whether to scale position size based on RSI strength
    """
    
    def __init__(self, rsi_period=14, oversold_threshold=30, overbought_threshold=70, position_scaling=True):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.position_scaling = position_scaling
        
        # Enhanced risk parameters for mean reversion
        self.risk_params.update({
            'max_position_size': 0.15,    # 15% per position (higher for mean reversion)
            'stop_loss_pct': 0.10,        # 10% stop loss
            'take_profit_pct': 0.08,      # 8% profit target (tighter for mean reversion)
            'max_leverage': 0.8,          # 80% max leverage
        })
        
        # Strategy-specific tracking
        self.rsi_history = {}
        self.entry_prices = {}

    def select_universe(self, context):
        """
        Select NSE stocks for RSI mean reversion trading.
        Focus on liquid, large-cap stocks that tend to mean revert.
        """
        # Available NSE stocks in your bundle suitable for mean reversion
        nse_symbols = [
            'SBIN',       # State Bank of India
            'RELIANCE',   # Reliance Industries
            'HDFCBANK',   # HDFC Bank
            'BAJFINANCE', # Bajaj Finance
            'HDFC',       # HDFC Ltd
        ]
        
        # Convert to Zipline assets
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            return universe
        except Exception as e:
            # Fallback to available symbols
            return [symbol('SBIN')]

    def calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series
            period: RSI calculation period
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50  # Neutral RSI if insufficient data
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def calculate_atr(self, data, asset, window=14):
        """
        Calculate Average True Range (ATR) for volatility measurement.

        Args:
            data: Zipline data object
            asset: Asset to calculate ATR for
            window: ATR calculation period

        Returns:
            ATR value
        """
        try:
            # Get OHLC data
            high = data.history(asset, 'high', window + 5, '1d')
            low = data.history(asset, 'low', window + 5, '1d')
            close = data.history(asset, 'close', window + 5, '1d')

            if len(high) < window + 1:
                # Fallback to simple price volatility if insufficient data
                prices = data.history(asset, 'price', window + 5, '1d')
                return prices.pct_change().std() * prices.iloc[-1] if len(prices) > 1 else 0.02

            # Calculate True Range components
            tr1 = high - low  # High - Low
            tr2 = abs(high - close.shift(1))  # High - Previous Close
            tr3 = abs(low - close.shift(1))   # Low - Previous Close

            # True Range is the maximum of the three
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # ATR is the moving average of True Range
            atr = true_range.rolling(window=window).mean()

            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.02

        except Exception as e:
            rsi_logger.warning(f"ATR calculation failed for {asset.symbol}: {e}")
            # Fallback to 2% of current price as ATR estimate
            current_price = data.current(asset, 'price')
            return current_price * 0.02

    def generate_signals(self, context, data) -> dict:
        """
        Generate RSI-based mean reversion signals.
        
        Returns:
            Dictionary of {asset: signal_strength} where signal_strength is between -1 and 1
        """
        signals = {}
        
        for asset in context.universe:
            try:
                # Get historical price data
                history = data.history(asset, 'price', self.rsi_period + 10, '1d')
                
                if len(history) < self.rsi_period + 1:
                    signals[asset] = 0.0
                    continue
                
                # Calculate RSI
                current_rsi = self.calculate_rsi(history, self.rsi_period)
                current_price = history.iloc[-1]
                
                # Store RSI history for tracking
                if asset not in self.rsi_history:
                    self.rsi_history[asset] = []
                self.rsi_history[asset].append(current_rsi)
                
                # Keep only last 50 RSI values
                if len(self.rsi_history[asset]) > 50:
                    self.rsi_history[asset] = self.rsi_history[asset][-50:]
                
                # Calculate additional factors
                rsi_normalized = (current_rsi - 50) / 50  # Normalize RSI to -1 to 1
                price_change_5d = (current_price / history.iloc[-6] - 1) if len(history) >= 6 else 0
                price_volatility = history.tail(10).pct_change().std() * np.sqrt(252)  # Annualized volatility

                # Calculate ATR and ATR-based factors
                current_atr = self.calculate_atr(data, asset)
                atr_percentage = current_atr / current_price  # ATR as percentage of price
                volatility_regime = "high" if atr_percentage > 0.03 else "low" if atr_percentage < 0.01 else "normal"
                
                # Generate signals based on RSI levels
                signal_strength = 0.0
                
                if current_rsi <= self.oversold_threshold:
                    # Oversold - Buy signal
                    if self.position_scaling:
                        # Stronger signal for more oversold conditions
                        signal_strength = min(1.0, (self.oversold_threshold - current_rsi) / 10)
                    else:
                        signal_strength = 1.0
                        
                elif current_rsi >= self.overbought_threshold:
                    # Overbought - Sell signal
                    if self.position_scaling:
                        # Stronger signal for more overbought conditions
                        signal_strength = -min(1.0, (current_rsi - self.overbought_threshold) / 10)
                    else:
                        signal_strength = -1.0
                
                # Adjust signal based on recent price action (momentum filter)
                if abs(price_change_5d) > 0.05:  # If price moved >5% in 5 days
                    signal_strength *= 0.7  # Reduce signal strength
                
                signals[asset] = signal_strength
                
                # Record factors for Alphalens analysis
                self.record_factor('rsi', current_rsi, context)
                self.record_factor('rsi_normalized', rsi_normalized, context)
                self.record_factor('rsi_oversold', 1.0 if current_rsi <= self.oversold_threshold else 0.0, context)
                self.record_factor('rsi_overbought', 1.0 if current_rsi >= self.overbought_threshold else 0.0, context)
                self.record_factor('price_volatility', price_volatility, context)
                self.record_factor('signal_strength', abs(signal_strength), context)

                # Record ATR-based factors
                self.record_factor('atr', current_atr, context)
                self.record_factor('atr_percentage', atr_percentage, context)
                self.record_factor('volatility_regime_high', 1.0 if atr_percentage > 0.03 else 0.0, context)
                self.record_factor('volatility_regime_low', 1.0 if atr_percentage < 0.01 else 0.0, context)

                # Record combined factors
                self.record_factor('rsi_atr_combo', current_rsi * atr_percentage, context)
                self.record_factor('signal_atr_adjusted', signal_strength * (1 / max(atr_percentage, 0.005)), context)
                
                # Record current prices and RSI for analysis
                record(prices=current_price, rsi_value=current_rsi)
                
            except Exception as e:
                # Handle any calculation errors gracefully
                signals[asset] = 0.0
                continue
        
        return signals

    def _get_atr(self, asset, data=None, window=14) -> float:
        """
        Override base class ATR method with proper implementation.
        """
        if data is None:
            # If no data provided, return fallback value
            return 0.02

        return self.calculate_atr(data, asset, window)

    def check_stop_loss_take_profit(self, context, data):
        """
        Check and execute stop loss and take profit orders.
        This method should be called before generating new signals.
        """
        positions_to_close = []

        for asset in list(self.positions.keys()):
            if asset not in context.portfolio.positions or context.portfolio.positions[asset].amount == 0:
                # Position no longer exists, remove from tracking
                positions_to_close.append(asset)
                continue

            try:
                current_price = data.current(asset, 'price')
                position_info = self.positions[asset]
                current_position = context.portfolio.positions[asset]

                # Determine if we're long or short
                is_long = current_position.amount > 0

                # Check stop loss
                if is_long and current_price <= position_info['stop_loss']:
                    rsi_logger.info(f"🛑 Stop loss triggered for {asset.symbol}: {current_price:.2f} <= {position_info['stop_loss']:.2f}")
                    order_target_percent(asset, 0)  # Close position
                    positions_to_close.append(asset)

                elif not is_long and current_price >= position_info['stop_loss']:
                    rsi_logger.info(f"🛑 Stop loss triggered for {asset.symbol}: {current_price:.2f} >= {position_info['stop_loss']:.2f}")
                    order_target_percent(asset, 0)  # Close position
                    positions_to_close.append(asset)

                # Check take profit
                elif is_long and current_price >= position_info['take_profit']:
                    rsi_logger.info(f"🎯 Take profit triggered for {asset.symbol}: {current_price:.2f} >= {position_info['take_profit']:.2f}")
                    order_target_percent(asset, 0)  # Close position
                    positions_to_close.append(asset)

                elif not is_long and current_price <= position_info['take_profit']:
                    rsi_logger.info(f"🎯 Take profit triggered for {asset.symbol}: {current_price:.2f} <= {position_info['take_profit']:.2f}")
                    order_target_percent(asset, 0)  # Close position
                    positions_to_close.append(asset)

                # Update trailing stop loss for profitable positions
                else:
                    self._update_trailing_stop(asset, current_price, is_long)

            except Exception as e:
                rsi_logger.warning(f"Error checking stop/profit for {asset.symbol}: {e}")
                continue

        # Clean up closed positions
        for asset in positions_to_close:
            self.positions.pop(asset, None)
            rsi_logger.debug(f"Removed {asset.symbol} from position tracking")

    def _update_trailing_stop(self, asset, current_price, is_long):
        """
        Update trailing stop loss based on current price movement.
        """
        position_info = self.positions[asset]

        if is_long:
            # For long positions, move stop loss up if price moved favorably
            new_stop = current_price * (1 - self.risk_params['stop_loss_pct'])
            if new_stop > position_info['stop_loss']:
                position_info['stop_loss'] = new_stop
                rsi_logger.debug(f"📈 Updated trailing stop for {asset.symbol}: {new_stop:.2f}")
        else:
            # For short positions, move stop loss down if price moved favorably
            new_stop = current_price * (1 + self.risk_params['stop_loss_pct'])
            if new_stop < position_info['stop_loss']:
                position_info['stop_loss'] = new_stop
                rsi_logger.debug(f"📉 Updated trailing stop for {asset.symbol}: {new_stop:.2f}")

    def rebalance(self, context, data):
        """
        Override base rebalance to include stop loss/take profit checks.
        """
        # Store current data context for ATR calculations
        self._current_data = data

        # First check stop losses and take profits
        self.check_stop_loss_take_profit(context, data)

        # Then proceed with normal rebalancing
        super().rebalance(context, data)

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Enhanced position sizing with ATR-based risk management and RSI adjustments.
        """
        try:
            current_price = data.current(asset, 'price')
            atr = self._get_atr(asset, data, window=20)

            # ATR-based position sizing (Van Tharp method)
            # Risk 1% of portfolio per trade
            portfolio_value = context.portfolio.portfolio_value
            risk_per_trade = portfolio_value * 0.01  # 1% risk per trade

            # Dynamic stop distance based on 2x ATR
            atr_stop_distance = (2 * atr) / current_price

            # Calculate base position size: Risk / Stop Distance
            if atr_stop_distance > 0:
                atr_based_size = risk_per_trade / (atr_stop_distance * portfolio_value)
            else:
                atr_based_size = self.risk_params['max_position_size'] * 0.5

            # Apply maximum position size limit
            base_size = min(
                abs(atr_based_size),
                self.risk_params['max_position_size']
            )

            # Apply RSI-based adjustments
            if asset in self.rsi_history and len(self.rsi_history[asset]) > 0:
                current_rsi = self.rsi_history[asset][-1]

                # RSI conviction scaling
                if current_rsi <= 20:  # Very oversold - high conviction
                    base_size *= 1.3
                elif current_rsi >= 80:  # Very overbought - high conviction
                    base_size *= 1.3
                elif current_rsi <= 25 or current_rsi >= 75:  # Moderate extremes
                    base_size *= 1.1
                elif 40 <= current_rsi <= 60:  # Neutral zone - low conviction
                    base_size *= 0.6

                # Additional volatility adjustment
                if atr / current_price > 0.03:  # High volatility (>3% daily ATR)
                    base_size *= 0.8  # Reduce size in high volatility
                elif atr / current_price < 0.01:  # Low volatility (<1% daily ATR)
                    base_size *= 1.1  # Increase size in low volatility

            # Ensure we don't exceed maximum position size after adjustments
            final_size = min(base_size, self.risk_params['max_position_size'])

            # Apply target weight direction (long/short)
            final_size = np.sign(target_weight) * final_size

            rsi_logger.debug(f"Position sizing for {asset.symbol}: ATR={atr:.4f}, "
                           f"ATR%={atr/current_price:.2%}, Size={final_size:.3f}")

            return final_size

        except Exception as e:
            rsi_logger.warning(f"Position sizing error for {asset.symbol}: {e}")
            # Fallback to simple sizing
            return np.sign(target_weight) * min(0.05, self.risk_params['max_position_size'])

    def _update_stop_losses(self, asset, size, price):
        """
        Enhanced stop loss and take profit setting with ATR-based levels.
        """
        if size == 0:
            # Remove position tracking if closing
            self.positions.pop(asset, None)
            return

        try:
            # Get ATR for dynamic stop/profit levels - use fallback if data not available
            try:
                # Try to get current data context (this will be available during rebalance)
                from zipline.api import get_datetime
                current_data = getattr(self, '_current_data', None)
                atr = self.calculate_atr(current_data, asset) if current_data else 0.02
            except:
                atr = 0.02  # Fallback ATR value

            # ATR-based stop loss (more dynamic than fixed percentage)
            atr_stop_multiplier = 2.0  # 2x ATR stop loss
            atr_profit_multiplier = 1.5  # 1.5x ATR take profit (tighter for mean reversion)

            if size > 0:  # Long position
                # Use the wider of: ATR-based stop or percentage-based stop
                atr_stop = price - (atr * atr_stop_multiplier)
                pct_stop = price * (1 - self.risk_params['stop_loss_pct'])
                stop_loss = max(atr_stop, pct_stop)  # Use wider stop for safety

                # Use the closer of: ATR-based profit or percentage-based profit
                atr_profit = price + (atr * atr_profit_multiplier)
                pct_profit = price * (1 + self.risk_params['take_profit_pct'])
                take_profit = min(atr_profit, pct_profit)  # Use closer profit for mean reversion

            else:  # Short position
                # Use the wider of: ATR-based stop or percentage-based stop
                atr_stop = price + (atr * atr_stop_multiplier)
                pct_stop = price * (1 + self.risk_params['stop_loss_pct'])
                stop_loss = min(atr_stop, pct_stop)  # Use wider stop for safety

                # Use the closer of: ATR-based profit or percentage-based profit
                atr_profit = price - (atr * atr_profit_multiplier)
                pct_profit = price * (1 - self.risk_params['take_profit_pct'])
                take_profit = max(atr_profit, pct_profit)  # Use closer profit for mean reversion

            # Store position information
            self.positions[asset] = {
                'entry_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'atr_at_entry': atr,
                'entry_time': get_datetime()
            }

            rsi_logger.info(f"📊 Position set for {asset.symbol}: Entry={price:.2f}, "
                          f"Stop={stop_loss:.2f}, Profit={take_profit:.2f}, ATR={atr:.4f}")

        except Exception as e:
            rsi_logger.warning(f"Error setting stops for {asset.symbol}: {e}")
            # Fallback to base class method
            super()._update_stop_losses(asset, size, price)

    def _record_enhanced_metrics(self, context, data):
        """
        Record enhanced metrics including ATR, RSI, and position information.
        """
        try:
            # Base metrics
            super()._record_metrics(context)

            # RSI strategy specific metrics
            active_positions = len([pos for pos in context.portfolio.positions.values() if pos.amount != 0])
            total_position_value = sum([abs(pos.amount * pos.last_sale_price)
                                      for pos in context.portfolio.positions.values()])

            # Calculate average RSI across universe
            avg_rsi = 0
            rsi_count = 0
            avg_atr_pct = 0
            atr_count = 0

            for asset in context.universe:
                if asset in self.rsi_history and len(self.rsi_history[asset]) > 0:
                    avg_rsi += self.rsi_history[asset][-1]
                    rsi_count += 1

                try:
                    current_price = data.current(asset, 'price')
                    atr = self._get_atr(asset, data)
                    avg_atr_pct += (atr / current_price)
                    atr_count += 1
                except:
                    continue

            avg_rsi = avg_rsi / rsi_count if rsi_count > 0 else 50
            avg_atr_pct = avg_atr_pct / atr_count if atr_count > 0 else 0.02

            # Record enhanced metrics
            record(
                # RSI metrics
                avg_rsi=avg_rsi,
                rsi_oversold_count=sum(1 for asset in context.universe
                                     if asset in self.rsi_history and
                                     len(self.rsi_history[asset]) > 0 and
                                     self.rsi_history[asset][-1] <= self.oversold_threshold),
                rsi_overbought_count=sum(1 for asset in context.universe
                                       if asset in self.rsi_history and
                                       len(self.rsi_history[asset]) > 0 and
                                       self.rsi_history[asset][-1] >= self.overbought_threshold),

                # Volatility metrics
                avg_atr_pct=avg_atr_pct,

                # Position metrics
                active_positions=active_positions,
                position_concentration=total_position_value / context.portfolio.portfolio_value if context.portfolio.portfolio_value > 0 else 0,
                positions_with_stops=len(self.positions),

                # Risk metrics
                max_position_size_used=max([abs(pos.amount * pos.last_sale_price) / context.portfolio.portfolio_value
                                          for pos in context.portfolio.positions.values()] + [0]),
            )

        except Exception as e:
            rsi_logger.warning(f"Error recording enhanced metrics: {e}")

    def _record_metrics(self, context):
        """
        Override base metrics recording to include enhanced RSI metrics.
        """
        # Store data context for enhanced metrics
        if hasattr(self, '_current_data'):
            self._record_enhanced_metrics(context, self._current_data)
        else:
            super()._record_metrics(context)


# Example usage and backtesting
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import os
    
    print("🎯 RSI Mean Reversion Strategy Backtest")
    print("=" * 50)
    
    # Create strategy instance
    strategy = RSIMeanReversionStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70,
        position_scaling=True
    )
    
    # Create runner with NSE data
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',  # Use NSE minute data
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    print("Running backtest...")
    results = runner.run()
    
    # Create results directory
    results_dir = 'backtest_results/rsi_mean_reversion'
    os.makedirs(results_dir, exist_ok=True)
    
    # Analyze results
    runner.analyze(results_dir)
    
    print("Backtest and analysis complete.")
