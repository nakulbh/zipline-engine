#!/usr/bin/env python3
"""
DuckDB to Parquet to Zipline Bundle Pipeline
============================================

This script provides a complete pipeline for:
1. Extracting data from DuckDB to compressed Parquet files (cached)
2. Ingesting Zipline bundles from the cached Parquet data

Features:
- Memory efficient processing with Polars
- Compressed Parquet caching for fast re-ingestion
- Automatic liquid stock selection
- Configurable date ranges and stock limits
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def show_config():
    """Show current configuration"""
    from bundles.duckdb_polars_bundle import (
        DUCKDB_PATH, CACHE_DIR, LIMIT_STOCKS, MAX_STOCKS, LAST_N_MONTHS, FORCE_REFRESH,
        USE_CUSTOM_DATE_RANGE, CUSTOM_START_DATE, CUSTOM_END_DATE
    )
    
    print("🔧 CURRENT CONFIGURATION")
    print("=" * 50)
    print(f"📁 Database path: {DUCKDB_PATH}")
    print(f"💾 Cache directory: {CACHE_DIR}")
    print(f"📅 Use custom date range: {USE_CUSTOM_DATE_RANGE}")
    if USE_CUSTOM_DATE_RANGE:
        print(f"📅 Custom start date: {CUSTOM_START_DATE}")
        print(f"📅 Custom end date: {CUSTOM_END_DATE}")
    print(f"🎯 Limited stocks: {LIMIT_STOCKS}")
    print(f"📊 Max stocks: {MAX_STOCKS}")
    print(f"📅 Last N months: {LAST_N_MONTHS}")
    print(f"🔄 Force refresh: {FORCE_REFRESH}")
    print()
    
    # Check if database exists
    if os.path.exists(DUCKDB_PATH):
        print(f"✅ Database file found")
        file_size = os.path.getsize(DUCKDB_PATH) / (1024**3)  # GB
        print(f"📏 Database size: {file_size:.2f} GB")
    else:
        print(f"❌ Database file not found!")
    
    # Check cache directory
    if CACHE_DIR.exists():
        cache_files = list(CACHE_DIR.glob("*.parquet"))
        print(f"📦 Cache files: {len(cache_files)}")
        if cache_files:
            total_cache_size = sum(f.stat().st_size for f in cache_files) / (1024**2)  # MB
            print(f"💾 Total cache size: {total_cache_size:.1f} MB")
            print("   Recent cache files:")
            for f in sorted(cache_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                size = f.stat().st_size / (1024**2)  # MB
                print(f"   • {f.name} ({size:.1f} MB, {age.days}d old)")
    else:
        print(f"📦 Cache directory will be created")

def extract_only():
    """Extract data to Parquet cache only"""
    print("🗂️  EXTRACT TO PARQUET CACHE")
    print("=" * 50)
    
    try:
        from bundles.duckdb_polars_bundle import extract_data_to_cache
        
        parquet_path = extract_data_to_cache(force_refresh=False)
        
        print(f"✅ Data extracted to: {parquet_path}")
        
        # Show file info
        from pathlib import Path
        cache_file = Path(parquet_path)
        file_size = cache_file.stat().st_size / (1024**2)  # MB
        print(f"📏 File size: {file_size:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        return False

def ingest_only():
    """Ingest bundle from cached Parquet data only"""
    print("📦 INGEST BUNDLE FROM CACHE")
    print("=" * 50)
    
    try:
        from bundles.duckdb_polars_bundle import ingest_bundle_from_cache
        
        ingest_bundle_from_cache()
        
        print("✅ Bundle ingestion completed!")
        return True
        
    except Exception as e:
        print(f"❌ Bundle ingestion failed: {str(e)}")
        return False

def run_full_pipeline():
    """Run complete pipeline: extract + ingest"""
    print("🚀 FULL PIPELINE: EXTRACT + INGEST")
    print("=" * 50)
    
    # Step 1: Extract
    if not extract_only():
        return False
    
    print()
    
    # Step 2: Ingest
    if not ingest_only():
        return False
    
    print()
    print("🎉 Full pipeline completed successfully!")
    print()
    print("📋 Next steps:")
    print("• Bundle name: 'nse-duckdb-parquet-bundle'")
    print("• Use in your strategies with this bundle name")
    print("• Run verify_bundle.py to check the bundle")
    
    return True

def main():
    """Main function"""
    print("🚀 DuckDB to Parquet to Zipline Pipeline")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    else:
        print("Available actions:")
        print("1. config  - Show current configuration")
        print("2. extract - Extract data to Parquet cache")
        print("3. ingest  - Ingest bundle from cache")
        print("4. both    - Run full pipeline (extract + ingest)")
        print()
        action = input("Choose action (1-4): ").strip()
        
        action_map = {'1': 'config', '2': 'extract', '3': 'ingest', '4': 'both'}
        action = action_map.get(action, action)
    
    if action == 'config':
        show_config()
    elif action == 'extract':
        extract_only()
    elif action == 'ingest':
        ingest_only()
    elif action == 'both':
        run_full_pipeline()
    else:
        print(f"❌ Unknown action: {action}")
        print("Valid actions: config, extract, ingest, both")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
