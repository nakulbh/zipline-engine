"""
Strategy Template - Copy and Modify for Your Own Strategy
This template shows how easy it is to create any strategy using the enhanced framework
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, get_datetime, record
from typing import Dict, List, Any

# Import our enhanced framework
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import (
    BaseStrategy, TradingConfig, SignalType, PositionType,
    SchedulingUtilities, DataUtilities, SignalGenerator
)
from engine.enhanced_zipline_runner import EnhancedTradingEngine


class StrategyTemplate(BaseStrategy):
    """
    Strategy Template - Customize this for your own strategy
    
    The framework provides:
    - Risk management (position sizing, stop losses, take profits)
    - Data utilities (technical indicators, momentum, mean reversion)
    - Scheduling utilities (custom time-based execution)
    - Signal generation utilities
    - Performance analysis (pyfolio tearsheets)
    - Factor analysis (alphalens integration)
    - Comprehensive logging and reporting
    """
    
    def __init__(self, config: TradingConfig, **strategy_params):
        super().__init__(config)
        
        # Store strategy-specific parameters
        self.strategy_params = strategy_params
        
        # Initialize any strategy-specific variables
        self.initialize_strategy_variables()
    
    def initialize_strategy_variables(self):
        """Initialize strategy-specific variables"""
        # Add your strategy-specific initialization here
        # Example:
        # self.lookback_period = self.strategy_params.get('lookback_period', 20)
        # self.entry_threshold = self.strategy_params.get('entry_threshold', 0.02)
        # self.exit_threshold = self.strategy_params.get('exit_threshold', 0.01)
        pass
    
    def setup_strategy(self, context):
        """Setup strategy-specific parameters"""
        # Define your trading universe
        context.universe = [
            symbol('BAJFINANCE'),
            symbol('HDFCBANK'),
            symbol('SBIN'),
            symbol('RELIANCE'),
            symbol('TCS')
        ]
        
        # Add any strategy-specific context variables
        # Example:
        # context.position_taken = False
        # context.signal_strength = 0.0
        # context.last_rebalance_date = None
    
    def schedule_functions(self, context):
        """Schedule strategy functions"""
        # Option 1: Use default scheduling (daily rebalancing)
        super().schedule_functions(context)
        
        # Option 2: Custom scheduling
        # Example for intraday strategy:
        # from zipline.api import schedule_function, date_rules, time_rules
        # 
        # # Check signals every 15 minutes
        # for minutes in range(15, 375, 15):  # 9:30 AM to 3:45 PM
        #     schedule_function(
        #         self.check_signals,
        #         date_rules.every_day(),
        #         time_rules.market_open(minutes=minutes)
        #     )
        # 
        # # Close positions at end of day
        # schedule_function(
        #     self.close_positions,
        #     date_rules.every_day(),
        #     time_rules.market_close(minutes=10)
        # )
    
    def define_universe(self, context, data) -> List[str]:
        """Define the trading universe"""
        # Filter for tradeable assets
        universe = [asset for asset in context.universe if data.can_trade(asset)]
        
        # Add any additional filtering logic
        # Example:
        # filtered_universe = []
        # for asset in universe:
        #     # Get technical indicators
        #     indicators = self.data_utilities.calculate_technical_indicators(data, asset)
        #     
        #     # Apply filters (e.g., volume, price, volatility)
        #     if indicators.get('volume', 0) > 1000000:  # Minimum volume
        #         filtered_universe.append(asset)
        # 
        # return filtered_universe
        
        return universe
    
    def generate_signals(self, context, data) -> Dict[str, Dict]:
        """
        Generate trading signals - This is where your strategy logic goes!
        
        Available utilities:
        - self.data_utilities.calculate_technical_indicators(data, symbol)
        - self.data_utilities.calculate_momentum_signals(data, symbol)
        - self.data_utilities.calculate_mean_reversion_signals(data, symbol)
        - self.signal_generator.generate_momentum_signals(context, data, symbols)
        - self.signal_generator.generate_mean_reversion_signals(context, data, symbols)
        """
        
        signals = {}
        
        # Example 1: Simple momentum strategy
        for symbol in context.universe:
            if not data.can_trade(symbol):
                continue
            
            # Get momentum signals using framework utilities
            momentum_data = self.data_utilities.calculate_momentum_signals(data, symbol)
            
            if momentum_data:
                # Example logic: Long if 5-day momentum > 2%
                momentum_5d = momentum_data.get('momentum_5d', 0)
                
                if momentum_5d > 0.02:  # 2% momentum threshold
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_LONG,
                        'strength': min(momentum_5d, 1.0),  # Cap at 100%
                        'entry_price': data.current(symbol, 'price'),
                        'stop_loss': data.current(symbol, 'price') * 0.95,  # 5% stop loss
                        'take_profit': data.current(symbol, 'price') * 1.10  # 10% take profit
                    }
                
                elif momentum_5d < -0.02:  # -2% momentum threshold
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_SHORT,
                        'strength': min(abs(momentum_5d), 1.0),
                        'entry_price': data.current(symbol, 'price'),
                        'stop_loss': data.current(symbol, 'price') * 1.05,  # 5% stop loss
                        'take_profit': data.current(symbol, 'price') * 0.90  # 10% take profit
                    }
        
        # Example 2: Mean reversion strategy
        # for symbol in context.universe:
        #     if not data.can_trade(symbol):
        #         continue
        #     
        #     # Get mean reversion signals
        #     reversion_data = self.data_utilities.calculate_mean_reversion_signals(data, symbol)
        #     
        #     if reversion_data:
        #         z_score = reversion_data.get('z_score', 0)
        #         
        #         if z_score < -2:  # Oversold
        #             signals[symbol] = {
        #                 'signal_type': SignalType.ENTRY_LONG,
        #                 'strength': min(abs(z_score) / 2, 1.0),
        #                 'entry_price': data.current(symbol, 'price')
        #             }
        #         elif z_score > 2:  # Overbought
        #             signals[symbol] = {
        #                 'signal_type': SignalType.ENTRY_SHORT,
        #                 'strength': min(abs(z_score) / 2, 1.0),
        #                 'entry_price': data.current(symbol, 'price')
        #             }
        
        return signals
    
    def before_trading_start(self, context, data):
        """Prepare for new trading day"""
        super().before_trading_start(context, data)
        
        # Add any daily preparation logic
        # Example:
        # current_date = get_datetime().date()
        # if not hasattr(context, 'current_date') or context.current_date != current_date:
        #     context.current_date = current_date
        #     # Reset daily variables
        #     context.position_taken = False
        #     print(f"New trading day: {current_date}")
    
    def handle_data(self, context, data):
        """Handle minute-by-minute data"""
        # The framework already handles position monitoring
        super().handle_data(context, data)
        
        # Add any custom minute-by-minute logic
        # Example:
        # if hasattr(context, 'position_taken') and context.position_taken:
        #     # Custom position management logic
        #     pass
    
    # Additional helper methods can be added here
    def custom_helper_method(self, context, data, symbol):
        """Example of custom helper method"""
        # Add your custom logic here
        # The framework provides access to all utilities
        indicators = self.data_utilities.calculate_technical_indicators(data, symbol)
        return indicators


def run_strategy_template():
    """Run the strategy template"""
    
    # Comprehensive configuration
    config = TradingConfig(
        start_date="2020-01-01",
        end_date="2021-12-31",
        capital_base=100000.0,
        data_frequency="daily",  # Change to "minute" for intraday
        
        # Risk management
        max_position_size=0.20,  # 20% max per position
        stop_loss_pct=0.05,      # 5% stop loss
        take_profit_pct=0.10,    # 10% take profit
        max_drawdown_limit=0.15, # 15% max drawdown
        
        # Position sizing
        position_sizing_method="volatility_target",  # or "equal_weight", "kelly"
        volatility_target=0.15,
        
        # Rebalancing
        rebalance_frequency="daily",  # or "weekly", "monthly"
        
        # Analysis
        generate_tearsheet=True,
        generate_factor_analysis=True,
        save_results=True,
        
        # Output
        output_dir="./backtest_results/strategy_template",
        log_level="INFO"
    )
    
    # Strategy-specific parameters
    strategy_params = {
        'lookback_period': 20,
        'entry_threshold': 0.02,
        'exit_threshold': 0.01,
        # Add your parameters here
    }
    
    # Create strategy and engine
    strategy = StrategyTemplate(config, **strategy_params)
    engine = EnhancedTradingEngine(config)
    
    print("=" * 60)
    print("STRATEGY TEMPLATE BACKTEST")
    print("=" * 60)
    
    try:
        # Run complete analysis workflow
        results = engine.run_complete_analysis(strategy)
        
        print("=" * 60)
        print("✅ Strategy template completed successfully!")
        print(f"📊 Results saved to: {config.output_dir}")
        print("=" * 60)
        
        return engine, results
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    engine, results = run_strategy_template()
    
    if engine and results:
        print("\n🎉 Backtest completed successfully!")
        print(f"📈 Check the results in: {engine.config.output_dir}")
        print("📊 Tearsheets and analysis reports have been generated!")
        print("\n💡 Tips for customizing your strategy:")
        print("1. Modify the generate_signals() method with your logic")
        print("2. Adjust the TradingConfig parameters")
        print("3. Add custom helper methods as needed")
        print("4. Use the framework utilities for technical analysis")
    else:
        print("\n❌ Backtest failed. Check the logs for details.")
