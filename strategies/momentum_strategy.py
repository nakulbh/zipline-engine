# momentum_strategy.py
import sys
import os

# Add the parent directory to Python path so we can import from engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.zipline_runner import TradingEngine
from engine.base_strategy import TradingConfig
import pandas as pd
import numpy as np
import pyfolio as pf
import matplotlib.pyplot as plt
from zipline.api import (
    order_target_percent, symbol, record, get_datetime,
    schedule_function, date_rules, time_rules
)

class MomentumStrategy:
    """
    A momentum strategy that:
    1. Calculates 20-day returns for a universe of stocks
    2. Goes long the top 5 performers
    3. Goes short the bottom 5 performers
    4. Rebalances monthly
    """
    
    def __init__(self, config):
        self.config = config
        self.lookback_days = 20
        self.num_long = 5
        self.num_short = 5
        
    def initialize(self, context):
        """Initialize the strategy"""
        print("Initializing Momentum Strategy...")
        
        # Define our universe of stocks (using symbols we know exist in our bundle)
        context.universe = [
            symbol('AAPL'), symbol('MSFT'), symbol('GOOGL'), symbol('AMZN'),
            symbol('TSLA'), symbol('META'), symbol('NVDA'), symbol('NFLX'),
            symbol('V'), symbol('MA'), symbol('JPM'), symbol('BAC'),
            symbol('JNJ'), symbol('PFE'), symbol('KO'), symbol('PEP'),
            symbol('WMT'), symbol('HD'), symbol('DIS'), symbol('XOM')
        ]
        
        # Add SPY as benchmark symbol
        context.spy = symbol('SPY')
        
        # Initialize tracking variables
        context.long_positions = []
        context.short_positions = []
        context.rebalance_count = 0
        
        # Schedule rebalancing function to run on the first trading day of each month
        schedule_function(
            self.rebalance,
            date_rules.month_start(),
            time_rules.market_open()
        )
        
        print(f"Strategy initialized with {len(context.universe)} stocks")
        print("SPY included as benchmark symbol")
        
    def before_trading_start(self, context, data):
        """Called before trading starts each day"""
        # Record SPY price for benchmark calculations
        if data.can_trade(context.spy):
            spy_price = data.current(context.spy, 'close')
            record(spy_price=spy_price)
        pass
        
    def rebalance(self, context, data):
        """Monthly rebalancing function"""
        context.rebalance_count += 1
        current_date = get_datetime()
        print(f"\n--- Rebalancing #{context.rebalance_count} on {current_date.date()} ---")
        
        # Calculate momentum scores
        momentum_scores = self.calculate_momentum(context, data)
        
        if momentum_scores is None or len(momentum_scores) < (self.num_long + self.num_short):
            print("Not enough data for rebalancing, skipping...")
            return
            
        # Sort by momentum (highest first)
        sorted_stocks = momentum_scores.sort_values(ascending=False)
        
        # Select long and short positions
        new_long_positions = sorted_stocks.head(self.num_long).index.tolist()
        new_short_positions = sorted_stocks.tail(self.num_short).index.tolist()
        
        print(f"Top {self.num_long} momentum stocks (LONG):")
        for i, stock in enumerate(new_long_positions, 1):
            momentum = sorted_stocks[stock]
            print(f"  {i}. {stock.symbol}: {momentum:.2%}")
            
        print(f"Bottom {self.num_short} momentum stocks (SHORT):")
        for i, stock in enumerate(new_short_positions, 1):
            momentum = sorted_stocks[stock]
            print(f"  {i}. {stock.symbol}: {momentum:.2%}")
        
        # Calculate position sizes
        long_weight = 0.8 / len(new_long_positions) if new_long_positions else 0
        short_weight = -0.2 / len(new_short_positions) if new_short_positions else 0
        
        # Close positions not in new portfolio
        all_new_positions = set(new_long_positions + new_short_positions)
        for stock in context.portfolio.positions:
            if stock not in all_new_positions:
                order_target_percent(stock, 0)
                print(f"  Closing position in {stock.symbol}")
        
        # Open long positions
        for stock in new_long_positions:
            if data.can_trade(stock):
                order_target_percent(stock, long_weight)
        
        # Open short positions  
        for stock in new_short_positions:
            if data.can_trade(stock):
                order_target_percent(stock, short_weight)
        
        # Update context
        context.long_positions = new_long_positions
        context.short_positions = new_short_positions
        
        # Record metrics
        record(
            num_long=len(new_long_positions),
            num_short=len(new_short_positions),
            leverage=context.account.leverage,
            portfolio_value=context.portfolio.portfolio_value
        )
        
    def calculate_momentum(self, context, data):
        """Calculate momentum scores for all stocks in universe"""
        momentum_scores = {}
        
        for stock in context.universe:
            try:
                # Get historical prices
                prices = data.history(stock, 'close', self.lookback_days + 1, '1d')
                
                if len(prices) >= self.lookback_days + 1:
                    # Calculate momentum as percentage return over lookback period
                    momentum = (prices.iloc[-1] / prices.iloc[0]) - 1
                    momentum_scores[stock] = momentum
                    
            except Exception as e:
                print(f"Error calculating momentum for {stock.symbol}: {e}")
                continue
        
        if momentum_scores:
            return pd.Series(momentum_scores)
        else:
            return None
            
    def handle_data(self, context, data):
        """Called every trading day"""
        # Record daily metrics
        record(
            portfolio_value=context.portfolio.portfolio_value,
            leverage=context.account.leverage,
            cash=context.portfolio.cash
        )

def run_momentum_strategy():
    """Run the momentum strategy backtest using engine's pyfolio integration"""
    
    # Create configuration
    config = TradingConfig(
        start_date="2020-01-01",
        end_date="2022-12-31",  # 3 years of data
        capital_base=100000.0,
        commission_cost=0.001,  # 0.1% commission
        output_dir="./backtest_results"
    )
    
    # Create strategy
    strategy = MomentumStrategy(config)
    
    # Create trading engine
    engine = TradingEngine(config)
    
    # Run backtest
    print("=" * 60)
    print("MOMENTUM STRATEGY BACKTEST WITH PYFOLIO ANALYSIS")
    print("=" * 60)
    print(f"Period: {config.start_date} to {config.end_date}")
    print(f"Initial Capital: ${config.capital_base:,.2f}")
    print(f"Commission: {config.commission_cost:.1%}")
    print("=" * 60)
    
    try:
        # Run the backtest
        print("Starting backtest...")
        backtest_results = engine.run_backtest(strategy)
        results = backtest_results['results']
        
        # Extract SPY benchmark data from the recorded results
        print("\n🔍 Extracting benchmark data (SPY) from backtest results...")
        benchmark_returns = None
        
        if 'spy_price' in results.columns:
            spy_prices = results['spy_price'].dropna()
            if len(spy_prices) > 1:
                benchmark_returns = spy_prices.pct_change().dropna()
                print(f"✅ Successfully extracted {len(benchmark_returns)} SPY benchmark returns from bundle data")
            else:
                print("⚠️ Warning: Insufficient SPY data in backtest results")
        else:
            print("⚠️ Warning: SPY data not found in backtest results, proceeding without benchmark")
        
        # Use engine's built-in performance analysis
        print("\n📊 Analyzing performance with engine's pyfolio integration...")
        performance = engine.analyze_performance(benchmark_returns)
        
        # Print summary statistics
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 60)
        
        summary = engine.get_summary_stats()
        for metric, value in summary.items():
            print(f"{metric:<25s}: {value}")
        
        # Print detailed performance metrics
        if benchmark_returns is not None:
            print(f"\nAlpha (vs SPY)          : {performance.get('alpha', 'N/A'):.4f}")
            print(f"Beta (vs SPY)           : {performance.get('beta', 'N/A'):.4f}")
        
        print("\n" + "=" * 60)
        print("📊 DETAILED PYFOLIO METRICS")
        print("=" * 60)
        
        # Display key performance statistics
        perf_stats = performance['performance_stats']
        for metric, value in perf_stats.items():
            if isinstance(value, (int, float)):
                if 'ratio' in metric.lower():
                    print(f"{metric:<30s}: {value:.3f}")
                elif 'return' in metric.lower() or 'volatility' in metric.lower():
                    print(f"{metric:<30s}: {value:.2%}")
                else:
                    print(f"{metric:<30s}: {value:.4f}")
            else:
                print(f"{metric:<30s}: {value}")
        
        # Generate comprehensive tearsheet using engine
        print("\n📋 Generating comprehensive pyfolio tearsheet...")
        try:
            engine.create_tearsheet(benchmark_returns)
            print("✅ Full tearsheet generated successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not generate full tearsheet: {e}")
            
            # Try creating basic plots as fallback
            try:
                print("📈 Creating basic performance plots as fallback...")
                
                import matplotlib.pyplot as plt
                import numpy as np
                import os
                os.makedirs('./backtest_results/figures', exist_ok=True)
                
                returns = engine.returns
                
                # Basic performance plot
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                
                # Cumulative returns
                cum_returns = (1 + returns).cumprod()
                axes[0,0].plot(cum_returns.index, cum_returns.values, label='Strategy')
                if benchmark_returns is not None:
                    cum_benchmark = (1 + benchmark_returns).cumprod()
                    axes[0,0].plot(cum_benchmark.index, cum_benchmark.values, 
                                  label='SPY Benchmark', alpha=0.7)
                    axes[0,0].legend()
                axes[0,0].set_title('Cumulative Returns')
                axes[0,0].set_ylabel('Cumulative Returns')
                
                # Daily returns
                axes[0,1].hist(returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
                axes[0,1].set_title('Daily Returns Distribution')
                axes[0,1].set_xlabel('Daily Returns')
                axes[0,1].set_ylabel('Frequency')
                
                # Rolling Sharpe (simplified)
                rolling_returns = returns.rolling(window=60).mean() * 252
                rolling_vol = returns.rolling(window=60).std() * np.sqrt(252)
                rolling_sharpe = rolling_returns / rolling_vol
                axes[1,0].plot(rolling_sharpe.index, rolling_sharpe.values)
                axes[1,0].set_title('Rolling Sharpe Ratio (60-day)')
                axes[1,0].set_ylabel('Sharpe Ratio')
                
                # Drawdown
                peak = cum_returns.expanding(min_periods=1).max()
                drawdown = (cum_returns / peak) - 1
                axes[1,1].fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
                axes[1,1].plot(drawdown.index, drawdown.values, color='red')
                axes[1,1].set_title('Drawdown')
                axes[1,1].set_ylabel('Drawdown')
                
                plt.tight_layout()
                plt.savefig('./backtest_results/figures/momentum_strategy_basic.png', dpi=300, bbox_inches='tight')
                print("💾 Saved basic performance plots to: ./backtest_results/figures/momentum_strategy_basic.png")
                plt.close()
                
            except Exception as plot_error:
                print(f"⚠️ Could not create fallback plots: {plot_error}")
        
        # Portfolio evolution summary
        print("\n" + "=" * 60)
        print("📈 PORTFOLIO EVOLUTION SUMMARY")
        print("=" * 60)
        
        portfolio_values = results.portfolio_value
        start_value = portfolio_values.iloc[0]
        end_value = portfolio_values.iloc[-1]
        total_return = (end_value / start_value) - 1
        
        print(f"Starting Portfolio Value: ${start_value:,.2f}")
        print(f"Ending Portfolio Value  : ${end_value:,.2f}")
        print(f"Total Return           : {total_return:.2%}")
        print(f"Total P&L              : ${end_value - start_value:,.2f}")
        
        # Monthly summary
        monthly_values = portfolio_values.resample('M').last()
        if len(monthly_values) > 1:
            monthly_returns = monthly_values.pct_change().dropna()
            
            print(f"\nMonthly Statistics:")
            print(f"Average Monthly Return : {monthly_returns.mean():.2%}")
            print(f"Monthly Volatility     : {monthly_returns.std():.2%}")
            print(f"Best Month             : {monthly_returns.max():.2%}")
            print(f"Worst Month            : {monthly_returns.min():.2%}")
            print(f"Positive Months        : {(monthly_returns > 0).sum()}/{len(monthly_returns)}")
        
        print("\n" + "=" * 60)
        print("✅ Strategy completed successfully with engine's pyfolio analysis!")
        print("📁 Check ./backtest_results/ for detailed results and figures")
        print("=" * 60)
        
        return engine, backtest_results, performance
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    engine, backtest_results, performance = run_momentum_strategy()
    
    if engine is not None:
        print(f"\nTest PASSED")
        print("🎉 Momentum strategy backtest completed successfully!")
    else:
        print(f"\nTest FAILED")
        print("❌ Momentum strategy backtest failed!")
