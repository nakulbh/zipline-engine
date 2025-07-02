

# Ingest the registered bundle
# zipline-engine/bundles/nse_ingestion.py

import os
from zipline.data.bundles import bundles
from zipline.data import bundles
from zipline.utils.calendar_utils import register_calendar
from nse_intraday_bundle import NSETradingCalendar  # adjust if needed

# Register custom NSE calendar
register_calendar("NSE", NSETradingCalendar(), force=True)
print("✅ NSE Trading Calendar registered as 'XNSE'")

# Get the bundle function
bundle = "nse-intraday-bundle"
# Call ingest properly
bundles.ingestions_for_bundle(bundle)()





print("✅ Ingestion completed for NSE bundle.")
