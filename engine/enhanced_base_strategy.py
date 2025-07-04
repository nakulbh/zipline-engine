"""
Enhanced Base Strategy Framework for Zipline-Reloaded
This framework provides comprehensive utilities for strategy development with:
- Integrated risk management utilities
- Position sizing and portfolio management
- Performance analysis with pyfolio-reloaded
- Factor analysis with alphalens-reloaded
- Comprehensive scheduling and timing utilities
- Advanced data handling and signal processing
"""

import os
import pandas as pd
import numpy as np
import pyfolio as pf
import alphalens as al
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta, time
import logging
from dataclasses import dataclass, field
from enum import Enum

# Zipline imports
from zipline.api import (
    order_target_percent, record, symbol, get_datetime,
    schedule_function, date_rules, time_rules, get_open_orders,
    cancel_order, order, order_target, get_order, 
    set_commission, set_slippage, attach_pipeline, pipeline_output
)
from zipline.finance import commission, slippage
from zipline.pipeline import Pipeline, CustomFactor
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import (
    SimpleMovingAverage, RSI, Returns, AverageDollarVolume,
    BollingerBands, EWMA, VWAP, AnnualizedVolatility
)
from zipline.utils.events import date_rules, time_rules

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


warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class BaseStrategy(ABC):
    """
    Enhanced abstract base strategy class with comprehensive utilities
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.context = None
        self.risk_manager = RiskManager(config)
        self.data_utilities = DataUtilities()
        self.scheduling_utilities = SchedulingUtilities()
        self.signal_generator = SignalGenerator(config)
        
        # Strategy state
        self.positions = {}
        self.daily_pnl = []
        self.trade_log = []
        self.performance_metrics = {}
        
        # Setup logging
        logging.getLogger().setLevel(getattr(logging, config.log_level))
        
    @abstractmethod
    def define_universe(self, context, data) -> List[str]:
        """Define the trading universe - must be implemented by each strategy"""
        pass
    
    @abstractmethod
    def generate_signals(self, context, data) -> Dict[str, Dict]:
        """Generate trading signals - must be implemented by each strategy"""
        pass
    
    def initialize(self, context):
        """Initialize strategy with enhanced setup"""
        self.context = context
        
        # Set commission and slippage
        set_commission(commission.PerTrade(cost=self.config.commission_cost))
        set_slippage(slippage.FixedSlippage(spread=self.config.slippage_spread))
        
        # Initialize strategy-specific setup
        self.setup_strategy(context)
        
        # Schedule main strategy functions
        self.schedule_functions(context)
        
        # Initialize risk management
        self.risk_manager.risk_metrics.peak_value = self.config.capital_base
        
        logger.info(f"Strategy initialized with capital: ${self.config.capital_base:,.2f}")
    
    def setup_strategy(self, context):
        """Strategy-specific setup - can be overridden"""
        pass
    
    def schedule_functions(self, context):
        """Schedule strategy functions - can be overridden"""
        # Default scheduling
        schedule_function(
            self.rebalance,
            date_rules.every_day(),
            time_rules.market_open(minutes=self.config.rebalance_offset_minutes)
        )
        
        schedule_function(
            self.record_metrics,
            date_rules.every_day(),
            time_rules.market_close()
        )
    
    def before_trading_start(self, context, data):
        """Prepare for trading day"""
        # Reset daily variables if needed
        current_date = get_datetime().date()
        
        # Update universe
        context.universe = self.define_universe(context, data)
        
        # Check risk limits
        if not self.risk_manager.check_risk_limits(context, data):
            logger.warning("Risk limits exceeded - limiting new positions")
            context.risk_limit_exceeded = True
        else:
            context.risk_limit_exceeded = False
    
    def rebalance(self, context, data):
        """Main rebalancing logic"""
        if context.risk_limit_exceeded:
            logger.warning("Skipping rebalance due to risk limits")
            return
        
        # Cancel existing orders
        for order_id in get_open_orders():
            cancel_order(order_id)
        
        # Generate signals
        signals = self.generate_signals(context, data)
        
        # Execute trades
        self.execute_trades(context, data, signals)
        
        # Log performance
        if self.config.log_performance:
            self.log_performance(context, data)
    
    def execute_trades(self, context, data, signals: Dict[str, Dict]):
        """Execute trades based on signals"""
        for symbol, signal_info in signals.items():
            if not data.can_trade(symbol):
                continue
            
            signal_type = signal_info['signal_type']
            strength = signal_info.get('strength', 1.0)
            
            # Calculate position size
            volatility = self.data_utilities.calculate_technical_indicators(
                data, symbol
            ).get('volatility', 0.2)
            
            position_size = self.risk_manager.calculate_position_size(
                strength, volatility, signal_info['entry_price'], 
                context.portfolio.portfolio_value
            )
            
            # Execute order based on signal type
            if signal_type == SignalType.ENTRY_LONG:
                order_target_percent(symbol, position_size)
                
            elif signal_type == SignalType.ENTRY_SHORT:
                order_target_percent(symbol, -position_size)
                
            elif signal_type in [SignalType.EXIT_LONG, SignalType.EXIT_SHORT]:
                order_target_percent(symbol, 0)
            
            # Log trade
            if self.config.log_trades:
                self.log_trade(symbol, signal_type, position_size, signal_info)
    
    def handle_data(self, context, data):
        """Handle minute-by-minute data - can be overridden"""
        # Monitor existing positions for stop losses and take profits
        self.monitor_positions(context, data)
    
    def monitor_positions(self, context, data):
        """Monitor positions for risk management"""
        for symbol, position in context.portfolio.positions.items():
            if position.amount == 0:
                continue
            
            current_price = data.current(symbol, 'price')
            
            # Check if we have position info
            if symbol in self.positions:
                pos_info = self.positions[symbol]
                
                # Check stop loss
                if pos_info.stop_loss:
                    if ((pos_info.position_type == PositionType.LONG and current_price <= pos_info.stop_loss) or
                        (pos_info.position_type == PositionType.SHORT and current_price >= pos_info.stop_loss)):
                        order_target_percent(symbol, 0)
                        logger.info(f"Stop loss triggered for {symbol} at {current_price}")
                
                # Check take profit
                if pos_info.take_profit:
                    if ((pos_info.position_type == PositionType.LONG and current_price >= pos_info.take_profit) or
                        (pos_info.position_type == PositionType.SHORT and current_price <= pos_info.take_profit)):
                        order_target_percent(symbol, 0)
                        logger.info(f"Take profit triggered for {symbol} at {current_price}")
    
    def record_metrics(self, context, data):
        """Record daily performance metrics"""
        portfolio_value = context.portfolio.portfolio_value
        
        record(
            portfolio_value=portfolio_value,
            leverage=context.account.leverage,
            positions=len(context.portfolio.positions),
            cash=context.portfolio.cash,
            returns=context.portfolio.returns,
            drawdown=self.risk_manager.risk_metrics.current_drawdown,
            max_drawdown=self.risk_manager.risk_metrics.max_drawdown
        )
    
    def log_trade(self, symbol, signal_type, position_size, signal_info):
        """Log trade information"""
        trade_info = {
            'timestamp': get_datetime(),
            'symbol': symbol,
            'signal_type': signal_type.value,
            'position_size': position_size,
            'entry_price': signal_info.get('entry_price'),
            'stop_loss': signal_info.get('stop_loss'),
            'take_profit': signal_info.get('take_profit')
        }
        
        self.trade_log.append(trade_info)
        
        if self.config.log_trades:
            logger.info(f"Trade: {symbol} {signal_type.value} size={position_size:.3f} price={signal_info.get('entry_price', 'N/A')}")
    
    def log_performance(self, context, data):
        """Log performance information"""
        portfolio_value = context.portfolio.portfolio_value
        daily_return = context.portfolio.returns
        
        if self.config.log_performance:
            logger.info(f"Portfolio: ${portfolio_value:,.2f} | Daily Return: {daily_return:.2%} | "
                       f"Positions: {len(context.portfolio.positions)} | "
                       f"Leverage: {context.account.leverage:.2f}")
