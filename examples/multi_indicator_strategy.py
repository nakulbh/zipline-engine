"""Example: Multi-indicator strategy (RSI + SMA crossover + Volume spike filter) using BaseStrategy + EnhancedZiplineRunner.

Logic:
1. Universe: Specify a few symbols (must exist in your bundle).
2. Daily before_trading_start builds indicator table using history.
3. Enter long when:
   - Short SMA > Long SMA AND
   - RSI < 60 AND
   - Volume > 1.2 * 20d average volume.
4. Exit when Short SMA < Long SMA OR RSI > 70.
5. Equal-weight positions, capped at 20% each.
"""
import os
import sys
import pandas as pd
import numpy as np
import pytz
from zipline.api import (
    order_target_percent, symbol, record, schedule_function,
    date_rules, time_rules, set_slippage, set_commission
)
from zipline.finance import slippage, commission
from zipline.utils.calendar_utils import get_calendar

# Ensure project root on path for engine imports when running standalone
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.enhanced_base_strategy import BaseStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

SYMBOLS = ['APOLLOTYRE', 'AXISBANK', 'HDFCBANK']  # adjust per bundle
SHORT_WIN = 20
LONG_WIN = 50
RSI_WIN = 14
VOL_WIN = 20
MAX_WEIGHT = 0.2


class MultiIndicatorStrategy(BaseStrategy):
    def initialize(self, context):
        context.assets = [symbol(s) for s in SYMBOLS]
        set_slippage(slippage.FixedSlippage(spread=0.01))
        set_commission(commission.PerShare(cost=0.001, min_trade_cost=1))
        # Schedule rebalance & metrics
        schedule_function(self.rebalance, date_rules.every_day(), time_rules.market_open(minutes=30))
        schedule_function(self.record_metrics, date_rules.every_day(), time_rules.market_close(minutes=1))

    def before_trading_start(self, context, data):
        context.indicators = {}
        for asset in getattr(context, 'assets', []):
            price_hist = data.history(asset, 'price', bar_count=LONG_WIN + 5, frequency='1d')
            vol_hist = data.history(asset, 'volume', bar_count=VOL_WIN + 5, frequency='1d')
            if len(price_hist) < LONG_WIN or len(vol_hist) < VOL_WIN:
                continue
            sma_short = price_hist.tail(SHORT_WIN).mean()
            sma_long = price_hist.tail(LONG_WIN).mean()
            diff = price_hist.diff().dropna()
            up = np.where(diff > 0, diff, 0)
            down = np.where(diff < 0, -diff, 0)
            roll_up = pd.Series(up).rolling(RSI_WIN).mean().iloc[-1]
            roll_down = pd.Series(down).rolling(RSI_WIN).mean().iloc[-1]
            if roll_down == 0:
                rsi = 100
            else:
                rs = roll_up / roll_down
                rsi = 100 - (100 / (1 + rs))
            avg_vol = vol_hist.tail(VOL_WIN).mean()
            cur_vol = vol_hist.iloc[-1]
            context.indicators[asset] = dict(
                sma_short=sma_short,
                sma_long=sma_long,
                rsi=rsi,
                vol=cur_vol,
                avg_vol=avg_vol,
                price=price_hist.iloc[-1]
            )

    def rebalance(self, context, data):
        if not hasattr(context, 'indicators'):
            return
        longs = []
        for asset, ind in context.indicators.items():
            if ind['sma_short'] > ind['sma_long'] and ind['rsi'] < 60 and ind['vol'] > 1.2 * ind['avg_vol']:
                longs.append(asset)
            elif asset in context.portfolio.positions and (ind['sma_short'] < ind['sma_long'] or ind['rsi'] > 70):
                order_target_percent(asset, 0)
        if longs:
            weight = min(MAX_WEIGHT, 1.0 / len(longs))
            for asset in longs:
                if data.can_trade(asset):
                    order_target_percent(asset, weight)

    def record_metrics(self, context, data):
        record(leverage=context.account.leverage, positions=len(context.portfolio.positions))

    def handle_data(self, context, data):
        pass


if __name__ == '__main__':
    strategy = MultiIndicatorStrategy()
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-duckdb-parquet-bundle',  # adjust
        start_date='2022-06-01',
        end_date='2023-01-01',
        capital_base=100000,
        data_frequency='daily'
    )
    runner.run()
