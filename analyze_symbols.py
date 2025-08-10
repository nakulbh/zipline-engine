#!/usr/bin/env python3
import pandas as pd
import sys
import os

def analyze_nse_bundle():
    cache_file = './.augment/cache/parquet_data/market_data_2020-09-01_2025-06-01_all.parquet'
    
    print('📊 Analyzing NSE Bundle Symbols')
    print('=' * 50)
    
    if not os.path.exists(cache_file):
        print(f"❌ Cache file not found: {cache_file}")
        return
    
    file_size = os.path.getsize(cache_file) / (1024 * 1024)  # MB
    print(f"📁 File size: {file_size:.1f} MB")
    
    try:
        # Read parquet file
        print("📖 Reading parquet data...")
        df = pd.read_parquet(cache_file)
        
        print(f"📈 Total records: {len(df):,}")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Check data structure
        if 'symbol' in df.columns:
            symbols = sorted(df['symbol'].unique())
            print(f"\n🏢 Total unique symbols: {len(symbols)}")
            
            # Get date range
            if 'date' in df.columns:
                date_min = df['date'].min()
                date_max = df['date'].max()
                print(f"📅 Date range: {date_min} to {date_max}")
            
            print(f"\n📋 All Available Symbols:")
            print("-" * 60)
            
            # Print symbols in organized columns
            for i in range(0, len(symbols), 5):
                row = symbols[i:i+5]
                print("  ".join(f"{symbol:<12}" for symbol in row))
            
            # Show some sample data
            print(f"\n📊 Sample Data (first 5 rows):")
            print("-" * 60)
            print(df.head())
            
        else:
            print("❌ No 'symbol' column found")
            print("Available columns:", df.columns.tolist())
            print("\nFirst few rows:")
            print(df.head())
            
    except Exception as e:
        print(f"❌ Error reading parquet file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_nse_bundle()
