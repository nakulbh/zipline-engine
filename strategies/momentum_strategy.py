"""
Multi-Timeframe Momentum Strategy

This strategy combines momentum indicators across multiple timeframes to identify strong trends.
The strategy:

1. Calculates short-term momentum (5-day and 10-day returns)
2. Calculates medium-term momentum (20-day and 50-day returns)
3. Calculates long-term momentum (100-day and 200-day returns)
4. Uses MACD for trend confirmation
5. Combines signals across timeframes with weighted scoring
6. Includes momentum persistence and acceleration factors

Author: NSE Backtesting Engine
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record
import pandas as pd
import numpy as np

class MultiTimeframeMomentumStrategy(BaseStrategy):
    """
    Multi-timeframe momentum strategy for NSE stocks.
    
    Parameters:
    - short_periods: List of short-term momentum periods (default: [5, 10])
    - medium_periods: List of medium-term momentum periods (default: [20, 50])
    - long_periods: List of long-term momentum periods (default: [100, 200])
    - macd_fast: MACD fast EMA period (default: 12)
    - macd_slow: MACD slow EMA period (default: 26)
    - macd_signal: MACD signal line period (default: 9)
    - momentum_threshold: Minimum momentum score for signal (default: 0.3)
    """
    
    def __init__(self, short_periods=[5, 10], medium_periods=[20, 50], 
                 long_periods=[100, 200], macd_fast=12, macd_slow=26, 
                 macd_signal=9, momentum_threshold=0.3):
        super().__init__()
        self.short_periods = short_periods
        self.medium_periods = medium_periods
        self.long_periods = long_periods
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.momentum_threshold = momentum_threshold
        
        # Calculate maximum lookback period
        self.max_period = max(long_periods + [macd_slow]) + 20
        
        # Enhanced risk parameters for momentum trading
        self.risk_params.update({
            'max_position_size': 0.10,    # 10% per position
            'stop_loss_pct': 0.08,        # 8% stop loss
            'take_profit_pct': 0.20,      # 20% profit target
            'max_leverage': 1.2,          # 120% leverage for momentum
        })
        
        # Strategy-specific tracking
        self.momentum_history = {}

    def select_universe(self, context):
        """
        Select NSE stocks suitable for momentum trading.
        Focus on liquid stocks with good trending characteristics.
        """
        # NSE stocks with good momentum characteristics
        nse_symbols = [
            'SBIN',      # State Bank of India
            'RELIANCE',  # Reliance Industries
            'TCS',       # Tata Consultancy Services
            'INFY',      # Infosys
            'HDFCBANK',  # HDFC Bank
            'ICICIBANK', # ICICI Bank
            'WIPRO',     # Wipro
            'LT',        # Larsen & Toubro
            'AXISBANK',  # Axis Bank
            'MARUTI',    # Maruti Suzuki
            'HINDUNILVR',# Hindustan Unilever
            'ITC'        # ITC Limited
        ]
        
        # Convert to Zipline assets
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            return universe
        except Exception as e:
            # Fallback to available symbols
            return [symbol('SBIN')]

    def calculate_momentum(self, prices, periods):
        """
        Calculate momentum for given periods.
        
        Args:
            prices: Price series
            periods: List of periods to calculate momentum
            
        Returns:
            Dictionary of {period: momentum_value}
        """
        momentum_values = {}
        
        for period in periods:
            if len(prices) >= period + 1:
                momentum = (prices.iloc[-1] / prices.iloc[-period-1]) - 1
                momentum_values[period] = momentum
            else:
                momentum_values[period] = 0.0
        
        return momentum_values

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """
        Calculate MACD indicator.
        
        Args:
            prices: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        if len(prices) < slow + signal:
            return 0, 0, 0
        
        # Calculate EMAs
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]

    def calculate_momentum_score(self, short_mom, medium_mom, long_mom, macd_hist):
        """
        Calculate combined momentum score across timeframes.
        
        Args:
            short_mom: Short-term momentum values
            medium_mom: Medium-term momentum values
            long_mom: Long-term momentum values
            macd_hist: MACD histogram value
            
        Returns:
            Combined momentum score (-1 to 1)
        """
        # Weight factors for different timeframes
        short_weight = 0.3
        medium_weight = 0.4
        long_weight = 0.2
        macd_weight = 0.1
        
        # Calculate weighted averages for each timeframe
        short_avg = np.mean(list(short_mom.values())) if short_mom else 0
        medium_avg = np.mean(list(medium_mom.values())) if medium_mom else 0
        long_avg = np.mean(list(long_mom.values())) if long_mom else 0
        
        # Normalize MACD histogram
        macd_normalized = np.tanh(macd_hist * 100)  # Normalize to -1 to 1
        
        # Calculate combined score
        combined_score = (
            short_avg * short_weight +
            medium_avg * medium_weight +
            long_avg * long_weight +
            macd_normalized * macd_weight
        )
        
        # Apply sigmoid function to bound between -1 and 1
        return np.tanh(combined_score * 2)

    def generate_signals(self, context, data) -> dict:
        """
        Generate multi-timeframe momentum signals.
        
        Returns:
            Dictionary of {asset: signal_strength} where signal_strength is between -1 and 1
        """
        signals = {}
        
        for asset in context.universe:
            try:
                # Get historical price data
                price_history = data.history(asset, 'price', self.max_period, '1d')
                
                if len(price_history) < max(self.long_periods) + 10:
                    signals[asset] = 0.0
                    continue
                
                current_price = price_history.iloc[-1]
                
                # Calculate momentum across different timeframes
                short_momentum = self.calculate_momentum(price_history, self.short_periods)
                medium_momentum = self.calculate_momentum(price_history, self.medium_periods)
                long_momentum = self.calculate_momentum(price_history, self.long_periods)
                
                # Calculate MACD
                macd_line, signal_line, macd_histogram = self.calculate_macd(
                    price_history, self.macd_fast, self.macd_slow, self.macd_signal
                )
                
                # Calculate combined momentum score
                momentum_score = self.calculate_momentum_score(
                    short_momentum, medium_momentum, long_momentum, macd_histogram
                )
                
                # Calculate additional factors
                volatility = price_history.tail(20).pct_change().std() * np.sqrt(252)
                price_trend = (current_price / price_history.iloc[-50]) - 1 if len(price_history) >= 50 else 0
                
                # Calculate momentum persistence (how consistent momentum is)
                momentum_values = list(short_momentum.values()) + list(medium_momentum.values())
                momentum_consistency = 1.0 - np.std(momentum_values) if momentum_values else 0.0
                
                # Calculate momentum acceleration (change in momentum)
                if len(price_history) >= max(self.medium_periods) + 10:
                    prev_medium_mom = self.calculate_momentum(price_history[:-5], self.medium_periods)
                    current_medium_mom = self.calculate_momentum(price_history, self.medium_periods)
                    momentum_acceleration = np.mean(list(current_medium_mom.values())) - np.mean(list(prev_medium_mom.values()))
                else:
                    momentum_acceleration = 0.0
                
                # Generate signal based on momentum score
                signal_strength = 0.0
                
                if abs(momentum_score) > self.momentum_threshold:
                    signal_strength = momentum_score
                    
                    # Adjust signal based on momentum consistency
                    signal_strength *= (0.5 + momentum_consistency * 0.5)
                    
                    # Boost signal if momentum is accelerating in same direction
                    if (momentum_score > 0 and momentum_acceleration > 0) or \
                       (momentum_score < 0 and momentum_acceleration < 0):
                        signal_strength *= 1.2
                    
                    # Reduce signal in high volatility environments
                    if volatility > 0.3:  # High volatility
                        signal_strength *= 0.8
                    
                    # MACD confirmation
                    if (momentum_score > 0 and macd_line > signal_line) or \
                       (momentum_score < 0 and macd_line < signal_line):
                        signal_strength *= 1.1  # MACD confirms momentum
                    else:
                        signal_strength *= 0.9  # MACD diverges from momentum
                
                # Ensure signal is within bounds
                signal_strength = max(-1.0, min(1.0, signal_strength))
                signals[asset] = signal_strength
                
                # Store momentum history
                if asset not in self.momentum_history:
                    self.momentum_history[asset] = []
                
                momentum_data = {
                    'score': momentum_score,
                    'short': short_momentum,
                    'medium': medium_momentum,
                    'long': long_momentum,
                    'macd_hist': macd_histogram,
                    'consistency': momentum_consistency,
                    'acceleration': momentum_acceleration
                }
                self.momentum_history[asset].append(momentum_data)
                
                # Keep only last 50 records
                if len(self.momentum_history[asset]) > 50:
                    self.momentum_history[asset] = self.momentum_history[asset][-50:]
                
                # Record factors for Alphalens analysis
                self.record_factor('momentum_score', momentum_score, context)
                self.record_factor('short_momentum', np.mean(list(short_momentum.values())), context)
                self.record_factor('medium_momentum', np.mean(list(medium_momentum.values())), context)
                self.record_factor('long_momentum', np.mean(list(long_momentum.values())), context)
                self.record_factor('macd_histogram', macd_histogram, context)
                self.record_factor('momentum_consistency', momentum_consistency, context)
                self.record_factor('momentum_acceleration', momentum_acceleration, context)
                self.record_factor('volatility', volatility, context)
                self.record_factor('signal_strength', abs(signal_strength), context)
                
                # Record current data for analysis
                record(
                    prices=current_price,
                    momentum_score=momentum_score,
                    macd_line=macd_line,
                    macd_signal=signal_line
                )
                
            except Exception as e:
                # Handle any calculation errors gracefully
                signals[asset] = 0.0
                continue
        
        return signals

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Calculate position size with momentum-based adjustments.
        """
        base_size = super()._calculate_position_size(context, data, asset, target_weight)
        
        # Get current momentum data if available
        if asset in self.momentum_history and len(self.momentum_history[asset]) > 0:
            momentum_data = self.momentum_history[asset][-1]
            
            # Adjust position size based on momentum strength
            momentum_score = abs(momentum_data['score'])
            if momentum_score > 0.5:  # Strong momentum
                base_size *= 1.2
            elif momentum_score < 0.2:  # Weak momentum
                base_size *= 0.7
            
            # Adjust based on momentum consistency
            if momentum_data['consistency'] > 0.8:  # Very consistent
                base_size *= 1.1
            elif momentum_data['consistency'] < 0.4:  # Inconsistent
                base_size *= 0.8
        
        return base_size


# Example usage and backtesting
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import os
    
    print("🎯 Multi-Timeframe Momentum Strategy Backtest")
    print("=" * 50)
    
    # Create strategy instance
    strategy = MultiTimeframeMomentumStrategy(
        short_periods=[5, 10],
        medium_periods=[20, 50],
        long_periods=[100, 200],
        momentum_threshold=0.3
    )
    
    # Create runner with NSE data
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='SBIN'
    )
    
    print("Running backtest...")
    results = runner.run()
    
    # Create results directory
    results_dir = 'backtest_results/momentum_strategy'
    os.makedirs(results_dir, exist_ok=True)
    
    # Analyze results
    runner.analyze(results_dir)
    
    print("Backtest and analysis complete.")
