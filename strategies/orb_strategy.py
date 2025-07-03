import sys
import os
import pandas as pd
import numpy as np
from zipline.api import (
    order_target_percent, symbol, record, get_datetime,
    schedule_function, date_rules, time_rules, order_target
)

# Add the parent directory to Python path so we can import from engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.zipline_runner import TradingEngine
from engine.base_strategy import TradingConfig


class ORBStrategy:
    """
    Opening Range Breakout (ORB) Strategy for NSE minute data (Zipline Reloaded):
    1. Uses 30-minute opening range candle (9:15-9:45)
    2. Takes position on 15-minute timeframe breakout
    3. Long position: if 15min close > ORB high
    4. Short position: if 15min close < ORB low
    5. Stop loss: ORB low for long, ORB high for short
    6. Target: 2R (2 times the risk)
    7. Exits all positions at 3:10 PM
    """

    def __init__(self, config):
        """Initialize strategy parameters"""
        self.config = config
        self.orb_start_time = "09:15"
        self.orb_end_time = "09:45"
        self.market_close_time = "15:10"
        self.risk_reward_ratio = 2.0
        self.position_size = 0.95  # Use 95% of available capital

    def initialize(self, context):
        """Initialize the ORB strategy"""
        print("Initializing ORB Strategy for NSE minute data...")

        # Define our trading universe based on available data for the backtest period
        context.universe = [
            symbol('BAJFINANCE'),
            symbol('BANKNIFTY'),
            symbol('HDFCBANK'),
            symbol('HINDALCO'), # Replaced RELIANCE
            symbol('SBIN')
        ]

        # Primary trading symbol - BAJFINANCE has data for the full period
        context.primary_symbol = symbol('BAJFINANCE')

        # Initialize strategy variables
        self.reset_daily_variables(context)

        # Schedule ORB establishment at 9:45 AM
        schedule_function(
            self.establish_orb,
            date_rules.every_day(),
            time_rules.market_open(minutes=30)
        )

        # Schedule breakout checks every 15 minutes from 9:45 AM to 3:00 PM
        for minutes_after_open in range(45, 345, 15):
            schedule_function(
                self.check_breakout,
                date_rules.every_day(),
                time_rules.market_open(minutes=minutes_after_open)
            )

        # Schedule end-of-day close at 3:10 PM
        schedule_function(
            self.close_all_positions,
            date_rules.every_day(),
            time_rules.market_close(minutes=20)
        )

    def reset_daily_variables(self, context):
        """Reset all daily trading variables"""
        context.orb_high = None
        context.orb_low = None
        context.orb_established = False
        context.position_taken = False
        context.entry_price = None
        context.stop_loss = None
        context.target = None
        context.position_type = None  # 'long' or 'short'
        context.current_day = None

    def establish_orb(self, context, data):
        """Calculate the Opening Range Breakout levels (9:15-9:45)"""
        if not data.can_trade(context.primary_symbol):
            return

        try:
            # Get 30 minutes of 1m bars starting from market open
            bars = data.history(
                context.primary_symbol,
                ['high', 'low'],
                bar_count=30,
                frequency='1m'
            )

            if len(bars) >= 30:
                context.orb_high = bars['high'].max()
                context.orb_low = bars['low'].min()
                context.orb_established = True

                print(f"\nORB Established at {get_datetime().time()}")
                print(f"Symbol: {context.primary_symbol.symbol}")
                print(f"ORB High: {context.orb_high:.2f}")
                print(f"ORB Low: {context.orb_low:.2f}")
                print(f"Range: {context.orb_high - context.orb_low:.2f}")

                record(
                    orb_high=context.orb_high,
                    orb_low=context.orb_low,
                    orb_range=context.orb_high - context.orb_low
                )
            else:
                print(f"Warning: Only {len(bars)} bars available for ORB calculation")

        except Exception as e:
            print(f"Error establishing ORB: {str(e)}")
            import traceback
            traceback.print_exc()

    def check_breakout(self, context, data):
        """Check for breakout signals every 15 minutes"""
        if not context.orb_established or context.position_taken:
            return

        if not data.can_trade(context.primary_symbol):
            return

        try:
            current_price = data.current(context.primary_symbol, 'price')

            # Long breakout condition
            if current_price > context.orb_high:
                self.enter_position(context, data, current_price, 'long')

            # Short breakout condition
            elif current_price < context.orb_low:
                self.enter_position(context, data, current_price, 'short')

        except Exception as e:
            print(f"Error checking breakout: {str(e)}")

    def enter_position(self, context, data, entry_price, position_type):
        """Enter either long or short position with proper risk management"""
        context.entry_price = entry_price
        context.position_type = position_type
        context.position_taken = True

        # Set risk parameters based on position type
        if position_type == 'long':
            context.stop_loss = context.orb_low
            risk_per_share = entry_price - context.stop_loss
            context.target = entry_price + (self.risk_reward_ratio * risk_per_share)
        else:  # short
            context.stop_loss = context.orb_high
            risk_per_share = context.stop_loss - entry_price
            context.target = entry_price - (self.risk_reward_ratio * risk_per_share)

        # Calculate position size
        if risk_per_share > 0:
            risk_capital = context.portfolio.portfolio_value * 0.02  # Risk 2% of capital
            shares = int(risk_capital / risk_per_share)
        else:
            shares = 100  # Default size if risk calculation fails

        # Execute order
        order_amount = shares if position_type == 'long' else -shares
        order_target(context.primary_symbol, order_amount)

        print(f"\n{'🟢 LONG' if position_type == 'long' else '🔴 SHORT'} ENTRY")
        print(f"Time: {get_datetime().time()}")
        print(f"Entry: {entry_price:.2f}")
        print(f"Stop: {context.stop_loss:.2f}")
        print(f"Target: {context.target:.2f}")
        print(f"Shares: {abs(shares)} ({'Long' if position_type == 'long' else 'Short'})")

        record(
            entry_price=entry_price,
            position_type=1 if position_type == 'long' else -1,
            position_size=shares
        )

    def handle_data(self, context, data):
        """Monitor positions every minute - this is the main handler"""
        if context.position_taken:
            self.manage_position(context, data)

    def manage_position(self, context, data):
        """Monitor open positions for exits"""
        if not context.position_taken:
            return

        try:
            current_price = data.current(context.primary_symbol, 'price')

            if context.position_type == 'long':
                if current_price <= context.stop_loss:
                    self.exit_position(context, data, current_price, "SL Hit")
                elif current_price >= context.target:
                    self.exit_position(context, data, current_price, "Target Hit")
            else:  # short
                if current_price >= context.stop_loss:
                    self.exit_position(context, data, current_price, "SL Hit")
                elif current_price <= context.target:
                    self.exit_position(context, data, current_price, "Target Hit")
        except Exception as e:
            print(f"Error managing position: {str(e)}")

    def exit_position(self, context, data, exit_price, reason):
        """Exit the current position"""
        order_target(context.primary_symbol, 0)

        pnl = (exit_price - context.entry_price) if context.position_type == 'long' \
              else (context.entry_price - exit_price)
        pnl_pct = (pnl / context.entry_price) * 100

        print(f"\n🔶 POSITION CLOSED: {reason}")
        print(f"Exit Price: {exit_price:.2f}")
        print(f"P&L: {pnl:.2f} ({pnl_pct:.2f}%)")

        record(
            exit_price=exit_price,
            pnl=pnl,
            exit_reason=reason
        )

        context.position_taken = False
        context.position_type = None

    def close_all_positions(self, context, data):
        """Close all positions at market close"""
        if context.position_taken:
            try:
                current_price = data.current(context.primary_symbol, 'price')
                self.exit_position(context, data, current_price, "EOD Close")
            except Exception as e:
                print(f"Error closing EOD position: {str(e)}")

    def before_trading_start(self, context, data):
        """Prepare for new trading day"""
        current_date = get_datetime().date()
        if context.current_day != current_date:
            self.reset_daily_variables(context)
            context.current_day = current_date
            print(f"\n📅 New Trading Day: {current_date}")


def run_orb_strategy():
    """Run the ORB strategy backtest"""

    config = TradingConfig(
        start_date="2018-01-01",
        end_date="2019-02-28",
        capital_base=100000.0,
        commission_cost=0.001,
        output_dir="./backtest_results/orb",
        data_frequency="minute"
    )

    strategy = ORBStrategy(config)
    engine = TradingEngine(config)

    print("=" * 60)
    print("ORB STRATEGY BACKTEST")
    print("=" * 60)

    try:
        backtest_results = engine.run_backtest(strategy)
        engine.analyze_performance()
        print("=" * 60)
        print("✅ ORB strategy completed successfully!")
        return engine, backtest_results

    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    engine, backtest_results = run_orb_strategy()

    if engine and backtest_results is not None:
        # Save results to CSV
        results_df = backtest_results['results']
        csv_path = os.path.join(engine.config.output_dir, "orb_results.csv")
        results_df.to_csv(csv_path)
        print(f"Saved backtest results to {csv_path}")

        # Generate and save tearsheet
        engine.create_tearsheet()
        print(f"Tearsheet saved in {engine.config.output_dir}")
