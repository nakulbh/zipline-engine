"""
NSE Backtesting Engine using Zipline-Reloaded and PyFolio-Reloaded

A comprehensive backtesting framework for Indian (NSE) equity markets
with support for multiple timeframes and professional performance analysis.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .engine.backtest_engine import BacktestEngine
from .engine.strategy_base import StrategyBase
from .data.bundle_manager import BundleManager
from .engine.performance_analyzer import PerformanceAnalyzer

__all__ = [
    'BacktestEngine',
    'StrategyBase', 
    'BundleManager',
    'PerformanceAnalyzer'
]