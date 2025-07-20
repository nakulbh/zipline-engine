#!/usr/bin/env python3
"""
Extract Detailed Trade-Level Metrics from Zipline Results

This script uses Pyfolio to extract comprehensive trade-level metrics
including round trip analysis, transaction costs, and detailed trading statistics.

Usage:
    python extract_detailed_trade_metrics.py <pickle_file_path>
    
Example:
    python extract_detailed_trade_metrics.py backtest_results/rsi_support_resistance/backtest_results.pickle
"""

import os
import sys
import pandas as pd
import numpy as np
import pyfolio as pf
import warnings
warnings.filterwarnings("ignore")

def analyze_pickle_results(pickle_path):
    """
    Analyze pickle results and extract comprehensive trade metrics
    """
    print(f"🔍 Loading backtest results from: {pickle_path}")
    
    # Load the pickle file
    try:
        perf = pd.read_pickle(pickle_path)
        print(f"📊 Loaded {len(perf)} periods of backtest data")
    except Exception as e:
        print(f"❌ Failed to load pickle file: {e}")
        return None
    
    # Extract returns, positions, transactions using Pyfolio
    try:
        returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)
        
        print(f"📈 Returns: {len(returns)} data points")
        print(f"📊 Positions: {len(positions) if positions is not None else 0} records")
        print(f"💱 Transactions: {len(transactions) if transactions is not None else 0} records")
        
    except Exception as e:
        print(f"❌ Failed to extract data: {e}")
        return None
    
    return perf, returns, positions, transactions

def extract_transaction_metrics(transactions):
    """
    Extract detailed transaction-level metrics
    """
    if transactions is None or transactions.empty:
        print("⚠️  No transaction data available")
        return {}
    
    print("\n💱 ANALYZING TRANSACTIONS...")
    
    metrics = {}
    
    # Basic transaction stats
    total_transactions = len(transactions)
    buy_transactions = transactions[transactions['amount'] > 0]
    sell_transactions = transactions[transactions['amount'] < 0]
    
    metrics['Total Transactions'] = total_transactions
    metrics['Buy Transactions'] = len(buy_transactions)
    metrics['Sell Transactions'] = len(sell_transactions)
    
    # Transaction amounts
    total_volume = transactions['amount'].abs().sum()
    avg_transaction_size = transactions['amount'].abs().mean()
    
    metrics['Total Volume'] = total_volume
    metrics['Average Transaction Size'] = avg_transaction_size
    
    # Transaction costs (if available)
    if 'commission' in transactions.columns:
        total_commissions = transactions['commission'].sum()
        avg_commission = transactions['commission'].mean()
        
        metrics['Total Transaction Costs'] = total_commissions
        metrics['Average Commission per Trade'] = avg_commission
    
    # Price analysis
    if 'price' in transactions.columns:
        avg_buy_price = buy_transactions['price'].mean() if len(buy_transactions) > 0 else 0
        avg_sell_price = sell_transactions['price'].mean() if len(sell_transactions) > 0 else 0
        
        metrics['Average Buy Price'] = avg_buy_price
        metrics['Average Sell Price'] = avg_sell_price
    
    return metrics

def extract_round_trip_metrics(transactions):
    """
    Extract round trip (complete trade) metrics using Pyfolio
    """
    if transactions is None or transactions.empty:
        print("⚠️  No transaction data for round trip analysis")
        return {}
    
    print("\n🔄 ANALYZING ROUND TRIPS...")
    
    try:
        # Extract round trips
        round_trips = pf.round_trips.extract_round_trips(transactions)
        
        if round_trips.empty:
            print("⚠️  No complete round trips found")
            return {}
        
        print(f"📊 Found {len(round_trips)} complete round trips")
        
        metrics = {}
        
        # Basic round trip stats
        metrics['Total Round Trips'] = len(round_trips)
        
        # PnL analysis
        total_pnl = round_trips['pnl'].sum()
        avg_pnl = round_trips['pnl'].mean()
        median_pnl = round_trips['pnl'].median()
        
        metrics['Total PnL from Round Trips'] = total_pnl
        metrics['Average PnL per Round Trip'] = avg_pnl
        metrics['Median PnL per Round Trip'] = median_pnl
        
        # Win/Loss analysis
        winning_trades = round_trips[round_trips['pnl'] > 0]
        losing_trades = round_trips[round_trips['pnl'] < 0]
        
        metrics['Winning Round Trips'] = len(winning_trades)
        metrics['Losing Round Trips'] = len(losing_trades)
        metrics['Round Trip Win Rate %'] = (len(winning_trades) / len(round_trips)) * 100
        
        # Average win/loss
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        metrics['Average Winning Trade'] = avg_win
        metrics['Average Losing Trade'] = avg_loss
        
        # Profit factor for round trips
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        metrics['Round Trip Profit Factor'] = profit_factor
        
        # Holding period analysis
        if 'duration' in round_trips.columns:
            avg_holding_period = round_trips['duration'].mean()
            median_holding_period = round_trips['duration'].median()
            
            metrics['Average Holding Period (days)'] = avg_holding_period.days if hasattr(avg_holding_period, 'days') else avg_holding_period
            metrics['Median Holding Period (days)'] = median_holding_period.days if hasattr(median_holding_period, 'days') else median_holding_period
        
        # Return analysis
        if 'returns' in round_trips.columns:
            avg_return = round_trips['returns'].mean()
            median_return = round_trips['returns'].median()
            
            metrics['Average Round Trip Return %'] = avg_return * 100
            metrics['Median Round Trip Return %'] = median_return * 100
        
        return metrics
        
    except Exception as e:
        print(f"⚠️  Round trip analysis failed: {e}")
        return {}

def extract_position_metrics(positions):
    """
    Extract position-level metrics
    """
    if positions is None or positions.empty:
        print("⚠️  No position data available")
        return {}
    
    print("\n📊 ANALYZING POSITIONS...")
    
    metrics = {}
    
    # Position count analysis
    total_positions = len(positions)
    
    # Calculate daily position counts
    daily_position_counts = positions.abs().sum(axis=1)
    avg_daily_positions = daily_position_counts.mean()
    max_daily_positions = daily_position_counts.max()
    
    metrics['Total Position Records'] = total_positions
    metrics['Average Daily Positions'] = avg_daily_positions
    metrics['Maximum Daily Positions'] = max_daily_positions
    
    # Position concentration
    if not positions.empty:
        # Get the maximum position size for each asset
        max_positions_per_asset = positions.abs().max()
        largest_position = max_positions_per_asset.max()
        
        metrics['Largest Single Position'] = largest_position
        
        # Count unique assets traded
        assets_traded = (positions != 0).any().sum()
        metrics['Number of Assets Traded'] = assets_traded
    
    return metrics

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_detailed_trade_metrics.py <pickle_file_path>")
        print("Example: python extract_detailed_trade_metrics.py backtest_results/rsi_support_resistance/backtest_results.pickle")
        sys.exit(1)
    
    pickle_path = sys.argv[1]
    
    if not os.path.exists(pickle_path):
        print(f"❌ Pickle file not found: {pickle_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("🚀 DETAILED TRADE-LEVEL METRICS ANALYSIS")
    print("=" * 80)
    
    # Analyze pickle results
    result = analyze_pickle_results(pickle_path)
    if result is None:
        sys.exit(1)
    
    perf, returns, positions, transactions = result
    
    # Extract various metrics
    transaction_metrics = extract_transaction_metrics(transactions)
    round_trip_metrics = extract_round_trip_metrics(transactions)
    position_metrics = extract_position_metrics(positions)
    
    # Combine all metrics
    all_metrics = {**transaction_metrics, **round_trip_metrics, **position_metrics}
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 DETAILED TRADE-LEVEL METRICS")
    print("=" * 80)
    
    if transaction_metrics:
        print("\n💱 TRANSACTION METRICS:")
        for key, value in transaction_metrics.items():
            if isinstance(value, float):
                if 'Price' in key or 'Cost' in key or 'Commission' in key:
                    print(f"   {key:<30}: ${value:>12,.2f}")
                else:
                    print(f"   {key:<30}: {value:>12,.2f}")
            else:
                print(f"   {key:<30}: {value:>12}")
    
    if round_trip_metrics:
        print("\n🔄 ROUND TRIP METRICS:")
        for key, value in round_trip_metrics.items():
            if isinstance(value, float):
                if '%' in key:
                    print(f"   {key:<30}: {value:>12.2f}%")
                elif 'PnL' in key or 'Trade' in key:
                    print(f"   {key:<30}: ${value:>12,.2f}")
                elif 'days' in key:
                    print(f"   {key:<30}: {value:>12.1f}")
                else:
                    print(f"   {key:<30}: {value:>12.4f}")
            else:
                print(f"   {key:<30}: {value:>12}")
    
    if position_metrics:
        print("\n📊 POSITION METRICS:")
        for key, value in position_metrics.items():
            if isinstance(value, float):
                print(f"   {key:<30}: {value:>12.2f}")
            else:
                print(f"   {key:<30}: {value:>12}")
    
    # Save to CSV
    results_dir = os.path.dirname(pickle_path)
    output_file = os.path.join(results_dir, 'detailed_trade_metrics.csv')
    
    if all_metrics:
        metrics_df = pd.DataFrame.from_dict(all_metrics, orient='index', columns=['Value'])
        metrics_df.to_csv(output_file)
        print(f"\n✅ Detailed trade metrics saved to: {output_file}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
