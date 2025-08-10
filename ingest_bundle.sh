#!/bin/bash

# -------------------------------------------------------------------
# DuckDB Zipline Bundle Ingest Script - Optimized for Strong Machines
# Usage: ./ingest_bundle.sh [action] [options]
# Examples:
#   ./ingest_bundle.sh both              # Extract + Ingest (full pipeline)
#   ./ingest_bundle.sh extract           # Extract to Parquet only
#   ./ingest_bundle.sh ingest            # Ingest from existing Parquet
#   ./ingest_bundle.sh extract --force   # Force refresh cache
#   ./ingest_bundle.sh config            # Show configuration
# -------------------------------------------------------------------

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Load environment variables (silently)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) > /dev/null 2>&1
    print_success "Loaded .env variables"
else
    print_warning "No .env file found. Proceeding with system environment."
fi

# Set Zipline root directory for macOS (updated path)
export ZIPLINE_ROOT="$HOME/.zipline"
print_info "ZIPLINE_ROOT set to: $ZIPLINE_ROOT"

# Default values
ACTION=""
FORCE_REFRESH=""
BUNDLE_NAME="nse-duckdb-parquet-bundle"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        both|extract|ingest|config)
            ACTION="$1"
            shift
            ;;
        --force|--force-refresh)
            FORCE_REFRESH="--force-refresh"
            shift
            ;;
        --bundle|-b)
            BUNDLE_NAME="$2"
            shift 2
            ;;
        --help|-h)
            echo "DuckDB Zipline Bundle Ingest Script"
            echo ""
            echo "Usage: $0 [action] [options]"
            echo ""
            echo "Actions:"
            echo "  both      Extract DuckDB data to Parquet cache, then ingest bundle"
            echo "  extract   Extract DuckDB data to Parquet cache only"
            echo "  ingest    Ingest bundle from existing Parquet cache"
            echo "  config    Show current configuration"
            echo ""
            echo "Options:"
            echo "  --force, --force-refresh    Force refresh cached Parquet data"
            echo "  --bundle, -b BUNDLE_NAME    Specify bundle name (default: nse-duckdb-parquet-bundle)"
            echo "  --help, -h                  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 both                     # Full pipeline: extract + ingest"
            echo "  $0 extract --force          # Force refresh cache"
            echo "  $0 ingest                   # Ingest from existing cache"
            echo "  $0 config                   # Show configuration"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if action is provided
if [ -z "$ACTION" ]; then
    print_error "Please specify an action."
    echo ""
    echo "Usage: $0 [action] [options]"
    echo "Actions: both, extract, ingest, config"
    echo "Use --help for more information"
    exit 1
fi

# Check if DuckDB bundle script exists
BUNDLE_SCRIPT="bundles/duckdb_polars_bundle.py"
if [ ! -f "$BUNDLE_SCRIPT" ]; then
    print_error "Bundle script not found: $BUNDLE_SCRIPT"
    print_info "Make sure you're running this script from the project root directory"
    exit 1
fi

# Check if DuckDB file exists (only for extract operations)
if [[ "$ACTION" == "both" || "$ACTION" == "extract" ]]; then
    # Try to get DuckDB path from the Python script using a more robust method
    DUCKDB_PATH=$(python3 -c "
import sys
import os
import re

# Read the bundle file directly without importing it
bundle_file = 'bundles/duckdb_polars_bundle.py'
if os.path.exists(bundle_file):
    with open(bundle_file, 'r') as f:
        content = f.read()
    # Extract DUCKDB_PATH using regex
    match = re.search(r'DUCKDB_PATH\s*=\s*[\"\'](.*?)[\"\']', content)
    if match:
        print(match.group(1))
    else:
        print('')
else:
    print('')
" 2>/dev/null)
    
    if [ -z "$DUCKDB_PATH" ]; then
        print_error "Could not extract DuckDB path from bundle script"
        print_info "Please check that bundles/duckdb_polars_bundle.py exists and contains DUCKDB_PATH"
        exit 1
    fi
    
    if [ ! -f "$DUCKDB_PATH" ]; then
        print_error "DuckDB file not found: $DUCKDB_PATH"
        print_info "Please ensure the DuckDB file exists before running extraction"
        print_info "Current path: $DUCKDB_PATH"
        exit 1
    else
        print_info "DuckDB file found: $DUCKDB_PATH"
    fi
fi

print_header "🚀 DuckDB Zipline Bundle Pipeline"
print_header "=================================="

# Run the Python bundle script
if [ "$ACTION" == "config" ]; then
    print_info "Showing configuration..."
    python3 "$BUNDLE_SCRIPT" config
elif [ "$ACTION" == "both" ]; then
    print_header "🔄 Running full pipeline (extract + ingest)..."
    python3 "$BUNDLE_SCRIPT" both $FORCE_REFRESH
elif [ "$ACTION" == "extract" ]; then
    print_header "📊 Extracting DuckDB data to Parquet cache..."
    python3 "$BUNDLE_SCRIPT" extract $FORCE_REFRESH
elif [ "$ACTION" == "ingest" ]; then
    print_header "📦 Ingesting bundle from Parquet cache..."
    python3 "$BUNDLE_SCRIPT" ingest
fi

# Check exit status
if [ $? -eq 0 ]; then
    print_success "Pipeline completed successfully!"
    
    # Show cache information if extraction was performed
    if [[ "$ACTION" == "both" || "$ACTION" == "extract" ]]; then
        CACHE_DIR=".augment/cache/parquet_data"
        if [ -d "$CACHE_DIR" ]; then
            print_info "Cache directory: $CACHE_DIR"
            CACHE_SIZE=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1)
            if [ ! -z "$CACHE_SIZE" ]; then
                print_info "Cache size: $CACHE_SIZE"
            fi
            
            # List cache files
            CACHE_FILES=$(ls -la "$CACHE_DIR"/*.parquet 2>/dev/null | wc -l)
            if [ "$CACHE_FILES" -gt 0 ]; then
                print_info "Parquet files in cache: $CACHE_FILES"
            fi
        fi
    fi
    
    # Show bundle information if ingestion was performed
    if [[ "$ACTION" == "both" || "$ACTION" == "ingest" ]]; then
        if [ -d "$ZIPLINE_ROOT" ]; then
            print_info "Bundle stored in: $ZIPLINE_ROOT"
        fi
        print_success "Bundle '$BUNDLE_NAME' is ready for backtesting!"
    fi
    
else
    print_error "Pipeline failed. Check logs above for details."
    exit 1
fi