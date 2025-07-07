"""
Volume-Price Trend Strategy

This strategy combines volume analysis with price trends to identify high-probability trades.
The strategy:

1. Calculates Volume-Price Trend (VPT) indicator
2. Analyzes On-Balance Volume (OBV) for volume confirmation
3. Uses Volume-Weighted Average Price (VWAP) for entry/exit levels
4. Identifies volume breakouts and price confirmations
5. Combines multiple volume-based indicators for signal generation

Author: NSE Backtesting Engine
"""

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record
import pandas as pd
import numpy as np


class VolumePriceTrendStrategy(BaseStrategy):
    """
    Volume-Price Trend strategy for NSE stocks.
    
    Parameters:
    - vpt_period: Period for VPT smoothing (default: 14)
    - obv_period: Period for OBV analysis (default: 20)
    - vwap_period: Period for VWAP calculation (default: 20)
    - volume_threshold: Minimum volume ratio for signals (default: 1.5)
    - price_trend_period: Period for price trend analysis (default: 10)
    """
    
    def __init__(self, vpt_period=14, obv_period=20, vwap_period=20, 
                 volume_threshold=1.5, price_trend_period=10):
        super().__init__()
        self.vpt_period = vpt_period
        self.obv_period = obv_period
        self.vwap_period = vwap_period
        self.volume_threshold = volume_threshold
        self.price_trend_period = price_trend_period
        
        # Calculate maximum lookback period
        self.max_period = max(vpt_period, obv_period, vwap_period, price_trend_period) + 20
        
        # Enhanced risk parameters for volume-based trading
        self.risk_params.update({
            'max_position_size': 0.12,    # 12% per position
            'stop_loss_pct': 0.07,        # 7% stop loss
            'take_profit_pct': 0.15,      # 15% profit target
            'max_leverage': 1.0,          # Full leverage
        })
        
        # Strategy-specific tracking
        self.volume_history = {}

    def select_universe(self, context):
        """
        Select NSE stocks with good volume characteristics.
        Focus on liquid stocks where volume analysis is meaningful.
        """
        # NSE stocks with good volume and liquidity
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
            'BHARTIARTL' # Bharti Airtel
        ]
        
        # Convert to Zipline assets
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            return universe
        except Exception as e:
            # Fallback to available symbols
            return [symbol('SBIN')]

    def calculate_vpt(self, prices, volumes):
        """
        Calculate Volume-Price Trend (VPT) indicator.
        
        Args:
            prices: Price series
            volumes: Volume series
            
        Returns:
            VPT series
        """
        if len(prices) < 2 or len(volumes) < 2:
            return pd.Series([0] * len(prices), index=prices.index)
        
        # Calculate price change percentage
        price_change_pct = prices.pct_change()
        
        # Calculate VPT
        vpt = (price_change_pct * volumes).cumsum()
        
        return vpt

    def calculate_obv(self, prices, volumes):
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            prices: Price series
            volumes: Volume series
            
        Returns:
            OBV series
        """
        if len(prices) < 2 or len(volumes) < 2:
            return pd.Series([0] * len(prices), index=prices.index)
        
        # Calculate price direction
        price_direction = np.where(prices.diff() > 0, 1, 
                         np.where(prices.diff() < 0, -1, 0))
        
        # Calculate OBV
        obv = (volumes * price_direction).cumsum()
        
        return obv

    def calculate_vwap(self, prices, volumes, period=20):
        """
        Calculate Volume-Weighted Average Price (VWAP).
        
        Args:
            prices: Price series
            volumes: Volume series
            period: Rolling period for VWAP
            
        Returns:
            VWAP series
        """
        if len(prices) < period or len(volumes) < period:
            return prices.rolling(window=min(len(prices), period)).mean()
        
        # Calculate typical price (assuming close prices)
        typical_price = prices
        
        # Calculate VWAP
        vwap = (typical_price * volumes).rolling(window=period).sum() / volumes.rolling(window=period).sum()
        
        return vwap

    def analyze_volume_pattern(self, volumes, period=10):
        """
        Analyze volume patterns for breakouts and trends.
        
        Args:
            volumes: Volume series
            period: Analysis period
            
        Returns:
            Dictionary with volume analysis results
        """
        if len(volumes) < period:
            return {
                'volume_ratio': 1.0,
                'volume_trend': 0.0,
                'volume_breakout': False,
                'avg_volume': volumes.mean() if len(volumes) > 0 else 0
            }
        
        current_volume = volumes.iloc[-1]
        avg_volume = volumes.rolling(window=period).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Calculate volume trend (increasing/decreasing)
        recent_volumes = volumes.tail(5)
        if len(recent_volumes) >= 3:
            volume_trend = np.polyfit(range(len(recent_volumes)), recent_volumes, 1)[0]
        else:
            volume_trend = 0.0
        
        # Detect volume breakout
        volume_breakout = volume_ratio > self.volume_threshold
        
        return {
            'volume_ratio': volume_ratio,
            'volume_trend': volume_trend,
            'volume_breakout': volume_breakout,
            'avg_volume': avg_volume
        }

    def generate_signals(self, context, data) -> dict:
        """
        Generate volume-price trend signals.
        
        Returns:
            Dictionary of {asset: signal_strength} where signal_strength is between -1 and 1
        """
        signals = {}
        
        for asset in context.universe:
            try:
                # Get historical price and volume data
                price_history = data.history(asset, 'price', self.max_period, '1d')
                
                # Try to get volume data
                try:
                    volume_history = data.history(asset, 'volume', self.max_period, '1d')
                except:
                    # If volume data not available, create synthetic volume
                    volume_history = pd.Series([1000000] * len(price_history), index=price_history.index)
                
                if len(price_history) < self.max_period // 2:
                    signals[asset] = 0.0
                    continue
                
                current_price = price_history.iloc[-1]
                current_volume = volume_history.iloc[-1]
                
                # Calculate volume-price indicators
                vpt = self.calculate_vpt(price_history, volume_history)
                obv = self.calculate_obv(price_history, volume_history)
                vwap = self.calculate_vwap(price_history, volume_history, self.vwap_period)
                
                # Analyze volume patterns
                volume_analysis = self.analyze_volume_pattern(volume_history, self.obv_period)
                
                # Calculate indicator trends
                vpt_trend = 0.0
                obv_trend = 0.0
                if len(vpt) >= self.vpt_period:
                    vpt_recent = vpt.tail(self.vpt_period)
                    vpt_trend = np.polyfit(range(len(vpt_recent)), vpt_recent, 1)[0]
                
                if len(obv) >= self.obv_period:
                    obv_recent = obv.tail(self.obv_period)
                    obv_trend = np.polyfit(range(len(obv_recent)), obv_recent, 1)[0]
                
                # Price vs VWAP analysis
                vwap_current = vwap.iloc[-1] if not pd.isna(vwap.iloc[-1]) else current_price
                price_vs_vwap = (current_price - vwap_current) / vwap_current if vwap_current > 0 else 0
                
                # Price trend analysis
                price_trend = 0.0
                if len(price_history) >= self.price_trend_period:
                    price_recent = price_history.tail(self.price_trend_period)
                    price_trend = np.polyfit(range(len(price_recent)), price_recent, 1)[0]
                
                # Calculate additional factors
                volatility = price_history.tail(20).pct_change().std() * np.sqrt(252)
                price_momentum = (current_price / price_history.iloc[-5] - 1) if len(price_history) >= 5 else 0
                
                # Generate signal based on volume-price analysis
                signal_strength = 0.0
                
                # VPT and OBV trend alignment
                if vpt_trend > 0 and obv_trend > 0 and price_trend > 0:
                    # All indicators bullish
                    signal_strength = 0.6
                elif vpt_trend < 0 and obv_trend < 0 and price_trend < 0:
                    # All indicators bearish
                    signal_strength = -0.6
                elif (vpt_trend > 0 or obv_trend > 0) and price_trend > 0:
                    # Partial bullish alignment
                    signal_strength = 0.3
                elif (vpt_trend < 0 or obv_trend < 0) and price_trend < 0:
                    # Partial bearish alignment
                    signal_strength = -0.3
                
                # Volume breakout confirmation
                if volume_analysis['volume_breakout']:
                    if signal_strength > 0:
                        signal_strength *= 1.5  # Boost bullish signal with volume
                    elif signal_strength < 0:
                        signal_strength *= 1.5  # Boost bearish signal with volume
                    else:
                        # Volume breakout without clear price signal
                        if price_vs_vwap > 0.02:  # Price above VWAP
                            signal_strength = 0.4
                        elif price_vs_vwap < -0.02:  # Price below VWAP
                            signal_strength = -0.4
                
                # VWAP position adjustment
                if abs(price_vs_vwap) > 0.03:  # Significant deviation from VWAP
                    if price_vs_vwap > 0 and signal_strength > 0:
                        signal_strength *= 1.2  # Price above VWAP, bullish signal
                    elif price_vs_vwap < 0 and signal_strength < 0:
                        signal_strength *= 1.2  # Price below VWAP, bearish signal
                    else:
                        signal_strength *= 0.8  # Price and signal diverge
                
                # Volume trend confirmation
                if volume_analysis['volume_trend'] > 0 and signal_strength > 0:
                    signal_strength *= 1.1  # Increasing volume confirms bullish signal
                elif volume_analysis['volume_trend'] < 0 and signal_strength < 0:
                    signal_strength *= 1.1  # Decreasing volume confirms bearish signal
                
                # Volatility adjustment
                if volatility > 0.4:  # High volatility
                    signal_strength *= 0.8  # Reduce signal in high volatility
                
                # Ensure signal is within bounds
                signal_strength = max(-1.0, min(1.0, signal_strength))
                signals[asset] = signal_strength
                
                # Store volume history
                if asset not in self.volume_history:
                    self.volume_history[asset] = []
                
                volume_data = {
                    'vpt': vpt.iloc[-1] if len(vpt) > 0 else 0,
                    'obv': obv.iloc[-1] if len(obv) > 0 else 0,
                    'vwap': vwap_current,
                    'volume_ratio': volume_analysis['volume_ratio'],
                    'volume_trend': volume_analysis['volume_trend'],
                    'price_vs_vwap': price_vs_vwap,
                    'vpt_trend': vpt_trend,
                    'obv_trend': obv_trend
                }
                self.volume_history[asset].append(volume_data)
                
                # Keep only last 50 records
                if len(self.volume_history[asset]) > 50:
                    self.volume_history[asset] = self.volume_history[asset][-50:]
                
                # Record factors for Alphalens analysis
                self.record_factor('vpt_trend', vpt_trend, context)
                self.record_factor('obv_trend', obv_trend, context)
                self.record_factor('volume_ratio', volume_analysis['volume_ratio'], context)
                self.record_factor('volume_breakout', 1.0 if volume_analysis['volume_breakout'] else 0.0, context)
                self.record_factor('price_vs_vwap', price_vs_vwap, context)
                self.record_factor('volume_trend', volume_analysis['volume_trend'], context)
                self.record_factor('price_momentum', price_momentum, context)
                self.record_factor('volatility', volatility, context)
                self.record_factor('signal_strength', abs(signal_strength), context)
                
                # Record current data for analysis
                record(
                    prices=current_price,
                    vwap=vwap_current,
                    volume_ratio=volume_analysis['volume_ratio'],
                    vpt=vpt.iloc[-1] if len(vpt) > 0 else 0,
                    obv=obv.iloc[-1] if len(obv) > 0 else 0
                )
                
            except Exception as e:
                # Handle any calculation errors gracefully
                signals[asset] = 0.0
                continue
        
        return signals

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Calculate position size with volume-based adjustments.
        """
        base_size = super()._calculate_position_size(context, data, asset, target_weight)
        
        # Get current volume data if available
        if asset in self.volume_history and len(self.volume_history[asset]) > 0:
            volume_data = self.volume_history[asset][-1]
            
            # Adjust position size based on volume confirmation
            if volume_data['volume_ratio'] > 2.0:  # High volume
                base_size *= 1.2  # Increase position size
            elif volume_data['volume_ratio'] < 0.8:  # Low volume
                base_size *= 0.7  # Reduce position size
            
            # Adjust based on VPT and OBV alignment
            if (volume_data['vpt_trend'] > 0 and volume_data['obv_trend'] > 0) or \
               (volume_data['vpt_trend'] < 0 and volume_data['obv_trend'] < 0):
                base_size *= 1.1  # Indicators aligned
            else:
                base_size *= 0.9  # Indicators diverging
        
        return base_size


# Example usage and backtesting
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import os
    
    print("🎯 Volume-Price Trend Strategy Backtest")
    print("=" * 50)
    
    # Create strategy instance
    strategy = VolumePriceTrendStrategy(
        vpt_period=14,
        obv_period=20,
        vwap_period=20,
        volume_threshold=1.5
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
    results_dir = 'backtest_results/volume_price_trend'
    os.makedirs(results_dir, exist_ok=True)
    
    # Analyze results
    runner.analyze(results_dir)
    
    print("Backtest and analysis complete.")
