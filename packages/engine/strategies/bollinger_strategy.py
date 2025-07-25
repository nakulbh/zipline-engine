"""
Bollinger Bands Breakout Strategy

This strategy uses Bollinger Bands to identify breakout opportunities. The strategy:

1. Calculates Bollinger Bands (SMA ± 2 standard deviations)
2. Generates buy signals when price breaks above upper band
3. Generates sell signals when price breaks below lower band
4. Uses band width and position relative to bands for signal strength
5. Includes volume confirmation for stronger signals

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


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands breakout strategy for NSE stocks.
    
    Parameters:
    - bb_period: Period for Bollinger Bands calculation (default: 20)
    - bb_std: Number of standard deviations for bands (default: 2.0)
    - volume_confirmation: Whether to use volume for signal confirmation
    - breakout_threshold: Minimum percentage breakout required (default: 0.5%)
    """
    
    def __init__(self, bb_period=20, bb_std=2.0, volume_confirmation=True, breakout_threshold=0.005, benchmark_symbol='NIFTY50'):
        super().__init__()
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.volume_confirmation = volume_confirmation
        self.breakout_threshold = breakout_threshold
        self.benchmark_symbol = benchmark_symbol  # Add benchmark symbol

        # Enhanced risk parameters for breakout trading
        self.risk_params.update({
            'max_position_size': 0.12,    # 12% per position
            'stop_loss_pct': 0.06,        # 6% stop loss (tighter for breakouts)
            'take_profit_pct': 0.15,      # 15% profit target
            'max_leverage': 1.0,          # Full leverage for breakouts
        })
        
        # Strategy-specific tracking
        self.bb_history = {}
        self.volume_history = {}

    def select_universe(self, context):
        """
        Select NSE stocks suitable for Bollinger Bands breakout trading.
        Focus on stocks with good volatility and volume.
        """
        # NSE stocks with good breakout potential
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
            'MARUTI'     # Maruti Suzuki
        ]
        
        # Convert to Zipline assets
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            return universe
        except Exception as e:
            # Fallback to available symbols
            return [symbol('SBIN')]

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2.0):
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Price series
            period: Moving average period
            std_dev: Number of standard deviations
            
        Returns:
            Tuple of (middle_band, upper_band, lower_band, band_width, bb_position)
        """
        if len(prices) < period:
            return None, None, None, 0, 0.5
        
        # Calculate middle band (SMA)
        middle_band = prices.rolling(window=period).mean()
        
        # Calculate standard deviation
        rolling_std = prices.rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * std_dev)
        lower_band = middle_band - (rolling_std * std_dev)
        
        # Calculate band width (volatility measure)
        band_width = (upper_band - lower_band) / middle_band
        
        # Calculate %B (position within bands)
        current_price = prices.iloc[-1]
        bb_position = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
        
        return (
            middle_band.iloc[-1],
            upper_band.iloc[-1],
            lower_band.iloc[-1],
            band_width.iloc[-1],
            bb_position
        )

    def calculate_volume_confirmation(self, volume_data, period=10):
        """
        Calculate volume-based confirmation signals.
        
        Args:
            volume_data: Volume series
            period: Period for volume average
            
        Returns:
            Volume ratio (current vs average)
        """
        if len(volume_data) < period:
            return 1.0
        
        current_volume = volume_data.iloc[-1]
        avg_volume = volume_data.rolling(window=period).mean().iloc[-1]
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0

    def generate_signals(self, context, data) -> dict:
        """
        Generate Bollinger Bands breakout signals.
        
        Returns:
            Dictionary of {asset: signal_strength} where signal_strength is between -1 and 1
        """
        signals = {}
        
        for asset in context.universe:
            try:
                # Get historical price data
                price_history = data.history(asset, 'price', self.bb_period + 10, '1d')
                
                if len(price_history) < self.bb_period + 1:
                    signals[asset] = 0.0
                    continue
                
                # Get volume data if volume confirmation is enabled
                volume_ratio = 1.0
                if self.volume_confirmation:
                    try:
                        volume_history = data.history(asset, 'volume', self.bb_period + 10, '1d')
                        volume_ratio = self.calculate_volume_confirmation(volume_history)
                    except:
                        volume_ratio = 1.0  # Default if volume data not available
                
                # Calculate Bollinger Bands
                middle_band, upper_band, lower_band, band_width, bb_position = self.calculate_bollinger_bands(
                    price_history, self.bb_period, self.bb_std
                )
                
                if middle_band is None:
                    signals[asset] = 0.0
                    continue
                
                current_price = price_history.iloc[-1]
                
                # Store BB history for tracking
                if asset not in self.bb_history:
                    self.bb_history[asset] = []
                
                bb_data = {
                    'price': current_price,
                    'middle': middle_band,
                    'upper': upper_band,
                    'lower': lower_band,
                    'width': band_width,
                    'position': bb_position
                }
                self.bb_history[asset].append(bb_data)
                
                # Keep only last 50 records
                if len(self.bb_history[asset]) > 50:
                    self.bb_history[asset] = self.bb_history[asset][-50:]
                
                # Calculate additional factors
                price_change_1d = (current_price / price_history.iloc[-2] - 1) if len(price_history) >= 2 else 0
                volatility = price_history.tail(20).pct_change().std() * np.sqrt(252)
                
                # Generate signals based on Bollinger Bands breakout
                signal_strength = 0.0
                
                # Upper band breakout (Buy signal)
                if current_price > upper_band * (1 + self.breakout_threshold):
                    # Calculate signal strength based on breakout magnitude
                    breakout_strength = (current_price - upper_band) / upper_band
                    signal_strength = min(1.0, breakout_strength * 10)  # Scale breakout strength
                    
                    # Adjust for band width (wider bands = stronger signal)
                    if band_width > 0.05:  # Wide bands indicate high volatility
                        signal_strength *= 1.2
                    
                    # Volume confirmation
                    if self.volume_confirmation and volume_ratio > 1.5:
                        signal_strength *= 1.3  # Boost signal with high volume
                    elif self.volume_confirmation and volume_ratio < 0.8:
                        signal_strength *= 0.7  # Reduce signal with low volume
                
                # Lower band breakout (Sell signal)
                elif current_price < lower_band * (1 - self.breakout_threshold):
                    # Calculate signal strength based on breakout magnitude
                    breakout_strength = (lower_band - current_price) / lower_band
                    signal_strength = -min(1.0, breakout_strength * 10)  # Scale breakout strength
                    
                    # Adjust for band width
                    if band_width > 0.05:
                        signal_strength *= 1.2
                    
                    # Volume confirmation
                    if self.volume_confirmation and volume_ratio > 1.5:
                        signal_strength *= 1.3
                    elif self.volume_confirmation and volume_ratio < 0.8:
                        signal_strength *= 0.7
                
                # Band squeeze detection (low volatility before breakout)
                band_squeeze = band_width < 0.02  # Very narrow bands
                if band_squeeze and abs(signal_strength) > 0:
                    signal_strength *= 1.5  # Boost signals during squeeze
                
                signals[asset] = signal_strength
                
                # Record factors for Alphalens analysis
                self.record_factor('bb_position', bb_position, context)
                self.record_factor('band_width', band_width, context)
                self.record_factor('upper_breakout', 1.0 if current_price > upper_band else 0.0, context)
                self.record_factor('lower_breakout', 1.0 if current_price < lower_band else 0.0, context)
                self.record_factor('band_squeeze', 1.0 if band_squeeze else 0.0, context)
                self.record_factor('volume_ratio', volume_ratio, context)
                self.record_factor('volatility', volatility, context)
                self.record_factor('signal_strength', abs(signal_strength), context)
                
                # Record current data for analysis
                record(
                    prices=current_price,
                    bb_upper=upper_band,
                    bb_lower=lower_band,
                    bb_middle=middle_band,
                    bb_width=band_width
                )
                
            except Exception as e:
                # Handle any calculation errors gracefully
                signals[asset] = 0.0
                continue
        
        return signals

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Calculate position size with Bollinger Bands adjustments.
        """
        base_size = super()._calculate_position_size(context, data, asset, target_weight)
        
        # Get current BB data if available
        if asset in self.bb_history and len(self.bb_history[asset]) > 0:
            bb_data = self.bb_history[asset][-1]
            
            # Adjust position size based on band width (volatility)
            if bb_data['width'] > 0.06:  # High volatility
                base_size *= 0.8  # Reduce position size
            elif bb_data['width'] < 0.02:  # Low volatility (squeeze)
                base_size *= 1.2  # Increase position size
            
            # Adjust based on breakout strength
            current_price = bb_data['price']
            if current_price > bb_data['upper']:  # Strong breakout
                base_size *= 1.1
            elif current_price < bb_data['lower']:  # Strong breakdown
                base_size *= 1.1
        
        return base_size


# Example usage and backtesting
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import os
    
    print("🎯 Bollinger Bands Breakout Strategy Backtest")
    print("=" * 50)
    
    # Create strategy instance
    strategy = BollingerBandsStrategy(
        bb_period=20,
        bb_std=2.0,
        volume_confirmation=True,
        breakout_threshold=0.005
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
    results_dir = 'backtest_results/bollinger_breakout'
    os.makedirs(results_dir, exist_ok=True)
    
    # Analyze results
    runner.analyze(results_dir)
    
    print("Backtest and analysis complete.")
