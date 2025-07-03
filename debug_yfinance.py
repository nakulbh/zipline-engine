import yfinance as yf
import pandas as pd

# Test with one symbol to see the actual column structure
print("Testing yfinance data structure...")
data = yf.download('RELIANCE.NS', start='2024-01-01', end='2024-01-02', progress=False, auto_adjust=False)
print('Raw columns:', data.columns.tolist())
print('Column types:', type(data.columns))
print('Sample data:')
print(data.head())
print('\nAfter reset_index:')
data_reset = data.reset_index()
print('Columns after reset:', data_reset.columns.tolist())

# Test clean function
def clean_column_names(columns):
    """Handle both single-level and multi-level column indexes from yfinance"""
    cleaned = []
    for col in columns:
        if isinstance(col, tuple):
            # For MultiIndex columns from yfinance, take the first element (price type)
            # and clean it up
            price_type = str(col[0]).lower().replace(' ', '_')
            # Map common yfinance column names to our expected names
            if price_type == 'adj_close':
                price_type = 'close'  # Use adjusted close as close price
            cleaned.append(price_type)
        else:
            cleaned.append(str(col).lower())
    return cleaned

print('\nCleaned columns:', clean_column_names(data_reset.columns))

# Check what we actually need
required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
cleaned_cols = clean_column_names(data_reset.columns)
print('\nRequired columns:', required_columns)
print('Available columns:', cleaned_cols)
print('Missing:', [col for col in required_columns if col not in cleaned_cols])
