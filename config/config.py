import os
from pathlib import Path

class Config:
    """Configuration settings for the backtesting engine"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RESULTS_DIR = BASE_DIR / "results"
    
    # Zipline settings
    ZIPLINE_ROOT = os.environ.get('ZIPLINE_ROOT', str(Path.home() / '.zipline'))
    
    # NSE specific settings
    NSE_TIMEZONE = 'Asia/Kolkata'
    NSE_MARKET_OPEN = '09:15'
    NSE_MARKET_CLOSE = '15:30'
    
    # Data settings
    DEFAULT_BUNDLE = 'nse-bundle'
    SUPPORTED_TIMEFRAMES = ['1min', '5min', '15min', '1H', '1D']
    
    # Performance settings
    BENCHMARK_SYMBOL = 'NIFTY50'  # Default benchmark
    RISK_FREE_RATE = 0.06  # 6% annual risk-free rate
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
