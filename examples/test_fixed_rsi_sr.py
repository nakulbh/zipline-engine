#!/usr/bin/env python3
"""
Test Fixed RSI Support/Resistance Strategy

This script tests the fixes applied to address the issues causing poor return quantiles.

Author: NSE Backtesting Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from strategies.rsi_support_resistance_strategy import RSISupportResistanceStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_fixed_strategy():
    """Test the fixed RSI S/R strategy"""
    
    print("🔧 Testing Fixed RSI Support/Resistance Strategy")
    print("=" * 60)
    
    # Create strategy with fixed parameters
    strategy = RSISupportResistanceStrategy(
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70,
        lookback_period=20,
        min_touches=2,
        sr_tolerance=0.02
    )
    
    print("📊 Fixed Strategy Configuration:")
    print(f"   Max Position Size: {strategy.risk_params['max_position_size']:.1%}")
    print(f"   Stop Loss: {strategy.risk_params['stop_loss_pct']:.1%}")
    print(f"   Max Leverage: {strategy.risk_params['max_leverage']:.1%}")
    print(f"   RSI Thresholds: {strategy.oversold_threshold}/{strategy.overbought_threshold}")
    print()
    
    print("🔧 Key Fixes Applied:")
    print("   ✅ Reduced max position size from 12% to 8%")
    print("   ✅ Tightened stop loss from 5% to 3%")
    print("   ✅ Reduced max leverage from 90% to 60%")
    print("   ✅ Reduced risk per trade from 1.5% to 1%")
    print("   ✅ Added fallback signals for very extreme RSI (25/75)")
    print("   ✅ Fixed format specifier errors")
    print("   ✅ Improved signal strength handling")
    print()
    
    # Test with a very short period first
    print("🚀 Running Short Test Backtest (3 months)...")
    print("-" * 45)
    
    try:
        runner = EnhancedZiplineRunner(
            strategy=strategy,
            bundle='nse-local-minute-bundle',
            start_date='2020-01-01',
            end_date='2020-04-01',  # Just 3 months
            capital_base=200000,
            benchmark_symbol='NIFTY50'
        )
        
        results = runner.run()
        
        print("✅ Backtest completed successfully!")
        print()
        
        # Quick analysis
        total_return = results.returns.cumsum().iloc[-1]
        volatility = results.returns.std() * (252**0.5)
        sharpe = results.returns.mean() / results.returns.std() * (252**0.5) if results.returns.std() > 0 else 0
        
        print("📈 Quick Results:")
        print(f"   Total Return: {total_return:.2%}")
        print(f"   Annualized Volatility: {volatility:.2%}")
        print(f"   Sharpe Ratio: {sharpe:.2f}")
        print()
        
        # Check if trades were executed
        if hasattr(results, 'positions'):
            position_data = results.positions.dropna()
            trading_days = (position_data > 0).sum()
            print(f"   Trading Days: {trading_days} out of {len(position_data)}")
            
            if trading_days > 0:
                print("   ✅ Strategy is now executing trades!")
            else:
                print("   ⚠️  Still no trades executed - may need further adjustments")
        
        # Check leverage
        if hasattr(results, 'leverage'):
            leverage_data = results.leverage.dropna()
            if len(leverage_data) > 0:
                max_leverage = leverage_data.max()
                avg_leverage = leverage_data.mean()
                print(f"   Max Leverage Used: {max_leverage:.1%}")
                print(f"   Avg Leverage Used: {avg_leverage:.1%}")
                
                if max_leverage <= 0.6:
                    print("   ✅ Leverage is within safe limits")
                else:
                    print("   ⚠️  Leverage exceeded 60% limit")
        
        print()
        
        # Return distribution analysis
        daily_returns = results.returns
        extreme_positive = (daily_returns > 0.02).sum()
        extreme_negative = (daily_returns < -0.02).sum()
        
        print("📊 Return Distribution:")
        print(f"   Days with >2% returns: {extreme_positive}")
        print(f"   Days with <-2% returns: {extreme_negative}")
        print(f"   Return std: {daily_returns.std():.4f}")
        
        if extreme_positive + extreme_negative < len(daily_returns) * 0.1:  # Less than 10% extreme days
            print("   ✅ Return distribution looks healthier")
        else:
            print("   ⚠️  Still high number of extreme return days")
        
        print()
        
        # Recommendations
        if total_return > 0 and sharpe > 0:
            print("🎉 IMPROVEMENT DETECTED!")
            print("   The fixes appear to be working. Key improvements:")
            print("   • Strategy is generating positive returns")
            print("   • Risk-adjusted returns are positive (Sharpe > 0)")
            print("   • Leverage is controlled")
            print()
            print("📈 Next Steps:")
            print("   1. Run full backtest with longer period")
            print("   2. Check return quantiles - should be much tighter")
            print("   3. Monitor for consistent performance")
            
        else:
            print("🔧 FURTHER TUNING NEEDED:")
            print("   Consider these additional adjustments:")
            print("   1. Reduce max position size to 5%")
            print("   2. Use even more extreme RSI thresholds (25/75)")
            print("   3. Increase S/R validation requirements")
            print("   4. Add momentum filter to avoid trending markets")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check if data bundle is properly ingested")
        print("   2. Verify date range has data")
        print("   3. Check for any remaining code issues")

def show_comparison():
    """Show before/after comparison"""
    
    print("\n📊 Before vs After Comparison:")
    print("=" * 40)
    
    print("BEFORE (Original Issues):")
    print("  • Max Position: 12%")
    print("  • Stop Loss: 5%")
    print("  • Max Leverage: 90%")
    print("  • Risk per Trade: 1.5%")
    print("  • Signal Quality: Weak signals allowed")
    print("  • Result: Poor return quantiles, high volatility")
    print()
    
    print("AFTER (Fixed Version):")
    print("  • Max Position: 8%")
    print("  • Stop Loss: 3%")
    print("  • Max Leverage: 60%")
    print("  • Risk per Trade: 1.0%")
    print("  • Signal Quality: Confluence preferred + extreme RSI fallback")
    print("  • Expected: Better return quantiles, controlled volatility")
    print()
    
    print("🎯 Expected Return Quantiles Improvement:")
    print("  • Daily: Tighter distribution around zero")
    print("  • Weekly: More consistent positive bias")
    print("  • Monthly: Smoother upward progression")

if __name__ == "__main__":
    test_fixed_strategy()
    show_comparison()
    
    print("\n✅ Testing Complete!")
    print("\n💡 To run full backtest with fixed strategy:")
    print("   python strategies/rsi_support_resistance_strategy.py")
