#!/usr/bin/env python3
"""
Web Interface Configuration
===========================

Configuration settings for the NSE Backtesting Engine Web Interface.
Customize these settings to match your preferences and setup.
"""

import os
from datetime import date, datetime

# =============================================================================
# WEB INTERFACE SETTINGS
# =============================================================================

# Page configuration
PAGE_CONFIG = {
    'page_title': 'NSE Backtesting Engine',
    'page_icon': '📈',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Theme colors
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#2e8b57',
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545',
    'info': '#17a2b8'
}

# =============================================================================
# DATA CONFIGURATION
# =============================================================================

# Available NSE assets in your bundle
NSE_ASSETS = [
    'BAJFINANCE',   # Bajaj Finance
    'BANKNIFTY',    # Bank Nifty Index
    'HDFCBANK',     # HDFC Bank
    'HDFC',         # HDFC Ltd
    'HINDALCO',     # Hindalco Industries
    'NIFTY50',      # Nifty 50 Index
    'RELIANCE',     # Reliance Industries
    'SBIN'          # State Bank of India
]

# Available data bundles
AVAILABLE_BUNDLES = {
    'nse-local-minute-bundle': 'NSE Local Minute Data Bundle'
}

# Default benchmark options
BENCHMARK_OPTIONS = ['NIFTY50', 'BANKNIFTY', 'SBIN', 'RELIANCE', 'HDFCBANK']

# =============================================================================
# BACKTEST CONFIGURATION
# =============================================================================

# Default backtest parameters
DEFAULT_BACKTEST_CONFIG = {
    'start_date': date(2020, 1, 1),
    'end_date': date(2021, 12, 31),
    'capital_base': 100000,
    'benchmark_symbol': 'NIFTY50',
    'bundle': 'nse-local-minute-bundle'
}

# Risk management defaults
DEFAULT_RISK_CONFIG = {
    'max_position_size': 0.15,      # 15%
    'stop_loss_pct': 0.08,          # 8%
    'take_profit_pct': 0.20,        # 20%
    'max_leverage': 1.0,            # No leverage
    'daily_loss_limit': -0.05       # -5%
}

# Analysis options defaults
DEFAULT_ANALYSIS_CONFIG = {
    'save_results': True,
    'generate_tearsheet': True,
    'save_plots': True,
    'save_csv': True
}

# =============================================================================
# FILE PATHS
# =============================================================================

# Directory paths
PATHS = {
    'strategies': 'strategies',
    'results': 'backtest_results',
    'logs': 'logs',
    'temp': 'temp',
    'exports': 'exports'
}

# Ensure directories exist
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

# =============================================================================
# STRATEGY TEMPLATES
# =============================================================================

# Strategy template configurations
TEMPLATE_CONFIG = {
    'default_imports': [
        'import pandas as pd',
        'import numpy as np',
        'from zipline.api import symbol, order_target_percent, record',
        'from engine.enhanced_base_strategy import BaseStrategy'
    ],
    'default_universe': ['SBIN', 'RELIANCE', 'HDFCBANK'],
    'default_risk_params': {
        'max_position_size': 0.15,
        'stop_loss_pct': 0.08,
        'take_profit_pct': 0.20
    }
}

# =============================================================================
# UI CONFIGURATION
# =============================================================================

# Sidebar navigation options
NAVIGATION_PAGES = [
    "🏠 Home",
    "📝 Strategy Builder", 
    "⚙️ Backtest Runner",
    "📊 Results Viewer",
    "📋 Strategy Manager"
]

# Code editor settings
CODE_EDITOR_CONFIG = {
    'theme': 'monokai',
    'language': 'python',
    'height': 400,
    'font_size': 14,
    'tab_size': 4,
    'wrap': False,
    'auto_update': True
}

# Chart configuration
CHART_CONFIG = {
    'default_height': 400,
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'background_color': 'white',
    'grid_color': '#f0f0f0'
}

# =============================================================================
# PERFORMANCE METRICS
# =============================================================================

# Metrics to display in results
PERFORMANCE_METRICS = [
    'total_return',
    'annual_return', 
    'volatility',
    'sharpe_ratio',
    'max_drawdown',
    'calmar_ratio',
    'sortino_ratio',
    'win_rate',
    'profit_factor'
]

# Metric display configuration
METRIC_DISPLAY = {
    'total_return': {'label': 'Total Return', 'format': '{:.2f}%', 'multiplier': 100},
    'annual_return': {'label': 'Annual Return', 'format': '{:.2f}%', 'multiplier': 100},
    'volatility': {'label': 'Volatility', 'format': '{:.2f}%', 'multiplier': 100},
    'sharpe_ratio': {'label': 'Sharpe Ratio', 'format': '{:.2f}', 'multiplier': 1},
    'max_drawdown': {'label': 'Max Drawdown', 'format': '{:.2f}%', 'multiplier': 100}
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(PATHS['logs'], 'web_interface.log'),
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

# Strategy validation rules
VALIDATION_RULES = {
    'required_methods': ['select_universe', 'generate_signals'],
    'required_imports': ['BaseStrategy'],
    'max_code_length': 50000,  # characters
    'timeout': 30  # seconds for validation
}

# =============================================================================
# EXPORT SETTINGS
# =============================================================================

# Export file formats
EXPORT_FORMATS = {
    'results': ['pickle', 'csv', 'json'],
    'plots': ['png', 'html', 'svg'],
    'reports': ['html', 'pdf']
}

# Export quality settings
EXPORT_QUALITY = {
    'plot_dpi': 300,
    'plot_width': 1200,
    'plot_height': 800
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_config(section, key=None, default=None):
    """Get configuration value"""
    config_map = {
        'page': PAGE_CONFIG,
        'colors': COLORS,
        'assets': NSE_ASSETS,
        'bundles': AVAILABLE_BUNDLES,
        'backtest': DEFAULT_BACKTEST_CONFIG,
        'risk': DEFAULT_RISK_CONFIG,
        'analysis': DEFAULT_ANALYSIS_CONFIG,
        'paths': PATHS,
        'template': TEMPLATE_CONFIG,
        'navigation': NAVIGATION_PAGES,
        'editor': CODE_EDITOR_CONFIG,
        'chart': CHART_CONFIG,
        'metrics': PERFORMANCE_METRICS,
        'logging': LOGGING_CONFIG,
        'validation': VALIDATION_RULES,
        'export': EXPORT_FORMATS
    }
    
    if section not in config_map:
        return default
    
    if key is None:
        return config_map[section]
    
    return config_map[section].get(key, default)

def update_config(section, key, value):
    """Update configuration value"""
    # This would be used for dynamic configuration updates
    # Implementation depends on persistence requirements
    pass

# =============================================================================
# ENVIRONMENT CHECKS
# =============================================================================

def check_environment():
    """Check if environment is properly configured"""
    checks = {
        'strategies_dir': os.path.exists(PATHS['strategies']),
        'engine_available': True,  # Would check engine imports
        'bundle_available': True   # Would check bundle availability
    }
    
    return all(checks.values()), checks

# Initialize configuration on import
if __name__ == "__main__":
    print("🔧 NSE Backtesting Engine Web Interface Configuration")
    print("=" * 50)
    
    # Display current configuration
    print(f"📁 Strategies Directory: {PATHS['strategies']}")
    print(f"📊 Results Directory: {PATHS['results']}")
    print(f"📈 Available Assets: {len(NSE_ASSETS)}")
    print(f"📦 Available Bundles: {len(AVAILABLE_BUNDLES)}")
    
    # Check environment
    env_ok, checks = check_environment()
    print(f"\n🔍 Environment Status: {'✅ OK' if env_ok else '❌ Issues Found'}")
    
    for check, status in checks.items():
        print(f"  {check}: {'✅' if status else '❌'}")
