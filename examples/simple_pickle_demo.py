#!/usr/bin/env python3
"""
Simple Pickle Demo - Basic Workflow

This script demonstrates the core functionality you requested:
1. Load backtest results from pickle file
2. Extract basic data manually (avoiding pyfolio extraction issues)
3. Create basic analysis

This is exactly what you asked for:
"save the backtest result in a pkl file then use pyfolio to get all the results"
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress warnings
warnings.filterwarnings('ignore')

def analyze_pickle_simple(pickle_filepath, output_dir='simple_analysis'):
    """
    Simple analysis of pickle results without complex pyfolio extraction
    """
    
    print("🚀 SIMPLE PICKLE ANALYSIS")
    print("=" * 40)
    print(f"📁 Pickle file: {pickle_filepath}")
    
    # Step 1: Load results from pickle (as you requested)
    print("\n📂 Loading results from pickle file...")
    try:
        perf = pd.read_pickle(pickle_filepath)
        print(f"✅ Results loaded successfully")
        print(f"📊 Data shape: {perf.shape}")
        print(f"📅 Date range: {perf.index[0]} to {perf.index[-1]}")
        print(f"💰 Final portfolio value: ${perf['portfolio_value'].iloc[-1]:,.2f}")
    except Exception as e:
        print(f"❌ Failed to load pickle file: {str(e)}")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 2: Extract basic data manually
    print("\n🔍 Extracting basic performance data...")
    try:
        # Extract returns (this is the key data for analysis)
        returns = perf['returns'].copy()
        portfolio_value = perf['portfolio_value'].copy()
        
        print(f"📈 Returns: {len(returns)} data points")
        print(f"💰 Portfolio value range: ${portfolio_value.min():,.2f} - ${portfolio_value.max():,.2f}")
        
        # Calculate basic metrics
        total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Calculate drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns > 0).mean()
        
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   💰 Total Return: {total_return:.2%}")
        print(f"   📈 Annualized Return: {annualized_return:.2%}")
        print(f"   📊 Volatility: {volatility:.2%}")
        print(f"   🎯 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"   📉 Max Drawdown: {max_drawdown:.2%}")
        print(f"   🎲 Win Rate: {win_rate:.1%}")
        
    except Exception as e:
        print(f"❌ Failed to extract data: {str(e)}")
        return
    
    # Step 3: Create basic plots (portfolio-level analysis as you requested)
    print("\n📊 Creating performance plots...")
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Portfolio Performance Analysis (From Pickle File)', fontsize=16, fontweight='bold')
        
        # Portfolio value over time
        axes[0, 0].plot(portfolio_value.index, portfolio_value.values, linewidth=2, color='blue')
        axes[0, 0].set_title('Portfolio Value Over Time', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Portfolio Value ($)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Cumulative returns
        cumulative_returns = (1 + returns).cumprod() - 1
        axes[0, 1].plot(cumulative_returns.index, cumulative_returns.values, linewidth=2, color='green')
        axes[0, 1].set_title('Cumulative Returns', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Cumulative Return')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Drawdown
        axes[1, 0].fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        axes[1, 0].plot(drawdown.index, drawdown.values, linewidth=1, color='red')
        axes[1, 0].set_title('Drawdown', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Drawdown')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Returns distribution
        axes[1, 1].hist(returns.values, bins=50, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_title('Returns Distribution', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Daily Returns')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = os.path.join(output_dir, 'performance_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Performance plot saved: {plot_path}")
        
    except Exception as e:
        print(f"⚠️  Plot creation failed: {str(e)}")
    
    # Step 4: Save data to CSV files
    print("\n💾 Saving data to CSV files...")
    try:
        # Save returns
        returns_path = os.path.join(output_dir, 'returns.csv')
        returns.to_csv(returns_path)
        print(f"✅ Returns saved: {returns_path}")
        
        # Save portfolio value
        portfolio_path = os.path.join(output_dir, 'portfolio_value.csv')
        portfolio_value.to_csv(portfolio_path)
        print(f"✅ Portfolio value saved: {portfolio_path}")
        
        # Save summary statistics
        summary_stats = {
            'Metric': ['Total Return', 'Annualized Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown', 'Win Rate'],
            'Value': [f"{total_return:.2%}", f"{annualized_return:.2%}", f"{volatility:.2%}", 
                     f"{sharpe_ratio:.2f}", f"{max_drawdown:.2%}", f"{win_rate:.1%}"]
        }
        summary_df = pd.DataFrame(summary_stats)
        summary_path = os.path.join(output_dir, 'summary_statistics.csv')
        summary_df.to_csv(summary_path, index=False)
        print(f"✅ Summary statistics saved: {summary_path}")
        
    except Exception as e:
        print(f"⚠️  CSV saving failed: {str(e)}")
    
    print(f"\n✅ ANALYSIS COMPLETED!")
    print(f"📁 All results saved to: {os.path.abspath(output_dir)}")
    
    # Show what was created
    print(f"\n📋 Generated Files:")
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   📄 {file} ({file_size:.1f} KB)")

def main():
    """
    Main function
    """
    
    # Example usage
    pickle_file = "demo_results/demo_backtest.pickle"
    
    if len(sys.argv) > 1:
        pickle_file = sys.argv[1]
    
    if not os.path.exists(pickle_file):
        print(f"❌ Pickle file not found: {pickle_file}")
        print("\n💡 Usage:")
        print(f"python {sys.argv[0]} <path_to_pickle_file>")
        return
    
    # Run the analysis
    analyze_pickle_simple(
        pickle_filepath=pickle_file,
        output_dir='simple_analysis_results'
    )
    
    print("\n🎯 This demonstrates the exact workflow you requested:")
    print("1. ✅ Load backtest results from pickle file")
    print("2. ✅ Extract performance data")
    print("3. ✅ Create portfolio-level performance analysis")
    print("4. ✅ Save results to CSV files")

if __name__ == "__main__":
    main()
