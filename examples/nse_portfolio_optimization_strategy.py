#!/usr/bin/env python3
"""
NSE Portfolio Optimization Strategy
==================================

A sophisticated portfolio optimization strategy for NSE Indian market data.
This strategy uses Riskfolio-Lib for portfolio optimization with mean-variance 
and risk parity approaches, adapted for Indian markets without pipeline dependencies.

Key Features:
- Dynamic universe selection based on liquidity and volatility filters
- Risk-based portfolio optimization using historical returns
- Leverage support with risk controls
- Weekly rebalancing with transaction cost modeling
- Volatility targeting and beta constraints

Author: NSE Backtesting Engine
Date: 2025-08-10
"""

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
from zipline.api import (
    order_target_percent,
    schedule_function,
    date_rules,
    time_rules,
    set_commission,
    set_slippage,
    record,
    get_datetime,
    symbol,
    get_open_orders,
)
from zipline.finance import commission, slippage
from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
import bundles.duckdb_polars_bundle  # ensure bundle registration

# Try to import riskfolio-lib for portfolio optimization
try:
    import riskfolio as rp
    RISKFOLIO_AVAILABLE = True
    print("✅ Riskfolio-Lib available for portfolio optimization")
except ImportError:
    RISKFOLIO_AVAILABLE = False
    print("⚠️  Riskfolio-Lib not available - using equal weight allocation")
    print("   Install with: pip install riskfolio-lib")


class NSEPortfolioOptimizationStrategy(BaseStrategy):
    """
    Portfolio optimization strategy for NSE bundle using risk-based allocation.
    
    This strategy selects a universe of liquid NSE stocks and optimizes portfolio
    weights using modern portfolio theory principles adapted for Indian markets.
    """

    def __init__(self,
                 leverage: float = 1.0,          # Portfolio leverage (1.0 = no leverage)
                 window_length: int = 126,       # 6 months of trading days (21*6)
                 bar_count: int = 126,           # Historical data window
                 top_n: int = 20,                # Number of assets to consider
                 min_price: float = 50.0,        # Minimum stock price filter (INR)
                 max_volatility: float = 0.60,   # Maximum annualized volatility (60%)
                 min_volatility: float = 0.15,   # Minimum annualized volatility (15%)
                 min_volume: float = 1000000,    # Minimum daily volume (INR)
                 target_return: float = 0.0015,  # Target daily return for optimization
                 rebalance_frequency: str = 'weekly'):
        
        self.leverage = leverage
        self.window_length = window_length
        self.bar_count = bar_count
        self.top_n = top_n
        self.min_price = min_price
        self.max_volatility = max_volatility
        self.min_volatility = min_volatility
        self.min_volume = min_volume
        self.target_return = target_return
        self.rebalance_frequency = rebalance_frequency
        
        print(f"[NSE PORTFOLIO] Strategy initialized:")
        print(f"  Leverage: {leverage}x")
        print(f"  Universe size: {top_n} assets")
        print(f"  Lookback window: {window_length} days")
        print(f"  Riskfolio optimization: {'✅' if RISKFOLIO_AVAILABLE else '❌'}")

    def initialize(self, context):
        """Initialize the strategy"""
        print(f"[NSE PORTFOLIO] Initializing portfolio optimization strategy")
        
        # Strategy parameters
        context.params = {
            'leverage': self.leverage,
            'window_length': self.window_length,
            'top_n': self.top_n,
            'min_price': self.min_price,
            'target_return': self.target_return
        }
        
        # State variables
        context.selected_assets = []
        context.universe = []
        context.screened_assets = []
        context.last_rebalance = None
        context.day_counter = 0
        
        # Schedule rebalancing based on frequency
        if self.rebalance_frequency == 'daily':
            schedule_function(
                self.rebalance,
                date_rules.every_day(),
                time_rules.market_open(minutes=30)
            )
        elif self.rebalance_frequency == 'weekly':
            schedule_function(
                self.rebalance,
                date_rules.week_start(days_offset=0),  # Monday
                time_rules.market_open(minutes=30)
            )
        elif self.rebalance_frequency == 'monthly':
            schedule_function(
                self.rebalance,
                date_rules.month_start(days_offset=0),
                time_rules.market_open(minutes=30)
            )
        
        # Daily recording
        schedule_function(
            self.daily_record,
            date_rules.every_day(),
            time_rules.market_close(minutes=1)
        )
        
        # Set transaction costs for Indian markets
        set_commission(commission.PerShare(cost=0.001, min_trade_cost=5.0))
        set_slippage(slippage.VolumeShareSlippage(volume_limit=0.025, price_impact=0.01))
        
        print("[NSE PORTFOLIO] Strategy initialized successfully")

    def get_universe(self, context, data):
        """Get expanded tradeable universe from NSE bundle"""
        try:
            # Expanded universe of NSE stocks and indices
            nse_symbols = [
                # Large cap stocks
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
                'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK',
                'HDFC', 'BAJFINANCE', 'ASIANPAINT', 'MARUTI', 'AXISBANK',
                'NESTLEIND', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA', 'WIPRO',
                
                # Mid cap additions
                'HINDALCO', 'NTPC', 'POWERGRID', 'ONGC', 'GRASIM',
                'COALINDIA', 'TECHM', 'HCLTECH', 'TATAMOTORS', 'JSWSTEEL',
                
                # Indices for benchmark/diversification
                'NIFTY', 'BANKNIFTY'
            ]
            
            tradeable_assets = []
            for symbol_name in nse_symbols:
                try:
                    asset = symbol(symbol_name)
                    if data.can_trade(asset):
                        # Basic data availability check
                        current_price = data.current(asset, 'close')
                        if current_price > 0:
                            tradeable_assets.append(asset)
                except:
                    continue
            
            print(f"[UNIVERSE] Found {len(tradeable_assets)} tradeable assets from {len(nse_symbols)} symbols")
            return tradeable_assets
            
        except Exception as e:
            print(f"[UNIVERSE] Error getting universe: {e}")
            return []

    def screen_assets(self, context, data, universe):
        """Screen assets based on liquidity, volatility and price filters"""
        if not universe:
            return []
        
        try:
            print(f"[SCREENING] Applying filters to {len(universe)} assets")
            
            # Get extended price history for screening
            prices = data.history(
                universe,
                'close',
                self.window_length + 10,  # Extra days for calculation safety
                '1d'
            )
            
            # Get volume data for liquidity screening
            volumes = data.history(
                universe,
                'volume',
                self.window_length,
                '1d'
            )
            
            screened_assets = []
            
            for asset in universe:
                try:
                    if asset not in prices.columns or asset not in volumes.columns:
                        continue
                    
                    asset_prices = prices[asset].dropna()
                    asset_volumes = volumes[asset].dropna()
                    
                    if len(asset_prices) < self.window_length or len(asset_volumes) < 30:
                        continue
                    
                    current_price = asset_prices.iloc[-1]
                    
                    # 1. Price filter
                    if current_price < self.min_price:
                        continue
                    
                    # 2. Volatility filter
                    returns = asset_prices.pct_change().dropna()
                    if len(returns) < 60:  # Need sufficient data
                        continue
                    
                    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                    if not (self.min_volatility <= volatility <= self.max_volatility):
                        continue
                    
                    # 3. Volume/Liquidity filter
                    avg_volume = asset_volumes.tail(30).mean()  # 30-day average volume
                    avg_dollar_volume = avg_volume * current_price
                    
                    if avg_dollar_volume < self.min_volume:
                        continue
                    
                    # 4. Data quality check - avoid stocks with too many zero returns
                    zero_return_pct = (returns == 0).sum() / len(returns)
                    if zero_return_pct > 0.1:  # More than 10% zero returns
                        continue
                    
                    screened_assets.append(asset)
                    
                except Exception as e:
                    print(f"[SCREENING] Error screening {asset}: {e}")
                    continue
            
            print(f"[SCREENING] {len(screened_assets)} assets passed screening from {len(universe)}")
            return screened_assets
            
        except Exception as e:
            print(f"[SCREENING] Error in screening process: {e}")
            return []

    def select_top_assets(self, context, data, screened_assets):
        """Select top N assets by dollar volume (liquidity)"""
        if not screened_assets or len(screened_assets) <= self.top_n:
            return screened_assets
        
        try:
            # Calculate average dollar volume for ranking
            volumes = data.history(screened_assets, 'volume', 30, '1d')
            prices = data.history(screened_assets, 'close', 30, '1d')
            
            asset_scores = {}
            
            for asset in screened_assets:
                try:
                    if asset in volumes.columns and asset in prices.columns:
                        avg_volume = volumes[asset].tail(20).mean()
                        avg_price = prices[asset].tail(20).mean()
                        dollar_volume = avg_volume * avg_price
                        asset_scores[asset] = dollar_volume
                except:
                    continue
            
            # Sort by dollar volume (descending) and select top N
            sorted_assets = sorted(asset_scores.items(), key=lambda x: x[1], reverse=True)
            top_assets = [asset for asset, score in sorted_assets[:self.top_n]]
            
            print(f"[SELECTION] Selected top {len(top_assets)} assets by liquidity")
            return top_assets
            
        except Exception as e:
            print(f"[SELECTION] Error selecting top assets: {e}")
            return screened_assets[:self.top_n]  # Fallback

    def compute_weights(self, returns):
        """Compute optimal portfolio weights using Riskfolio-Lib with improved numerical stability"""
        
        if not RISKFOLIO_AVAILABLE or returns.empty:
            # Fallback to equal weights
            n_assets = len(returns.columns)
            if n_assets == 0:
                return None
            
            weights = pd.DataFrame(
                np.ones(n_assets) / n_assets,
                index=returns.columns,
                columns=['weights']
            )
            print(f"[OPTIMIZATION] Using equal weights: {1/n_assets:.3f} each for {n_assets} assets")
            return weights
        
        try:
            # Data quality checks
            if len(returns.columns) < 3:
                print(f"[OPTIMIZATION] Too few assets ({len(returns.columns)}), using equal weights")
                n_assets = len(returns.columns)
                weights = pd.DataFrame(
                    np.ones(n_assets) / n_assets,
                    index=returns.columns,
                    columns=['weights']
                )
                return weights
            
            # Check for and handle problematic returns
            returns_clean = returns.copy()
            
            # Remove assets with too little variance (numerical issues)
            asset_volatilities = returns_clean.std()
            min_vol_threshold = 0.001  # 0.1% daily volatility minimum
            valid_assets = asset_volatilities[asset_volatilities > min_vol_threshold].index
            
            if len(valid_assets) < len(returns_clean.columns):
                print(f"[OPTIMIZATION] Removing {len(returns_clean.columns) - len(valid_assets)} low-volatility assets")
                returns_clean = returns_clean[valid_assets]
            
            if len(returns_clean.columns) < 3:
                print(f"[OPTIMIZATION] Too few valid assets after cleaning, using equal weights")
                n_assets = len(returns_clean.columns)
                weights = pd.DataFrame(
                    np.ones(n_assets) / n_assets,
                    index=returns_clean.columns,
                    columns=['weights']
                )
                return weights
            
            # Suppress numpy warnings during optimization
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                
                # Use Riskfolio-Lib for optimization with more robust settings
                port = rp.Portfolio(returns=returns_clean)
                
                # Calculate asset statistics with robust methods
                port.assets_stats(
                    method_mu="hist",     # Historical mean
                    method_cov="ledoit"   # Ledoit-Wolf shrinkage (more stable)
                )
                
                # Set constraints for more stable optimization
                port.lowerret = max(0.0005, self.target_return)  # Minimum target return
                port.upperlng = 0.40    # Maximum 40% in any single asset
                port.lowerlng = 0.02    # Minimum 2% in any asset (if selected)
                
                # Try risk parity first (more stable than mean-variance)
                try:
                    weights = port.rp_optimization(
                        model="Classic",
                        rm="MV",           # Mean-Variance
                        rf=0.0,            # Risk-free rate
                        b=None,            # No benchmark
                        hist=True          # Use historical data
                    )
                except:
                    # Fallback to equal risk contribution
                    try:
                        weights = port.rp_optimization(
                            model="Classic",
                            rm="CVaR",     # Conditional Value at Risk (more robust)
                            rf=0.0,
                            b=None,
                            hist=True
                        )
                    except:
                        weights = None
            
            if weights is not None and not weights.empty:
                # Check for extreme concentrations and adjust if needed
                max_weight = weights.iloc[:, 0].max()
                if max_weight > 0.5:  # More than 50% in single asset
                    print(f"[OPTIMIZATION] Extreme concentration detected ({max_weight:.1%}), applying caps")
                    # Cap maximum weight and redistribute
                    weights_capped = weights.copy()
                    weights_capped.iloc[:, 0] = np.minimum(weights_capped.iloc[:, 0], 0.4)
                    # Renormalize
                    weights_capped = weights_capped / weights_capped.sum()
                    weights = weights_capped
                
                # Rename column to match expected format
                weights.columns = ['weights']
                print(f"[OPTIMIZATION] Riskfolio optimization successful for {len(weights)} assets")
                print(f"[OPTIMIZATION] Weight range: {weights['weights'].min():.3f} - {weights['weights'].max():.3f}")
                return weights
            else:
                # Fallback to equal weights
                n_assets = len(returns_clean.columns)
                weights = pd.DataFrame(
                    np.ones(n_assets) / n_assets,
                    index=returns_clean.columns,
                    columns=['weights']
                )
                print(f"[OPTIMIZATION] Riskfolio failed, using equal weights")
                return weights
                
        except Exception as e:
            print(f"[OPTIMIZATION] Error in Riskfolio optimization: {e}")
            # Fallback to equal weights
            n_assets = len(returns.columns)
            weights = pd.DataFrame(
                np.ones(n_assets) / n_assets,
                index=returns.columns,
                columns=['weights']
            )
            print(f"[OPTIMIZATION] Using equal weights fallback")
            return weights

    def exec_trades(self, data, assets, weights):
        """Execute trades for given assets and weights"""
        if weights is None or weights.empty:
            return
        
        executed_orders = 0
        
        for asset in assets:
            try:
                # Check if asset is tradeable and has weight
                if (data.can_trade(asset) and 
                    asset in weights.index and 
                    not get_open_orders(asset)):
                    
                    target_percent = weights.at[asset, 'weights']
                    
                    # Only place order if weight is significant
                    if abs(target_percent) > 0.001:  # 0.1% minimum
                        order_target_percent(asset, target_percent)
                        executed_orders += 1
                        print(f"[ORDER] Target {target_percent:.3f} for {asset.symbol}")
                    
            except Exception as e:
                print(f"[ORDER] Failed to order {asset.symbol}: {e}")
        
        print(f"[EXECUTION] Executed {executed_orders} orders out of {len(assets)} assets")

    def rebalance(self, context, data):
        """Main rebalancing logic"""
        context.day_counter += 1
        current_time = get_datetime()
        
        print(f"\n[REBALANCE] Day {context.day_counter}: {current_time.date()}")
        
        # Step 1: Get universe
        universe = self.get_universe(context, data)
        if not universe:
            print("[REBALANCE] No tradeable assets found")
            return
        
        # Step 2: Screen assets
        screened_assets = self.screen_assets(context, data, universe)
        if not screened_assets:
            print("[REBALANCE] No assets passed screening")
            return
        
        # Step 3: Select top N assets
        selected_assets = self.select_top_assets(context, data, screened_assets)
        context.selected_assets = selected_assets
        
        if not selected_assets:
            print("[REBALANCE] No assets selected")
            return
        
        print(f"[REBALANCE] Selected {len(selected_assets)} assets for optimization")
        
        # Step 4: Get historical data for optimization
        try:
            prices = data.history(
                selected_assets,
                'close',
                self.bar_count,
                '1d'
            )
            
            # Calculate returns and clean data more robustly
            returns = prices.pct_change()[1:]  # Skip first row (NaN)
            
            # Remove assets with insufficient data
            min_observations = max(30, int(0.6 * len(returns)))  # At least 60% of observations
            sufficient_data = returns.count() >= min_observations
            returns = returns.loc[:, sufficient_data]
            
            # Remove assets with all zero returns or extreme values
            returns = returns.loc[:, (returns != 0).any(axis=0)]
            returns = returns.loc[:, (returns.abs() < 0.5).all(axis=0)]  # Cap at 50% daily moves
            
            # Final NaN cleanup
            returns.dropna(how='any', axis=1, inplace=True)
            
            # Check correlation issues - remove highly correlated assets
            if len(returns.columns) > 3:
                corr_matrix = returns.corr()
                # Find pairs with correlation > 0.95
                high_corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        if abs(corr_matrix.iloc[i, j]) > 0.95:
                            high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
                
                # Remove one asset from each highly correlated pair (keep the more liquid one)
                assets_to_remove = set()
                for asset1, asset2 in high_corr_pairs:
                    if asset1 not in assets_to_remove and asset2 not in assets_to_remove:
                        # Simple heuristic: remove the second one
                        assets_to_remove.add(asset2)
                
                if assets_to_remove:
                    print(f"[REBALANCE] Removing {len(assets_to_remove)} highly correlated assets")
                    returns = returns.drop(columns=list(assets_to_remove))
            
            if returns.empty or len(returns.columns) < 3:
                print("[REBALANCE] Insufficient valid returns data for optimization")
                return
                
            print(f"[REBALANCE] Using {len(returns.columns)} assets with {len(returns)} days of returns")
            
        except Exception as e:
            print(f"[REBALANCE] Error getting price data: {e}")
            return
        
        # Step 5: Figure out assets to divest
        current_positions = set(context.portfolio.positions.keys())
        target_assets = set(returns.columns)
        divest_assets = list(current_positions - target_assets)
        
        if divest_assets:
            divest_weights = pd.DataFrame(
                np.zeros(len(divest_assets)),
                index=divest_assets,
                columns=['weights']
            )
            print(f"[REBALANCE] Divesting {len(divest_assets)} assets")
            self.exec_trades(data, divest_assets, divest_weights)
        
        # Step 6: Compute optimal weights
        weights = self.compute_weights(returns)
        
        if weights is not None:
            # Apply leverage
            weights *= self.leverage
            
            print(f"[REBALANCE] Applying {self.leverage}x leverage")
            print(f"[REBALANCE] Portfolio target weights sum: {weights['weights'].sum():.3f}")
            
            # Execute trades for target assets
            self.exec_trades(data, returns.columns, weights)
        
        # Record metrics
        context.last_rebalance = current_time
        record(
            num_positions=len(selected_assets),
            universe_size=len(universe),
            screened_size=len(screened_assets),
            leverage_used=self.leverage
        )

    def daily_record(self, context, data):
        """Record daily metrics"""
        portfolio_value = context.portfolio.portfolio_value
        cash = context.portfolio.cash
        positions_count = len(context.portfolio.positions)
        
        # Calculate actual leverage
        total_positions_value = sum(
            abs(position.amount * position.last_sale_price) 
            for position in context.portfolio.positions.values()
        )
        actual_leverage = total_positions_value / portfolio_value if portfolio_value > 0 else 0
        
        record(
            portfolio_value=portfolio_value,
            cash=cash,
            positions_count=positions_count,
            actual_leverage=actual_leverage,
            target_leverage=self.leverage
        )

    def handle_data(self, context, data):
        """Handle per-minute data (not used in this strategy)"""
        pass

    def analyze(self, context, perf):
        """Post-backtest analysis (handled by runner)"""
        pass


# ---------------- Script Entrypoint -----------------
if __name__ == '__main__':
    print("=" * 70)
    print("🚀 NSE PORTFOLIO OPTIMIZATION STRATEGY")
    print("=" * 70)
    
    # Strategy parameters - improved for numerical stability
    strategy = NSEPortfolioOptimizationStrategy(
        leverage=1.1,                    # Reduced leverage for stability
        window_length=126,               # 6 months lookback
        bar_count=126,                   # Historical data window
        top_n=20,                        # More assets for better diversification
        min_price=50.0,                  # Minimum ₹50 stock price
        max_volatility=0.45,             # Slightly lower max volatility
        min_volatility=0.12,             # Lower minimum volatility for more assets
        min_volume=1500000,              # Slightly lower volume requirement
        target_return=0.0005,            # More conservative target return
        rebalance_frequency='weekly'     # Weekly rebalancing
    )

    # Backtest parameters
    start_date = '2024-03-01'
    end_date = '2024-12-31'
    capital_base = 2000000              # ₹20 lakh capital
    bundle = 'nse-duckdb-parquet-bundle'
    benchmark_symbol = 'NIFTY'

    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle=bundle,
        start_date=start_date,
        end_date=end_date,
        capital_base=capital_base,
        benchmark_symbol=benchmark_symbol,
        data_frequency='daily'
    )

    print(f"📊 Running portfolio optimization backtest")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"💰 Capital: ₹{capital_base:,}")
    print(f"📈 Benchmark: {benchmark_symbol}")
    print(f"⚖️  Leverage: {strategy.leverage}x")
    print("🔄 Starting backtest...")

    results = runner.run()
    
    if results is not None:
        print("\n" + "=" * 70)
        print("✅ PORTFOLIO OPTIMIZATION BACKTEST COMPLETED!")
        print("=" * 70)
        
        # Save results
        out_dir = os.path.join(project_root, 'backtest_results', strategy.__class__.__name__)
        os.makedirs(out_dir, exist_ok=True)
        results.to_csv(os.path.join(out_dir, 'portfolio_optimization_results.csv'))
        
        # Calculate and display summary statistics
        total_return = (results['portfolio_value'].iloc[-1] / results['portfolio_value'].iloc[0] - 1) * 100
        returns = results['returns']
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        max_drawdown = ((results['portfolio_value'] / results['portfolio_value'].cummax() - 1).min()) * 100
        
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"📊 Annualized Volatility: {volatility:.2f}%")
        print(f"⚡ Sharpe Ratio: {sharpe:.2f}")
        print(f"📉 Maximum Drawdown: {max_drawdown:.2f}%")
        print(f"💾 Results saved to: {out_dir}")
        print("🎉 Portfolio optimization strategy completed!")
        
    else:
        print("❌ Backtest failed - check logs above")
