"""
This module implements a simple dual moving average crossover strategy.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
from zipline.api import order_target, symbol, set_commission, set_slippage
from zipline.finance import commission, slippage
from zipline.data import data_portal


from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from engine.enhanced_base_strategy import BaseStrategy

import bundles.duckdb_polars_bundle

class SimpleMAStrategy(BaseStrategy): 
    """
    A simple dual moving average crossover strategy.
    """
    def initialize(self, context):
        """
        Called once at the start of the algorithm.
        """
        context.i = 0
        context.asset = symbol("APOLLOTYRE")
        context.universe = [context.asset]

        # Set commission and slippage
        set_commission(commission.PerShare(cost=0.01, min_trade_cost=1))
        set_slippage(slippage.FixedSlippage(spread=0.01))

    def handle_data(self, context, data):
        """
        Called every day.
        """
        # Skip first 50 days to get full windows
        context.i += 1
        if context.i < 50:
            return

        # Compute averages
        # data.history() has to be called with the same params
        # from above and returns a pandas dataframe.
        short_mavg = data.history(
            context.asset,
            "price",
            bar_count=14,
            frequency="1m"
        ).mean()

        long_mavg = data.history(
            context.asset,
            "price",
            bar_count=50,
            frequency="1m"
        ).mean()

        # Trading logic
        if short_mavg > long_mavg:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            order_target(context.asset, 100)
        elif short_mavg < long_mavg:
            order_target(context.asset, 0)

if __name__ == '__main__':
    # Define the strategy
    strategy = SimpleMAStrategy()

    # --- Benchmark data retrieval (intraday) ---
    from zipline.data import bundles as zlbundles  # avoid name clash with local 'bundles' package
    from zipline.data.data_portal import DataPortal
    from zipline.utils.calendar_utils import get_calendar

    bundle_name = 'nse-duckdb-parquet-bundle'
    bundle_data = zlbundles.load(bundle_name)

    calendar = get_calendar('XBOM')  # Indian market calendar

    benchmark_symbol = 'NIFTY'
    start_date = '2021-01-01'
    end_date = '2025-01-01'

    # ExchangeCalendar expects timezone-naive dates for session queries
    start_session = pd.Timestamp(start_date)
    end_session = pd.Timestamp(end_date)

    # Define the backtest parameters
    capital_base = 100000
    bundle = bundle_name  # reuse
    # Create and run the backtest
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle=bundle,
        start_date=start_date,
        end_date=end_date,
        capital_base=capital_base,
        data_frequency='minute',
        live_start_date=start_date,
    )

    # Run the backtest
    results = runner.run()

    # Note: Analysis is handled within the EnhancedZiplineRunner in a real scenario.
    # The user's request mentions PyFolio, which is often used for analysis.
    # The EnhancedZiplineRunner could be extended to include PyFolio tear sheets.
    # For now, we just print a success message.
    if results is not None:
        print("Backtest completed successfully. Results are available in the `results` variable.")
        
        # Define the output path
        output_dir = os.path.join(project_root, 'backtest_results', 'simple_ma_strategy')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        file_path = os.path.join(output_dir, 'backtest_results.csv')
        results.to_pickle(file_path)
        
        print(f"Results saved to {file_path}")

