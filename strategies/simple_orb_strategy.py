"""
Simplified ORB Strategy using Enhanced Framework
This demonstrates how the enhanced framework makes strategy writing much simpler
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, get_datetime, record
from typing import Dict, List

# Import our enhanced framework
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import (
    BaseStrategy, TradingConfig
)
from engine.enhanced_zipline_runner import EnhancedTradingEngine

from config import (
    TimeFrame,
    PositionType,
    SignalType,
    TradingConfig,
    RiskMetrics,
    PositionInfo,
)

from utils.Data_Utilities import (
    DataUtilities,
)
from utils.risk_manager import RiskManager
from utils.schedule_utility import (
    SchedulingUtilities,
    SignalGenerator
)


class SimpleORBStrategy(BaseStrategy):
    """
    Simplified ORB Strategy using the enhanced framework
    Notice how much cleaner and focused this is on the actual strategy logic!
    """
    
    def __init__(self, config: TradingConfig, orb_minutes: int = 30):
        super().__init__(config)
        self.orb_minutes = orb_minutes
        self.orb_data = {}  # Store ORB data for each symbol
    
    def setup_strategy(self, context):
        """Setup ORB-specific parameters"""
        # Define our universe - framework handles the rest
        context.universe = [symbol('BAJFINANCE'), symbol('HDFCBANK'), symbol('SBIN')]
        context.primary_symbol = symbol('NIFTY50')
        
        # ORB-specific variables
        context.orb_established = False
        context.orb_high = None
        context.orb_low = None
        
        # Initialize ORB data storage
        for sym in context.universe:
            self.orb_data[sym] = {
                'high': None,
                'low': None,
                'established': False,
                'breakout_taken': False
            }
    
    def schedule_functions(self, context):
        """Schedule ORB-specific functions using the enhanced scheduling utilities"""
        # Use the enhanced scheduling utilities for ORB strategy
        self.scheduling_utilities.schedule_orb_strategy(
            self.establish_orb,
            self.check_breakout,
            self.close_all_positions,
            context
        )
        
        # Schedule daily recording
        from zipline.api import schedule_function, date_rules, time_rules
        schedule_function(
            self.record_metrics,
            date_rules.every_day(),
            time_rules.market_close()
        )
    
    def define_universe(self, context, data) -> List[str]:
        """Define the trading universe"""
        return [asset for asset in context.universe if data.can_trade(asset)]
    
    def establish_orb(self, context, data):
        """Establish ORB levels - much simpler now!"""
        for symbol in context.universe:
            if not data.can_trade(symbol):
                continue
            
            try:
                # Get ORB data using framework utilities
                bars = data.history(symbol, ['high', 'low'], self.orb_minutes, '1m')
                
                if len(bars) >= self.orb_minutes:
                    orb_high = bars['high'].max()
                    orb_low = bars['low'].min()
                    
                    # Store ORB data
                    self.orb_data[symbol]['high'] = orb_high
                    self.orb_data[symbol]['low'] = orb_low
                    self.orb_data[symbol]['established'] = True
                    self.orb_data[symbol]['breakout_taken'] = False
                    
                    print(f"ORB established for {symbol.symbol}: H={orb_high:.2f}, L={orb_low:.2f}")
                    
                    # Record ORB data
                    record(**{
                        f'{symbol.symbol}_orb_high': orb_high,
                        f'{symbol.symbol}_orb_low': orb_low,
                        f'{symbol.symbol}_orb_range': orb_high - orb_low
                    })
                    
            except Exception as e:
                print(f"Error establishing ORB for {symbol.symbol}: {e}")
    
    def check_breakout(self, context, data):
        """Check for breakout signals - framework handles position sizing and risk management"""
        for symbol in context.universe:
            if not data.can_trade(symbol):
                continue
            
            orb_info = self.orb_data[symbol]
            
            if not orb_info['established'] or orb_info['breakout_taken']:
                continue
            
            # Generate signals using the enhanced signal generator
            signals = self.signal_generator.generate_orb_signals(
                context, data, symbol, orb_info['high'], orb_info['low']
            )
            
            # Execute signals - framework handles everything!
            if signals:
                self.execute_trades(context, data, signals)
                orb_info['breakout_taken'] = True
                print(f"Breakout signal generated for {symbol.symbol}")
    
    def close_all_positions(self, context, data):
        """Close all positions at end of day"""
        from zipline.api import order_target_percent
        
        for symbol in context.portfolio.positions:
            if context.portfolio.positions[symbol].amount != 0:
                order_target_percent(symbol, 0)
                print(f"Closing position in {symbol.symbol}")
        
        # Reset ORB data for next day
        for sym in self.orb_data:
            self.orb_data[sym] = {
                'high': None,
                'low': None,
                'established': False,
                'breakout_taken': False
            }
    
    def generate_signals(self, context, data) -> Dict[str, Dict]:
        """Generate trading signals - called by framework"""
        # For ORB strategy, signals are generated in check_breakout
        # This method is required by base class but not used in this implementation
        return {}
    
    def before_trading_start(self, context, data):
        """Prepare for new trading day"""
        super().before_trading_start(context, data)
        
        # Reset daily ORB data
        current_date = get_datetime().date()
        if not hasattr(context, 'current_date') or context.current_date != current_date:
            context.current_date = current_date
            context.orb_established = False
            
            # Reset ORB data for all symbols
            for sym in self.orb_data:
                self.orb_data[sym] = {
                    'high': None,
                    'low': None,
                    'established': False,
                    'breakout_taken': False
                }
            
            print(f"New trading day: {current_date}")


def run_simple_orb_strategy():
    """Run the simplified ORB strategy"""
    
    # Configuration is now much more comprehensive
    config = TradingConfig(
        start_date="2018-01-01",
        end_date="2021-02-28",
        capital_base=100000.0,
        data_frequency="minute",
        
        # Enhanced risk management
        max_position_size=0.30,  # 30% max per position
        stop_loss_pct=0.02,      # 2% stop loss
        take_profit_pct=0.06,    # 6% take profit
        
        # Position sizing
        position_sizing_method="volatility_target",
        volatility_target=0.15,
        
        # Enhanced analysis
        generate_tearsheet=True,
        generate_factor_analysis=True,
        save_results=True,
        
        # Output
        output_dir="./backtest_results/enhanced_orb",
        log_level="INFO"
    )
    
    # Create strategy and engine
    strategy = SimpleORBStrategy(config, orb_minutes=30)
    engine = EnhancedTradingEngine(config)
    
    print("=" * 60)
    print("ENHANCED ORB STRATEGY BACKTEST")
    print("=" * 60)
    
    try:
        # Run complete analysis workflow
        results = engine.run_complete_analysis(strategy)
        
        print("=" * 60)
        print("✅ Enhanced ORB strategy completed successfully!")
        print(f"📊 Results saved to: {config.output_dir}")
        print("=" * 60)
        
        return engine, results
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    engine, results = run_simple_orb_strategy()
    
    if engine and results:
        print("\n🎉 Backtest completed successfully!")
        print(f"📈 Check the results in: {engine.config.output_dir}")
        print("📊 Tearsheets and analysis reports have been generated!")
    else:
        print("\n❌ Backtest failed. Check the logs for details.")
