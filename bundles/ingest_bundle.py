#!/usr/bin/env python3

import os
import sys
import pandas as pd
from zipline.data.bundles import register, ingest
from zipline.data.bundles.csvdir import csvdir_equities

def fix_csv_files():
    """Fix CSV files to ensure proper timezone handling"""
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'daily')
    data_dir = os.path.abspath(data_dir)
    
    print(f"Fixing CSV files in: {data_dir}")
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        
        try:
            # Read the CSV
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            
            # Ensure index is timezone-naive (Zipline expects this)
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            # Ensure proper column names and order
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Check if columns exist (case-insensitive)
            df.columns = [col.lower() for col in df.columns]
            
            if not all(col in df.columns for col in required_columns):
                print(f"Warning: Missing columns in {csv_file}")
                continue
            
            # Reorder columns
            df = df[required_columns]
            
            # Ensure volume is integer
            df['volume'] = df['volume'].astype(int)
            
            # Remove any NaN values
            df = df.dropna()
            
            # Save back to CSV
            df.to_csv(file_path)
            
        except Exception as e:
            print(f"Error fixing {csv_file}: {e}")
    
    print(f"Fixed {len(csv_files)} CSV files")

def register_us_equities_bundle():
    """Register the US equities bundle with Zipline"""
    
    def us_equities_bundle(environ,
                          asset_db_writer,
                          minute_bar_writer,
                          daily_bar_writer,
                          adjustment_writer,
                          calendar,
                          start_session,
                          end_session,
                          cache,
                          show_progress,
                          output_dir):
        
        # Get the absolute path to the data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        data_dir = os.path.abspath(data_dir)
        
        print(f"Loading data from: {data_dir}")
        
        # Verify data directory structure
        daily_dir = os.path.join(data_dir, 'daily')
        if not os.path.exists(daily_dir):
            raise FileNotFoundError(f"Daily data directory not found: {daily_dir}")
        
        csv_files = [f for f in os.listdir(daily_dir) if f.endswith('.csv')]
        print(f"Found {len(csv_files)} CSV files")
        
        # Use csvdir_equities to load the data
        csvdir_equities(
            ['daily'],  # frequency
            data_dir,   # path to data directory
        )(
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
            output_dir
        )
    
    # Register the bundle
    register(
        'us-equities-bundle',
        us_equities_bundle,
        calendar_name='NYSE',
        start_session=pd.Timestamp('2018-01-01', tz='UTC'),
        end_session=pd.Timestamp('2023-12-31', tz='UTC')  # Use end of 2023 instead
    )

def main():
    """Main function to register and ingest the bundle"""
    
    # First, fix the CSV files
    print("Fixing CSV files...")
    fix_csv_files()
    
    # Register the bundle
    print("Registering bundle...")
    register_us_equities_bundle()
    
    # Ingest the bundle
    print("Ingesting bundle data...")
    try:
        ingest('us-equities-bundle', show_progress=True)
        print("Bundle ingestion completed successfully!")
        
        # Verify the ingestion
        print("\nBundle ingestion summary:")
        print(f"Bundle name: us-equities-bundle")
        print(f"Data period: 2018-01-01 to 2023-12-31")
        print(f"Calendar: NYSE")
        
    except Exception as e:
        print(f"Bundle ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)