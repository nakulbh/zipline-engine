import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

from zipline.api import symbol, record, schedule_function, date_rules, time_rules
import numpy as np

# Import bundle to register it
import bundles.duckdb_polars_bundle

class IndianMarketScheduleStrategy(BaseStrategy):
    """
    SMA Strategy with Indian Market Optimized Scheduling
    
    This strategy demonstrates practical scheduling for Indian markets:
    - Pre-market analysis
    - Opening momentum
    - Mid-day rebalancing
    - End-of-day position management
    """

    def __init__(self, short_window=20, long_window=50, assets=None):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.assets = assets if assets else ['NIFTY', 'ACC']
        
        # Strategy state
        self.morning_signals = {}
        self.risk_alert = False

    def _setup_schedules(self):
        """
        Indian Market Optimized Scheduling
        
        NSE Trading Hours: 9:15 AM - 3:30 PM IST
        """
        
        # 1. PRE-MARKET ANALYSIS (9:00 AM - before market open)
        schedule_function(
            func=self.pre_market_prep,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(minutes=-15)  # 9:00 AM
        )
        
        # 2. OPENING MOMENTUM (9:15 AM - market open)
        schedule_function(
            func=self.opening_strategy,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open()  # 9:15 AM
        )
        
        # 3. MAIN REBALANCING (10:30 AM - after opening volatility settles)
        schedule_function(
            func=self.main_rebalance,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(hours=1, minutes=15)  # 10:30 AM
        )
        
        # 4. WEEKLY MOMENTUM CHECK (Every Monday at 11:00 AM)
        schedule_function(
            func=self.weekly_momentum_check,
            date_rule=date_rules.week_start(),  # Mondays only
            time_rule=time_rules.market_open(hours=1, minutes=45)  # 11:00 AM
        )
        
        # 5. LUNCH TIME RISK CHECK (12:30 PM)
        schedule_function(
            func=self.midday_risk_check,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(hours=3, minutes=15)  # 12:30 PM
        )
        
        # 6. AFTERNOON REBALANCING (2:00 PM)
        schedule_function(
            func=self.afternoon_rebalance,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_open(hours=4, minutes=45)  # 2:00 PM
        )
        
        # 7. END-OF-DAY POSITION MANAGEMENT (3:15 PM - 15 min before close)
        schedule_function(
            func=self.eod_position_management,
            date_rule=date_rules.every_day(),
            time_rule=time_rules.market_close(minutes=15)  # 3:15 PM
        )
        
        # 8. MONTHLY REBALANCING (First Monday of every month)
        schedule_function(
            func=self.monthly_portfolio_review,
            date_rule=date_rules.month_start(),
            time_rule=time_rules.market_open(hours=2)  # 11:15 AM on first trading day
        )

    def pre_market_prep(self, context, data):
        """Pre-market analysis and preparation"""
        record(pre_market_prep=True)
        
        # Reset daily flags
        self.risk_alert = False
        self.morning_signals = {}
        
        # Log pre-market preparation
        from zipline.api import get_datetime
        current_time = get_datetime()
        
        record(
            pre_market_time=current_time,
            portfolio_value=context.portfolio.portfolio_value
        )

    def opening_strategy(self, context, data):
        """Opening bell strategy - capture opening momentum"""
        record(opening_strategy=True)
        
        # Generate opening signals based on overnight moves
        opening_signals = {}
        
        for asset in context.universe:
            try:
                # Get recent price data
                prices = data.history(asset, 'price', 5, '1m')
                if len(prices) >= 2:
                    # Calculate opening momentum
                    current_price = prices[-1]
                    prev_price = prices[-2]
                    momentum = (current_price / prev_price) - 1
                    
                    # Opening momentum signal
                    if momentum > 0.001:  # 0.1% positive momentum
                        opening_signals[asset] = 0.1  # Small opening position
                    elif momentum < -0.001:  # 0.1% negative momentum
                        opening_signals[asset] = -0.1  # Small short position
                    else:
                        opening_signals[asset] = 0
                        
                    record(**{f"opening_momentum_{asset.symbol}": momentum})
            except:
                opening_signals[asset] = 0
        
        # Store for main rebalancing
        self.morning_signals = opening_signals
        
        # Execute small opening positions
        for asset, weight in opening_signals.items():
            from zipline.api import order_target_percent
            order_target_percent(asset, weight)

    def main_rebalance(self, context, data):
        """Main rebalancing using SMA signals"""
        record(main_rebalancing=True)
        
        # This is the core SMA logic from your original strategy
        signals = self.generate_signals(context, data)
        
        # Combine with morning momentum
        final_signals = {}
        for asset in context.universe:
            sma_signal = signals.get(asset, 0)
            morning_signal = self.morning_signals.get(asset, 0)
            
            # Combine signals (SMA gets 80% weight, momentum gets 20%)
            final_signals[asset] = (sma_signal * 0.8) + (morning_signal * 0.2)
        
        # Execute main rebalancing
        for asset, weight in final_signals.items():
            from zipline.api import order_target_percent
            order_target_percent(asset, weight * 0.3)  # 30% max allocation per asset

    def weekly_momentum_check(self, context, data):
        """Weekly momentum analysis (Mondays only)"""
        record(weekly_momentum_check=True)
        
        weekly_momentum = {}
        for asset in context.universe:
            try:
                # Get 5-day price history
                prices = data.history(asset, 'price', 5, '1d')
                if len(prices) >= 5:
                    weekly_return = (prices[-1] / prices[0]) - 1
                    weekly_momentum[asset] = weekly_return
                    
                    record(**{f"weekly_momentum_{asset.symbol}": weekly_return})
            except:
                weekly_momentum[asset] = 0
        
        # Adjust positions based on weekly momentum
        for asset, momentum in weekly_momentum.items():
            if abs(momentum) > 0.05:  # 5% weekly move
                # Increase position if momentum is strong
                current_weight = 0.1 if momentum > 0 else -0.1
                from zipline.api import order_target_percent
                order_target_percent(asset, current_weight)

    def midday_risk_check(self, context, data):
        """Lunch-time risk assessment"""
        record(midday_risk_check=True)
        
        # Check portfolio performance
        daily_return = (context.portfolio.portfolio_value / context.portfolio.starting_cash) - 1
        leverage = context.account.leverage
        
        # Risk alert if daily loss > 2% or leverage > 0.8
        if daily_return < -0.02 or leverage > 0.8:
            self.risk_alert = True
            record(risk_alert=True)
            
            # Reduce positions if risk is high
            for asset in context.portfolio.positions:
                if context.portfolio.positions[asset].amount != 0:
                    current_pos = context.portfolio.positions[asset].amount
                    # Reduce position by 25%
                    from zipline.api import order_target
                    order_target(asset, current_pos * 0.75)
        
        record(
            midday_daily_return=daily_return,
            midday_leverage=leverage,
            midday_positions=len(context.portfolio.positions)
        )

    def afternoon_rebalance(self, context, data):
        """Afternoon trend continuation"""
        record(afternoon_rebalancing=True)
        
        if not self.risk_alert:  # Only if no risk alerts
            # Check afternoon momentum
            afternoon_signals = {}
            for asset in context.universe:
                try:
                    # Get last 2 hours of data
                    prices = data.history(asset, 'price', 120, '1m')  # 2 hours
                    if len(prices) >= 120:
                        afternoon_momentum = (prices[-1] / prices[0]) - 1
                        
                        # Continue strong afternoon trends
                        if abs(afternoon_momentum) > 0.01:  # 1% move in 2 hours
                            afternoon_signals[asset] = np.sign(afternoon_momentum) * 0.05
                        else:
                            afternoon_signals[asset] = 0
                            
                        record(**{f"afternoon_momentum_{asset.symbol}": afternoon_momentum})
                except:
                    afternoon_signals[asset] = 0
            
            # Execute afternoon adjustments
            for asset, weight in afternoon_signals.items():
                from zipline.api import order_target_percent
                current_weight = context.portfolio.positions[asset].amount / context.portfolio.portfolio_value
                new_weight = current_weight + weight
                order_target_percent(asset, new_weight)

    def eod_position_management(self, context, data):
        """End-of-day position management"""
        record(eod_position_management=True)
        
        # Close intraday positions, keep swing positions
        total_positions = len(context.portfolio.positions)
        portfolio_value = context.portfolio.portfolio_value
        leverage = context.account.leverage
        
        # Log end-of-day metrics
        record(
            eod_total_positions=total_positions,
            eod_portfolio_value=portfolio_value,
            eod_leverage=leverage
        )
        
        # If too many positions, close smallest ones
        if total_positions > 5:
            # Get position sizes
            position_values = {}
            for asset, position in context.portfolio.positions.items():
                if position.amount != 0:
                    position_values[asset] = abs(position.amount * data.current(asset, 'price'))
            
            # Sort by size and close smallest positions
            sorted_positions = sorted(position_values.items(), key=lambda x: x[1])
            positions_to_close = sorted_positions[:total_positions-5]  # Keep top 5
            
            for asset, _ in positions_to_close:
                from zipline.api import order_target_percent
                order_target_percent(asset, 0)

    def monthly_portfolio_review(self, context, data):
        """Monthly portfolio optimization"""
        record(monthly_portfolio_review=True)
        
        # Monthly rebalancing to equal weights
        if len(context.universe) > 0:
            target_weight = 1.0 / len(context.universe)
            
            for asset in context.universe:
                from zipline.api import order_target_percent
                order_target_percent(asset, target_weight)
        
        record(monthly_rebalance_target_weight=target_weight)

    def select_universe(self, context):
        """Select trading universe"""
        return [symbol(asset) for asset in self.assets]

    def generate_signals(self, context, data):
        """Core SMA signal generation (same as original)"""
        signals = {}
        for asset in context.universe:
            history = data.history(asset, 'price', self.long_window + 1, '1m')

            if not history.empty and len(history) >= self.long_window:
                short_mavg = history.tail(self.short_window).mean()
                long_mavg = history.mean()

                # Generate signals
                if short_mavg > long_mavg:
                    signals[asset] = 1.0
                else:
                    signals[asset] = -1.0

                # Record factors
                current_price = history.iloc[-1]
                sma_ratio = short_mavg / long_mavg if long_mavg != 0 else 1.0
                
                self.record_factor('sma_ratio', sma_ratio, context)
                record(prices=current_price)
            else:
                signals[asset] = 0.0

        return signals


if __name__ == '__main__':
    """
    Run the Indian Market Schedule Strategy
    """
    
    # Strategy configuration
    assets_to_trade = ['RELIANCE', 'TCS', 'HDFCBANK']
    
    strategy = IndianMarketScheduleStrategy(
        short_window=20,
        long_window=50,
        assets=assets_to_trade
    )
    
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-duckdb-parquet-bundle',
        start_date='2024-01-01',
        end_date='2024-12-01',
        capital_base=100000,
        benchmark_symbol=None,
        data_frequency='minute'
    )
    
    print("Running Indian Market Schedule Strategy...")
    results = runner.run()
    
    print("Analyzing results...")
    runner.analyze(results_dir='backtest_results/indian_market_schedule')
    
    print("Backtest and analysis complete!")
