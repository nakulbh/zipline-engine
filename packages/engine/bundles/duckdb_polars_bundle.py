import os
import sys
import gc
import pandas as pd
import polars as pl
import duckdb
import logging
import pytz
from datetime import datetime, timedelta
from pathlib import Path
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

# DuckDB database path - Update this to your actual database path
DUCKDB_PATH = "/media/nakulbh/PickleRick/nifty500_5year_data.duckdb"

# Configuration for full 5-year dataset ingestion
LIMIT_STOCKS = False  # Set to False to ingest all stocks
MAX_STOCKS = 100  # Maximum number of stocks to ingest (not used when LIMIT_STOCKS=False)
LAST_N_MONTHS = 12  # Last N months of data (not used when LIMIT_STOCKS=False)

# Custom date range configuration (Full 5-year range based on database)
USE_CUSTOM_DATE_RANGE = True  # Set to True to use the full database range
CUSTOM_START_DATE = "2020-07-20"  # Start date from database
CUSTOM_END_DATE = "2025-07-18"    # End date from database

# Parquet cache configuration
CACHE_DIR = Path(".augment/cache/parquet_data")  # Cache directory for Parquet files
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # Create cache directory if it doesn't exist
FORCE_REFRESH = False # Set to True to force refresh cached data

def extract_to_parquet(db_path, start_date=None, end_date=None, symbols=None, force_refresh=False):
    """
    Extract data from DuckDB to compressed Parquet files using Polars

    Parameters:
    -----------
    db_path : str
        Path to the DuckDB database file
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date in 'YYYY-MM-DD' format
    symbols : list, optional
        List of symbols to extract
    force_refresh : bool
        Force refresh cached data

    Returns:
    --------
    str
        Path to the cached Parquet file
    """

    # Create cache filename based on parameters
    cache_params = f"{start_date}_{end_date}_{len(symbols) if symbols else 'all'}"
    cache_file = CACHE_DIR / f"market_data_{cache_params}.parquet"

    # Check if cached file exists and is recent (unless force refresh)
    if cache_file.exists() and not force_refresh:
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age.days < 1:  # Cache valid for 1 day
            log.info(f"📁 Using cached Parquet file: {cache_file}")
            log.info(f"   Cache age: {file_age}")
            return str(cache_file)

    log.info(f"🔄 Extracting data to Parquet: {cache_file}")

    try:
        # Connect to DuckDB
        conn = duckdb.connect(db_path)

        # Configure DuckDB for memory efficiency with conservative settings for 50M records
        conn.execute("SET memory_limit='4GB'")  # Conservative memory limit
        conn.execute("SET threads=1")  # Single thread to minimize memory usage
        conn.execute("SET preserve_insertion_order=false")  # Disable order preservation
        conn.execute("PRAGMA max_temp_directory_size='15GB'")  # Large temp directory for sorting

        # First, get total record count to decide on chunking strategy
        count_query = "SELECT COUNT(*) as total_records FROM nifty500_minute_data"
        conditions = []
        if start_date:
            conditions.append(f"DATE(timestamp) >= '{start_date}'")
        if end_date:
            conditions.append(f"DATE(timestamp) <= '{end_date}'")
        if symbols:
            symbol_list = "', '".join(symbols)
            conditions.append(f"symbol IN ('{symbol_list}')")

        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)

        total_records = conn.execute(count_query).fetchone()[0]
        log.info(f"📊 Total records to extract: {total_records:,}")

        # Determine extraction strategy based on dataset size
        CHUNK_THRESHOLD = 5_000_000  # 5M records threshold for chunking
        ULTRA_LARGE_THRESHOLD = 30_000_000  # 30M records threshold for ultra-large processing

        if total_records > ULTRA_LARGE_THRESHOLD:
            log.info(f"🚀 Ultra-large dataset detected ({total_records:,} records). Using symbol-by-symbol processing...")
            return _extract_ultra_large_dataset_by_symbol(conn, start_date, end_date, symbols, cache_file, total_records)
        elif total_records > CHUNK_THRESHOLD:
            log.info(f"🔄 Large dataset detected ({total_records:,} records). Using chunked extraction...")
            return _extract_large_dataset_chunked(conn, start_date, end_date, symbols, cache_file, total_records)
        else:
            log.info(f"📊 Small dataset ({total_records:,} records). Using direct extraction...")
            return _extract_small_dataset_direct(conn, start_date, end_date, symbols, cache_file)

    except Exception as e:
        log.error(f"❌ Failed to extract to Parquet: {str(e)}")
        raise

def _extract_small_dataset_direct(conn, start_date, end_date, symbols, cache_file):
    """Extract small datasets directly without chunking"""
    # Build query
    query = """
    SELECT
        symbol,
        timestamp,
        open,
        high,
        low,
        close,
        volume
    FROM nifty500_minute_data
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
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY symbol, timestamp"

    log.info(f"📊 Executing direct extraction query...")

    # Execute query and get result as Polars DataFrame directly
    result = conn.execute(query).pl()

    log.info(f"✅ Extracted {len(result):,} records for {result['symbol'].n_unique()} symbols")

    # Write to compressed Parquet
    log.info(f"💾 Writing to compressed Parquet...")
    result.write_parquet(
        cache_file,
        compression="zstd",  # High compression
        compression_level=3,  # Good balance of speed vs compression
        use_pyarrow=True
    )

    # Get file size
    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
    log.info(f"✅ Parquet file created: {file_size_mb:.1f} MB")

    conn.close()
    return str(cache_file)

def _extract_large_dataset_chunked(conn, start_date, end_date, symbols, cache_file, total_records):
    """Extract large datasets using chunked processing to avoid memory issues"""
    import polars as pl
    import time

    # Calculate chunk size based on available memory (very conservative for 50M records)
    chunk_size = min(100_000, max(25_000, total_records // 200))  # Even smaller chunks for stability
    total_chunks = (total_records + chunk_size - 1) // chunk_size  # Calculate total chunks
    log.info(f"🔄 Using chunk size: {chunk_size:,} records")
    log.info(f"📊 Estimated total chunks: {total_chunks:,}")
    log.info(f"⏱️  Estimated processing time: {total_chunks * 2:.0f}-{total_chunks * 5:.0f} seconds")

    # Build base query
    base_query = """
    SELECT
        symbol,
        timestamp,
        open,
        high,
        low,
        close,
        volume
    FROM nifty500_minute_data
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

    # Process data in chunks and write to Parquet incrementally
    all_chunks = []
    offset = 0
    chunk_num = 0

    start_time = time.time()
    last_log_time = start_time

    while offset < total_records:
        chunk_start_time = time.time()
        chunk_query = f"{base_query} LIMIT {chunk_size} OFFSET {offset}"
        progress_pct = (chunk_num / total_chunks) * 100
        elapsed_time = time.time() - start_time

        log.info(f"📊 Starting chunk {chunk_num + 1}/{total_chunks} ({progress_pct:.1f}%), records {offset:,} to {min(offset + chunk_size, total_records):,}")
        log.info(f"⏱️  Elapsed time: {elapsed_time:.1f}s, ETA: {(elapsed_time / max(chunk_num, 1)) * (total_chunks - chunk_num):.1f}s")

        try:
            # Log query execution start
            log.info(f"🔍 Executing DuckDB query for chunk {chunk_num + 1}...")
            query_start = time.time()

            # Execute query and convert to Polars DataFrame
            chunk_result = conn.execute(chunk_query).pl()

            query_time = time.time() - query_start
            log.info(f"✅ Query completed in {query_time:.2f}s, got {len(chunk_result):,} records")

            if len(chunk_result) == 0:
                log.info("📋 No more data to process, breaking...")
                break

            # Log memory usage before adding chunk
            log.info(f"📊 Adding chunk to memory (current chunks in memory: {len(all_chunks)})")
            all_chunks.append(chunk_result)

            chunk_time = time.time() - chunk_start_time
            log.info(f"✅ Chunk {chunk_num + 1} completed in {chunk_time:.2f}s")

            offset += chunk_size
            chunk_num += 1

            # Memory management: combine chunks more frequently for very large datasets
            if len(all_chunks) >= 2:  # Combine every 2 chunks (very aggressive for 50M records)
                combine_start = time.time()
                log.info(f"🔄 Combining {len(all_chunks)} chunks to manage memory...")

                combined = pl.concat(all_chunks)
                all_chunks = [combined]

                # Force garbage collection for large datasets
                import gc
                gc.collect()

                combine_time = time.time() - combine_start
                log.info(f"🧹 Memory cleanup completed in {combine_time:.2f}s")

            # Log progress every 10 chunks or every 60 seconds
            current_time = time.time()
            if chunk_num % 10 == 0 or (current_time - last_log_time) > 60:
                records_processed = chunk_num * chunk_size
                processing_rate = records_processed / elapsed_time if elapsed_time > 0 else 0
                log.info(f"📈 Progress: {records_processed:,}/{total_records:,} records ({processing_rate:.0f} records/sec)")
                last_log_time = current_time

        except Exception as e:
            log.error(f"❌ Error processing chunk {chunk_num + 1}: {str(e)}")
            log.error(f"🔍 Query was: {chunk_query[:200]}...")
            raise

    # Combine all chunks
    total_time = time.time() - start_time
    log.info(f"🔄 All chunks processed in {total_time:.1f}s. Combining {len(all_chunks)} chunk groups...")

    combine_start = time.time()
    final_result = pl.concat(all_chunks) if len(all_chunks) > 1 else all_chunks[0]
    combine_time = time.time() - combine_start

    log.info(f"✅ Combined {len(final_result):,} records for {final_result['symbol'].n_unique()} symbols in {combine_time:.2f}s")

    # Write to compressed Parquet
    log.info(f"💾 Writing to compressed Parquet...")
    write_start = time.time()

    final_result.write_parquet(
        cache_file,
        compression="zstd",  # High compression
        compression_level=3,  # Good balance of speed vs compression
        use_pyarrow=True
    )

    write_time = time.time() - write_start
    log.info(f"💾 Parquet write completed in {write_time:.2f}s")

    # Get file size
    file_size_mb = cache_file.stat().st_size / (1024 * 1024)
    total_pipeline_time = time.time() - start_time
    log.info(f"✅ Parquet file created: {file_size_mb:.1f} MB")
    log.info(f"🎉 Total extraction time: {total_pipeline_time:.1f}s ({len(final_result)/total_pipeline_time:.0f} records/sec)")

    conn.close()
    return str(cache_file)

def _extract_ultra_large_dataset_native(conn, start_date, end_date, symbols, cache_file, total_records):
    """Extract ultra-large datasets using DuckDB's native COPY TO PARQUET functionality"""
    import time

    log.info(f"🚀 Using DuckDB native export for {total_records:,} records")
    log.info(f"📁 Output file: {cache_file}")

    start_time = time.time()

    try:
        # Build the query
        query = """
        SELECT
            symbol,
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM nifty500_minute_data
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
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY symbol, timestamp"

        # Use DuckDB's native COPY TO for efficient export (without ORDER BY for large datasets)
        # Remove ORDER BY to avoid memory issues with 50M records
        query_no_order = query.replace(" ORDER BY symbol, timestamp", "")

        copy_query = f"""
        COPY ({query_no_order}) TO '{cache_file}'
        (FORMAT PARQUET, COMPRESSION 'ZSTD', COMPRESSION_LEVEL 1)
        """

        log.info(f"🔄 Executing native DuckDB export (without ordering for performance)...")
        log.info(f"📝 Query: COPY (...) TO '{cache_file.name}' (FORMAT PARQUET, COMPRESSION 'ZSTD')")
        log.info(f"⚠️  Note: Data will not be sorted by symbol/timestamp for performance reasons")

        # Add a timeout mechanism
        import signal
        import threading

        def timeout_handler():
            log.error("⏰ Export timeout after 300 seconds, falling back to chunked processing...")
            raise TimeoutError("DuckDB export timeout")

        # Set up timeout
        timer = threading.Timer(300.0, timeout_handler)  # 5 minute timeout
        timer.start()

        try:
            # Execute the export
            log.info(f"⏱️  Starting export with 5-minute timeout...")
            conn.execute(copy_query)
            timer.cancel()  # Cancel timeout if successful
        except Exception as e:
            timer.cancel()
            raise e

        export_time = time.time() - start_time

        # Get file size
        file_size_mb = cache_file.stat().st_size / (1024 * 1024)
        records_per_sec = total_records / export_time if export_time > 0 else 0

        log.info(f"✅ Native export completed in {export_time:.1f}s")
        log.info(f"📏 File size: {file_size_mb:.1f} MB")
        log.info(f"⚡ Processing rate: {records_per_sec:,.0f} records/sec")

        conn.close()
        return str(cache_file)

    except Exception as e:
        log.error(f"❌ Native export failed: {str(e)}")
        log.info(f"🔄 Falling back to chunked processing...")
        # Fall back to chunked processing
        return _extract_large_dataset_chunked(conn, start_date, end_date, symbols, cache_file, total_records)

def _extract_ultra_large_dataset_by_symbol(conn, start_date, end_date, symbols, cache_file, total_records):
    """Extract ultra-large datasets by processing one symbol at a time"""
    import polars as pl
    import time
    import tempfile
    import shutil
    from pathlib import Path

    log.info(f"🔄 Processing {total_records:,} records symbol by symbol")
    start_time = time.time()

    # Create temporary directory for symbol files
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_symbols_"))
    log.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        # First, get all unique symbols
        symbol_query = "SELECT DISTINCT symbol FROM nifty500_minute_data"
        conditions = []
        if start_date:
            conditions.append(f"DATE(timestamp) >= '{start_date}'")
        if end_date:
            conditions.append(f"DATE(timestamp) <= '{end_date}'")
        if symbols:
            symbol_list = "', '".join(symbols)
            conditions.append(f"symbol IN ('{symbol_list}')")

        if conditions:
            symbol_query += " WHERE " + " AND ".join(conditions)

        symbol_query += " ORDER BY symbol"

        log.info(f"🔍 Getting list of symbols...")
        all_symbols = conn.execute(symbol_query).fetchall()
        all_symbols = [row[0] for row in all_symbols]

        log.info(f"📊 Found {len(all_symbols)} symbols to process")

        # Process each symbol separately
        symbol_files = []
        processed_symbols = 0

        for i, symbol in enumerate(all_symbols):
            symbol_start_time = time.time()
            progress_pct = (i / len(all_symbols)) * 100

            log.info(f"📊 Processing symbol {i+1}/{len(all_symbols)} ({progress_pct:.1f}%): {symbol}")

            # Query for this symbol only
            symbol_query = f"""
            SELECT
                symbol,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM nifty500_minute_data
            WHERE symbol = '{symbol}'
            """

            if start_date:
                symbol_query += f" AND DATE(timestamp) >= '{start_date}'"
            if end_date:
                symbol_query += f" AND DATE(timestamp) <= '{end_date}'"

            symbol_query += " ORDER BY timestamp"

            try:
                # Execute query for this symbol
                symbol_data = conn.execute(symbol_query).pl()

                if len(symbol_data) > 0:
                    # Write symbol data to temporary file
                    symbol_file = temp_dir / f"symbol_{i:04d}_{symbol.replace(' ', '_').replace('/', '_')}.parquet"
                    symbol_data.write_parquet(
                        symbol_file,
                        compression="zstd",
                        compression_level=1,
                        use_pyarrow=True
                    )

                    symbol_files.append(symbol_file)
                    processed_symbols += 1

                    symbol_time = time.time() - symbol_start_time
                    log.info(f"✅ {symbol}: {len(symbol_data):,} records in {symbol_time:.2f}s")
                else:
                    log.warning(f"⚠️  {symbol}: No data found")

            except Exception as e:
                log.error(f"❌ Error processing {symbol}: {str(e)}")
                continue

            # Log progress every 10 symbols
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                avg_time_per_symbol = elapsed / (i + 1)
                eta = avg_time_per_symbol * (len(all_symbols) - i - 1)
                log.info(f"📈 Progress: {i+1}/{len(all_symbols)} symbols, ETA: {eta:.0f}s")

        log.info(f"✅ Processed {processed_symbols} symbols, combining into final file...")

        # Combine all symbol files
        if symbol_files:
            log.info(f"🔄 Reading and combining {len(symbol_files)} symbol files...")

            # Read files in batches to manage memory
            batch_size = 20  # Process 20 symbol files at a time
            all_data = []

            for i in range(0, len(symbol_files), batch_size):
                batch_files = symbol_files[i:i + batch_size]
                log.info(f"📊 Processing batch {i//batch_size + 1}/{(len(symbol_files) + batch_size - 1)//batch_size}")

                batch_data = []
                for symbol_file in batch_files:
                    data = pl.read_parquet(symbol_file)
                    batch_data.append(data)

                # Combine this batch
                if batch_data:
                    batch_combined = pl.concat(batch_data)
                    all_data.append(batch_combined)

                # Clean up batch files
                for symbol_file in batch_files:
                    symbol_file.unlink()

                # Force garbage collection
                import gc
                gc.collect()

            # Final combination
            log.info(f"🔄 Final combination of {len(all_data)} batches...")
            final_result = pl.concat(all_data)

            log.info(f"✅ Combined {len(final_result):,} records for {final_result['symbol'].n_unique()} symbols")

            # Write final file
            log.info(f"💾 Writing final compressed Parquet...")
            final_result.write_parquet(
                cache_file,
                compression="zstd",
                compression_level=3,
                use_pyarrow=True
            )

            # Get file size and stats
            file_size_mb = cache_file.stat().st_size / (1024 * 1024)
            total_time = time.time() - start_time

            log.info(f"✅ Final file created: {file_size_mb:.1f} MB")
            log.info(f"🎉 Symbol-by-symbol processing completed in {total_time:.1f}s")
            log.info(f"⚡ Average: {len(final_result)/total_time:.0f} records/sec")

            return str(cache_file)
        else:
            raise ValueError("No symbol files were created")

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            log.info(f"🧹 Cleaned up temporary directory")

        conn.close()

def _extract_ultra_large_dataset_batched(conn, start_date, end_date, symbols, cache_file, total_records):
    """Extract ultra-large datasets (50M+ records) using batched file processing"""
    import polars as pl
    import tempfile
    import shutil
    from pathlib import Path

    # Create temporary directory for batch files
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_batch_"))
    log.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        # Very small batch size for ultra-large datasets
        batch_size = 100_000  # 100K records per batch file
        total_batches = (total_records + batch_size - 1) // batch_size
        log.info(f"🔄 Processing {total_records:,} records in {total_batches:,} batches of {batch_size:,} records each")

        # Build base query
        base_query = """
        SELECT
            symbol,
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM nifty500_minute_data
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

        # Process data in small batches and write temporary Parquet files
        batch_files = []
        offset = 0
        batch_num = 0

        while offset < total_records:
            batch_query = f"{base_query} LIMIT {batch_size} OFFSET {offset}"
            progress_pct = (batch_num / total_batches) * 100
            log.info(f"📊 Processing batch {batch_num + 1}/{total_batches} ({progress_pct:.1f}%), records {offset:,} to {min(offset + batch_size, total_records):,}")

            try:
                # Execute query and convert to Polars DataFrame
                batch_result = conn.execute(batch_query).pl()

                if len(batch_result) == 0:
                    log.info("📋 No more data to process, breaking...")
                    break

                # Write batch to temporary Parquet file
                batch_file = temp_dir / f"batch_{batch_num:06d}.parquet"
                batch_result.write_parquet(
                    batch_file,
                    compression="zstd",
                    compression_level=1,  # Fast compression for temp files
                    use_pyarrow=True
                )

                batch_files.append(batch_file)
                log.info(f"✅ Wrote batch {batch_num + 1} with {len(batch_result):,} records to temp file")

                offset += batch_size
                batch_num += 1

                # Force garbage collection after each batch
                import gc
                gc.collect()

            except Exception as e:
                log.error(f"❌ Error processing batch {batch_num + 1}: {str(e)}")
                raise

        # Combine all batch files into final Parquet file
        log.info(f"🔄 Combining {len(batch_files)} batch files into final Parquet...")

        # Read and combine batch files in groups to manage memory
        final_chunks = []
        batch_group_size = 10  # Process 10 batch files at a time

        for i in range(0, len(batch_files), batch_group_size):
            group_files = batch_files[i:i + batch_group_size]
            log.info(f"📊 Combining batch group {i//batch_group_size + 1}/{(len(batch_files) + batch_group_size - 1)//batch_group_size}")

            group_chunks = []
            for batch_file in group_files:
                chunk = pl.read_parquet(batch_file)
                group_chunks.append(chunk)

            # Combine this group
            group_combined = pl.concat(group_chunks)
            final_chunks.append(group_combined)

            # Clean up batch files as we go
            for batch_file in group_files:
                batch_file.unlink()

            # Force garbage collection
            import gc
            gc.collect()

        # Final combination
        log.info(f"🔄 Final combination of {len(final_chunks)} chunk groups...")
        final_result = pl.concat(final_chunks)

        log.info(f"✅ Combined {len(final_result):,} records for {final_result['symbol'].n_unique()} symbols")

        # Write final compressed Parquet
        log.info(f"💾 Writing final compressed Parquet...")
        final_result.write_parquet(
            cache_file,
            compression="zstd",  # High compression for final file
            compression_level=3,
            use_pyarrow=True
        )

        # Get file size
        file_size_mb = cache_file.stat().st_size / (1024 * 1024)
        log.info(f"✅ Final Parquet file created: {file_size_mb:.1f} MB")

        return str(cache_file)

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            log.info(f"🧹 Cleaned up temporary directory")

        conn.close()

def load_from_parquet(parquet_path):
    """
    Load data from cached Parquet file using Polars

    Parameters:
    -----------
    parquet_path : str
        Path to the Parquet file

    Returns:
    --------
    pl.DataFrame
        Loaded data
    """
    try:
        log.info(f"📁 Loading data from Parquet: {parquet_path}")

        # Load with Polars (very fast)
        df = pl.read_parquet(parquet_path)

        log.info(f"✅ Loaded {len(df):,} records for {df['symbol'].n_unique()} symbols")
        log.info(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

        return df

    except Exception as e:
        log.error(f"❌ Failed to load from Parquet: {str(e)}")
        raise

def get_top_liquid_stocks(db_path, limit=50, months_back=12, include_specific=None):
    """
    Get top liquid stocks based on average volume over the last N months

    Parameters:
    -----------
    db_path : str
        Path to the DuckDB database file
    limit : int
        Number of top stocks to return
    months_back : int
        Number of months to look back for volume calculation
    include_specific : list, optional
        List of specific symbols to always include

    Returns:
    --------
    list
        List of top liquid stock symbols
    """
    try:
        # Initialize specific symbols to include
        specific_symbols = []
        if include_specific:
            specific_symbols = include_specific
            log.info(f"Will include specific symbols: {specific_symbols}")

        # Always include AMARA RAJA ENERGY MOB LTD
        if "AMARA RAJA ENERGY MOB LTD" not in specific_symbols:
            specific_symbols.append("AMARA RAJA ENERGY MOB LTD")
            log.info(f"Added AMARA RAJA ENERGY MOB LTD to included symbols")

        conn = duckdb.connect(db_path)

        # Configure DuckDB for low memory usage
        conn.execute("SET memory_limit='2GB'")
        conn.execute("SET threads=2")

        # Calculate date range for liquidity analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)

        # Query to get top liquid stocks by average volume
        liquidity_query = f"""
        SELECT
            symbol,
            AVG(volume) as avg_volume,
            COUNT(*) as data_points,
            MIN(timestamp) as first_date,
            MAX(timestamp) as last_date
        FROM nifty500_minute_data
        WHERE DATE(timestamp) >= '{start_date.strftime('%Y-%m-%d')}'
        AND DATE(timestamp) <= '{end_date.strftime('%Y-%m-%d')}'
        AND volume > 0
        GROUP BY symbol
        HAVING COUNT(*) > 1000  -- Ensure sufficient data points
        ORDER BY avg_volume DESC
        LIMIT {limit}
        """

        result = conn.execute(liquidity_query).fetchall()

        # Also get data for specific symbols if they exist
        if specific_symbols:
            specific_symbols_str = "', '".join(specific_symbols)
            specific_query = f"""
            SELECT
                symbol,
                AVG(volume) as avg_volume,
                COUNT(*) as data_points,
                MIN(timestamp) as first_date,
                MAX(timestamp) as last_date
            FROM nifty500_minute_data
            WHERE symbol IN ('{specific_symbols_str}')
            GROUP BY symbol
            """

            specific_result = conn.execute(specific_query).fetchall()
            log.info(f"Found {len(specific_result)} specific symbols in database")

            # Add specific symbols to result
            specific_symbols_found = [row[0] for row in specific_result]
            for symbol in specific_symbols_found:
                log.info(f"✅ Found specific symbol in database: {symbol}")
        else:
            specific_result = []

        conn.close()

        if not result and not specific_result:
            log.warning("No liquid stocks found, using fallback list")
            # Fallback to common liquid stocks
            return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
                   'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK']

        # Combine results, prioritizing specific symbols
        all_results = specific_result + result
        symbols = []
        seen = set()

        for row in all_results:
            symbol = row[0]
            if symbol not in seen:
                symbols.append(symbol)
                seen.add(symbol)

        # Limit to requested number (but always include specific symbols)
        if len(symbols) > limit and not specific_symbols:
            symbols = symbols[:limit]

        log.info(f"Selected {len(symbols)} stocks: {symbols[:10]}...")

        return symbols

    except Exception as e:
        log.error(f"Error getting liquid stocks: {str(e)}")
        # Return fallback list
        return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR']

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
    Process Polars DataFrame for Zipline ingestion with chunked processing for large datasets

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
    log.info(f"📊 Processing {len(df):,} records...")

    # Clean symbol names first (this is fast)
    df = df.with_columns([
        pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
    ])

    # For very large datasets, use a much simpler approach
    if len(df) > 30_000_000:  # 30M+ records - use ultra-simple processing
        log.info("🔄 Ultra-large dataset detected, using minimal memory processing...")
        return _process_ultra_large_dataset_simple(df)
    elif len(df) > 10_000_000:  # 10M+ records
        log.info("🔄 Large dataset detected, using streaming processing...")
        return _process_large_dataset_streaming(df)
    else:
        log.info("📊 Small dataset, using direct processing...")
        return _process_small_dataset_direct(df)

def _process_small_dataset_direct(df):
    """Process small datasets directly"""
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

    return _finalize_processing(df)

def _process_large_dataset_streaming(df):
    """Process large datasets using streaming approach - no memory accumulation"""
    import time
    import tempfile
    import shutil
    from pathlib import Path

    log.info(f"🚀 Starting streaming processing for {len(df):,} records")
    log.info(f"💾 Using ultra-low memory streaming approach")

    # Create temporary directory for final result
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_streaming_"))
    log.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        # Process data in very small chunks and write immediately
        chunk_size = 100_000  # Very small chunks (100K records)
        total_records = len(df)
        total_chunks = (total_records + chunk_size - 1) // chunk_size

        log.info(f"🔄 Processing {total_records:,} records in {total_chunks} chunks of {chunk_size:,} records each")

        # Create final output file path
        final_processed_file = temp_dir / "final_processed.parquet"

        start_time = time.time()
        processed_records = 0

        # Process first chunk to establish schema
        log.info(f"📊 Processing initial chunk to establish schema...")
        first_chunk = df.slice(0, chunk_size)

        # Process first chunk
        first_chunk_pd = first_chunk.to_pandas()
        if first_chunk_pd['timestamp'].dt.tz is None:
            first_chunk_pd['datetime'] = pd.to_datetime(first_chunk_pd['timestamp']).dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')
        else:
            first_chunk_pd['datetime'] = pd.to_datetime(first_chunk_pd['timestamp']).dt.tz_convert('UTC')

        first_chunk_pl = pl.from_pandas(first_chunk_pd)

        # Apply basic processing
        first_chunk_pl = first_chunk_pl.with_columns([
            pl.col("datetime").dt.round("1m")
        ]).filter(
            (pl.col("open") > 0) &
            (pl.col("high") > 0) &
            (pl.col("low") > 0) &
            (pl.col("close") > 0) &
            (pl.col("volume") >= 0)
        )

        # Write first chunk to establish the file
        first_chunk_pl.write_parquet(
            final_processed_file,
            compression="zstd",
            compression_level=1,
            use_pyarrow=True
        )

        processed_records += len(first_chunk_pl)
        log.info(f"✅ Initial chunk processed: {len(first_chunk_pl):,} records")

        # Process remaining chunks and append
        for i in range(chunk_size, total_records, chunk_size):
            chunk_start_time = time.time()
            chunk_num = i // chunk_size + 1
            end_idx = min(i + chunk_size, total_records)

            if chunk_num % 10 == 0:  # Log every 10 chunks
                progress_pct = (i / total_records) * 100
                elapsed = time.time() - start_time
                rate = processed_records / elapsed if elapsed > 0 else 0
                log.info(f"📊 Processing chunk {chunk_num}/{total_chunks} ({progress_pct:.1f}%), rate: {rate:.0f} records/sec")

            # Get chunk
            chunk = df.slice(i, chunk_size)

            # Process chunk
            chunk_pd = chunk.to_pandas()
            if chunk_pd['timestamp'].dt.tz is None:
                chunk_pd['datetime'] = pd.to_datetime(chunk_pd['timestamp']).dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')
            else:
                chunk_pd['datetime'] = pd.to_datetime(chunk_pd['timestamp']).dt.tz_convert('UTC')

            chunk_pl = pl.from_pandas(chunk_pd)

            # Apply basic processing
            chunk_pl = chunk_pl.with_columns([
                pl.col("datetime").dt.round("1m")
            ]).filter(
                (pl.col("open") > 0) &
                (pl.col("high") > 0) &
                (pl.col("low") > 0) &
                (pl.col("close") > 0) &
                (pl.col("volume") >= 0)
            )

            # Append to existing file (this is memory efficient)
            existing_data = pl.read_parquet(final_processed_file)
            combined_data = pl.concat([existing_data, chunk_pl])
            combined_data.write_parquet(
                final_processed_file,
                compression="zstd",
                compression_level=1,
                use_pyarrow=True
            )

            processed_records += len(chunk_pl)

            # Force garbage collection after each chunk
            import gc
            gc.collect()

        # Read final processed data
        log.info(f"📁 Reading final processed data...")
        final_df = pl.read_parquet(final_processed_file)

        total_time = time.time() - start_time
        log.info(f"✅ Streaming processing completed in {total_time:.1f}s")
        log.info(f"📊 Processed {processed_records:,} records ({processed_records/total_time:.0f} records/sec)")

        # Create asset metadata
        log.info(f"📊 Creating asset metadata...")
        asset_metadata = final_df.group_by("clean_symbol").agg([
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

        # Convert to pandas in small chunks
        log.info(f"🔄 Converting to pandas for Zipline...")
        processed_data = final_df.select([
            "clean_symbol",
            "symbol",
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]).to_pandas()

        asset_metadata_pd = asset_metadata.to_pandas()

        log.info(f"✅ Final result: {len(processed_data)} records for {len(asset_metadata_pd)} assets")

        return processed_data, asset_metadata_pd

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            log.info(f"🧹 Cleaned up temporary directory")

def _process_ultra_large_dataset_simple(df):
    """Process ultra-large datasets with chunked processing to avoid memory issues"""
    import time
    import tempfile
    import shutil
    from pathlib import Path

    log.info(f"🚀 Chunked processing for {len(df):,} records")
    log.info(f"💾 Using disk-based chunked approach to avoid memory issues")

    start_time = time.time()

    # Create temporary directory for processed chunks
    temp_dir = Path(tempfile.mkdtemp(prefix="zipline_ultra_"))
    log.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        # Process data in very small chunks
        chunk_size = 1_000_000  # 1M records per chunk
        total_records = len(df)
        total_chunks = (total_records + chunk_size - 1) // chunk_size

        log.info(f"🔄 Processing {total_records:,} records in {total_chunks} chunks of {chunk_size:,} each")

        processed_chunk_files = []

        for i in range(0, total_records, chunk_size):
            chunk_start_time = time.time()
            chunk_num = i // chunk_size + 1
            end_idx = min(i + chunk_size, total_records)

            log.info(f"📊 Processing chunk {chunk_num}/{total_chunks}, records {i:,} to {end_idx:,}")

            # Get chunk
            chunk = df.slice(i, chunk_size)

            # Process this chunk
            log.info(f"🔄 Chunk {chunk_num}: Adding clean symbol column...")
            chunk = chunk.with_columns([
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
            ])

            log.info(f"🔄 Chunk {chunk_num}: Converting timestamps...")
            try:
                chunk = chunk.with_columns([
                    pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            except:
                chunk = chunk.with_columns([
                    pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])

            log.info(f"🔄 Chunk {chunk_num}: Rounding timestamps...")
            chunk = chunk.with_columns([
                pl.col("datetime").dt.round("1m")
            ])

            log.info(f"🔄 Chunk {chunk_num}: Filtering invalid data...")
            chunk = chunk.filter(
                (pl.col("open") > 0) &
                (pl.col("high") > 0) &
                (pl.col("low") > 0) &
                (pl.col("close") > 0) &
                (pl.col("volume") >= 0)
            )

            # Write processed chunk to disk
            chunk_file = temp_dir / f"processed_chunk_{chunk_num:04d}.parquet"
            chunk.write_parquet(
                chunk_file,
                compression="zstd",
                compression_level=1,
                use_pyarrow=True
            )
            processed_chunk_files.append(chunk_file)

            chunk_time = time.time() - chunk_start_time
            log.info(f"✅ Chunk {chunk_num} processed: {len(chunk):,} records in {chunk_time:.2f}s")

            # Force garbage collection
            import gc
            gc.collect()

        # Combine processed chunks
        log.info(f"🔄 Combining {len(processed_chunk_files)} processed chunks...")

        # Read and combine in batches
        batch_size = 5  # Process 5 chunk files at a time
        final_chunks = []

        for i in range(0, len(processed_chunk_files), batch_size):
            batch_files = processed_chunk_files[i:i + batch_size]
            log.info(f"📊 Loading batch {i//batch_size + 1}/{(len(processed_chunk_files) + batch_size - 1)//batch_size}")

            batch_data = []
            for chunk_file in batch_files:
                data = pl.read_parquet(chunk_file)
                batch_data.append(data)

            # Combine this batch
            if batch_data:
                batch_combined = pl.concat(batch_data)
                final_chunks.append(batch_combined)

            # Clean up batch files
            for chunk_file in batch_files:
                chunk_file.unlink()

            gc.collect()

        # Final combination
        log.info(f"🔄 Final combination of {len(final_chunks)} batches...")
        df = pl.concat(final_chunks)

        log.info(f"✅ Chunked processing completed: {len(df):,} records")

        return _create_metadata_and_finalize(df, start_time)

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            log.info(f"🧹 Cleaned up temporary directory")

def _create_metadata_and_finalize(df, start_time):
    """Create metadata and finalize processing with chunked metadata creation"""
    import time

    log.info(f"🔄 Creating asset metadata (chunked approach)...")
    metadata_start = time.time()

    # Get unique symbols first (this is fast even for large datasets)
    log.info(f"📊 Getting unique symbols...")
    unique_symbols = df.select("clean_symbol", "symbol").unique().sort("clean_symbol")
    log.info(f"📊 Found {len(unique_symbols)} unique symbols")

    # Create metadata by processing symbols in small groups to avoid memory issues
    symbol_chunk_size = 10  # Process 10 symbols at a time
    total_symbols = len(unique_symbols)
    total_chunks = (total_symbols + symbol_chunk_size - 1) // symbol_chunk_size

    log.info(f"📊 Creating metadata in {total_chunks} chunks of {symbol_chunk_size} symbols each")

    metadata_chunks = []

    for i in range(0, total_symbols, symbol_chunk_size):
        chunk_start_time = time.time()
        chunk_symbols = unique_symbols.slice(i, symbol_chunk_size)
        chunk_num = i // symbol_chunk_size + 1

        log.info(f"📊 Processing metadata chunk {chunk_num}/{total_chunks}")

        # Get date ranges for this chunk of symbols
        symbol_list = chunk_symbols["clean_symbol"].to_list()

        # Filter data for these symbols only
        chunk_data = df.filter(pl.col("clean_symbol").is_in(symbol_list))

        # Create metadata for this chunk
        chunk_metadata = chunk_data.group_by("clean_symbol").agg([
            pl.col("symbol").first().alias("original_symbol"),
            pl.col("datetime").min().alias("start_date"),
            pl.col("datetime").max().alias("end_date")
        ])

        metadata_chunks.append(chunk_metadata)

        chunk_time = time.time() - chunk_start_time
        log.info(f"✅ Metadata chunk {chunk_num} completed in {chunk_time:.2f}s")

        # Force garbage collection every few chunks
        if chunk_num % 5 == 0:
            import gc
            gc.collect()

    # Combine all metadata chunks
    log.info(f"📊 Combining {len(metadata_chunks)} metadata chunks...")
    asset_metadata = pl.concat(metadata_chunks).sort("clean_symbol")

    log.info(f"📊 Adding metadata columns...")
    asset_metadata = asset_metadata.with_columns([
        pl.lit("NSE").alias("exchange"),
        pl.col("original_symbol").alias("asset_name"),
        pl.lit(None).alias("first_traded"),
        pl.lit(None).alias("auto_close_date"),
        pl.lit(1.0).alias("tick_size")
    ])

    metadata_time = time.time() - metadata_start
    log.info(f"✅ Created metadata for {len(asset_metadata)} assets (took {metadata_time:.2f}s)")

    # Convert metadata to pandas (small, so safe)
    log.info(f"📊 Converting metadata to pandas...")
    asset_metadata_pd = asset_metadata.to_pandas()

    total_time = time.time() - start_time
    log.info(f"✅ Ultra-chunked processing completed in {total_time:.1f}s")
    log.info(f"📊 Final result: {len(df)} records for {len(asset_metadata_pd)} assets")
    log.info(f"💡 Data will be converted to pandas incrementally during ingestion")

    return df, asset_metadata_pd

def _finalize_processing(df):
    """Finalize processing with common steps"""
    log.info(f"🔄 Finalizing processing for {len(df):,} records...")

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

    log.info(f"✅ After filtering: {len(df):,} valid records")

    # Create asset metadata with date ranges
    log.info(f"📊 Creating asset metadata...")
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

    log.info(f"✅ Created metadata for {len(asset_metadata)} assets")

    # Convert to pandas for Zipline compatibility (in chunks if large)
    if len(df) > 5_000_000:  # 5M+ records
        log.info(f"🔄 Converting large dataset to pandas in chunks...")
        chunk_size = 1_000_000
        pandas_chunks = []

        for i in range(0, len(df), chunk_size):
            chunk = df.slice(i, chunk_size)
            chunk_pd = chunk.select([
                "clean_symbol",
                "symbol",
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]).to_pandas()
            pandas_chunks.append(chunk_pd)

            if (i // chunk_size + 1) % 10 == 0:
                log.info(f"📊 Converted chunk {i // chunk_size + 1}/{(len(df) + chunk_size - 1) // chunk_size}")

        log.info(f"🔄 Combining pandas chunks...")
        processed_data = pd.concat(pandas_chunks, ignore_index=True)
    else:
        processed_data = df.select([
            "clean_symbol",
            "symbol",
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

def create_asset_metadata_from_parquet(parquet_path):
    """Create asset metadata by scanning Parquet file without loading all data"""
    import polars as pl

    log.info(f"📊 Creating asset metadata from Parquet file...")

    # Read only the columns we need for metadata (very memory efficient)
    metadata_df = pl.scan_parquet(parquet_path).select([
        "symbol",
        "timestamp"
    ]).collect()

    # Add clean symbol
    metadata_df = metadata_df.with_columns([
        pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
    ])

    # Convert timestamp to datetime
    try:
        metadata_df = metadata_df.with_columns([
            pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
        ])
    except:
        metadata_df = metadata_df.with_columns([
            pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
        ])

    # Create metadata
    asset_metadata = metadata_df.group_by("clean_symbol").agg([
        pl.col("symbol").first().alias("original_symbol"),
        pl.col("datetime").min().alias("start_date"),
        pl.col("datetime").max().alias("end_date")
    ]).sort("clean_symbol")

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
    """
    Memory-efficient streaming parser that reads Parquet data in chunks
    and yields (asset_id, pandas_dataframe) tuples for Zipline writers
    """
    import polars as pl
    import pytz

    log.info(f"🚀 Starting streaming data parsing from {parquet_path}")
    log.info(f"📊 Processing {len(symbol_map)} assets")

    # Process each symbol individually to minimize memory usage
    for asset_id, symbol in symbol_map.items():
        try:
            if asset_id % 10 == 0:  # Log every 10th asset
                log.info(f"📊 Streaming data for {symbol} (asset_id: {asset_id})")

            # Read only this symbol's data from Parquet (memory efficient)
            symbol_data = pl.scan_parquet(parquet_path).filter(
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8) == symbol
            ).collect()

            if len(symbol_data) == 0:
                log.warning(f"No data found for symbol {symbol}")
                continue

            # Process this symbol's data
            symbol_data = symbol_data.with_columns([
                pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8).alias("clean_symbol")
            ])

            # Convert timestamp
            try:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])
            except:
                symbol_data = symbol_data.with_columns([
                    pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                ])

            # Round timestamps and filter
            symbol_data = symbol_data.with_columns([
                pl.col("datetime").dt.round("1m")
            ]).filter(
                (pl.col("open") > 0) &
                (pl.col("high") > 0) &
                (pl.col("low") > 0) &
                (pl.col("close") > 0) &
                (pl.col("volume") >= 0)
            )

            # Filter to only include market hours (9:15 AM to 3:30 PM IST = 3:45 AM to 10:00 AM UTC)
            symbol_data = symbol_data.filter(
                (pl.col("datetime").dt.hour() >= 3) &
                (pl.col("datetime").dt.hour() < 10)
            )

            # Filter to only include weekdays (Monday=1 to Friday=5)
            symbol_data = symbol_data.filter(
                pl.col("datetime").dt.weekday().is_in([1, 2, 3, 4, 5])
            )

            if len(symbol_data) == 0:
                continue

            # Convert to pandas for Zipline (only this symbol's data)
            asset_data = symbol_data.select([
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]).to_pandas()

            # Set datetime as index
            asset_data = asset_data.set_index('datetime')

            # Ensure timezone is UTC
            if asset_data.index.tz is None:
                asset_data.index = asset_data.index.tz_localize('UTC')
            elif asset_data.index.tz != pytz.UTC:
                asset_data.index = asset_data.index.tz_convert('UTC')

            # Sort by datetime
            asset_data = asset_data.sort_index()

            # Ensure volume is integer
            asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)

            if len(asset_data) > 0:
                yield asset_id, asset_data

        except Exception as e:
            log.error(f"❌ Error processing symbol {symbol} (asset_id: {asset_id}): {str(e)}")
            continue

        # Force garbage collection after each symbol
        if asset_id % 20 == 0:  # GC every 20 symbols
            import gc
            gc.collect()

def parse_pricing_and_vol(data, sessions, symbol_map):
    """
    Parse pricing and volume data for Zipline ingestion - optimized for Polars input
    """
    import pytz

    # Check if data is Polars DataFrame
    if hasattr(data, 'to_pandas'):
        # Data is Polars - process efficiently
        log.info(f"Processing Polars DataFrame with {len(data):,} records")

        # Get unique symbols from Polars DataFrame
        available_symbols = set(data['clean_symbol'].unique().to_list())
        log.info(f"Processing {len(available_symbols)} symbols: {sorted(list(available_symbols))[:5]}...")

        for asset_id, symbol in symbol_map.items():
            try:
                # Check if symbol exists in the data
                if symbol not in available_symbols:
                    log.warning(f"No data found for symbol {symbol} (asset_id: {asset_id})")
                    continue

                # Filter data for this symbol using Polars (very fast)
                symbol_data_pl = data.filter(pl.col("clean_symbol") == symbol)

                if len(symbol_data_pl) == 0:
                    continue

                # Convert only this symbol's data to pandas (memory efficient)
                asset_data = symbol_data_pl.select([
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]).to_pandas()

                # Set datetime as index
                asset_data = asset_data.set_index('datetime')

                # Ensure the index is timezone-aware UTC for Zipline compatibility
                if asset_data.index.tz is None:
                    asset_data.index = asset_data.index.tz_localize('UTC')
                elif asset_data.index.tz != pytz.UTC:
                    asset_data.index = asset_data.index.tz_convert('UTC')

                # Sort by datetime
                asset_data = asset_data.sort_index()

                # Ensure volume is integer
                asset_data['volume'] = asset_data['volume'].fillna(0).astype(int)

                if len(asset_data) > 0:
                    yield asset_id, asset_data

            except Exception as e:
                log.error(f"Error processing symbol {symbol} (asset_id: {asset_id}): {str(e)}")
                continue
    else:
        # Data is already Pandas - use original logic
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

    log.info(f"🚀 Starting Parquet-cached NSE bundle ingestion")

    # Determine date range - prioritize custom date range, then limited mode, then environment/session
    if USE_CUSTOM_DATE_RANGE:
        # Use custom date range (2021-2024)
        start_date_str = CUSTOM_START_DATE
        end_date_str = CUSTOM_END_DATE
        log.info(f"🎯 Using custom date range: {start_date_str} to {end_date_str}")
        selected_symbols = None  # Use all symbols for custom range
    elif LIMIT_STOCKS:
        # Use last N months of data
        end_date_dt = datetime.now()
        start_date_dt = end_date_dt - timedelta(days=LAST_N_MONTHS * 30)
        start_date_str = start_date_dt.strftime('%Y-%m-%d')
        end_date_str = end_date_dt.strftime('%Y-%m-%d')
        log.info(f"🎯 Using limited mode: Last {LAST_N_MONTHS} months ({start_date_str} to {end_date_str})")

        # Get top liquid stocks (including specific symbols)
        selected_symbols = get_top_liquid_stocks(
            DUCKDB_PATH,
            MAX_STOCKS,
            LAST_N_MONTHS,
            include_specific=["AMARA RAJA ENERGY MOB LTD"]
        )
        log.info(f"📈 Selected {len(selected_symbols)} liquid stocks for ingestion")
    else:
        # Use provided date range or environment variables
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

        selected_symbols = None  # Use all symbols

    log.info(f"📅 Final filtering date range: {start_date_str} to {end_date_str}")

    # Determine cache file path first
    cache_dir = Path(".augment/cache/parquet_data")
    cache_dir.mkdir(parents=True, exist_ok=True)

    if USE_CUSTOM_DATE_RANGE:
        cache_filename = f"market_data_{start_date_str}_{end_date_str}_all.parquet"
    elif LIMIT_STOCKS:
        cache_filename = f"market_data_{start_date_str}_{end_date_str}_{len(selected_symbols) if selected_symbols else MAX_STOCKS}.parquet"
    else:
        cache_filename = f"market_data_{start_date_str}_{end_date_str}_all.parquet"

    parquet_path = cache_dir / cache_filename

    log.info(f"🔍 Looking for cache file: {parquet_path}")
    log.info(f"🔍 Cache file exists: {parquet_path.exists()}")
    log.info(f"🔍 Force refresh: {FORCE_REFRESH}")

    # Check if cache exists and is not being force refreshed
    if parquet_path.exists() and not FORCE_REFRESH:
        log.info("=" * 60)
        log.info("🗂️  STAGE 1: Using Existing Parquet Cache")
        log.info("=" * 60)
        log.info(f"📁 Found existing cache: {parquet_path}")
        file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
        log.info(f"📏 Cache file size: {file_size_mb:.1f} MB")
    else:
        # Only check for DuckDB if we need to extract
        if not os.path.exists(DUCKDB_PATH):
            raise ValueError(f"DuckDB file does not exist: {DUCKDB_PATH}")

        # STAGE 1: Extract to Parquet (with caching)
        log.info("=" * 60)
        log.info("🗂️  STAGE 1: Extract to Parquet Cache")
        log.info("=" * 60)

        parquet_path = extract_to_parquet(
            DUCKDB_PATH,
            start_date_str,
            end_date_str,
            selected_symbols,
            force_refresh=FORCE_REFRESH
        )

    # STAGE 2: Stream from Parquet and Create Bundle (Memory-Efficient)
    log.info("=" * 60)
    log.info("🚀 STAGE 2: Streaming Parquet to Zipline Bundle")
    log.info("=" * 60)

    # Instead of loading all data into memory, use streaming approach
    log.info("🔄 Using streaming ingestion to avoid memory issues...")
    log.info(f"� Streaming from: {parquet_path}")

    # Create asset metadata first (lightweight operation)
    asset_metadata_temp = create_asset_metadata_from_parquet(parquet_path)

    if asset_metadata_temp.empty:
        raise ValueError("No valid assets found in Parquet file")

    log.info(f"✅ Found {len(asset_metadata_temp)} assets for streaming ingestion")

    # Use the asset metadata we already created
    log.info("📝 Using pre-created asset metadata...")

    # Convert asset metadata to the format expected by Zipline
    asset_data = []
    for _, row in asset_metadata_temp.iterrows():
        symbol = row['clean_symbol']
        start_dt = row['start_date']
        end_dt = row['end_date']

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
        asset_metadata[col] = pd.to_datetime(asset_metadata[col], format='%Y-%m-%d', errors='coerce')

    # Check for any NaT values and log them
    for col in date_columns:
        nat_count = asset_metadata[col].isna().sum()
        if nat_count > 0:
            log.warning(f"Found {nat_count} NaT values in {col}")
            # Fill NaT values with a default date
            if col in ['start_date', 'first_traded']:
                asset_metadata[col] = asset_metadata[col].fillna(pd.Timestamp('2024-07-26'))
            else:  # end_date, auto_close_date
                asset_metadata[col] = asset_metadata[col].fillna(pd.Timestamp('2025-07-18'))

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
    overall_start = asset_metadata_temp['start_date'].min()
    overall_end = asset_metadata_temp['end_date'].max()

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

    # Write minute bars using streaming approach (memory efficient)
    log.info("📊 Writing minute bars using streaming approach...")

    def streaming_minute_data_generator():
        yield from streaming_parse_pricing_and_vol(parquet_path, sessions, symbol_map)

    minute_bar_writer.write(
        streaming_minute_data_generator(),
        show_progress=show_progress,
    )

    # Generate daily data from minute data using streaming approach
    log.info("📊 Generating daily bars using streaming approach...")

    def streaming_generate_daily_data(parquet_path, symbol_map, trading_sessions):
        """Generate daily OHLCV data from Parquet using streaming approach"""
        import polars as pl

        # Get trading dates for filtering
        trading_dates = set(trading_sessions.date)

        # Process each symbol individually for daily data
        for asset_id, symbol in symbol_map.items():
            try:
                # Read only this symbol's data from Parquet
                symbol_data = pl.scan_parquet(parquet_path).filter(
                    pl.col("symbol").map_elements(clean_symbol_name, return_dtype=pl.Utf8) == symbol
                ).collect()

                if len(symbol_data) == 0:
                    continue

                # Process timestamp
                try:
                    symbol_data = symbol_data.with_columns([
                        pl.col("timestamp").dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                    ])
                except:
                    symbol_data = symbol_data.with_columns([
                        pl.col("timestamp").str.to_datetime().dt.replace_time_zone("Asia/Kolkata").dt.convert_time_zone("UTC").alias("datetime")
                    ])

                # Filter and create daily data
                symbol_data = symbol_data.filter(
                    (pl.col("open") > 0) &
                    (pl.col("high") > 0) &
                    (pl.col("low") > 0) &
                    (pl.col("close") > 0) &
                    (pl.col("volume") >= 0)
                )

                # Filter to only include market hours and weekdays
                symbol_data = symbol_data.filter(
                    (pl.col("datetime").dt.hour() >= 3) &
                    (pl.col("datetime").dt.hour() < 10) &
                    pl.col("datetime").dt.weekday().is_in([1, 2, 3, 4, 5])
                ).with_columns([
                    pl.col("datetime").dt.date().alias("date")
                ])

                # Group by date to create daily bars
                daily_data = symbol_data.group_by("date").agg([
                    pl.col("open").first(),
                    pl.col("high").max(),
                    pl.col("low").min(),
                    pl.col("close").last(),
                    pl.col("volume").sum()
                ]).with_columns([
                    pl.col("date").cast(pl.Datetime).alias("datetime")
                ])

                # Convert to pandas and align with Zipline's exact trading sessions
                daily_pd = daily_data.to_pandas()

                # Create a complete DataFrame with all expected trading sessions for this symbol
                # This ensures we have exactly the sessions Zipline expects
                trading_session_dates = pd.DataFrame({'datetime': trading_sessions})

                # Merge with our data to ensure we have all expected sessions
                daily_pd = trading_session_dates.merge(daily_pd, on='datetime', how='left')

                # Forward fill missing OHLC data (use previous day's close as open, etc.)
                daily_pd = daily_pd.sort_values('datetime')
                daily_pd['open'] = daily_pd['open'].ffill()  # Updated syntax
                daily_pd['high'] = daily_pd['high'].fillna(daily_pd['open'])
                daily_pd['low'] = daily_pd['low'].fillna(daily_pd['open'])
                daily_pd['close'] = daily_pd['close'].fillna(daily_pd['open'])
                daily_pd['volume'] = daily_pd['volume'].fillna(0)

                # Remove any rows that still have NaN (beginning of series)
                daily_pd = daily_pd.dropna(subset=['open', 'high', 'low', 'close'])

                if len(daily_pd) > 0:
                    # Set datetime as index
                    daily_pd = daily_pd.set_index('datetime')
                    daily_pd = daily_pd.sort_index()
                    daily_pd['volume'] = daily_pd['volume'].fillna(0).astype(int)

                    yield asset_id, daily_pd

            except Exception as e:
                log.error(f"❌ Error generating daily data for {symbol}: {str(e)}")
                continue



    # Write daily bars using streaming approach
    log.info("📊 Writing daily bars using streaming approach...")

    def streaming_daily_data_generator():
        yield from streaming_generate_daily_data(parquet_path, symbol_map, sessions)

    daily_bar_writer.write(
        streaming_daily_data_generator(),
        show_progress=show_progress,
    )

    # Write empty adjustments (no splits/dividends data in current dataset)
    adjustment_writer.write(
        splits=pd.DataFrame(columns=['sid', 'effective_date', 'ratio']),
        dividends=pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']),
    )

    log.info("🎉 Parquet-cached DuckDB bundle ingestion completed successfully!")

def extract_data_to_cache(force_refresh=False):
    """
    Extract data from DuckDB to Parquet cache

    Parameters:
    -----------
    force_refresh : bool
        Force refresh cached data
    """
    log.info("🗂️  EXTRACTING DATA TO PARQUET CACHE")
    log.info("=" * 60)

    if not os.path.exists(DUCKDB_PATH):
        raise ValueError(f"DuckDB file does not exist: {DUCKDB_PATH}")

    # Determine parameters - prioritize custom date range, then limited mode, then full mode
    if USE_CUSTOM_DATE_RANGE:
        start_date_str = CUSTOM_START_DATE
        end_date_str = CUSTOM_END_DATE
        selected_symbols = None
        log.info(f"🎯 Custom date range mode: All stocks, {start_date_str} to {end_date_str}")
    elif LIMIT_STOCKS:
        end_date_dt = datetime.now()
        start_date_dt = end_date_dt - timedelta(days=LAST_N_MONTHS * 30)
        start_date_str = start_date_dt.strftime('%Y-%m-%d')
        end_date_str = end_date_dt.strftime('%Y-%m-%d')
        selected_symbols = get_top_liquid_stocks(
            DUCKDB_PATH,
            MAX_STOCKS,
            LAST_N_MONTHS,
            include_specific=["AMARA RAJA ENERGY MOB LTD"]
        )
        log.info(f"🎯 Limited mode: {len(selected_symbols)} stocks, {start_date_str} to {end_date_str}")
    else:
        start_date_str = None
        end_date_str = None
        selected_symbols = None
        log.info("🌐 Full mode: All stocks, all dates")

    # Extract to Parquet
    parquet_path = extract_to_parquet(
        DUCKDB_PATH,
        start_date_str,
        end_date_str,
        selected_symbols,
        force_refresh=force_refresh
    )

    log.info(f"✅ Data cached to: {parquet_path}")
    return parquet_path

def ingest_bundle_from_cache():
    """
    Ingest Zipline bundle from cached Parquet data
    """
    log.info("📦 INGESTING BUNDLE FROM CACHE")
    log.info("=" * 60)

    from zipline.data.bundles import ingest

    # Run the bundle ingestion
    ingest('nse-duckdb-parquet-bundle', show_progress=True)

    log.info("✅ Bundle ingestion completed!")

def main():
    """
    Main CLI function
    """
    import argparse

    parser = argparse.ArgumentParser(description='DuckDB to Parquet to Zipline Bundle Pipeline')
    parser.add_argument('action', choices=['extract', 'ingest', 'both'],
                       help='Action to perform: extract (to parquet), ingest (bundle), or both')
    parser.add_argument('--force-refresh', action='store_true',
                       help='Force refresh cached Parquet data')
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')

    args = parser.parse_args()

    if args.config:
        log.info("📋 CURRENT CONFIGURATION")
        log.info("=" * 40)
        log.info(f"Database path: {DUCKDB_PATH}")
        log.info(f"Cache directory: {CACHE_DIR}")
        log.info(f"Use custom date range: {USE_CUSTOM_DATE_RANGE}")
        if USE_CUSTOM_DATE_RANGE:
            log.info(f"Custom start date: {CUSTOM_START_DATE}")
            log.info(f"Custom end date: {CUSTOM_END_DATE}")
        log.info(f"Limited stocks: {LIMIT_STOCKS}")
        log.info(f"Max stocks: {MAX_STOCKS}")
        log.info(f"Last N months: {LAST_N_MONTHS}")
        log.info(f"Force refresh: {FORCE_REFRESH}")
        return

    try:
        if args.action in ['extract', 'both']:
            extract_data_to_cache(force_refresh=args.force_refresh)

        if args.action in ['ingest', 'both']:
            ingest_bundle_from_cache()

        log.info("🎉 Pipeline completed successfully!")

    except Exception as e:
        log.error(f"❌ Pipeline failed: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return 1

    return 0

# Register the bundle with XBOM calendar for NSE
import time
bundle_timestamp = int(time.time())
log.info(f"🔄 Registering bundle with timestamp: {bundle_timestamp}")
log.info(f"📅 Using XBOM calendar for NSE trading sessions")

register(
    'nse-duckdb-parquet-bundle',  # New name for Parquet-based bundle
    duckdb_polars_minute_bundle,
    calendar_name='XBOM',  # XBOM is the correct calendar for NSE (Bombay Stock Exchange)
    minutes_per_day=375,   # NSE trading session: 9:15 AM to 3:30 PM (375 minutes)
    create_writers=True
)

if __name__ == "__main__":
    sys.exit(main())
