#!/usr/bin/env python3
"""
Enhanced Pyfolio Analysis Example
=================================

This example demonstrates how to use the enhanced Pyfolio functionality
in the NSE Backtesting Engine, similar to the Pyfolio example you provided.

Features demonstrated:
- Comprehensive Pyfolio tear sheet generation
- Plot saving with high-quality output
- CSV export of all performance metrics
- Round trips analysis
- Risk metrics calculation
- Out-of-sample analysis with live_start_date

Author: NSE Backtesting Engine
Date: 2025-07-07
"""

import os
import sys
import warnings
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from strategies.volume_price_strategy import VolumePriceTrendStrategy

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def main():
    """
    Main function demonstrating enhanced Pyfolio analysis
    """
    print("🚀 Enhanced Pyfolio Analysis Example")
    print("=" * 50)
    
    # 1. Create a strategy instance
    print("📊 Creating strategy...")
    strategy = VolumePriceTrendStrategy()
    
    # 2. Configure the runner
    print("⚙️  Configuring backtest runner...")
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='SBIN'
    )
    
    # 3. Run the backtest
    print("🔄 Running backtest...")
    try:
        results = runner.run()
        print(f"✅ Backtest completed successfully!")
        print(f"📈 Final Portfolio Value: ${results.portfolio_value.iloc[-1]:,.2f}")
        print(f"📊 Total Return: {((results.portfolio_value.iloc[-1] / results.portfolio_value.iloc[0]) - 1) * 100:.2f}%")
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return
    
    # 4. Create results directory
    results_dir = 'enhanced_pyfolio_results'
    os.makedirs(results_dir, exist_ok=True)
    print(f"📁 Results will be saved to: {os.path.abspath(results_dir)}")
    
    # 5. Standard analysis (already includes Pyfolio)
    print("\n📊 Running standard analysis...")
    runner.analyze(results_dir)
    
    # 6. Enhanced Pyfolio analysis (new functionality)
    print("\n🚀 Running enhanced Pyfolio analysis...")
    try:
        # Example with out-of-sample analysis
        # Assume live trading started on 2020-01-01 (last year of backtest)
        live_start_date = '2020-01-01'
        
        runner.create_enhanced_pyfolio_analysis(
            results_dir=results_dir,
            live_start_date=live_start_date,  # Out-of-sample analysis
            save_plots=True,
            save_csv=True
        )
        print("✅ Enhanced Pyfolio analysis completed!")
        
    except Exception as e:
        print(f"⚠️  Enhanced analysis failed: {e}")
        print("📊 Standard analysis is still available in results directory")
    
    # 7. Display results summary
    print("\n📋 Results Summary")
    print("-" * 30)
    
    # List all generated files
    if os.path.exists(results_dir):
        files = os.listdir(results_dir)
        
        print("📊 Generated Analysis Files:")
        for file in sorted(files):
            if file.endswith('.png'):
                print(f"   🖼️  {file}")
            elif file.endswith('.csv'):
                print(f"   📄 {file}")
            else:
                print(f"   📋 {file}")
    
    print(f"\n✅ Analysis complete! Check the '{results_dir}' directory for all results.")
    print("\n📚 Key Files Generated:")
    print("   🖼️  enhanced_pyfolio_analysis.png - Comprehensive performance charts")
    print("   📄 performance_statistics.csv - Key performance metrics")
    print("   📄 returns_series.csv - Daily returns data")
    print("   📄 risk_metrics.csv - Risk analysis metrics")
    print("   📄 round_trips_analysis.csv - Trade round trips analysis")
    print("   📄 monthly_returns.csv - Monthly performance breakdown")
    print("   📄 annual_returns.csv - Annual performance summary")

def demonstrate_csv_analysis():
    """
    Demonstrate how to load and analyze the generated CSV files
    """
    print("\n🔍 CSV Analysis Example")
    print("-" * 30)
    
    import pandas as pd
    
    results_dir = 'enhanced_pyfolio_results'
    
    try:
        # Load performance statistics
        perf_stats = pd.read_csv(os.path.join(results_dir, 'performance_statistics.csv'), index_col=0)
        print("📊 Key Performance Metrics:")

        # Check what columns are available
        col_name = perf_stats.columns[0] if len(perf_stats.columns) > 0 else 'value'

        # Display available metrics
        available_metrics = perf_stats.index.tolist()
        print(f"   📋 Available metrics: {', '.join(available_metrics[:5])}...")

        # Display key metrics if they exist
        for metric_name, display_name in [
            ('Cumulative returns', 'Total Return'),
            ('Sharpe ratio', 'Sharpe Ratio'),
            ('Max drawdown', 'Max Drawdown'),
            ('Annual return', 'Annual Return'),
            ('Annual volatility', 'Annual Volatility')
        ]:
            if metric_name in available_metrics:
                value = perf_stats.loc[metric_name, col_name]
                if 'return' in metric_name.lower() or 'drawdown' in metric_name.lower() or 'volatility' in metric_name.lower():
                    print(f"   📊 {display_name}: {value:.2%}")
                else:
                    print(f"   📊 {display_name}: {value:.2f}")
        
        # Load risk metrics (if available)
        risk_file = os.path.join(results_dir, 'risk_metrics.csv')
        if os.path.exists(risk_file):
            risk_metrics = pd.read_csv(risk_file, index_col=0)
            print("\n🎯 Risk Analysis:")
            col_name = risk_metrics.columns[0] if len(risk_metrics.columns) > 0 else 'value'

            for metric_name, display_name in [
                ('calmar_ratio', 'Calmar Ratio'),
                ('sortino_ratio', 'Sortino Ratio'),
                ('tail_ratio', 'Tail Ratio')
            ]:
                if metric_name in risk_metrics.index:
                    print(f"   📊 {display_name}: {risk_metrics.loc[metric_name, col_name]:.2f}")
        else:
            print("\n🎯 Risk Analysis: Risk metrics file not found")
        
        # Load monthly returns
        monthly_returns = pd.read_csv(os.path.join(results_dir, 'monthly_returns.csv'), index_col=0)
        print(f"\n📅 Monthly Performance:")
        print(f"   📈 Best Month: {monthly_returns['monthly_return'].max():.2%}")
        print(f"   📉 Worst Month: {monthly_returns['monthly_return'].min():.2%}")
        print(f"   📊 Average Month: {monthly_returns['monthly_return'].mean():.2%}")
        
    except FileNotFoundError as e:
        print(f"⚠️  CSV files not found. Run the main analysis first: {e}")
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")

if __name__ == "__main__":
    # Run the main analysis
    main()
    
    # Demonstrate CSV analysis
    demonstrate_csv_analysis()
    
    print("\n🎉 Enhanced Pyfolio Example Complete!")
    print("📚 This example demonstrates:")
    print("   ✅ Comprehensive Pyfolio tear sheet generation")
    print("   ✅ High-quality plot saving")
    print("   ✅ Complete CSV data export")
    print("   ✅ Out-of-sample analysis")
    print("   ✅ Risk metrics calculation")
    print("   ✅ Round trips analysis")
    print("   ✅ Performance statistics")
    print("\n📖 For more information, see the documentation:")
    print("   📄 docs/ZiplineRunner.md")
    print("   📄 docs/APIReference.md")
