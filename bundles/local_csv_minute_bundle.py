# import os
# import pandas as pd
# import logging
# from datetime import datetime, timedelta
# from zipline.data.bundles import register
# from zipline.utils.calendar_utils import get_calendar
# import glob

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# log = logging.getLogger(__name__)

# # Path to your local CSV files
# CSV_DATA_PATH = "/media/nakulbh/SanDisk/eq-files"

# def load_csv_data(file_path):
#     """
#     Load and process CSV data from local files
#     """
#     try:
#         # Read CSV file
#         df = pd.read_csv(file_path)
        
#         # Convert datetime column
#         df['datetime'] = pd.to_datetime(df['datetime'])
        
#         # Extract symbol from filename (remove -EQ.csv extension)
#         symbol = os.path.basename(file_path).replace('-EQ.csv', '').replace('.csv', '')
        
#         # Handle special case for NIFTY 50
#         if 'NIFTY 50' in symbol:
#             symbol = 'NIFTY50'
        
#         # Set datetime as index
#         df.set_index('datetime', inplace=True)
        
#         # Ensure we have required columns and rename if necessary
#         required_cols = ['open', 'high', 'low', 'close', 'volume']
        
#         # Check if all required columns exist
#         missing_cols = [col for col in required_cols if col not in df.columns]
#         if missing_cols:
#             log.warning(f"Missing columns in {file_path}: {missing_cols}")
#             return None, None
        
#         # Select only required columns
#         df = df[required_cols].copy()
        
#         # Handle volume - for indices, volume might be 0
#         df['volume'] = df['volume'].fillna(0).astype(int)
        
#         # Remove any rows with NaN values in OHLC data
#         df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
#         if df.empty:
#             log.warning(f"No valid data found in {file_path}")
#             return None, None
        
#         log.info(f"Loaded {len(df)} records for {symbol} from {df.index.min()} to {df.index.max()}")
        
#         return symbol, df
        
#     except Exception as e:
#         log.error(f"Error loading {file_path}: {str(e)}")
#         return None, None

# def resample_to_daily(minute_data):
#     """
#     Resample minute data to daily OHLCV
#     """
#     try:
#         daily_data = minute_data.resample('D').agg({
#             'open': 'first',
#             'high': 'max',
#             'low': 'min',
#             'close': 'last',
#             'volume': 'sum'
#         }).dropna()
        
#         return daily_data
#     except Exception as e:
#         log.error(f"Error resampling to daily: {str(e)}")
#         return pd.DataFrame()

# def local_csv_minute_bundle(
#     environ,
#     asset_db_writer,
#     minute_bar_writer,
#     daily_bar_writer,
#     adjustment_writer,
#     calendar,
#     start_session,
#     end_session,
#     cache,
#     show_progress,
#     output_dir,
# ):
#     """
#     Custom NSE equities bundle using local CSV files for minute-level data
#     """
    
#     if not os.path.exists(CSV_DATA_PATH):
#         raise ValueError(f"CSV data path does not exist: {CSV_DATA_PATH}")
    
#     log.info(f"Starting NSE equities bundle ingestion from local CSV files in {CSV_DATA_PATH}...")
    
#     # Find all CSV files
#     csv_files = glob.glob(os.path.join(CSV_DATA_PATH, "*-EQ.csv"))
#     csv_files.extend(glob.glob(os.path.join(CSV_DATA_PATH, "NIFTY*.csv")))
    
#     if not csv_files:
#         raise ValueError(f"No CSV files found in {CSV_DATA_PATH}")
    
#     log.info(f"Found {len(csv_files)} CSV files to process")
    
#     # Load data from all CSV files
#     all_minute_data = []
#     all_daily_data = []
#     successful_symbols = []
    
#     for file_path in csv_files:
#         try:
#             if show_progress:
#                 log.info(f"Processing {os.path.basename(file_path)}...")
            
#             symbol, minute_data = load_csv_data(file_path)
            
#             if symbol is None or minute_data is None:
#                 continue
            
#             # Add symbol column for processing
#             minute_data_with_symbol = minute_data.copy()
#             minute_data_with_symbol['symbol'] = symbol
#             minute_data_with_symbol = minute_data_with_symbol.reset_index()
#             minute_data_with_symbol = minute_data_with_symbol.rename(columns={'datetime': 'date'})
#             all_minute_data.append(minute_data_with_symbol)
            
#             # Create daily data
#             daily_data = resample_to_daily(minute_data)
#             if not daily_data.empty:
#                 daily_data['symbol'] = symbol
#                 daily_data = daily_data.reset_index()
#                 daily_data = daily_data.rename(columns={'datetime': 'date'})
#                 all_daily_data.append(daily_data)
                
#                 successful_symbols.append(symbol)
#             else:
#                 log.warning(f"No daily data generated for {symbol}")
                
#         except Exception as e:
#             log.error(f"Failed to process {file_path}: {str(e)}")
#             continue
    
#     if not all_minute_data:
#         raise ValueError("No minute-level data was successfully loaded")
    
#     # Combine all data
#     minute_data_combined = pd.concat(all_minute_data, ignore_index=True)
#     daily_data_combined = pd.concat(all_daily_data, ignore_index=True)
    
#     log.info(f"Combined data: {len(minute_data_combined)} minute bars, {len(daily_data_combined)} daily bars")
    
#     # Generate asset metadata
#     asset_metadata = daily_data_combined.groupby('symbol').agg({
#         'date': ['min', 'max']
#     }).reset_index()
#     asset_metadata.columns = ['symbol', 'start_date', 'end_date']
#     asset_metadata['exchange'] = 'NSE'
#     asset_metadata['auto_close_date'] = asset_metadata['end_date'] + pd.Timedelta(days=1)
    
#     # Mark indices appropriately
#     index_symbols = ['NIFTY50', 'BANKNIFTY']
#     asset_metadata.loc[asset_metadata['symbol'].isin(index_symbols), 'exchange'] = 'NSE_INDEX'
    
#     # Create exchanges DataFrame
#     exchanges = pd.DataFrame(
#         data=[
#             ['NSE', 'National Stock Exchange of India', 'IN'],
#             ['NSE_INDEX', 'NSE Indices', 'IN']
#         ],
#         columns=['exchange', 'canonical_name', 'country_code']
#     )
    
#     # Write asset metadata
#     asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)
    
#     log.info(f"Asset metadata written for {len(asset_metadata)} symbols")
    
#     # Create symbol map
#     symbol_map = {symbol: idx for idx, symbol in enumerate(asset_metadata['symbol'])}
    
#     # Get sessions from the calendar
#     sessions = calendar.sessions_in_range(
#         daily_data_combined['date'].min(),
#         daily_data_combined['date'].max()
#     )
    
#     log.info(f"Calendar sessions: {len(sessions)} sessions from {sessions[0]} to {sessions[-1]}")
    
#     # Write minute bars
#     if minute_bar_writer:
#         log.info("Writing minute bars...")
#         minute_data_indexed = minute_data_combined.set_index(['date', 'symbol'])
        
#         def minute_data_generator():
#             for symbol, asset_id in symbol_map.items():
#                 try:
#                     if symbol in minute_data_indexed.index.get_level_values('symbol'):
#                         asset_data = minute_data_indexed.xs(symbol, level=1)
                        
#                         # Ensure we have required columns
#                         asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']].copy()
                        
#                         # Convert volume to int
#                         asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
                        
#                         # Sort by date
#                         asset_data = asset_data.sort_index()
                        
#                         if show_progress:
#                             log.info(f"Writing minute data for {symbol}: {len(asset_data)} bars")
                        
#                         yield asset_id, asset_data
#                     else:
#                         log.warning(f"No minute data found for {symbol}")
                        
#                 except Exception as e:
#                     log.error(f"Error processing minute data for {symbol}: {str(e)}")
#                     continue
        
#         minute_bar_writer.write(minute_data_generator(), show_progress=show_progress)
    
#     # Write daily bars
#     log.info("Writing daily bars...")
#     daily_data_indexed = daily_data_combined.set_index(['date', 'symbol'])
    
#     def daily_data_generator():
#         for symbol, asset_id in symbol_map.items():
#             try:
#                 asset_data = daily_data_indexed.xs(symbol, level=1)
                
#                 # Reindex to calendar sessions and forward fill
#                 asset_data = asset_data.reindex(sessions)
#                 asset_data = asset_data.ffill()
                
#                 # Ensure we have required columns
#                 asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']].copy()
                
#                 # Convert volume to int
#                 asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
                
#                 # Sort by date
#                 asset_data = asset_data.sort_index()
                
#                 if show_progress:
#                     log.info(f"Writing daily data for {symbol}: {len(asset_data)} bars")
                
#                 yield asset_id, asset_data
                
#             except Exception as e:
#                 log.error(f"Error processing daily data for {symbol}: {str(e)}")
#                 continue
    
#     daily_bar_writer.write(daily_data_generator(), show_progress=show_progress)
    
#     # Write empty adjustments (no splits/dividends data)
#     adjustment_writer.write(
#         splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
#         dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']),
#     )
    
#     log.info(f"NSE minute-level bundle ingestion completed! Successfully processed {len(successful_symbols)} symbols.")
#     log.info(f"Symbols: {', '.join(successful_symbols)}")

# # Register the NSE minute-level bundle
# register(
#     'nse-local-minute-bundle',
#     local_csv_minute_bundle,
#     calendar_name='XBOM',  # XBOM is the exchange code for NSE
#     minutes_per_day=375,   # NSE trading session: 9:15 AM to 3:30 PM (375 minutes)
#     create_writers=True
# )



# bundle.py
import os
import pandas as pd
import logging
import glob

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DEFAULT_CSV_DATA_PATH = "/media/nakulbh/SanDisk/eq-files"

def load_csv_data(file_path):
    """Load minute-level CSV data (unchanged from your original)"""
    try:
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        symbol = os.path.basename(file_path).replace('-EQ.csv', '').replace('.csv', '')
        
        if 'NIFTY 50' in symbol:
            symbol = 'NIFTY50'
            
        df.set_index('datetime', inplace=True)
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        
        if not all(col in df.columns for col in required_cols):
            log.warning(f"Missing columns in {file_path}")
            return None, None
            
        df = df[required_cols].copy()
        df['volume'] = df['volume'].fillna(0).astype(int)
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        if df.empty:
            log.warning(f"No valid data in {file_path}")
            return None, None
            
        log.info(f"Loaded {len(df)} minute bars for {symbol}")
        return symbol, df
        
    except Exception as e:
        log.error(f"Error loading {file_path}: {str(e)}")
        return None, None

def local_csv_minute_only_bundle(
    environ,
    asset_db_writer,
    minute_bar_writer,  # We only use this (no daily_bar_writer)
    adjustment_writer,
    calendar,
    start_session,
    end_session,
    cache,
    show_progress,
    output_dir,
):
    """Minute-only bundle (skips daily resampling)"""
    if not os.path.exists(DEFAULT_CSV_DATA_PATH):
        raise ValueError(f"Path does not exist: {DEFAULT_CSV_DATA_PATH}")

    csv_files = glob.glob(os.path.join(DEFAULT_CSV_DATA_PATH, "*-EQ.csv"))
    csv_files.extend(glob.glob(os.path.join(DEFAULT_CSV_DATA_PATH, "NIFTY*.csv")))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {DEFAULT_CSV_DATA_PATH}")

    # Load all minute data
    all_minute_data = []
    successful_symbols = []
    
    for file_path in csv_files:
        symbol, minute_data = load_csv_data(file_path)
        if symbol is None:
            continue
            
        minute_data['symbol'] = symbol
        minute_data = minute_data.reset_index().rename(columns={'datetime': 'date'})
        all_minute_data.append(minute_data)
        successful_symbols.append(symbol)

    if not all_minute_data:
        raise ValueError("No minute data loaded")

    # Generate asset metadata (same as before)
    combined = pd.concat(all_minute_data)
    asset_metadata = combined.groupby('symbol').agg({'date': ['min', 'max']})
    asset_metadata.columns = ['start_date', 'end_date']
    asset_metadata['exchange'] = 'NSE'
    asset_metadata['auto_close_date'] = asset_metadata['end_date'] + pd.Timedelta(days=1)
    
    # Handle indices
    index_symbols = ['NIFTY50', 'BANKNIFTY']
    asset_metadata.loc[asset_metadata.index.isin(index_symbols), 'exchange'] = 'NSE_INDEX'
    
    # Write assets
    exchanges = pd.DataFrame({
        'exchange': ['NSE', 'NSE_INDEX'],
        'canonical_name': ['National Stock Exchange of India', 'NSE Indices'],
        'country_code': ['IN', 'IN']
    })
    
    asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)

    # Write minute bars
    symbol_map = {symbol: idx for idx, symbol in enumerate(asset_metadata.index)}
    minute_data_indexed = combined.set_index(['date', 'symbol'])

    def minute_data_generator():
        for symbol, asset_id in symbol_map.items():
            if symbol in minute_data_indexed.index.get_level_values('symbol'):
                asset_data = minute_data_indexed.xs(symbol, level=1)
                asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']]
                asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
                yield asset_id, asset_data

    minute_bar_writer.write(minute_data_generator(), show_progress=show_progress)

    # Empty adjustments (no splits/dividends)
    adjustment_writer.write(
        splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
        dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount'])
    )

    log.info(f"Success! Processed {len(successful_symbols)} symbols.")