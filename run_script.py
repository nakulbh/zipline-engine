import os
import sys
from pathlib import Path
import pandas as pd
from zipline import run_algorithm
from zipline.api import symbol

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from strategies.volume_strategy import VolumeSpikeReversalStrategy, VOLUME_SPIKE_CONFIG

# Updated config for Indian stocks
INDIAN_VOLUME_CONFIG = {
    'stocks': [
        '360ONE',      # 360ONE_minute.csv
        '3MINDIA',     # 3MINDIA_minute.csv  
        'AADHARHFC',   # AADHARHFC_minute.csv
        'AARTIIND',    # AARTIIND_minute.csv
        'AAVAS',       # AAVAS_minute.csv
        'ABB',         # ABB_minute.csv
        'ABBOTINDIA'   # ABBOTINDIA_minute.csv
    ],
    'volume_window': 20,
    'volume_factor': 2.0,
    'pin_bar_threshold': 0.7,
    'use_pin_bars': True,
    'use_engulfing': True,
    'max_positions': 3,  # Reduced since we have fewer stocks
    'position_size': 0.15,  # 15% per position
    'atr_window': 14,
    'atr_target_multiplier': 2.0,
    'atr_stop_multiplier': 1.0,
    'max_hold_days': 10,
    'rebalance_frequency': 'never',
    'max_portfolio_leverage': 1.0,
    'commission_model': 'per_share',
    'commission_cost': 0.05,  # ₹0.05 per share for Indian markets
    'commission_min': 20.0,   # Minimum ₹20
    'slippage_model': 'volume_share',
    'slippage_volume_limit': 0.025,
    'slippage_price_impact': 0.1,
    'benchmark': '360ONE',  # Use 360ONE as benchmark
    'cancel_unfilled_orders': True,
    'max_errors': 20
}

def initialize(context):
    """Initialize the strategy."""
    context.strategy = VolumeSpikeReversalStrategy(INDIAN_VOLUME_CONFIG)
    context.strategy.initialize(context)

def handle_data(context, data):
    """Handle daily data."""
    context.strategy.handle_data(context, data)

def before_trading_start(context, data):
    """Before trading start."""
    if hasattr(context.strategy, 'before_trading_start'):
        context.strategy.before_trading_start(context, data)

def analyze(context, perf):
    """Analyze results."""
    print("\n" + "="*50)
    print("INDIAN VOLUME SPIKE REVERSAL STRATEGY RESULTS")
    print("="*50)
    
    final_value = perf.portfolio_value.iloc[-1]
    initial_value = perf.portfolio_value.iloc[0]
    total_return = (final_value / initial_value - 1) * 100
    
    print(f"Initial Portfolio Value: ₹{initial_value:,.2f}")
    print(f"Final Portfolio Value: ₹{final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    
    # Calculate additional metrics
    daily_returns = perf.returns
    sharpe_ratio = daily_returns.mean() / daily_returns.std() * (252**0.5) if daily_returns.std() > 0 else 0
    max_drawdown = ((perf.portfolio_value / perf.portfolio_value.expanding().max()) - 1).min() * 100
    
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Maximum Drawdown: {max_drawdown:.2f}%")
    
    # Save results
    results_file = 'indian_volume_strategy_results.csv'
    perf.to_csv(results_file)
    print(f"\nResults saved to: {results_file}")
    
    # Print strategy-specific metrics if available
    if 'long_positions' in perf.columns:
        print(f"\nStrategy Metrics:")
        print(f"Average Long Positions: {perf.long_positions.mean():.1f}")
        print(f"Average Short Positions: {perf.short_positions.mean():.1f}")
        print(f"Max Positions Held: {perf.total_positions.max()}")

def main():
    """Run the Indian Volume Spike Reversal Strategy backtest."""
    
    print("Starting Indian Volume Spike Reversal Strategy Backtest...")
    print(f"Stocks to trade: {INDIAN_VOLUME_CONFIG['stocks']}")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Run the backtest
        results = run_algorithm(
            start=pd.Timestamp('2015-02-02'),  # Match your data start date
            end=pd.Timestamp('2025-01-31'),    # Match your data end date
            initialize=initialize,
            handle_data=handle_data,
            before_trading_start=before_trading_start,
            analyze=analyze,
            capital_base=1000000,  # ₹10,00,000 starting capital
            bundle='intraday-bundle',  # Your ingested bundle
            data_frequency='daily'
        )
        
        return results
        
    except Exception as e:
        print(f"Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Set up environment
    os.chdir('/home/nakulbh/Desktop/Ankit/QuantMania/bactestingEngine/zipline-engine')
    
    # Load environment variables
    os.system('export $(cat .env | xargs)')
    
    # Run the backtest
    results = main()
    
    if results is not None:
        print("\nBacktest completed successfully!")
        print("Check the CSV file for detailed results.")
    else:
        print("\nBacktest failed. Please check the error messages above.")