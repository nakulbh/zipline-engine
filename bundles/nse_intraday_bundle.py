import os
import pandas as pd
from datetime import date
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities
from zipline.utils.calendar_utils import register_calendar, TradingCalendar
from zipline.utils.memoize import lazyval
from dotenv import load_dotenv
from nse_workday import get_workdays_list
import pytz

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

BUNDLE_NAME = os.environ.get("ZIPLINE_BUNDLE_NAME", "nse-intraday-bundle")
CSV_PATH = os.environ.get("ZIPLINE_CSV_PATH", "/path/to/your/intraday/data")
CALENDAR_NAME = os.environ.get("ZIPLINE_CALENDAR", "NSE")
START_DATE = os.environ.get("ZIPLINE_START_DATE", "2015-01-01")
END_DATE = os.environ.get("ZIPLINE_END_DATE", "2025-12-31")


# -----------------------------
# Custom NSE Calendar (from nse-workday)
# -----------------------------
class NSETradingCalendar(TradingCalendar):
    name = "NSE"

    @property
    def tz(self):
        return pytz.timezone("Asia/Kolkata")

    @property
    def open_time(self):
        return pd.Timestamp("09:15", tz=self.tz).time()

    @property
    def close_time(self):
        return pd.Timestamp("15:30", tz=self.tz).time()

    @lazyval
    def sessions(self):
        start = date(2010, 1, 1)
        end = date(2025, 12, 31)
        workdays = get_workdays_list(start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y"))
        return pd.DatetimeIndex(pd.to_datetime(workdays).tz_localize(self.tz))

    @lazyval
    def open_times(self):
        return [(None, pd.Timestamp.combine(d.date(), self.open_time).tz_localize(self.tz))
                for d in self.sessions]

    @lazyval
    def close_times(self):
        return [(None, pd.Timestamp.combine(d.date(), self.close_time).tz_localize(self.tz))
                for d in self.sessions]



# -----------------------------
# Register NSE Calendar
# -----------------------------
try:
    register_calendar("NSE", NSETradingCalendar())
    print("✅ NSE Trading Calendar registered as 'NSE'")
except Exception as e:
    print(f"⚠️ Could not register NSE calendar: {e}")


# -----------------------------
# Register the Zipline Data Bundle
# -----------------------------
register(
    BUNDLE_NAME,
    csvdir_equities(
        ['minute'],
        CSV_PATH,
    ),
    calendar_name=CALENDAR_NAME,
    start_session=pd.Timestamp(START_DATE, tz="Asia/Kolkata"),
    end_session=pd.Timestamp(END_DATE, tz="Asia/Kolkata"),
)

print(f"✅ Bundle '{BUNDLE_NAME}' registered with calendar '{CALENDAR_NAME}'")
