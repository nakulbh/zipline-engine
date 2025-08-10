"""Simple dual moving average crossover strategy with MLflow logging.

Features:
- Parameterized short/long window lengths
- Uses EnhancedZiplineRunner (PyFolio artifacts auto-generated in analyze())
- Logs params, metrics, and artifacts (returns/positions/transactions + tear sheets) to MLflow
- Supports simple hyperparameter grid search inside the script

Run:
    python examples/mlflow_hyperparameter.py --short_windows 10 14 20 --long_windows 40 50 100 \
        --start 2021-01-01 --end 2025-01-01 --bundle nse-duckdb-parquet-bundle \
        --data-frequency minute --experiment zipline_ma

Ensure mlflow installed:
    pip install mlflow
"""

import sys
import os
import argparse
from typing import List

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
from zipline.api import order_target, symbol, set_commission, set_slippage
from zipline.finance import commission, slippage

from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from engine.enhanced_base_strategy import BaseStrategy

# Ensure bundle import side-effects (if required)
import bundles.duckdb_polars_bundle  # noqa: F401

try:
    import mlflow
except ImportError:  # Graceful message
    mlflow = None


class SimpleMAStrategy(BaseStrategy):
    def __init__(self, short_window: int = 14, long_window: int = 50, asset_symbol: str = "APOLLOTYRE"):
        self.short_window = short_window
        self.long_window = long_window
        self.asset_symbol = asset_symbol

    def initialize(self, context):
        context.i = 0
        context.asset = symbol(self.asset_symbol)
        context.universe = [context.asset]
        set_commission(commission.PerShare(cost=0.01, min_trade_cost=1))
        set_slippage(slippage.FixedSlippage(spread=0.01))

    def handle_data(self, context, data):
        context.i += 1
        # Need enough bars for long window
        if context.i < self.long_window:
            return

        short_mavg = data.history(
            context.asset,
            "price",
            bar_count=self.short_window,
            frequency="1m"
        ).mean()

        long_mavg = data.history(
            context.asset,
            "price",
            bar_count=self.long_window,
            frequency="1m"
        ).mean()

        if short_mavg > long_mavg:
            order_target(context.asset, 100)  # simplistic sizing
        elif short_mavg < long_mavg:
            order_target(context.asset, 0)


def compute_metrics(results: pd.DataFrame, capital_base: float) -> dict:
    metrics = {}
    if results is None or results.empty:
        return metrics
    final_value = results['portfolio_value'].iloc[-1]
    total_return = (final_value / capital_base) - 1.0
    metrics['final_portfolio_value'] = float(final_value)
    metrics['total_return_pct'] = float(total_return * 100)
    for col in ['max_drawdown', 'sharpe', 'sortino', 'alpha', 'beta']:
        if col in results.columns:
            val = results[col].iloc[-1]
            if pd.notna(val):
                metrics[col] = float(val)
    # Period count
    metrics['periods'] = int(len(results))
    return metrics


def log_artifacts_mlflow(runner: EnhancedZiplineRunner):
    if mlflow is None:
        return
    out_dir = runner.output_dir
    # Core CSVs
    for fname in ['returns.csv', 'positions.csv', 'transactions.csv', 'analysis_objects.pkl']:
        fpath = os.path.join(out_dir, fname)
        if os.path.exists(fpath):
            mlflow.log_artifact(fpath, artifact_path='pyfolio')
    # Figures (single + directory + pdf + zip)
    for fname in ['full_tear_sheet.png', 'full_tear_sheet.pdf', 'full_tear_sheet_figures.zip']:
        fpath = os.path.join(out_dir, fname)
        if os.path.exists(fpath):
            mlflow.log_artifact(fpath, artifact_path='pyfolio')
    figs_dir = os.path.join(out_dir, 'tear_sheet_figures')
    if os.path.isdir(figs_dir):
        mlflow.log_artifacts(figs_dir, artifact_path='pyfolio/tear_sheet_figures')


def run_single(short_window: int, long_window: int, args) -> dict:
    strategy = SimpleMAStrategy(short_window=short_window, long_window=long_window, asset_symbol=args.asset)
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle=args.bundle,
        start_date=args.start,
        end_date=args.end,
        capital_base=args.capital,
        data_frequency=args.data_frequency,
        live_start_date=None,
    )
    results = runner.run()
    metrics = compute_metrics(results, args.capital)
    return {'runner': runner, 'results': results, 'metrics': metrics}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--short_windows', nargs='+', type=int, default=[10, 14, 20])
    p.add_argument('--long_windows', nargs='+', type=int, default=[40, 50, 100])
    p.add_argument('--asset', type=str, default='APOLLOTYRE')
    p.add_argument('--start', type=str, default='2021-01-01')
    p.add_argument('--end', type=str, default='2025-01-01')
    p.add_argument('--bundle', type=str, default='nse-duckdb-parquet-bundle')
    p.add_argument('--capital', type=float, default=100000)
    p.add_argument('--data-frequency', type=str, default='minute', choices=['minute', 'daily'])
    p.add_argument('--experiment', type=str, default='zipline_simple_ma')
    p.add_argument('--no-mlflow', action='store_true', help='Skip MLflow even if installed')
    return p.parse_args()


def main():
    args = parse_args()
    use_mlflow = (mlflow is not None) and (not args.no_mlflow)
    if use_mlflow:
        mlflow.set_experiment(args.experiment)

    best = None
    best_key = None

    for lw in args.long_windows:
        for sw in args.short_windows:
            if sw >= lw:
                continue  # enforce short < long
            run_name = f"sw{sw}_lw{lw}"
            if use_mlflow:
                mlflow.start_run(run_name=run_name)
                mlflow.log_params({
                    'short_window': sw,
                    'long_window': lw,
                    'asset': args.asset,
                    'start': args.start,
                    'end': args.end,
                    'bundle': args.bundle,
                    'capital_base': args.capital,
                    'data_frequency': args.data_frequency,
                })
            outcome = run_single(sw, lw, args)
            metrics = outcome['metrics']
            if use_mlflow:
                mlflow.log_metrics(metrics)
                log_artifacts_mlflow(outcome['runner'])
                mlflow.end_run()
            # Track best by sharpe if available else total_return_pct
            key = metrics.get('sharpe', metrics.get('total_return_pct', -1e9))
            if best_key is None or key > best_key:
                best_key = key
                best = {'params': {'short_window': sw, 'long_window': lw}, 'metrics': metrics}

    if best:
        print("Best configuration:", best)
        if use_mlflow:
            # Log summary as separate run
            mlflow.start_run(run_name='best_summary')
            mlflow.log_params(best['params'])
            mlflow.log_metrics(best['metrics'])
            mlflow.end_run()
    else:
        print("No successful runs.")


if __name__ == '__main__':
    main()

