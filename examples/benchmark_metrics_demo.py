#!/usr/bin/env python3
"""
Benchmark Metrics Demo
======================

This demo shows how to get comprehensive benchmark analysis including:
- Alpha: Strategy's excess return vs benchmark, adjusted for risk
- Beta: Strategy's sensitivity to benchmark movements  
- Benchmark returns: The benchmark's own returns
- Excess return: Strategy return - benchmark return
- Benchmark volatility: Standard deviation of benchmark returns

All these metrics will be saved to CSV files for analysis.
"""

import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.bollinger_strategy import BollingerBandsStrategy
from strategies.momentum_strategy import MultiTimeframeMomentumStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

def demo_benchmark_metrics():
    """
    Demonstrate comprehensive benchmark metrics extraction
    """
    print("🚀 BENCHMARK METRICS DEMO")
    print("=" * 30)
    print("📊 This demo shows how to extract Alpha, Beta, Benchmark Returns,")
    print("   Excess Returns, and Benchmark Volatility from your backtests")
    print()
    
    # Create strategy with benchmark
    print("⚙️  Creating Bollinger Bands strategy with NIFTY50 benchmark...")
    strategy = BollingerBandsStrategy(
        bb_period=20,
        bb_std=2.0,
        benchmark_symbol='NIFTY50'  # Set benchmark
    )
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'  # Ensure benchmark is set
    )
    
    print(f"📊 Benchmark set to: {runner.benchmark_symbol}")
    print()
    
    # Run backtest
    print("🔄 Running backtest with benchmark analysis...")
    results = runner.run()
    
    if results is None:
        print("❌ Backtest failed")
        return
    
    # Display basic results
    final_value = results['portfolio_value'].iloc[-1]
    total_return = (final_value / 100000 - 1) * 100
    
    print("✅ Backtest completed successfully!")
    print(f"💰 Final Portfolio Value: ₹{final_value:,.2f}")
    print(f"📈 Total Return: {total_return:.2f}%")
    print()
    
    # Check what benchmark columns are available
    benchmark_columns = [col for col in results.columns if 'benchmark' in col.lower()]
    print("📊 Available benchmark data columns:")
    for col in benchmark_columns:
        print(f"   📈 {col}")
    print()
    
    # Save results with comprehensive analysis
    print("💾 Saving comprehensive analysis with benchmark metrics...")
    results_dir = 'benchmark_metrics_results'
    
    # This will automatically extract and save all benchmark metrics
    runner.analyze(results_dir)
    
    print(f"✅ Analysis completed! Check the '{results_dir}' directory for:")
    print("   📄 basic_results.csv - Includes benchmark returns and excess returns")
    print("   📄 benchmark_metrics.csv - Alpha, Beta, and all benchmark metrics")
    print("   📄 benchmark_timeseries.csv - Time series comparison data")
    print("   📄 performance_stats.csv - Overall performance statistics")
    print()
    
    # Display key benchmark metrics if available
    try:
        import pandas as pd
        metrics_file = os.path.join(results_dir, 'benchmark_metrics.csv')
        if os.path.exists(metrics_file):
            metrics_df = pd.read_csv(metrics_file, index_col=0)
            
            print("🎯 KEY BENCHMARK METRICS:")
            print("-" * 25)
            
            key_metrics = [
                'Alpha (Annualized)',
                'Beta', 
                'Benchmark Returns (Annualized)',
                'Excess Return (Annualized)',
                'Benchmark Volatility (Annualized)',
                'Information Ratio',
                'Correlation'
            ]
            
            for metric in key_metrics:
                if metric in metrics_df.index:
                    value = metrics_df.loc[metric, 'Value']
                    if 'Return' in metric or 'Alpha' in metric or 'Volatility' in metric:
                        print(f"   📊 {metric}: {value:.4f} ({value*100:.2f}%)")
                    else:
                        print(f"   📊 {metric}: {value:.4f}")
            
            print()
            print("💡 Interpretation:")
            alpha = metrics_df.loc['Alpha (Annualized)', 'Value'] if 'Alpha (Annualized)' in metrics_df.index else 0
            beta = metrics_df.loc['Beta', 'Value'] if 'Beta' in metrics_df.index else 0
            
            if alpha > 0:
                print(f"   ✅ Positive Alpha ({alpha*100:.2f}%): Strategy outperformed benchmark")
            else:
                print(f"   ❌ Negative Alpha ({alpha*100:.2f}%): Strategy underperformed benchmark")
            
            if beta > 1:
                print(f"   📈 High Beta ({beta:.2f}): Strategy is more volatile than benchmark")
            elif beta < 1:
                print(f"   📉 Low Beta ({beta:.2f}): Strategy is less volatile than benchmark")
            else:
                print(f"   📊 Beta ≈ 1 ({beta:.2f}): Strategy moves with benchmark")
                
    except Exception as e:
        print(f"⚠️  Could not display metrics: {e}")
    
    return results

def compare_strategies_vs_benchmark():
    """
    Compare different strategies against the same benchmark
    """
    print("\n🔄 STRATEGY COMPARISON AGAINST BENCHMARK")
    print("=" * 45)
    
    strategies_config = [
        {
            'name': 'Bollinger Bands',
            'strategy': BollingerBandsStrategy(bb_period=20, benchmark_symbol='NIFTY50'),
            'results_dir': 'bollinger_vs_nifty50'
        },
        {
            'name': 'Momentum',
            'strategy': MultiTimeframeMomentumStrategy(
                short_periods=[5, 10],
                medium_periods=[15, 20],
                long_periods=[30, 50],
                benchmark_symbol='NIFTY50'
            ),
            'results_dir': 'momentum_vs_nifty50'
        }
    ]
    
    comparison_results = {}
    
    for config in strategies_config:
        print(f"\n📊 Testing {config['name']} strategy...")
        
        runner = EnhancedZiplineRunner(
            strategy=config['strategy'],
            bundle='nse-local-minute-bundle',
            start_date='2020-01-01',
            end_date='2020-12-31',  # Shorter period for comparison
            capital_base=100000,
            benchmark_symbol='NIFTY50'
        )
        
        results = runner.run()
        
        if results is not None:
            final_value = results['portfolio_value'].iloc[-1]
            total_return = (final_value / 100000 - 1) * 100
            
            # Save analysis
            runner.analyze(config['results_dir'])
            
            comparison_results[config['name']] = {
                'return': total_return,
                'final_value': final_value,
                'results_dir': config['results_dir']
            }
            
            print(f"   ✅ {config['name']}: {total_return:.2f}% return")
    
    # Display comparison
    if comparison_results:
        print("\n📊 STRATEGY COMPARISON SUMMARY")
        print("=" * 35)
        print(f"{'Strategy':<15} {'Return':<10} {'Final Value':<15}")
        print("-" * 45)
        
        for name, data in comparison_results.items():
            print(f"{name:<15} {data['return']:>8.2f}% ₹{data['final_value']:>12,.2f}")
        
        print("\n💡 Check individual results directories for detailed benchmark analysis:")
        for name, data in comparison_results.items():
            print(f"   📁 {data['results_dir']}/benchmark_metrics.csv")

def main():
    """
    Run benchmark metrics demonstration
    """
    try:
        # Demo 1: Single strategy with comprehensive benchmark analysis
        demo_benchmark_metrics()
        
        # Demo 2: Compare multiple strategies against same benchmark
        # compare_strategies_vs_benchmark()
        
        print("\n🎉 BENCHMARK METRICS DEMO COMPLETED!")
        print("=" * 40)
        print("\n📋 Generated Files:")
        print("   📄 basic_results.csv - Portfolio vs benchmark performance")
        print("   📄 benchmark_metrics.csv - Alpha, Beta, and all metrics")
        print("   📄 benchmark_timeseries.csv - Time series comparison")
        print("   📄 performance_stats.csv - Comprehensive statistics")
        
        print("\n🎯 Key Metrics Explained:")
        print("   📊 Alpha: Excess return vs benchmark (risk-adjusted)")
        print("   📊 Beta: Sensitivity to benchmark movements")
        print("   📊 Excess Return: Strategy return - benchmark return")
        print("   📊 Information Ratio: Excess return / tracking error")
        print("   📊 Correlation: How closely strategy follows benchmark")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
