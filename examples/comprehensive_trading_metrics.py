#!/usr/bin/env python3
"""
Comprehensive Trading Metrics Extractor

This script extracts detailed trading metrics from Zipline backtest results
that are missing from the basic performance statistics, including:

- Number of trades
- Initial and ending capital
- Net profit and profit percentage
- Exposure metrics
- Transaction costs
- Win rate and profit factor
- Average profit/loss per trade
- Risk-adjusted returns
- And many more detailed trading statistics

Usage:
    python comprehensive_trading_metrics.py <results_directory>
    
Example:
    python comprehensive_trading_metrics.py backtest_results/rsi_support_resistance
"""

import os
import sys
import pandas as pd
import numpy as np
import pyfolio as pf
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def extract_comprehensive_metrics(results_dir):
    """
    Extract comprehensive trading metrics from Zipline backtest results
    """
    print(f"🔍 Analyzing results from: {results_dir}")
    
    # Check if basic_results.csv exists
    basic_results_path = os.path.join(results_dir, 'basic_results.csv')
    if not os.path.exists(basic_results_path):
        print(f"❌ basic_results.csv not found in {results_dir}")
        return None
    
    # Load basic results
    basic_results = pd.read_csv(basic_results_path, index_col=0, parse_dates=True)
    print(f"📊 Loaded {len(basic_results)} trading days of data")
    
    # Extract key data
    portfolio_value = basic_results['portfolio_value']
    returns = basic_results['returns']
    
    # Calculate comprehensive metrics
    metrics = {}
    
    # ============= CAPITAL METRICS =============
    initial_capital = portfolio_value.iloc[0]
    ending_capital = portfolio_value.iloc[-1]
    net_profit = ending_capital - initial_capital
    net_profit_pct = (net_profit / initial_capital) * 100
    
    metrics['Initial Capital'] = initial_capital
    metrics['Ending Capital'] = ending_capital
    metrics['Net Profit'] = net_profit
    metrics['Net Profit %'] = net_profit_pct
    
    # ============= RETURN METRICS =============
    total_return = (ending_capital / initial_capital) - 1
    cumulative_returns = (1 + returns).cumprod() - 1
    annual_return = (1 + total_return) ** (252 / len(returns)) - 1
    
    metrics['Total Return'] = total_return
    metrics['Total Return %'] = total_return * 100
    metrics['Annualized Return'] = annual_return
    metrics['Annualized Return %'] = annual_return * 100
    
    # ============= RISK METRICS =============
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
    
    # Drawdown calculation
    peak = portfolio_value.expanding().max()
    drawdown = (portfolio_value - peak) / peak
    max_drawdown = drawdown.min()
    
    # Calmar ratio
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # Sortino ratio (downside deviation)
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
    sortino_ratio = annual_return / downside_std if downside_std != 0 else 0
    
    metrics['Annual Volatility'] = volatility
    metrics['Annual Volatility %'] = volatility * 100
    metrics['Sharpe Ratio'] = sharpe_ratio
    metrics['Max Drawdown'] = max_drawdown
    metrics['Max Drawdown %'] = max_drawdown * 100
    metrics['Calmar Ratio'] = calmar_ratio
    metrics['Sortino Ratio'] = sortino_ratio
    
    # ============= TRADING ACTIVITY METRICS =============
    # Win/Loss analysis
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]
    
    winning_days = len(positive_returns)
    losing_days = len(negative_returns)
    total_trading_days = len(returns)
    
    win_rate = (winning_days / total_trading_days) * 100 if total_trading_days > 0 else 0
    
    avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
    avg_loss = negative_returns.mean() if len(negative_returns) > 0 else 0
    
    # Profit factor
    total_wins = positive_returns.sum() if len(positive_returns) > 0 else 0
    total_losses = abs(negative_returns.sum()) if len(negative_returns) > 0 else 0
    profit_factor = total_wins / total_losses if total_losses != 0 else float('inf')
    
    metrics['Total Trading Days'] = total_trading_days
    metrics['Winning Days'] = winning_days
    metrics['Losing Days'] = losing_days
    metrics['Win Rate %'] = win_rate
    metrics['Average Win'] = avg_win
    metrics['Average Win %'] = avg_win * 100
    metrics['Average Loss'] = avg_loss
    metrics['Average Loss %'] = avg_loss * 100
    metrics['Profit Factor'] = profit_factor
    
    # ============= EXPOSURE METRICS =============
    # Calculate exposure (time in market)
    # This is a simplified calculation - in reality, you'd need position data
    non_zero_return_days = len(returns[returns != 0])
    exposure = (non_zero_return_days / total_trading_days) * 100 if total_trading_days > 0 else 0
    
    metrics['Market Exposure %'] = exposure
    
    return metrics

def analyze_transactions(results_dir):
    """
    Analyze transaction data if available and extract detailed trade metrics
    """
    trade_book_path = os.path.join(results_dir, 'trade_book.csv')
    order_book_path = os.path.join(results_dir, 'order_book.csv')

    transaction_metrics = {}

    if os.path.exists(trade_book_path):
        try:
            trade_book = pd.read_csv(trade_book_path)
            print(f"📈 Found trade book with {len(trade_book)} records")

            # Count actual trades (non-empty transaction strings)
            actual_trades = trade_book[trade_book['transaction_str'] != '[]']
            num_trades = len(actual_trades)

            transaction_metrics['Number of Trades'] = num_trades
            transaction_metrics['Average Trades per Day'] = num_trades / len(trade_book) if len(trade_book) > 0 else 0

            # Parse transaction details for more metrics
            total_transaction_value = 0
            total_commissions = 0
            buy_trades = 0
            sell_trades = 0

            for _, row in actual_trades.iterrows():
                try:
                    # Parse the transaction string (it's a list representation)
                    import ast
                    transactions = ast.literal_eval(row['transaction_str'])

                    for txn in transactions:
                        if isinstance(txn, dict):
                            amount = txn.get('amount', 0)
                            price = txn.get('price', 0)
                            commission = txn.get('commission', 0)

                            total_transaction_value += abs(amount * price)
                            if commission:
                                total_commissions += commission

                            if amount > 0:
                                buy_trades += 1
                            elif amount < 0:
                                sell_trades += 1

                except Exception as parse_e:
                    continue

            transaction_metrics['Buy Trades'] = buy_trades
            transaction_metrics['Sell Trades'] = sell_trades
            transaction_metrics['Total Transaction Value'] = total_transaction_value
            transaction_metrics['Total Transaction Costs'] = total_commissions
            transaction_metrics['Average Transaction Cost'] = total_commissions / num_trades if num_trades > 0 else 0

        except Exception as e:
            print(f"⚠️  Could not analyze trade book: {e}")

    if os.path.exists(order_book_path):
        try:
            order_book = pd.read_csv(order_book_path)
            print(f"📋 Found order book with {len(order_book)} records")

            # Count actual orders (non-empty order strings)
            actual_orders = order_book[order_book['order_str'] != '[]']
            num_orders = len(actual_orders)

            transaction_metrics['Number of Orders'] = num_orders

            # Parse order details
            filled_orders = 0
            total_order_value = 0

            for _, row in actual_orders.iterrows():
                try:
                    import ast
                    orders = ast.literal_eval(row['order_str'])

                    for order in orders:
                        if isinstance(order, dict):
                            status = order.get('status', '')
                            if 'FILLED' in str(status):
                                filled_orders += 1

                            amount = order.get('amount', 0)
                            # Estimate order value (would need price data for exact calculation)
                            total_order_value += abs(amount)

                except Exception as parse_e:
                    continue

            transaction_metrics['Filled Orders'] = filled_orders
            transaction_metrics['Order Fill Rate %'] = (filled_orders / num_orders) * 100 if num_orders > 0 else 0

        except Exception as e:
            print(f"⚠️  Could not analyze order book: {e}")

    return transaction_metrics

def calculate_risk_adjusted_returns(returns, risk_free_rate=0.02):
    """
    Calculate various risk-adjusted return metrics
    """
    risk_metrics = {}
    
    # Convert risk-free rate to daily
    daily_rf = risk_free_rate / 252
    
    # Excess returns
    excess_returns = returns - daily_rf
    
    # Information ratio (similar to Sharpe but uses tracking error)
    tracking_error = returns.std() * np.sqrt(252)
    information_ratio = (returns.mean() * 252) / tracking_error if tracking_error != 0 else 0
    
    # Treynor ratio (requires beta, simplified here)
    # Assuming beta = 1 for simplification
    beta = 1.0
    treynor_ratio = (returns.mean() * 252 - risk_free_rate) / beta
    
    # Value at Risk (VaR) - 95% confidence
    var_95 = np.percentile(returns, 5)
    
    # Conditional Value at Risk (CVaR) - Expected Shortfall
    cvar_95 = returns[returns <= var_95].mean()
    
    risk_metrics['Information Ratio'] = information_ratio
    risk_metrics['Treynor Ratio'] = treynor_ratio
    risk_metrics['Value at Risk (95%)'] = var_95
    risk_metrics['Value at Risk (95%) %'] = var_95 * 100
    risk_metrics['Conditional VaR (95%)'] = cvar_95
    risk_metrics['Conditional VaR (95%) %'] = cvar_95 * 100
    
    return risk_metrics

def main():
    if len(sys.argv) != 2:
        print("Usage: python comprehensive_trading_metrics.py <results_directory>")
        print("Example: python comprehensive_trading_metrics.py backtest_results/rsi_support_resistance")
        sys.exit(1)

    results_dir = sys.argv[1]

    if not os.path.exists(results_dir):
        print(f"❌ Directory not found: {results_dir}")
        sys.exit(1)

    print("=" * 80)
    print("🚀 COMPREHENSIVE TRADING METRICS ANALYSIS")
    print("=" * 80)

    # Extract comprehensive metrics
    metrics = extract_comprehensive_metrics(results_dir)
    if metrics is None:
        sys.exit(1)

    # Analyze transactions
    transaction_metrics = analyze_transactions(results_dir)

    # Calculate risk-adjusted returns
    basic_results = pd.read_csv(os.path.join(results_dir, 'basic_results.csv'), index_col=0, parse_dates=True)
    risk_metrics = calculate_risk_adjusted_returns(basic_results['returns'])

    # Combine all metrics
    all_metrics = {**metrics, **transaction_metrics, **risk_metrics}

    # Display results
    print("\n📊 COMPREHENSIVE TRADING METRICS")
    print("=" * 50)

    # Capital & Returns
    print("\n💰 CAPITAL & RETURNS:")
    for key in ['Initial Capital', 'Ending Capital', 'Net Profit', 'Net Profit %',
                'Total Return %', 'Annualized Return %']:
        if key in all_metrics:
            value = all_metrics[key]
            if isinstance(value, float):
                if '%' in key:
                    print(f"   {key:<25}: {value:>12.2f}%")
                elif 'Capital' in key or 'Profit' in key:
                    print(f"   {key:<25}: ${value:>12,.2f}")
                else:
                    print(f"   {key:<25}: {value:>12.4f}")
            else:
                print(f"   {key:<25}: {value:>12}")

    # Risk Metrics
    print("\n📉 RISK METRICS:")
    for key in ['Annual Volatility %', 'Sharpe Ratio', 'Max Drawdown %',
                'Calmar Ratio', 'Sortino Ratio', 'Information Ratio']:
        if key in all_metrics:
            value = all_metrics[key]
            if '%' in key:
                print(f"   {key:<25}: {value:>12.2f}%")
            else:
                print(f"   {key:<25}: {value:>12.4f}")

    # Trading Activity
    print("\n📈 TRADING ACTIVITY:")
    for key in ['Total Trading Days', 'Number of Trades', 'Number of Orders',
                'Winning Days', 'Losing Days', 'Win Rate %', 'Market Exposure %']:
        if key in all_metrics:
            value = all_metrics[key]
            if isinstance(value, float):
                if '%' in key:
                    print(f"   {key:<25}: {value:>12.2f}%")
                else:
                    print(f"   {key:<25}: {value:>12.2f}")
            else:
                print(f"   {key:<25}: {value:>12}")

    # Performance Analysis
    print("\n🎯 PERFORMANCE ANALYSIS:")
    for key in ['Average Win %', 'Average Loss %', 'Profit Factor']:
        if key in all_metrics:
            value = all_metrics[key]
            if '%' in key:
                print(f"   {key:<25}: {value:>12.2f}%")
            else:
                print(f"   {key:<25}: {value:>12.4f}")

    # Risk Analysis
    print("\n⚠️  RISK ANALYSIS:")
    for key in ['Value at Risk (95%) %', 'Conditional VaR (95%) %', 'Treynor Ratio']:
        if key in all_metrics:
            value = all_metrics[key]
            if '%' in key:
                print(f"   {key:<25}: {value:>12.2f}%")
            else:
                print(f"   {key:<25}: {value:>12.4f}")

    # Save to CSV
    output_file = os.path.join(results_dir, 'comprehensive_trading_metrics.csv')
    metrics_df = pd.DataFrame.from_dict(all_metrics, orient='index', columns=['Value'])
    metrics_df.to_csv(output_file)

    print(f"\n✅ Comprehensive metrics saved to: {output_file}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
