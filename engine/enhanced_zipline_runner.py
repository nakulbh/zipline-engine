import os
import pandas as pd
import pyfolio as pf
import alphalens as al
from zipline import run_algorithm
from zipline.api import set_benchmark, symbol
from zipline.utils.calendar_utils import get_calendar
import matplotlib.pyplot as plt
import logging
import time
from datetime import datetime
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest.log'),
        logging.StreamHandler()
    ]
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Suppress excessive warnings from dependencies
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

class EnhancedZiplineRunner:
    def __init__(self, strategy, bundle='quantopian-quandl', start_date='2015-1-1', end_date='2018-1-1', capital_base=100000, benchmark_symbol='NIFTY50'):
        """
        Initialize the Enhanced Zipline Runner with comprehensive logging.

        Args:
            strategy: Trading strategy instance
            bundle: Data bundle name
            start_date: Backtest start date
            end_date: Backtest end date
            capital_base: Initial capital
            benchmark_symbol: Benchmark symbol for comparison
        """
        self.strategy = strategy
        self.bundle = bundle
        # Use timezone-naive timestamps to avoid timezone parsing issues
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.capital_base = capital_base
        self.results = None
        self.benchmark_symbol = benchmark_symbol
        self.start_time = None
        self.end_time = None

        # Log initialization
        logger.info("=" * 60)
        logger.info("🚀 ENHANCED ZIPLINE RUNNER INITIALIZED")
        logger.info("=" * 60)
        logger.info(f"📊 Strategy: {strategy.__class__.__name__}")
        logger.info(f"📦 Bundle: {bundle}")
        logger.info(f"📅 Period: {start_date} to {end_date}")
        logger.info(f"💰 Capital: ${capital_base:,}")
        logger.info(f"📈 Benchmark: {benchmark_symbol}")
        logger.info(f"⏱️  Duration: {(self.end_date - self.start_date).days} days")
        logger.info("=" * 60)

    def run(self):
        """
        Runs the backtest for the given strategy with comprehensive logging.
        """
        logger.info("🔄 STARTING BACKTEST EXECUTION")
        logger.info("-" * 40)

        # Record start time
        self.start_time = time.time()
        start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"⏰ Start Time: {start_timestamp}")

        try:
            # Log strategy configuration
            logger.info(f"🎯 Initializing strategy: {self.strategy.__class__.__name__}")

            def initialize_wrapper(context):
                logger.info("📋 Setting up trading context...")
                if self.benchmark_symbol:
                    logger.info(f"📊 Setting benchmark: {self.benchmark_symbol}")
                    set_benchmark(symbol(self.benchmark_symbol))

                logger.info("🔧 Calling strategy initialization...")
                self.strategy.initialize(context)
                logger.info(f"🌐 Universe size: {len(context.universe) if hasattr(context, 'universe') else 'Unknown'}")

            # Log algorithm parameters
            logger.info("⚙️  Algorithm Configuration:")
            logger.info(f"   📅 Start Date: {self.start_date}")
            logger.info(f"   📅 End Date: {self.end_date}")
            logger.info(f"   💰 Capital Base: ${self.capital_base:,}")
            logger.info(f"   📦 Data Bundle: {self.bundle}")
            logger.info(f"   📊 Data Frequency: minute")
            logger.info(f"   🗓️  Trading Calendar: XBOM (NSE/BSE)")

            logger.info("🚀 Launching Zipline algorithm...")

            self.results = run_algorithm(
                start=self.start_date,
                end=self.end_date,
                initialize=initialize_wrapper,
                before_trading_start=self.strategy.before_trading_start,
                capital_base=self.capital_base,
                data_frequency='minute',  # Specify minute data frequency
                bundle=self.bundle,
                trading_calendar=get_calendar('XBOM'), # Use a calendar that matches your data (e.g., XBOM for NSE/BSE)
                benchmark_returns=None # Zipline will use the benchmark set in initialize
            )

            # Record end time and calculate duration
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logger.info("✅ BACKTEST COMPLETED SUCCESSFULLY!")
            logger.info("-" * 40)
            logger.info(f"⏰ End Time: {end_timestamp}")
            logger.info(f"⏱️  Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

            # Log basic results summary
            if self.results is not None:
                final_value = self.results['portfolio_value'].iloc[-1]
                total_return = (final_value / self.capital_base - 1) * 100
                logger.info(f"💰 Final Portfolio Value: ${final_value:,.2f}")
                logger.info(f"📈 Total Return: {total_return:.2f}%")
                logger.info(f"📊 Total Trading Days: {len(self.results)}")

            return self.results

        except Exception as e:
            self.end_time = time.time()
            duration = self.end_time - self.start_time if self.start_time else 0

            logger.error("❌ BACKTEST FAILED!")
            logger.error("-" * 40)
            logger.error(f"💥 Error: {str(e)}")
            logger.error(f"⏱️  Failed after: {duration:.2f} seconds")
            logger.error(f"🔍 Error Type: {type(e).__name__}")

            # Log stack trace for debugging
            import traceback
            logger.error("📋 Stack Trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")

            raise

    def analyze(self, results_dir='backtest_results'):
        """
        Analyzes the performance of the backtest using pyfolio and alphalens with comprehensive logging.
        """
        logger.info("📊 STARTING PERFORMANCE ANALYSIS")
        logger.info("-" * 40)

        if self.results is None:
            logger.error("❌ No backtest results found. Please run the backtest first.")
            return

        # Create results directory
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            logger.info(f"📁 Created results directory: {results_dir}")
        else:
            logger.info(f"📁 Using existing results directory: {results_dir}")

        analysis_start_time = time.time()

        try:
            logger.info("🔍 Attempting Pyfolio analysis...")

            # Manual extraction of data from Zipline results (more robust approach)
            returns = self.results['returns'].copy()
            returns.index = pd.to_datetime(returns.index)

            # Extract positions data
            positions = None
            transactions = None

            # Try to extract positions if available
            try:
                if hasattr(self.results, 'positions') and len(self.results.positions) > 0:
                    # Convert positions to DataFrame format expected by Pyfolio
                    positions_data = []
                    for pos in self.results.positions:
                        if hasattr(pos, 'to_dict'):
                            positions_data.append(pos.to_dict())

                    if positions_data:
                        positions = pd.DataFrame(positions_data)
                        if not positions.empty:
                            positions.index = pd.to_datetime(positions.index) if hasattr(positions, 'index') else returns.index[:len(positions)]
                        else:
                            positions = None
                else:
                    logger.info("   ℹ️  No positions data available")
            except Exception as pos_e:
                logger.warning(f"   ⚠️  Could not extract positions: {pos_e}")
                positions = None

            # Try to extract transactions if available
            try:
                if hasattr(self.results, 'transactions') and len(self.results.transactions) > 0:
                    transactions_data = []
                    for txn in self.results.transactions:
                        if hasattr(txn, 'to_dict'):
                            transactions_data.append(txn.to_dict())

                    if transactions_data:
                        transactions = pd.DataFrame(transactions_data)
                        if not transactions.empty:
                            transactions.index = pd.to_datetime(transactions.index) if hasattr(transactions, 'index') else returns.index[:len(transactions)]
                        else:
                            transactions = None
                else:
                    logger.info("   ℹ️  No transactions data available")
            except Exception as txn_e:
                logger.warning(f"   ⚠️  Could not extract transactions: {txn_e}")
                transactions = None

            logger.info("✅ Successfully extracted data for Pyfolio")
            logger.info(f"   📈 Returns data points: {len(returns)}")
            logger.info(f"   💼 Positions available: {'Yes' if positions is not None else 'No'}")
            logger.info(f"   💱 Transactions available: {'Yes' if transactions is not None else 'No'}")

            logger.info("📊 Generating Pyfolio tear sheet...")

            # Create simplified tear sheet (more robust)
            pf.create_returns_tear_sheet(
                returns,
                benchmark_rets=None,  # We'll add benchmark later if available
                live_start_date=None
            )
            plt.savefig(os.path.join(results_dir, 'pyfolio_returns_tearsheet.png'), dpi=300, bbox_inches='tight')
            plt.close()

            # If we have positions and transactions, create full tear sheet
            if positions is not None and transactions is not None:
                try:
                    logger.info("📊 Creating full tear sheet with positions and transactions...")
                    pf.create_full_tear_sheet(
                        returns,
                        positions=positions,
                        transactions=transactions,
                        round_trips=True
                    )
                    plt.savefig(os.path.join(results_dir, 'pyfolio_full_tearsheet.png'), dpi=300, bbox_inches='tight')
                    plt.close()
                    logger.info("✅ Full Pyfolio tear sheet created successfully")
                except Exception as full_e:
                    logger.warning(f"⚠️  Full tear sheet failed, but returns tear sheet succeeded: {full_e}")

            logger.info("✅ Pyfolio analysis completed successfully")

        except Exception as e:
            logger.warning(f"⚠️  Pyfolio analysis failed: {str(e)}")
            logger.info("📊 Falling back to basic performance analysis...")

            # Basic performance analysis
            self._create_basic_analysis(results_dir)

        # Alphalens analysis (if factor data available)
        try:
            # Check for factor data in multiple places
            factor_data = None
            pricing_data = None

            # Method 1: Check if strategy has factor_data attribute
            if hasattr(self.strategy, 'factor_data') and self.strategy.factor_data is not None:
                factor_data = self.strategy.factor_data
                logger.info("🔍 Found factor data in strategy")

            # Method 2: Check recorded variables for factor-like data
            elif hasattr(self.results, 'recorded_vars') and not self.results.recorded_vars.empty:
                recorded_vars = self.results.recorded_vars
                logger.info(f"🔍 Found recorded variables: {list(recorded_vars.columns)}")

                factor_candidates = []

                for var_name in recorded_vars.columns:
                    if any(keyword in var_name.lower() for keyword in ['factor', 'signal', 'score', 'rank', 'sma', 'momentum']):
                        factor_candidates.append(var_name)

                if factor_candidates:
                    logger.info(f"🔍 Found potential factor data in recorded variables: {factor_candidates}")
                    # Use the first factor candidate
                    factor_data = recorded_vars[factor_candidates[0]].dropna()
                    if len(factor_data) > 0:
                        logger.info(f"   📊 Using '{factor_candidates[0]}' as factor data ({len(factor_data)} observations)")
                else:
                    logger.info("   ℹ️  No factor-like variables found in recorded data")
            else:
                logger.info("   ℹ️  No recorded variables found in results")

            # Method 3: Extract pricing data for factor analysis
            if factor_data is not None:
                try:
                    # Try to construct pricing data from portfolio values or recorded prices
                    if hasattr(self.results, 'recorded_vars') and 'prices' in self.results.recorded_vars.columns:
                        pricing_data = self.results.recorded_vars['prices']
                        logger.info("📊 Using recorded prices for Alphalens analysis")
                    else:
                        # Create synthetic pricing data from portfolio performance
                        # This is a fallback - not ideal but allows basic factor analysis
                        portfolio_values = self.results['portfolio_value']
                        pricing_data = pd.DataFrame({
                            'synthetic_price': portfolio_values / portfolio_values.iloc[0] * 100
                        })
                        logger.info("📊 Using synthetic pricing data based on portfolio performance")
                        logger.warning("   ⚠️  Using synthetic pricing - results may not be accurate")

                    if pricing_data is not None and len(pricing_data) > 0:
                        logger.info("🔍 Attempting Alphalens factor analysis...")

                        # Prepare factor data for Alphalens
                        if isinstance(factor_data, pd.Series):
                            # Convert Series to DataFrame format expected by Alphalens
                            factor_df = factor_data.to_frame('factor')
                        else:
                            factor_df = factor_data

                        # Align factor and pricing data
                        common_dates = factor_df.index.intersection(pricing_data.index)
                        if len(common_dates) < 10:
                            logger.warning("⚠️  Insufficient overlapping data for factor analysis")
                            raise ValueError("Not enough overlapping data points")

                        factor_aligned = factor_df.loc[common_dates]
                        pricing_aligned = pricing_data.loc[common_dates]

                        logger.info(f"   📊 Aligned data: {len(common_dates)} common dates")

                        # Create factor and returns data for Alphalens
                        factor_and_returns = al.utils.get_clean_factor_and_forward_returns(
                            factor=factor_aligned.iloc[:, 0],  # Use first column as factor
                            prices=pricing_aligned.iloc[:, 0] if pricing_aligned.shape[1] == 1 else pricing_aligned,
                            quantiles=3,  # Reduce quantiles for smaller datasets
                            periods=(1, 5),  # Shorter periods for more robust analysis
                            max_loss=0.5  # Allow more data loss for small datasets
                        )

                        logger.info(f"   📊 Factor analysis data prepared: {len(factor_and_returns)} observations")

                        # Create Alphalens tear sheet
                        al.tears.create_returns_tear_sheet(factor_and_returns)
                        plt.savefig(os.path.join(results_dir, 'alphalens_returns_tearsheet.png'), dpi=300, bbox_inches='tight')
                        plt.close()

                        # Create information coefficient analysis
                        al.tears.create_information_tear_sheet(factor_and_returns)
                        plt.savefig(os.path.join(results_dir, 'alphalens_ic_tearsheet.png'), dpi=300, bbox_inches='tight')
                        plt.close()

                        logger.info("✅ Alphalens analysis completed successfully")
                        logger.info(f"   📁 Tearsheets saved to {results_dir}")
                    else:
                        logger.info("ℹ️  No suitable pricing data found for Alphalens analysis")

                except Exception as pricing_e:
                    logger.warning(f"⚠️  Could not prepare pricing data: {pricing_e}")
                    logger.info("ℹ️  Skipping Alphalens analysis due to pricing data issues")
            else:
                logger.info("ℹ️  No factor data available for Alphalens analysis")
                logger.info("   💡 Tip: Record factor data in your strategy using record(factor_name=factor_values)")

        except Exception as e:
            logger.warning(f"⚠️  Alphalens analysis failed: {str(e)}")
            logger.info("   🔍 This is often due to insufficient data or misaligned timestamps")

        # Save results to CSV
        logger.info("💾 Saving results to CSV files...")
        self.save_results_to_csv(results_dir)

        # Calculate and log analysis completion time
        analysis_end_time = time.time()
        analysis_duration = analysis_end_time - analysis_start_time

        logger.info("✅ PERFORMANCE ANALYSIS COMPLETED")
        logger.info("-" * 40)
        logger.info(f"⏱️  Analysis Duration: {analysis_duration:.2f} seconds")
        logger.info(f"📁 Results Location: {os.path.abspath(results_dir)}")
        logger.info("=" * 60)

    def _create_basic_analysis(self, results_dir):
        """Create basic performance analysis when pyfolio fails"""
        logger.info("📊 Creating basic performance analysis...")

        try:
            # Extract basic metrics
            returns = self.results['returns']
            portfolio_value = self.results['portfolio_value']

            logger.info(f"📈 Processing {len(returns)} return data points")
            logger.info(f"💰 Portfolio value range: ${portfolio_value.min():,.2f} - ${portfolio_value.max():,.2f}")

            # Create basic plots
            logger.info("📊 Generating performance charts...")
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))

            # Portfolio value over time
            axes[0, 0].plot(portfolio_value.index, portfolio_value.values, linewidth=2, color='blue')
            axes[0, 0].set_title('Portfolio Value Over Time', fontsize=12, fontweight='bold')
            axes[0, 0].set_ylabel('Portfolio Value ($)')
            axes[0, 0].grid(True, alpha=0.3)

            # Daily returns
            axes[0, 1].plot(returns.index, returns.values, linewidth=1, color='green', alpha=0.7)
            axes[0, 1].set_title('Daily Returns', fontsize=12, fontweight='bold')
            axes[0, 1].set_ylabel('Returns')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)

            # Cumulative returns
            cumulative_returns = (1 + returns).cumprod()
            axes[1, 0].plot(cumulative_returns.index, cumulative_returns.values, linewidth=2, color='purple')
            axes[1, 0].set_title('Cumulative Returns', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylabel('Cumulative Returns')
            axes[1, 0].grid(True, alpha=0.3)

            # Returns distribution
            axes[1, 1].hist(returns.values, bins=50, alpha=0.7, color='orange', edgecolor='black')
            axes[1, 1].set_title('Returns Distribution', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('Returns')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].axvline(x=returns.mean(), color='red', linestyle='--', label=f'Mean: {returns.mean():.4f}')
            axes[1, 1].legend()

            plt.tight_layout()
            chart_path = os.path.join(results_dir, 'basic_analysis.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"📊 Charts saved to: {chart_path}")

            # Calculate basic statistics
            logger.info("📊 Calculating performance metrics...")
            total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5) if returns.std() != 0 else 0
            max_drawdown = ((portfolio_value / portfolio_value.expanding().max()) - 1).min()

            # Additional metrics
            win_rate = (returns > 0).sum() / len(returns) * 100
            avg_win = returns[returns > 0].mean() if (returns > 0).any() else 0
            avg_loss = returns[returns < 0].mean() if (returns < 0).any() else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')

            # Save statistics to file
            stats = {
                'Total Return': f"{total_return:.2%}",
                'Annualized Volatility': f"{volatility:.2%}",
                'Sharpe Ratio': f"{sharpe_ratio:.2f}",
                'Max Drawdown': f"{max_drawdown:.2%}",
                'Win Rate': f"{win_rate:.1f}%",
                'Average Win': f"{avg_win:.4f}",
                'Average Loss': f"{avg_loss:.4f}",
                'Profit Factor': f"{profit_factor:.2f}",
                'Start Value': f"${portfolio_value.iloc[0]:,.2f}",
                'End Value': f"${portfolio_value.iloc[-1]:,.2f}",
                'Total Trading Days': f"{len(returns)}"
            }

            stats_path = os.path.join(results_dir, 'performance_stats.txt')
            with open(stats_path, 'w') as f:
                f.write("BACKTEST PERFORMANCE SUMMARY\n")
                f.write("=" * 40 + "\n\n")
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")

            # Log key metrics
            logger.info("📊 KEY PERFORMANCE METRICS:")
            logger.info(f"   💰 Total Return: {total_return:.2%}")
            logger.info(f"   📊 Sharpe Ratio: {sharpe_ratio:.2f}")
            logger.info(f"   📉 Max Drawdown: {max_drawdown:.2%}")
            logger.info(f"   🎯 Win Rate: {win_rate:.1f}%")
            logger.info(f"   📈 Volatility: {volatility:.2%}")

            logger.info("✅ Basic analysis completed successfully!")
            logger.info(f"📁 Statistics saved to: {stats_path}")

        except Exception as e:
            logger.error(f"❌ Basic analysis failed: {str(e)}")
            logger.error("🔍 This indicates a serious issue with the backtest results")
            import traceback
            logger.error("📋 Stack Trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")

    def save_results_to_csv(self, results_dir):
        """
        Saves the order book, trade book, and ledger to CSV files with comprehensive logging.
        """
        logger.info("💾 SAVING RESULTS TO CSV FILES")
        logger.info("-" * 30)

        if self.results is None:
            logger.error("❌ No results to save. Run backtest first.")
            return

        saved_files = []

        try:
            # Basic results - always available
            logger.info("📊 Saving basic results (portfolio value & returns)...")
            basic_results = self.results[['portfolio_value', 'returns']].copy()
            basic_path = os.path.join(results_dir, 'basic_results.csv')
            basic_results.to_csv(basic_path)
            saved_files.append('basic_results.csv')
            logger.info(f"   ✅ Basic results: {len(basic_results)} rows saved")

            # Save recorded variables if they exist
            try:
                if hasattr(self.results, 'recorded_vars') and not self.results.recorded_vars.empty:
                    logger.info("📊 Saving recorded variables (factors, signals, etc.)...")
                    recorded_vars_path = os.path.join(results_dir, 'recorded_variables.csv')
                    self.results.recorded_vars.to_csv(recorded_vars_path)
                    saved_files.append('recorded_variables.csv')
                    logger.info(f"   ✅ Recorded variables: {len(self.results.recorded_vars)} rows, {len(self.results.recorded_vars.columns)} columns")
                    logger.info(f"   📊 Variables: {list(self.results.recorded_vars.columns)}")
                else:
                    logger.info("   ℹ️  No recorded variables to save")
            except Exception as e:
                logger.warning(f"⚠️  Could not save recorded variables: {str(e)}")

            # Try to save orders if they exist
            try:
                if hasattr(self.results, 'orders') and len(self.results.orders) > 0:
                    logger.info("📋 Processing order book data...")
                    # Convert orders to DataFrame if they're not empty
                    orders_data = []
                    for i, order in enumerate(self.results.orders):
                        try:
                            if hasattr(order, 'to_dict'):
                                orders_data.append(order.to_dict())
                            else:
                                orders_data.append({'order_str': str(order), 'order_id': i})
                        except Exception as order_e:
                            logger.warning(f"   ⚠️  Could not process order {i}: {order_e}")

                    if orders_data:
                        orders_df = pd.DataFrame(orders_data)
                        orders_path = os.path.join(results_dir, 'order_book.csv')
                        orders_df.to_csv(orders_path)
                        saved_files.append('order_book.csv')
                        logger.info(f"   ✅ Order book: {len(orders_data)} orders saved")
                    else:
                        logger.info("   ℹ️  No valid order data to save")
                else:
                    logger.info("   ℹ️  No orders found in results")
            except Exception as e:
                logger.warning(f"⚠️  Could not save orders: {str(e)}")

            # Try to save transactions if they exist
            try:
                if hasattr(self.results, 'transactions') and len(self.results.transactions) > 0:
                    logger.info("💱 Processing transaction data...")
                    transactions_data = []
                    for i, txn in enumerate(self.results.transactions):
                        try:
                            if hasattr(txn, 'to_dict'):
                                transactions_data.append(txn.to_dict())
                            else:
                                transactions_data.append({'transaction_str': str(txn), 'txn_id': i})
                        except Exception as txn_e:
                            logger.warning(f"   ⚠️  Could not process transaction {i}: {txn_e}")

                    if transactions_data:
                        transactions_df = pd.DataFrame(transactions_data)
                        transactions_path = os.path.join(results_dir, 'trade_book.csv')
                        transactions_df.to_csv(transactions_path)
                        saved_files.append('trade_book.csv')
                        logger.info(f"   ✅ Trade book: {len(transactions_data)} transactions saved")
                    else:
                        logger.info("   ℹ️  No valid transaction data to save")
                else:
                    logger.info("   ℹ️  No transactions found in results")
            except Exception as e:
                logger.warning(f"⚠️  Could not save transactions: {str(e)}")

            # Log summary
            logger.info("✅ CSV EXPORT COMPLETED")
            logger.info(f"📁 Location: {os.path.abspath(results_dir)}")
            logger.info(f"📄 Files saved: {', '.join(saved_files)}")

        except Exception as e:
            logger.error(f"❌ Error saving results: {str(e)}")
            logger.error("🔍 This may indicate corrupted backtest results")
            import traceback
            logger.error("📋 Stack Trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")

if __name__ == '__main__':
    # This is an example of how to use the runner
    # You would import your strategy and run it here
    
    # from my_strategy import MyStrategy
    # strategy = MyStrategy()
    
    # runner = EnhancedZiplineRunner(strategy)
    # runner.run()
    # runner.analyze()
    pass
