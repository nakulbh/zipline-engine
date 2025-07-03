#!/bin/bash

# -------------------------------------------------------------------
# Zipline Bundle Ingest Script
# Usage: ./ingest_bundle.sh [bundle_name]
# Example: ./ingest_bundle.sh nse-local-minute-only-bundle
# -------------------------------------------------------------------

# Load environment variables (silently)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) > /dev/null 2>&1
    echo "✅ Loaded .env variables"
else
    echo "⚠️  No .env file found. Proceeding with system environment."
fi

# Set Zipline root directory (custom location)
export ZIPLINE_ROOT="/home/nakulbh/Desktop/Ankit/QuantMania/bactestingEngine/zipline-engine/.zipline"
echo "📦 ZIPLINE_ROOT set to: $ZIPLINE_ROOT"

# Check if bundle name is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please specify a bundle name."
    echo "Usage: ./ingest_bundle.sh [bundle_name]"
    exit 1
fi

BUNDLE_NAME="$1"

# Run zipline ingest
echo "⏳ Ingesting bundle: $BUNDLE_NAME..."
zipline ingest -b "$BUNDLE_NAME"

# Check exit status
if [ $? -eq 0 ]; then
    echo "🎉 Successfully ingested $BUNDLE_NAME!"
else
    echo "❌ Failed to ingest $BUNDLE_NAME. Check logs above."
    exit 1
fi