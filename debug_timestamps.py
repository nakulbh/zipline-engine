#!/usr/bin/env python3

import pandas as pd
import pytz
from zipline.utils.calendar_utils import get_calendar

# Check what the trading calendar expects
trading_calendar = get_calendar('XBOM')
sample_session = pd.Timestamp('2015-01-09')
sample_minutes = trading_calendar.session_minutes(sample_session)
print('Sample trading calendar minutes for 2015-01-09:')
print(sample_minutes[:10])

# Check what our CSV data looks like after conversion
IST = pytz.timezone('Asia/Kolkata')
csv_timestamps = [
    '2015-01-09 09:15:59',
    '2015-01-09 09:16:59', 
    '2015-01-09 09:17:59'
]
print('\nCSV timestamps converted to UTC:')
for ts in csv_timestamps:
    dt_ist = pd.to_datetime(ts).tz_localize(IST)
    dt_utc = dt_ist.tz_convert('UTC')
    print(f'CSV: {ts} -> UTC: {dt_utc}')

print('\nCalendar expects minutes ending in :00, CSV has minutes ending in :59')
print('Need to round/adjust timestamps to match calendar expectations')

# Test the solution - round timestamps to nearest minute
print('\nTesting timestamp rounding:')
for ts in csv_timestamps:
    dt_ist = pd.to_datetime(ts).tz_localize(IST)
    dt_utc = dt_ist.tz_convert('UTC')
    # Round to nearest minute
    dt_rounded = dt_utc.round('min')
    print(f'Original: {dt_utc} -> Rounded: {dt_rounded}')
    print(f'In calendar: {dt_rounded in sample_minutes}')
