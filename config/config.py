import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import pandas as pd

class TimeFrame(Enum):
    """Time frame enumeration for strategy execution"""
    MINUTE = "1m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    THIRTY_MINUTE = "30m"
    HOURLY = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"


class PositionType(Enum):
    """Position type enumeration"""
    LONG = 1
    SHORT = -1
    FLAT = 0


class SignalType(Enum):
    """Signal type enumeration"""
    ENTRY_LONG = "entry_long"
    ENTRY_SHORT = "entry_short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"
    REBALANCE = "rebalance"


@dataclass
class TradingConfig:
    """Enhanced configuration class for trading engine"""
    # Basic configuration
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    capital_base: float = 100000.0
    benchmark_symbol: str = Optional[str]
    data_frequency: str = "minute"  # minute or daily
    
    # Risk management
    max_position_size: float = 0.20  # 20% max per position
    max_total_exposure: float = 1.0  # 100% total exposure
    max_leverage: float = 1.0  # No leverage by default
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.06  # 6% take profit
    max_drawdown_limit: float = 0.10  # 10% max drawdown
    
    # Position sizing
    position_sizing_method: str = "equal_weight"  # equal_weight, volatility_target, kelly
    volatility_target: float = 0.15  # 15% annualized volatility target
    lookback_period: int = 252  # Days for volatility calculation
    
    # Trading costs
    commission_cost: float = 0.001  # 0.1% per trade
    slippage_spread: float = 0.001  # 0.1% slippage
    
    # Universe selection
    universe_size: int = 500
    min_volume: float = 1e6
    min_price: float = 5.0
    max_price: float = 1000.0
    
    # Rebalancing
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    rebalance_time: str = "market_open"  # market_open, market_close, custom
    rebalance_offset_minutes: int = 30  # Minutes after market open/before close
    
    # Analysis and reporting
    benchmark_returns: Optional[pd.Series] = None
    output_dir: str = "./results"
    save_results: bool = True
    save_intermediate_data: bool = True
    generate_tearsheet: bool = True
    generate_factor_analysis: bool = True
    
    # Trading records
    save_trading_records: bool = True
    save_orderbook: bool = True
    save_tradebook: bool = True  
    save_ledger: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_trades: bool = True
    log_performance: bool = True


@dataclass
class RiskMetrics:
    """Risk metrics tracking"""
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    peak_value: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional Value at Risk 95%


@dataclass
class PositionInfo:
    """Position information tracking"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    entry_time: datetime
    position_type: PositionType
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0