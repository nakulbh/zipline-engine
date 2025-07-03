import os
import pandas as pd
import logging
import pytz
from zipline.data.bundles import register
from zipline.utils.calendar_utils import get_calendar
import glob

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

# Path to your local CSV files
CSV_DATA_PATH = "/media/nakulbh/SanDisk/eq-files"

def load_csv_data(file_path):
    """Load and process CSV data from local files with proper timezone handling"""
    try:
        # Read CSV file - only load the columns we need
        df = pd.read_csv(file_path, usecols=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert datetime column to IST then UTC
        df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(IST).dt.tz_convert(UTC)
        
        # Round timestamps to nearest minute to align with trading calendar
        # CSV data has timestamps ending with :59, but calendar expects :00
        df['datetime'] = df['datetime'].dt.round('min')
        
        # Extract symbol from filename
        symbol = os.path.basename(file_path).replace('-EQ.csv', '').replace('.csv', '')
        
        # Handle NIFTY 50 special case
        if 'NIFTY 50' in symbol:
            symbol = 'NIFTY50'
        
        # Set datetime as index
        df.set_index('datetime', inplace=True)
        
        # Clean data
        df['volume'] = df['volume'].fillna(0).astype(int)
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        if df.empty:
            log.warning(f"No valid data found in {file_path}")
            return None, None
        
        log.info(f"Loaded {len(df)} records for {symbol} from {df.index.min()} to {df.index.max()}")
        return symbol, df
        
    except Exception as e:
        log.error(f"Error loading {file_path}: {str(e)}")
        return None, None

def resample_to_daily(minute_data):
    """Resample minute data to daily OHLCV"""
    try:
        if minute_data.empty:
            return pd.DataFrame()
        
        # Create a copy to avoid modifying original data
        data = minute_data.copy()
        
        # Convert to timezone-naive for resampling if needed
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # First resample to daily
        daily_data = data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # Filter out weekends (Monday=0, Sunday=6)
        daily_data = daily_data[daily_data.index.weekday < 5]
        
        # Forward fill OHLC prices but set volume to 0 for missing days
        daily_data[['open', 'high', 'low', 'close']] = daily_data[['open', 'high', 'low', 'close']].ffill()
        daily_data['volume'] = daily_data['volume'].fillna(0).astype(int)
        
        return daily_data.dropna(subset=['open', 'high', 'low', 'close'])
    except Exception as e:
        log.error(f"Error resampling to daily: {str(e)}")
        return pd.DataFrame()

def filter_to_trading_hours(minute_data):
    """Filter minute data to only include trading hours (9:15 AM to 3:30 PM IST)"""
    if minute_data.empty:
        return minute_data
    
    # Convert trading hours to UTC (9:15 AM to 3:30 PM IST = 3:45 AM to 10:00 AM UTC)
    start_time = pd.Timestamp('03:45:00').time()
    end_time = pd.Timestamp('10:00:00').time()
    
    return minute_data[
        (minute_data.index.time >= start_time) & 
        (minute_data.index.time <= end_time)
    ]

def local_csv_minute_bundle(
    environ,
    asset_db_writer,
    minute_bar_writer,
    daily_bar_writer,
    adjustment_writer,
    calendar,
    start_session,
    end_session,
    cache,
    show_progress,
    output_dir,
):
    """Custom NSE equities bundle using local CSV files"""
    
    if not os.path.exists(CSV_DATA_PATH):
        raise ValueError(f"CSV data path does not exist: {CSV_DATA_PATH}")
    
    log.info(f"Starting NSE equities bundle ingestion from {CSV_DATA_PATH}...")
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(CSV_DATA_PATH, "*-EQ.csv"))
    csv_files.extend(glob.glob(os.path.join(CSV_DATA_PATH, "NIFTY*.csv")))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {CSV_DATA_PATH}")
    
    log.info(f"Found {len(csv_files)} CSV files to process")
    
    # Process all files with deduplication
    symbols_data = {}  # Use dict to automatically handle duplicates
    successful_symbols = []
    
    for file_path in csv_files:
        try:
            if show_progress:
                log.info(f"Processing {os.path.basename(file_path)}...")
            
            symbol, minute_data = load_csv_data(file_path)
            if symbol is None or minute_data is None:
                continue
            
            # Filter to trading hours
            minute_data = filter_to_trading_hours(minute_data)
            if minute_data.empty:
                log.warning(f"No trading hours data for {symbol}")
                continue
            
            # If symbol already exists, combine the data
            if symbol in symbols_data:
                log.info(f"Combining data for duplicate symbol: {symbol}")
                existing_data = symbols_data[symbol]
                combined_data = pd.concat([existing_data, minute_data]).sort_index()
                # Remove duplicates by keeping the last value for each timestamp
                combined_data = combined_data.groupby(combined_data.index).last()
                symbols_data[symbol] = combined_data
            else:
                symbols_data[symbol] = minute_data
                successful_symbols.append(symbol)
            
        except Exception as e:
            log.error(f"Failed to process {file_path}: {str(e)}")
            continue
    
    if not symbols_data:
        raise ValueError("No valid data was successfully loaded")
    
    # Prepare data for writers
    all_minute_data = []
    all_daily_data = []
    
    for symbol, minute_data in symbols_data.items():
        # Prepare minute data
        minute_df = minute_data.copy()
        minute_df = minute_df.reset_index()
        minute_df.rename(columns={'datetime': 'date'}, inplace=True)
        minute_df['symbol'] = symbol
        all_minute_data.append(minute_df)
        
        # Prepare daily data
        daily_data = resample_to_daily(minute_data)
        if not daily_data.empty:
            daily_data = daily_data.reset_index()
            daily_data.rename(columns={'datetime': 'date'}, inplace=True)
            daily_data['symbol'] = symbol
            all_daily_data.append(daily_data)
    
    if not all_minute_data or not all_daily_data:
        raise ValueError("No valid data was successfully loaded")
    
    # Combine all data
    try:
        minute_data_combined = pd.concat(all_minute_data, ignore_index=True)
        daily_data_combined = pd.concat(all_daily_data, ignore_index=True)
    except ValueError as e:
        log.error(f"Error combining data: {str(e)}")
        raise
    
    log.info(f"Combined data: {len(minute_data_combined)} minute bars, {len(daily_data_combined)} daily bars")
    
    # Generate asset metadata from unique symbols
    asset_metadata_list = []
    unique_symbols = list(symbols_data.keys())
    
    for symbol in unique_symbols:
        symbol_daily_data = daily_data_combined[daily_data_combined['symbol'] == symbol]
        if not symbol_daily_data.empty:
            start_date = symbol_daily_data['date'].min()
            end_date = symbol_daily_data['date'].max()
            
            # Ensure dates are timezone-naive
            if hasattr(start_date, 'tz') and start_date.tz is not None:
                start_date = start_date.tz_localize(None)
            if hasattr(end_date, 'tz') and end_date.tz is not None:
                end_date = end_date.tz_localize(None)
            
            # Determine exchange
            exchange = 'NSE_INDEX' if symbol in ['NIFTY50', 'BANKNIFTY'] else 'NSE'
            
            asset_metadata_list.append({
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'exchange': exchange,
                'auto_close_date': end_date + pd.Timedelta(days=1)
            })
    
    asset_metadata = pd.DataFrame(asset_metadata_list)
    
    # Write asset metadata
    exchanges = pd.DataFrame([
        ['NSE', 'XBOM', 'IN'],
        ['NSE_INDEX', 'XBOM', 'IN']
    ], columns=['exchange', 'canonical_name', 'country_code'])
    
    asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)
    log.info(f"Asset metadata written for {len(asset_metadata)} symbols")
    
    # Create symbol map
    symbol_map = {symbol: idx for idx, symbol in enumerate(asset_metadata['symbol'])}
    
    # Get trading sessions using the proper calendar
    from zipline.utils.calendar_utils import get_calendar
    trading_calendar = get_calendar('XBOM')
    
    min_date = daily_data_combined['date'].min()
    max_date = daily_data_combined['date'].max()
    
    # Ensure dates are timezone-naive
    if hasattr(min_date, 'tz') and min_date.tz is not None:
        min_date = min_date.tz_localize(None)
    if hasattr(max_date, 'tz') and max_date.tz is not None:
        max_date = max_date.tz_localize(None)
    
    # Get actual trading sessions from the calendar
    sessions = trading_calendar.sessions_in_range(
        pd.Timestamp(min_date),
        pd.Timestamp(max_date)
    )
    # Convert to timezone-naive for consistency
    sessions = sessions.tz_localize(None)
    log.info(f"Trading sessions: {len(sessions)} from {sessions[0]} to {sessions[-1]}")
    
    # Write minute bars with proper calendar alignment
    if minute_bar_writer:
        log.info("Writing minute bars...")
        minute_data_indexed = minute_data_combined.set_index(['date', 'symbol'])
        
        # Generate all valid minute timestamps for the trading sessions
        all_minutes = trading_calendar.sessions_minutes(
            pd.Timestamp(sessions[0]),
            pd.Timestamp(sessions[-1])
        )
        
        log.info(f"Trading calendar has {len(all_minutes)} valid minutes from {all_minutes[0]} to {all_minutes[-1]}")
        
        def minute_data_generator():
            for symbol, asset_id in symbol_map.items():
                try:
                    if symbol in minute_data_indexed.index.get_level_values('symbol'):
                        asset_data = minute_data_indexed.xs(symbol, level=1)
                        asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']].copy()
                        
                        # Clean the data
                        asset_data = asset_data.dropna(subset=['open', 'high', 'low', 'close'])
                        asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
                        asset_data = asset_data.sort_index()
                        
                        # Ensure proper timezone handling
                        if asset_data.index.tz is None:
                            asset_data.index = asset_data.index.tz_localize('UTC')
                        elif asset_data.index.tz != pytz.UTC:
                            asset_data.index = asset_data.index.tz_convert('UTC')
                        
                        # Filter to only include data within the valid trading minutes
                        asset_data = asset_data[asset_data.index.isin(all_minutes)]
                        
                        # Validate data quality
                        asset_data = asset_data[
                            (asset_data['open'] > 0) &
                            (asset_data['high'] > 0) &
                            (asset_data['low'] > 0) &
                            (asset_data['close'] > 0) &
                            (asset_data['high'] >= asset_data['low']) &
                            (asset_data['high'] >= asset_data['open']) &
                            (asset_data['high'] >= asset_data['close']) &
                            (asset_data['low'] <= asset_data['open']) &
                            (asset_data['low'] <= asset_data['close'])
                        ]
                        
                        if len(asset_data) > 0:
                            log.info(f"Writing {len(asset_data)} minute bars for {symbol}")
                            yield asset_id, asset_data
                        else:
                            log.warning(f"No valid minute data for {symbol}")
                            
                except Exception as e:
                    log.error(f"Error processing minute data for {symbol}: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        minute_bar_writer.write(minute_data_generator(), show_progress=show_progress)
    
    # Write daily bars (timezone-naive)
    log.info("Writing daily bars...")
    daily_data_indexed = daily_data_combined.set_index(['date', 'symbol'])
    
    def daily_data_generator():
        for symbol, asset_id in symbol_map.items():
            try:
                if symbol in daily_data_indexed.index.get_level_values('symbol'):
                    asset_data = daily_data_indexed.xs(symbol, level=1)
                    
                    # Remove duplicates if any
                    asset_data = asset_data.groupby(asset_data.index).last()
                    
                    # Reindex to include all trading sessions
                    asset_data = asset_data.reindex(sessions)
                    
                    # Forward fill OHLC prices but keep volume as 0 for missing days
                    asset_data[['open', 'high', 'low', 'close']] = asset_data[['open', 'high', 'low', 'close']].ffill()
                    asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
                    
                    # Remove rows with NaN values in OHLC
                    asset_data = asset_data.dropna(subset=['open', 'high', 'low', 'close'])
                    
                    # Validate data quality
                    asset_data = asset_data[
                        (asset_data['open'] > 0) &
                        (asset_data['high'] > 0) &
                        (asset_data['low'] > 0) &
                        (asset_data['close'] > 0) &
                        (asset_data['high'] >= asset_data['low']) &
                        (asset_data['high'] >= asset_data['open']) &
                        (asset_data['high'] >= asset_data['close']) &
                        (asset_data['low'] <= asset_data['open']) &
                        (asset_data['low'] <= asset_data['close'])
                    ]
                    
                    if len(asset_data) > 0:
                        log.info(f"Writing {len(asset_data)} daily bars for {symbol}")
                        yield asset_id, asset_data
                    else:
                        log.warning(f"No valid daily data for {symbol}")
                        
            except Exception as e:
                log.error(f"Error processing daily data for {symbol}: {str(e)}")
                import traceback
                traceback.print_exc()
    
    daily_bar_writer.write(daily_data_generator(), show_progress=show_progress)
    
    # Write empty adjustments
    adjustment_writer.write(
        splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
        dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']),
    )
    
    log.info(f"Ingestion completed! Processed {len(unique_symbols)} symbols: {', '.join(unique_symbols)}")

# Register the bundle with comprehensive error handling
try:
    register(
        'nse-local-minute-bundle',
        local_csv_minute_bundle,
        calendar_name='XBOM',
        minutes_per_day=375,
        create_writers=True
    )
    log.info("✅ nse-local-minute-bundle registered successfully")
except Exception as e:
    log.error(f"❌ Error registering nse-local-minute-bundle: {e}")
    import traceback
    traceback.print_exc()

# Also register a simpler daily-only bundle for testing
def nse_daily_bundle(
    environ,
    asset_db_writer,
    minute_bar_writer,
    daily_bar_writer,
    adjustment_writer,
    calendar,
    start_session,
    end_session,
    cache,
    show_progress,
    output_dir,
):
    """Simplified NSE daily bundle"""
    # Use the same ingestion logic but skip minute bars
    local_csv_minute_bundle(
        environ, asset_db_writer, None, daily_bar_writer, 
        adjustment_writer, calendar, start_session, end_session,
        cache, show_progress, output_dir
    )

try:
    register(
        'nse-daily-bundle',
        nse_daily_bundle,
        calendar_name='XBOM',
        create_writers=True
    )
    log.info("✅ nse-daily-bundle registered successfully")
except Exception as e:
    log.error(f"❌ Error registering nse-daily-bundle: {e}")
    import traceback
    traceback.print_exc()