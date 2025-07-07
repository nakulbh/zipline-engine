# Pickle & Pyfolio Workflow Guide

This guide explains how to save backtest results to pickle files and use Pyfolio for comprehensive analysis, exactly as requested.

## Overview

The NSE Backtesting Engine now supports:
1. **Saving backtest results to pickle files** for persistent storage
2. **Loading results from pickle files** for analysis
3. **Creating comprehensive Pyfolio analysis** from pickle files
4. **Generating both portfolio-level and trade-level performance metrics**

## Quick Start

### Method 1: Complete Workflow

```python
from engine.enhanced_zipline_runner import EnhancedZiplineRunner
from strategies.volume_price_strategy import VolumePriceTrendStrategy

# 1. Run backtest
strategy = VolumePriceTrendStrategy()
runner = EnhancedZiplineRunner(
    strategy=strategy,
    bundle='nse-local-minute-bundle',
    start_date='2019-01-01',
    end_date='2020-01-01',
    capital_base=100000
)

results = runner.run()

# 2. Save to pickle
pickle_path = runner.save_results_to_pickle(
    filename="my_backtest.pickle",
    results_dir="results"
)

# 3. Create Pyfolio analysis from pickle
runner.create_pyfolio_analysis_from_pickle(
    pickle_filepath=pickle_path,
    results_dir="results/pyfolio_analysis",
    save_plots=True,
    save_csv=True
)
```

### Method 2: Direct Pyfolio Analysis (Your Requested Approach)

```python
import pandas as pd
import pyfolio as pf

# Load results from pickle (as you requested)
perf = pd.read_pickle("my_backtest.pickle")

# Extract data (as you requested)
returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)

# Portfolio-level performance metrics (as you requested)
pf.create_full_tear_sheet(returns, positions, transactions)

# Individual trades performance metrics (as you requested)
pf.create_round_trip_tear_sheet(returns, positions, transactions)
```

## Available Methods

### `save_results_to_pickle(filename=None, results_dir='backtest_results')`

Saves backtest results to a pickle file.

**Parameters:**
- `filename` (str, optional): Name of pickle file. Auto-generated if None.
- `results_dir` (str): Directory to save the file.

**Returns:** Path to saved pickle file

**Example:**
```python
pickle_path = runner.save_results_to_pickle(
    filename="strategy_results.pickle",
    results_dir="my_results"
)
```

### `load_results_from_pickle(filepath)`

Loads backtest results from a pickle file.

**Parameters:**
- `filepath` (str): Path to the pickle file

**Returns:** Loaded pandas DataFrame

**Example:**
```python
results = runner.load_results_from_pickle("my_results/strategy_results.pickle")
```

### `create_pyfolio_analysis_from_pickle(pickle_filepath, results_dir, ...)`

Creates comprehensive Pyfolio analysis from a pickle file.

**Parameters:**
- `pickle_filepath` (str): Path to pickle file
- `results_dir` (str): Directory to save analysis
- `live_start_date` (str, optional): Date for out-of-sample analysis
- `save_plots` (bool): Whether to save plots as PNG files
- `save_csv` (bool): Whether to save data as CSV files

**Example:**
```python
runner.create_pyfolio_analysis_from_pickle(
    pickle_filepath="results/my_backtest.pickle",
    results_dir="analysis",
    live_start_date="2020-01-01",  # Out-of-sample analysis
    save_plots=True,
    save_csv=True
)
```

## Generated Outputs

### Pickle Files
- **`*.pickle`**: Serialized backtest results for later analysis

### Pyfolio Analysis
- **`full_tear_sheet.png`**: Complete portfolio performance analysis
- **`round_trip_tear_sheet.png`**: Individual trades analysis
- **`returns.csv`**: Daily returns data
- **`positions.csv`**: Position data over time
- **`transactions.csv`**: All trade transactions

## Example Scripts

### 1. Complete Workflow Demo
```bash
python examples/pickle_pyfolio_workflow.py
```

### 2. Analyze Existing Pickle File
```bash
python examples/analyze_pickle_results.py my_backtest.pickle
```

### 3. Quick Demo
```bash
python examples/demo_pickle_workflow.py
```

## Performance Metrics Generated

### Portfolio-Level Metrics (Full Tear Sheet)
- **Returns Analysis**: Cumulative returns, rolling returns
- **Risk Metrics**: Sharpe ratio, Sortino ratio, volatility
- **Drawdown Analysis**: Maximum drawdown, drawdown periods
- **Rolling Performance**: Rolling Sharpe, rolling volatility
- **Monthly/Annual Returns**: Performance breakdown by period

### Trade-Level Metrics (Round Trip Tear Sheet)
- **Individual Trade Analysis**: Profit/loss per trade
- **Trade Duration**: Holding periods for each position
- **Win/Loss Analysis**: Win rate, average win/loss
- **Trade Distribution**: Histogram of trade returns

## Best Practices

1. **Consistent Naming**: Use descriptive filenames for pickle files
2. **Directory Organization**: Keep results organized in separate directories
3. **Out-of-Sample Analysis**: Use `live_start_date` for realistic performance assessment
4. **Data Backup**: Keep pickle files as backup for important backtests
5. **Regular Cleanup**: Remove old pickle files to save disk space

## Troubleshooting

### Common Issues

**Issue**: "No transactions available for round trip analysis"
**Solution**: Ensure your strategy generates actual trades, not just position changes.

**Issue**: "Failed to extract positions/transactions"
**Solution**: Check that your backtest completed successfully and generated trade data.

**Issue**: "Pickle file not found"
**Solution**: Verify the file path and ensure the pickle file was saved successfully.

### Getting Help

If you encounter issues:
1. Check the log output for detailed error messages
2. Verify your strategy generates trades
3. Ensure sufficient data is available for the backtest period
4. Check that all required NSE assets are available in your bundle

## Integration with Existing Code

This functionality integrates seamlessly with your existing NSE backtesting engine:
- All existing strategies work without modification
- Standard analysis methods remain available
- Pickle functionality is optional and doesn't affect normal operation
