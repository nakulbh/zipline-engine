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
import pickle

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
    def __init__(self, strategy, bundle='quantopian-quandl', start_date='2015-1-1', end_date='2018-1-1', capital_base=100000, benchmark_symbol='NIFTY50', data_frequency='minute'):
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
        self.data_frequency = data_frequency
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
                data_frequency=self.data_frequency,  # Use configurable data frequency
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

            # Create comprehensive Pyfolio analysis with enhanced saving
            logger.info("📊 Creating comprehensive Pyfolio tear sheets...")

            # 1. Returns tear sheet
            logger.info("   📈 Generating returns tear sheet...")
            pf.create_returns_tear_sheet(
                returns,
                benchmark_rets=None,
                live_start_date=None
            )
            plt.savefig(os.path.join(results_dir, 'pyfolio_returns_tearsheet.png'),
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            # 2. Performance statistics tear sheet
            logger.info("   📊 Generating performance statistics...")
            try:
                # Get performance stats and save to CSV
                perf_stats = pf.timeseries.perf_stats(returns)
                perf_stats.to_csv(os.path.join(results_dir, 'performance_statistics.csv'))
                logger.info(f"   ✅ Performance statistics saved to CSV")
            except Exception as stats_e:
                logger.warning(f"   ⚠️  Could not save performance statistics: {stats_e}")

            # 3. Full tear sheet with positions and transactions
            if positions is not None and transactions is not None:
                try:
                    logger.info("   📊 Creating full tear sheet with positions and transactions...")

                    # Create full tear sheet with round trips
                    pf.create_full_tear_sheet(
                        returns,
                        positions=positions,
                        transactions=transactions,
                        round_trips=True,
                        live_start_date=None
                    )
                    plt.savefig(os.path.join(results_dir, 'pyfolio_full_tearsheet.png'),
                               dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()

                    # Save round trip analysis to CSV
                    try:
                        round_trips = pf.round_trips.extract_round_trips(transactions)
                        if not round_trips.empty:
                            round_trips.to_csv(os.path.join(results_dir, 'round_trips_analysis.csv'))
                            logger.info("   ✅ Round trips analysis saved to CSV")
                    except Exception as rt_e:
                        logger.warning(f"   ⚠️  Could not save round trips analysis: {rt_e}")

                    logger.info("✅ Full Pyfolio tear sheet created successfully")

                except Exception as full_e:
                    logger.warning(f"⚠️  Full tear sheet failed, but returns tear sheet succeeded: {full_e}")

            # 4. Individual analysis components with CSV export
            try:
                logger.info("   📊 Creating individual analysis components...")

                # Rolling performance metrics
                rolling_stats = pf.timeseries.rolling_stats(returns, rolling_window=252)
                rolling_stats.to_csv(os.path.join(results_dir, 'rolling_performance_stats.csv'))

                # Drawdown analysis
                drawdown_df = pf.timeseries.gen_drawdown_table(returns, top=10)
                drawdown_df.to_csv(os.path.join(results_dir, 'top_drawdowns.csv'))

                # Monthly returns
                monthly_returns = pf.timeseries.aggregate_returns(returns, 'monthly')
                monthly_returns.to_csv(os.path.join(results_dir, 'monthly_returns.csv'))

                # Annual returns
                annual_returns = pf.timeseries.aggregate_returns(returns, 'yearly')
                annual_returns.to_csv(os.path.join(results_dir, 'annual_returns.csv'))

                logger.info("   ✅ Individual analysis components saved to CSV")

            except Exception as comp_e:
                logger.warning(f"   ⚠️  Could not save individual components: {comp_e}")

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

        # Save results to CSV with benchmark analysis
        logger.info("💾 Saving results to CSV files...")
        self.save_results_to_csv(results_dir)

        # Calculate and save benchmark metrics
        if self.benchmark_symbol:
            logger.info("📊 Calculating benchmark metrics...")
            self.save_benchmark_analysis_to_csv(results_dir)

        # Calculate and log analysis completion time
        analysis_end_time = time.time()
        analysis_duration = analysis_end_time - analysis_start_time

        logger.info("✅ PERFORMANCE ANALYSIS COMPLETED")
        logger.info("-" * 40)
        logger.info(f"⏱️  Analysis Duration: {analysis_duration:.2f} seconds")
        logger.info(f"📁 Results Location: {os.path.abspath(results_dir)}")
        logger.info("=" * 60)

    def create_enhanced_pyfolio_analysis(self, results_dir='backtest_results', live_start_date=None,
                                       save_plots=True, save_csv=True):
        """
        Create enhanced Pyfolio analysis similar to the example you provided.
        This method provides comprehensive analysis with plot saving and CSV export.

        Parameters:
        -----------
        results_dir : str
            Directory to save results
        live_start_date : str or datetime, optional
            Date when live trading started (for out-of-sample analysis)
        save_plots : bool
            Whether to save plots as PNG files
        save_csv : bool
            Whether to save data as CSV files
        """
        if self.results is None:
            logger.error("❌ No backtest results available. Run backtest first.")
            return

        logger.info("🚀 CREATING ENHANCED PYFOLIO ANALYSIS")
        logger.info("=" * 50)

        # Ensure results directory exists
        os.makedirs(results_dir, exist_ok=True)

        try:
            # Extract data from results
            returns = self.results['returns'].copy()
            returns.index = pd.to_datetime(returns.index)

            # Extract positions and transactions
            positions = None
            transactions = None

            try:
                if hasattr(self.results, 'positions') and len(self.results.positions) > 0:
                    positions_data = []
                    for pos in self.results.positions:
                        if hasattr(pos, 'to_dict'):
                            positions_data.append(pos.to_dict())

                    if positions_data:
                        positions = pd.DataFrame(positions_data)
                        positions.index = pd.to_datetime(positions.index)

                if hasattr(self.results, 'transactions') and len(self.results.transactions) > 0:
                    transactions_data = []
                    for txn in self.results.transactions:
                        if hasattr(txn, 'to_dict'):
                            transactions_data.append(txn.to_dict())

                    if transactions_data:
                        transactions = pd.DataFrame(transactions_data)
                        transactions.index = pd.to_datetime(transactions.index)

            except Exception as e:
                logger.warning(f"⚠️  Could not extract positions/transactions: {e}")

            # Convert live_start_date if provided
            if live_start_date:
                if isinstance(live_start_date, str):
                    live_start_date = pd.to_datetime(live_start_date)

            logger.info("📊 Creating comprehensive Pyfolio tear sheet...")

            # Create the full tear sheet (similar to your example)
            if positions is not None and transactions is not None:
                pf.create_full_tear_sheet(
                    returns,
                    positions=positions,
                    transactions=transactions,
                    live_start_date=live_start_date,
                    round_trips=True,
                    hide_positions=False,
                    cone_std=(1.0, 1.5, 2.0),
                    bootstrap=False  # Disable bootstrap to avoid benchmark requirement
                )
            else:
                # Create returns-only tear sheet if positions/transactions not available
                pf.create_returns_tear_sheet(
                    returns,
                    live_start_date=live_start_date,
                    cone_std=(1.0, 1.5, 2.0),
                    bootstrap=False  # Disable bootstrap to avoid benchmark requirement
                )

            if save_plots:
                # Save the comprehensive plot
                plt.savefig(os.path.join(results_dir, 'enhanced_pyfolio_analysis.png'),
                           dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                logger.info("✅ Enhanced Pyfolio plots saved")

            if save_csv:
                # Save comprehensive CSV data
                self._save_enhanced_csv_data(results_dir, returns, positions, transactions)

            logger.info("✅ Enhanced Pyfolio analysis completed successfully")

        except Exception as e:
            logger.error(f"❌ Enhanced Pyfolio analysis failed: {e}")
            raise

    def _save_enhanced_csv_data(self, results_dir, returns, positions=None, transactions=None):
        """Save comprehensive CSV data similar to the Pyfolio example"""
        logger.info("💾 Saving enhanced CSV data...")

        try:
            # 1. Basic returns and performance metrics
            returns.to_csv(os.path.join(results_dir, 'returns_series.csv'), header=['returns'])

            # 2. Performance statistics
            perf_stats = pf.timeseries.perf_stats(returns)
            perf_stats.to_csv(os.path.join(results_dir, 'performance_statistics.csv'), header=['value'])

            # 3. Rolling performance metrics (252-day rolling window)
            rolling_stats = pf.timeseries.rolling_stats(returns, rolling_window=252)
            rolling_stats.to_csv(os.path.join(results_dir, 'rolling_performance_metrics.csv'))

            # 4. Drawdown analysis
            drawdown_table = pf.timeseries.gen_drawdown_table(returns, top=10)
            drawdown_table.to_csv(os.path.join(results_dir, 'top_10_drawdowns.csv'))

            # 5. Monthly and annual returns
            monthly_returns = pf.timeseries.aggregate_returns(returns, 'monthly')
            monthly_returns.to_csv(os.path.join(results_dir, 'monthly_returns.csv'), header=['monthly_return'])

            annual_returns = pf.timeseries.aggregate_returns(returns, 'yearly')
            annual_returns.to_csv(os.path.join(results_dir, 'annual_returns.csv'), header=['annual_return'])

            # 6. Risk metrics
            risk_metrics = {
                'sharpe_ratio': pf.timeseries.sharpe_ratio(returns),
                'calmar_ratio': pf.timeseries.calmar_ratio(returns),
                'sortino_ratio': pf.timeseries.sortino_ratio(returns),
                'max_drawdown': pf.timeseries.max_drawdown(returns),
                'annual_volatility': pf.timeseries.annual_volatility(returns),
                'stability': pf.timeseries.stability_of_timeseries(returns),
                'tail_ratio': pf.timeseries.tail_ratio(returns)
            }
            risk_df = pd.DataFrame.from_dict(risk_metrics, orient='index', columns=['value'])
            risk_df.to_csv(os.path.join(results_dir, 'risk_metrics.csv'))

            # 7. Positions data (if available)
            if positions is not None:
                positions.to_csv(os.path.join(results_dir, 'positions_data.csv'))
                logger.info("   ✅ Positions data saved")

            # 8. Transactions data (if available)
            if transactions is not None:
                transactions.to_csv(os.path.join(results_dir, 'transactions_data.csv'))

                # Round trips analysis
                try:
                    round_trips = pf.round_trips.extract_round_trips(transactions)
                    if not round_trips.empty:
                        round_trips.to_csv(os.path.join(results_dir, 'round_trips_analysis.csv'))

                        # Round trip statistics
                        rt_stats = pf.round_trips.gen_round_trip_stats(round_trips)
                        rt_stats.to_csv(os.path.join(results_dir, 'round_trip_statistics.csv'))

                        logger.info("   ✅ Round trips analysis saved")
                except Exception as rt_e:
                    logger.warning(f"   ⚠️  Round trips analysis failed: {rt_e}")

                logger.info("   ✅ Transactions data saved")

            # 9. Underwater plot data (drawdown over time)
            underwater = pf.timeseries.underwater(returns)
            underwater.to_csv(os.path.join(results_dir, 'underwater_drawdown.csv'), header=['drawdown'])

            # 10. Rolling Sharpe ratio
            rolling_sharpe = pf.timeseries.rolling_sharpe(returns, rolling_window=252)
            rolling_sharpe.to_csv(os.path.join(results_dir, 'rolling_sharpe_ratio.csv'), header=['rolling_sharpe'])

            logger.info("✅ Enhanced CSV data saved successfully")
            logger.info(f"   📁 Location: {os.path.abspath(results_dir)}")

        except Exception as e:
            logger.error(f"❌ Failed to save enhanced CSV data: {e}")

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
            fig.suptitle('Portfolio Performance Analysis', fontsize=16, fontweight='bold')

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
            # Basic results - always available (including benchmark data if present)
            logger.info("📊 Saving basic results (portfolio value & returns)...")

            # Start with core columns
            basic_columns = ['portfolio_value', 'returns']

            # Add benchmark columns if they exist
            benchmark_columns = [col for col in self.results.columns if 'benchmark' in col.lower()]
            if benchmark_columns:
                basic_columns.extend(benchmark_columns)
                logger.info(f"   📊 Including benchmark columns: {benchmark_columns}")

            basic_results = self.results[basic_columns].copy()

            # Add calculated benchmark metrics if benchmark data exists
            if benchmark_columns and self.benchmark_symbol:
                benchmark_return_col = None
                for col in benchmark_columns:
                    if 'return' in col.lower():
                        benchmark_return_col = col
                        break

                if benchmark_return_col:
                    # Add excess returns column
                    basic_results['excess_returns'] = basic_results['returns'] - basic_results[benchmark_return_col]
                    logger.info("   📊 Added excess returns column")

            basic_path = os.path.join(results_dir, 'basic_results.csv')
            basic_results.to_csv(basic_path)
            saved_files.append('basic_results.csv')
            logger.info(f"   ✅ Basic results: {len(basic_results)} rows, {len(basic_results.columns)} columns saved")

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

    def save_results_to_pickle(self, filename=None, results_dir='backtest_results'):
        """
        Save backtest results to a pickle file for later analysis.

        Parameters:
        -----------
        filename : str, optional
            Name of the pickle file. If None, generates a timestamp-based name.
        results_dir : str
            Directory to save the pickle file

        Returns:
        --------
        str: Path to the saved pickle file
        """
        logger.info("💾 SAVING BACKTEST RESULTS TO PICKLE FILE")
        logger.info("-" * 40)

        if self.results is None:
            logger.error("❌ No backtest results available. Run backtest first.")
            return None

        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            strategy_name = getattr(self.strategy, '__class__', type(self.strategy)).__name__
            filename = f"{strategy_name}_{timestamp}.pickle"

        # Ensure .pickle extension
        if not filename.endswith('.pickle') and not filename.endswith('.pkl'):
            filename += '.pickle'

        filepath = os.path.join(results_dir, filename)

        try:
            # Save the results DataFrame to pickle
            self.results.to_pickle(filepath)

            logger.info(f"✅ Results saved to pickle file: {filepath}")
            logger.info(f"📊 Data shape: {self.results.shape}")
            logger.info(f"📅 Date range: {self.results.index[0]} to {self.results.index[-1]}")
            logger.info(f"💾 File size: {os.path.getsize(filepath) / 1024:.2f} KB")

            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to save results to pickle: {str(e)}")
            return None

    def load_results_from_pickle(self, filepath):
        """
        Load backtest results from a pickle file.

        Parameters:
        -----------
        filepath : str
            Path to the pickle file

        Returns:
        --------
        pd.DataFrame: Loaded backtest results
        """
        logger.info(f"📂 LOADING BACKTEST RESULTS FROM PICKLE")
        logger.info(f"📁 File: {filepath}")

        try:
            if not os.path.exists(filepath):
                logger.error(f"❌ Pickle file not found: {filepath}")
                return None

            # Load the results
            results = pd.read_pickle(filepath)

            logger.info(f"✅ Results loaded successfully")
            logger.info(f"📊 Data shape: {results.shape}")
            logger.info(f"📅 Date range: {results.index[0]} to {results.index[-1]}")

            # Set the loaded results as current results
            self.results = results

            return results

        except Exception as e:
            logger.error(f"❌ Failed to load results from pickle: {str(e)}")
            return None

    def create_pyfolio_analysis_from_pickle(self, pickle_filepath, results_dir='pyfolio_analysis',
                                          live_start_date=None, save_plots=True, save_csv=True):
        """
        Create comprehensive Pyfolio analysis from a pickle file.
        This method replicates the example you provided.

        Parameters:
        -----------
        pickle_filepath : str
            Path to the pickle file containing backtest results
        results_dir : str
            Directory to save analysis results
        live_start_date : str or datetime, optional
            Date when live trading started (for out-of-sample analysis)
        save_plots : bool
            Whether to save plots as PNG files
        save_csv : bool
            Whether to save data as CSV files
        """
        logger.info("🚀 CREATING PYFOLIO ANALYSIS FROM PICKLE FILE")
        logger.info("=" * 50)
        logger.info(f"📁 Pickle file: {pickle_filepath}")
        logger.info(f"📊 Results directory: {results_dir}")

        # Load results from pickle
        perf = self.load_results_from_pickle(pickle_filepath)
        if perf is None:
            logger.error("❌ Failed to load pickle file. Cannot proceed with analysis.")
            return

        # Create results directory
        os.makedirs(results_dir, exist_ok=True)

        try:
            logger.info("🔍 Extracting returns, positions, and transactions from Zipline results...")

            # Extract data using pyfolio utility function
            returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)

            logger.info(f"📈 Returns data: {len(returns)} periods")
            logger.info(f"📊 Positions data: {len(positions) if positions is not None else 0} records")
            logger.info(f"💱 Transactions data: {len(transactions) if transactions is not None else 0} records")

            # Convert live_start_date if provided
            live_start_date_parsed = None
            if live_start_date:
                live_start_date_parsed = pd.Timestamp(live_start_date)
                logger.info(f"📅 Live start date for out-of-sample analysis: {live_start_date_parsed}")

            # 1. Create Full Tear Sheet
            logger.info("📊 Creating full tear sheet...")
            try:
                fig = pf.create_full_tear_sheet(
                    returns,
                    positions=positions,
                    transactions=transactions,
                    live_start_date=live_start_date_parsed,
                    return_fig=True
                )

                if save_plots and fig:
                    full_tearsheet_path = os.path.join(results_dir, 'full_tear_sheet.png')
                    fig.savefig(full_tearsheet_path, dpi=300, bbox_inches='tight')
                    logger.info(f"   ✅ Full tear sheet saved: {full_tearsheet_path}")

            except Exception as e:
                logger.warning(f"   ⚠️  Full tear sheet creation failed: {str(e)}")

            # 2. Create Round Trip Tear Sheet (Individual trades analysis)
            logger.info("🔄 Creating round trip tear sheet...")
            try:
                if transactions is not None and len(transactions) > 0:
                    fig = pf.create_round_trip_tear_sheet(
                        returns,
                        positions=positions,
                        transactions=transactions,
                        return_fig=True
                    )

                    if save_plots and fig:
                        round_trip_path = os.path.join(results_dir, 'round_trip_tear_sheet.png')
                        fig.savefig(round_trip_path, dpi=300, bbox_inches='tight')
                        logger.info(f"   ✅ Round trip tear sheet saved: {round_trip_path}")
                else:
                    logger.warning("   ⚠️  No transactions available for round trip analysis")

            except Exception as e:
                logger.warning(f"   ⚠️  Round trip tear sheet creation failed: {str(e)}")

            # 3. Save data to CSV files if requested
            if save_csv:
                logger.info("💾 Saving analysis data to CSV files...")

                try:
                    # Save returns
                    returns_path = os.path.join(results_dir, 'returns.csv')
                    returns.to_csv(returns_path)
                    logger.info(f"   ✅ Returns saved: {returns_path}")

                    # Save positions if available
                    if positions is not None and len(positions) > 0:
                        positions_path = os.path.join(results_dir, 'positions.csv')
                        positions.to_csv(positions_path)
                        logger.info(f"   ✅ Positions saved: {positions_path}")

                    # Save transactions if available
                    if transactions is not None and len(transactions) > 0:
                        transactions_path = os.path.join(results_dir, 'transactions.csv')
                        transactions.to_csv(transactions_path)
                        logger.info(f"   ✅ Transactions saved: {transactions_path}")

                except Exception as e:
                    logger.warning(f"   ⚠️  CSV saving failed: {str(e)}")

            logger.info("✅ PYFOLIO ANALYSIS COMPLETED SUCCESSFULLY!")
            logger.info(f"📁 All results saved to: {os.path.abspath(results_dir)}")

        except Exception as e:
            logger.error(f"❌ Pyfolio analysis failed: {str(e)}")
            logger.error("🔍 This might be due to insufficient data or incompatible data format")
            import traceback
            logger.error("📋 Stack Trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")

    def save_benchmark_analysis_to_csv(self, results_dir):
        """
        Extract and save comprehensive benchmark analysis metrics to CSV.

        This method extracts the key benchmark metrics you requested:
        - Alpha: Strategy's excess return vs benchmark, adjusted for risk
        - Beta: Strategy's sensitivity to benchmark movements
        - Benchmark returns: The benchmark's own returns
        - Excess return: Strategy return - benchmark return
        - Benchmark volatility: Standard deviation of benchmark returns
        """
        logger.info("📊 EXTRACTING BENCHMARK METRICS")
        logger.info("-" * 35)

        try:
            # Check if we have benchmark data in results
            benchmark_columns = [col for col in self.results.columns if 'benchmark' in col.lower()]

            if not benchmark_columns:
                logger.warning("⚠️  No benchmark data found in results")
                logger.info("💡 Ensure benchmark is set before running backtest")
                return

            # Extract key data
            strategy_returns = self.results['returns']
            portfolio_value = self.results['portfolio_value']

            # Find benchmark return column (Zipline typically names it 'benchmark_period_return')
            benchmark_return_col = None
            for col in self.results.columns:
                if 'benchmark' in col.lower() and 'return' in col.lower():
                    benchmark_return_col = col
                    break

            if benchmark_return_col is None:
                logger.warning("⚠️  Benchmark return column not found")
                logger.info(f"📊 Available columns: {list(self.results.columns)}")
                return

            benchmark_returns = self.results[benchmark_return_col]

            logger.info(f"✅ Found benchmark data in column: {benchmark_return_col}")
            logger.info(f"📊 Strategy returns: {len(strategy_returns)} periods")
            logger.info(f"📊 Benchmark returns: {len(benchmark_returns)} periods")

            # Calculate benchmark metrics
            benchmark_metrics = self._calculate_benchmark_metrics(
                strategy_returns, benchmark_returns, portfolio_value
            )

            # Save comprehensive benchmark analysis
            self._save_benchmark_metrics_to_csv(benchmark_metrics, results_dir)

            # Save time series data
            self._save_benchmark_timeseries_to_csv(
                strategy_returns, benchmark_returns, results_dir
            )

            logger.info("✅ Benchmark analysis completed successfully")

        except Exception as e:
            logger.error(f"❌ Benchmark analysis failed: {str(e)}")
            import traceback
            logger.error("📋 Stack Trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")

    def _calculate_benchmark_metrics(self, strategy_returns, benchmark_returns, portfolio_value):
        """
        Calculate comprehensive benchmark metrics
        """
        import numpy as np
        from scipy import stats

        logger.info("🔢 Calculating benchmark metrics...")

        # Align data (remove any NaN values)
        aligned_data = pd.DataFrame({
            'strategy': strategy_returns,
            'benchmark': benchmark_returns
        }).dropna()

        strategy_aligned = aligned_data['strategy']
        benchmark_aligned = aligned_data['benchmark']

        if len(strategy_aligned) < 10:
            logger.warning("⚠️  Insufficient data for reliable benchmark analysis")
            return {}

        # 1. Excess Returns (Strategy - Benchmark)
        excess_returns = strategy_aligned - benchmark_aligned

        # 2. Beta (sensitivity to benchmark movements)
        if benchmark_aligned.std() > 0:
            beta = np.cov(strategy_aligned, benchmark_aligned)[0, 1] / np.var(benchmark_aligned)
        else:
            beta = 0.0

        # 3. Alpha (risk-adjusted excess return)
        # Alpha = Strategy Return - (Risk-free rate + Beta * (Benchmark Return - Risk-free rate))
        # Assuming risk-free rate = 0 for simplicity
        mean_strategy_return = strategy_aligned.mean()
        mean_benchmark_return = benchmark_aligned.mean()
        alpha = mean_strategy_return - (beta * mean_benchmark_return)

        # 4. Benchmark Volatility
        benchmark_volatility = benchmark_aligned.std()

        # 5. Strategy Volatility
        strategy_volatility = strategy_aligned.std()

        # 6. Correlation
        correlation = strategy_aligned.corr(benchmark_aligned)

        # 7. Information Ratio (excess return / tracking error)
        tracking_error = excess_returns.std()
        information_ratio = excess_returns.mean() / tracking_error if tracking_error > 0 else 0

        # 8. Sharpe Ratios (assuming risk-free rate = 0)
        strategy_sharpe = mean_strategy_return / strategy_volatility if strategy_volatility > 0 else 0
        benchmark_sharpe = mean_benchmark_return / benchmark_volatility if benchmark_volatility > 0 else 0

        # 9. Annualized metrics (assuming daily data, 252 trading days)
        annualization_factor = np.sqrt(252)
        annual_alpha = alpha * 252
        annual_strategy_return = mean_strategy_return * 252
        annual_benchmark_return = mean_benchmark_return * 252
        annual_excess_return = excess_returns.mean() * 252
        annual_strategy_vol = strategy_volatility * annualization_factor
        annual_benchmark_vol = benchmark_volatility * annualization_factor
        annual_tracking_error = tracking_error * annualization_factor

        # 10. Downside metrics
        downside_strategy = strategy_aligned[strategy_aligned < 0]
        downside_benchmark = benchmark_aligned[benchmark_aligned < 0]
        downside_deviation_strategy = downside_strategy.std() if len(downside_strategy) > 0 else 0
        downside_deviation_benchmark = downside_benchmark.std() if len(downside_benchmark) > 0 else 0

        # 11. Maximum Drawdown comparison
        strategy_cumulative = (1 + strategy_aligned).cumprod()
        benchmark_cumulative = (1 + benchmark_aligned).cumprod()

        strategy_drawdown = (strategy_cumulative / strategy_cumulative.expanding().max() - 1).min()
        benchmark_drawdown = (benchmark_cumulative / benchmark_cumulative.expanding().max() - 1).min()

        # 12. Win rates
        strategy_win_rate = (strategy_aligned > 0).mean()
        benchmark_win_rate = (benchmark_aligned > 0).mean()
        excess_win_rate = (excess_returns > 0).mean()

        metrics = {
            # Core benchmark metrics (as requested)
            'Alpha (Daily)': alpha,
            'Alpha (Annualized)': annual_alpha,
            'Beta': beta,
            'Benchmark Returns (Mean Daily)': mean_benchmark_return,
            'Benchmark Returns (Annualized)': annual_benchmark_return,
            'Excess Return (Mean Daily)': excess_returns.mean(),
            'Excess Return (Annualized)': annual_excess_return,
            'Benchmark Volatility (Daily)': benchmark_volatility,
            'Benchmark Volatility (Annualized)': annual_benchmark_vol,

            # Additional useful metrics
            'Strategy Returns (Mean Daily)': mean_strategy_return,
            'Strategy Returns (Annualized)': annual_strategy_return,
            'Strategy Volatility (Daily)': strategy_volatility,
            'Strategy Volatility (Annualized)': annual_strategy_vol,
            'Correlation': correlation,
            'Information Ratio': information_ratio,
            'Tracking Error (Daily)': tracking_error,
            'Tracking Error (Annualized)': annual_tracking_error,
            'Strategy Sharpe Ratio': strategy_sharpe,
            'Benchmark Sharpe Ratio': benchmark_sharpe,
            'Strategy Max Drawdown': strategy_drawdown,
            'Benchmark Max Drawdown': benchmark_drawdown,
            'Strategy Win Rate': strategy_win_rate,
            'Benchmark Win Rate': benchmark_win_rate,
            'Excess Return Win Rate': excess_win_rate,
            'Downside Deviation Strategy': downside_deviation_strategy,
            'Downside Deviation Benchmark': downside_deviation_benchmark,
            'Observations': len(strategy_aligned),
            'Benchmark Symbol': self.benchmark_symbol
        }

        # Log key metrics
        logger.info(f"   📊 Alpha (Annualized): {annual_alpha:.4f} ({annual_alpha*100:.2f}%)")
        logger.info(f"   📊 Beta: {beta:.4f}")
        logger.info(f"   📊 Information Ratio: {information_ratio:.4f}")
        logger.info(f"   📊 Correlation: {correlation:.4f}")
        logger.info(f"   📊 Tracking Error: {annual_tracking_error:.4f} ({annual_tracking_error*100:.2f}%)")

        return metrics

    def _save_benchmark_metrics_to_csv(self, metrics, results_dir):
        """
        Save benchmark metrics to CSV file
        """
        logger.info("💾 Saving benchmark metrics to CSV...")

        try:
            # Convert metrics to DataFrame
            metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
            metrics_df.index.name = 'Metric'

            # Save to CSV
            metrics_path = os.path.join(results_dir, 'benchmark_metrics.csv')
            metrics_df.to_csv(metrics_path)

            logger.info(f"   ✅ Benchmark metrics saved: {metrics_path}")
            logger.info(f"   📊 Metrics saved: {len(metrics)} metrics")

        except Exception as e:
            logger.error(f"   ❌ Failed to save benchmark metrics: {str(e)}")

    def _save_benchmark_timeseries_to_csv(self, strategy_returns, benchmark_returns, results_dir):
        """
        Save time series comparison data to CSV
        """
        logger.info("💾 Saving benchmark time series data...")

        try:
            # Create comprehensive time series DataFrame
            timeseries_data = pd.DataFrame({
                'Date': strategy_returns.index,
                'Strategy_Returns': strategy_returns.values,
                'Benchmark_Returns': benchmark_returns.values,
                'Excess_Returns': (strategy_returns - benchmark_returns).values,
                'Strategy_Cumulative': (1 + strategy_returns).cumprod().values,
                'Benchmark_Cumulative': (1 + benchmark_returns).cumprod().values
            })

            # Calculate rolling metrics (30-day window)
            window = min(30, len(strategy_returns) // 4)  # Adaptive window size
            if window >= 5:
                timeseries_data['Strategy_Rolling_Vol'] = strategy_returns.rolling(window).std()
                timeseries_data['Benchmark_Rolling_Vol'] = benchmark_returns.rolling(window).std()
                timeseries_data['Rolling_Beta'] = strategy_returns.rolling(window).cov(benchmark_returns) / benchmark_returns.rolling(window).var()
                timeseries_data['Rolling_Correlation'] = strategy_returns.rolling(window).corr(benchmark_returns)

            # Set date as index
            timeseries_data.set_index('Date', inplace=True)

            # Save to CSV
            timeseries_path = os.path.join(results_dir, 'benchmark_timeseries.csv')
            timeseries_data.to_csv(timeseries_path)

            logger.info(f"   ✅ Time series data saved: {timeseries_path}")
            logger.info(f"   📊 Data points: {len(timeseries_data)} periods")
            logger.info(f"   📊 Columns: {list(timeseries_data.columns)}")

        except Exception as e:
            logger.error(f"   ❌ Failed to save time series data: {str(e)}")

if __name__ == '__main__':
    # This is an example of how to use the runner
    # You would import your strategy and run it here

    # from my_strategy import MyStrategy
    # strategy = MyStrategy()

    # runner = EnhancedZiplineRunner(strategy)
    # runner.run()
    # runner.analyze()
    pass
