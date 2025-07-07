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

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record
import pandas as pd
import numpy as np


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
        # NSE large-cap stocks suitable for mean reversion
        nse_symbols = [
            'SBIN',      # State Bank of India
            'RELIANCE',  # Reliance Industries
            'TCS',       # Tata Consultancy Services
            'INFY',      # Infosys
            'HDFCBANK',  # HDFC Bank
            'ICICIBANK', # ICICI Bank
            'ITC',       # ITC Limited
            'HINDUNILVR',# Hindustan Unilever
            'BHARTIARTL',# Bharti Airtel
            'KOTAKBANK'  # Kotak Mahindra Bank
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
                
                # Record current prices and RSI for analysis
                record(prices=current_price, rsi_value=current_rsi)
                
            except Exception as e:
                # Handle any calculation errors gracefully
                signals[asset] = 0.0
                continue
        
        return signals

    def _calculate_position_size(self, context, data, asset, target_weight) -> float:
        """
        Calculate position size with RSI-based adjustments.
        """
        base_size = super()._calculate_position_size(context, data, asset, target_weight)
        
        # Get current RSI if available
        if asset in self.rsi_history and len(self.rsi_history[asset]) > 0:
            current_rsi = self.rsi_history[asset][-1]
            
            # Adjust position size based on RSI extremes
            if current_rsi <= 20:  # Very oversold
                base_size *= 1.2  # Increase position size
            elif current_rsi >= 80:  # Very overbought
                base_size *= 1.2  # Increase position size (for short)
            elif 40 <= current_rsi <= 60:  # Neutral zone
                base_size *= 0.5  # Reduce position size
        
        return base_size


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
        benchmark_symbol='SBIN'
    )
    
    print("Running backtest...")
    results = runner.run()
    
    # Create results directory
    results_dir = 'backtest_results/rsi_mean_reversion'
    os.makedirs(results_dir, exist_ok=True)
    
    # Analyze results
    runner.analyze(results_dir)
    
    print("Backtest and analysis complete.")
