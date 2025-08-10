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
)
from zipline.finance import commission, slippage
from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
import bundles.duckdb_polars_bundle  # ensure bundle registration

class NSEMomentumStrategy(BaseStrategy):
    """
    Momentum strategy for NSE bundle using data.history() instead of pipelines.
    
    This approach bypasses all pipeline compatibility issues by directly accessing
    historical price data and calculating momentum factors manually.
    """

    def __init__(self,
                 top_n: int = 10,
                 lookback_days: int = 63,  # ~3 months
                 rebalance_frequency: str = 'weekly',  # 'daily', 'weekly', 'monthly'
                 min_price: float = 10.0,  # Minimum stock price filter
                 max_positions: int = 15):
        self.top_n = top_n
        self.lookback_days = lookback_days
        self.rebalance_frequency = rebalance_frequency
        self.min_price = min_price
        self.max_positions = max_positions

    def initialize(self, context):
        """Initialize the strategy"""
        print(f"[NSE MOMENTUM] Initializing strategy with {self.top_n} positions, {self.lookback_days} day lookback")
        
        # Strategy parameters
        context.params = {
            'top_n': self.top_n,
            'lookback_days': self.lookback_days,
            'min_price': self.min_price
        }
        
        # State variables
        context.selected_assets = []
        context.universe = []
        context.last_rebalance = None
        context.day_counter = 0
        
        # Schedule rebalancing
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
        
        # Set transaction costs
        set_commission(commission.PerShare(cost=0.001, min_trade_cost=1))  # Realistic for Indian markets
        set_slippage(slippage.FixedSlippage(spread=0.005))  # 0.5% slippage
        
        print("[NSE MOMENTUM] Strategy initialized successfully")

    def get_universe(self, context, data):
        """Get tradeable universe from the bundle - using known symbols approach"""
        try:
            # Use known symbols from NSE bundle instead of dynamic discovery
            known_symbols = ['BAJFINANCE', 'HDFCBANK', 'HDFC', 'HINDALCO', 
                           'RELIANCE', 'SBIN', 'BANKNIFTY', 'NIFTY']
            
            tradeable_assets = []
            for symbol_name in known_symbols:
                try:
                    asset = symbol(symbol_name)
                    if data.can_trade(asset):
                        # Try to get current price to ensure data availability
                        current_price = data.current(asset, 'close')
                        if current_price > 0:
                            tradeable_assets.append(asset)
                except:
                    continue
            
            print(f"[UNIVERSE] Found {len(tradeable_assets)} tradeable assets out of {len(known_symbols)} symbols")
            return tradeable_assets
        except Exception as e:
            print(f"[UNIVERSE] Error getting universe: {e}")
            import traceback
            traceback.print_exc()
            return []

    def calculate_momentum_scores(self, context, data, assets):
        """Calculate momentum scores for given assets using data.history()"""
        if not assets:
            return pd.Series(dtype=float)
        
        try:
            # Get price history for momentum calculation
            print(f"[MOMENTUM] Calculating momentum for {len(assets)} assets over {self.lookback_days} days")
            
            # Get daily price data
            prices = data.history(
                assets,
                'close',
                self.lookback_days + 5,  # Extra days for safety
                '1d'
            )
            
            print(f"[MOMENTUM] Retrieved price data: {prices.shape}")
            
            if prices.empty:
                print("[MOMENTUM] No price data available")
                return pd.Series(dtype=float)
            
            # Calculate momentum metrics
            momentum_scores = pd.Series(index=assets, dtype=float)
            
            for asset in assets:
                if asset not in prices.columns:
                    continue
                    
                asset_prices = prices[asset].dropna()
                
                if len(asset_prices) < self.lookback_days:
                    continue
                
                # Calculate multiple momentum metrics
                current_price = asset_prices.iloc[-1]
                
                # 1. Total return over lookback period
                start_price = asset_prices.iloc[0]
                if start_price > 0:
                    total_return = (current_price - start_price) / start_price
                else:
                    continue
                
                # 2. Price filter - exclude low-priced stocks
                if current_price < self.min_price:
                    continue
                
                # 3. Volatility-adjusted momentum (Sharpe-like)
                returns = asset_prices.pct_change().dropna()
                if len(returns) > 10:
                    volatility = returns.std()
                    if volatility > 0:
                        risk_adjusted_momentum = returns.mean() / volatility
                    else:
                        risk_adjusted_momentum = 0
                else:
                    risk_adjusted_momentum = 0
                
                # Combined momentum score
                momentum_score = total_return * 0.7 + risk_adjusted_momentum * 0.3
                momentum_scores[asset] = momentum_score
            
            # Remove invalid scores
            momentum_scores = momentum_scores.dropna()
            print(f"[MOMENTUM] Calculated scores for {len(momentum_scores)} assets")
            
            return momentum_scores
            
        except Exception as e:
            print(f"[MOMENTUM] Error calculating momentum: {e}")
            import traceback
            traceback.print_exc()
            return pd.Series(dtype=float)

    def select_assets(self, momentum_scores):
        """Select top momentum assets"""
        if momentum_scores.empty:
            return []
        
        # Sort by momentum score (descending) and select top N
        top_assets = momentum_scores.nlargest(min(self.top_n, len(momentum_scores)))
        selected = top_assets.index.tolist()
        
        print(f"[SELECTION] Selected {len(selected)} assets from {len(momentum_scores)} candidates")
        if len(selected) > 0:
            print(f"[SELECTION] Top 3 momentum scores: {top_assets.head(3).to_dict()}")
        
        return selected

    def rebalance(self, context, data):
        """Rebalance the portfolio based on momentum signals"""
        context.day_counter += 1
        current_time = get_datetime()
        
        print(f"\n[REBALANCE] Day {context.day_counter}: {current_time}")
        
        # Get current universe
        universe = self.get_universe(context, data)
        context.universe = [asset.symbol for asset in universe]
        
        if not universe:
            print("[REBALANCE] No tradeable assets found")
            return
        
        # Calculate momentum scores
        momentum_scores = self.calculate_momentum_scores(context, data, universe)
        
        # Select top momentum assets
        selected_assets = self.select_assets(momentum_scores)
        context.selected_assets = selected_assets
        
        if not selected_assets:
            print("[REBALANCE] No assets selected - liquidating portfolio")
            # Liquidate all positions
            for asset in context.portfolio.positions:
                if data.can_trade(asset):
                    order_target_percent(asset, 0)
            return
        
        # Calculate equal weights
        target_weight = 1.0 / len(selected_assets)
        selected_set = set(selected_assets)
        
        print(f"[REBALANCE] Targeting {len(selected_assets)} positions at {target_weight:.3f} each")
        
        # Place orders for selected assets
        for asset in selected_assets:
            if data.can_trade(asset):
                try:
                    order_target_percent(asset, target_weight)
                    print(f"[ORDER] Target {target_weight:.3f} for {asset.symbol}")
                except Exception as e:
                    print(f"[ORDER] Failed to order {asset.symbol}: {e}")
        
        # Liquidate positions not in current selection
        for asset in context.portfolio.positions:
            if asset not in selected_set and data.can_trade(asset):
                try:
                    order_target_percent(asset, 0)
                    print(f"[ORDER] Liquidating {asset.symbol}")
                except Exception as e:
                    print(f"[ORDER] Failed to liquidate {asset.symbol}: {e}")
        
        context.last_rebalance = current_time
        record(
            num_positions=len(selected_assets),
            universe_size=len(universe)
        )

    def daily_record(self, context, data):
        """Record daily metrics"""
        portfolio_value = context.portfolio.portfolio_value
        cash = context.portfolio.cash
        positions_count = len(context.portfolio.positions)
        
        record(
            portfolio_value=portfolio_value,
            cash=cash,
            positions_count=positions_count,
            leverage=getattr(context.account, 'leverage', 0)
        )

    def handle_data(self, context, data):
        """Handle per-minute data (not used in this strategy)"""
        pass

    def analyze(self, context, perf):
        """Post-backtest analysis (handled by runner)"""
        pass


# ---------------- Script Entrypoint -----------------
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NSE MOMENTUM STRATEGY (Non-Pipeline Version)")
    print("=" * 60)
    
    # Strategy parameters
    strategy = NSEMomentumStrategy(
        top_n=10,                    # Number of positions
        lookback_days=63,            # ~3 months momentum period  
        rebalance_frequency='weekly', # Rebalance frequency
        min_price=20.0,             # Minimum stock price (INR)
        max_positions=15            # Maximum positions
    )

    # Backtest parameters
    start_date = '2024-03-01'  # Start after some data is available
    end_date = '2024-12-31'    # Full year of testing
    capital_base = 1000000     # 10 Lakh INR
    bundle = 'nse-duckdb-parquet-bundle'
    benchmark_symbol = 'NIFTY'

    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle=bundle,
        start_date=start_date,
        end_date=end_date,
        capital_base=capital_base,
        benchmark_symbol=benchmark_symbol,
        data_frequency='daily'  # Use daily for momentum strategy
    )

    print(f"📊 Running backtest from {start_date} to {end_date}")
    print(f"💰 Capital: ₹{capital_base:,}")
    print(f"📈 Benchmark: {benchmark_symbol}")
    print("🔄 Starting backtest...")

    results = runner.run()
    
    if results is not None:
        print("\n" + "=" * 60)
        print("✅ BACKTEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Save results
        out_dir = os.path.join(project_root, 'backtest_results', strategy.__class__.__name__)
        os.makedirs(out_dir, exist_ok=True)
        results.to_csv(os.path.join(out_dir, 'backtest_results.csv'))
        
        # Print summary statistics
        total_return = (results['portfolio_value'].iloc[-1] / results['portfolio_value'].iloc[0] - 1) * 100
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"💾 Results saved to: {out_dir}")
        print("🎉 Strategy completed successfully!")
        
    else:
        print("❌ Backtest failed - check logs above")
