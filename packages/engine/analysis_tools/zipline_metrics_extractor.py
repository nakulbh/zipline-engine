#!/usr/bin/env python3
"""
Zipline Reloaded Metrics Extractor

This script shows you ALL the metrics that Zipline Reloaded can provide
and extracts them from your backtest results. It demonstrates that Zipline
has much more comprehensive metrics than just the basic performance stats.

Usage:
    python zipline_metrics_extractor.py <results_directory>
    
Example:
    python zipline_metrics_extractor.py backtest_results/rsi_support_resistance
"""

import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def extract_all_available_metrics(results_dir):
    """
    Extract ALL available metrics from Zipline backtest results
    """
    print(f"🔍 Extracting ALL available metrics from: {results_dir}")
    
    all_metrics = {}
    
    # 1. BASIC RESULTS ANALYSIS
    basic_results_path = os.path.join(results_dir, 'basic_results.csv')
    if os.path.exists(basic_results_path):
        print("📊 Analyzing basic_results.csv...")
        basic_results = pd.read_csv(basic_results_path, index_col=0, parse_dates=True)
        
        # Portfolio metrics
        portfolio_value = basic_results['portfolio_value']
        returns = basic_results['returns']
        
        all_metrics.update({
            'Initial Capital': portfolio_value.iloc[0],
            'Ending Capital': portfolio_value.iloc[-1],
            'Net Profit': portfolio_value.iloc[-1] - portfolio_value.iloc[0],
            'Net Profit %': ((portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1) * 100,
            'Total Return %': ((portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1) * 100,
            'Total Trading Days': len(basic_results),
            'Peak Portfolio Value': portfolio_value.max(),
            'Lowest Portfolio Value': portfolio_value.min(),
        })
        
        # Return analysis
        all_metrics.update({
            'Best Day Return %': returns.max() * 100,
            'Worst Day Return %': returns.min() * 100,
            'Average Daily Return %': returns.mean() * 100,
            'Median Daily Return %': returns.median() * 100,
            'Daily Return Std Dev %': returns.std() * 100,
            'Positive Return Days': (returns > 0).sum(),
            'Negative Return Days': (returns < 0).sum(),
            'Zero Return Days': (returns == 0).sum(),
            'Win Rate %': ((returns > 0).sum() / len(returns)) * 100,
        })
        
        # Risk metrics
        annual_return = (1 + returns.mean()) ** 252 - 1
        annual_vol = returns.std() * np.sqrt(252)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        
        # Drawdown analysis
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        
        all_metrics.update({
            'Annualized Return %': annual_return * 100,
            'Annualized Volatility %': annual_vol * 100,
            'Sharpe Ratio': sharpe,
            'Max Drawdown %': drawdown.min() * 100,
            'Current Drawdown %': drawdown.iloc[-1] * 100,
            'Average Drawdown %': drawdown[drawdown < 0].mean() * 100 if (drawdown < 0).any() else 0,
            'Drawdown Duration (days)': len(drawdown[drawdown < 0]),
        })
        
        # Benchmark analysis (if available)
        if 'benchmark_period_return' in basic_results.columns:
            benchmark_returns = basic_results['benchmark_period_return']
            excess_returns = returns - benchmark_returns
            
            all_metrics.update({
                'Benchmark Total Return %': ((1 + benchmark_returns).prod() - 1) * 100,
                'Excess Return %': excess_returns.mean() * 252 * 100,
                'Tracking Error %': excess_returns.std() * np.sqrt(252) * 100,
                'Information Ratio': (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() != 0 else 0,
                'Beta': np.cov(returns, benchmark_returns)[0,1] / np.var(benchmark_returns) if np.var(benchmark_returns) != 0 else 0,
            })
    
    # 2. PERFORMANCE STATISTICS ANALYSIS
    perf_stats_path = os.path.join(results_dir, 'performance_statistics.csv')
    if os.path.exists(perf_stats_path):
        print("📈 Analyzing performance_statistics.csv...")
        perf_stats = pd.read_csv(perf_stats_path, index_col=0)
        
        # Add all Pyfolio metrics
        for metric_name in perf_stats.index:
            value = perf_stats.loc[metric_name].iloc[0]
            all_metrics[f'Pyfolio {metric_name}'] = value
    
    # 3. TRADE BOOK ANALYSIS
    trade_book_path = os.path.join(results_dir, 'trade_book.csv')
    if os.path.exists(trade_book_path):
        print("💱 Analyzing trade_book.csv...")
        trade_book = pd.read_csv(trade_book_path)
        
        # Count actual trades
        actual_trades = trade_book[trade_book['transaction_str'] != '[]']
        
        all_metrics.update({
            'Total Trade Records': len(trade_book),
            'Actual Trades': len(actual_trades),
            'Trading Frequency %': (len(actual_trades) / len(trade_book)) * 100,
            'Average Trades per Day': len(actual_trades) / len(trade_book),
        })
        
        # Parse transaction details
        total_volume = 0
        total_commissions = 0
        buy_count = 0
        sell_count = 0
        
        for _, row in actual_trades.iterrows():
            try:
                import ast
                transactions = ast.literal_eval(row['transaction_str'])
                
                for txn in transactions:
                    if isinstance(txn, dict):
                        amount = txn.get('amount', 0)
                        price = txn.get('price', 0)
                        commission = txn.get('commission', 0)
                        
                        total_volume += abs(amount * price)
                        if commission:
                            total_commissions += commission
                        
                        if amount > 0:
                            buy_count += 1
                        elif amount < 0:
                            sell_count += 1
            except:
                continue
        
        all_metrics.update({
            'Buy Transactions': buy_count,
            'Sell Transactions': sell_count,
            'Total Transaction Volume': total_volume,
            'Total Transaction Costs': total_commissions,
            'Average Transaction Cost': total_commissions / len(actual_trades) if len(actual_trades) > 0 else 0,
            'Transaction Cost %': (total_commissions / total_volume) * 100 if total_volume > 0 else 0,
        })
    
    # 4. ORDER BOOK ANALYSIS
    order_book_path = os.path.join(results_dir, 'order_book.csv')
    if os.path.exists(order_book_path):
        print("📋 Analyzing order_book.csv...")
        order_book = pd.read_csv(order_book_path)
        
        actual_orders = order_book[order_book['order_str'] != '[]']
        
        all_metrics.update({
            'Total Order Records': len(order_book),
            'Actual Orders': len(actual_orders),
            'Order Frequency %': (len(actual_orders) / len(order_book)) * 100,
        })
        
        # Parse order details
        filled_orders = 0
        cancelled_orders = 0
        
        for _, row in actual_orders.iterrows():
            try:
                import ast
                orders = ast.literal_eval(row['order_str'])
                
                for order in orders:
                    if isinstance(order, dict):
                        status = str(order.get('status', ''))
                        if 'FILLED' in status:
                            filled_orders += 1
                        elif 'CANCELLED' in status:
                            cancelled_orders += 1
            except:
                continue
        
        all_metrics.update({
            'Filled Orders': filled_orders,
            'Cancelled Orders': cancelled_orders,
            'Order Fill Rate %': (filled_orders / len(actual_orders)) * 100 if len(actual_orders) > 0 else 0,
            'Order Cancel Rate %': (cancelled_orders / len(actual_orders)) * 100 if len(actual_orders) > 0 else 0,
        })
    
    # 5. BENCHMARK METRICS ANALYSIS
    benchmark_path = os.path.join(results_dir, 'benchmark_metrics.csv')
    if os.path.exists(benchmark_path):
        print("📊 Analyzing benchmark_metrics.csv...")
        benchmark_metrics = pd.read_csv(benchmark_path, index_col=0)
        
        for metric_name in benchmark_metrics.index:
            value = benchmark_metrics.loc[metric_name].iloc[0]
            all_metrics[f'Benchmark {metric_name}'] = value
    
    return all_metrics

def display_metrics_by_category(all_metrics):
    """
    Display metrics organized by category
    """
    print("\n" + "=" * 80)
    print("📊 ALL AVAILABLE ZIPLINE RELOADED METRICS")
    print("=" * 80)
    
    # Capital & Portfolio Metrics
    capital_metrics = [k for k in all_metrics.keys() if any(word in k for word in ['Capital', 'Profit', 'Portfolio', 'Value'])]
    if capital_metrics:
        print("\n💰 CAPITAL & PORTFOLIO METRICS:")
        for key in sorted(capital_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if '%' in key:
                    print(f"   {key:<40}: {value:>15.2f}%")
                elif any(word in key for word in ['Capital', 'Profit', 'Value', 'Volume', 'Cost']):
                    print(f"   {key:<40}: ${value:>15,.2f}")
                else:
                    print(f"   {key:<40}: {value:>15.2f}")
            else:
                print(f"   {key:<40}: {value:>15}")
    
    # Return Metrics
    return_metrics = [k for k in all_metrics.keys() if 'Return' in k and k not in capital_metrics]
    if return_metrics:
        print("\n📈 RETURN METRICS:")
        for key in sorted(return_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if '%' in key:
                    print(f"   {key:<40}: {value:>15.2f}%")
                else:
                    print(f"   {key:<40}: {value:>15.4f}")
            else:
                print(f"   {key:<40}: {value:>15}")
    
    # Risk Metrics
    risk_metrics = [k for k in all_metrics.keys() if any(word in k for word in ['Risk', 'Volatility', 'Sharpe', 'Drawdown', 'VaR', 'Ratio'])]
    if risk_metrics:
        print("\n📉 RISK METRICS:")
        for key in sorted(risk_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if '%' in key:
                    print(f"   {key:<40}: {value:>15.2f}%")
                else:
                    print(f"   {key:<40}: {value:>15.4f}")
            else:
                print(f"   {key:<40}: {value:>15}")
    
    # Trading Activity Metrics
    trading_metrics = [k for k in all_metrics.keys() if any(word in k for word in ['Trade', 'Order', 'Transaction', 'Days', 'Frequency'])]
    if trading_metrics:
        print("\n📊 TRADING ACTIVITY METRICS:")
        for key in sorted(trading_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if '%' in key:
                    print(f"   {key:<40}: {value:>15.2f}%")
                else:
                    print(f"   {key:<40}: {value:>15.0f}")
            else:
                print(f"   {key:<40}: {value:>15}")
    
    # Benchmark Metrics
    benchmark_metrics = [k for k in all_metrics.keys() if 'Benchmark' in k or any(word in k for word in ['Beta', 'Alpha', 'Excess', 'Tracking'])]
    if benchmark_metrics:
        print("\n🎯 BENCHMARK COMPARISON METRICS:")
        for key in sorted(benchmark_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if '%' in key:
                    print(f"   {key:<40}: {value:>15.2f}%")
                else:
                    print(f"   {key:<40}: {value:>15.4f}")
            else:
                print(f"   {key:<40}: {value:>15}")
    
    # Pyfolio Metrics
    pyfolio_metrics = [k for k in all_metrics.keys() if 'Pyfolio' in k]
    if pyfolio_metrics:
        print("\n🔬 PYFOLIO ADVANCED METRICS:")
        for key in sorted(pyfolio_metrics):
            value = all_metrics[key]
            if isinstance(value, (int, float)):
                if any(word in key.lower() for word in ['return', 'volatility', 'drawdown']):
                    print(f"   {key:<40}: {value:>15.2%}")
                else:
                    print(f"   {key:<40}: {value:>15.4f}")
            else:
                print(f"   {key:<40}: {value:>15}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python zipline_metrics_extractor.py <results_directory>")
        print("Example: python zipline_metrics_extractor.py backtest_results/rsi_support_resistance")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    
    if not os.path.exists(results_dir):
        print(f"❌ Directory not found: {results_dir}")
        sys.exit(1)
    
    print("=" * 80)
    print("🚀 ZIPLINE RELOADED COMPREHENSIVE METRICS EXTRACTOR")
    print("=" * 80)
    
    # Extract all available metrics
    all_metrics = extract_all_available_metrics(results_dir)
    
    # Display metrics by category
    display_metrics_by_category(all_metrics)
    
    # Save comprehensive metrics to CSV
    output_file = os.path.join(results_dir, 'all_zipline_metrics.csv')
    metrics_df = pd.DataFrame.from_dict(all_metrics, orient='index', columns=['Value'])
    metrics_df.to_csv(output_file)
    
    print(f"\n✅ ALL {len(all_metrics)} metrics saved to: {output_file}")
    print(f"\n📋 SUMMARY:")
    print(f"   Total metrics extracted: {len(all_metrics)}")
    print(f"   Files analyzed: {len([f for f in ['basic_results.csv', 'performance_statistics.csv', 'trade_book.csv', 'order_book.csv', 'benchmark_metrics.csv'] if os.path.exists(os.path.join(results_dir, f))])}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
