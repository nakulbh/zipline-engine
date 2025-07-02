# bundles/register_us_equities_bundle.py

import os
import pandas as pd
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

# Set the correct data directory and bundle name
BUNDLE_NAME = "us-equities-bundle"
DATA_PATH = "./data"  # Parent of the 'daily' folder

# Register the bundle
register(
    BUNDLE_NAME,
    csvdir_equities(
        ['daily'],  # frequency
        DATA_PATH,  # this should contain the 'daily' folder
    ),
    calendar_name='NYSE',  # calendar used for US stocks
    start_session=pd.Timestamp('2018-01-01', tz='UTC'),
    end_session=pd.Timestamp('2024-01-01', tz='UTC')
)

print(f"✅ Bundle '{BUNDLE_NAME}' registered successfully with data at {DATA_PATH}")
