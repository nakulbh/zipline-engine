#!/usr/bin/env python3
"""
Complete Workflow: Backtest -> Pickle -> Pyfolio Analysis

This example demonstrates the complete workflow you requested:
1. Run a backtest
2. Save results to a pickle file
3. Load results from pickle
4. Use pyfolio to create comprehensive analysis

Based on your request: "save the backtest result in a pkl file then use pyfolio to get all the results"
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
    Complete workflow demonstration
    """
    print("🚀 COMPLETE BACKTEST -> PICKLE -> PYFOLIO WORKFLOW")
    print("=" * 60)
    
    # Step 1: Create and configure strategy
    print("\n📊 STEP 1: Creating strategy...")
    strategy = VolumePriceTrendStrategy()
    print(f"✅ Strategy created: {strategy.__class__.__name__}")
    
    # Step 2: Configure the backtest runner
    print("\n⚙️  STEP 2: Configuring backtest runner...")
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='SBIN'
    )
    print("✅ Runner configured successfully")
    
    # Step 3: Run the backtest
    print("\n🔄 STEP 3: Running backtest...")
    try:
        results = runner.run()
        if results is not None:
            final_value = results['portfolio_value'].iloc[-1]
            total_return = (final_value / 100000 - 1) * 100
            print(f"✅ Backtest completed successfully!")
            print(f"💰 Final Portfolio Value: ${final_value:,.2f}")
            print(f"📈 Total Return: {total_return:.2f}%")
        else:
            print("❌ Backtest failed - no results returned")
            return
    except Exception as e:
        print(f"❌ Backtest failed: {str(e)}")
        return
    
    # Step 4: Save results to pickle file
    print("\n💾 STEP 4: Saving results to pickle file...")
    results_dir = 'pickle_pyfolio_results'
    pickle_filename = 'backtest_results.pickle'
    
    pickle_path = runner.save_results_to_pickle(
        filename=pickle_filename,
        results_dir=results_dir
    )
    
    if pickle_path:
        print(f"✅ Results saved to pickle: {pickle_path}")
    else:
        print("❌ Failed to save pickle file")
        return
    
    # Step 5: Create comprehensive Pyfolio analysis from pickle
    print("\n📊 STEP 5: Creating comprehensive Pyfolio analysis...")
    
    # Create a new runner instance to demonstrate loading from pickle
    analysis_runner = EnhancedZiplineRunner(
        strategy=strategy,  # We still need strategy for metadata
        bundle='nse-local-minute-bundle',
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='SBIN'
    )
    
    # Create analysis from pickle file
    analysis_dir = os.path.join(results_dir, 'pyfolio_analysis')
    
    try:
        analysis_runner.create_pyfolio_analysis_from_pickle(
            pickle_filepath=pickle_path,
            results_dir=analysis_dir,
            live_start_date='2020-01-01',  # Out-of-sample analysis from last year
            save_plots=True,
            save_csv=True
        )
        print(f"✅ Pyfolio analysis completed!")
        print(f"📁 Analysis saved to: {os.path.abspath(analysis_dir)}")
        
    except Exception as e:
        print(f"❌ Pyfolio analysis failed: {str(e)}")
        print("🔄 Falling back to standard analysis...")
        
        # Fallback to standard analysis
        try:
            analysis_runner.load_results_from_pickle(pickle_path)
            analysis_runner.analyze(analysis_dir)
            print("✅ Standard analysis completed as fallback")
        except Exception as fallback_e:
            print(f"❌ Fallback analysis also failed: {str(fallback_e)}")
    
    # Step 6: Summary and next steps
    print("\n📋 STEP 6: Workflow Summary")
    print("-" * 40)
    print("✅ Backtest executed successfully")
    print(f"✅ Results saved to pickle: {pickle_path}")
    print(f"✅ Pyfolio analysis created in: {analysis_dir}")
    
    print("\n📁 Generated Files:")
    if os.path.exists(results_dir):
        for root, dirs, files in os.walk(results_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, results_dir)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   📄 {rel_path} ({file_size:.1f} KB)")
    
    print("\n🎯 Next Steps:")
    print("1. Review the generated plots and CSV files")
    print("2. Examine the full tear sheet for comprehensive performance metrics")
    print("3. Analyze round trip tear sheet for individual trade performance")
    print("4. Use the pickle file for further custom analysis")
    
    print("\n💡 Usage Examples:")
    print("# Load results for custom analysis:")
    print(f"import pandas as pd")
    print(f"perf = pd.read_pickle('{pickle_path}')")
    print(f"returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)")
    print(f"pf.create_full_tear_sheet(returns, positions, transactions)")
    
    print("\n🚀 Workflow completed successfully!")

if __name__ == "__main__":
    main()
