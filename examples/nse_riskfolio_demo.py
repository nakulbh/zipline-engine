#!/usr/bin/env python3
"""
NSE Riskfolio Strategy Demo
===========================

This demo shows how to run the NSE version of the sophisticated portfolio 
optimization strategy you provided. It demonstrates:

1. Portfolio optimization using Riskfolio-Portfolio
2. Mean-variance optimization with Ledoit-Wolf covariance
3. Dynamic asset screening and selection
4. Risk management and leverage control
5. Comprehensive performance analysis

Key Adaptations for NSE:
- Uses your 8 available NSE assets instead of US equities
- Adapted volatility thresholds for Indian markets
- Conservative leverage (1.2x instead of 1.5x)
- NSE-specific risk management parameters
"""

import os
import sys
import warnings

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.nse_riskfolio_strategy import NSERiskfolioStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

# Suppress warnings
warnings.filterwarnings('ignore')

def run_nse_riskfolio_demo():
    """
    Run the NSE Riskfolio strategy demo
    """
    print("🚀 NSE RISKFOLIO PORTFOLIO STRATEGY DEMO")
    print("=" * 55)
    print("📊 Replicating sophisticated portfolio optimization for NSE markets")
    print()
    
    # Strategy configuration
    print("⚙️  STRATEGY CONFIGURATION")
    print("-" * 30)
    
    strategy_config = {
        'leverage': 1.2,              # 20% leverage (conservative for NSE)
        'lookback_window': 126,       # 6 months (21 days * 6)
        'min_volatility': 0.15,       # 15% minimum volatility
        'max_volatility': 0.60,       # 60% maximum volatility  
        'min_return_target': 0.0008   # Minimum expected return
    }
    
    for key, value in strategy_config.items():
        if 'volatility' in key or 'return' in key:
            print(f"   📈 {key}: {value:.1%}")
        else:
            print(f"   📊 {key}: {value}")
    
    print()
    print("🎯 AVAILABLE NSE ASSETS")
    print("-" * 25)
    nse_assets = [
        "BAJFINANCE - Bajaj Finance",
        "BANKNIFTY - Bank Nifty Index", 
        "HDFCBANK - HDFC Bank",
        "HDFC - HDFC Ltd",
        "HINDALCO - Hindalco Industries",
        "NIFTY50 - Nifty 50 Index",
        "RELIANCE - Reliance Industries",
        "SBIN - State Bank of India"
    ]
    
    for asset in nse_assets:
        print(f"   📈 {asset}")
    
    print()
    print("🔄 RUNNING BACKTEST")
    print("-" * 20)
    
    # Create strategy
    strategy = NSERiskfolioStrategy(**strategy_config)
    
    # Create runner with NSE-specific settings
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2019-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    # Run backtest
    try:
        results = runner.run()
        
        if results is not None:
            final_value = results['portfolio_value'].iloc[-1]
            total_return = (final_value / 100000 - 1) * 100
            
            print()
            print("✅ BACKTEST COMPLETED SUCCESSFULLY!")
            print("=" * 40)
            print(f"💰 Final Portfolio Value: ₹{final_value:,.2f}")
            print(f"📈 Total Return: {total_return:.2f}%")
            print(f"📊 Number of trades: {len(results)}")
            
            # Save results to pickle
            print()
            print("💾 SAVING RESULTS")
            print("-" * 18)
            
            pickle_path = runner.save_results_to_pickle(
                filename="nse_riskfolio_backtest.pickle",
                results_dir="nse_riskfolio_results"
            )
            
            if pickle_path:
                print(f"✅ Results saved to: {pickle_path}")
                
                # Create comprehensive analysis
                print()
                print("📊 CREATING COMPREHENSIVE ANALYSIS")
                print("-" * 35)
                
                try:
                    runner.create_pyfolio_analysis_from_pickle(
                        pickle_filepath=pickle_path,
                        results_dir="nse_riskfolio_results/pyfolio_analysis",
                        save_plots=True,
                        save_csv=True
                    )
                    print("✅ Pyfolio analysis completed")
                    
                except Exception as e:
                    print(f"⚠️  Pyfolio analysis failed: {e}")
                    print("🔄 Creating standard analysis instead...")
                    
                    # Fallback to standard analysis
                    runner.analyze('nse_riskfolio_results/standard_analysis')
                    print("✅ Standard analysis completed")
            
            # Display key insights
            print()
            print("🎯 KEY STRATEGY INSIGHTS")
            print("-" * 25)
            
            # Calculate some basic metrics
            returns = results['returns']
            portfolio_values = results['portfolio_value']
            
            # Performance metrics
            sharpe_ratio = returns.mean() / returns.std() * (252**0.5) if returns.std() > 0 else 0
            max_drawdown = ((portfolio_values / portfolio_values.expanding().max()) - 1).min()
            win_rate = (returns > 0).mean()
            
            print(f"   📈 Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"   📉 Max Drawdown: {max_drawdown:.2%}")
            print(f"   🎲 Win Rate: {win_rate:.1%}")
            print(f"   📊 Volatility: {returns.std() * (252**0.5):.2%}")
            
            # Show file structure
            print()
            print("📁 GENERATED FILES")
            print("-" * 18)
            
            results_dir = "nse_riskfolio_results"
            if os.path.exists(results_dir):
                for root, dirs, files in os.walk(results_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, results_dir)
                        file_size = os.path.getsize(file_path) / 1024  # KB
                        print(f"   📄 {rel_path} ({file_size:.1f} KB)")
            
            print()
            print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 35)
            print()
            print("💡 NEXT STEPS:")
            print("1. Review the generated analysis files")
            print("2. Examine portfolio weights and rebalancing frequency")
            print("3. Compare performance vs NIFTY50 benchmark")
            print("4. Analyze risk-adjusted returns and drawdowns")
            print("5. Consider parameter tuning for better performance")
            
            print()
            print("🔧 STRATEGY CUSTOMIZATION:")
            print("- Adjust leverage for more/less aggressive positioning")
            print("- Modify volatility thresholds for different asset selection")
            print("- Change lookback window for different optimization periods")
            print("- Experiment with different Riskfolio optimization models")
            
        else:
            print("❌ Backtest failed - no results returned")
            
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

def compare_with_original():
    """
    Show comparison between original strategy and NSE adaptation
    """
    print()
    print("🔄 STRATEGY COMPARISON: ORIGINAL vs NSE ADAPTATION")
    print("=" * 55)
    
    comparison = [
        ("Asset Universe", "US Equities (500+ stocks)", "NSE Equities (8 quality stocks)"),
        ("Data Bundle", "Quandl/QuoteMedia", "nse-local-minute-bundle"),
        ("Leverage", "1.5x", "1.2x (more conservative)"),
        ("Volatility Range", "35%-60%", "15%-60% (adapted for NSE)"),
        ("Benchmark", "SPY (S&P 500)", "NIFTY50"),
        ("Currency", "USD", "INR"),
        ("Market Hours", "US Eastern", "Indian Standard Time"),
        ("Optimization", "Riskfolio MV", "Same - Riskfolio MV"),
        ("Covariance", "Ledoit-Wolf", "Same - Ledoit-Wolf"),
        ("Rebalancing", "Weekly", "Same - Weekly")
    ]
    
    print(f"{'Aspect':<15} {'Original':<25} {'NSE Adaptation':<25}")
    print("-" * 65)
    
    for aspect, original, nse in comparison:
        print(f"{aspect:<15} {original:<25} {nse:<25}")
    
    print()
    print("✅ Key advantages of NSE adaptation:")
    print("   🎯 Focused on high-quality Indian blue-chip stocks")
    print("   📊 Conservative risk management for emerging markets")
    print("   🏦 Includes both individual stocks and indices")
    print("   💰 Optimized for INR-based portfolio construction")

def main():
    """
    Main demo function
    """
    run_nse_riskfolio_demo()
    compare_with_original()

if __name__ == "__main__":
    main()
