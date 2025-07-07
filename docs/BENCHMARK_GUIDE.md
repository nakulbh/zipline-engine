# Benchmark Guide for NSE Backtesting Engine

## 🎯 **What are Benchmarks?**

Benchmarks are reference indices or assets used to evaluate your strategy's performance. Instead of just looking at absolute returns, benchmarks help you understand:

- **Relative Performance**: How did your strategy perform vs the market?
- **Risk-Adjusted Returns**: Are you getting compensated for the risk taken?
- **Market Context**: Did you outperform during bull/bear markets?

## 📊 **Available NSE Benchmarks**

Your NSE backtesting engine supports these benchmarks:

| Symbol | Description | Use Case |
|--------|-------------|----------|
| `NIFTY50` | Nifty 50 Index | Broad market benchmark |
| `BANKNIFTY` | Bank Nifty Index | Banking sector strategies |
| `SBIN` | State Bank of India | Banking stock comparison |
| `RELIANCE` | Reliance Industries | Large-cap stock comparison |
| `HDFCBANK` | HDFC Bank | Banking stock comparison |
| `BAJFINANCE` | Bajaj Finance | Financial services comparison |
| `HDFC` | HDFC Ltd | Financial services comparison |
| `HINDALCO` | Hindalco Industries | Industrial stock comparison |

## 🚀 **How to Add Benchmarks**

### **Method 1: Strategy-Level Benchmark (Recommended)**

Set the benchmark when creating your strategy:

```python
from strategies.bollinger_strategy import BollingerBandsStrategy

# Create strategy with benchmark
strategy = BollingerBandsStrategy(
    bb_period=20,
    bb_std=2.0,
    benchmark_symbol='NIFTY50'  # Set benchmark here
)

# Runner will use strategy's benchmark
runner = EnhancedZiplineRunner(
    strategy=strategy,
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2021-01-01',
    capital_base=100000
)
```

### **Method 2: Runner-Level Benchmark**

Set the benchmark in the runner (overrides strategy benchmark):

```python
from strategies.momentum_strategy import MomentumStrategy

strategy = MomentumStrategy()

# Set benchmark in runner
runner = EnhancedZiplineRunner(
    strategy=strategy,
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2021-01-01',
    capital_base=100000,
    benchmark_symbol='BANKNIFTY'  # Runner benchmark
)
```

### **Method 3: Custom Strategy with Benchmark**

Create your own strategy with benchmark support:

```python
from engine.enhanced_base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, benchmark_symbol='NIFTY50'):
        super().__init__()
        self.benchmark_symbol = benchmark_symbol  # Add this line
        
        # Your strategy parameters
        self.my_param = 10
        
    def select_universe(self, context):
        # Your universe selection
        return [symbol('SBIN'), symbol('RELIANCE')]
        
    def generate_signals(self, context, data):
        # Your signal generation logic
        return {asset: 0.5 for asset in context.universe}
```

## 🔧 **Benchmark Selection Guidelines**

### **For Broad Market Strategies**
```python
benchmark_symbol='NIFTY50'  # Best for diversified strategies
```

### **For Banking/Financial Strategies**
```python
benchmark_symbol='BANKNIFTY'  # Best for banking sector focus
```

### **For Single Stock Strategies**
```python
benchmark_symbol='SBIN'  # Use relevant stock as benchmark
```

### **For Sector-Specific Strategies**
Choose the most representative asset from that sector.

## 📈 **Benchmark Comparison Example**

Compare your strategy against multiple benchmarks:

```python
benchmarks = ['NIFTY50', 'BANKNIFTY', 'SBIN']
results = {}

for benchmark in benchmarks:
    strategy = MyStrategy(benchmark_symbol=benchmark)
    runner = EnhancedZiplineRunner(strategy=strategy, ...)
    results[benchmark] = runner.run()

# Compare performance
for benchmark, result in results.items():
    final_value = result['portfolio_value'].iloc[-1]
    total_return = (final_value / 100000 - 1) * 100
    print(f"{benchmark}: {total_return:.2f}% return")
```

## 🎯 **Best Practices**

### **1. Choose Relevant Benchmarks**
- **Broad strategies** → Use `NIFTY50`
- **Sector strategies** → Use sector-specific index
- **Single stock** → Use that stock or sector leader

### **2. Consistent Comparison**
- Use the same benchmark across similar strategies
- Document why you chose specific benchmarks

### **3. Multiple Benchmark Analysis**
- Test against 2-3 different benchmarks
- Understand performance in different market contexts

### **4. Risk-Adjusted Metrics**
- Don't just look at returns
- Consider Sharpe ratio vs benchmark
- Analyze drawdowns relative to benchmark

## 📊 **Benchmark Analysis Output**

When you run backtests with benchmarks, you get:

### **Pyfolio Analysis**
- Returns comparison charts
- Risk-adjusted metrics
- Drawdown analysis vs benchmark
- Rolling performance comparison

### **CSV Exports**
- `basic_results.csv` - Portfolio vs benchmark performance
- `performance_stats.csv` - Comparative metrics
- `trade_book.csv` - Individual trade analysis

### **Visual Charts**
- Cumulative returns comparison
- Rolling Sharpe ratio vs benchmark
- Drawdown comparison
- Monthly/yearly performance breakdown

## 🚀 **Quick Start Commands**

### **Run with NIFTY50 benchmark:**
```bash
python examples/benchmark_examples.py
```

### **Test your strategy with benchmark:**
```python
# In your strategy file
strategy = MyStrategy(benchmark_symbol='NIFTY50')
runner = EnhancedZiplineRunner(strategy=strategy, ...)
results = runner.run()
```

### **Compare multiple benchmarks:**
```python
python examples/benchmark_examples.py  # Runs comparison demo
```

## 🔍 **Troubleshooting**

### **Benchmark not found error:**
```
❌ Failed to set benchmark INVALID_SYMBOL
```
**Solution**: Use only available NSE symbols from the list above.

### **No benchmark comparison in results:**
```
⚠️ Benchmark data not available
```
**Solution**: Ensure benchmark symbol exists in your data bundle.

### **Benchmark override warning:**
```
⚠️ Runner benchmark overrides strategy benchmark
```
**Solution**: This is normal - runner benchmark takes precedence.

## 💡 **Advanced Tips**

1. **Dynamic Benchmarks**: Change benchmark based on market conditions
2. **Multiple Benchmarks**: Run same strategy against different benchmarks
3. **Custom Benchmarks**: Create composite benchmarks from multiple assets
4. **Sector Rotation**: Use different benchmarks for different time periods

Benchmarks are crucial for understanding whether your strategy is actually adding value beyond market returns!
