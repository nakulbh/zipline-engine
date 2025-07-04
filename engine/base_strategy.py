import os
import pandas as pd
import numpy as np
import pyfolio as pf
import alphalens as al
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

# Zipline imports
from zipline import run_algorithm
from zipline.api import (
    order_target_percent, record, symbol, get_datetime,
    schedule_function, date_rules, time_rules, get_open_orders,
    cancel_order, order, order_target, get_order
)
from zipline.finance import commission, slippage
from zipline.pipeline import Pipeline, CustomFactor
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import (
    SimpleMovingAverage, RSI, Returns, AverageDollarVolume
)
from zipline.utils.events import date_rules, time_rules

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TradingConfig:
    """Configuration class for trading engine"""
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    capital_base: float = 100000.0
    benchmark_symbol: str = "SPY"
    data_frequency: str = "daily"
    commission_cost: float = 0.001  # 0.1% per trade
    slippage_spread: float = 0.001  # 0.1% slippage
    max_position_size: float = 0.05  # 5% max per position
    rebalance_frequency: str = "monthly"  # daily, weekly, monthly
    universe_size: int = 500  # Number of stocks in universe
    min_volume: float = 1e6  # Minimum daily volume
    log_level: str = "INFO"
    output_dir: str = "./results"
    save_results: bool = True


class BaseStrategy(ABC):
    """
    Abstract base strategy class that all trading strategies should inherit from.
    Provides standard interface and common functionality.
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.context = None
        self.pipeline_columns = {}
        self.rebalance_count = 0
        
    @abstractmethod
    def create_pipeline(self) -> Pipeline:
        """
        Create and return the pipeline for data preprocessing.
        Must be implemented by each strategy.
        """
        pass
    
    @abstractmethod
    def select_universe(self, context, data) -> List[str]:
        """
        Select trading universe based on current market conditions.
        Must be implemented by each strategy.
        """
        pass
    
    @abstractmethod
    def generate_signals(self, context, data) -> Dict[str, float]:
        """
        Generate trading signals for selected universe.
        Returns dict with symbol: weight pairs.
        Must be implemented by each strategy.
        """
        pass
    
    def initialize(self, context):
        """Initialize strategy parameters and schedule functions"""
        self.context = context
        
        # Set commission and slippage
        context.set_commission(commission.PerTrade(cost=self.config.commission_cost))
        context.set_slippage(slippage.FixedSlippage(spread=self.config.slippage_spread))
        
        # Create and attach pipeline
        pipe = self.create_pipeline()
        context.attach_pipeline(pipe, 'main_pipeline')
        
        # Schedule rebalancing
        if self.config.rebalance_frequency == "daily":
            schedule_function(
                self.rebalance,
                date_rules.every_day(),
                time_rules.market_open(minutes=30)
            )
        elif self.config.rebalance_frequency == "weekly":
            schedule_function(
                self.rebalance,
                date_rules.week_start(),
                time_rules.market_open(minutes=30)
            )
        else:  # monthly
            schedule_function(
                self.rebalance,
                date_rules.month_start(),
                time_rules.market_open(minutes=30)
            )
        
        # Schedule daily recording
        schedule_function(
            self.record_positions,
            date_rules.every_day(),
            time_rules.market_close()
        )
        
        logger.info(f"Strategy initialized with {self.config.rebalance_frequency} rebalancing")
    
    def before_trading_start(self, context, data):
        """Run before market opens each day"""
        context.pipeline_data = context.pipeline_output('main_pipeline')
        
        # Filter for tradeable assets
        context.tradeable_assets = [
            asset for asset in context.pipeline_data.index
            if data.can_trade(asset)
        ]
        
        logger.debug(f"Found {len(context.tradeable_assets)} tradeable assets")
    
    def rebalance(self, context, data):
        """Main rebalancing function"""
        try:
            self.rebalance_count += 1
            
            # Cancel all open orders
            for order_id in get_open_orders():
                cancel_order(order_id)
            
            # Get universe and signals
            universe = self.select_universe(context, data)
            signals = self.generate_signals(context, data)
            
            # Apply risk management
            signals = self.apply_risk_management(signals)
            
            # Execute trades
            self.execute_trades(context, data, signals)
            
            # Record metrics
            record(
                rebalance_count=self.rebalance_count,
                universe_size=len(universe),
                positions=len(context.portfolio.positions),
                leverage=context.account.leverage
            )
            
            logger.info(f"Rebalancing #{self.rebalance_count}: {len(signals)} positions")
            
        except Exception as e:
            logger.error(f"Error in rebalancing: {str(e)}")
    
    def apply_risk_management(self, signals: Dict[str, float]) -> Dict[str, float]:
        """Apply risk management rules to signals"""
        # Limit individual position sizes
        for symbol in signals:
            signals[symbol] = np.clip(
                signals[symbol], 
                -self.config.max_position_size, 
                self.config.max_position_size
            )
        
        # Normalize weights if they exceed 100%
        total_weight = sum(abs(w) for w in signals.values())
        if total_weight > 1.0:
            signals = {k: v/total_weight for k, v in signals.items()}
        
        return signals
    
    def execute_trades(self, context, data, signals: Dict[str, float]):
        """Execute trades based on signals"""
        for asset, weight in signals.items():
            if data.can_trade(asset):
                order_target_percent(asset, weight)
    
    def record_positions(self, context, data):
        """Record daily position metrics"""
        positions = context.portfolio.positions
        
        record(
            num_positions=len(positions),
            gross_leverage=context.account.leverage,
            net_leverage=context.account.net_leverage,
            cash=context.portfolio.cash,
            portfolio_value=context.portfolio.portfolio_value,
        )


class MomentumStrategy(BaseStrategy):
    """
    Example momentum strategy implementation
    Buys stocks with highest momentum, shorts stocks with lowest momentum
    """
    
    def __init__(self, config: TradingConfig, 
                 momentum_window: int = 20, 
                 top_n: int = 50, 
                 bottom_n: int = 50):
        super().__init__(config)
        self.momentum_window = momentum_window
        self.top_n = top_n
        self.bottom_n = bottom_n
    
    def create_pipeline(self) -> Pipeline:
        """Create pipeline with momentum and volume filters"""
        # Price momentum
        momentum = Returns(window_length=self.momentum_window)
        
        # Volume filter
        dollar_volume = AverageDollarVolume(window_length=30)
        
        # Create pipeline
        pipe = Pipeline(
            columns={
                'momentum': momentum,
                'dollar_volume': dollar_volume,
            },
            screen=(
                dollar_volume.top(self.config.universe_size) &
                momentum.notnull()
            )
        )
        
        return pipe
    
    def select_universe(self, context, data) -> List[str]:
        """Select universe from pipeline output"""
        return list(context.pipeline_data.index)
    
    def generate_signals(self, context, data) -> Dict[str, float]:
        """Generate momentum-based signals"""
        pipeline_data = context.pipeline_data
        
        # Sort by momentum
        sorted_by_momentum = pipeline_data.sort_values('momentum', ascending=False)
        
        # Select top and bottom stocks
        longs = sorted_by_momentum.head(self.top_n).index
        shorts = sorted_by_momentum.tail(self.bottom_n).index
        
        # Create signals dictionary
        signals = {}
        
        # Long positions
        for asset in longs:
            if data.can_trade(asset):
                signals[asset] = self.config.max_position_size
        
        # Short positions
        for asset in shorts:
            if data.can_trade(asset):
                signals[asset] = -self.config.max_position_size
        
        return signals