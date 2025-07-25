#!/usr/bin/env python3
"""
NSE Portfolio Strategy
======================

A comprehensive multi-asset strategy using all available NSE stocks in your bundle.
This strategy demonstrates portfolio construction with your specific stock universe.

Available Stocks in Bundle:
- BAJFINANCE (Bajaj Finance)
- HDFCBANK (HDFC Bank) 
- HDFC (HDFC Ltd)
- HINDALCO (Hindalco Industries)
- RELIANCE (Reliance Industries)
- SBIN (State Bank of India)
- BANKNIFTY (Bank Nifty Index)
- NIFTY50 (Nifty 50 Index)

Strategy Logic:
- Multi-factor approach combining momentum, mean reversion, and volume analysis
- Dynamic position sizing based on volatility
- Sector diversification across banking, finance, metals, and energy
- Index-based market timing

Author: NSE Backtesting Engine
Date: 2025-07-07
"""

import numpy as np
import pandas as pd
from zipline.api import symbol, record
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.enhanced_base_strategy import BaseStrategy

class NSEPortfolioStrategy(BaseStrategy):
    """
    Comprehensive NSE portfolio strategy using all available stocks
    """
    
    def __init__(self, 
                 momentum_window=20,
                 mean_reversion_window=10,
                 volume_window=15,
                 volatility_window=30):
        super().__init__()
        
        # Strategy parameters
        self.momentum_window = momentum_window
        self.mean_reversion_window = mean_reversion_window
        self.volume_window = volume_window
        self.volatility_window = volatility_window
        
        # Enhanced risk management for portfolio strategy
        self.risk_params.update({
            'max_position_size': 0.15,    # 15% max per stock
            'stop_loss_pct': 0.08,        # 8% stop loss
            'take_profit_pct': 0.20,      # 20% take profit
            'max_leverage': 1.0,          # No leverage
            'daily_loss_limit': -0.03,    # 3% daily loss limit
        })
        
        # Stock categorization for sector analysis
        self.banking_stocks = ['HDFCBANK', 'SBIN']
        self.finance_stocks = ['BAJFINANCE', 'HDFC']
        self.industrial_stocks = ['HINDALCO', 'RELIANCE']
        self.indices = ['NIFTY50', 'BANKNIFTY']
        
        print(f"🎯 Initializing NSE Portfolio Strategy")
        print(f"📊 Parameters: momentum={momentum_window}, mean_rev={mean_reversion_window}")
        print(f"⚙️  Risk Parameters: {self.risk_params}")

    def select_universe(self, context):
        """
        Select all available NSE stocks from your bundle
        """
        # All available stocks in your bundle
        nse_symbols = [
            'BAJFINANCE',  # Bajaj Finance
            'HDFCBANK',    # HDFC Bank
            'HDFC',        # HDFC Ltd
            'HINDALCO',    # Hindalco Industries
            'RELIANCE',    # Reliance Industries
            'SBIN',        # State Bank of India
            'BANKNIFTY',   # Bank Nifty Index
            'NIFTY50'      # Nifty 50 Index
        ]
        
        try:
            universe = [symbol(sym) for sym in nse_symbols]
            print(f"🌐 Selected universe: {len(universe)} assets")
            return universe
        except Exception as e:
            print(f"❌ Error creating universe: {e}")
            # Fallback to core stocks
            return [symbol('SBIN'), symbol('RELIANCE'), symbol('HDFCBANK')]

    def generate_signals(self, context, data):
        """
        Generate comprehensive signals using multiple factors
        """
        signals = {}
        
        try:
            # Get market sentiment from indices
            market_sentiment = self._get_market_sentiment(context, data)
            
            for asset in context.universe:
                try:
                    # Get sufficient historical data
                    prices = data.history(asset, 'price', max(self.momentum_window, 
                                                            self.volatility_window) + 10, '1d')
                    volumes = data.history(asset, 'volume', self.volume_window + 5, '1d')
                    
                    if len(prices) < self.momentum_window:
                        signals[asset] = 0.0
                        continue
                    
                    # Calculate individual factors
                    momentum_signal = self._calculate_momentum_signal(prices)
                    mean_reversion_signal = self._calculate_mean_reversion_signal(prices)
                    volume_signal = self._calculate_volume_signal(prices, volumes)
                    volatility_factor = self._calculate_volatility_factor(prices)
                    
                    # Sector-specific adjustments
                    sector_adjustment = self._get_sector_adjustment(asset, market_sentiment)
                    
                    # Combine signals with weights
                    combined_signal = (
                        momentum_signal * 0.35 +
                        mean_reversion_signal * 0.25 +
                        volume_signal * 0.20 +
                        market_sentiment * 0.20
                    )
                    
                    # Apply sector adjustment
                    combined_signal *= sector_adjustment
                    
                    # Apply volatility adjustment (reduce position in high volatility)
                    combined_signal *= volatility_factor
                    
                    # Normalize signal
                    signals[asset] = max(-1.0, min(1.0, combined_signal))
                    
                    # Record factors for analysis
                    asset_name = str(asset).split('(')[1].split(')')[0] if '(' in str(asset) else str(asset)
                    self.record_factor(f'momentum_{asset_name}', momentum_signal, context)
                    self.record_factor(f'mean_rev_{asset_name}', mean_reversion_signal, context)
                    self.record_factor(f'volume_{asset_name}', volume_signal, context)
                    
                except Exception as e:
                    print(f"⚠️  Error calculating signal for {asset}: {e}")
                    signals[asset] = 0.0

            # Log signal summary
            active_signals = {k: v for k, v in signals.items() if abs(v) > 0.1}
            if active_signals:
                print(f"📊 Active signals: {len(active_signals)}/{len(signals)}")

            return signals

        except Exception as e:
            print(f"❌ Error in signal generation: {e}")
            return {asset: 0.0 for asset in context.universe}

    def _get_market_sentiment(self, context, data):
        """
        Calculate market sentiment using indices
        """
        try:
            nifty_symbol = symbol('NIFTY50')
            banknifty_symbol = symbol('BANKNIFTY')
            
            sentiment = 0.0
            count = 0
            
            # NIFTY 50 sentiment
            if nifty_symbol in context.universe:
                nifty_prices = data.history(nifty_symbol, 'price', 20, '1d')
                if len(nifty_prices) >= 10:
                    nifty_momentum = (nifty_prices.iloc[-1] / nifty_prices.iloc[-10]) - 1
                    sentiment += np.tanh(nifty_momentum * 10)  # Scale and bound
                    count += 1
            
            # Bank NIFTY sentiment
            if banknifty_symbol in context.universe:
                banknifty_prices = data.history(banknifty_symbol, 'price', 20, '1d')
                if len(banknifty_prices) >= 10:
                    banknifty_momentum = (banknifty_prices.iloc[-1] / banknifty_prices.iloc[-10]) - 1
                    sentiment += np.tanh(banknifty_momentum * 10)
                    count += 1
            
            return sentiment / count if count > 0 else 0.0
            
        except Exception as e:
            print(f"⚠️  Error calculating market sentiment: {e}")
            return 0.0

    def _calculate_momentum_signal(self, prices):
        """
        Calculate momentum signal using multiple timeframes
        """
        try:
            if len(prices) < self.momentum_window:
                return 0.0
            
            # Short-term momentum (5 days)
            short_momentum = (prices.iloc[-1] / prices.iloc[-5]) - 1 if len(prices) >= 5 else 0
            
            # Medium-term momentum (momentum_window)
            medium_momentum = (prices.iloc[-1] / prices.iloc[-self.momentum_window]) - 1
            
            # Combine momentums
            combined_momentum = short_momentum * 0.6 + medium_momentum * 0.4
            
            # Scale and bound the signal
            return np.tanh(combined_momentum * 15)  # Scale factor of 15
            
        except Exception as e:
            return 0.0

    def _calculate_mean_reversion_signal(self, prices):
        """
        Calculate mean reversion signal using z-score
        """
        try:
            if len(prices) < self.mean_reversion_window:
                return 0.0
            
            recent_prices = prices.tail(self.mean_reversion_window)
            current_price = prices.iloc[-1]
            mean_price = recent_prices.mean()
            std_price = recent_prices.std()
            
            if std_price == 0:
                return 0.0
            
            # Z-score calculation
            z_score = (current_price - mean_price) / std_price
            
            # Mean reversion signal (negative z-score means buy, positive means sell)
            return -np.tanh(z_score * 0.5)  # Invert for mean reversion
            
        except Exception as e:
            return 0.0

    def _calculate_volume_signal(self, prices, volumes):
        """
        Calculate volume-based signal
        """
        try:
            if len(volumes) < self.volume_window or len(prices) < 2:
                return 0.0
            
            # Volume trend
            recent_volume = volumes.tail(5).mean()
            avg_volume = volumes.tail(self.volume_window).mean()
            
            if avg_volume == 0:
                return 0.0
            
            volume_ratio = recent_volume / avg_volume
            
            # Price change
            price_change = (prices.iloc[-1] / prices.iloc[-2]) - 1
            
            # Volume confirmation signal
            if volume_ratio > 1.2 and price_change > 0:  # High volume + price up
                return 0.5
            elif volume_ratio > 1.2 and price_change < 0:  # High volume + price down
                return -0.5
            else:
                return 0.0
                
        except Exception as e:
            return 0.0

    def _calculate_volatility_factor(self, prices):
        """
        Calculate volatility adjustment factor
        """
        try:
            if len(prices) < self.volatility_window:
                return 1.0
            
            returns = prices.pct_change().dropna()
            if len(returns) < 10:
                return 1.0
            
            volatility = returns.tail(self.volatility_window).std() * np.sqrt(252)  # Annualized
            
            # Reduce position size for high volatility stocks
            # Target volatility around 25%
            target_vol = 0.25
            vol_adjustment = min(1.0, target_vol / max(volatility, 0.1))
            
            return vol_adjustment
            
        except Exception as e:
            return 1.0

    def _get_sector_adjustment(self, asset, market_sentiment):
        """
        Apply sector-specific adjustments
        """
        try:
            asset_name = str(asset).split('(')[1].split(')')[0] if '(' in str(asset) else str(asset)
            
            # Banking sector adjustment
            if asset_name in self.banking_stocks:
                # Banking stocks are sensitive to interest rates and market sentiment
                return 1.0 + (market_sentiment * 0.3)
            
            # Finance sector adjustment  
            elif asset_name in self.finance_stocks:
                # Finance stocks benefit from positive market sentiment
                return 1.0 + (market_sentiment * 0.2)
            
            # Industrial sector adjustment
            elif asset_name in self.industrial_stocks:
                # Industrial stocks are cyclical
                return 1.0 + (market_sentiment * 0.1)
            
            # Indices
            elif asset_name in self.indices:
                # Reduce direct index trading
                return 0.5
            
            else:
                return 1.0
                
        except Exception as e:
            return 1.0

    def _calculate_position_size(self, context, data, asset, target_weight):
        """
        Custom position sizing with portfolio considerations
        """
        try:
            # Get base position size
            base_size = super()._calculate_position_size(context, data, asset, target_weight)
            
            # Apply portfolio-level adjustments
            asset_name = str(asset).split('(')[1].split(')')[0] if '(' in str(asset) else str(asset)
            
            # Sector concentration limits
            if asset_name in self.banking_stocks:
                # Limit banking exposure to 40% of portfolio
                base_size = min(base_size, 0.20)  # Max 20% per banking stock
            elif asset_name in self.finance_stocks:
                # Limit finance exposure
                base_size = min(base_size, 0.15)  # Max 15% per finance stock
            elif asset_name in self.indices:
                # Limit index exposure
                base_size = min(base_size, 0.10)  # Max 10% per index
            
            return base_size
            
        except Exception as e:
            print(f"⚠️  Error in position sizing for {asset}: {e}")
            return 0.0


def main():
    """
    Test the NSE Portfolio Strategy
    """
    from engine.enhanced_zipline_runner import EnhancedZiplineRunner
    
    print("🚀 Testing NSE Portfolio Strategy")
    print("=" * 50)
    
    # Create strategy
    strategy = NSEPortfolioStrategy(
        momentum_window=15,
        mean_reversion_window=10,
        volume_window=12,
        volatility_window=20
    )
    
    # Create runner
    runner = EnhancedZiplineRunner(
        strategy=strategy,
        bundle='nse-local-minute-bundle',
        start_date='2016-01-01',
        end_date='2021-01-01',
        capital_base=100000,
        benchmark_symbol='NIFTY50'
    )
    
    # Run backtest
    try:
        print("🔄 Running backtest...")
        results = runner.run()
        
        print(f"✅ Backtest completed!")
        print(f"📈 Final Portfolio Value: ${results.portfolio_value.iloc[-1]:,.2f}")
        print(f"📊 Total Return: {((results.portfolio_value.iloc[-1] / results.portfolio_value.iloc[0]) - 1) * 100:.2f}%")
        
        # Analyze results
        print("📊 Running analysis...")
        runner.analyze('backtest_results/nse_portfolio_strategy')
        
        print("✅ Analysis completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
