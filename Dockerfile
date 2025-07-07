# NSE Backtesting Engine Dockerfile
# ===================================
# 
# This Dockerfile creates a containerized environment for the NSE Backtesting Engine
# with all dependencies, data bundles, and configurations pre-installed.
#
# Build: docker build -t nse-backtesting-engine .
# Run:   docker run -it --name nse-backtest -v $(pwd)/results:/app/results nse-backtesting-engine

FROM python:3.10-slim

# Set metadata
LABEL maintainer="NSE Backtesting Engine"
LABEL description="Professional backtesting engine for NSE stocks using zipline-reloaded"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ZIPLINE_ROOT=/app/.zipline
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    pkg-config \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml uv.lock ./
COPY setup.py ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Install additional dependencies from setup.py
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/.zipline/data \
    /app/results \
    /app/logs \
    /app/backtest_results \
    /app/pickle_results

# Copy the entire project
COPY . .

# Copy zipline configuration and data
COPY .zipline/ /app/.zipline/

# Set proper permissions
RUN chmod +x /app/ingest_bundle.sh 2>/dev/null || true
RUN chmod -R 755 /app

# Create a non-root user for security
RUN useradd -m -u 1000 trader && \
    chown -R trader:trader /app
USER trader

# Set up Zipline environment
ENV ZIPLINE_ROOT=/app/.zipline

# Expose port for Jupyter notebooks (optional)
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import zipline; import pandas; import numpy; print('OK')" || exit 1

# Default command - run interactive shell
CMD ["/bin/bash"]

# Alternative commands (uncomment as needed):
# CMD ["python", "examples/nse_riskfolio_demo.py"]
# CMD ["python", "run_momentum_strategy.py"]
# CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
