#!/usr/bin/env python3
"""
Ultra-Minimal Mean Reversion - Raw Style
=======================================

This is as close as possible to the original example while 
still using your BaseStrategy for the minimal framework.
"""

import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from zipline.api import symbol, schedule_function, date_rules, time_rules, record, order_target_percent, get_datetime
from datetime import datetime

import bundles.duckdb_polars_bundle

class UltraMinimalMeanReversion(BaseStrategy):
    """Ultra-minimal mean reversion - raw style"""
    
    def select_universe(self, context):
        return [symbol('NIFTY'), symbol('ACC'), symbol('RELIANCE'), symbol('TCS'), symbol('INFY')]
    
    def generate_signals(self, context, data):
        scores = []
        
        for asset in context.universe:
            try:
                returns = data.history(asset, 'price', 22, '1d').pct_change().dropna()
                if len(returns) >= 21:
                    score = (returns.iloc[-1] - returns.mean()) / returns.std()
                    scores.append((asset, score))
            except:
                continue
        
        if len(scores) >= 3:
            scores.sort(key=lambda x: x[1])
            longs = [asset for asset, _ in scores[:3]]  # Bottom 3
            weight = 1.0 / len(longs)
            
            print(f"{get_datetime().date()} | Longs: {len(longs)} | Value: {context.portfolio.portfolio_value}")
            
            return {asset: weight if asset in longs else 0.0 for asset in context.universe}
        
        return {asset: 0.0 for asset in context.universe}
    
    def _setup_schedules(self):
        schedule_function(self.rebalance, date_rules.month_start(), time_rules.market_open())

# One-liner to run
def run():
    strategy = UltraMinimalMeanReversion()
    runner = EnhancedZiplineRunner(strategy, 'duckdb_polars_bundle', datetime(2023,1,1), datetime(2024,12,31), 100000)
    return runner.run()

if __name__ == "__main__":
    print("🚀 Ultra-Minimal Mean Reversion")
    performance = run()
    if performance is not None:
        print(f"Return: {(performance['portfolio_value'].iloc[-1]/100000-1)*100:.1f}%")
