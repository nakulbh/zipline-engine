"""
NSE Calendar using pandas_market_calendars for exchange_calendars
"""

import pandas as pd
from datetime import time
from pytz import timezone
import pandas_market_calendars as mcal
from exchange_calendars import ExchangeCalendar
from pandas import Timestamp
from pandas.tseries.holiday import HolidayCalendarFactory


class NSECalendar(ExchangeCalendar):
    """
    Custom NSE trading calendar using `pandas_market_calendars`.

    Open Time: 9:15 AM, Asia/Kolkata
    Close Time: 3:30 PM, Asia/Kolkata

    This calendar uses pandas_market_calendars XNSE calendar data
    to provide accurate NSE trading sessions and holidays.
    """

    name = "NSE"
    tz = timezone("Asia/Kolkata")

    # Required for ExchangeCalendar
    regular_market_times = {
        "market_open": ((None, time(9, 15)),),
        "market_close": ((None, time(15, 30)),),
    }

    def __init__(self, start=None, end=None):
        """
        Initialize NSE calendar with sessions from pandas_market_calendars.
        """
        # Set default date range
        if start is None:
            start = Timestamp('2000-01-01')
        if end is None:
            end = Timestamp('2035-12-31')

        # Create a simple holiday calendar (NSE holidays handled by mcal)
        self.adhoc_holidays = []
        self.regular_holidays = HolidayCalendarFactory(
            "NSEHolidays",
            base_class=None,
            rules=[]
        )()

        super().__init__(start=start, end=end)

    @property
    def open_time_default(self):
        return time(9, 15)

    @property
    def close_time_default(self):
        return time(15, 30)

    def valid_sessions(self, start_date, end_date):
        """
        Get valid trading sessions from pandas_market_calendars.
        """
        try:
            mcal_nse = mcal.get_calendar("XNSE")
            schedule = mcal_nse.schedule(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )

            sessions = schedule.index

            # Remove timezone if exists and normalize to midnight
            if sessions.tz is not None:
                sessions = sessions.tz_localize(None)

            trading_days = pd.DatetimeIndex(sessions.normalize())

            # Clean any NaT values
            if trading_days.isna().any():
                trading_days = trading_days.dropna()

            return trading_days

        except Exception as e:
            print(f"❌ Failed to get NSE trading days: {e}")
            # Fallback to business days
            return pd.bdate_range(start_date, end_date, freq='B')

    @property
    def open_times(self):
        """
        Return the open times for all sessions.
        """
        sessions = self.valid_sessions(
            self.first_session,
            self.last_session
        )
        return pd.Series(
            index=sessions,
            data=[self.open_time_default] * len(sessions),
            dtype=object
        )

    @property
    def close_times(self):
        """
        Return the close times for all sessions.
        """
        sessions = self.valid_sessions(
            self.first_session,
            self.last_session
        )
        return pd.Series(
            index=sessions,
            data=[self.close_time_default] * len(sessions),
            dtype=object
        )




def get_nse_sessions(start_date='2018-01-01', end_date='2023-12-31'):
    """
    Returns NSE trading sessions from mcal for given range.
    """
    try:
        print(f"📅 Fetching NSE sessions from {start_date} to {end_date}...")
        mcal_nse = mcal.get_calendar("XNSE")
        schedule = mcal_nse.schedule(start_date=start_date, end_date=end_date)

        sessions = schedule.index
        if sessions.tz is not None:
            sessions = sessions.tz_localize(None)

        all_sessions = pd.DatetimeIndex(sessions.normalize(), name='session')
        if all_sessions.isna().any():
            print("⚠️  Found NaT values. Cleaning...")
            all_sessions = all_sessions.dropna()

        print(f"✅ Found {len(all_sessions)} sessions")
        return all_sessions

    except Exception as e:
        print(f"❌ Error retrieving sessions: {e}")
        raise


def create_nse_calendar():
    """
    Creates and returns an instance of NSECalendar.
    """
    return NSECalendar()


def register_nse_calendar():
    """
    Register the NSE calendar with exchange_calendars.
    Call this function to make the NSE calendar available for use.
    """
    try:
        print("📝 Registering NSE calendar with exchange_calendars...")
        from exchange_calendars import register_calendar
        register_calendar("NSE", NSECalendar)
        print("✅ NSE calendar registered successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to register NSE calendar: {e}")
        return False


# Test harness
if __name__ == "__main__":
    print("🧪 Testing NSECalendar...")

    try:
        # Test getting sessions
        sessions = get_nse_sessions()
        print(f"✅ Got {len(sessions)} sessions")

        # Test creating calendar
        cal = create_nse_calendar()
        print(f"✅ Calendar created: {cal.name}")
        print(f"   Timezone: {cal.tz}")
        print(f"   Open time: {cal.open_time}")
        print(f"   Close time: {cal.close_time}")

        # Test registration
        register_nse_calendar()

    except Exception as e:
        print(f"❌ Test failed: {e}")

    print("🎉 Done")
