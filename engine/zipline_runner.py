import os
import pandas as pd
import numpy as np
import pyfolio as pf
import alphalens as al
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

# Zipline imports
from zipline import run_algorithm
from zipline.api import (
    order_target_percent, record, symbol, get_datetime,
    schedule_function, date_rules, time_rules, get_open_orders,
    cancel_order, order, order_target, get_order
)
from zipline.finance import commission, slippage
from zipline.pipeline import Pipeline, CustomFactor
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import (
    SimpleMovingAverage, RSI, Returns, AverageDollarVolume
)
from zipline.utils.events import date_rules, time_rules
from zipline.utils.calendar_utils import get_calendar 
from .base_strategy import BaseStrategy, TradingConfig

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingEngine:
    """
    Main trading engine that orchestrates backtesting and analysis
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.results = None
        self.returns = None
        self.positions = None
        self.transactions = None
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Setup logging
        logging.getLogger().setLevel(getattr(logging, config.log_level))
    
    def run_backtest(self, strategy: BaseStrategy) -> Dict[str, Any]:
        """
        Run backtest with given strategy
        """
        logger.info("Starting backtest...")
        
        try:

            calendar = get_calendar("XBOM")
            # Run zipline backtest
            results = run_algorithm(
                start=pd.Timestamp(self.config.start_date),
                end=pd.Timestamp(self.config.end_date),
                initialize=strategy.initialize,
                before_trading_start=strategy.before_trading_start,
                capital_base=self.config.capital_base,
                data_frequency=self.config.data_frequency,
                bundle='nse-local-minute-bundle',  # Use our custom NSE bundle
                benchmark_returns=None,  # Will be set automatically
                trading_calendar=calendar
            )
            
            self.results = results
            self.returns = results.returns
            self.positions = results.positions if hasattr(results, 'positions') else None
            self.transactions = results.transactions if hasattr(results, 'transactions') else None
            
            logger.info("Backtest completed successfully")
            
            # Save raw results if configured
            if self.config.save_results:
                results_path = os.path.join(self.config.output_dir, "raw_results.pkl")
                results.to_pickle(results_path)
                logger.info(f"Raw results saved to {results_path}")
            
            return {
                'results': results,
                'returns': self.returns,
                'positions': self.positions,
                'transactions': self.transactions
            }
            
        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}")
            raise
    
    def analyze_performance(self, benchmark_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        Analyze performance using pyfolio
        """
        if self.returns is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        logger.info("Analyzing performance with pyfolio...")
        
        try:
            # Create pyfolio tear sheet
            if benchmark_returns is not None:
                perf_stats = pf.timeseries.perf_stats(
                    self.returns, 
                    factor_returns=benchmark_returns
                )
            else:
                perf_stats = pf.timeseries.perf_stats(self.returns)
            
            # Calculate additional metrics
            cum_returns = pf.timeseries.cum_returns(self.returns)
            total_return = cum_returns.iloc[-1] if len(cum_returns) > 0 else 0.0
            
            analysis = {
                'performance_stats': perf_stats,
                'total_return': total_return,
                'annual_return': pf.timeseries.annual_return(self.returns),
                'annual_volatility': pf.timeseries.annual_volatility(self.returns),
                'sharpe_ratio': pf.timeseries.sharpe_ratio(self.returns),
                'max_drawdown': pf.timeseries.max_drawdown(self.returns),
                'calmar_ratio': pf.timeseries.calmar_ratio(self.returns),
            }
            
            # Add benchmark comparison if available
            if benchmark_returns is not None:
                analysis['alpha'] = pf.timeseries.alpha(self.returns, benchmark_returns)
                analysis['beta'] = pf.timeseries.beta(self.returns, benchmark_returns)
            
            logger.info("Performance analysis completed")
            
            # Save analysis if configured
            if self.config.save_results:
                analysis_path = os.path.join(self.config.output_dir, "performance_analysis.pkl")
                pd.Series(analysis).to_pickle(analysis_path)
                logger.info(f"Performance analysis saved to {analysis_path}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            raise
    
    def analyze_factors(self, factor_data: pd.DataFrame, 
                       prices: pd.DataFrame, 
                       periods: Tuple[int, ...] = (1, 5, 10)) -> Dict[str, Any]:
        """
        Analyze alpha factors using alphalens
        """
        logger.info("Analyzing factors with alphalens...")
        
        try:
            # Create alphalens factor data format
            factor_data_clean = al.utils.get_clean_factor_and_forward_returns(
                factor=factor_data,
                prices=prices,
                periods=periods,
                quantiles=5
            )
            
            # Generate factor analysis
            analysis = {
                'factor_returns': al.performance.factor_returns(factor_data_clean),
                'mean_return_by_quantile': al.performance.mean_return_by_quantile(factor_data_clean),
                'ic': al.performance.factor_information_coefficient(factor_data_clean),
                'turnover': al.performance.quantile_turnover(factor_data_clean),
            }
            
            logger.info("Factor analysis completed")
            
            # Save factor analysis if configured
            if self.config.save_results:
                factor_path = os.path.join(self.config.output_dir, "factor_analysis.pkl")
                pd.Series(analysis).to_pickle(factor_path)
                logger.info(f"Factor analysis saved to {factor_path}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Factor analysis failed: {str(e)}")
            raise
    
    def create_tearsheet(self, benchmark_returns: Optional[pd.Series] = None):
        """
        Create comprehensive pyfolio tearsheet and save to results folder
        """
        if self.returns is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        logger.info("Creating pyfolio tearsheet...")
        
        try:
            import matplotlib.pyplot as plt
            
            # Create figures directory if it doesn't exist
            figures_dir = os.path.join(self.config.output_dir, "figures")
            os.makedirs(figures_dir, exist_ok=True)
            
            # Create full tear sheet and save to file
            tearsheet_path = os.path.join(figures_dir, "pyfolio_tearsheet.png")
            
            # Set matplotlib backend to save figure without displaying
            plt.ioff()  # Turn off interactive mode
            
            # Create the tearsheet
            pf.create_full_tear_sheet(
                self.returns,
                benchmark_rets=benchmark_returns,
                positions=self.positions,
                transactions=self.transactions,
                live_start_date=None,  # For out-of-sample analysis if needed
            )
            
            # Save the current figure
            plt.savefig(tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close('all')  # Close all figures to free memory
            plt.ion()  # Turn interactive mode back on
            
            logger.info(f"Tearsheet saved to {tearsheet_path}")
            
        except Exception as e:
            logger.error(f"Tearsheet creation failed: {str(e)}")
            # Try alternative approach with individual plots
            try:
                self._create_alternative_tearsheet(benchmark_returns)
            except Exception as alt_error:
                logger.error(f"Alternative tearsheet creation also failed: {alt_error}")
                raise e
    
    def _create_alternative_tearsheet(self, benchmark_returns: Optional[pd.Series] = None):
        """
        Create alternative tearsheet with individual plots when full tearsheet fails
        """
        import matplotlib.pyplot as plt
        
        figures_dir = os.path.join(self.config.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        # Create individual plots
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('Strategy Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Cumulative Returns
        pf.plotting.plot_returns(self.returns, live_start_date=None, ax=axes[0,0])
        if benchmark_returns is not None:
            cum_benchmark = (1 + benchmark_returns).cumprod()
            axes[0,0].plot(cum_benchmark.index, cum_benchmark.values, 
                          label='Benchmark', alpha=0.7, color='gray')
            axes[0,0].legend()
        axes[0,0].set_title('Cumulative Returns')
        
        # 2. Rolling Sharpe
        pf.plotting.plot_rolling_sharpe(self.returns, ax=axes[0,1])
        axes[0,1].set_title('Rolling Sharpe Ratio (6M)')
        
        # 3. Drawdown
        pf.plotting.plot_drawdown_underwater(self.returns, ax=axes[1,0])
        axes[1,0].set_title('Underwater Plot (Drawdowns)')
        
        # 4. Monthly Returns Heatmap
        pf.plotting.plot_monthly_returns_heatmap(self.returns, ax=axes[1,1])
        axes[1,1].set_title('Monthly Returns Heatmap')
        
        # 5. Returns Distribution
        axes[2,0].hist(self.returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
        axes[2,0].set_title('Daily Returns Distribution')
        axes[2,0].set_xlabel('Daily Returns')
        axes[2,0].set_ylabel('Frequency')
        
        # 6. Rolling Volatility
        pf.plotting.plot_rolling_volatility(self.returns, ax=axes[2,1])
        axes[2,1].set_title('Rolling Volatility (6M)')
        
        plt.tight_layout()
        
        # Save the alternative tearsheet
        alt_tearsheet_path = os.path.join(figures_dir, "alternative_tearsheet.png")
        plt.savefig(alt_tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        logger.info(f"Alternative tearsheet saved to {alt_tearsheet_path}")
    
    def get_summary_stats(self) -> Dict[str, str]:
        """Get summary statistics for quick review"""
        if self.returns is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        # Calculate cumulative returns and get the final value
        cum_returns = pf.timeseries.cum_returns(self.returns)
        total_return = cum_returns.iloc[-1] if len(cum_returns) > 0 else 0.0
        
        return {
            'Total Return': f"{total_return:.2%}",
            'Annual Return': f"{pf.timeseries.annual_return(self.returns):.2%}",
            'Annual Volatility': f"{pf.timeseries.annual_volatility(self.returns):.2%}",
            'Sharpe Ratio': f"{pf.timeseries.sharpe_ratio(self.returns):.3f}",
            'Max Drawdown': f"{pf.timeseries.max_drawdown(self.returns):.2%}",
            'Calmar Ratio': f"{pf.timeseries.calmar_ratio(self.returns):.3f}",
        }