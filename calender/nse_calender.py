# zipline_engine/calendars/nse_calendar.py

from zipline.utils.calendar_utils import TradingCalendar
from zipline.utils.memoize import lazyval
from nse_workday import get_workdays_list
from datetime import date
import pandas as pd
import pytz


class NSETradingCalendar(TradingCalendar):
    """
    Custom NSE trading calendar using nse-workday
    """

    @property
    def name(self):
        return "XNSE"

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
        # Hardcoded valid range — can also make dynamic
        start = date(2010, 1, 1)
        end = date(2030, 12, 31)

        workdays = get_workdays_list(start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y"))
        return pd.DatetimeIndex(pd.to_datetime(workdays).tz_localize("Asia/Kolkata"))
