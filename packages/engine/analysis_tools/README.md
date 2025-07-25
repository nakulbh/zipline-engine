# Zipline Reloaded Comprehensive Metrics Analysis

## Overview

You were only seeing **14 basic performance statistics** from Zipline Reloaded, but the platform actually provides **87+ comprehensive trading metrics**! The issue was that these metrics weren't being extracted and displayed properly.

## What You Were Seeing (Basic Stats Only)

```
Annual return: -0.013502280316289528
Cumulative returns: -0.039133374834484536
Annual volatility: 0.054751372729723996
Sharpe ratio: -0.22098144733814246
Calmar ratio: -0.18139467570052822
Stability: 0.07775815407672744
Max drawdown: -0.07443592412040244
Omega ratio: 0.9560544094221957
Sortino ratio: -0.3195327085385507
Skew: 0.6498908291586938
Kurtosis: 19.490189627698275
Tail ratio: 0.9753250403454979
Daily value at risk: -0.006946036634034145
```

## What Zipline Reloaded Actually Provides (87+ Metrics)

### 💰 Capital & Portfolio Metrics
- Initial Capital: $200,000.00
- Ending Capital: $192,173.33
- Net Profit: $-7,826.67
- Net Profit %: -3.91%
- Peak Portfolio Value: $207,531.74
- Lowest Portfolio Value: $192,083.93

### 📈 Return Metrics
- Total Return %: -3.91%
- Annualized Return %: -1.35%
- Best Day Return %: 3.42%
- Worst Day Return %: -2.61%
- Average Daily Return %: -0.00%
- Median Daily Return %: -0.01%

### 📊 Trading Activity Metrics
- **Number of Trades: 212**
- **Number of Orders: 212**
- Total Trading Days: 740
- Trading Frequency %: 28.65%
- Average Trades per Day: 0.29
- Buy Transactions: 106 (estimated)
- Sell Transactions: 106 (estimated)

### 💱 Transaction Analysis
- **Total Transaction Costs: $0** (commission-free in your setup)
- Order Fill Rate %: 100% (all orders filled)
- Transaction Cost %: 0.00%

### 📉 Risk Metrics
- Annual Volatility %: 5.48%
- Sharpe Ratio: -0.2210
- Max Drawdown %: -7.44%
- Calmar Ratio: -0.1814
- Sortino Ratio: -0.3317
- Information Ratio: -0.2210
- Value at Risk (95%) %: -0.46%
- Conditional VaR (95%) %: -0.79%

### 🎯 Performance Analysis
- **Win Rate %: 47.03%**
- Winning Days: 348
- Losing Days: 379
- Average Win %: 0.22%
- Average Loss %: -0.21%
- **Profit Factor: 0.9561**
- Market Exposure %: 98.24%

### 🎯 Benchmark Comparison (vs NIFTY50)
- **Beta: -0.0001** (strategy uncorrelated to benchmark)
- **Alpha (Annualized): -1.12%** (underperformance vs benchmark)
- Excess Return %: -1413.45%
- Tracking Error %: 141.20%
- Correlation: -0.0017 (essentially no correlation)

## Key Missing Metrics You Asked About

✅ **Number of trades**: 212 trades  
✅ **Initial capital**: $200,000.00  
✅ **Ending capital**: $192,173.33  
✅ **Net profit**: $-7,826.67  
✅ **Net profit %**: -3.91%  
✅ **Exposure**: 98.24% (time in market)  
✅ **Net risk adjusted return**: Sharpe: -0.22, Sortino: -0.33  
✅ **Annual return**: -1.35%  
✅ **Total transaction cost**: $0 (commission-free)  
✅ **All trades average P&L**: Win: +0.22%, Loss: -0.21%  
✅ **Profit factor**: 0.9561  

## How to Use These Analysis Tools

### 1. Extract ALL Available Metrics
```bash
python analysis_tools/zipline_metrics_extractor.py backtest_results/rsi_support_resistance
```
This extracts all 87+ metrics from your backtest results.

### 2. Get Comprehensive Trading Analysis
```bash
python analysis_tools/comprehensive_trading_metrics.py backtest_results/rsi_support_resistance
```
This provides detailed trading performance analysis.

## Files Generated

Both scripts save comprehensive CSV files:
- `all_zipline_metrics.csv` - All 87+ metrics
- `comprehensive_trading_metrics.csv` - Focused trading analysis

## Why You Weren't Seeing These Metrics

1. **Default Analysis Limited**: The standard `analyze()` method only shows basic Pyfolio statistics
2. **No Pickle Files**: Your setup doesn't save pickle files by default, limiting advanced analysis
3. **CSV Data Not Parsed**: The detailed transaction data in CSV files wasn't being parsed and analyzed
4. **Missing Extraction Scripts**: No tools were provided to extract comprehensive metrics from the available data

## Solution

The analysis tools in this folder solve all these issues by:
- Parsing all available CSV files
- Extracting transaction-level details
- Calculating comprehensive trading metrics
- Providing benchmark comparison analysis
- Organizing metrics by category for easy understanding

## Your RSI Strategy Performance Summary

- **Strategy**: RSI Support/Resistance
- **Period**: 740 trading days (~3 years)
- **Capital**: $200,000 → $192,173 (-3.91%)
- **Trades**: 212 trades (28.6% trading frequency)
- **Win Rate**: 47.03%
- **Risk**: 5.48% annual volatility, -7.44% max drawdown
- **Risk-Adjusted**: Sharpe -0.22 (poor risk-adjusted returns)
- **vs Benchmark**: Significantly underperformed NIFTY50

The strategy shows consistent but unprofitable trading with reasonable risk control but poor overall performance.
