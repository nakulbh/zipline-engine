# simple_test.py
import sys
import os

# Add the parent directory to Python path so we can import from engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.zipline_runner import TradingEngine
from engine.base_strategy import TradingConfig
import pandas as pd
from zipline.api import order_target_percent, symbol, record

class SimpleTestStrategy:
    """A very simple strategy without pipelines"""
    
    def __init__(self, config):
        self.config = config
        
    def initialize(self, context):
        """Initialize the strategy"""
        # Set some stocks to trade
        context.stocks = [symbol('AAPL'), symbol('MSFT'), symbol('GOOGL')]
        context.rebalance_days = 0
        
    def before_trading_start(self, context, data):
        """Called before trading starts each day"""
        pass
        
    def handle_data(self, context, data):
        """Called every minute/day"""
        # Rebalance every 30 days
        context.rebalance_days += 1
        
        if context.rebalance_days % 30 == 0:
            # Simple equal weight strategy
            weight = 1.0 / len(context.stocks)
            
            for stock in context.stocks:
                if data.can_trade(stock):
                    order_target_percent(stock, weight)
            
            record(leverage=context.account.leverage)

def run_simple_test():
    """Run a simple test backtest"""
    
    # 1. Create configuration
    config = TradingConfig(
        start_date="2020-01-01",
        end_date="2020-12-31",  # Shorter period for testing
        capital_base=100000.0,
        commission_cost=0.001,
        output_dir="./backtest_results"
    )
    
    # 2. Create strategy
    strategy = SimpleTestStrategy(config)
    
    # 3. Create trading engine
    engine = TradingEngine(config)
    
    # 4. Run backtest
    print("Starting simple backtest...")
    try:
        backtest_results = engine.run_backtest(strategy)
        print("Backtest completed successfully!")
        print(f"Final portfolio value: ${backtest_results['results'].portfolio_value.iloc[-1]:,.2f}")
        print(f"Total return: {backtest_results['results'].returns.sum():.2%}")
        
        return True
        
    except Exception as e:
        print(f"Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_simple_test()
    print(f"Test {'PASSED' if success else 'FAILED'}")
