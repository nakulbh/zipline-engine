import os
import pandas as pd
import pyfolio as pf
import alphalens as al
from zipline import run_algorithm
from zipline.api import set_benchmark, symbol
from zipline.utils.calendar_utils import get_calendar
import matplotlib
matplotlib.use('Agg')  # Ensure headless backend so figures render when no display
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
    def __init__(self, strategy, bundle='quantopian-quandl', start_date='2015-1-1', end_date='2018-1-1', capital_base=100000, benchmark_symbol='NIFTY', data_frequency='minute', live_start_date=None):
        """
        Initialize the Enhanced Zipline Runner with comprehensive logging.

        Args:
            strategy: Trading strategy instance
            bundle: Data bundle name
            start_date: Backtest start date
            end_date: Backtest end date
            capital_base: Initial capital
            benchmark_symbol: Benchmark symbol for comparison
            data_frequency: 'daily' or 'minute'
            live_start_date: Date for live trading start in PyFolio tear sheet
        """
        self.strategy = strategy
        self.bundle = bundle
        # Use timezone-naive timestamps to avoid timezone parsing issues
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        
        # Validate dates against XBOM calendar
        calendar = get_calendar('XBOM')
        calendar_start = calendar.first_session
        calendar_end = calendar.last_session
        
        if self.start_date < calendar_start:
            logger.warning(f"⚠️  Start date {self.start_date} is before calendar start {calendar_start}. Adjusting to {calendar_start}")
            self.start_date = calendar_start
            
        if self.end_date > calendar_end:
            logger.warning(f"⚠️  End date {self.end_date} is after calendar end {calendar_end}. Adjusting to {calendar_end}")
            self.end_date = calendar_end
            
        if self.start_date >= self.end_date:
            raise ValueError(f"Start date {self.start_date} must be before end date {self.end_date}")
        
        self.capital_base = capital_base
        self.results = None
        self.benchmark_symbol = benchmark_symbol
        self.data_frequency = data_frequency
        self.live_start_date = live_start_date
        self.start_time = None
        self.end_time = None

        # Create a directory for the results
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'backtest_results',
            strategy.__class__.__name__
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # Log initialization
        logger.info("=" * 60)
        logger.info("🚀 ENHANCED ZIPLINE RUNNER INITIALIZED")
        logger.info("=" * 60)
        logger.info(f"📊 Strategy: {strategy.__class__.__name__}")
        logger.info(f"📦 Bundle: {bundle}")
        logger.info(f"📅 Period: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"💰 Capital: ${capital_base:,}")
        logger.info(f"📈 Benchmark: {benchmark_symbol}")
        logger.info(f"⏱️  Duration: {(self.end_date - self.start_date).days} days")
        logger.info(f"📂 Output Directory: {self.output_dir}")
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
                
                # WORKAROUND: Zipline-reloaded 3.1 has a bug where before_trading_start is never called
                # Schedule it manually to run at market open (before any other scheduled functions)
                def before_trading_start_scheduler(context, data):
                    logger.info("📅 Manual before_trading_start_scheduler called (workaround)")
                    logger.info(f"🗓️  Trading date: {data.current_dt}")
                    try:
                        if hasattr(self.strategy, 'before_trading_start'):
                            method_name = self.strategy.before_trading_start.__qualname__
                            logger.info(f"🔍 Calling method: {method_name}")
                            return self.strategy.before_trading_start(context, data)
                    except Exception as e:
                        logger.error(f"❌ Error in before_trading_start: {e}")
                        raise
                
                # Schedule before_trading_start to run at market open with highest priority
                from zipline.api import schedule_function, date_rules, time_rules
                schedule_function(
                    before_trading_start_scheduler,
                    date_rules.every_day(),
                    time_rules.market_open(minutes=1)  # Run 1 minute after market open (minimum allowed)
                )
                logger.info("🔧 Scheduled manual before_trading_start workaround")
                
                logger.info(f"🌐 Universe size: {len(context.universe) if hasattr(context, 'universe') else 'Unknown'}")

            def before_trading_start_wrapper(context, data):
                # This function is never called due to zipline-reloaded bug
                # Keeping it for documentation and potential future fixes
                logger.info("📅 before_trading_start_wrapper called!")
                logger.info(f"🗓️  Trading date: {data.current_dt}")
                method_name = self.strategy.before_trading_start.__qualname__
                logger.info(f"🔍 Method being called: {method_name}")
                try:
                    return self.strategy.before_trading_start(context, data)
                except Exception as e:
                    logger.error(f"❌ Error in before_trading_start: {e}")
                    raise

            # Log algorithm parameters
            logger.info("⚙️  Algorithm Configuration:")
            logger.info(f"   📅 Start Date: {self.start_date}")
            logger.info(f"   📅 End Date: {self.end_date}")
            logger.info(f"   💰 Capital Base: ${self.capital_base:,}")
            logger.info(f"   📦 Data Bundle: {self.bundle}")
            logger.info(f"   📊 Data Frequency: {self.data_frequency}")
            logger.info(f"   🗓️  Trading Calendar: XBOM (NSE/BSE)")

            logger.info("🚀 Launching Zipline algorithm...")

            self.results = run_algorithm(
                start=self.start_date,
                end=self.end_date,
                initialize=initialize_wrapper,
                handle_data=self.strategy.handle_data,
                # Note: before_trading_start is broken in zipline-reloaded 3.1
                # We implement it as a scheduled function in initialize_wrapper
                analyze=self.analyze,  # Pass the analyze method
                capital_base=self.capital_base,
                data_frequency=self.data_frequency,
                bundle=self.bundle,
                trading_calendar=get_calendar('XBOM'),
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

    def analyze(self, context, perf):
        """Robust PyFolio analysis that handles no-trade scenarios.
        - Extract Zipline results with error handling
        - Generate analysis only if trades occurred
        - Save core artifacts regardless
        """
        logger.info("📊 STARTING PERFORMANCE ANALYSIS (robust mode)...")
        logger.info("-" * 40)
        try:
            # Check if any trades occurred
            if 'transactions' not in perf.columns or perf['transactions'].apply(len).sum() == 0:
                logger.info("⚠️  No trades detected - skipping PyFolio analysis")
                logger.info("💾 Saving performance data only...")
                
                # Save basic performance data
                perf.to_csv(os.path.join(self.output_dir, 'performance_basic.csv'))
                
                # Create basic summary
                summary = {
                    'total_days': len(perf),
                    'final_value': perf['portfolio_value'].iloc[-1],
                    'total_return': (perf['portfolio_value'].iloc[-1] / self.capital_base - 1) * 100,
                    'trades_count': 0
                }
                
                with open(os.path.join(self.output_dir, 'summary.txt'), 'w') as f:
                    f.write("BACKTEST SUMMARY (No Trades)\n")
                    f.write("=" * 30 + "\n")
                    for key, value in summary.items():
                        f.write(f"{key}: {value}\n")
                
                logger.info("✅ ANALYSIS COMPLETED (no trades scenario)")
                return
            
            # Normal PyFolio analysis for strategies with trades
            returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)

            # Normalize index: make tz-naive (pyfolio expects naive)
            idx = returns.index
            if getattr(idx, 'tz', None) is not None:
                try:
                    returns.index = idx.tz_convert('UTC').tz_localize(None)
                except Exception:
                    returns.index = idx.tz_localize(None)
            else:
                returns.index = pd.DatetimeIndex(returns.index)

            # Save raw artifacts
            returns.to_csv(os.path.join(self.output_dir, 'returns.csv'))
            positions.to_csv(os.path.join(self.output_dir, 'positions.csv'))
            transactions.to_csv(os.path.join(self.output_dir, 'transactions.csv'))
            logger.info("💾 Saved returns/positions/transactions.")

            # Generate tear sheet WITHOUT live_start_date
            logger.info("📈 Generating PyFolio full tear sheet...")
            pf.create_full_tear_sheet(
                returns=returns,
                positions=positions,
                transactions=transactions,
                round_trips=False
            )

            # Save ALL figures
            fig_nums = plt.get_fignums()
            if fig_nums:
                figures_dir = os.path.join(self.output_dir, 'tear_sheet_figures')
                os.makedirs(figures_dir, exist_ok=True)
                saved_paths = []
                for i, fnum in enumerate(fig_nums, start=1):
                    fig = plt.figure(fnum)
                    png_path = os.path.join(figures_dir, f'tear_sheet_{i:02d}.png')
                    fig.savefig(png_path, bbox_inches='tight', dpi=180)
                    saved_paths.append(png_path)
                    logger.info(f"🖼️  Saved figure {i}/{len(fig_nums)} -> {png_path}")

                # Primary summary alias
                main_path = os.path.join(self.output_dir, 'full_tear_sheet.png')
                plt.figure(fig_nums[0]).savefig(main_path, bbox_inches='tight', dpi=180)
                logger.info(f"🖼️  Saved primary tear sheet alias -> {main_path}")

                # Multi-page PDF
                from matplotlib.backends.backend_pdf import PdfPages
                pdf_path = os.path.join(self.output_dir, 'full_tear_sheet.pdf')
                with PdfPages(pdf_path) as pdf:
                    for fnum in fig_nums:
                        pdf.savefig(plt.figure(fnum), bbox_inches='tight')
                logger.info(f"📄 Saved multi-page PDF -> {pdf_path}")

                # ZIP archive of PNGs
                import zipfile
                zip_path = os.path.join(self.output_dir, 'full_tear_sheet_figures.zip')
                with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                    for p in saved_paths:
                        zf.write(p, arcname=os.path.basename(p))
                logger.info(f"🗜️  Compressed figures -> {zip_path}")
            else:
                logger.warning("⚠️ No figures produced by pyfolio.")

            # Cache objects
            with open(os.path.join(self.output_dir, 'analysis_objects.pkl'), 'wb') as fh:
                pickle.dump({'returns': returns, 'positions': positions, 'transactions': transactions}, fh)

            plt.close('all')
            logger.info("✅ ANALYSIS COMPLETED SUCCESSFULLY (robust mode)")
            logger.info("-" * 40)
        except Exception as e:
            logger.error("❌ ANALYSIS FAILED (robust mode)!")
            logger.error(f"💥 Error: {e}")
            import traceback
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")
            try:
                plt.close('all')
            except Exception:
                pass
            # Don't re-raise to keep perf results available



