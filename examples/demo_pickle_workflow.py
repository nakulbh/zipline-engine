#!/usr/bin/env python3
"""
Demo: Pickle Workflow for NSE Backtesting Engine

This script demonstrates the exact workflow you requested:
1. Run a backtest
2. Save results to pickle file  
3. Load pickle file and create Pyfolio analysis

Usage:
    python demo_pickle_workflow.py
"""

import os
import sys
import warnings

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from strategies.volume_price_strategy import VolumePriceTrendStrategy

# Suppress warnings
warnings.filterwarnings('ignore')

def demo_workflow():
    """
    Demonstrate the complete pickle workflow
    """
    print("🚀 NSE BACKTESTING ENGINE - PICKLE WORKFLOW DEMO")
    print("=" * 55)
    
    # 1. Create strategy
    print("📊 Creating strategy...")
    strategy = VolumePriceTrendStrategy()
    
    # 2. Setup runner
    print("⚙️  Setting up backtest runner...")
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2019-01-01',
        end_date='2020-01-01',  # Shorter period for demo
        capital_base=100000,
        benchmark_symbol='SBIN'
    )
    
    # 3. Run backtest
    print("🔄 Running backtest...")
    results = runner.run()
    
    if results is None:
        print("❌ Backtest failed")
        return
    
    print(f"✅ Backtest completed!")
    print(f"💰 Final Value: ${results['portfolio_value'].iloc[-1]:,.2f}")
    
    # 4. Save to pickle
    print("💾 Saving results to pickle...")
    pickle_path = runner.save_results_to_pickle(
        filename="demo_backtest.pickle",
        results_dir="demo_results"
    )
    
    if not pickle_path:
        print("❌ Failed to save pickle")
        return
    
    # 5. Create Pyfolio analysis from pickle
    print("📊 Creating Pyfolio analysis from pickle...")
    runner.create_pyfolio_analysis_from_pickle(
        pickle_filepath=pickle_path,
        results_dir="demo_results/pyfolio_analysis",
        save_plots=True,
        save_csv=True
    )
    
    print("✅ Demo completed successfully!")
    print("📁 Check 'demo_results' folder for all outputs")

if __name__ == "__main__":
    demo_workflow()
