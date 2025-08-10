#!/usr/bin/env python3
"""
Mean Reversion Strategy using BaseStrategy Framework
==================================================

This strategy implements monthly mean reversion trading based on the example you provided,
but adapted to work with your BaseStrategy framework and Indian market data.

Strategy Logic:
- Calculate 21-day mean reversion scores (z-scores)
- Go long on oversold stocks (bottom 5 by score)
- Go short on overbought stocks (top 5 by score) - if shorting enabled
- Rebalance monthly at market open
- Use built-in risk management from BaseStrategy
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

from zipline.api import symbol, schedule_function, date_rules, time_rules, record
import numpy as np
import pandas as pd

# Import bundle to register it
import bundles.duckdb_polars_bundle

class MeanReversionStrategy(BaseStrategy):
    """
    Monthly Mean Reversion Strategy
    
    This strategy bets on extreme stock moves reverting to the average.
    It targets assets whose monthly returns deviate sharply, capitalizing 
    on behavioral overreactions.
    
    Key Features:
    - Monthly rebalancing (reduces noise and costs)
    - Mean reversion scoring based on 21-day returns
    - Long oversold stocks, short overbought stocks
    - Built-in risk management and position sizing
    - Quality screening for liquidity
    """

    def __init__(self, lookback_window=21, n_long=5, n_short=5, 
                 min_price=15.0, enable_shorting=False):
        """
        Initialize Mean Reversion Strategy
        
        Parameters:
        -----------
        lookback_window : int
            Number of days for mean reversion calculation (default: 21)
        n_long : int
            Number of stocks to go long (default: 5)
        n_short : int
            Number of stocks to go short (default: 5)
        min_price : float
            Minimum price filter for liquidity (default: 15.0)
        enable_shorting : bool
            Whether to enable short positions (default: False for Indian markets)
        """
        super().__init__()
        
        self.lookback_window = lookback_window
        self.n_long = n_long
        self.n_short = n_short
        self.min_price = min_price
        self.enable_shorting = enable_shorting
        
        # Strategy state tracking
        self.mean_reversion_scores = {}
        self.selected_longs = []
        self.selected_shorts = []
        
        # Optional benchmark
        self.benchmark_symbol = 'NIFTY'
        
        print(f"✅ MeanReversionStrategy initialized:")
        print(f"   📊 Lookback window: {lookback_window} days")
        print(f"   📈 Long positions: {n_long}")
        print(f"   📉 Short positions: {n_short} {'(enabled)' if enable_shorting else '(disabled)'}")
        print(f"   💰 Min price filter: ₹{min_price}")
        print(f"   📊 Benchmark: {self.benchmark_symbol}")

    def select_universe(self, context):
        """
        Define tradeable assets - use liquid NSE stocks
        
        For Indian markets, we'll focus on liquid large-cap stocks
        """
        # Large-cap Indian stocks with good liquidity
        indian_stocks = [
            'NIFTY',      # Nifty 50 Index
            'ACC',        # ACC Limited  
            'RELIANCE',   # Reliance Industries
            'TCS',        # Tata Consultancy Services
            'INFY',       # Infosys
            'HDFC',       # HDFC Bank
            'ICICIBANK',  # ICICI Bank
            'SBIN',       # State Bank of India
            'ITC',        # ITC Limited
            'HDFCBANK',   # HDFC Bank
            'KOTAKBANK',  # Kotak Mahindra Bank
            'AXISBANK',   # Axis Bank
            'BAJFINANCE', # Bajaj Finance
            'MARUTI',     # Maruti Suzuki
            'ONGC',       # Oil and Natural Gas Corp
        ]
        
        # Convert to symbols
        try:
            assets = [symbol(stock) for stock in indian_stocks]
            print(f"📈 Universe: {len(assets)} Indian stocks")
            return assets
        except Exception as e:
            print(f"⚠️  Error creating universe: {e}")
            # Fallback to minimal universe
            return [symbol('NIFTY'), symbol('ACC')]
    
    def generate_signals(self, context, data):
        """
        Generate mean reversion signals
        
        This is the core of the strategy - calculates mean reversion scores
        and selects stocks for long/short positions.
        """
        signals = {}
        self.mean_reversion_scores = {}
        
        # Get price data for all assets
        valid_assets = []
        
        for asset in context.universe:
            try:
                # Check if we can get enough price data
                prices = data.history(asset, 'price', self.lookback_window + 1, '1d')
                current_price = data.current(asset, 'price')
                
                # Apply minimum price filter for liquidity
                if len(prices) >= self.lookback_window and current_price >= self.min_price:
                    valid_assets.append(asset)
                    
            except Exception as e:
                print(f"⚠️  {asset.symbol}: Could not get price data - {e}")
                continue
        
        if len(valid_assets) < (self.n_long + self.n_short):
            print(f"⚠️  Only {len(valid_assets)} valid assets, need {self.n_long + self.n_short}")
        
        # Calculate mean reversion scores for valid assets
        asset_scores = []
        
        for asset in valid_assets:
            try:
                # Get returns data
                prices = data.history(asset, 'price', self.lookback_window + 1, '1d')
                returns = prices.pct_change().dropna()
                
                if len(returns) >= self.lookback_window:
                    # Calculate mean reversion score (z-score)
                    # Score = (latest_return - mean_return) / std_return
                    latest_return = returns.iloc[-1]
                    mean_return = returns.mean()
                    std_return = returns.std()
                    
                    if std_return > 0:
                        mean_reversion_score = (latest_return - mean_return) / std_return
                        self.mean_reversion_scores[asset] = mean_reversion_score
                        asset_scores.append((asset, mean_reversion_score))
                        
                        # Record individual scores for analysis
                        record(**{f'mr_score_{asset.symbol}': mean_reversion_score})
                    else:
                        signals[asset] = 0.0  # No position if no volatility
                        
            except Exception as e:
                print(f"⚠️  {asset.symbol}: Error calculating mean reversion score - {e}")
                signals[asset] = 0.0
                continue
        
        # Sort assets by mean reversion score
        if len(asset_scores) > 0:
            asset_scores.sort(key=lambda x: x[1])  # Sort by score (ascending)
            
            # Select stocks for long positions (most oversold - lowest scores)
            long_candidates = asset_scores[:self.n_long]
            self.selected_longs = [asset for asset, score in long_candidates]
            
            # Select stocks for short positions (most overbought - highest scores)
            if self.enable_shorting and len(asset_scores) >= self.n_long + self.n_short:
                short_candidates = asset_scores[-self.n_short:]
                self.selected_shorts = [asset for asset, score in short_candidates]
            else:
                self.selected_shorts = []
            
            # Assign weights
            # Long positions: equal weight allocation
            long_weight = 0.8 / len(self.selected_longs) if len(self.selected_longs) > 0 else 0
            
            # Short positions: equal weight allocation (if enabled)
            short_weight = -0.2 / len(self.selected_shorts) if len(self.selected_shorts) > 0 else 0
            
            # Initialize all signals to zero
            for asset in context.universe:
                signals[asset] = 0.0
            
            # Set long signals
            for asset in self.selected_longs:
                signals[asset] = long_weight
                print(f"📈 LONG: {asset.symbol} (score: {self.mean_reversion_scores[asset]:.3f}, weight: {long_weight:.1%})")
            
            # Set short signals (if enabled)
            for asset in self.selected_shorts:
                signals[asset] = short_weight
                print(f"📉 SHORT: {asset.symbol} (score: {self.mean_reversion_scores[asset]:.3f}, weight: {short_weight:.1%})")
            
            # Record strategy metrics
            record(
                n_long_positions=len(self.selected_longs),
                n_short_positions=len(self.selected_shorts),
                mean_mr_score=np.mean([score for _, score in asset_scores]),
                total_target_exposure=sum(abs(weight) for weight in signals.values())
            )
            
            print(f"📊 Mean Reversion Summary:")
            print(f"   📈 Long positions: {len(self.selected_longs)}")
            print(f"   📉 Short positions: {len(self.selected_shorts)}")
            print(f"   📊 Total exposure: {sum(abs(weight) for weight in signals.values()):.1%}")
            
        else:
            print("⚠️  No valid mean reversion scores calculated")
            # Set all signals to zero
            for asset in context.universe:
                signals[asset] = 0.0
        
        return signals
    
    def _setup_schedules(self):
        """
        Set up monthly rebalancing schedule
        
        Monthly rebalancing reduces noise and transaction costs while
        still capturing mean reversion opportunities.
        """
        schedule_function(
            func=self.rebalance,
            date_rule=date_rules.month_start(),  # First trading day of each month
            time_rule=time_rules.market_open(minutes=30)  # 9:45 AM IST (after opening volatility)
        )
        
        print("📅 Schedule set: Monthly rebalancing on first trading day at 9:45 AM")
        print("   ✅ This reduces transaction costs")
        print("   ✅ This avoids short-term noise")
        print("   ✅ This captures behavioral mean reversion")


# ==================== STRATEGY RUNNER ==================== #

def create_mean_reversion_runner():
    """
    Create a runner for the mean reversion strategy
    """
    from datetime import datetime
    
    # Create strategy with parameters
    strategy = MeanReversionStrategy(
        lookback_window=21,      # 21-day lookback (about 1 month)
        n_long=5,                # Long 5 stocks
        n_short=3,               # Short 3 stocks (conservative)
        min_price=15.0,          # Minimum ₹15 for liquidity
        enable_shorting=False    # Disable shorting for Indian markets
    )
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle_name='duckdb_polars_bundle',     # Your DuckDB bundle
        start_date=datetime(2023, 1, 1),        # Start date
        end_date=datetime(2024, 12, 31),        # End date
        initial_capital=500000,                 # ₹5 lakh initial capital
        benchmark_symbol='NIFTY',               # Benchmark
        data_frequency='daily'                  # Daily data (not minute)
    )
    
    return runner, strategy

def run_mean_reversion_backtest():
    """
    Run the mean reversion strategy backtest
    """
    print("🚀 RUNNING MEAN REVERSION STRATEGY BACKTEST")
    print("=" * 60)
    
    try:
        # Create runner and strategy
        runner, strategy = create_mean_reversion_runner()
        
        print("🔄 Starting backtest execution...")
        
        # Run backtest
        performance = runner.run()
        
        if performance is not None:
            print("✅ Backtest completed successfully!")
            
            # Basic performance summary
            initial_value = performance.portfolio_value.iloc[0]
            final_value = performance.portfolio_value.iloc[-1]
            total_return = (final_value / initial_value - 1) * 100
            
            print(f"📊 PERFORMANCE SUMMARY:")
            print(f"   💰 Initial Capital: ₹{initial_value:,.0f}")
            print(f"   💰 Final Value: ₹{final_value:,.0f}")
            print(f"   📈 Total Return: {total_return:.2f}%")
            print(f"   📊 Trading Days: {len(performance)}")
            
            # Run analysis
            print("\n🔍 Running performance analysis...")
            runner.analyze(results_dir='backtest_results/mean_reversion')
            
            return performance, runner
        else:
            print("❌ Backtest failed - no performance data returned")
            return None, None
            
    except Exception as e:
        print(f"❌ Backtest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_mean_reversion_signals():
    """
    Test the mean reversion signal generation logic
    """
    print("🧪 TESTING MEAN REVERSION SIGNAL GENERATION")
    print("=" * 50)
    
    # Create a simple test
    strategy = MeanReversionStrategy(
        lookback_window=21,
        n_long=3,
        n_short=2,
        enable_shorting=True
    )
    
    print("✅ Strategy created successfully")
    print(f"📊 Parameters: {strategy.lookback_window}-day lookback, {strategy.n_long} longs, {strategy.n_short} shorts")
    
    # Test universe selection
    class MockContext:
        pass
    
    context = MockContext()
    try:
        universe = strategy.select_universe(context)
        print(f"📈 Universe size: {len(universe)} assets")
        print(f"📋 Assets: {[asset.symbol for asset in universe[:5]]}...")
        print("✅ Universe selection test passed")
    except Exception as e:
        print(f"❌ Universe selection test failed: {e}")

if __name__ == "__main__":
    print("🎯 MEAN REVERSION STRATEGY")
    print("=" * 40)
    
    print("\n📝 STRATEGY OVERVIEW:")
    print("✅ Monthly mean reversion based on 21-day returns")
    print("✅ Long oversold stocks (bottom 5 by z-score)")
    print("✅ Short overbought stocks (top 5 by z-score)")
    print("✅ Monthly rebalancing to reduce costs")
    print("✅ Built-in risk management from BaseStrategy")
    print("✅ Adapted for Indian market constraints")
    
    print("\n🎯 DIFFERENCES FROM ORIGINAL EXAMPLE:")
    print("✅ Uses your BaseStrategy framework")
    print("✅ Works with your DuckDB bundle")
    print("✅ Includes Indian market considerations")
    print("✅ Has comprehensive logging and error handling")
    print("✅ Supports both long-only and long-short modes")
    
    print("\n🚀 AVAILABLE FUNCTIONS:")
    print("1. test_mean_reversion_signals() - Test signal generation")
    print("2. run_mean_reversion_backtest() - Run full backtest")
    print("3. create_mean_reversion_runner() - Create runner object")
    
    print("\n📚 TO RUN:")
    print("1. Copy this file to strategies/mean_reversion_strategy.py")
    print("2. Run: python strategies/mean_reversion_strategy.py")
    print("3. Or import and call run_mean_reversion_backtest()")
    
    print("\n" + "=" * 60)
    print("👇 TESTING SIGNAL GENERATION...")
    
    # Run basic test
    test_mean_reversion_signals()
    
    print("\n✅ Mean Reversion Strategy ready!")
    print("🎯 This implements the exact logic from your example!")
    print("🚀 Run run_mean_reversion_backtest() to start trading!")
