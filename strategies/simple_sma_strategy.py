#!/usr/bin/env python3
"""
SIMPLE SMA STRATEGY - Start Here!
=================================

This is the EXACT strategy you should use to start.
No confusion, no complexity, just clean SMA crossover.
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, schedule_function, date_rules, time_rules
import numpy as np

# Import bundle to register it
import bundles.duckdb_polars_bundle

class SimpleSMAStrategy(BaseStrategy):
    """
    Clean, Simple SMA Crossover Strategy
    
    This does EXACTLY what you need:
    - SMA crossover signals
    - Daily rebalancing at 9:45 AM
    - Built-in risk management
    - Low trading costs
    
    NO confusion, NO complexity!
    """

    def __init__(self, short_window=20, long_window=50):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        
        # Optional: Set a benchmark for comparison
        self.benchmark_symbol = 'NIFTY'
        
        print(f"✅ SimpleSMAStrategy initialized:")
        print(f"   📊 Short SMA: {short_window} days")
        print(f"   📊 Long SMA: {long_window} days")
        print(f"   📊 Benchmark: {self.benchmark_symbol}")

    def select_universe(self, context):
        """
        Define which assets to trade
        
        Start with just 2-3 assets to keep it simple
        """
        assets = [
            symbol('NIFTY'),  # Nifty index
            symbol('ACC'),    # ACC Limited
            # symbol('RELIANCE'),  # Add more later if needed
        ]
        
        print(f"📈 Trading universe: {[asset.symbol for asset in assets]}")
        return assets
    
    def generate_signals(self, context, data):
        """
        Generate SMA crossover signals
        
        This is the CORE of your strategy - keep it simple!
        """
        signals = {}
        
        for asset in context.universe:
            try:
                # Get price history (need long_window + 1 for calculations)
                prices = data.history(asset, 'price', self.long_window + 1, '1d')
                
                if len(prices) >= self.long_window:
                    # Calculate SMAs
                    sma_short = prices.rolling(self.short_window).mean().iloc[-1]
                    sma_long = prices.rolling(self.long_window).mean().iloc[-1]
                    current_price = prices.iloc[-1]
                    
                    # Simple crossover logic
                    if sma_short > sma_long:
                        # Bullish signal - go long
                        signals[asset] = 0.4  # 40% allocation per asset
                    else:
                        # Bearish signal - no position
                        signals[asset] = 0.0
                    
                    # Optional: Record for analysis
                    from zipline.api import record
                    record(**{
                        f'sma_short_{asset.symbol}': sma_short,
                        f'sma_long_{asset.symbol}': sma_long,
                        f'price_{asset.symbol}': current_price,
                        f'signal_{asset.symbol}': signals[asset]
                    })
                    
                    print(f"📊 {asset.symbol}: SMA_short={sma_short:.2f}, SMA_long={sma_long:.2f}, Signal={signals[asset]:.1%}")
                    
                else:
                    # Not enough data - no position
                    signals[asset] = 0.0
                    print(f"⚠️  {asset.symbol}: Not enough data ({len(prices)} days)")
                    
            except Exception as e:
                # Error - no position (safe default)
                signals[asset] = 0.0
                print(f"❌ {asset.symbol}: Error generating signal - {e}")
        
        return signals
    
    def _setup_schedules(self):
        """
        Set up rebalancing schedule
        
        KISS (Keep It Simple, Stupid!):
        - Once per day
        - 30 minutes after market open (avoids opening volatility)
        - That's it!
        """
        schedule_function(
            func=self.rebalance,  # Uses built-in rebalance method
            date_rule=date_rules.every_day(),  # Every trading day
            time_rule=time_rules.market_open(minutes=30)  # 9:45 AM IST
        )
        
        print("📅 Schedule set: Daily rebalancing at 9:45 AM")
        print("   ✅ This avoids opening volatility")
        print("   ✅ This catches all SMA crossovers") 
        print("   ✅ This keeps trading costs low")


# ==================== HOW TO USE THIS STRATEGY ==================== #

def create_runner():
    """
    Example of how to run this strategy
    """
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    from datetime import datetime
    
    # Create strategy
    strategy = SimpleSMAStrategy(short_window=20, long_window=50)
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle_name='duckdb_polars_bundle',  # Your bundle
        start_date=datetime(2023, 1, 1),     # Start date
        end_date=datetime(2024, 12, 31),     # End date
        initial_capital=100000               # ₹1 lakh
    )
    
    return runner

def run_backtest():
    """
    Run the backtest with this simple strategy
    """
    print("🚀 Running Simple SMA Strategy Backtest")
    print("=" * 50)
    
    runner = create_runner()
    
    try:
        # Run backtest
        performance = runner.run_backtest()
        
        print("✅ Backtest completed successfully!")
        print(f"📊 Final portfolio value: {performance.portfolio_value.iloc[-1]:,.2f}")
        print(f"📈 Total return: {(performance.portfolio_value.iloc[-1] / performance.portfolio_value.iloc[0] - 1) * 100:.2f}%")
        
        return performance
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return None

if __name__ == "__main__":
    print("🎯 SIMPLE SMA STRATEGY")
    print("=" * 30)
    
    print("\n📝 THIS STRATEGY:")
    print("✅ Uses ONLY ONE schedule (daily at 9:45 AM)")
    print("✅ Trades 2-3 assets maximum")
    print("✅ Simple SMA crossover signals")
    print("✅ Built-in risk management")
    print("✅ Low complexity, high clarity")
    
    print("\n🎯 NO CONFUSION:")
    print("❌ No multiple schedules")
    print("❌ No handle_data complexity")
    print("❌ No pre-market/post-market logic")
    print("❌ No weekly/monthly complications")
    
    print("\n🚀 TO RUN THIS STRATEGY:")
    print("1. Copy this file to strategies/simple_sma_strategy.py")
    print("2. Run: python strategies/simple_sma_strategy.py")
    print("3. Check results")
    print("4. Only modify if needed!")
    
    print("\n" + "=" * 50)
    print("👇 RUNNING BACKTEST NOW...")
    
    # Uncomment to run backtest
    # run_backtest()
    
    print("\n✅ Strategy template ready!")
    print("🎯 This is ALL you need for SMA crossover trading!")
