# Docker Guide for NSE Backtesting Engine

## 🐳 **Quick Start**

### **Build and Run**
```bash
# Build the Docker image
docker build -t nse-backtesting-engine .

# Run interactively
docker run -it --name nse-backtest \
  -v $(pwd)/results:/app/results \
  nse-backtesting-engine

# Or use Docker Compose (recommended)
docker-compose up -d
```

## 🚀 **Docker Compose Usage (Recommended)**

### **Basic Commands**
```bash
# Start the container
docker-compose up -d

# Access the container shell
docker-compose exec nse-backtesting-engine bash

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### **Run Strategies**
```bash
# Run momentum strategy
docker-compose exec nse-backtesting-engine python run_momentum_strategy.py

# Run Riskfolio strategy
docker-compose exec nse-backtesting-engine python examples/nse_riskfolio_demo.py

# Run any strategy
docker-compose exec nse-backtesting-engine python strategies/sma_strategy.py
```

### **Start Jupyter Notebook**
```bash
# Start Jupyter service
docker-compose --profile jupyter up -d

# Access at: http://localhost:8889
```

## 🔧 **Advanced Usage**

### **Custom Strategy Development**
```bash
# Mount your local strategies for development
docker run -it \
  -v $(pwd)/strategies:/app/strategies \
  -v $(pwd)/results:/app/results \
  nse-backtesting-engine bash

# Then run your strategy
python strategies/my_custom_strategy.py
```

### **Data Persistence**
```bash
# Mount multiple directories
docker run -it \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/backtest_results:/app/backtest_results \
  -v $(pwd)/logs:/app/logs \
  nse-backtesting-engine
```

### **Resource Limits**
```bash
# Limit memory and CPU
docker run -it \
  --memory=4g \
  --cpus=2 \
  -v $(pwd)/results:/app/results \
  nse-backtesting-engine
```

## 📊 **Running Specific Strategies**

### **1. Momentum Strategy**
```bash
docker-compose exec nse-backtesting-engine python -c "
from strategies.momentum_strategy import MomentumStrategy
from engine.enhanced_zipline_runner import EnhancedZiplineRunner

strategy = MomentumStrategy()
runner = EnhancedZiplineRunner(
    strategy=strategy,
    bundle='nse-local-minute-bundle',
    start_date='2020-01-01',
    end_date='2021-01-01',
    capital_base=100000
)
results = runner.run()
print(f'Final Value: {results[\"portfolio_value\"].iloc[-1]:,.2f}')
"
```

### **2. Riskfolio Strategy**
```bash
docker-compose exec nse-backtesting-engine python examples/nse_riskfolio_demo.py
```

### **3. Volume-Price Strategy**
```bash
docker-compose exec nse-backtesting-engine python strategies/volume_price_strategy.py
```

## 🔍 **Debugging and Development**

### **Interactive Shell**
```bash
# Access container shell
docker-compose exec nse-backtesting-engine bash

# Or start a new container with shell
docker run -it nse-backtesting-engine bash
```

### **Check Dependencies**
```bash
docker-compose exec nse-backtesting-engine python -c "
import zipline
import pandas as pd
import numpy as np
import riskfolio as rp
print('All dependencies loaded successfully!')
print(f'Zipline version: {zipline.__version__}')
print(f'Pandas version: {pd.__version__}')
print(f'Riskfolio version: {rp.__version__}')
"
```

### **View Available Assets**
```bash
docker-compose exec nse-backtesting-engine python -c "
from zipline.data import bundles
bundle_data = bundles.load('nse-local-minute-bundle')
print('Available assets:')
for asset in bundle_data.asset_finder.retrieve_all():
    print(f'  {asset.symbol}: {asset.asset_name}')
"
```

## 📁 **File Structure in Container**

```
/app/
├── strategies/          # Trading strategies
├── engine/             # Core engine files
├── examples/           # Example scripts
├── utils/              # Utility functions
├── .zipline/           # Zipline data and config
├── results/            # Output results (mounted)
├── backtest_results/   # Backtest outputs (mounted)
└── logs/              # Log files (mounted)
```

## 🔧 **Environment Variables**

```bash
# Set custom environment variables
docker run -it \
  -e ZIPLINE_ROOT=/app/.zipline \
  -e PYTHONPATH=/app \
  -e LOG_LEVEL=DEBUG \
  nse-backtesting-engine
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Permission Issues**
```bash
# Fix permissions
docker-compose exec nse-backtesting-engine chown -R trader:trader /app/results
```

2. **Memory Issues**
```bash
# Increase memory limit
docker-compose down
# Edit docker-compose.yml to increase memory limit
docker-compose up -d
```

3. **Bundle Issues**
```bash
# Rebuild bundle
docker-compose exec nse-backtesting-engine python -c "
from zipline.data import bundles
bundles.ingest('nse-local-minute-bundle')
"
```

### **View Container Logs**
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f nse-backtesting-engine

# View specific service logs
docker logs nse-backtest-engine
```

## 🔄 **Updates and Maintenance**

### **Rebuild Image**
```bash
# Rebuild after code changes
docker-compose build --no-cache

# Or rebuild specific service
docker-compose build nse-backtesting-engine
```

### **Clean Up**
```bash
# Remove containers and images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```

## 🎯 **Production Deployment**

### **Docker Swarm**
```bash
# Deploy to swarm
docker stack deploy -c docker-compose.yml nse-backtest-stack
```

### **Kubernetes**
```bash
# Convert to Kubernetes (using kompose)
kompose convert
kubectl apply -f .
```

## 📊 **Performance Monitoring**

### **Resource Usage**
```bash
# Monitor container resources
docker stats nse-backtest-engine

# View container processes
docker-compose exec nse-backtesting-engine top
```

This Docker setup provides a complete, isolated environment for your NSE backtesting engine with all dependencies pre-installed and configured!
