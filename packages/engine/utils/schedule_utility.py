

# Zipline imports
from zipline.api import (
    schedule_function
)

from zipline.utils.events import date_rules, time_rules

from config import (
    SignalType,
    TradingConfig,
)

from typing import Dict, Any, Optional, List, Tuple, Union

from utils.Data_Utilities import DataUtilities

class SchedulingUtilities:
    """Advanced scheduling utilities for different time frames"""
    
    @staticmethod
    def schedule_intraday_function(func, context, times: List[str], 
                                 days_offset: int = 0, 
                                 market_open_offset: int = 0):
        """Schedule function at specific times during the day"""
        for time_str in times:
            hour, minute = map(int, time_str.split(':'))
            schedule_function(
                func,
                date_rules.every_day(),
                time_rules.market_open(hours=hour-9, minutes=minute-15+market_open_offset)
            )
    
    @staticmethod
    def schedule_orb_strategy(establish_orb_func, check_breakout_func, 
                            close_positions_func, context):
        """Schedule ORB strategy specific timings"""
        # Establish ORB at 9:45 AM (30 minutes after market open)
        schedule_function(
            establish_orb_func,
            date_rules.every_day(),
            time_rules.market_open(minutes=30)
        )
        
        # Check breakouts every 15 minutes from 9:45 AM to 3:00 PM
        for minutes_after_open in range(45, 345, 15):
            schedule_function(
                check_breakout_func,
                date_rules.every_day(),
                time_rules.market_open(minutes=minutes_after_open)
            )
        
        # Close positions at 3:10 PM (20 minutes before market close)
        schedule_function(
            close_positions_func,
            date_rules.every_day(),
            time_rules.market_close(minutes=20)
        )


class SignalGenerator:
    """Signal generation utilities"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.data_utils = DataUtilities()
    
    def generate_orb_signals(self, context, data, symbol, orb_high, orb_low):
        """Generate ORB breakout signals"""
        if not data.can_trade(symbol):
            return {}
        
        current_price = data.current(symbol, 'price')
        
        signals = {}
        
        # Long breakout
        if current_price > orb_high:
            signals[symbol] = {
                'signal_type': SignalType.ENTRY_LONG,
                'strength': min((current_price - orb_high) / orb_high, 1.0),
                'entry_price': current_price,
                'stop_loss': orb_low,
                'take_profit': current_price + 2 * (current_price - orb_low)
            }
        
        # Short breakout
        elif current_price < orb_low:
            signals[symbol] = {
                'signal_type': SignalType.ENTRY_SHORT,
                'strength': min((orb_low - current_price) / orb_low, 1.0),
                'entry_price': current_price,
                'stop_loss': orb_high,
                'take_profit': current_price - 2 * (orb_high - current_price)
            }
        
        return signals
    
    def generate_momentum_signals(self, context, data, symbols):
        """Generate momentum-based signals"""
        signals = {}
        
        for symbol in symbols:
            if not data.can_trade(symbol):
                continue
            
            momentum_data = self.data_utils.calculate_momentum_signals(data, symbol)
            
            if momentum_data:
                # Simple momentum strategy
                short_momentum = momentum_data.get('momentum_5d', 0)
                long_momentum = momentum_data.get('momentum_20d', 0)
                
                if short_momentum > 0.02 and long_momentum > 0.05:
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_LONG,
                        'strength': min(short_momentum, 1.0),
                        'entry_price': data.current(symbol, 'price')
                    }
                elif short_momentum < -0.02 and long_momentum < -0.05:
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_SHORT,
                        'strength': min(abs(short_momentum), 1.0),
                        'entry_price': data.current(symbol, 'price')
                    }
        
        return signals
    
    def generate_mean_reversion_signals(self, context, data, symbols):
        """Generate mean reversion signals"""
        signals = {}
        
        for symbol in symbols:
            if not data.can_trade(symbol):
                continue
            
            reversion_data = self.data_utils.calculate_mean_reversion_signals(data, symbol)
            
            if reversion_data:
                z_score = reversion_data.get('z_score', 0)
                
                # Mean reversion signals
                if z_score < -2:  # Oversold
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_LONG,
                        'strength': min(abs(z_score) / 2, 1.0),
                        'entry_price': data.current(symbol, 'price')
                    }
                elif z_score > 2:  # Overbought
                    signals[symbol] = {
                        'signal_type': SignalType.ENTRY_SHORT,
                        'strength': min(abs(z_score) / 2, 1.0),
                        'entry_price': data.current(symbol, 'price')
                    }
        
        return signals