#!/usr/bin/env python3
"""
NSE Backtesting Engine Web Interface Demo
=========================================

This script demonstrates how to use the web interface programmatically
and provides examples of creating strategies and running backtests.

Usage:
    python demo_web_interface.py
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_demo_strategy():
    """Create a demo strategy for testing"""
    
    demo_strategy_code = '''#!/usr/bin/env python3
"""
Demo Momentum Strategy
Created for Web Interface Demo
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, order_target_percent, record
from engine.enhanced_base_strategy import BaseStrategy

class DemoMomentumStrategy(BaseStrategy):
    def __init__(self, lookback_period=20, momentum_threshold=0.02):
        super().__init__()
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        
        # Configure risk parameters
        self.risk_params.update({
            'max_position_size': 0.20,  # 20% max per position
            'stop_loss_pct': 0.10,      # 10% stop loss
            'take_profit_pct': 0.25,    # 25% take profit
        })
        
        print(f"🚀 Demo Momentum Strategy initialized")
        print(f"   📊 Lookback Period: {lookback_period} days")
        print(f"   📈 Momentum Threshold: {momentum_threshold:.1%}")
    
    def select_universe(self, context):
        """Select NSE assets for trading"""
        return [
            symbol('SBIN'),      # State Bank of India
            symbol('RELIANCE'),  # Reliance Industries
            symbol('HDFCBANK'),  # HDFC Bank
            symbol('BAJFINANCE') # Bajaj Finance
        ]
    
    def generate_signals(self, context, data):
        """Generate momentum-based trading signals"""
        signals = {}
        
        for asset in context.universe:
            try:
                # Get historical prices
                prices = data.history(asset, 'price', self.lookback_period + 5, '1d')
                
                if len(prices) >= self.lookback_period:
                    # Calculate momentum
                    current_price = prices.iloc[-1]
                    past_price = prices.iloc[-self.lookback_period]
                    momentum = (current_price / past_price) - 1
                    
                    # Generate signals based on momentum
                    if momentum > self.momentum_threshold:
                        signals[asset] = 1.0  # Strong positive momentum - Buy
                    elif momentum < -self.momentum_threshold:
                        signals[asset] = -1.0  # Strong negative momentum - Sell
                    else:
                        signals[asset] = 0.0  # Weak momentum - Hold
                        
                    # Record momentum for analysis
                    record(**{f'{asset.symbol}_momentum': momentum})
                    
                else:
                    signals[asset] = 0.0  # Insufficient data
                    
            except Exception as e:
                print(f"Error processing {asset}: {e}")
                signals[asset] = 0.0
        
        return signals

# Example usage and testing
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    
    print("🎯 Demo Momentum Strategy Backtest")
    print("=" * 50)
    
    # Create strategy instance
    strategy = DemoMomentumStrategy(
        lookback_period=15,
        momentum_threshold=0.03
    )
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    # Run backtest
    try:
        print("🔄 Running backtest...")
        results = runner.run()
        
        if results is not None:
            print("✅ Backtest completed successfully!")
            
            # Display basic results
            final_value = results.portfolio_value.iloc[-1]
            initial_value = results.portfolio_value.iloc[0]
            total_return = (final_value / initial_value - 1) * 100
            
            print(f"📈 Final Portfolio Value: ₹{final_value:,.2f}")
            print(f"📊 Total Return: {total_return:.2f}%")
            
            # Save results
            results_dir = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            runner.analyze(f'backtest_results/{results_dir}')
            
            print(f"📁 Results saved to: backtest_results/{results_dir}")
            
        else:
            print("❌ Backtest failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
'''
    
    # Save the demo strategy
    strategies_dir = "strategies"
    if not os.path.exists(strategies_dir):
        os.makedirs(strategies_dir)
    
    demo_file = os.path.join(strategies_dir, "demo_momentum_strategy.py")
    
    with open(demo_file, 'w') as f:
        f.write(demo_strategy_code)
    
    print(f"✅ Demo strategy created: {demo_file}")
    return demo_file

def show_web_interface_guide():
    """Show guide for using the web interface"""
    
    print("\n🌐 NSE Backtesting Engine Web Interface Guide")
    print("=" * 60)
    
    print("\n📋 Step-by-Step Usage:")
    print("1. 🚀 Launch the web interface:")
    print("   python launch_web_interface.py")
    print("   OR")
    print("   streamlit run web_interface.py")
    
    print("\n2. 📝 Create or Edit Strategies:")
    print("   - Go to 'Strategy Builder' page")
    print("   - Choose a template or start from scratch")
    print("   - Write your strategy code")
    print("   - Validate and save your strategy")
    
    print("\n3. ⚙️ Run Backtests:")
    print("   - Go to 'Backtest Runner' page")
    print("   - Select your strategy")
    print("   - Configure parameters (dates, capital, etc.)")
    print("   - Click 'Run Backtest'")
    
    print("\n4. 📊 View Results:")
    print("   - Go to 'Results Viewer' page")
    print("   - View latest results or load saved ones")
    print("   - Analyze performance metrics and charts")
    
    print("\n5. 📋 Manage Strategies:")
    print("   - Go to 'Strategy Manager' page")
    print("   - View, edit, or delete strategies")
    print("   - Organize your strategy files")
    
    print("\n🎯 Available Features:")
    print("- ✅ Interactive code editor with syntax highlighting")
    print("- ✅ Real-time strategy validation")
    print("- ✅ Progress tracking during backtests")
    print("- ✅ Interactive performance charts")
    print("- ✅ Comprehensive performance metrics")
    print("- ✅ Export results to multiple formats")
    print("- ✅ Strategy templates and examples")
    
    print("\n📈 Available Assets:")
    assets = ['BAJFINANCE', 'BANKNIFTY', 'HDFCBANK', 'HDFC', 
              'HINDALCO', 'NIFTY50', 'RELIANCE', 'SBIN']
    print(f"   {', '.join(assets)}")
    
    print("\n🔧 Tips for Best Results:")
    print("- Start with simple strategies and gradually add complexity")
    print("- Always validate your strategy code before running")
    print("- Test with different date ranges and parameters")
    print("- Compare your strategy against benchmarks")
    print("- Save your strategies and results regularly")
    
    print("\n📞 Troubleshooting:")
    print("- Check error messages in the web interface")
    print("- Ensure all dependencies are installed")
    print("- Verify your NSE data bundle is properly configured")
    print("- Review strategy code for proper BaseStrategy inheritance")

def main():
    """Main demo function"""
    
    print("🎯 NSE Backtesting Engine Web Interface Demo")
    print("=" * 50)
    
    # Create demo strategy
    print("\n📝 Creating demo strategy...")
    demo_file = create_demo_strategy()
    
    # Show usage guide
    show_web_interface_guide()
    
    print("\n🚀 Ready to Launch!")
    print("=" * 30)
    print("Run one of these commands to start the web interface:")
    print("  python launch_web_interface.py")
    print("  streamlit run web_interface.py")
    
    print(f"\n💡 Demo strategy available: {demo_file}")
    print("   You can use this strategy in the web interface!")
    
    # Ask if user wants to launch immediately
    try:
        response = input("\n❓ Launch web interface now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🚀 Launching web interface...")
            os.system("python launch_web_interface.py")
    except KeyboardInterrupt:
        print("\n👋 Demo completed!")

if __name__ == "__main__":
    main()
