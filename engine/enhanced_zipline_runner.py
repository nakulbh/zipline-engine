"""
Enhanced Trading Engine with Advanced Analytics
Integrates zipline-reloaded, pyfolio-reloaded, and alphalens-reloaded
for comprehensive backtesting and analysis
"""

import os
import pandas as pd
import numpy as np
import pyfolio as pf
import alphalens as al
import warnings
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import json

# Zipline imports
from zipline import run_algorithm
from zipline.utils.calendar_utils import get_calendar
from zipline.data import bundles

# Custom imports
from .enhanced_base_strategy import BaseStrategy, TradingConfig, RiskMetrics

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTradingEngine:
    """
    Enhanced trading engine with comprehensive analysis capabilities
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.results = None
        self.returns = None
        self.positions = None
        self.transactions = None
        self.benchmark_returns = None
        
        # Analytics storage
        self.factor_data = {}
        self.alpha_factors = {}
        self.performance_stats = {}
        self.risk_metrics = RiskMetrics()
        
        # Create output directory structure
        self.setup_output_directories()
        
        # Setup logging
        logging.getLogger().setLevel(getattr(logging, config.log_level))
        
    def setup_output_directories(self):
        """Create comprehensive output directory structure"""
        base_dir = Path(self.config.output_dir)
        
        # Create subdirectories
        directories = [
            base_dir,
            base_dir / "figures",
            base_dir / "data",
            base_dir / "reports",
            base_dir / "tearsheets",
            base_dir / "factor_analysis",
            base_dir / "risk_analysis"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def run_backtest(self, strategy: BaseStrategy, 
                    bundle_name: str = 'nse-local-minute-bundle',
                    benchmark_symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Run enhanced backtest with comprehensive logging and analysis
        """
        logger.info("Starting enhanced backtest...")
        logger.info(f"Strategy: {strategy.__class__.__name__}")
        logger.info(f"Period: {self.config.start_date} to {self.config.end_date}")
        logger.info(f"Capital: ${self.config.capital_base:,.2f}")
        
        try:
            # Get appropriate calendar
            calendar = get_calendar("XBOM")  # NSE calendar
            
            # Store strategy reference for access to custom data
            self.strategy = strategy
            
            # Run zipline backtest
            results = run_algorithm(
                start=pd.Timestamp(self.config.start_date),
                end=pd.Timestamp(self.config.end_date),
                initialize=strategy.initialize,
                before_trading_start=strategy.before_trading_start,
                handle_data=strategy.handle_data,
                capital_base=self.config.capital_base,
                data_frequency=self.config.data_frequency,
                bundle=bundle_name,
                benchmark_returns=self.benchmark_returns,
                trading_calendar=calendar
            )
            
            # Store results
            self.results = results
            self.returns = results.returns
            self.positions = results.positions if hasattr(results, 'positions') else None
            self.transactions = results.transactions if hasattr(results, 'transactions') else None
            
            # Load benchmark if specified
            if benchmark_symbol:
                self.load_benchmark_returns(benchmark_symbol)
            
            logger.info("Backtest completed successfully")
            logger.info(f"Final portfolio value: ${results.portfolio_value.iloc[-1]:,.2f}")
            logger.info(f"Total return: {(results.portfolio_value.iloc[-1] / self.config.capital_base - 1):.2%}")
            
            # Save raw results
            if self.config.save_results:
                self.save_raw_results()
            
            return {
                'results': results,
                'returns': self.returns,
                'positions': self.positions,
                'transactions': self.transactions,
                'benchmark_returns': self.benchmark_returns
            }
            
        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def load_benchmark_returns(self, benchmark_symbol: str):
        """Load benchmark returns for comparison"""
        try:
            # This would typically load from your data bundle
            # For now, we'll create a simple benchmark
            logger.info(f"Loading benchmark returns for {benchmark_symbol}")
            # Implementation depends on your data source
            pass
        except Exception as e:
            logger.warning(f"Could not load benchmark returns: {e}")
    
    def analyze_performance(self, save_analysis: bool = True) -> Dict[str, Any]:
        """
        Comprehensive performance analysis using pyfolio-reloaded
        """
        if self.returns is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        logger.info("Analyzing performance with pyfolio-reloaded...")
        
        try:
            # Basic performance statistics
            perf_stats = pf.timeseries.perf_stats(
                self.returns, 
                factor_returns=self.benchmark_returns
            )
            
            # Additional metrics
            cum_returns = pf.timeseries.cum_returns(self.returns)
            
            # Risk metrics - using correct parameter names
            rolling_sharpe = pf.timeseries.rolling_sharpe(self.returns, rolling_sharpe_window=63)
            rolling_volatility = pf.timeseries.rolling_volatility(self.returns, rolling_vol_window=63)
            
            # Drawdown analysis with error handling
            try:
                drawdown = pf.timeseries.gen_drawdown_table(self.returns, top=10)
                # Handle NaT values in the drawdown table
                if not drawdown.empty:
                    for col in ['Peak date', 'Valley date', 'Recovery date']:
                        if col in drawdown.columns:
                            # Replace NaT with None to prevent formatting errors later
                            drawdown[col] = drawdown[col].where(~pd.isna(drawdown[col]), None)
            except Exception as e:
                logger.warning(f"Error generating drawdown table: {str(e)}")
                # Create an empty DataFrame with the expected structure
                drawdown = pd.DataFrame(columns=['Peak date', 'Valley date', 'Recovery date', 
                                               'Duration', 'Net drawdown in %'])
            
            # Performance analysis
            analysis = {
                'performance_stats': perf_stats,
                'cumulative_returns': cum_returns,
                'total_return': cum_returns.iloc[-1] if len(cum_returns) > 0 else 0.0,
                'annual_return': pf.timeseries.annual_return(self.returns),
                'annual_volatility': pf.timeseries.annual_volatility(self.returns),
                'sharpe_ratio': pf.timeseries.sharpe_ratio(self.returns),
                'max_drawdown': pf.timeseries.max_drawdown(self.returns),
                'calmar_ratio': pf.timeseries.calmar_ratio(self.returns),
                'sortino_ratio': pf.timeseries.sortino_ratio(self.returns),
                'rolling_sharpe': rolling_sharpe,
                'rolling_volatility': rolling_volatility,
                'drawdown_table': drawdown
            }
            
            # Add benchmark comparison if available
            if self.benchmark_returns is not None:
                analysis['alpha'] = pf.timeseries.alpha(self.returns, self.benchmark_returns)
                analysis['beta'] = pf.timeseries.beta(self.returns, self.benchmark_returns)
                analysis['information_ratio'] = pf.timeseries.excess_sharpe(self.returns, self.benchmark_returns)
            
            # Store analysis
            self.performance_stats = analysis
            
            logger.info("Performance analysis completed")
            self.print_performance_summary(analysis)
            
            # Save analysis
            if save_analysis and self.config.save_results:
                self.save_performance_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            raise
    
    def analyze_factors(self, factor_data: Optional[Dict[str, pd.DataFrame]] = None,
                       periods: Tuple[int, ...] = (1, 5, 10, 21)) -> Dict[str, Any]:
        """
        Analyze alpha factors using alphalens-reloaded
        """
        logger.info("Analyzing factors with alphalens-reloaded...")
        
        if factor_data is None:
            factor_data = self.extract_factor_data()
        
        if not factor_data:
            logger.warning("No factor data available for analysis")
            return {}
        
        try:
            factor_analysis = {}
            
            for factor_name, factor_df in factor_data.items():
                logger.info(f"Analyzing factor: {factor_name}")
                
                # Get pricing data (this would need to be implemented based on your data source)
                prices = self.get_pricing_data_for_factor_analysis(factor_df)
                
                if prices is None:
                    logger.warning(f"No pricing data available for factor {factor_name}")
                    continue
                
                # Clean factor data
                factor_data_clean = al.utils.get_clean_factor_and_forward_returns(
                    factor=factor_df.stack(),
                    prices=prices,
                    periods=periods,
                    quantiles=5,
                    max_loss=0.35  # Allow up to 35% data loss
                )
                
                # Factor analysis
                factor_stats = {
                    'factor_returns': al.performance.factor_returns(factor_data_clean),
                    'mean_return_by_quantile': al.performance.mean_return_by_quantile(
                        factor_data_clean, by_group=False
                    ),
                    'ic_table': al.performance.factor_information_coefficient(factor_data_clean),
                    'turnover_analysis': al.performance.quantile_turnover(factor_data_clean),
                    'factor_rank_autocorrelation': al.performance.factor_rank_autocorrelation(
                        factor_data_clean
                    )
                }
                
                factor_analysis[factor_name] = factor_stats
                
                # Generate factor tearsheet
                self.create_factor_tearsheet(factor_name, factor_data_clean)
            
            logger.info("Factor analysis completed")
            
            # Save factor analysis
            if self.config.save_results:
                self.save_factor_analysis(factor_analysis)
            
            return factor_analysis
            
        except Exception as e:
            logger.error(f"Factor analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    def extract_factor_data(self) -> Dict[str, pd.DataFrame]:
        """Extract factor data from strategy if available"""
        factor_data = {}
        
        # Check if strategy has factor data
        if hasattr(self.strategy, 'factor_data') and self.strategy.factor_data:
            factor_data = self.strategy.factor_data
        
        # Extract factors from results data if available
        if self.results is not None and hasattr(self.results, 'recorded_vars'):
            # Look for factor-related recorded variables
            for var_name, var_data in self.results.recorded_vars.items():
                if 'factor' in var_name.lower() or 'signal' in var_name.lower():
                    factor_data[var_name] = var_data
        
        return factor_data
    
    def get_pricing_data_for_factor_analysis(self, factor_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Get pricing data for factor analysis"""
        # This would need to be implemented based on your data source
        # For now, return None
        logger.warning("Pricing data extraction not implemented")
        return None
    
    def create_comprehensive_tearsheet(self, save_tearsheet: bool = True):
        """
        Create comprehensive tearsheet with multiple analysis views
        """
        if self.returns is None:
            raise ValueError("No backtest results available. Run backtest first.")
        
        logger.info("Creating comprehensive tearsheet...")
        
        try:
            # Set up the plotting environment
            plt.style.use('seaborn-v0_8')
            
            # Create comprehensive tearsheet
            fig = plt.figure(figsize=(20, 24))
            
            # Create pyfolio tearsheet with extra error handling for NaT values
            try:
                # Ensure we have clean data with no NaT values
                clean_returns = self.returns.copy()
                clean_returns = clean_returns[~clean_returns.index.isna()]
                
                if self.benchmark_returns is not None:
                    clean_benchmark = self.benchmark_returns.copy()
                    clean_benchmark = clean_benchmark[~clean_benchmark.index.isna()]
                else:
                    clean_benchmark = None
                    
                # Try to create the full tearsheet
                axes = pf.create_full_tear_sheet(
                    clean_returns,
                    benchmark_rets=clean_benchmark,
                    positions=self.positions,
                    transactions=self.transactions,
                    live_start_date=None,
                    return_fig=True
                )
                
                if save_tearsheet:
                    tearsheet_path = Path(self.config.output_dir) / "tearsheets" / "comprehensive_tearsheet.png"
                    plt.savefig(tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
                    logger.info(f"Comprehensive tearsheet saved to {tearsheet_path}")
                
            except Exception as tear_error:
                logger.warning(f"Full tearsheet creation failed: {tear_error}")
                plt.close('all')
                
                # Try with a simpler approach - returns tearsheet only
                try:
                    fig = plt.figure(figsize=(20, 16))
                    axes = pf.create_returns_tear_sheet(
                        self.returns, 
                        benchmark_rets=self.benchmark_returns,
                        return_fig=True
                    )
                    
                    if save_tearsheet:
                        tearsheet_path = Path(self.config.output_dir) / "tearsheets" / "returns_tearsheet.png"
                        plt.savefig(tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
                        logger.info(f"Returns tearsheet saved to {tearsheet_path}")
                        
                except Exception as e:
                    logger.warning(f"Returns tearsheet also failed: {e}")
            
            plt.close('all')
            
            # Create alternative tearsheet with custom metrics
            self.create_custom_tearsheet()
            
        except Exception as e:
            logger.error(f"Tearsheet creation failed: {str(e)}")
            try:
                # Fallback to simple tearsheet
                self.create_simple_tearsheet()
            except Exception as fallback_error:
                logger.error(f"Fallback tearsheet creation also failed: {fallback_error}")
                # Don't re-raise, just log the error and continue
                logger.error("Could not create any tearsheet. Continuing without visualization.")
    
    def create_custom_tearsheet(self):
        """Create custom tearsheet with additional analysis"""
        fig, axes = plt.subplots(4, 3, figsize=(20, 16))
        fig.suptitle('Custom Strategy Analysis', fontsize=16, fontweight='bold')
        
        # 1. Cumulative Returns
        cum_returns = pf.timeseries.cum_returns(self.returns)
        axes[0, 0].plot(cum_returns.index, cum_returns.values, linewidth=2)
        axes[0, 0].set_title('Cumulative Returns')
        axes[0, 0].set_ylabel('Cumulative Return')
        
        # 2. Rolling Sharpe Ratio
        rolling_sharpe = pf.timeseries.rolling_sharpe(self.returns, rolling_window=63)
        axes[0, 1].plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2)
        axes[0, 1].set_title('Rolling Sharpe Ratio (3M)')
        axes[0, 1].set_ylabel('Sharpe Ratio')
        axes[0, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # 3. Drawdown
        try:
            underwater = cum_returns / cum_returns.cummax() - 1
            axes[0, 2].fill_between(underwater.index, underwater.values, 0, alpha=0.3, color='red')
            axes[0, 2].set_title('Underwater Plot')
            axes[0, 2].set_ylabel('Drawdown')
            
            # Try to safely get drawdown table but don't use it directly
            try:
                drawdown = pf.timeseries.gen_drawdown_table(self.returns, top=1)
            except Exception:
                # Just log that we couldn't get the drawdown table but continue
                pass
        except Exception as e:
            logger.warning(f"Error creating underwater plot: {e}")
            axes[0, 2].text(0.5, 0.5, 'Underwater plot unavailable', 
                           ha='center', va='center', transform=axes[0, 2].transAxes)
            axes[0, 2].set_title('Underwater Plot')
        
        # 4. Monthly Returns Heatmap
        monthly_returns = pf.timeseries.aggregate_returns(self.returns, 'monthly')
        monthly_returns_table = pf.timeseries.monthly_returns_table(self.returns)
        sns.heatmap(monthly_returns_table, annot=True, fmt='.2%', cmap='RdYlGn', 
                   center=0, ax=axes[1, 0])
        axes[1, 0].set_title('Monthly Returns Heatmap')
        
        # 5. Rolling Volatility
        rolling_vol = pf.timeseries.rolling_volatility(self.returns, rolling_window=63)
        axes[1, 1].plot(rolling_vol.index, rolling_vol.values, linewidth=2)
        axes[1, 1].set_title('Rolling Volatility (3M)')
        axes[1, 1].set_ylabel('Volatility')
        
        # 6. Return Distribution
        axes[1, 2].hist(self.returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
        axes[1, 2].set_title('Daily Returns Distribution')
        axes[1, 2].set_xlabel('Daily Returns')
        axes[1, 2].set_ylabel('Frequency')
        axes[1, 2].axvline(x=0, color='red', linestyle='--', alpha=0.5)
        
        # 7. Top Drawdown Periods
        if len(self.returns) > 0:
            try:
                drawdown_table = pf.timeseries.gen_drawdown_table(self.returns, top=5)
                if not drawdown_table.empty:
                    # Create labels for drawdown periods that handle NaT values
                    labels = []
                    for idx, row in drawdown_table.iterrows():
                        peak_date = row.get('Peak date')
                        valley_date = row.get('Valley date')
                        
                        # Format dates safely
                        peak_str = "N/A" if pd.isna(peak_date) else peak_date.strftime('%Y-%m-%d')
                        valley_str = "N/A" if pd.isna(valley_date) else valley_date.strftime('%Y-%m-%d')
                        labels.append(f"{peak_str} to {valley_str}")
                    
                    # Plot drawdowns with safe labels
                    axes[2, 0].barh(range(len(drawdown_table)), drawdown_table['Net drawdown in %'])
                    axes[2, 0].set_yticks(range(len(drawdown_table)))
                    axes[2, 0].set_yticklabels(labels)
                    axes[2, 0].set_title('Top 5 Drawdown Periods')
                    axes[2, 0].set_ylabel('Drawdown Period')
                    axes[2, 0].set_xlabel('Drawdown (%)')
            except Exception as e:
                logger.warning(f"Could not create drawdown plot: {e}")
                axes[2, 0].text(0.5, 0.5, 'Drawdown plot unavailable', ha='center', va='center', transform=axes[2, 0].transAxes)
                axes[2, 0].set_title('Top 5 Drawdown Periods')
        
        # 8. Rolling Beta (if benchmark available)
        if self.benchmark_returns is not None:
            rolling_beta = pf.timeseries.rolling_beta(self.returns, self.benchmark_returns)
            axes[2, 1].plot(rolling_beta.index, rolling_beta.values, linewidth=2)
            axes[2, 1].set_title('Rolling Beta')
            axes[2, 1].set_ylabel('Beta')
            axes[2, 1].axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        else:
            axes[2, 1].text(0.5, 0.5, 'No benchmark data', ha='center', va='center', 
                          transform=axes[2, 1].transAxes)
            axes[2, 1].set_title('Rolling Beta (No Benchmark)')
        
        # 9. Exposure Analysis
        if self.positions is not None:
            # Calculate gross exposure over time
            gross_exposure = self.positions.abs().sum(axis=1)
            axes[2, 2].plot(gross_exposure.index, gross_exposure.values, linewidth=2)
            axes[2, 2].set_title('Gross Exposure Over Time')
            axes[2, 2].set_ylabel('Gross Exposure')
        
        # 10. Performance Summary Table
        perf_summary = self.get_performance_summary_table()
        axes[3, 0].axis('tight')
        axes[3, 0].axis('off')
        table_data = [[metric, value] for metric, value in perf_summary.items()]
        axes[3, 0].table(cellText=table_data, colLabels=['Metric', 'Value'], 
                        cellLoc='center', loc='center')
        axes[3, 0].set_title('Performance Summary')
        
        # 11. Transaction Analysis
        if self.transactions is not None and not self.transactions.empty:
            transaction_amounts = self.transactions['amount'].abs()
            axes[3, 1].hist(transaction_amounts, bins=30, alpha=0.7, edgecolor='black')
            axes[3, 1].set_title('Transaction Size Distribution')
            axes[3, 1].set_xlabel('Transaction Amount')
            axes[3, 1].set_ylabel('Frequency')
        
        # 12. Risk Metrics Over Time
        if len(self.returns) > 60:
            # Calculate 30-day rolling VaR
            rolling_var = self.returns.rolling(window=30).quantile(0.05)
            axes[3, 2].plot(rolling_var.index, rolling_var.values, linewidth=2, label='VaR 5%')
            axes[3, 2].set_title('30-Day Rolling VaR')
            axes[3, 2].set_ylabel('VaR')
            axes[3, 2].legend()
        
        plt.tight_layout()
        
        # Save custom tearsheet
        if self.config.save_results:
            custom_tearsheet_path = Path(self.config.output_dir) / "tearsheets" / "custom_tearsheet.png"
            plt.savefig(custom_tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Custom tearsheet saved to {custom_tearsheet_path}")
        
        plt.close()
    
    def create_simple_tearsheet(self):
        """Create simple tearsheet when full tearsheet fails"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Simple Strategy Analysis', fontsize=16, fontweight='bold')
        
        # Cumulative returns
        cum_returns = pf.timeseries.cum_returns(self.returns)
        axes[0, 0].plot(cum_returns.index, cum_returns.values, linewidth=2)
        axes[0, 0].set_title('Cumulative Returns')
        axes[0, 0].set_ylabel('Cumulative Return')
        
        # Drawdown
        underwater = cum_returns / cum_returns.cummax() - 1
        axes[0, 1].fill_between(underwater.index, underwater.values, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Underwater Plot')
        axes[0, 1].set_ylabel('Drawdown')
        
        # Returns distribution
        axes[1, 0].hist(self.returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Daily Returns Distribution')
        axes[1, 0].set_xlabel('Daily Returns')
        axes[1, 0].set_ylabel('Frequency')
        
        # Performance summary
        try:
            perf_summary = self.get_performance_summary_table()
            axes[1, 1].axis('tight')
            axes[1, 1].axis('off')
            table_data = [[metric, value] for metric, value in perf_summary.items()]
            axes[1, 1].table(cellText=table_data, colLabels=['Metric', 'Value'], 
                            cellLoc='center', loc='center')
            axes[1, 1].set_title('Performance Summary')
        except Exception as e:
            logger.warning(f"Error creating performance summary table: {e}")
            axes[1, 1].text(0.5, 0.5, 'Performance summary unavailable', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Performance Summary')
        
        plt.tight_layout()
        
        # Save simple tearsheet
        if self.config.save_results:
            simple_tearsheet_path = Path(self.config.output_dir) / "tearsheets" / "simple_tearsheet.png"
            plt.savefig(simple_tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Simple tearsheet saved to {simple_tearsheet_path}")
        
        plt.close()
    
    def create_factor_tearsheet(self, factor_name: str, factor_data_clean):
        """Create factor-specific tearsheet"""
        try:
            # Create factor tearsheet
            al.tears.create_full_tear_sheet(factor_data_clean, long_short=True)
            
            # Save factor tearsheet
            factor_tearsheet_path = Path(self.config.output_dir) / "factor_analysis" / f"{factor_name}_tearsheet.png"
            plt.savefig(factor_tearsheet_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Factor tearsheet for {factor_name} saved to {factor_tearsheet_path}")
            
        except Exception as e:
            logger.error(f"Factor tearsheet creation failed for {factor_name}: {e}")
    
    def get_performance_summary_table(self) -> Dict[str, str]:
        """Get formatted performance summary with error handling"""
        try:
            if self.performance_stats:
                # Get values safely with defaults if missing
                summary = {}
                metrics = [
                    ('Total Return', 'total_return', 0.0, '.2%'),
                    ('Annual Return', 'annual_return', 0.0, '.2%'),
                    ('Volatility', 'annual_volatility', 0.0, '.2%'),
                    ('Sharpe Ratio', 'sharpe_ratio', 0.0, '.3f'),
                    ('Max Drawdown', 'max_drawdown', 0.0, '.2%'),
                    ('Calmar Ratio', 'calmar_ratio', 0.0, '.3f'),
                    ('Sortino Ratio', 'sortino_ratio', 0.0, '.3f')
                ]
                
                for display_name, stat_key, default_val, format_str in metrics:
                    try:
                        if stat_key in self.performance_stats and not pd.isna(self.performance_stats[stat_key]):
                            val = self.performance_stats[stat_key]
                            summary[display_name] = f"{val:{format_str}}"
                        else:
                            summary[display_name] = f"{default_val:{format_str}}"
                    except Exception:
                        summary[display_name] = "N/A"
                
                return summary
            else:
                # Calculate basic stats with error handling
                summary = {}
                
                try:
                    cum_returns = pf.timeseries.cum_returns(self.returns)
                    total_return = cum_returns.iloc[-1] if len(cum_returns) > 0 else 0.0
                    summary['Total Return'] = f"{total_return:.2%}"
                except Exception:
                    summary['Total Return'] = "N/A"
                
                # Safely get other metrics
                metrics = [
                    ('Annual Return', lambda: pf.timeseries.annual_return(self.returns), '.2%'),
                    ('Volatility', lambda: pf.timeseries.annual_volatility(self.returns), '.2%'),
                    ('Sharpe Ratio', lambda: pf.timeseries.sharpe_ratio(self.returns), '.3f'),
                    ('Max Drawdown', lambda: pf.timeseries.max_drawdown(self.returns), '.2%'),
                    ('Calmar Ratio', lambda: pf.timeseries.calmar_ratio(self.returns), '.3f')
                ]
                
                for display_name, metric_func, format_str in metrics:
                    try:
                        val = metric_func()
                        if not pd.isna(val):
                            summary[display_name] = f"{val:{format_str}}"
                        else:
                            summary[display_name] = "N/A"
                    except Exception:
                        summary[display_name] = "N/A"
                
                return summary
                
        except Exception as e:
            logger.warning(f"Error creating performance summary table: {e}")
            return {
                'Total Return': "N/A",
                'Annual Return': "N/A",
                'Volatility': "N/A",
                'Sharpe Ratio': "N/A",
                'Max Drawdown': "N/A",
                'Calmar Ratio': "N/A"
            }
    
    def save_raw_results(self):
        """Save raw backtest results"""
        results_path = Path(self.config.output_dir) / "data" / "raw_results.pkl"
        self.results.to_pickle(results_path)
        logger.info(f"Raw results saved to {results_path}")
        
        # Save returns as CSV for easy access
        returns_csv_path = Path(self.config.output_dir) / "data" / "returns.csv"
        self.returns.to_csv(returns_csv_path)
        logger.info(f"Returns saved to {returns_csv_path}")
    
    def save_performance_analysis(self, analysis: Dict[str, Any]):
        """Save performance analysis"""
        analysis_path = Path(self.config.output_dir) / "data" / "performance_analysis.pkl"
        with open(analysis_path, 'wb') as f:
            pickle.dump(analysis, f)
        logger.info(f"Performance analysis saved to {analysis_path}")
    
    def save_factor_analysis(self, factor_analysis: Dict[str, Any]):
        """Save factor analysis"""
        factor_path = Path(self.config.output_dir) / "data" / "factor_analysis.pkl"
        with open(factor_path, 'wb') as f:
            pickle.dump(factor_analysis, f)
        logger.info(f"Factor analysis saved to {factor_path}")
    
    def generate_report(self, include_factor_analysis: bool = True):
        """Generate comprehensive HTML report"""
        logger.info("Generating comprehensive report...")
        
        # This would generate an HTML report with all analysis
        # For now, just create a summary
        report_data = {
            'strategy_name': self.strategy.__class__.__name__,
            'backtest_period': f"{self.config.start_date} to {self.config.end_date}",
            'initial_capital': self.config.capital_base,
            'final_value': self.results.portfolio_value.iloc[-1] if self.results is not None else 0,
            'performance_summary': self.get_performance_summary_table(),
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = Path(self.config.output_dir) / "reports" / "summary_report.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Summary report saved to {report_path}")
    
    def print_performance_summary(self, analysis: Dict[str, Any]):
        """Print performance summary to console"""
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        
        summary = self.get_performance_summary_table()
        for metric, value in summary.items():
            print(f"{metric:<20}: {value}")
        
        print("="*60)
        
        if 'drawdown_table' in analysis and not analysis['drawdown_table'].empty:
            print("\nTOP 5 DRAWDOWN PERIODS:")
            print("-"*40)
            dd_table = analysis['drawdown_table'].head()
            for idx, row in dd_table.iterrows():
                # Safely format each date, with extra protection against NaT values
                try:
                    peak_date = row.get('Peak date')
                    peak_str = "N/A" if pd.isna(peak_date) else str(peak_date.date())
                except Exception:
                    peak_str = "N/A"
                    
                try:
                    valley_date = row.get('Valley date')
                    valley_str = "N/A" if pd.isna(valley_date) else str(valley_date.date())
                except Exception:
                    valley_str = "N/A"
                    
                try:
                    recovery_date = row.get('Recovery date')
                    recovery_str = "N/A" if pd.isna(recovery_date) else str(recovery_date.date())
                except Exception:
                    recovery_str = "N/A"
                
                # Get drawdown percentage safely
                try:
                    net_drawdown = float(row.get('Net drawdown in %', 0.0))
                    drawdown_str = f"{net_drawdown:.2f}%"
                except Exception:
                    drawdown_str = "N/A"
                
                # Print drawdown information with completely safe handling of all fields
                print(f"Peak: {peak_str} | Valley: {valley_str} | Recovery: {recovery_str} | Drawdown: {drawdown_str}")
        
        print("\n")
    
    def run_complete_analysis(self, strategy: BaseStrategy, 
                            bundle_name: str = 'nse-local-minute-bundle'):
        """Run complete backtest and analysis workflow"""
        logger.info("Starting complete analysis workflow...")
        
        # 1. Run backtest
        backtest_results = self.run_backtest(strategy, bundle_name)
        
        # 2. Analyze performance
        performance_analysis = self.analyze_performance()
        
        # 3. Analyze factors (if enabled)
        if self.config.generate_factor_analysis:
            factor_analysis = self.analyze_factors()
        
        # 4. Create comprehensive tearsheet
        if self.config.generate_tearsheet:
            self.create_comprehensive_tearsheet()
        
        # 5. Generate report
        self.generate_report()
        
        logger.info("Complete analysis workflow finished!")
        logger.info(f"Results saved to: {self.config.output_dir}")
        
        return {
            'backtest_results': backtest_results,
            'performance_analysis': performance_analysis,
            'factor_analysis': factor_analysis if self.config.generate_factor_analysis else None
        }
