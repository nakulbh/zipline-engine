#!/usr/bin/env python3
"""
Enhanced Strategy Example - Demonstrates core backtesting functionality
"""

import pandas as pd
import numpy as np
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from strategies.sma_strategy import SmaCrossoverStrategy

def main():
    """Run enhanced strategy example"""
    print("🚀 Enhanced Strategy Example")
    print("=" * 40)
    
    # Initialize strategy
    strategy = SmaCrossoverStrategy()
    
    # Initialize runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle_name='nse-duckdb-parquet-bundle',
        start_date='2023-01-01',
        end_date='2023-12-31',
        capital_base=100000
    )
    
    # Run backtest
    results = runner.run()
    
    print("✅ Backtest completed successfully!")
    return results

if __name__ == "__main__":
    main()
