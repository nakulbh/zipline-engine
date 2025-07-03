#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np

# Set up environment
os.environ['ZIPLINE_ROOT'] = '/home/nakulbh/Desktop/Ankit/QuantMania/bactestingEngine/zipline-engine/.zipline'
os.chdir('/home/nakulbh/Desktop/Ankit/QuantMania/bactestingEngine/zipline-engine')

print("🔄 Testing minute data access...")

try:
    # First import the extension to register bundles
    sys.path.insert(0, '.zipline')
    import extension
    print("✅ Extension imported, bundles registered")
    
    from zipline.data import bundles
    from zipline.utils.calendar_utils import get_calendar

    # Load the bundle
    print("📦 Loading bundle...")
    bundle_data = bundles.load('nse-local-minute-bundle')
    
    # Get the trading calendar
    trading_calendar = get_calendar('XBOM')
    
    # Get some sample assets
    asset_finder = bundle_data.asset_finder
    assets = asset_finder.retrieve_all(asset_finder.sids)
    
    print(f"📊 Found {len(assets)} assets in bundle:")
    for asset in assets[:5]:  # Only show first 5 to avoid clutter
        print(f"  - {asset.symbol} (sid: {asset.sid})")
    if len(assets) > 5:
        print(f"  ... and {len(assets)-5} more")
    
    # Test minute data access for a specific asset
    if assets:
        test_asset = assets[0]  # Use first asset
        print(f"\n🔍 Testing minute data access for {test_asset.symbol}...")
        
        # Find first available date in the bundle
        first_available = bundle_data.equity_minute_bar_reader.first_trading_day
        last_available = bundle_data.equity_minute_bar_reader.last_trading_day
        
        print(f"📅 Data available from {first_available.date()} to {last_available.date()}")
        
        # Use a date we know should have data
        test_date = first_available
        test_end = trading_calendar.next_session_label(test_date)
        
        # Get the trading minutes for the date range
        trading_minutes = trading_calendar.minutes_in_range(test_date, test_end)
        
        if trading_minutes.empty:
            print("⚠️ No trading minutes found in this date range")
            sys.exit(0)
            
        print(f"📅 Found {len(trading_minutes)} trading minutes on {test_date.date()}")
        
        try:
            # Get the minute bar reader
            minute_reader = bundle_data.equity_minute_bar_reader
            
            # Get market open and close for our test date
            market_open = trading_calendar.open_and_close_for_session(test_date)[0]
            market_close = trading_calendar.open_and_close_for_session(test_date)[1]
            
            print(f"⏰ Market hours: {market_open.time()} to {market_close.time()}")
            
            # Get the data arrays
            fields = ['open', 'high', 'low', 'close', 'volume']
            data = {}
            
            for field in fields:
                try:
                    arr = minute_reader.load_raw_arrays(
                        [field],
                        market_open,
                        market_close,
                        [test_asset.sid]
                    )[0]
                    data[field] = arr
                except Exception as e:
                    print(f"⚠️ Error loading {field}: {e}")
                    data[field] = np.array([])
            
            if not all(len(arr) > 0 for arr in data.values()):
                print("❌ No data loaded for one or more fields")
                sys.exit(1)
            
            print(f"\n📊 First 5 minutes of data for {test_asset.symbol} on {test_date.date()}:")
            for i in range(min(5, len(data['open']))):
                print(f"  Minute {i+1}: "
                      f"O={data['open'][i]:.2f}, H={data['high'][i]:.2f}, "
                      f"L={data['low'][i]:.2f}, C={data['close'][i]:.2f}, "
                      f"V={data['volume'][i]}")
            
            # Data quality metrics
            print("\n📊 Data quality metrics:")
            for field in fields:
                if len(data[field]) == 0:
                    print(f"  - {field.upper()}: No data available")
                    continue
                    
                if field == 'volume':
                    valid = (data[field] >= 0).sum()
                else:
                    valid = (data[field] > 0).sum()
                print(f"  - {field.upper()}: {valid} valid values out of {len(data[field])}")
            
            print("\n✅ Minute data access successful!")
            
        except Exception as e:
            print(f"❌ Error reading minute data: {e}")
            import traceback
            traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error accessing data: {e}")
    import traceback
    traceback.print_exc()