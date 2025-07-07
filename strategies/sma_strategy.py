import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from zipline.api import symbol, record
import numpy as np

class SmaCrossoverStrategy(BaseStrategy):
    """
    A simple moving average (SMA) crossover strategy.

    **Strategy Logic:**
    - **Entry Signal**: A buy signal is generated when the short-term moving average crosses above the long-term moving average.
    - **Exit Signal**: A sell signal is generated when the short-term moving average crosses below the long-term moving average.
    """

    def __init__(self, short_window=50, long_window=200, assets=None):
        """
        Initializes the strategy with SMA windows and a list of assets.

        Parameters:
        - short_window (int): The lookback period for the short-term moving average.
        - long_window (int): The lookback period for the long-term moving average.
        - assets (list[str]): A list of asset symbols to trade.
        """
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.assets = assets if assets else ['SBIN', 'RELIANCE', 'HDFCBANK'] # Default NSE assets

    def initialize(self, context):
        """
        This method is called once at the start of the backtest. It's the ideal place for one-time setup tasks.
        We call the parent's initialize method to ensure the base strategy is set up correctly.
        """
        super().initialize(context)

    def select_universe(self, context) -> list:
        """
        This method defines the universe of assets the strategy will trade.
        It's called by the `initialize` method in the base class.
        Here, we convert the list of asset symbols into Zipline `Asset` objects.
        """
        return [symbol(asset) for asset in self.assets]

    def generate_signals(self, context, data) -> dict:
        """
        This is the core of the strategy, where trading signals are generated.
        It's called at each rebalance interval defined by the schedule in the base strategy.

        For each asset in our universe, we:
        1. Fetch historical price data.
        2. Calculate the short-term and long-term moving averages.
        3. Generate a buy signal (1.0) if the short SMA is above the long SMA, and a sell signal (-1.0) otherwise.
        4. Record factor data for Alphalens analysis.
        """
        signals = {}
        for asset in context.universe:
            # Get historical data for the asset
            history = data.history(asset, 'price', self.long_window + 1, '1d')

            if not history.empty:
                # Calculate moving averages
                short_mavg = history.tail(self.short_window).mean()
                long_mavg = history.mean()

                # Calculate additional factors for Alphalens analysis
                current_price = history.iloc[-1]

                # SMA ratio factor (short SMA / long SMA)
                sma_ratio = short_mavg / long_mavg if long_mavg != 0 else 1.0

                # Price momentum factor (current price / long SMA)
                price_momentum = current_price / long_mavg if long_mavg != 0 else 1.0

                # SMA spread factor (normalized difference)
                sma_spread = (short_mavg - long_mavg) / current_price if current_price != 0 else 0.0

                # Generate signals
                if short_mavg > long_mavg:
                    signals[asset] = 1.0  # Buy signal
                else:
                    signals[asset] = -1.0  # Sell signal

                # Record factors for Alphalens analysis
                self.record_factor('sma_ratio', sma_ratio, context)
                self.record_factor('price_momentum', price_momentum, context)
                self.record_factor('sma_spread', sma_spread, context)
                self.record_factor('signal_strength', abs(sma_spread), context)

                # Record current prices for Alphalens
                record(prices=current_price)

            else:
                signals[asset] = 0.0 # No signal if no data

        return signals

if __name__ == '__main__':
    """
    This block allows you to run the strategy directly from this file.
    It demonstrates how to instantiate the strategy and the backtest runner, 
    execute the backtest, and perform the analysis.
    """
    # Import the backtest runner
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    import pandas as pd

    # 1. Define Strategy Parameters
    # You can easily tweak the strategy's behavior by changing these variables.
    assets_to_trade = ['SBIN']
    short_window_sma = 20
    long_window_sma = 50
    nse_bundle = 'nse-local-minute-bundle'

    # 2. Instantiate the Strategy
    # Create an instance of your strategy with the parameters you defined.
    sma_strategy = SmaCrossoverStrategy(
        short_window=short_window_sma,
        long_window=long_window_sma,
        assets=assets_to_trade
    )

    # 3. Configure the Backtest Runner
    # Set up the environment for the backtest, including the date range, 
    # initial capital, and the data bundle to use.
    # IMPORTANT: Make sure the 'bundle' name matches the one you have ingested.
    runner = EnhancedZiplineRunner(
        strategy=sma_strategy,
        bundle=nse_bundle,  # <-- CHANGE THIS if you use a different bundle
        start_date='2018-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'  
    )

    # 4. Run the Backtest
    # This command executes the Zipline algorithm and stores the results.
    print("Running backtest...")
    results = runner.run()

    # 5. Analyze the Results
    # This command generates the performance reports (Pyfolio and Alphalens)
    # and saves them to the 'backtest_results' directory.
    print("Analyzing results...")
    runner.analyze(results_dir='backtest_results/sma_crossover')

    print("Backtest and analysis complete.")
