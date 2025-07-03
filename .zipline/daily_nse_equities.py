import os
import pandas as pd
import yfinance as yf
import logging
from six import iteritems

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

NSE_SYMBOLS = [
    'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'TCS.NS',
    'LT.NS', 'ITC.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS',
    'BHARTIARTL.NS', 'HINDUNILVR.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS',
    'WIPRO.NS', 'HCLTECH.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'ULTRACEMCO.NS',
    'TECHM.NS', 'NTPC.NS', 'TITAN.NS', 'POWERGRID.NS', 'ONGC.NS',
    'GRASIM.NS', 'BAJAJFINSV.NS', 'NESTLEIND.NS', 'TATAMOTORS.NS',
    'HINDALCO.NS', 'DRREDDY.NS', 'JSWSTEEL.NS', 'CIPLA.NS', 'ADANIENT.NS',
    'DIVISLAB.NS', 'COALINDIA.NS', 'BRITANNIA.NS', 'BPCL.NS', 'EICHERMOT.NS',
    'HEROMOTOCO.NS', 'TATASTEEL.NS', 'SBILIFE.NS', 'BAJAJ-AUTO.NS',
    'UPL.NS', 'SHREECEM.NS', 'INDUSINDBK.NS', 'APOLLOHOSP.NS',
    'HDFCLIFE.NS', 'ICICIPRULI.NS', 'M&M.NS', 'SBICARD.NS'
]

DATA_START_DATE = "2018-01-01"
DATA_END_DATE = "2024-12-31"


def fetch_nse_data(symbols, start_date=DATA_START_DATE, end_date=DATA_END_DATE, show_progress=True):
    """Fetch NSE data using yfinance"""
    if show_progress:
        log.info(f"Fetching NSE data for {len(symbols)} symbols from {start_date} to {end_date}")
    
    all_data = []
    successful_symbols = []
    failed_symbols = []
    
    for symbol in symbols:
        try:
            if show_progress:
                log.info(f"Downloading {symbol}...")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
            
            if data.empty:
                log.warning(f"No data available for {symbol}")
                failed_symbols.append(symbol)
                continue
            
            # Reset index to make date a column
            data = data.reset_index()
            
            # Rename columns to match Zipline expectations
            data.columns = [col.lower() for col in data.columns]
            data['symbol'] = symbol
            
            # Select required columns
            required_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            data = data[required_columns]
            
            # Add dividend and split columns (set to 0 for now)
            data['ex_dividend'] = 0.0
            data['split_ratio'] = 1.0
            
            # Clean data
            data = data.dropna()
            data['volume'] = data['volume'].astype('Int64')
            
            all_data.append(data)
            successful_symbols.append(symbol)
            
        except Exception as e:
            log.error(f"Failed to fetch data for {symbol}: {e}")
            failed_symbols.append(symbol)
    
    if not all_data:
        raise ValueError("No data was successfully fetched for any symbol")
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    if show_progress:
        log.info(f"Successfully fetched data for {len(successful_symbols)} symbols")
        if failed_symbols:
            log.warning(f"Failed to fetch data for: {failed_symbols}")
    
    return combined_data


def gen_asset_metadata(data, show_progress):
    """Generate asset metadata from the data"""
    if show_progress:
        log.info("Generating asset metadata.")

    metadata = data.groupby('symbol').agg({
        'date': ['min', 'max']
    }).reset_index()
    
    metadata.columns = ['symbol', 'start_date', 'end_date']
    metadata['exchange'] = 'NSE'
    metadata['auto_close_date'] = metadata['end_date'] + pd.Timedelta(days=1)
    
    return metadata


def parse_splits(data, show_progress):
    """Parse split data"""
    if show_progress:
        log.info("Parsing split data.")

    splits_data = data[data['split_ratio'] != 1.0].copy()
    
    if splits_data.empty:
        return pd.DataFrame(columns=['sid', 'effective_date', 'ratio'])
    
    splits_data['ratio'] = 1.0 / splits_data['split_ratio']
    splits_data = splits_data.rename(columns={
        'split_ratio': 'ratio',
        'date': 'effective_date'
    })
    
    return splits_data[['sid', 'effective_date', 'ratio']]


def parse_dividends(data, show_progress):
    """Parse dividend data"""
    if show_progress:
        log.info("Parsing dividend data.")

    dividends_data = data[data['ex_dividend'] != 0.0].copy()
    
    if dividends_data.empty:
        return pd.DataFrame(columns=['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date'])
    
    dividends_data['record_date'] = pd.NaT
    dividends_data['declared_date'] = pd.NaT
    dividends_data['pay_date'] = pd.NaT
    
    dividends_data = dividends_data.rename(columns={
        'ex_dividend': 'amount',
        'date': 'ex_date'
    })
    
    return dividends_data[['sid', 'ex_date', 'amount', 'record_date', 'declared_date', 'pay_date']]


def parse_pricing_and_vol(data, sessions, symbol_map):
    """Parse pricing and volume data"""
    data_indexed = data.set_index(['date', 'symbol'])
    
    for asset_id, symbol in iteritems(symbol_map):
        try:
            asset_data = data_indexed.xs(symbol, level=1)
            asset_data = asset_data.reindex(sessions.tz_localize(None)).ffill()
            
            # Select only OHLCV columns
            asset_data = asset_data[['open', 'high', 'low', 'close', 'volume']]
            
            yield asset_id, asset_data
        except KeyError:
            log.warning(f"No data found for symbol {symbol} (asset_id: {asset_id})")
            continue


def daily_nse_equities_bundle(
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
    daily_nse_equities_bundle builds a daily dataset using yfinance
    NSE equities data.
    """
    
    log.info("Starting NSE equities bundle ingestion...")
    
    # Fetch raw data
    raw_data = fetch_nse_data(NSE_SYMBOLS, show_progress=show_progress)
    
    # Generate asset metadata
    asset_metadata = gen_asset_metadata(raw_data[['symbol', 'date']], show_progress)
    
    # Create exchanges DataFrame
    exchanges = pd.DataFrame(
        data=[['NSE', 'National Stock Exchange of India', 'IN']],
        columns=['exchange', 'canonical_name', 'country_code']
    )
    
    # Write asset metadata
    asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)
    
    # Create symbol map for asset IDs
    symbol_map = pd.Series(
        index=asset_metadata.index,
        data=asset_metadata['symbol'].values
    )
    
    # Get trading sessions
    actual_start = raw_data['date'].min()
    actual_end = raw_data['date'].max()
    sessions = calendar.sessions_in_range(actual_start, actual_end)
    
    log.info(f"Writing daily bars for period {actual_start} to {actual_end}")
    
    # Write daily bars
    daily_bar_writer.write(
        parse_pricing_and_vol(raw_data, sessions, symbol_map),
        show_progress=show_progress,
    )
    
    # Prepare data for adjustments
    raw_data['symbol'] = raw_data['symbol'].astype('category')
    raw_data['sid'] = raw_data['symbol'].cat.codes
    
    # Write adjustments (splits and dividends)
    adjustment_writer.write(
        splits=parse_splits(
            raw_data[['sid', 'date', 'split_ratio']].loc[raw_data['split_ratio'] != 1],
            show_progress=show_progress,
        ),
        dividends=parse_dividends(
            raw_data[['sid', 'date', 'ex_dividend']].loc[raw_data['ex_dividend'] != 0],
            show_progress=show_progress,
        ),
    )
    
    log.info("NSE equities bundle ingestion completed successfully!")
