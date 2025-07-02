import pandas as pd
import yfinance as yf
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities
import os
from typing import List


def create_data_bundle():
    """Create a simple data bundle for testing."""

    # Define symbols for your universe
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
        'PYPL', 'ADBE', 'CRM', 'INTC', 'AMD', 'ORCL', 'IBM', 'CSCO',
        'V', 'MA', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK-B',
        'JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN',
        'KO', 'PEP', 'WMT', 'HD', 'MCD', 'SBUX', 'NKE', 'DIS',
        'XOM', 'CVX', 'COP', 'SLB', 'HAL', 'OXY', 'DVN', 'SPY'
    ]

    start_date = '2018-01-01'
    end_date = '2024-01-01'

    print(f"Downloading data for {len(symbols)} symbols...")

    os.makedirs('./data/daily', exist_ok=True)

    successful_downloads = []
    failed_downloads = []

    for symbol in symbols:
        try:
            print(f"Downloading {symbol}...")

            data = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                print(f"No data available for {symbol}")
                failed_downloads.append(symbol)
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            data.columns = [col.lower() for col in data.columns]
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing = [col for col in required_columns if col not in data.columns]
            if missing:
                print(f"Missing columns for {symbol}: {missing}")
                failed_downloads.append(symbol)
                continue

            data = data[required_columns].dropna()
            if data.empty:
                print(f"No valid data remaining for {symbol} after cleaning")
                failed_downloads.append(symbol)
                continue

            data['volume'] = data['volume'].astype(int)
            output_path = f'./data/daily/{symbol}.csv'
            data.to_csv(output_path)
            print(f"✓ {symbol}: {len(data)} rows")
            successful_downloads.append(symbol)

        except Exception as e:
            print(f"✗ {symbol} failed: {e}")
            failed_downloads.append(symbol)

    print("\n✅ Data bundle creation completed!")
    print(f"Successful downloads: {len(successful_downloads)}")
    print(f"Failed downloads: {len(failed_downloads)}")
    if failed_downloads:
        print(f"Failed symbols: {failed_downloads}")

    if successful_downloads:
        pd.DataFrame({'symbol': successful_downloads}).to_csv('./data/symbols.csv', index=False)
        print(f"Symbols file saved with {len(successful_downloads)} symbols")


def bulk_download_symbols(symbols: List[str], start_date: str, end_date: str, batch_size: int = 10):
    """Download multiple symbols in batches to avoid rate limiting."""

    print(f"Downloading {len(symbols)} symbols in batches of {batch_size}...")
    os.makedirs('./data/daily', exist_ok=True)

    successful_downloads = []
    failed_downloads = []

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}: {batch}")

        try:
            data = yf.download(
                ' '.join(batch),
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False,
                group_by='ticker'
            )

            for symbol in batch:
                try:
                    symbol_data = data if len(batch) == 1 else data[symbol]

                    if symbol_data.empty:
                        print(f"No data for {symbol}")
                        failed_downloads.append(symbol)
                        continue

                    symbol_data.columns = [col.lower() for col in symbol_data.columns]
                    required_columns = ['open', 'high', 'low', 'close', 'volume']

                    if not all(col in symbol_data.columns for col in required_columns):
                        print(f"Missing columns for {symbol}")
                        failed_downloads.append(symbol)
                        continue

                    symbol_data = symbol_data[required_columns].dropna()

                    if symbol_data.empty:
                        print(f"No valid data for {symbol}")
                        failed_downloads.append(symbol)
                        continue

                    symbol_data['volume'] = symbol_data['volume'].astype(int)
                    symbol_data.to_csv(f'./data/daily/{symbol}.csv')
                    successful_downloads.append(symbol)
                    print(f"✓ {symbol}")

                except Exception as e:
                    print(f"✗ {symbol}: {e}")
                    failed_downloads.append(symbol)

        except Exception as e:
            print(f"Batch download failed: {e}")
            failed_downloads.extend(batch)

    return successful_downloads, failed_downloads


if __name__ == "__main__":
    # Example usage:
    
    # Option 1: Use single symbol download
    # create_data_bundle()

    # Option 2: Use batch download
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
        'PYPL', 'ADBE', 'CRM', 'INTC', 'AMD', 'ORCL', 'IBM', 'CSCO',
        'V', 'MA', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK-B',
        'JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN',
        'KO', 'PEP', 'WMT', 'HD', 'MCD', 'SBUX', 'NKE', 'DIS',
        'XOM', 'CVX', 'COP', 'SLB', 'HAL', 'OXY', 'DVN', 'SPY'
    ]

    successful, failed = bulk_download_symbols(symbols, '2018-01-01', '2024-01-01')

    print(f"\nResults:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if failed:
        print(f"Failed symbols: {failed}")

    if successful:
        pd.DataFrame({'symbol': successful}).to_csv('./data/symbols.csv', index=False)
        print(f"Symbols file saved with {len(successful)} symbols")
