#!/usr/bin/env python3
"""
Benchmark Examples for NSE Backtesting Engine
==============================================

This script demonstrates different ways to set benchmarks in your strategies.
Benchmarks are crucial for evaluating strategy performance relative to market indices.

Available NSE Benchmarks:
- NIFTY50: Nifty 50 Index (broad market)
- BANKNIFTY: Bank Nifty Index (banking sector)
- SBIN: State Bank of India (individual stock)
- RELIANCE: Reliance Industries (individual stock)
- HDFCBANK: HDFC Bank (individual stock)
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.bollinger_strategy import BollingerBandsStrategy
from strategies.momentum_strategy import MomentumStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

def example_1_strategy_level_benchmark():
    """
    Example 1: Set benchmark at strategy level
    This is the most flexible approach - each strategy can have its own benchmark
    """
    print("🎯 EXAMPLE 1: Strategy-Level Benchmark")
    print("=" * 45)
    
    # Create strategy with benchmark specified in constructor
    strategy = BollingerBandsStrategy(
        bb_period=20,
        bb_std=2.0,
        benchmark_symbol='NIFTY50'  # Set benchmark here
    )
    
    # Create runner (benchmark will be set by strategy)
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2020-12-31',
        capital_base=100000
        # No benchmark_symbol needed here - strategy handles it
    )
    
    print(f"📊 Strategy benchmark: {strategy.benchmark_symbol}")
    print("🔄 Running backtest...")
    
    results = runner.run()
    
    if results is not None:
        final_value = results['portfolio_value'].iloc[-1]
        total_return = (final_value / 100000 - 1) * 100
        print(f"✅ Backtest completed!")
        print(f"💰 Final Value: ₹{final_value:,.2f}")
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"📊 Benchmark: {strategy.benchmark_symbol}")
    
    return results

def example_2_runner_level_benchmark():
    """
    Example 2: Set benchmark at runner level
    This overrides any strategy-level benchmark
    """
    print("\n🎯 EXAMPLE 2: Runner-Level Benchmark")
    print("=" * 42)
    
    # Create strategy without specific benchmark
    strategy = MomentumStrategy(
        short_window=5,
        medium_window=15,
        long_window=30
    )
    
    # Set benchmark in runner (this takes precedence)
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2020-12-31',
        capital_base=100000,
        benchmark_symbol='BANKNIFTY'  # Set benchmark here
    )
    
    print(f"📊 Runner benchmark: {runner.benchmark_symbol}")
    print("🔄 Running backtest...")
    
    results = runner.run()
    
    if results is not None:
        final_value = results['portfolio_value'].iloc[-1]
        total_return = (final_value / 100000 - 1) * 100
        print(f"✅ Backtest completed!")
        print(f"💰 Final Value: ₹{final_value:,.2f}")
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"📊 Benchmark: {runner.benchmark_symbol}")
    
    return results

def example_3_compare_benchmarks():
    """
    Example 3: Compare same strategy against different benchmarks
    """
    print("\n🎯 EXAMPLE 3: Benchmark Comparison")
    print("=" * 38)
    
    benchmarks = ['NIFTY50', 'BANKNIFTY', 'SBIN']
    results_comparison = {}
    
    for benchmark in benchmarks:
        print(f"\n📊 Testing with benchmark: {benchmark}")
        print("-" * 30)
        
        # Create strategy with specific benchmark
        strategy = BollingerBandsStrategy(
            bb_period=15,
            bb_std=2.0,
            benchmark_symbol=benchmark
        )
        
        runner = EnhancedZiplineRunner(
            strategy=strategy,
            bundle='nse-local-minute-bundle',
            start_date='2020-01-01',
            end_date='2020-06-30',  # Shorter period for comparison
            capital_base=100000
        )
        
        results = runner.run()
        
        if results is not None:
            final_value = results['portfolio_value'].iloc[-1]
            total_return = (final_value / 100000 - 1) * 100
            
            results_comparison[benchmark] = {
                'final_value': final_value,
                'total_return': total_return,
                'results': results
            }
            
            print(f"   💰 Final Value: ₹{final_value:,.2f}")
            print(f"   📈 Total Return: {total_return:.2f}%")
    
    # Display comparison
    print("\n📊 BENCHMARK COMPARISON SUMMARY")
    print("=" * 35)
    print(f"{'Benchmark':<12} {'Final Value':<15} {'Return':<10}")
    print("-" * 40)
    
    for benchmark, data in results_comparison.items():
        print(f"{benchmark:<12} ₹{data['final_value']:>12,.2f} {data['total_return']:>8.2f}%")
    
    return results_comparison

def example_4_custom_benchmark_strategy():
    """
    Example 4: Create a strategy that dynamically selects benchmark
    """
    print("\n🎯 EXAMPLE 4: Dynamic Benchmark Selection")
    print("=" * 45)
    
    class DynamicBenchmarkStrategy(BollingerBandsStrategy):
        """
        Strategy that selects benchmark based on market conditions
        """
        def __init__(self, **kwargs):
            # Start with default benchmark
            super().__init__(benchmark_symbol='NIFTY50', **kwargs)
            
        def select_benchmark_dynamically(self, context, data):
            """
            Example: Switch benchmark based on strategy focus
            """
            # If we're trading banking stocks, use BANKNIFTY
            banking_stocks = ['SBIN', 'HDFCBANK']
            if any(str(asset).split('(')[1].split(')')[0] in banking_stocks 
                   for asset in context.universe):
                return 'BANKNIFTY'
            else:
                return 'NIFTY50'
    
    strategy = DynamicBenchmarkStrategy(
        bb_period=20,
        bb_std=2.0
    )
    
    print(f"📊 Initial benchmark: {strategy.benchmark_symbol}")
    
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2020-06-30',
        capital_base=100000
    )
    
    results = runner.run()
    
    if results is not None:
        final_value = results['portfolio_value'].iloc[-1]
        total_return = (final_value / 100000 - 1) * 100
        print(f"✅ Dynamic benchmark strategy completed!")
        print(f"💰 Final Value: ₹{final_value:,.2f}")
        print(f"📈 Total Return: {total_return:.2f}%")
    
    return results

def main():
    """
    Run all benchmark examples
    """
    print("🚀 NSE BACKTESTING ENGINE - BENCHMARK EXAMPLES")
    print("=" * 55)
    print("📊 This demo shows different ways to set benchmarks")
    print()
    
    try:
        # Run examples
        example_1_strategy_level_benchmark()
        example_2_runner_level_benchmark()
        example_3_compare_benchmarks()
        example_4_custom_benchmark_strategy()
        
        print("\n🎉 ALL BENCHMARK EXAMPLES COMPLETED!")
        print("=" * 40)
        
        print("\n💡 KEY TAKEAWAYS:")
        print("1. ✅ Strategy-level benchmarks: Set in strategy constructor")
        print("2. ✅ Runner-level benchmarks: Set in runner constructor")
        print("3. ✅ Runner benchmark overrides strategy benchmark")
        print("4. ✅ Compare performance against different benchmarks")
        print("5. ✅ Dynamic benchmark selection based on strategy logic")
        
        print("\n📊 AVAILABLE NSE BENCHMARKS:")
        benchmarks = [
            "NIFTY50 - Broad market index",
            "BANKNIFTY - Banking sector index", 
            "SBIN - State Bank of India",
            "RELIANCE - Reliance Industries",
            "HDFCBANK - HDFC Bank",
            "BAJFINANCE - Bajaj Finance",
            "HDFC - HDFC Ltd",
            "HINDALCO - Hindalco Industries"
        ]
        
        for benchmark in benchmarks:
            print(f"   📈 {benchmark}")
            
    except Exception as e:
        print(f"❌ Error in benchmark examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
