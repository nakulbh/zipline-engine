import os
import sys
import gc
import pandas as pd
import polars as pl
import duckdb
import logging
import pytz
from datetime import datetime, timedelta
from zipline.data.bundles import register
from zipline.utils.calendar_utils import get_calendar

# Import memory configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from memory_config import (
        get_recommended_chunk_size,
        should_run_gc,
        get_memory_status,
        MEMORY_THRESHOLD_MB
    )
except ImportError:
    # Fallback if memory_config is not available
    def get_recommended_chunk_size(total_records, available_memory_mb=None):
        return min(50000, max(10000, total_records // 100))

    def should_run_gc(chunk_num, current_memory_mb):
        return chunk_num % 5 == 0

    def get_memory_status(current_memory_mb):
        return 'normal' if current_memory_mb < 4000 else 'warning'

    MEMORY_THRESHOLD_MB = 4000

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

# DuckDB database path
DUCKDB_PATH = "/media/nakulbh/PickleRick/nifty500_5year_data.duckdb"

def load_duckdb_data_chunked(db_path, start_date=None, end_date=None, symbols=None, chunk_size=100000):
    """
    Load data from DuckDB in chunks using Polars for memory-efficient processing

    Parameters:
    -----------
    db_path : str
        Path to the DuckDB database file
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date in 'YYYY-MM-DD' format
    symbols : list, optional
        List of symbols to filter
    chunk_size : int
        Number of records to process at a time (default: 100,000)

    Yields:
    -------
    pl.DataFrame
        Polars DataFrame chunks with the loaded data
    """
    try:
        # Connect to DuckDB with memory optimization
        conn = duckdb.connect(db_path)

        # Configure DuckDB for low memory usage
        conn.execute("SET memory_limit='2GB'")  # Limit DuckDB memory usage
        conn.execute("SET threads=2")  # Reduce thread count
        conn.execute("SET preserve_insertion_order=false")  # Disable order preservation
        conn.execute("PRAGMA max_temp_directory_size='5GB'")  # Limit temp directory size

        # Build the base query
        base_query = "SELECT security_id, symbol, timestamp, open, high, low, close, volume FROM nifty500_minute_data"
        conditions = []

        if start_date:
            conditions.append(f"DATE(timestamp) >= '{start_date}'")
        if end_date:
            conditions.append(f"DATE(timestamp) <= '{end_date}'")
        if symbols:
            symbol_list = "', '".join(symbols)
            conditions.append(f"symbol IN ('{symbol_list}')")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY symbol, timestamp"

        # Get total count for progress tracking
        count_query = f"SELECT COUNT(*) FROM ({base_query}) AS subquery"
        total_records = conn.execute(count_query).fetchone()[0]
        log.info(f"Total records to process: {total_records:,}")

        if total_records == 0:
            log.warning("No records found matching the criteria")
            conn.close()
            return

        # Process data in chunks
        offset = 0
        chunk_num = 0

        while offset < total_records:
            chunk_query = f"{base_query} LIMIT {chunk_size} OFFSET {offset}"
            log.info(f"Loading chunk {chunk_num + 1}, records {offset:,} to {min(offset + chunk_size, total_records):,}")

            # Execute query and convert to Polars DataFrame
            result = conn.execute(chunk_query).fetchall()

            if not result:
                break

            columns = ['security_id', 'symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
            df_chunk = pl.DataFrame(result, schema=columns, orient="row")

            log.info(f"Loaded chunk with {len(df_chunk)} records")
            yield df_chunk

            offset += chunk_size
            chunk_num += 1

        conn.close()
        log.info(f"Completed loading {chunk_num} chunks, total {total_records:,} records")

    except Exception as e:
        log.error(f"Error loading data from DuckDB: {str(e)}")
        raise

def get_data_summary(db_path, start_date=None, end_date=None, symbols=None):
    """
    Get summary statistics without loading all data into memory
    """
    try:
        conn = duckdb.connect(db_path)

        # Configure DuckDB for low memory usage
        conn.execute("SET memory_limit='2GB'")
        conn.execute("SET threads=2")
        conn.execute("SET preserve_insertion_order=false")
        conn.execute("PRAGMA max_temp_directory_size='5GB'")

        # Build the query
        base_query = "SELECT * FROM nifty500_minute_data"
        conditions = []

        if start_date:
            conditions.append(f"DATE(timestamp) >= '{start_date}'")
        if end_date:
            conditions.append(f"DATE(timestamp) <= '{end_date}'")
        if symbols:
            symbol_list = "', '".join(symbols)
            conditions.append(f"symbol IN ('{symbol_list}')")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # Get summary statistics
        summary_query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(timestamp) as start_date,
            MAX(timestamp) as end_date,
            MIN(close) as min_price,
            MAX(close) as max_price,
            AVG(close) as avg_price,
            MAX(volume) as max_volume,
            AVG(volume) as avg_volume
        FROM ({base_query}) AS subquery
        """

        result = conn.execute(summary_query).fetchone()
        conn.close()

        return {
            'total_records': result[0],
            'unique_symbols': result[1],
            'start_date': result[2],
            'end_date': result[3],
            'min_price': result[4],
            'max_price': result[5],
            'avg_price': result[6],
            'max_volume': result[7],
            'avg_volume': result[8]
        }

    except Exception as e:
        log.error(f"Error getting data summary: {str(e)}")
        raise

def clean_symbol_name(symbol):
    """
    Clean and standardize symbol names for Zipline
    """
    # Remove common suffixes and clean up
    symbol = symbol.replace(' LIMITED', '').replace(' LTD', '')
    symbol = symbol.replace(' COMPANY', '').replace(' CO.', '')
    symbol = symbol.replace('.', '').replace(' ', '_')
    symbol = symbol.replace('&', 'AND').replace('-', '_')
    symbol = symbol.upper()
    
    # Handle special cases
    if 'NIFTY' in symbol:
        symbol = symbol.replace('NIFTY_', 'NIFTY')
    
    return symbol

def process_data_for_zipline(df):
    """
    Process Polars DataFrame for Zipline ingestion
    
    Parameters:
    -----------
    df : pl.DataFrame
        Raw data from DuckDB
    
    Returns:
    --------
    tuple
        (processed_data_df, asset_metadata_df)
    """
    log.info("Processing data for Zipline ingestion...")
    
    # Clean symbol names
    df = df.with_columns([
        pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
    ])
    
    # Convert timestamp to datetime and handle timezone
    # Convert to pandas first for easier timezone handling
    df_pd = df.to_pandas()

    # Handle timezone conversion in pandas
    if df_pd['timestamp'].dt.tz is None:
        # If timezone-naive, assume IST and convert to UTC
        df_pd['datetime'] = pd.to_datetime(df_pd['timestamp']).dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')
    else:
        # If already timezone-aware, convert to UTC
        df_pd['datetime'] = pd.to_datetime(df_pd['timestamp']).dt.tz_convert('UTC')

    # Convert back to Polars
    df = pl.from_pandas(df_pd)
    
    # Round timestamps to nearest minute for alignment
    df = df.with_columns([
        pl.col("datetime").dt.round("1m")
    ])
    
    # Filter out invalid data
    df = df.filter(
        (pl.col("open") > 0) & 
        (pl.col("high") > 0) & 
        (pl.col("low") > 0) & 
        (pl.col("close") > 0) &
        (pl.col("volume") >= 0)
    )
    
    # Create asset metadata with date ranges
    asset_metadata = df.group_by("clean_symbol").agg([
        pl.col("symbol").first().alias("original_symbol"),
        pl.col("datetime").min().alias("start_date"),
        pl.col("datetime").max().alias("end_date")
    ]).sort("clean_symbol")

    # Add required metadata columns
    asset_metadata = asset_metadata.with_columns([
        pl.lit("NSE").alias("exchange"),
        pl.col("original_symbol").alias("asset_name"),
        pl.lit(None).alias("first_traded"),
        pl.lit(None).alias("auto_close_date"),
        pl.lit(1.0).alias("tick_size")
    ])
    
    # Convert to pandas for Zipline compatibility
    processed_data = df.select([
        "clean_symbol",
        "symbol",  # Keep original symbol for metadata generation
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]).to_pandas()
    
    asset_metadata_pd = asset_metadata.to_pandas()
    
    log.info(f"Processed {len(processed_data)} records for {len(asset_metadata_pd)} assets")

    return processed_data, asset_metadata_pd

def generate_asset_metadata(processed_data):
    """
    Generate asset metadata DataFrame for Zipline
    """
    # Get unique symbols and their date ranges
    symbol_info = processed_data.groupby('clean_symbol').agg({
        'datetime': ['min', 'max'],
        'symbol': 'first'  # Get original symbol name
    }).reset_index()

    # Flatten column names
    symbol_info.columns = ['symbol', 'start_date', 'end_date', 'asset_name']

    # Create asset metadata DataFrame
    asset_metadata = pd.DataFrame({
        'symbol': symbol_info['symbol'],
        'asset_name': symbol_info['asset_name'],
        'start_date': symbol_info['start_date'].dt.tz_localize(None),
        'end_date': symbol_info['end_date'].dt.tz_localize(None),
        'first_traded': symbol_info['start_date'].dt.tz_localize(None),
        'auto_close_date': symbol_info['end_date'].dt.tz_localize(None) + pd.Timedelta(days=1),
        'exchange': 'NSE',
        'tick_size': 0.01
    })

    # Set index to be sequential integers (asset IDs)
    asset_metadata.index = range(len(asset_metadata))
    asset_metadata.index.name = 'sid'

    return asset_metadata

def parse_pricing_and_vol(data, sessions, symbol_map):
    """
    Parse pricing and volume data for Zipline ingestion
    """
    # Set datetime as index and create multi-index with symbol
    data_indexed = data.set_index(['datetime', 'clean_symbol'])

    # Debug: log available symbols in this chunk
    available_symbols = set(data_indexed.index.get_level_values('clean_symbol'))
    log.info(f"Processing chunk with {len(available_symbols)} symbols: {sorted(list(available_symbols))[:5]}...")

    for asset_id, symbol in symbol_map.items():
        try:
            # Check if symbol exists in the data
            if symbol not in data_indexed.index.get_level_values('clean_symbol'):
                log.warning(f"No data found for symbol {symbol} (asset_id: {asset_id})")
                continue

            # Extract data for this symbol
            asset_data = data_indexed.xs(symbol, level=1)

            # Ensure the index is timezone-aware UTC for Zipline compatibility
            if asset_data.index.tz is None:
                asset_data.index = asset_data.index.tz_localize('UTC')
            elif asset_data.index.tz != pytz.UTC:
                asset_data.index = asset_data.index.tz_convert('UTC')

            # Don't reindex to all trading minutes - just use the data we have
            # This avoids creating excessive data and potential conflicts
            # asset_data is already properly indexed by datetime

            # Select only OHLCV columns
            asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']].copy()

            # Ensure volume is integer and handle NaN values
            asset_data['volume'] = asset_data['volume'].fillna(0).astype('int64')

            # Drop rows where all OHLC values are NaN
            asset_data = asset_data.dropna(subset=['open', 'high', 'low', 'close'], how='all')

            if not asset_data.empty:
                yield asset_id, asset_data
            else:
                log.warning(f"No valid data for symbol {symbol} (asset_id: {asset_id})")

        except KeyError:
            log.warning(f"No data found for symbol {symbol} (asset_id: {asset_id})")
            continue
        except Exception as e:
            log.error(f"Error processing symbol {symbol} (asset_id: {asset_id}): {str(e)}")
            continue

def duckdb_polars_minute_bundle(
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
    """
    Memory-efficient NSE equities bundle using DuckDB data source and chunked Polars processing
    """

    if not os.path.exists(DUCKDB_PATH):
        raise ValueError(f"DuckDB file does not exist: {DUCKDB_PATH}")

    log.info(f"Starting memory-efficient NSE equities bundle ingestion from DuckDB: {DUCKDB_PATH}")

    # Get data summary first - IMPORTANT: Use the date filters!
    # Check if we have environment variables for date range (from command line)
    cmd_start_date = os.environ.get('ZIPLINE_START_DATE')
    cmd_end_date = os.environ.get('ZIPLINE_END_DATE')

    if cmd_start_date and cmd_end_date:
        start_date_str = cmd_start_date
        end_date_str = cmd_end_date
        log.info(f"🎯 Using command-line date range: {start_date_str} to {end_date_str}")
    else:
        start_date_str = start_session.strftime('%Y-%m-%d') if start_session else None
        end_date_str = end_session.strftime('%Y-%m-%d') if end_session else None
        log.info(f"🎯 Using session date range: {start_date_str} to {end_date_str}")

    log.info(f"📅 Final filtering date range: {start_date_str} to {end_date_str}")

    summary = get_data_summary(DUCKDB_PATH, start_date_str, end_date_str)
    log.info(f"📊 Filtered data summary: {summary['total_records']:,} records, {summary['unique_symbols']} symbols")
    log.info(f"📅 Actual date range: {summary['start_date']} to {summary['end_date']}")

    if summary['total_records'] == 0:
        raise ValueError("No valid data found in DuckDB for the specified date range")

    # Determine optimal chunk size based on system memory and dataset size
    recommended_chunk = get_recommended_chunk_size(summary['total_records'])
    # For memory-constrained systems, use even smaller chunks
    chunk_size = min(recommended_chunk, 5000)  # Max 5K records per chunk for safety
    log.info(f"Using conservative chunk size: {chunk_size:,} records per chunk (recommended: {recommended_chunk:,})")
    log.info(f"Estimated {summary['total_records'] // chunk_size + 1} chunks to process")

    # Process data in chunks and collect asset metadata
    all_symbols = set()
    symbol_date_ranges = {}
    processed_chunks = []

    log.info("Processing data in memory-efficient chunks...")

    # CRITICAL FIX: Pass the date filters to the chunked loader
    log.info(f"🔄 Starting chunked processing with date filters: {start_date_str} to {end_date_str}")

    for chunk_num, raw_chunk in enumerate(load_duckdb_data_chunked(
        DUCKDB_PATH, start_date_str, end_date_str, chunk_size=chunk_size
    )):
        log.info(f"Processing chunk {chunk_num + 1}...")

        # Process this chunk
        processed_chunk, _ = process_data_for_zipline(raw_chunk)

        if not processed_chunk.empty:
            # Track symbols and their date ranges
            for symbol in processed_chunk['clean_symbol'].unique():
                all_symbols.add(symbol)
                symbol_data = processed_chunk[processed_chunk['clean_symbol'] == symbol]
                min_date = symbol_data['datetime'].min()
                max_date = symbol_data['datetime'].max()

                if symbol in symbol_date_ranges:
                    symbol_date_ranges[symbol]['start'] = min(symbol_date_ranges[symbol]['start'], min_date)
                    symbol_date_ranges[symbol]['end'] = max(symbol_date_ranges[symbol]['end'], max_date)
                else:
                    symbol_date_ranges[symbol] = {'start': min_date, 'end': max_date}

            processed_chunks.append(processed_chunk)

        # Clear the raw chunk from memory
        del raw_chunk

        # Memory management
        import psutil
        current_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        # Run garbage collection if needed
        if should_run_gc(chunk_num, current_memory):
            gc.collect()
            new_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            log.info(f"🗑️  Garbage collection: {current_memory:.1f} MB → {new_memory:.1f} MB")
            current_memory = new_memory

        # Check memory status
        memory_status = get_memory_status(current_memory)
        if memory_status == 'warning':
            log.warning(f"⚠️  High memory usage: {current_memory:.1f} MB")
        elif memory_status == 'critical':
            log.error(f"🚨 Critical memory usage: {current_memory:.1f} MB")
            log.error("Consider reducing chunk size or processing smaller date ranges")

        # Periodically log progress and memory usage
        if (chunk_num + 1) % 10 == 0:
            log.info(f"Processed {chunk_num + 1} chunks, {len(all_symbols)} unique symbols found")
            log.info(f"💾 Current memory usage: {current_memory:.1f} MB")

    log.info(f"Completed chunked processing. Found {len(all_symbols)} unique symbols")

    # Generate asset metadata - use a completely different approach to avoid timezone issues
    log.info("📝 Creating asset metadata with timezone-safe approach...")

    # Create asset metadata using only date strings, then convert to proper format
    asset_data = []
    for idx, symbol in enumerate(sorted(all_symbols)):
        start_dt = symbol_date_ranges[symbol]['start']
        end_dt = symbol_date_ranges[symbol]['end']

        # Convert to date strings first
        start_date_str = str(start_dt).split('T')[0].split(' ')[0][:10]
        end_date_str = str(end_dt).split('T')[0].split(' ')[0][:10]

        asset_data.append({
            'symbol': symbol,
            'asset_name': symbol,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'first_traded': start_date_str,
            'auto_close_date': end_date_str,
            'exchange': 'NSE',
            'tick_size': 0.01
        })

    # Create DataFrame from strings
    asset_metadata = pd.DataFrame(asset_data)

    # Convert date strings to datetime objects (timezone-naive)
    date_columns = ['start_date', 'end_date', 'first_traded', 'auto_close_date']
    for col in date_columns:
        asset_metadata[col] = pd.to_datetime(asset_metadata[col], format='%Y-%m-%d')

    # Adjust auto_close_date to be one day after end_date
    asset_metadata['auto_close_date'] = asset_metadata['end_date'] + pd.Timedelta(days=1)

    # Set index
    asset_metadata.index = range(len(asset_metadata))
    asset_metadata.index.name = 'sid'

    log.info(f"✅ Created asset metadata for {len(asset_metadata)} assets")

    # Create exchanges DataFrame with proper format for Zipline
    exchanges = pd.DataFrame({
        'exchange': ['NSE'],
        'canonical_name': ['XBOM'],  # Use XBOM as canonical name for NSE
        'country_code': ['IN']
    })

    log.info(f"Writing asset metadata for {len(asset_metadata)} assets")

    # Write asset metadata
    asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)

    # Create symbol map for asset IDs (asset_id -> cleaned_symbol)
    symbol_map = pd.Series(
        index=asset_metadata.index,
        data=asset_metadata['symbol'].values
    ).to_dict()

    # Get trading sessions for the actual data range using XBOM calendar
    overall_start = min(info['start'] for info in symbol_date_ranges.values())
    overall_end = max(info['end'] for info in symbol_date_ranges.values())

    # Convert to timezone-naive dates for calendar operations
    overall_start_date = overall_start.tz_localize(None).normalize()
    overall_end_date = overall_end.tz_localize(None).normalize()

    # Ensure we're using the XBOM calendar for NSE sessions
    from zipline.utils.calendar_utils import get_calendar
    xbom_calendar = get_calendar('XBOM')

    sessions = xbom_calendar.sessions_in_range(
        overall_start_date,
        overall_end_date
    )

    log.info(f"Writing minute bars for period {overall_start} to {overall_end}")
    log.info(f"Total trading sessions: {len(sessions)}")

    # Write minute bars using chunked data
    def chunked_data_generator():
        for chunk in processed_chunks:
            yield from parse_pricing_and_vol(chunk, sessions, symbol_map)

    minute_bar_writer.write(
        chunked_data_generator(),
        show_progress=show_progress,
    )

    # Clear processed chunks from memory
    del processed_chunks

    # Write empty adjustments (no splits/dividends data in current dataset)
    adjustment_writer.write(
        splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
        dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']),
    )

    log.info("Memory-efficient DuckDB Polars bundle ingestion completed successfully!")

# Register the bundle with XBOM calendar for NSE
import time
bundle_timestamp = int(time.time())
log.info(f"🔄 Registering bundle with timestamp: {bundle_timestamp}")
log.info(f"📅 Using XBOM calendar for NSE trading sessions")

register(
    'nse-duckdb-polars-bundle-v2',  # Changed name to force new registration
    duckdb_polars_minute_bundle,
    calendar_name='XBOM',  # XBOM is the correct calendar for NSE (Bombay Stock Exchange)
    minutes_per_day=375,   # NSE trading session: 9:15 AM to 3:30 PM (375 minutes)
    create_writers=True
)
