#!/usr/bin/env python3
"""
RSI Strategy Comparison Script

This script demonstrates the differences between:
1. RSI Strategy with ATR-based stops and position sizing
2. RSI Strategy with Support/Resistance-based stops and position sizing

Author: NSE Backtesting Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.rsi_strategy import RSIMeanReversionStrategy
from strategies.rsi_support_resistance_strategy import RSISupportResistanceStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
import pandas as pd

def compare_rsi_strategies():
    """Compare ATR-based vs Support/Resistance-based RSI strategies"""
    
    print("🎯 RSI Strategy Comparison")
    print("=" * 60)
    print()
    
    # Common parameters
    common_params = {
        'rsi_period': 14,
        'oversold_threshold': 30,
        'overbought_threshold': 70
    }
    
    backtest_params = {
        'bundle': 'nse-local-minute-bundle',
        'start_date': '2020-01-01',
        'end_date': '2022-01-01',
        'capital_base': 200000,
        'benchmark_symbol': 'NIFTY50'
    }
    
    print("📊 Strategy Configurations:")
    print("-" * 30)
    
    # Strategy 1: ATR-based RSI
    print("1️⃣  ATR-Based RSI Strategy:")
    atr_strategy = RSIMeanReversionStrategy(
        position_scaling=True,
        **common_params
    )
    print(f"   • Position Sizing: ATR-based (Van Tharp method)")
    print(f"   • Stop Loss: 2x ATR or 10% (whichever is wider)")
    print(f"   • Take Profit: 1.5x ATR or 8% (whichever is closer)")
    print(f"   • Risk per Trade: 1% of portfolio")
    print(f"   • Max Position: {atr_strategy.risk_params['max_position_size']:.0%}")
    print()
    
    # Strategy 2: Support/Resistance-based RSI
    print("2️⃣  Support/Resistance-Based RSI Strategy:")
    sr_strategy = RSISupportResistanceStrategy(
        lookback_period=20,
        min_touches=2,
        sr_tolerance=0.02,
        **common_params
    )
    print(f"   • Position Sizing: S/R distance-based")
    print(f"   • Stop Loss: 0.5% below support (longs) / above resistance (shorts)")
    print(f"   • Take Profit: 0.5% below resistance (longs) / above support (shorts)")
    print(f"   • Risk per Trade: 1.5% of portfolio")
    print(f"   • Max Position: {sr_strategy.risk_params['max_position_size']:.0%}")
    print(f"   • S/R Lookback: {sr_strategy.lookback_period} days")
    print(f"   • Min S/R Touches: {sr_strategy.min_touches}")
    print()
    
    print("🔄 Key Differences:")
    print("-" * 20)
    print("ATR Strategy:")
    print("  ✓ Adapts to volatility automatically")
    print("  ✓ Works in all market conditions")
    print("  ✓ Consistent risk management")
    print("  ✓ No dependency on price patterns")
    print()
    
    print("S/R Strategy:")
    print("  ✓ Uses actual technical levels")
    print("  ✓ Better confluence signals")
    print("  ✓ More intuitive for technical traders")
    print("  ✓ Precise entry/exit points")
    print()
    
    print("📈 Signal Generation Comparison:")
    print("-" * 35)
    
    # Mock data for demonstration
    mock_price = 100.0
    mock_rsi = 25  # Oversold
    
    print(f"Example: Stock at ₹{mock_price}, RSI = {mock_rsi} (oversold)")
    print()
    
    print("ATR Strategy Signal:")
    print(f"  • RSI {mock_rsi} ≤ 30 → Buy signal strength based on RSI extremeness")
    print(f"  • Position size based on ATR volatility")
    print(f"  • Stop at price - (2 × ATR) or price × 0.90")
    print()
    
    print("S/R Strategy Signal:")
    print(f"  • RSI {mock_rsi} ≤ 30 + Near Support → Strong buy signal")
    print(f"  • RSI {mock_rsi} ≤ 30 + No Support → Weak buy signal")
    print(f"  • Position size based on distance to support level")
    print(f"  • Stop 0.5% below nearest support level")
    print()
    
    print("🎛️ When to Use Each Strategy:")
    print("-" * 35)
    
    print("Use ATR Strategy when:")
    print("  • Trading volatile or trending markets")
    print("  • Want consistent risk management")
    print("  • Don't want to analyze charts manually")
    print("  • Trading multiple timeframes")
    print()
    
    print("Use S/R Strategy when:")
    print("  • Trading range-bound markets")
    print("  • Want precise technical entries")
    print("  • Comfortable with chart analysis")
    print("  • Trading liquid, well-established stocks")
    print()
    
    print("📊 Metrics Comparison:")
    print("-" * 25)
    
    print("ATR Strategy Records:")
    print("  • avg_rsi, atr, atr_percentage")
    print("  • volatility_regime_high/low")
    print("  • rsi_atr_combo, signal_atr_adjusted")
    print()
    
    print("S/R Strategy Records:")
    print("  • nearest_support, nearest_resistance")
    print("  • support_distance, resistance_distance")
    print("  • total_support_levels, total_resistance_levels")
    print("  • sr_stop_positions, sr_profit_positions")
    print()
    
    # Uncomment below to run actual backtests
    """
    print("🚀 Running Backtests...")
    print("-" * 25)
    
    # Run ATR strategy
    print("Running ATR-based RSI strategy...")
    atr_runner = EnhancedZiplineRunner(strategy=atr_strategy, **backtest_params)
    atr_results = atr_runner.run()
    
    # Run S/R strategy  
    print("Running S/R-based RSI strategy...")
    sr_runner = EnhancedZiplineRunner(strategy=sr_strategy, **backtest_params)
    sr_results = sr_runner.run()
    
    # Compare results
    print("📈 Results Comparison:")
    print("-" * 25)
    
    atr_returns = atr_results.returns.cumsum().iloc[-1]
    sr_returns = sr_results.returns.cumsum().iloc[-1]
    
    print(f"ATR Strategy Total Return: {atr_returns:.2%}")
    print(f"S/R Strategy Total Return: {sr_returns:.2%}")
    
    atr_sharpe = atr_results.returns.mean() / atr_results.returns.std() * (252**0.5)
    sr_sharpe = sr_results.returns.mean() / sr_results.returns.std() * (252**0.5)
    
    print(f"ATR Strategy Sharpe Ratio: {atr_sharpe:.2f}")
    print(f"S/R Strategy Sharpe Ratio: {sr_sharpe:.2f}")
    """
    
    print("✅ Comparison Complete!")
    print()
    print("💡 Recommendation:")
    print("   Try both strategies on your data to see which works better")
    print("   for your specific assets and market conditions.")

if __name__ == "__main__":
    compare_rsi_strategies()
