import os
import sys
import gc
import pandas as pd
import polars as pl
import duckdb
import logging
import pytz
import time
import tempfile
import shutil
import argparse
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from zipline.data.bundles import register
from zipline.utils.calendar_utils import get_calendar

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

# Configuration
DUCKDB_PATH = "/Volumes/PickleRick/nifty500_5year_data.duckdb"
TABLE_NAME = "nifty500_minute_data"

# Processing modes
LIMIT_STOCKS = False  # Set to True to limit to top liquid stocks
MAX_STOCKS = 100      # Maximum stocks when limiting
LAST_N_MONTHS = 12    # Months of data when limiting

# Custom date range (use full database range)
USE_CUSTOM_DATE_RANGE = True
CUSTOM_START_DATE = "2020-09-01"
CUSTOM_END_DATE = "2025-06-01"

# Cache configuration - Use faster internal storage for large datasets
CACHE_DIR = Path("~/Developer/Projects/zipline-cache/parquet_data").expanduser()
CACHE_DIR.mkdir(parents=True, exist_ok=True)
FORCE_REFRESH = False

# Memory optimization thresholds
SMALL_DATASET_THRESHOLD = 10_000_000     # 10M records
LARGE_DATASET_THRESHOLD = 50_000_000     # 50M records
ULTRA_LARGE_THRESHOLD = 500_000_000      # 500M records

def clean_symbol_name(symbol):
    """Clean and standardize symbol names for Zipline"""
    if isinstance(symbol, str):
        # Remove common suffixes and standardize
        symbol = symbol.replace(' LIMITED', '').replace(' LTD', '')
        symbol = symbol.replace(' COMPANY', '').replace(' CO.', '')
        symbol = symbol.replace('.', '').replace(' ', '_')
        symbol = symbol.replace('&', 'AND').replace('-', '_')
        symbol = symbol.upper()
        
        # Handle special cases
        if 'NIFTY' in symbol:
            symbol = symbol.replace('NIFTY_', 'NIFTY')
    
    return symbol

def get_data_range_info(db_path, required_start_date=None, required_end_date=None):
    """
    Get data range info and optionally filter stocks that don't have data in required date range
    
    Parameters:
    -----------
    db_path : str
        Path to DuckDB database
    required_start_date : str, optional
        Required start date in 'YYYY-MM-DD' format. Stocks without data from this date will be excluded.
    required_end_date : str, optional  
        Required end date in 'YYYY-MM-DD' format. Stocks without data until this date will be excluded.
    
    Returns:
    --------
    dict
        Contains global_start, global_end, total_symbols, total_records, and optionally valid_symbols
    """
    try:
        conn = duckdb.connect(db_path)
        conn.execute("SET memory_limit='8GB'")  # Increased for large dataset
        conn.execute("SET threads=8")  # Use all M4 performance cores
        
        # Get basic global info first
        basic_query = f"""
        SELECT 
            MIN(timestamp) as global_start,
            MAX(timestamp) as global_end,
            COUNT(DISTINCT symbol) as total_symbols,
            COUNT(*) as total_records
        FROM {TABLE_NAME}
        """
        
        basic_result = conn.execute(basic_query).fetchone()
        
        result_info = {
            'global_start': basic_result[0],
            'global_end': basic_result[1],
            'total_symbols': basic_result[2],
            'total_records': basic_result[3]
        }
        
        # If date range filtering is requested, find stocks with complete data coverage
        if required_start_date or required_end_date:
            log.info(f"🔍 Filtering stocks with complete data coverage...")
            
            # Find stocks that have data spanning the required date range
            coverage_query = f"""
            SELECT 
                symbol,
                MIN(DATE(timestamp)) as stock_start,
                MAX(DATE(timestamp)) as stock_end,
                COUNT(*) as data_points
            FROM {TABLE_NAME}
            GROUP BY symbol
            """
            
            # Add conditions for stocks that meet the date range requirements
            conditions = []
            if required_start_date:
                conditions.append(f"MIN(DATE(timestamp)) <= '{required_start_date}'")
            if required_end_date:
                conditions.append(f"MAX(DATE(timestamp)) >= '{required_end_date}'")
            
            if conditions:
                coverage_query += f"""
                HAVING {' AND '.join(conditions)}
                AND COUNT(*) > 1000  -- Ensure sufficient data points
                """
            
            coverage_query += " ORDER BY symbol"
            
            coverage_results = conn.execute(coverage_query).fetchall()
            
            valid_symbols = [row[0] for row in coverage_results]
            
            log.info(f"📊 Found {len(valid_symbols)} stocks with complete coverage from {basic_result[2]} total stocks")
            
            # Get filtered stats for valid symbols only
            if valid_symbols:
                symbol_list = "', '".join(valid_symbols)
                filtered_query = f"""
                SELECT 
                    MIN(timestamp) as filtered_start,
                    MAX(timestamp) as filtered_end,
                    COUNT(DISTINCT symbol) as filtered_symbols,
                    COUNT(*) as filtered_records
                FROM {TABLE_NAME}
                WHERE symbol IN ('{symbol_list}')
                """
                
                filtered_result = conn.execute(filtered_query).fetchone()
                
                result_info.update({
                    'filtered_start': filtered_result[0],
                    'filtered_end': filtered_result[1], 
                    'filtered_symbols': filtered_result[2],
                    'filtered_records': filtered_result[3],
                    'valid_symbols': valid_symbols
                })
                
                log.info(f"📈 Filtered dataset: {filtered_result[3]:,} records for {filtered_result[2]} symbols")
                log.info(f"📅 Filtered date range: {filtered_result[0]} to {filtered_result[1]}")
            else:
                log.warning("⚠️ No stocks found with complete coverage for the required date range!")
                result_info['valid_symbols'] = []
        
        conn.close()
        return result_info
        
    except Exception as e:
        log.error(f"Error getting data range info: {str(e)}")
        raise

def get_top_liquid_stocks(db_path, limit=50, months_back=12):
    """Get top liquid stocks based on average volume"""
    try:
        conn = duckdb.connect(db_path)
        conn.execute("SET memory_limit='8GB'")  # Increased for large dataset
        conn.execute("SET threads=8")  # Use all M4 performance cores
        
        # Calculate date range for liquidity analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        liquidity_query = f"""
        SELECT
            symbol,
            AVG(volume) as avg_volume,
            COUNT(*) as data_points
        FROM {TABLE_NAME}
        WHERE DATE(timestamp) >= '{start_date.strftime('%Y-%m-%d')}'
        AND DATE(timestamp) <= '{end_date.strftime('%Y-%m-%d')}'
        AND volume > 0
        GROUP BY symbol
        HAVING COUNT(*) > 1000
        ORDER BY avg_volume DESC
        LIMIT {limit}
        """
        
        result = conn.execute(liquidity_query).fetchall()
        conn.close()
        
        symbols = [row[0] for row in result]
        log.info(f"Selected {len(symbols)} liquid stocks")
        
        return symbols
        
    except Exception as e:
        log.error(f"Error getting liquid stocks: {str(e)}")
        return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR']

def extract_to_parquet_optimized(db_path, start_date=None, end_date=None, symbols=None, force_refresh=False):
    """
    Extract data from DuckDB to Parquet with optimized memory usage
    """
    # Create cache filename
    cache_params = f"{start_date}_{end_date}_{len(symbols) if symbols else 'all'}"
    cache_file = CACHE_DIR / f"market_data_{cache_params}.parquet"
    
    # Check cache
    if cache_file.exists() and not force_refresh:
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age.days < 1:
            log.info(f"📁 Using cached file: {cache_file}")
            return str(cache_file)
    
    log.info(f"🔄 Extracting data to: {cache_file}")
    
    try:
        conn = duckdb.connect(db_path)
        
        # Optimized memory settings for ultra-large datasets
        conn.execute("SET memory_limit='12GB'")  # Use more RAM
        conn.execute("SET threads=8")  # Use all M4 performance cores
        conn.execute("SET preserve_insertion_order=false")
        conn.execute("SET enable_progress_bar=false")  # Disable for speed
        conn.execute("SET checkpoint_threshold='1GB'")  # Less frequent checkpoints
        
        # Build query with consistent date range
        base_query = f"""
        SELECT 
            symbol,
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM {TABLE_NAME}
        """
        
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
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM ({base_query}) AS subquery"
        total_records = conn.execute(count_query).fetchone()[0]
        log.info(f"📊 Total records to extract: {total_records:,}")
        
        # Choose extraction strategy based on size
        if total_records > ULTRA_LARGE_THRESHOLD:
            return _extract_ultra_large_dataset(conn, base_query, cache_file, total_records)
        elif total_records > LARGE_DATASET_THRESHOLD:
            return _extract_large_dataset(conn, base_query, cache_file, total_records)
        elif total_records > SMALL_DATASET_THRESHOLD:
            return _extract_medium_dataset(conn, base_query, cache_file, total_records)
        else:
            return _extract_small_dataset(conn, base_query, cache_file)
            
    except Exception as e:
        log.error(f"❌ Extraction failed: {str(e)}")
        raise

def _extract_small_dataset(conn, query, cache_file):
    """Extract small datasets directly"""
    log.info("📊 Using direct extraction for small dataset")
    
    result = conn.execute(query).pl()
    log.info(f"✅ Extracted {len(result):,} records")
    
    # Write to compressed Parquet
    result.write_parquet(
        cache_file,
        compression="zstd",
        compression_level=3,
        use_pyarrow=True
    )
    
    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
    log.info(f"✅ Created {file_size_mb:.1f} MB Parquet file")
    
    conn.close()
    return str(cache_file)

def _extract_medium_dataset(conn, base_query, cache_file, total_records):
    """Extract medium datasets with chunking"""
    log.info("🔄 Using chunked extraction for medium dataset")
    
    chunk_size = 500_000  # Increased chunk size for better performance
    total_chunks = (total_records + chunk_size - 1) // chunk_size
    
    log.info(f"📊 Processing {total_chunks} chunks of {chunk_size:,} records")
    
    chunks = []
    start_time = time.time()
    
    for i in range(total_chunks):
        offset = i * chunk_size
        chunk_query = f"{base_query} LIMIT {chunk_size} OFFSET {offset}"
        
        if i % 5 == 0 or i == total_chunks - 1:  # More frequent progress updates
            progress = (i + 1) / total_chunks * 100
            elapsed = time.time() - start_time
            log.info(f"📊 Processing chunk {i+1}/{total_chunks} ({progress:.1f}%) - {elapsed:.1f}s elapsed")
        
        chunk_result = conn.execute(chunk_query).pl()
        if len(chunk_result) == 0:
            break
            
        chunks.append(chunk_result)
        
        # Memory management - combine fewer chunks to reduce overhead
        if len(chunks) >= 3:  # Reduced from 5 to 3
            combined = pl.concat(chunks)
            chunks = [combined]
            gc.collect()
    
    # Final combination
    log.info("🔄 Combining all chunks...")
    final_result = pl.concat(chunks)
    
    # Write to Parquet with optimized settings
    final_result.write_parquet(
        cache_file,
        compression="lz4",  # Faster compression than zstd
        compression_level=1,  # Lower compression for speed
        use_pyarrow=True
    )
    
    total_time = time.time() - start_time
    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
    
    log.info(f"✅ Processed {len(final_result):,} records in {total_time:.1f}s")
    log.info(f"✅ Created {file_size_mb:.1f} MB Parquet file")
    
    conn.close()
    return str(cache_file)

def _extract_ultra_large_dataset(conn, base_query, cache_file, total_records):
    """Extract ultra-large datasets (900M+ records) using optimized parallel processing"""
    log.info("🚀 Using ultra-large dataset extraction for 900M+ records")
    
    # Get unique symbols first with optimized query
    symbol_query = f"""
    SELECT DISTINCT symbol 
    FROM ({base_query}) AS subquery 
    ORDER BY symbol
    """
    
    symbols = [row[0] for row in conn.execute(symbol_query).fetchall()]
    log.info(f"📊 Processing {len(symbols)} symbols in parallel batches")
    
    # Create multiple temporary directories for parallel processing
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_ultra_"))
    symbol_files = []
    
    try:
        start_time = time.time()
        
        # Process symbols in larger batches for efficiency
        batch_size = 5  # Process 5 symbols at once
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, len(symbols))
            batch_symbols = symbols[batch_start:batch_end]
            
            progress = (batch_idx + 1) / total_batches * 100
            elapsed = time.time() - start_time
            log.info(f"📊 Processing batch {batch_idx+1}/{total_batches} ({progress:.1f}%) - {elapsed:.1f}s elapsed")
            log.info(f"🔄 Batch symbols: {', '.join(batch_symbols)}")
            
            # Process each symbol in the batch
            for symbol in batch_symbols:
                try:
                    # Optimized query for this symbol with proper WHERE clause handling
                    if "WHERE" in base_query:
                        # If WHERE clause exists, add symbol condition with AND
                        symbol_query_text = base_query.replace("WHERE", f"WHERE symbol = '{symbol}' AND")
                    else:
                        # If no WHERE clause, add it
                        symbol_query_text = base_query.replace(
                            f"FROM {TABLE_NAME}",
                            f"FROM {TABLE_NAME} WHERE symbol = '{symbol}'"
                        )
                    
                    symbol_data = conn.execute(symbol_query_text).pl()
                    if len(symbol_data) > 0:
                        symbol_file = temp_dir / f"{symbol}.parquet"
                        # Use fastest compression for intermediate files
                        symbol_data.write_parquet(
                            symbol_file, 
                            compression="lz4", 
                            compression_level=1,
                            use_pyarrow=True
                        )
                        symbol_files.append(symbol_file)
                        
                except Exception as e:
                    log.warning(f"⚠️ Error processing {symbol}: {str(e)}")
                    continue
            
            # Aggressive garbage collection every batch
            gc.collect()
        
        # Combine all symbol files using streaming approach
        log.info(f"🔄 Combining {len(symbol_files)} symbol files using streaming...")
        
        if len(symbol_files) == 0:
            raise ValueError("No symbol files were created successfully. Check database connectivity and query syntax.")
        
        # Process files in larger batches for efficiency
        combine_batch_size = 20  # Combine 20 files at once
        combined_chunks = []
        
        for i in range(0, len(symbol_files), combine_batch_size):
            batch_files = symbol_files[i:i + combine_batch_size]
            
            log.info(f"🔄 Combining batch {i//combine_batch_size + 1}/{(len(symbol_files) + combine_batch_size - 1)//combine_batch_size}")
            
            try:
                # Read and combine files in this batch
                batch_data = []
                for file_path in batch_files:
                    if file_path.exists():
                        data = pl.read_parquet(file_path)
                        if len(data) > 0:
                            batch_data.append(data)
                
                if batch_data:
                    batch_combined = pl.concat(batch_data)
                    combined_chunks.append(batch_combined)
                
                # Clean up batch files immediately
                for f in batch_files:
                    if f.exists():
                        f.unlink()
                
                # Aggressive memory management
                del batch_data
                gc.collect()
                
            except Exception as e:
                log.warning(f"⚠️ Error combining batch: {str(e)}")
                continue
        
        # Final combination and write with optimized settings
        if len(combined_chunks) == 0:
            raise ValueError("No data was successfully extracted from any symbols.")
            
        log.info("🔄 Final combination and write...")
        final_result = pl.concat(combined_chunks)
        
        # Write final file with balanced compression
        final_result.write_parquet(
            cache_file,
            compression="lz4",  # Fast compression for large files
            compression_level=1,
            use_pyarrow=True,
            row_group_size=100_000  # Optimize for reading performance
        )
        
        total_time = time.time() - start_time
        file_size_mb = cache_file.stat().st_size / (1024 * 1024)
        records_per_second = len(final_result) / total_time if total_time > 0 else 0
        
        log.info(f"✅ Processed {len(final_result):,} records in {total_time:.1f}s")
        log.info(f"✅ Speed: {records_per_second:,.0f} records/second")
        log.info(f"✅ Created {file_size_mb:.1f} MB Parquet file")
        
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except:
                log.warning("⚠️ Could not clean up temp directory completely")
    
    conn.close()
    return str(cache_file)

def _extract_large_dataset(conn, base_query, cache_file, total_records):
    """Extract large datasets using symbol-by-symbol processing"""
    log.info("🚀 Using symbol-by-symbol extraction for large dataset")
    
    # Get unique symbols first
    symbol_query = f"""
    SELECT DISTINCT symbol 
    FROM ({base_query}) AS subquery 
    ORDER BY symbol
    """
    
    symbols = [row[0] for row in conn.execute(symbol_query).fetchall()]
    log.info(f"📊 Processing {len(symbols)} symbols individually")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_large_"))
    symbol_files = []
    
    try:
        start_time = time.time()
        
        for i, symbol in enumerate(symbols):
            if i % 20 == 0:
                progress = i / len(symbols) * 100
                log.info(f"📊 Processing symbol {i+1}/{len(symbols)} ({progress:.1f}%): {symbol}")
            
            # Query for this symbol with proper WHERE clause handling
            try:
                if "WHERE" in base_query:
                    # If WHERE clause exists, add symbol condition with AND
                    symbol_query_text = base_query.replace("WHERE", f"WHERE symbol = '{symbol}' AND")
                else:
                    # If no WHERE clause, add it
                    symbol_query_text = base_query.replace(
                        f"FROM {TABLE_NAME}",
                        f"FROM {TABLE_NAME} WHERE symbol = '{symbol}'"
                    )
                
                # Debug logging
                if symbol == 'AAVAS':  # Log first symbol for debugging
                    log.info(f"🐛 Debug query for {symbol}: {symbol_query_text}")
                
                symbol_data = conn.execute(symbol_query_text).pl()
                if len(symbol_data) > 0:
                    symbol_file = temp_dir / f"{symbol}.parquet"
                    symbol_data.write_parquet(symbol_file, compression="zstd", compression_level=1)
                    symbol_files.append(symbol_file)
            except Exception as e:
                log.warning(f"⚠️ Error processing {symbol}: {str(e)}")
                continue
        
        # Combine all symbol files
        log.info(f"🔄 Combining {len(symbol_files)} symbol files...")
        
        if len(symbol_files) == 0:
            raise ValueError("No symbol files were created successfully. Check database connectivity and query syntax.")
        
        combined_chunks = []
        batch_size = 10
        
        for i in range(0, len(symbol_files), batch_size):
            batch_files = symbol_files[i:i + batch_size]
            batch_data = [pl.read_parquet(f) for f in batch_files]
            
            if batch_data:
                batch_combined = pl.concat(batch_data)
                combined_chunks.append(batch_combined)
            
            # Clean up batch files
            for f in batch_files:
                f.unlink()
            
            gc.collect()
        
        # Final combination and write
        if len(combined_chunks) == 0:
            raise ValueError("No data was successfully extracted from any symbols.")
            
        final_result = pl.concat(combined_chunks)
        final_result.write_parquet(
            cache_file,
            compression="zstd",
            compression_level=3,
            use_pyarrow=True
        )
        
        total_time = time.time() - start_time
        file_size_mb = cache_file.stat().st_size / (1024 * 1024)
        
        log.info(f"✅ Processed {len(final_result):,} records in {total_time:.1f}s")
        log.info(f"✅ Created {file_size_mb:.1f} MB Parquet file")
        
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    conn.close()
    return str(cache_file)

def create_asset_metadata_from_parquet(parquet_path, global_start=None, global_end=None):
    """Create asset metadata ensuring consistent date ranges"""
    
    log.info("📊 Creating asset metadata from Parquet...")
    
    # Read minimal data for metadata
    metadata_df = pl.scan_parquet(parquet_path).select([
        "symbol",
        "timestamp"
    ]).collect()
    
    # Clean symbols
    metadata_df = metadata_df.with_columns([
        pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
    ])
    
    # Convert timestamps
    try:
        metadata_df = metadata_df.with_columns([
            pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
        ])
    except:
        metadata_df = metadata_df.with_columns([
            pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
        ])
    
    # Create metadata with consistent date ranges
    asset_metadata = metadata_df.group_by("clean_symbol").agg([
        pl.col("symbol").first().alias("original_symbol"),
        pl.col("datetime").min().alias("actual_start"),
        pl.col("datetime").max().alias("actual_end")
    ]).sort("clean_symbol")
    
    # Use global dates if provided to ensure consistency
    if global_start and global_end:
        log.info(f"📅 Using consistent global date range: {global_start} to {global_end}")
        
        # Convert global dates to UTC if needed
        if isinstance(global_start, str):
            global_start = pd.Timestamp(global_start).tz_localize('Asia/Kolkata').tz_convert('UTC')
        if isinstance(global_end, str):
            global_end = pd.Timestamp(global_end).tz_localize('Asia/Kolkata').tz_convert('UTC')
        
        asset_metadata = asset_metadata.with_columns([
            pl.lit(global_start).alias("start_date"),
            pl.lit(global_end).alias("end_date")
        ])
    else:
        asset_metadata = asset_metadata.with_columns([
            pl.col("actual_start").alias("start_date"),
            pl.col("actual_end").alias("end_date")
        ])
    
    # Add required columns
    asset_metadata = asset_metadata.with_columns([
        pl.lit("NSE").alias("exchange"),
        pl.col("original_symbol").alias("asset_name"),
        pl.lit(None).alias("first_traded"),
        pl.lit(None).alias("auto_close_date"),
        pl.lit(1.0).alias("tick_size")
    ])
    
    log.info(f"✅ Created metadata for {len(asset_metadata)} assets")
    return asset_metadata.to_pandas()

def streaming_parse_pricing_and_vol(parquet_path, sessions, symbol_map):
    """Memory-efficient streaming parser for Zipline writers"""
    
    log.info(f"🚀 Streaming data for {len(symbol_map)} assets")
    
    for asset_id, symbol in symbol_map.items():
        try:
            if asset_id % 25 == 0:
                log.info(f"📊 Processing asset {asset_id}: {symbol}")
            
            # Read only this symbol's data
            symbol_data = pl.scan_parquet(parquet_path).filter(
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8) == symbol
            ).collect()
            
            if len(symbol_data) == 0:
                continue
            
            # Process timestamps
            symbol_data = symbol_data.with_columns([
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
            ])
            
            try:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            except:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            
            # Clean and filter data
            symbol_data = symbol_data.with_columns([
                pl.col("datetime").dt.round("1m")
            ]).filter(
                (pl.col("open") > 0) &
                (pl.col("high") > 0) &
                (pl.col("low") > 0) &
                (pl.col("close") > 0) &
                (pl.col("volume") >= 0)
            )
            
            # Market hours filter (9:15 AM to 3:30 PM IST = 3:45 AM to 10:00 AM UTC)
            symbol_data = symbol_data.filter(
                (pl.col("datetime").dt.hour() >= 3) &
                (pl.col("datetime").dt.hour() < 10) &
                pl.col("datetime").dt.weekday().is_in([1, 2, 3, 4, 5])
            )
            
            if len(symbol_data) == 0:
                continue
            
            # Convert to pandas for Zipline
            asset_data = symbol_data.select([
                "datetime", "open", "high", "low", "close", "volume"
            ]).to_pandas()
            
            # Set datetime index
            asset_data = asset_data.set_index('datetime')
            
            # Ensure UTC timezone
            if asset_data.index.tz is None:
                asset_data.index = asset_data.index.tz_localize('UTC')
            elif asset_data.index.tz != pytz.UTC:
                asset_data.index = asset_data.index.tz_convert('UTC')
            
            asset_data = asset_data.sort_index()
            asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)
            
            if len(asset_data) > 0:
                yield asset_id, asset_data
                
        except Exception as e:
            log.error(f"❌ Error processing {symbol}: {str(e)}")
            continue
        
        # Memory management
        if asset_id % 50 == 0:
            gc.collect()

def generate_daily_bars_streaming(parquet_path, symbol_map, trading_sessions):
    """Generate daily bars using streaming approach"""
    
    log.info("📊 Generating daily bars...")
    
    for asset_id, symbol in symbol_map.items():
        try:
            # Read symbol data
            symbol_data = pl.scan_parquet(parquet_path).filter(
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8) == symbol
            ).collect()
            
            if len(symbol_data) == 0:
                continue
            
            # Process timestamps
            try:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            except:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            
            # Filter valid data and market hours
            symbol_data = symbol_data.filter(
                (pl.col("open") > 0) &
                (pl.col("high") > 0) &
                (pl.col("low") > 0) &
                (pl.col("close") > 0) &
                (pl.col("volume") >= 0) &
                (pl.col("datetime").dt.hour() >= 3) &
                (pl.col("datetime").dt.hour() < 10) &
                pl.col("datetime").dt.weekday().is_in([1, 2, 3, 4, 5])
            ).with_columns([
                pl.col("datetime").dt.date().alias("date")
            ])
            
            # Create daily aggregations
            daily_data = symbol_data.group_by("date").agg([
                pl.col("open").first(),
                pl.col("high").max(),
                pl.col("low").min(),
                pl.col("close").last(),
                pl.col("volume").sum()
            ]).with_columns([
                pl.col("date").cast(pl.Datetime).alias("datetime")
            ])
            
            # Convert to pandas and align with trading sessions
            daily_pd = daily_data.to_pandas()
            trading_session_dates = pd.DataFrame({'datetime': trading_sessions})
            
            # Merge and fill missing data
            daily_pd = trading_session_dates.merge(daily_pd, on='datetime', how='left')
            daily_pd = daily_pd.sort_values('datetime')
            
            # Forward fill OHLC data
            daily_pd['open'] = daily_pd['open'].ffill()
            daily_pd['high'] = daily_pd['high'].fillna(daily_pd['open'])
            daily_pd['low'] = daily_pd['low'].fillna(daily_pd['open'])
            daily_pd['close'] = daily_pd['close'].fillna(daily_pd['open'])
            daily_pd['volume'] = daily_pd['volume'].fillna(0)
            
            # Remove NaN rows
            daily_pd = daily_pd.dropna(subset=['open', 'high', 'low', 'close'])
            
            if len(daily_pd) > 0:
                daily_pd = daily_pd.set_index('datetime').sort_index()
                daily_pd['volume'] = daily_pd['volume'].fillna(0).astype(int)
                yield asset_id, daily_pd
                
        except Exception as e:
            log.error(f"❌ Error generating daily data for {symbol}: {str(e)}")
            continue

def clean_duckdb_bundle(
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
    Clean, optimized NSE bundle using DuckDB with memory-efficient processing
    """
    
    log.info("🚀 Starting clean DuckDB bundle ingestion")
    
    # Determine processing parameters first
    if USE_CUSTOM_DATE_RANGE:
        start_date_str = CUSTOM_START_DATE
        end_date_str = CUSTOM_END_DATE
        selected_symbols = None
        log.info(f"🎯 Using custom range: {start_date_str} to {end_date_str}")
    elif LIMIT_STOCKS:
        end_date_dt = datetime.now()
        start_date_dt = end_date_dt - timedelta(days=LAST_N_MONTHS * 30)
        start_date_str = start_date_dt.strftime('%Y-%m-%d')
        end_date_str = end_date_dt.strftime('%Y-%m-%d')
        selected_symbols = get_top_liquid_stocks(DUCKDB_PATH, MAX_STOCKS, LAST_N_MONTHS)
        log.info(f"🎯 Limited mode: {len(selected_symbols)} stocks, {start_date_str} to {end_date_str}")
    else:
        start_date_str = start_session.strftime('%Y-%m-%d') if start_session else None
        end_date_str = end_session.strftime('%Y-%m-%d') if end_session else None
        selected_symbols = None
        log.info(f"🎯 Session range: {start_date_str} to {end_date_str}")
    
    # Get data range info with filtering for stocks that have complete coverage
    data_info = get_data_range_info(DUCKDB_PATH, start_date_str, end_date_str)
    log.info(f"📊 Database contains {data_info['total_records']:,} records for {data_info['total_symbols']} symbols")
    log.info(f"📅 Global date range: {data_info['global_start']} to {data_info['global_end']}")
    
    # Use filtered symbols if date range filtering was applied
    if 'valid_symbols' in data_info and data_info['valid_symbols']:
        if selected_symbols is None:  # If no symbol selection was already applied
            selected_symbols = data_info['valid_symbols']
            log.info(f"🔍 Using {len(selected_symbols)} stocks with complete date coverage")
        else:
            # Intersect with already selected symbols
            selected_symbols = [s for s in selected_symbols if s in data_info['valid_symbols']]
            log.info(f"🔍 Filtered to {len(selected_symbols)} stocks with both liquidity and date coverage")
    elif 'valid_symbols' in data_info and not data_info['valid_symbols']:
        raise ValueError(f"No stocks found with complete data coverage for date range {start_date_str} to {end_date_str}")
    
    # Determine processing parameters
    
    # Stage 1: Extract to Parquet cache
    log.info("=" * 50)
    log.info("📦 STAGE 1: Extract to Parquet Cache")
    log.info("=" * 50)
    
    cache_file = f"market_data_{start_date_str}_{end_date_str}_{len(selected_symbols) if selected_symbols else 'all'}.parquet"
    parquet_path = CACHE_DIR / cache_file
    
    if parquet_path.exists() and not FORCE_REFRESH:
        log.info(f"📁 Using existing cache: {parquet_path}")
        file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
        log.info(f"📏 Cache size: {file_size_mb:.1f} MB")
    else:
        if not os.path.exists(DUCKDB_PATH):
            raise ValueError(f"Database not found: {DUCKDB_PATH}")
        
        parquet_path = extract_to_parquet_optimized(
            DUCKDB_PATH,
            start_date_str,
            end_date_str,
            selected_symbols,
            force_refresh=FORCE_REFRESH
        )
    
    # Stage 2: Create Zipline bundle
    log.info("=" * 50)
    log.info("🚀 STAGE 2: Create Zipline Bundle")
    log.info("=" * 50)
    
    # Create asset metadata with consistent date ranges
    asset_metadata = create_asset_metadata_from_parquet(
        parquet_path, 
        data_info['global_start'], 
        data_info['global_end']
    )
    
    if asset_metadata.empty:
        raise ValueError("No assets found in data")
    
    log.info(f"✅ Created metadata for {len(asset_metadata)} assets")
    
    # Prepare asset metadata for Zipline
    asset_data = []
    for _, row in asset_metadata.iterrows():
        symbol = row['clean_symbol']
        start_dt = row['start_date']
        end_dt = row['end_date']
        
        asset_data.append({
            'symbol': symbol,
            'asset_name': symbol,
            'start_date': pd.Timestamp(start_dt).tz_localize(None),
            'end_date': pd.Timestamp(end_dt).tz_localize(None),
            'first_traded': pd.Timestamp(start_dt).tz_localize(None),
            'auto_close_date': pd.Timestamp(end_dt).tz_localize(None) + pd.Timedelta(days=1),
            'exchange': 'NSE',
            'tick_size': 0.01
        })
    
    # Create final asset metadata DataFrame
    final_asset_metadata = pd.DataFrame(asset_data)
    final_asset_metadata.index = range(len(final_asset_metadata))
    final_asset_metadata.index.name = 'sid'
    
    # Create exchanges DataFrame
    exchanges = pd.DataFrame({
        'exchange': ['NSE'],
        'canonical_name': ['XBOM'],
        'country_code': ['IN']
    })
    
    # Write asset metadata
    log.info("📝 Writing asset metadata...")
    asset_db_writer.write(equities=final_asset_metadata, exchanges=exchanges)
    
    # Create symbol map
    symbol_map = pd.Series(
        index=final_asset_metadata.index,
        data=final_asset_metadata['symbol'].values
    ).to_dict()
    
    # Get trading sessions
    from zipline.utils.calendar_utils import get_calendar
    xbom_calendar = get_calendar('XBOM')
    
    overall_start = final_asset_metadata['start_date'].min()
    overall_end = final_asset_metadata['end_date'].max()
    
    sessions = xbom_calendar.sessions_in_range(overall_start, overall_end)
    log.info(f"📅 Trading sessions: {len(sessions)} from {overall_start} to {overall_end}")
    
    # Write minute bars
    log.info("📊 Writing minute bars...")
    def minute_data_generator():
        yield from streaming_parse_pricing_and_vol(parquet_path, sessions, symbol_map)
    
    minute_bar_writer.write(minute_data_generator(), show_progress=show_progress)
    
    # Write daily bars
    log.info("📊 Writing daily bars...")
    def daily_data_generator():
        yield from generate_daily_bars_streaming(parquet_path, symbol_map, sessions)
    
    daily_bar_writer.write(daily_data_generator(), show_progress=show_progress)
    
    # Write empty adjustments
    adjustment_writer.write(
        splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
        dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']),
    )
    
    log.info("🎉 Clean DuckDB bundle ingestion completed successfully!")

def extract_data_to_cache(force_refresh=False):
    """CLI function to extract data to cache"""
    log.info("🗂️ EXTRACTING DATA TO CACHE")
    
    if not os.path.exists(DUCKDB_PATH):
        raise ValueError(f"Database not found: {DUCKDB_PATH}")
    
    # Determine parameters
    if USE_CUSTOM_DATE_RANGE:
        start_date_str = CUSTOM_START_DATE
        end_date_str = CUSTOM_END_DATE
        selected_symbols = None
    elif LIMIT_STOCKS:
        end_date_dt = datetime.now()
        start_date_dt = end_date_dt - timedelta(days=LAST_N_MONTHS * 30)
        start_date_str = start_date_dt.strftime('%Y-%m-%d')
        end_date_str = end_date_dt.strftime('%Y-%m-%d')
        selected_symbols = get_top_liquid_stocks(DUCKDB_PATH, MAX_STOCKS, LAST_N_MONTHS)
    else:
        start_date_str = None
        end_date_str = None
        selected_symbols = None
    
    # Filter stocks with complete date coverage
    if start_date_str or end_date_str:
        data_info = get_data_range_info(DUCKDB_PATH, start_date_str, end_date_str)
        
        if 'valid_symbols' in data_info and data_info['valid_symbols']:
            if selected_symbols is None:
                selected_symbols = data_info['valid_symbols']
                log.info(f"🔍 Using {len(selected_symbols)} stocks with complete date coverage")
            else:
                # Intersect with already selected symbols
                selected_symbols = [s for s in selected_symbols if s in data_info['valid_symbols']]
                log.info(f"🔍 Filtered to {len(selected_symbols)} stocks with both criteria")
        elif 'valid_symbols' in data_info and not data_info['valid_symbols']:
            raise ValueError(f"No stocks found with complete data coverage for date range {start_date_str} to {end_date_str}")
    
    parquet_path = extract_to_parquet_optimized(
        DUCKDB_PATH,
        start_date_str,
        end_date_str,
        selected_symbols,
        force_refresh=force_refresh
    )
    
    log.info(f"✅ Data cached to: {parquet_path}")
    return parquet_path

def ingest_bundle_from_cache():
    """CLI function to ingest bundle from cache"""
    log.info("📦 INGESTING BUNDLE FROM CACHE")
    
    from zipline.data.bundles import ingest
    ingest('clean-nse-bundle', show_progress=True)
    log.info("✅ Bundle ingestion completed!")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Clean DuckDB to Zipline Bundle Pipeline')
    parser.add_argument('action', choices=['extract', 'ingest', 'both'],
                       help='Action: extract (to parquet), ingest (bundle), or both')
    parser.add_argument('--force-refresh', action='store_true',
                       help='Force refresh cached data')
    parser.add_argument('--config', action='store_true',
                       help='Show configuration')
    
    args = parser.parse_args()
    
    if args.config:
        log.info("📋 CONFIGURATION")
        log.info(f"Database: {DUCKDB_PATH}")
        log.info(f"Table: {TABLE_NAME}")
        log.info(f"Cache dir: {CACHE_DIR}")
        log.info(f"Custom date range: {USE_CUSTOM_DATE_RANGE}")
        if USE_CUSTOM_DATE_RANGE:
            log.info(f"Date range: {CUSTOM_START_DATE} to {CUSTOM_END_DATE}")
        log.info(f"Limit stocks: {LIMIT_STOCKS}")
        if LIMIT_STOCKS:
            log.info(f"Max stocks: {MAX_STOCKS}, Last months: {LAST_N_MONTHS}")
        return
    
    try:
        if args.action in ['extract', 'both']:
            extract_data_to_cache(force_refresh=args.force_refresh)
        
        if args.action in ['ingest', 'both']:
            ingest_bundle_from_cache()
        
        log.info("🎉 Pipeline completed successfully!")
        
    except Exception as e:
        log.error(f"❌ Pipeline failed: {str(e)}")
        log.error(traceback.format_exc())
        return 1
    
    return 0

# Register the bundle
log.info("🔄 Registering clean NSE bundle with XBOM calendar")

register(
    'clean-nse-bundle',
    clean_duckdb_bundle,
    calendar_name='XBOM',
    minutes_per_day=375,  # 9:15 AM to 3:30 PM (375 minutes)
    create_writers=True
)

if __name__ == "__main__":
    sys.exit(main())
