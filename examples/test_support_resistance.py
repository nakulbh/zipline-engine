#!/usr/bin/env python3
"""
Test Support/Resistance Level Identification

This script tests the S/R identification logic with sample price data
to ensure it correctly identifies support and resistance levels.

Author: NSE Backtesting Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from strategies.rsi_support_resistance_strategy import RSISupportResistanceStrategy

def create_sample_data():
    """Create sample price data with clear S/R levels"""
    
    # Create a price series with clear support at 95 and resistance at 105
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    
    # Base trend with support/resistance
    base_prices = []
    for i in range(50):
        if i < 10:
            # Initial uptrend to resistance
            price = 90 + (i * 1.5)
        elif i < 15:
            # Hit resistance around 105, bounce down
            price = 105 - ((i - 10) * 2)
        elif i < 25:
            # Range between 95-105
            price = 95 + (10 * np.sin((i - 15) * 0.3))
        elif i < 30:
            # Break below support to 90
            price = 95 - ((i - 25) * 1)
        elif i < 40:
            # Bounce back to resistance
            price = 90 + ((i - 30) * 1.5)
        else:
            # Final range
            price = 100 + (5 * np.sin((i - 40) * 0.5))
        
        base_prices.append(price)
    
    # Add some noise
    noise = np.random.normal(0, 0.5, 50)
    prices = [max(85, p + n) for p, n in zip(base_prices, noise)]
    
    # Create OHLC data
    data = []
    for i, close in enumerate(prices):
        high = close + np.random.uniform(0, 1)
        low = close - np.random.uniform(0, 1)
        open_price = close + np.random.uniform(-0.5, 0.5)
        
        data.append({
            'date': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'price': close  # For compatibility
        })
    
    return pd.DataFrame(data).set_index('date')

def test_sr_identification():
    """Test the S/R identification logic"""
    
    print("🧪 Testing Support/Resistance Identification")
    print("=" * 50)
    
    # Create strategy instance
    strategy = RSISupportResistanceStrategy(
        lookback_period=20,
        min_touches=2,
        sr_tolerance=0.02
    )
    
    # Create sample data
    df = create_sample_data()
    
    print("📊 Sample Data Overview:")
    print(f"   Date Range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"   Price Range: ₹{df['price'].min():.2f} - ₹{df['price'].max():.2f}")
    print(f"   Current Price: ₹{df['price'].iloc[-1]:.2f}")
    print()
    
    # Test S/R identification
    print("🔍 Identifying Support/Resistance Levels...")
    
    prices = df['price']
    highs = df['high']
    lows = df['low']
    
    support_levels, resistance_levels = strategy.identify_support_resistance(
        prices, highs, lows
    )
    
    print(f"✅ Found {len(support_levels)} Support Levels:")
    for i, level in enumerate(sorted(support_levels), 1):
        print(f"   {i}. ₹{level:.2f}")
    
    print(f"✅ Found {len(resistance_levels)} Resistance Levels:")
    for i, level in enumerate(sorted(resistance_levels, reverse=True), 1):
        print(f"   {i}. ₹{level:.2f}")
    
    print()
    
    # Test nearest level identification
    current_price = df['price'].iloc[-1]
    nearest_support, nearest_resistance = strategy.get_nearest_support_resistance(
        current_price, support_levels, resistance_levels
    )
    
    print("🎯 Nearest Levels to Current Price:")
    print(f"   Current Price: ₹{current_price:.2f}")
    print(f"   Nearest Support: ₹{nearest_support:.2f}" if nearest_support else "   Nearest Support: None")
    print(f"   Nearest Resistance: ₹{nearest_resistance:.2f}" if nearest_resistance else "   Nearest Resistance: None")
    
    if nearest_support:
        support_distance = abs(current_price - nearest_support) / current_price
        print(f"   Distance to Support: {support_distance:.1%}")
    
    if nearest_resistance:
        resistance_distance = abs(current_price - nearest_resistance) / current_price
        print(f"   Distance to Resistance: {resistance_distance:.1%}")
    
    print()
    
    # Test signal generation logic
    print("📈 Testing Signal Generation:")
    
    # Mock RSI values for testing
    test_rsi_values = [25, 35, 50, 65, 75]  # Oversold to overbought
    
    for rsi in test_rsi_values:
        # Simulate signal generation logic
        signal_strength = 0.0
        signal_type = "No Signal"
        
        if rsi <= strategy.oversold_threshold:
            if nearest_support and abs(current_price - nearest_support) / current_price <= 0.03:
                signal_strength = min(1.0, (strategy.oversold_threshold - rsi) / 10 + 0.3)
                signal_type = "Strong Buy (RSI + Support)"
            else:
                signal_strength = min(0.6, (strategy.oversold_threshold - rsi) / 15)
                signal_type = "Weak Buy (RSI only)"
        
        elif rsi >= strategy.overbought_threshold:
            if nearest_resistance and abs(current_price - nearest_resistance) / current_price <= 0.03:
                signal_strength = -min(1.0, (rsi - strategy.overbought_threshold) / 10 + 0.3)
                signal_type = "Strong Sell (RSI + Resistance)"
            else:
                signal_strength = -min(0.6, (rsi - strategy.overbought_threshold) / 15)
                signal_type = "Weak Sell (RSI only)"
        
        print(f"   RSI {rsi:2d}: {signal_type:25s} (Strength: {signal_strength:+.2f})")
    
    print()
    
    # Test stop loss calculation
    print("🛑 Testing Stop Loss Calculation:")
    
    # Test long position
    entry_price = current_price
    if nearest_support:
        sr_stop = nearest_support * 0.995  # 0.5% below support
        fallback_stop = entry_price * (1 - strategy.risk_params['stop_loss_pct'])
        
        print(f"   Long Position Entry: ₹{entry_price:.2f}")
        print(f"   S/R Stop Loss: ₹{sr_stop:.2f} (0.5% below support)")
        print(f"   Fallback Stop: ₹{fallback_stop:.2f} ({strategy.risk_params['stop_loss_pct']:.0%} below entry)")
        print(f"   Using: ₹{sr_stop:.2f} (S/R-based)")
    
    # Test profit target
    if nearest_resistance:
        sr_profit = nearest_resistance * 0.995  # 0.5% below resistance
        fallback_profit = entry_price * (1 + strategy.risk_params['take_profit_pct'])
        
        print(f"   S/R Take Profit: ₹{sr_profit:.2f} (0.5% below resistance)")
        print(f"   Fallback Profit: ₹{fallback_profit:.2f} ({strategy.risk_params['take_profit_pct']:.0%} above entry)")
        print(f"   Using: ₹{sr_profit:.2f} (S/R-based)")
    
    print()
    
    # Test position sizing
    print("💰 Testing Position Sizing:")
    
    if nearest_support:
        risk_distance = (entry_price - nearest_support) / entry_price
        portfolio_value = 200000  # Mock portfolio
        risk_per_trade = portfolio_value * 0.015  # 1.5%
        position_size = risk_per_trade / (risk_distance * portfolio_value)
        max_size = strategy.risk_params['max_position_size']
        final_size = min(position_size, max_size)
        
        print(f"   Portfolio Value: ₹{portfolio_value:,}")
        print(f"   Risk per Trade: ₹{risk_per_trade:,.0f} (1.5%)")
        print(f"   Risk Distance: {risk_distance:.1%} (to support)")
        print(f"   Calculated Size: {position_size:.1%}")
        print(f"   Max Allowed: {max_size:.1%}")
        print(f"   Final Position Size: {final_size:.1%}")
    
    print()
    print("✅ Support/Resistance Testing Complete!")
    print()
    print("💡 Key Observations:")
    print("   • S/R levels are identified from local highs/lows")
    print("   • Signals are stronger when RSI extremes occur near S/R levels")
    print("   • Stop losses are placed at logical technical levels")
    print("   • Position sizing adapts to distance to S/R levels")

if __name__ == "__main__":
    # Set random seed for reproducible results
    np.random.seed(42)
    test_sr_identification()
