# example_usage.py
import sys
import os

# Add the parent directory to Python path so we can import from engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.zipline_runner import TradingEngine
from engine.base_strategy import MomentumStrategy, TradingConfig
import pandas as pd
import yfinance as yf

def run_example_backtest():
    """Run a complete example backtest"""
    
    # 1. Create configuration
    config = TradingConfig(
        start_date="2020-01-01",
        end_date="2023-12-31",
        capital_base=100000.0,
        rebalance_frequency="monthly",
        max_position_size=0.03,  # 3% per position
        universe_size=100,
        commission_cost=0.001,   # 0.1% commission
        save_results=True,
        output_dir="./backtest_results"
    )
    
    # 2. Create strategy
    strategy = MomentumStrategy(
        config=config,
        momentum_window=20,  # 20-day momentum
        top_n=20,           # Long top 20 stocks
        bottom_n=20         # Short bottom 20 stocks
    )
    
    # 3. Create trading engine
    engine = TradingEngine(config)
    
    # 4. Run backtest
    print("Starting backtest...")
    backtest_results = engine.run_backtest(strategy)
    
    # 5. Download benchmark data
    benchmark = yf.download('SPY', start=config.start_date, end=config.end_date)['Close']
    benchmark_returns = benchmark.pct_change().dropna()
    benchmark_returns.index = pd.to_datetime(benchmark_returns.index)
    
    # 6. Analyze performance
    print("Analyzing performance...")
    performance = engine.analyze_performance(benchmark_returns)
    
    # 7. Print results
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    
    summary = engine.get_summary_stats()
    for metric, value in summary.items():
        print(f"{metric:20s}: {value}")
    
    print("\n" + "="*50)
    print("DETAILED PERFORMANCE METRICS")
    print("="*50)
    
    for metric, value in performance['performance_stats'].items():
        if isinstance(value, (int, float)):
            print(f"{metric:30s}: {value:.4f}")
        else:
            print(f"{metric:30s}: {value}")
    
    # 8. Create full tearsheet (optional)
    print("\nGenerating tearsheet...")
    try:
        engine.create_tearsheet(benchmark_returns)
    except Exception as e:
        print(f"Tearsheet generation failed: {e}")
    
    return engine, backtest_results, performance

if __name__ == "__main__":
    engine, results, performance = run_example_backtest()