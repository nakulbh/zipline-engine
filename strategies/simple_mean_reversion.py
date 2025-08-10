#!/usr/bin/env python3
"""
Simple Mean Reversion Strategy - Clean & Minimal
===============================================

This maintains the simplicity of the original example while using 
BaseStrategy only for the essential framework.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from zipline.api import (
    symbol, record, schedule_function, date_rules, time_rules,
    order_target_percent, get_datetime
)

# Import bundle
import bundles.duckdb_polars_bundle

class SimpleMeanReversionStrategy(BaseStrategy):
    """Simple Mean Reversion - Just like the original example"""
    
    def __init__(self):
        super().__init__()
        # Keep it simple - no complex parameters
        
    def select_universe(self, context):
        """Define assets to trade"""
        return [
            symbol('NIFTY'), symbol('ACC'), symbol('RELIANCE'), 
            symbol('TCS'), symbol('INFY'), symbol('HDFC'),
            symbol('ICICIBANK'), symbol('SBIN'), symbol('ITC')
        ]
    
    def generate_signals(self, context, data):
        """Core mean reversion logic - clean and simple"""
        signals = {}
        asset_scores = []
        
        # Calculate mean reversion scores
        for asset in context.universe:
            try:
                # Get 21-day returns (just like original example)
                prices = data.history(asset, 'price', 22, '1d')
                returns = prices.pct_change().dropna()
                
                if len(returns) >= 21:
                    # Mean reversion score (z-score)
                    latest_return = returns.iloc[-1]
                    mean_return = returns.mean()
                    std_return = returns.std()
                    
                    if std_return > 0:
                        score = (latest_return - mean_return) / std_return
                        asset_scores.append((asset, score))
                        
                        # Record for analysis
                        record(**{f'score_{asset.symbol}': score})
                        
            except Exception:
                continue
        
        # Sort by score and select assets (just like original)
        if len(asset_scores) >= 5:
            asset_scores.sort(key=lambda x: x[1])
            
            # Bottom 5 for longs (oversold)
            longs = [asset for asset, score in asset_scores[:5]]
            
            # Equal weight allocation
            weight = 1.0 / len(longs) if longs else 0
            
            # Assign signals
            for asset in context.universe:
                if asset in longs:
                    signals[asset] = weight
                else:
                    signals[asset] = 0.0
                    
            # Log selections
            print(f"{get_datetime().date()} | Longs: {len(longs)} | Portfolio Value: {context.portfolio.portfolio_value}")
            
        else:
            # Not enough data
            for asset in context.universe:
                signals[asset] = 0.0
                
        return signals
    
    def _setup_schedules(self):
        """Monthly rebalancing - simple"""
        schedule_function(
            func=self.rebalance,
            date_rule=date_rules.month_start(),
            time_rule=time_rules.market_open()
        )

# Simple runner function
def run_backtest():
    """Run the backtest - clean and simple"""
    from datetime import datetime
    
    # Create strategy
    strategy = SimpleMeanReversionStrategy()
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle_name='duckdb_polars_bundle',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31),
        initial_capital=100000  # ₹1 lakh
    )
    
    # Run backtest
    print("Running simple mean reversion backtest...")
    performance = runner.run()
    
    if performance is not None:
        final_value = performance['portfolio_value'].iloc[-1]
        total_return = (final_value / 100000 - 1) * 100
        print(f"Final Value: ₹{final_value:,.0f}")
        print(f"Total Return: {total_return:.2f}%")
        
        # Save basic results
        runner.analyze(results_dir='backtest_results/simple_mean_reversion')
    
    return performance

if __name__ == "__main__":
    print("🎯 SIMPLE MEAN REVERSION STRATEGY")
    print("=" * 40)
    print("✅ Minimal code, maximum clarity")
    print("✅ Just like the original example")
    print("✅ Uses BaseStrategy only for essentials")
    
    # Run it
    run_backtest()
