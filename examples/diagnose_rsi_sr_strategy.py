#!/usr/bin/env python3
"""
Diagnostic Script for RSI Support/Resistance Strategy

This script helps identify issues with the RSI S/R strategy that might be causing
poor return quantiles by analyzing signals, position sizes, and trade execution.

Author: NSE Backtesting Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from strategies.rsi_support_resistance_strategy import RSISupportResistanceStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def diagnose_strategy_issues():
    """Diagnose potential issues with the RSI S/R strategy"""
    
    print("🔍 RSI Support/Resistance Strategy Diagnostics")
    print("=" * 60)
    
    # Create strategy with diagnostic logging
    strategy = RSISupportResistanceStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70,
        lookback_period=20,
        min_touches=2,
        sr_tolerance=0.02
    )
    
    print("📊 Strategy Configuration:")
    print(f"   RSI Period: {strategy.rsi_period}")
    print(f"   Oversold/Overbought: {strategy.oversold_threshold}/{strategy.overbought_threshold}")
    print(f"   S/R Lookback: {strategy.lookback_period} days")
    print(f"   Min S/R Touches: {strategy.min_touches}")
    print(f"   S/R Tolerance: {strategy.sr_tolerance:.1%}")
    print(f"   Max Position Size: {strategy.risk_params['max_position_size']:.1%}")
    print(f"   Stop Loss: {strategy.risk_params['stop_loss_pct']:.1%}")
    print()
    
    # Test with a short backtest period first
    print("🚀 Running Short Diagnostic Backtest...")
    print("-" * 40)
    
    try:
        runner = EnhancedZiplineRunner(
            strategy=strategy,
            bundle='nse-local-minute-bundle',
            start_date='2020-01-01',
            end_date='2020-06-01',  # Short 5-month test
            capital_base=200000,
            benchmark_symbol='NIFTY50'
        )
        
        results = runner.run()
        
        print("✅ Backtest completed successfully!")
        print()
        
        # Analyze results
        print("📈 Basic Performance Metrics:")
        print("-" * 35)
        
        total_return = results.returns.cumsum().iloc[-1]
        volatility = results.returns.std() * np.sqrt(252)
        sharpe = results.returns.mean() / results.returns.std() * np.sqrt(252) if results.returns.std() > 0 else 0
        max_drawdown = (results.returns.cumsum() - results.returns.cumsum().expanding().max()).min()
        
        print(f"   Total Return: {total_return:.2%}")
        print(f"   Annualized Volatility: {volatility:.2%}")
        print(f"   Sharpe Ratio: {sharpe:.2f}")
        print(f"   Max Drawdown: {max_drawdown:.2%}")
        print()
        
        # Analyze return distribution
        print("📊 Return Distribution Analysis:")
        print("-" * 35)
        
        daily_returns = results.returns
        print(f"   Mean Daily Return: {daily_returns.mean():.4f} ({daily_returns.mean()*252:.2%} annualized)")
        print(f"   Std Daily Return: {daily_returns.std():.4f}")
        print(f"   Skewness: {daily_returns.skew():.2f}")
        print(f"   Kurtosis: {daily_returns.kurtosis():.2f}")
        print()
        
        # Check for extreme returns
        extreme_positive = daily_returns[daily_returns > 0.02].count()  # >2% daily
        extreme_negative = daily_returns[daily_returns < -0.02].count()  # <-2% daily
        
        print(f"   Days with >2% returns: {extreme_positive}")
        print(f"   Days with <-2% returns: {extreme_negative}")
        print()
        
        if extreme_positive > 10 or extreme_negative > 10:
            print("⚠️  WARNING: High number of extreme return days detected!")
            print("   This suggests potential issues with:")
            print("   • Position sizing (too large positions)")
            print("   • Stop loss execution (not working properly)")
            print("   • Signal quality (false signals)")
            print()
        
        # Analyze recorded metrics
        if hasattr(results, 'rsi_value'):
            print("📊 RSI Analysis:")
            print("-" * 20)
            
            rsi_data = results.rsi_value.dropna()
            if len(rsi_data) > 0:
                print(f"   Average RSI: {rsi_data.mean():.1f}")
                print(f"   RSI Range: {rsi_data.min():.1f} - {rsi_data.max():.1f}")
                print(f"   Oversold periods: {(rsi_data <= 30).sum()} days")
                print(f"   Overbought periods: {(rsi_data >= 70).sum()} days")
            print()
        
        # Check leverage usage
        if hasattr(results, 'leverage'):
            leverage_data = results.leverage.dropna()
            if len(leverage_data) > 0:
                print("📊 Leverage Analysis:")
                print("-" * 20)
                print(f"   Average Leverage: {leverage_data.mean():.2f}x")
                print(f"   Max Leverage: {leverage_data.max():.2f}x")
                print(f"   Days with >50% leverage: {(leverage_data > 0.5).sum()}")
                print()
                
                if leverage_data.max() > 1.0:
                    print("⚠️  WARNING: Leverage exceeded 100%!")
                    print("   This could cause amplified losses.")
                    print()
        
        # Check position count
        if hasattr(results, 'positions'):
            position_data = results.positions.dropna()
            if len(position_data) > 0:
                print("📊 Position Analysis:")
                print("-" * 20)
                print(f"   Average Positions: {position_data.mean():.1f}")
                print(f"   Max Positions: {position_data.max():.0f}")
                print(f"   Days with positions: {(position_data > 0).sum()}")
                print()
        
        # Recommendations based on analysis
        print("💡 Diagnostic Recommendations:")
        print("-" * 35)
        
        if total_return < -0.05:  # More than 5% loss
            print("🔴 POOR PERFORMANCE DETECTED:")
            print("   1. Check if S/R levels are being identified correctly")
            print("   2. Verify position sizing isn't too aggressive")
            print("   3. Ensure stop losses are executing properly")
            print("   4. Consider tightening RSI thresholds (25/75 instead of 30/70)")
            print()
        
        if volatility > 0.3:  # More than 30% annualized volatility
            print("🟡 HIGH VOLATILITY DETECTED:")
            print("   1. Reduce maximum position size")
            print("   2. Tighten stop loss percentages")
            print("   3. Increase minimum S/R touches requirement")
            print()
        
        if sharpe < 0:
            print("🔴 NEGATIVE SHARPE RATIO:")
            print("   1. Strategy is not compensating for risk taken")
            print("   2. Consider using only strong confluence signals")
            print("   3. Review signal generation logic")
            print()
        
        # Specific fixes to try
        print("🔧 Suggested Strategy Modifications:")
        print("-" * 40)
        print("1. Reduce max position size to 8%:")
        print("   strategy.risk_params['max_position_size'] = 0.08")
        print()
        print("2. Tighten stop losses to 3%:")
        print("   strategy.risk_params['stop_loss_pct'] = 0.03")
        print()
        print("3. Use only strong confluence signals:")
        print("   # In generate_signals, set weak signals to 0.0")
        print()
        print("4. Increase S/R validation:")
        print("   min_touches=3, sr_tolerance=0.015")
        print()
        
    except Exception as e:
        print(f"❌ Backtest failed with error: {e}")
        print()
        print("🔧 Troubleshooting Steps:")
        print("1. Check if the data bundle is properly ingested")
        print("2. Verify the date range has sufficient data")
        print("3. Ensure all required symbols are available")
        print("4. Check for any import or dependency issues")

def create_fixed_strategy():
    """Create a potentially improved version of the strategy"""
    
    print("\n🔧 Creating Improved Strategy Configuration:")
    print("-" * 50)
    
    # More conservative strategy
    improved_strategy = RSISupportResistanceStrategy(
        rsi_period=14,
        oversold_threshold=25,      # More aggressive entry
        overbought_threshold=75,    # More aggressive entry
        lookback_period=30,         # Longer S/R analysis
        min_touches=3,              # Stricter S/R validation
        sr_tolerance=0.015          # Tighter clustering
    )
    
    # More conservative risk parameters
    improved_strategy.risk_params.update({
        'max_position_size': 0.08,    # Smaller positions
        'stop_loss_pct': 0.03,        # Tighter stops
        'take_profit_pct': 0.12,      # Reasonable profits
        'max_leverage': 0.6,          # Lower leverage
    })
    
    print("📊 Improved Strategy Configuration:")
    print(f"   RSI Thresholds: {improved_strategy.oversold_threshold}/{improved_strategy.overbought_threshold}")
    print(f"   S/R Lookback: {improved_strategy.lookback_period} days")
    print(f"   Min S/R Touches: {improved_strategy.min_touches}")
    print(f"   S/R Tolerance: {improved_strategy.sr_tolerance:.1%}")
    print(f"   Max Position: {improved_strategy.risk_params['max_position_size']:.1%}")
    print(f"   Stop Loss: {improved_strategy.risk_params['stop_loss_pct']:.1%}")
    print(f"   Max Leverage: {improved_strategy.risk_params['max_leverage']:.1%}")
    print()
    
    return improved_strategy

if __name__ == "__main__":
    diagnose_strategy_issues()
    create_fixed_strategy()
    
    print("✅ Diagnostics Complete!")
    print()
    print("📝 Next Steps:")
    print("1. Run this diagnostic script to identify issues")
    print("2. Apply the suggested modifications")
    print("3. Test with the improved strategy configuration")
    print("4. Monitor the return quantiles in the next backtest")
