#!/usr/bin/env python3
"""
Benchmark Examples - Demonstrates benchmark comparison functionality
"""

from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from strategies.sma_strategy import SmaCrossoverStrategy

def run_benchmark_example():
    """Run strategy with benchmark comparison"""
    print("📊 Benchmark Comparison Example")
    print("=" * 40)
    
    # Initialize strategy
    strategy = SmaCrossoverStrategy()
    
    # Initialize runner with benchmark
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle_name='nse-duckdb-parquet-bundle',
        start_date='2023-01-01',
        end_date='2023-12-31',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    # Run backtest
    results = runner.run()
    
    print("✅ Benchmark comparison completed!")
    return results

if __name__ == "__main__":
    run_benchmark_example()
