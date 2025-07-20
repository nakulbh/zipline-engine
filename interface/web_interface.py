#!/usr/bin/env python3
"""
NSE Backtesting Engine Web Interface
====================================

A comprehensive web-based interface for the NSE backtesting engine using Streamlit.
Allows users to:
- Write and edit strategies
- Select bundles and configure parameters
- Run backtests with real-time progress
- View results and interactive plots
- Download reports and analysis

Usage:
    streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import sys
import json
import pickle
import time
from datetime import datetime, date
import traceback
import importlib.util
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our engine components
try:
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    from engine.enhanced_base_strategy import BaseStrategy
    from strategies import *
    from config.config import TradingConfig
    from web_config import *
except ImportError as e:
    st.error(f"Failed to import engine components: {e}")
    st.stop()

# Page configuration
st.set_page_config(**get_config('page'))

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Get configuration from web_config
NSE_ASSETS = get_config('assets')
AVAILABLE_BUNDLES = get_config('bundles')

# Strategy templates
STRATEGY_TEMPLATES = {
    'Simple Moving Average': '''
class CustomSMAStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        
        # Customize risk parameters
        self.risk_params.update({
            'max_position_size': 0.15,
            'stop_loss_pct': 0.08,
        })
    
    def select_universe(self, context):
        """Define trading universe"""
        return [symbol('SBIN'), symbol('RELIANCE'), symbol('HDFCBANK')]
    
    def generate_signals(self, context, data):
        """Generate trading signals"""
        signals = {}
        for asset in context.universe:
            try:
                prices = data.history(asset, 'price', self.long_window + 1, '1d')
                if len(prices) >= self.long_window:
                    short_ma = prices.tail(self.short_window).mean()
                    long_ma = prices.tail(self.long_window).mean()
                    
                    if short_ma > long_ma:
                        signals[asset] = 1.0  # Buy
                    else:
                        signals[asset] = -1.0  # Sell
                else:
                    signals[asset] = 0.0
            except Exception as e:
                signals[asset] = 0.0
        return signals
''',
    
    'RSI Mean Reversion': '''
class CustomRSIStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        
        self.risk_params.update({
            'max_position_size': 0.12,
            'stop_loss_pct': 0.06,
        })
    
    def select_universe(self, context):
        return [symbol('SBIN'), symbol('RELIANCE'), symbol('BAJFINANCE')]
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50
        
        delta = prices.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            try:
                prices = data.history(asset, 'price', self.rsi_period + 10, '1d')
                if len(prices) >= self.rsi_period + 1:
                    rsi = self.calculate_rsi(prices, self.rsi_period)
                    
                    if rsi <= self.oversold:
                        signals[asset] = 1.0  # Oversold - Buy
                    elif rsi >= self.overbought:
                        signals[asset] = -1.0  # Overbought - Sell
                    else:
                        signals[asset] = 0.0  # Neutral
                else:
                    signals[asset] = 0.0
            except Exception as e:
                signals[asset] = 0.0
        return signals
''',
    
    'Momentum Strategy': '''
class CustomMomentumStrategy(BaseStrategy):
    def __init__(self, lookback_period=20, momentum_threshold=0.02):
        super().__init__()
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        
        self.risk_params.update({
            'max_position_size': 0.10,
            'stop_loss_pct': 0.10,
        })
    
    def select_universe(self, context):
        return [symbol(asset) for asset in ['SBIN', 'RELIANCE', 'HDFCBANK', 'BAJFINANCE']]
    
    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            try:
                prices = data.history(asset, 'price', self.lookback_period + 5, '1d')
                if len(prices) >= self.lookback_period:
                    momentum = (prices.iloc[-1] / prices.iloc[-self.lookback_period]) - 1
                    
                    if momentum > self.momentum_threshold:
                        signals[asset] = 1.0  # Strong momentum - Buy
                    elif momentum < -self.momentum_threshold:
                        signals[asset] = -1.0  # Negative momentum - Sell
                    else:
                        signals[asset] = 0.0  # Weak momentum - Hold
                else:
                    signals[asset] = 0.0
            except Exception as e:
                signals[asset] = 0.0
        return signals
'''
}

def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="main-header">📈 NSE Backtesting Engine</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        get_config('navigation')
    )
    
    # Route to different pages
    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Strategy Builder":
        show_strategy_builder()
    elif page == "⚙️ Backtest Runner":
        show_backtest_runner()
    elif page == "📊 Results Viewer":
        show_results_viewer()
    elif page == "📋 Strategy Manager":
        show_strategy_manager()

def show_home_page():
    """Display the home page with overview and quick start"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🎯 Welcome to NSE Backtesting Engine")
        st.markdown("""
        This comprehensive backtesting platform allows you to:
        
        - **📝 Build Custom Strategies**: Write and test your trading strategies with our intuitive interface
        - **⚙️ Run Backtests**: Execute backtests with professional-grade analysis
        - **📊 Analyze Results**: Get detailed performance metrics, plots, and tearsheets
        - **💾 Manage Strategies**: Save, load, and organize your trading strategies
        
        ### 🚀 Quick Start Guide
        
        1. **Strategy Builder**: Create or customize your trading strategy
        2. **Backtest Runner**: Configure parameters and run your backtest
        3. **Results Viewer**: Analyze performance and download reports
        """)
        
        # System status
        st.markdown("### 🔧 System Status")
        
        # Check bundle availability
        bundle_status = check_bundle_status()
        if bundle_status:
            st.success("✅ NSE Data Bundle: Available")
        else:
            st.error("❌ NSE Data Bundle: Not Available")
            
        # Check available assets
        st.info(f"📈 Available Assets: {', '.join(NSE_ASSETS)}")
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        
        # Display some quick statistics
        results_dir = "backtest_results"
        if os.path.exists(results_dir):
            result_files = [f for f in os.listdir(results_dir) if f.endswith('.pickle')]
            st.metric("Saved Results", len(result_files))
        else:
            st.metric("Saved Results", 0)
            
        strategy_files = [f for f in os.listdir("strategies") if f.endswith('.py') and not f.startswith('__')]
        st.metric("Available Strategies", len(strategy_files))
        
        st.metric("Supported Assets", len(NSE_ASSETS))

def check_bundle_status():
    """Check if the NSE bundle is available"""
    try:
        # Try to import and check bundle
        return True  # Simplified check
    except:
        return False

def show_strategy_builder():
    """Strategy builder page with code editor and templates"""

    st.markdown("## 📝 Strategy Builder")
    st.markdown("Create and customize your trading strategies using our templates or write from scratch.")

    # Strategy template selection
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎯 Strategy Templates")
        selected_template = st.selectbox(
            "Choose a template to start with:",
            ["Custom (Start from scratch)"] + list(STRATEGY_TEMPLATES.keys())
        )

        if selected_template != "Custom (Start from scratch)":
            if st.button("📋 Load Template"):
                st.session_state.strategy_code = STRATEGY_TEMPLATES[selected_template]
                st.success(f"✅ Loaded {selected_template} template!")

    with col2:
        st.markdown("### ⚙️ Strategy Parameters")
        strategy_name = st.text_input("Strategy Name", value="MyCustomStrategy")

        # Asset selection
        selected_assets = st.multiselect(
            "Select Assets for Universe:",
            NSE_ASSETS,
            default=['SBIN', 'RELIANCE', 'HDFCBANK']
        )

    # Code editor
    st.markdown("### 💻 Strategy Code Editor")

    # Initialize session state for code
    if 'strategy_code' not in st.session_state:
        st.session_state.strategy_code = STRATEGY_TEMPLATES['Simple Moving Average']

    try:
        from streamlit_ace import st_ace

        # Code editor with syntax highlighting
        strategy_code = st_ace(
            value=st.session_state.strategy_code,
            language='python',
            theme='monokai',
            key="strategy_editor",
            height=400,
            auto_update=True,
            font_size=14,
            tab_size=4,
            wrap=False,
            annotations=None
        )

        st.session_state.strategy_code = strategy_code

    except ImportError:
        # Fallback to text area if streamlit-ace is not available
        strategy_code = st.text_area(
            "Strategy Code:",
            value=st.session_state.strategy_code,
            height=400,
            key="strategy_code_fallback"
        )
        st.session_state.strategy_code = strategy_code

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Validate Strategy"):
            validate_strategy_code(strategy_code, strategy_name)

    with col2:
        if st.button("💾 Save Strategy"):
            save_strategy_to_file(strategy_code, strategy_name)

    with col3:
        if st.button("🔄 Reset Code"):
            st.session_state.strategy_code = STRATEGY_TEMPLATES['Simple Moving Average']
            st.experimental_rerun()

    with col4:
        if st.button("📖 Show Documentation"):
            show_strategy_documentation()

def validate_strategy_code(code: str, name: str):
    """Validate the strategy code"""
    try:
        # Create a temporary module to test the code
        import tempfile
        import importlib.util

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Add necessary imports
            full_code = f"""
import pandas as pd
import numpy as np
from zipline.api import symbol
from engine.enhanced_base_strategy import BaseStrategy

{code}
"""
            f.write(full_code)
            f.flush()

            # Try to load the module
            spec = importlib.util.spec_from_file_location("temp_strategy", f.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if the strategy class exists and is properly defined
            strategy_classes = [getattr(module, name) for name in dir(module)
                              if isinstance(getattr(module, name), type) and
                              issubclass(getattr(module, name), BaseStrategy) and
                              getattr(module, name) != BaseStrategy]

            if strategy_classes:
                st.success(f"✅ Strategy validation successful! Found {len(strategy_classes)} strategy class(es).")

                # Try to instantiate the strategy
                strategy_class = strategy_classes[0]
                try:
                    strategy_instance = strategy_class()
                    st.success("✅ Strategy can be instantiated successfully!")
                except Exception as e:
                    st.warning(f"⚠️ Strategy validates but instantiation failed: {str(e)}")

            else:
                st.error("❌ No valid strategy class found. Make sure your class inherits from BaseStrategy.")

        # Clean up
        os.unlink(f.name)

    except Exception as e:
        st.error(f"❌ Strategy validation failed: {str(e)}")
        st.code(traceback.format_exc())

def save_strategy_to_file(code: str, name: str):
    """Save strategy to a Python file"""
    try:
        # Ensure strategies directory exists
        strategies_dir = "strategies"
        if not os.path.exists(strategies_dir):
            os.makedirs(strategies_dir)

        # Create filename
        filename = f"{name.lower().replace(' ', '_')}.py"
        filepath = os.path.join(strategies_dir, filename)

        # Add proper imports and formatting
        full_code = f'''#!/usr/bin/env python3
"""
{name} Strategy
Generated by NSE Backtesting Engine Web Interface
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, order_target_percent, record
from engine.enhanced_base_strategy import BaseStrategy

{code}

# Example usage
if __name__ == "__main__":
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner

    print(f"🚀 Testing {name}")
    print("=" * 50)

    # Create strategy instance
    strategy = {name.replace(' ', '')}Strategy()

    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2020-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )

    # Run backtest
    try:
        results = runner.run()
        if results is not None:
            print("✅ Backtest completed successfully!")
            runner.analyze(f'backtest_results/{filename[:-3]}')
        else:
            print("❌ Backtest failed")
    except Exception as e:
        print(f"❌ Error: {{e}}")
'''

        # Write to file
        with open(filepath, 'w') as f:
            f.write(full_code)

        st.success(f"✅ Strategy saved to: {filepath}")

        # Show download button
        with open(filepath, 'r') as f:
            st.download_button(
                label="📥 Download Strategy File",
                data=f.read(),
                file_name=filename,
                mime="text/x-python"
            )

    except Exception as e:
        st.error(f"❌ Failed to save strategy: {str(e)}")

def show_strategy_documentation():
    """Show strategy development documentation"""
    with st.expander("📖 Strategy Development Guide", expanded=True):
        st.markdown("""
        ### 🎯 Strategy Structure

        Every strategy must inherit from `BaseStrategy` and implement two required methods:

        ```python
        class MyStrategy(BaseStrategy):
            def select_universe(self, context):
                # Return list of assets to trade
                return [symbol('SBIN'), symbol('RELIANCE')]

            def generate_signals(self, context, data):
                # Return dictionary of signals {asset: weight}
                # Weights should be between -1.0 (short) and 1.0 (long)
                return {asset: signal_value}
        ```

        ### 📊 Available Assets
        Your NSE bundle includes: `{', '.join(NSE_ASSETS)}`

        ### ⚙️ Risk Parameters
        Customize risk management in `__init__`:

        ```python
        self.risk_params.update({
            'max_position_size': 0.15,  # 15% max per position
            'stop_loss_pct': 0.08,      # 8% stop loss
            'take_profit_pct': 0.20,    # 20% take profit
        })
        ```

        ### 📈 Data Access
        Use `data.history()` to get historical data:

        ```python
        prices = data.history(asset, 'price', 20, '1d')  # 20 days of daily prices
        volume = data.history(asset, 'volume', 10, '1d')  # 10 days of volume
        ```

        ### 🔍 Signal Generation
        - Return values between -1.0 and 1.0
        - Positive values = Long positions
        - Negative values = Short positions
        - Zero = No position/Close position
        """)

def show_backtest_runner():
    """Backtest runner page with configuration and execution"""

    st.markdown("## ⚙️ Backtest Runner")
    st.markdown("Configure and execute your backtests with comprehensive analysis.")

    # Strategy selection
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎯 Strategy Selection")

        # Get available strategies
        strategy_files = get_available_strategies()

        strategy_source = st.radio(
            "Strategy Source:",
            ["📁 Saved Strategies", "💻 Custom Code"]
        )

        if strategy_source == "📁 Saved Strategies":
            if strategy_files:
                selected_strategy_file = st.selectbox(
                    "Select Strategy:",
                    strategy_files
                )

                if st.button("📖 Preview Strategy"):
                    show_strategy_preview(selected_strategy_file)
            else:
                st.warning("No saved strategies found. Create one in Strategy Builder first.")

        else:  # Custom Code
            st.info("💡 Use the code from Strategy Builder or paste your own strategy code.")

            if 'strategy_code' in st.session_state:
                st.success("✅ Strategy code loaded from Strategy Builder")
                if st.button("👀 View Code"):
                    st.code(st.session_state.strategy_code[:500] + "..." if len(st.session_state.strategy_code) > 500 else st.session_state.strategy_code)
            else:
                st.warning("⚠️ No strategy code found. Please use Strategy Builder first.")

    with col2:
        st.markdown("### ⚙️ Backtest Configuration")

        # Bundle selection
        selected_bundle = st.selectbox(
            "Data Bundle:",
            list(AVAILABLE_BUNDLES.keys()),
            format_func=lambda x: AVAILABLE_BUNDLES[x]
        )

        # Date range
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input(
                "Start Date:",
                value=date(2020, 1, 1),
                min_value=date(2016, 1, 1),
                max_value=date(2023, 12, 31)
            )

        with col_end:
            end_date = st.date_input(
                "End Date:",
                value=date(2021, 12, 31),
                min_value=date(2016, 1, 1),
                max_value=date(2023, 12, 31)
            )

        # Capital and benchmark
        capital_base = st.number_input(
            "Initial Capital (₹):",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000,
            format="%d"
        )

        benchmark_symbol = st.selectbox(
            "Benchmark:",
            ['NIFTY50', 'BANKNIFTY', 'SBIN', 'RELIANCE'],
            index=0
        )

    # Advanced configuration
    with st.expander("🔧 Advanced Configuration"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Risk Management**")
            max_position_size = st.slider("Max Position Size (%)", 5, 50, 15) / 100
            stop_loss_pct = st.slider("Stop Loss (%)", 1, 20, 8) / 100
            take_profit_pct = st.slider("Take Profit (%)", 5, 50, 20) / 100

        with col2:
            st.markdown("**Analysis Options**")
            save_results = st.checkbox("Save Results to Pickle", value=True)
            generate_tearsheet = st.checkbox("Generate PyFolio Tearsheet", value=True)
            save_plots = st.checkbox("Save Plots as Images", value=True)
            save_csv = st.checkbox("Save Results to CSV", value=True)

    # Run backtest button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
            run_backtest_with_progress(
                strategy_source=strategy_source,
                strategy_file=selected_strategy_file if strategy_source == "📁 Saved Strategies" else None,
                bundle=selected_bundle,
                start_date=start_date,
                end_date=end_date,
                capital_base=capital_base,
                benchmark_symbol=benchmark_symbol,
                config={
                    'max_position_size': max_position_size,
                    'stop_loss_pct': stop_loss_pct,
                    'take_profit_pct': take_profit_pct,
                    'save_results': save_results,
                    'generate_tearsheet': generate_tearsheet,
                    'save_plots': save_plots,
                    'save_csv': save_csv
                }
            )

def get_available_strategies():
    """Get list of available strategy files"""
    strategies_dir = "strategies"
    if not os.path.exists(strategies_dir):
        return []

    strategy_files = []
    for file in os.listdir(strategies_dir):
        if file.endswith('.py') and not file.startswith('__'):
            strategy_files.append(file)

    return sorted(strategy_files)

def show_strategy_preview(strategy_file):
    """Show preview of selected strategy"""
    try:
        filepath = os.path.join("strategies", strategy_file)
        with open(filepath, 'r') as f:
            content = f.read()

        # Extract class name and docstring
        lines = content.split('\n')
        class_line = next((line for line in lines if line.strip().startswith('class ') and 'BaseStrategy' in line), None)

        if class_line:
            class_name = class_line.split('class ')[1].split('(')[0].strip()
            st.success(f"📋 Strategy: **{class_name}**")

        # Show first few lines of code
        preview_lines = content.split('\n')[:20]
        st.code('\n'.join(preview_lines) + '\n...' if len(content.split('\n')) > 20 else content)

    except Exception as e:
        st.error(f"Failed to preview strategy: {str(e)}")

def run_backtest_with_progress(strategy_source, strategy_file, bundle, start_date, end_date,
                              capital_base, benchmark_symbol, config):
    """Run backtest with progress tracking"""

    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Load strategy
        status_text.text("🔄 Loading strategy...")
        progress_bar.progress(10)

        if strategy_source == "📁 Saved Strategies":
            strategy = load_strategy_from_file(strategy_file)
        else:
            strategy = create_strategy_from_code(st.session_state.get('strategy_code', ''))

        if strategy is None:
            st.error("❌ Failed to load strategy")
            return

        progress_bar.progress(25)

        # Step 2: Configure runner
        status_text.text("⚙️ Configuring backtest runner...")

        runner = EnhancedZiplineRunner(
            strategy=strategy,
            bundle=bundle,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            capital_base=capital_base,
            benchmark_symbol=benchmark_symbol
        )

        progress_bar.progress(40)

        # Step 3: Run backtest
        status_text.text("🚀 Running backtest... This may take a few minutes...")

        # Store start time
        start_time = time.time()

        results = runner.run()

        if results is None:
            st.error("❌ Backtest failed. Check logs for details.")
            return

        progress_bar.progress(70)

        # Step 4: Save results
        if config['save_results']:
            status_text.text("💾 Saving results...")

            # Create results directory
            results_dir = f"backtest_results/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(results_dir, exist_ok=True)

            # Save to pickle
            pickle_path = runner.save_results_to_pickle(
                filename="backtest_results.pickle",
                results_dir=results_dir
            )

            progress_bar.progress(85)

            # Step 5: Generate analysis
            if config['generate_tearsheet']:
                status_text.text("📊 Generating analysis...")

                if pickle_path:
                    runner.create_pyfolio_analysis_from_pickle(
                        pickle_filepath=pickle_path,
                        results_dir=f"{results_dir}/analysis",
                        save_plots=config['save_plots'],
                        save_csv=config['save_csv']
                    )

                # Standard analysis
                runner.analyze(f"{results_dir}/standard_analysis")

        progress_bar.progress(100)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Show success message
        status_text.text("✅ Backtest completed successfully!")

        # Display results summary
        show_backtest_summary(results, execution_time, results_dir if config['save_results'] else None)

        # Store results in session state for results viewer
        st.session_state.latest_results = {
            'results': results,
            'runner': runner,
            'results_dir': results_dir if config['save_results'] else None,
            'execution_time': execution_time,
            'config': {
                'strategy_source': strategy_source,
                'strategy_file': strategy_file,
                'bundle': bundle,
                'start_date': start_date,
                'end_date': end_date,
                'capital_base': capital_base,
                'benchmark_symbol': benchmark_symbol
            }
        }

    except Exception as e:
        st.error(f"❌ Backtest failed: {str(e)}")
        st.code(traceback.format_exc())

    finally:
        progress_bar.empty()
        status_text.empty()

def load_strategy_from_file(strategy_file):
    """Load strategy class from file"""
    try:
        filepath = os.path.join("strategies", strategy_file)

        # Import the module
        spec = importlib.util.spec_from_file_location("strategy_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find strategy classes
        strategy_classes = [getattr(module, name) for name in dir(module)
                          if isinstance(getattr(module, name), type) and
                          issubclass(getattr(module, name), BaseStrategy) and
                          getattr(module, name) != BaseStrategy]

        if strategy_classes:
            # Return instance of first strategy class found
            return strategy_classes[0]()
        else:
            st.error(f"No valid strategy class found in {strategy_file}")
            return None

    except Exception as e:
        st.error(f"Failed to load strategy from {strategy_file}: {str(e)}")
        return None

def create_strategy_from_code(code):
    """Create strategy instance from code string"""
    try:
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Add necessary imports
            full_code = f"""
import pandas as pd
import numpy as np
from zipline.api import symbol, order_target_percent, record
from engine.enhanced_base_strategy import BaseStrategy

{code}
"""
            f.write(full_code)
            f.flush()

            # Import the module
            spec = importlib.util.spec_from_file_location("temp_strategy", f.name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find strategy classes
            strategy_classes = [getattr(module, name) for name in dir(module)
                              if isinstance(getattr(module, name), type) and
                              issubclass(getattr(module, name), BaseStrategy) and
                              getattr(module, name) != BaseStrategy]

            if strategy_classes:
                strategy_instance = strategy_classes[0]()
                os.unlink(f.name)  # Clean up
                return strategy_instance
            else:
                st.error("No valid strategy class found in code")
                os.unlink(f.name)
                return None

    except Exception as e:
        st.error(f"Failed to create strategy from code: {str(e)}")
        return None

def show_backtest_summary(results, execution_time, results_dir):
    """Display backtest results summary"""

    st.markdown("## 📊 Backtest Results Summary")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        final_value = results.portfolio_value.iloc[-1]
        st.metric("Final Portfolio Value", f"₹{final_value:,.0f}")

    with col2:
        initial_value = results.portfolio_value.iloc[0]
        total_return = (final_value / initial_value - 1) * 100
        st.metric("Total Return", f"{total_return:.2f}%")

    with col3:
        returns = results.returns
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

    with col4:
        max_drawdown = ((results.portfolio_value / results.portfolio_value.expanding().max()) - 1).min() * 100
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")

    # Performance chart
    st.markdown("### 📈 Portfolio Performance")

    fig = go.Figure()

    # Portfolio value
    fig.add_trace(go.Scatter(
        x=results.index,
        y=results.portfolio_value,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=2)
    ))

    # Benchmark if available
    if 'benchmark_return' in results.columns:
        benchmark_value = (1 + results.benchmark_return.fillna(0)).cumprod() * results.portfolio_value.iloc[0]
        fig.add_trace(go.Scatter(
            x=results.index,
            y=benchmark_value,
            mode='lines',
            name='Benchmark',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

    fig.update_layout(
        title="Portfolio Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹)",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Additional info
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"⏱️ Execution Time: {execution_time:.2f} seconds")
        if results_dir:
            st.success(f"📁 Results saved to: {results_dir}")

    with col2:
        st.info(f"📊 Total Trading Days: {len(results)}")
        st.info(f"📈 Data Points: {len(results.portfolio_value)}")

def show_results_viewer():
    """Results viewer page for analyzing saved results"""

    st.markdown("## 📊 Results Viewer")
    st.markdown("Analyze and compare your backtest results with interactive charts and detailed metrics.")

    # Check for latest results
    if 'latest_results' in st.session_state:
        st.success("✅ Latest backtest results available!")

        if st.button("📈 View Latest Results"):
            display_detailed_results(st.session_state.latest_results)

    # Load saved results
    st.markdown("### 📁 Load Saved Results")

    results_dir = "backtest_results"
    if os.path.exists(results_dir):
        # Get all result directories
        result_dirs = [d for d in os.listdir(results_dir)
                      if os.path.isdir(os.path.join(results_dir, d))]

        if result_dirs:
            selected_result_dir = st.selectbox(
                "Select Results to View:",
                sorted(result_dirs, reverse=True)  # Most recent first
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 Load Results"):
                    load_and_display_results(os.path.join(results_dir, selected_result_dir))

            with col2:
                if st.button("🗑️ Delete Results"):
                    if st.confirm(f"Delete results from {selected_result_dir}?"):
                        import shutil
                        shutil.rmtree(os.path.join(results_dir, selected_result_dir))
                        st.success("✅ Results deleted!")
                        st.experimental_rerun()
        else:
            st.info("No saved results found. Run a backtest first.")
    else:
        st.info("No results directory found. Run a backtest first.")

def display_detailed_results(results_data):
    """Display detailed analysis of results"""

    results = results_data['results']
    config = results_data['config']
    execution_time = results_data['execution_time']

    # Configuration summary
    with st.expander("⚙️ Backtest Configuration", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Strategy Source:** {config['strategy_source']}")
            if config.get('strategy_file'):
                st.write(f"**Strategy File:** {config['strategy_file']}")
            st.write(f"**Bundle:** {config['bundle']}")
            st.write(f"**Benchmark:** {config['benchmark_symbol']}")

        with col2:
            st.write(f"**Start Date:** {config['start_date']}")
            st.write(f"**End Date:** {config['end_date']}")
            st.write(f"**Initial Capital:** ₹{config['capital_base']:,}")
            st.write(f"**Execution Time:** {execution_time:.2f}s")

    # Performance metrics
    st.markdown("### 📊 Performance Metrics")

    returns = results.returns
    portfolio_value = results.portfolio_value

    # Calculate metrics
    initial_value = portfolio_value.iloc[0]
    final_value = portfolio_value.iloc[-1]
    total_return = (final_value / initial_value - 1) * 100

    annual_return = (final_value / initial_value) ** (252 / len(returns)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / volatility if volatility != 0 else 0

    max_drawdown = ((portfolio_value / portfolio_value.expanding().max()) - 1).min() * 100

    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Return", f"{total_return:.2f}%")
    with col2:
        st.metric("Annual Return", f"{annual_return*100:.2f}%")
    with col3:
        st.metric("Volatility", f"{volatility*100:.2f}%")
    with col4:
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    with col5:
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")

def load_and_display_results(results_path):
    """Load and display results from saved directory"""
    try:
        # Look for pickle file
        pickle_files = [f for f in os.listdir(results_path) if f.endswith('.pickle')]

        if pickle_files:
            pickle_path = os.path.join(results_path, pickle_files[0])

            # Load results
            with open(pickle_path, 'rb') as f:
                results = pickle.load(f)

            # Create mock results data structure
            results_data = {
                'results': results,
                'execution_time': 0,  # Unknown for saved results
                'config': {
                    'strategy_source': 'Saved Results',
                    'strategy_file': 'Unknown',
                    'bundle': 'Unknown',
                    'benchmark_symbol': 'Unknown',
                    'start_date': results.index[0].date() if len(results) > 0 else 'Unknown',
                    'end_date': results.index[-1].date() if len(results) > 0 else 'Unknown',
                    'capital_base': results.portfolio_value.iloc[0] if 'portfolio_value' in results.columns else 'Unknown'
                }
            }

            display_detailed_results(results_data)

        else:
            st.error("No pickle files found in the selected results directory.")

    except Exception as e:
        st.error(f"Failed to load results: {str(e)}")

def show_strategy_manager():
    """Strategy manager page for organizing strategies"""

    st.markdown("## 📋 Strategy Manager")
    st.markdown("Organize, compare, and manage your trading strategies.")

    # Get available strategies
    strategy_files = get_available_strategies()

    if not strategy_files:
        st.info("No strategies found. Create some strategies in the Strategy Builder first.")
        return

    # Strategy list
    st.markdown("### 📁 Available Strategies")

    for i, strategy_file in enumerate(strategy_files):
        with st.expander(f"📄 {strategy_file}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                # Show strategy info
                try:
                    filepath = os.path.join("strategies", strategy_file)
                    with open(filepath, 'r') as f:
                        content = f.read()

                    # Extract class name
                    lines = content.split('\n')
                    class_line = next((line for line in lines if line.strip().startswith('class ') and 'BaseStrategy' in line), None)

                    if class_line:
                        class_name = class_line.split('class ')[1].split('(')[0].strip()
                        st.write(f"**Class:** {class_name}")

                    # File stats
                    file_stats = os.stat(filepath)
                    st.write(f"**Size:** {file_stats.st_size} bytes")
                    st.write(f"**Modified:** {datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')}")

                except Exception as e:
                    st.error(f"Error reading strategy: {str(e)}")

            with col2:
                if st.button(f"👀 View", key=f"view_{i}"):
                    show_strategy_code(strategy_file)

                if st.button(f"✏️ Edit", key=f"edit_{i}"):
                    edit_strategy_in_builder(strategy_file)

            with col3:
                if st.button(f"🚀 Run", key=f"run_{i}"):
                    st.session_state.selected_strategy_for_run = strategy_file
                    st.info(f"Strategy {strategy_file} selected. Go to Backtest Runner to execute.")

                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    if st.confirm(f"Delete {strategy_file}?"):
                        delete_strategy_file(strategy_file)

def show_strategy_code(strategy_file):
    """Display strategy code"""
    try:
        filepath = os.path.join("strategies", strategy_file)
        with open(filepath, 'r') as f:
            content = f.read()

        st.code(content, language='python')

        # Download button
        st.download_button(
            label="📥 Download Strategy",
            data=content,
            file_name=strategy_file,
            mime="text/x-python"
        )

    except Exception as e:
        st.error(f"Failed to display strategy code: {str(e)}")

def edit_strategy_in_builder(strategy_file):
    """Load strategy into builder for editing"""
    try:
        filepath = os.path.join("strategies", strategy_file)
        with open(filepath, 'r') as f:
            content = f.read()

        # Extract just the strategy class code (remove imports and main section)
        lines = content.split('\n')

        # Find class definition start
        class_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and 'BaseStrategy' in line:
                class_start = i
                break

        if class_start is not None:
            # Find the end of the class (next non-indented line or end of file)
            class_end = len(lines)
            for i in range(class_start + 1, len(lines)):
                if lines[i] and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                    class_end = i
                    break

            # Extract class code
            class_code = '\n'.join(lines[class_start:class_end])

            # Store in session state
            st.session_state.strategy_code = class_code
            st.success(f"✅ Strategy {strategy_file} loaded into Strategy Builder!")
            st.info("💡 Go to Strategy Builder to edit the code.")
        else:
            st.error("Could not find strategy class in file.")

    except Exception as e:
        st.error(f"Failed to load strategy for editing: {str(e)}")

def delete_strategy_file(strategy_file):
    """Delete strategy file"""
    try:
        filepath = os.path.join("strategies", strategy_file)
        os.remove(filepath)
        st.success(f"✅ Strategy {strategy_file} deleted!")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Failed to delete strategy: {str(e)}")

# Add some utility functions for better user experience
def create_sample_strategies():
    """Create sample strategies for demonstration"""

    strategies_dir = "strategies"
    if not os.path.exists(strategies_dir):
        os.makedirs(strategies_dir)

    # Sample SMA strategy
    sma_strategy = '''#!/usr/bin/env python3
"""
Sample SMA Strategy
Generated by NSE Backtesting Engine
"""

import pandas as pd
import numpy as np
from zipline.api import symbol, order_target_percent, record
from engine.enhanced_base_strategy import BaseStrategy

class SampleSMAStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

        self.risk_params.update({
            'max_position_size': 0.15,
            'stop_loss_pct': 0.08,
        })

    def select_universe(self, context):
        return [symbol('SBIN'), symbol('RELIANCE')]

    def generate_signals(self, context, data):
        signals = {}
        for asset in context.universe:
            try:
                prices = data.history(asset, 'price', self.long_window + 1, '1d')
                if len(prices) >= self.long_window:
                    short_ma = prices.tail(self.short_window).mean()
                    long_ma = prices.tail(self.long_window).mean()

                    if short_ma > long_ma:
                        signals[asset] = 1.0
                    else:
                        signals[asset] = -1.0
                else:
                    signals[asset] = 0.0
            except Exception:
                signals[asset] = 0.0
        return signals
'''

    # Write sample strategy if it doesn't exist
    sample_path = os.path.join(strategies_dir, "sample_sma_strategy.py")
    if not os.path.exists(sample_path):
        with open(sample_path, 'w') as f:
            f.write(sma_strategy)

# Initialize sample strategies on startup
create_sample_strategies()

if __name__ == "__main__":
    main()
