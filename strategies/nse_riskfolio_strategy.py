#!/usr/bin/env python3
"""
NSE Riskfolio Portfolio Strategy
================================

This strategy adapts the sophisticated portfolio optimization approach from the example
you provided, using Riskfolio-Portfolio for mean-variance optimization with your NSE assets.

Key Features:
- Mean-variance optimization using Riskfolio-Portfolio
- Ledoit-Wolf covariance shrinkage
- Dynamic rebalancing based on market conditions
- Risk management with leverage control
- Works with your NSE asset universe

Available NSE Assets:
- BAJFINANCE (Bajaj Finance)
- BANKNIFTY (Bank Nifty Index) 
- HDFCBANK (HDFC Bank)
- HDFC (HDFC Ltd)
- HINDALCO (Hindalco Industries)
- NIFTY50 (Nifty 50 Index)
- RELIANCE (Reliance Industries)
- SBIN (State Bank of India)

Strategy Logic:
1. Screen assets based on liquidity and volatility criteria
2. Calculate historical returns for selected assets
3. Use Riskfolio-Portfolio for optimal weight calculation
4. Apply leverage and risk controls
5. Rebalance weekly
"""

import numpy as np
import pandas as pd
import riskfolio as rp
from zipline.api import symbol, get_datetime, record
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class NSERiskfolioStrategy(BaseStrategy):
    """
    NSE Portfolio Strategy using Riskfolio-Portfolio optimization
    
    This strategy replicates the sophisticated approach from your example,
    adapted for NSE markets with your available assets.
    """
    
    def __init__(self, 
                 leverage=1.2,           # Reduced from 1.5 for NSE markets
                 lookback_window=126,    # 6 months of trading days (21*6)
                 min_volatility=0.15,    # Minimum annualized volatility
                 max_volatility=0.60,    # Maximum annualized volatility
                 min_return_target=0.0008):  # Minimum expected return
        """
        Initialize the NSE Riskfolio Strategy
        
        Parameters:
        -----------
        leverage : float
            Portfolio leverage (1.2 = 20% leverage)
        lookback_window : int
            Historical data window for optimization
        min_volatility : float
            Minimum volatility threshold for asset selection
        max_volatility : float
            Maximum volatility threshold for asset selection
        min_return_target : float
            Minimum expected return for optimization
        """
        super().__init__()
        
        # Strategy parameters
        self.leverage = leverage
        self.lookback_window = lookback_window
        self.min_volatility = min_volatility
        self.max_volatility = max_volatility
        self.min_return_target = min_return_target
        
        # Risk management - more conservative for NSE
        self.risk_params.update({
            'max_leverage': leverage,
            'max_position_size': 0.25,    # 25% max per position
            'stop_loss_pct': 0.08,        # 8% stop loss
            'take_profit_pct': 0.25,      # 25% take profit
            'daily_loss_limit': -0.05     # 5% daily loss limit
        })
        
        # Track optimization results
        self.last_optimization_date = None
        self.optimization_weights = {}
        self.screened_assets = []
        
        print(f"🚀 NSE Riskfolio Strategy initialized")
        print(f"   📊 Leverage: {leverage}x")
        print(f"   📅 Lookback: {lookback_window} days")
        print(f"   📈 Volatility range: {min_volatility:.1%} - {max_volatility:.1%}")
    
    def select_universe(self, context):
        """
        Define the NSE trading universe
        Using all available assets from your bundle
        """
        nse_assets = [
            symbol('BAJFINANCE'),
            symbol('BANKNIFTY'), 
            symbol('HDFCBANK'),
            symbol('HDFC'),
            symbol('HINDALCO'),
            symbol('NIFTY50'),
            symbol('RELIANCE'),
            symbol('SBIN')
        ]
        
        return nse_assets
    
    def generate_signals(self, context, data):
        """
        Generate portfolio weights using Riskfolio optimization
        This is the core of the strategy, replicating your example
        """
        current_date = get_datetime().date()
        
        # Screen assets based on volatility and data availability
        screened_assets = self._screen_assets(context, data)
        
        if len(screened_assets) < 3:  # Need minimum assets for diversification
            print(f"⚠️  Insufficient assets after screening: {len(screened_assets)}")
            return {asset: 0.0 for asset in context.universe}
        
        # Get historical price data for screened assets
        try:
            prices_data = self._get_historical_prices(screened_assets, data)
            if prices_data is None or prices_data.empty:
                print("⚠️  No price data available for optimization")
                return {asset: 0.0 for asset in context.universe}
            
            # Calculate returns
            returns = prices_data.pct_change().dropna()
            
            # Remove assets with insufficient data or zero variance
            returns = returns.loc[:, (returns != 0).any(axis=0)]
            returns = returns.dropna(axis=1, how='any')
            
            if returns.empty or len(returns.columns) < 2:
                print("⚠️  Insufficient return data for optimization")
                return {asset: 0.0 for asset in context.universe}
            
            # Compute optimal weights using Riskfolio
            optimal_weights = self._compute_riskfolio_weights(returns)
            
            if optimal_weights is not None:
                # Apply leverage
                optimal_weights *= self.leverage
                
                # Convert to signals dictionary for all universe assets
                signals = {asset: 0.0 for asset in context.universe}
                
                for asset_symbol, weight in optimal_weights.items():
                    # Find matching asset in universe
                    for asset in context.universe:
                        if str(asset).split('(')[1].split(')')[0] == asset_symbol:
                            signals[asset] = weight
                            break
                
                # Record optimization metrics
                self._record_optimization_metrics(context, optimal_weights, returns)
                
                print(f"✅ Portfolio optimized with {len(optimal_weights)} assets")
                for asset_symbol, weight in optimal_weights.items():
                    if abs(weight) > 0.01:  # Only show meaningful weights
                        print(f"   📊 {asset_symbol}: {weight:.1%}")
                
                return signals
            
        except Exception as e:
            print(f"❌ Optimization failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Fallback to equal weights if optimization fails
        return self._fallback_equal_weights(context)
    
    def _screen_assets(self, context, data):
        """
        Screen assets based on volatility and data availability
        Similar to the pipeline screening in your example
        """
        screened = []
        
        for asset in context.universe:
            try:
                # Get price history for volatility calculation
                prices = data.history(asset, 'price', self.lookback_window, '1d')
                
                if len(prices) < 60:  # Need minimum data
                    continue
                
                # Calculate annualized volatility
                returns = prices.pct_change().dropna()
                if len(returns) < 20:
                    continue
                
                volatility = returns.std() * np.sqrt(252)  # Annualized
                
                # Apply volatility screen (similar to your example)
                if self.min_volatility <= volatility <= self.max_volatility:
                    screened.append(asset)
                    
            except Exception as e:
                print(f"⚠️  Error screening {asset}: {e}")
                continue
        
        self.screened_assets = screened
        print(f"📊 Screened {len(screened)} assets from {len(context.universe)} total")
        
        return screened
    
    def _get_historical_prices(self, assets, data):
        """
        Get historical price data for optimization
        """
        try:
            # Get price data for all screened assets
            price_data = {}
            
            for asset in assets:
                prices = data.history(asset, 'price', self.lookback_window, '1d')
                if len(prices) >= self.lookback_window * 0.8:  # Allow some missing data
                    asset_symbol = str(asset).split('(')[1].split(')')[0]
                    price_data[asset_symbol] = prices
            
            if not price_data:
                return None
            
            # Create DataFrame with aligned dates
            prices_df = pd.DataFrame(price_data)
            prices_df = prices_df.dropna()  # Remove rows with any NaN
            
            return prices_df
            
        except Exception as e:
            print(f"❌ Error getting historical prices: {e}")
            return None
    
    def _compute_riskfolio_weights(self, returns):
        """
        Compute optimal weights using Riskfolio-Portfolio
        This replicates the compute_weights function from your example
        """
        try:
            # Create Riskfolio portfolio object
            port = rp.Portfolio(returns=returns)
            
            # Calculate statistics (method_mu="hist", method_cov="ledoit")
            port.assets_stats(method_mu="hist", method_cov="ledoit")
            
            # Set minimum expected return
            port.lowerret = self.min_return_target
            
            # Optimize portfolio (model="Classic", rm="MV")
            weights = port.rp_optimization(
                model="Classic",  # Classic mean-variance
                rm="MV",         # Mean-Variance
                b=None           # No benchmark
            )
            
            if weights is not None and not weights.empty:
                # Convert to Series with proper index
                weights_series = weights.iloc[:, 0]  # First column contains weights
                return weights_series
            
            return None
            
        except Exception as e:
            print(f"❌ Riskfolio optimization failed: {e}")
            return None
    
    def _record_optimization_metrics(self, context, weights, returns):
        """
        Record optimization metrics for analysis
        """
        try:
            # Portfolio expected return and risk
            portfolio_return = (returns.mean() * weights).sum() * 252  # Annualized
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(returns.cov() * 252, weights)))
            sharpe_ratio = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
            # Record metrics
            record(
                portfolio_expected_return=portfolio_return,
                portfolio_volatility=portfolio_vol,
                portfolio_sharpe=sharpe_ratio,
                num_positions=len([w for w in weights if abs(w) > 0.01]),
                max_weight=weights.max(),
                min_weight=weights.min()
            )
            
        except Exception as e:
            print(f"⚠️  Error recording metrics: {e}")
    
    def _fallback_equal_weights(self, context):
        """
        Fallback to equal weights if optimization fails
        """
        if self.screened_assets:
            equal_weight = 1.0 / len(self.screened_assets)
            signals = {asset: 0.0 for asset in context.universe}
            for asset in self.screened_assets:
                signals[asset] = equal_weight
            print(f"📊 Using equal weights fallback: {equal_weight:.1%} each")
            return signals
        else:
            return {asset: 0.0 for asset in context.universe}


def main():
    """
    Test the NSE Riskfolio Strategy
    """
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    
    print("🚀 Testing NSE Riskfolio Strategy")
    print("=" * 50)
    
    # Create strategy
    strategy = NSERiskfolioStrategy(
        leverage=1.2,
        lookback_window=126,
        min_volatility=0.15,
        max_volatility=0.60
    )
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2019-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    # Run backtest
    print("🔄 Running backtest...")
    results = runner.run()
    
    if results is not None:
        print("✅ Backtest completed successfully!")
        
        # Save results to pickle
        pickle_path = runner.save_results_to_pickle(
            filename="nse_riskfolio_strategy.pickle",
            results_dir="riskfolio_results"
        )
        
        if pickle_path:
            # Create analysis
            runner.create_pyfolio_analysis_from_pickle(
                pickle_filepath=pickle_path,
                results_dir="riskfolio_results/analysis",
                save_plots=True,
                save_csv=True
            )
        
        # Standard analysis
        runner.analyze('riskfolio_results/standard_analysis')
        
    else:
        print("❌ Backtest failed")


if __name__ == "__main__":
    main()
