[Skip to main content](https://zipline.ml4trading.io/api-reference.html#main-content)

`Ctrl` + `K`

[Zipline 3.0 docs](https://zipline.ml4trading.io/index.html)

Site Navigation


- [Installation](https://zipline.ml4trading.io/install.html)
- [Tutorial](https://zipline.ml4trading.io/beginner-tutorial.html)
- [Data](https://zipline.ml4trading.io/bundles.html)
- [Calendars](https://zipline.ml4trading.io/trading-calendars.html)
- [Metrics](https://zipline.ml4trading.io/risk-and-perf-metrics.html)

More


[Development](https://zipline.ml4trading.io/development-guidelines.html)
[API](https://zipline.ml4trading.io/api-reference.html#)
[Releases](https://zipline.ml4trading.io/releases.html)
[ML for Trading](https://ml4trading.io/)
[Community](https://exchange.ml4trading.io/)

- [GitHub](https://github.com/stefan-jansen/zipline-reloaded)
- [Twitter](https://twitter.com/ml4trading)

Site Navigation


- [Installation](https://zipline.ml4trading.io/install.html)
- [Tutorial](https://zipline.ml4trading.io/beginner-tutorial.html)
- [Data](https://zipline.ml4trading.io/bundles.html)
- [Calendars](https://zipline.ml4trading.io/trading-calendars.html)
- [Metrics](https://zipline.ml4trading.io/risk-and-perf-metrics.html)

More


[Development](https://zipline.ml4trading.io/development-guidelines.html)
[API](https://zipline.ml4trading.io/api-reference.html#)
[Releases](https://zipline.ml4trading.io/releases.html)
[ML for Trading](https://ml4trading.io/)
[Community](https://exchange.ml4trading.io/)

- [GitHub](https://github.com/stefan-jansen/zipline-reloaded)
- [Twitter](https://twitter.com/ml4trading)

- [Home](https://zipline.ml4trading.io/index.html)
- API

# API [\#](https://zipline.ml4trading.io/api-reference.html\#api "Permalink to this heading")

## Running a Backtest [\#](https://zipline.ml4trading.io/api-reference.html\#running-a-backtest "Permalink to this heading")

The function [`run_algorithm()`](https://zipline.ml4trading.io/api-reference.html#zipline.run_algorithm "zipline.run_algorithm") creates an instance of
`TradingAlgorithm` that represents a
trading strategy and parameters to execute the strategy.

zipline.run\_algorithm( _..._) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/run_algo.html#run_algorithm) [#](https://zipline.ml4trading.io/api-reference.html#zipline.run_algorithm "Permalink to this definition")

Run a trading algorithm.

Parameters:

- **start** ( _datetime_) – The start date of the backtest.

- **end** ( _datetime_) – The end date of the backtest..

- **initialize** ( _callable_ _\[_ _context -> None_ _\]_) – The initialize function to use for the algorithm. This is called once
at the very begining of the backtest and should be used to set up
any state needed by the algorithm.

- **capital\_base** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The starting capital for the backtest.

- **handle\_data** ( _callable_ _\[_ _(_ _context_ _,_ [_BarData_](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "zipline.protocol.BarData") _)_ _-\> None_ _\]_ _,_ _optional_) – The handle\_data function to use for the algorithm. This is called
every minute when `data_frequency == 'minute'` or every day
when `data_frequency == 'daily'`.

- **before\_trading\_start** ( _callable_ _\[_ _(_ _context_ _,_ [_BarData_](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "zipline.protocol.BarData") _)_ _-\> None_ _\]_ _,_ _optional_) – The before\_trading\_start function for the algorithm. This is called
once before each trading day (after initialize on the first day).

- **analyze** ( _callable_ _\[_ _(_ _context_ _,_ _pd.DataFrame_ _)_ _-\> None_ _\]_ _,_ _optional_) – The analyze function to use for the algorithm. This function is called
once at the end of the backtest and is passed the context and the
performance data.

- **data\_frequency** ( _{'daily'_ _,_ _'minute'}_ _,_ _optional_) – The data frequency to run the algorithm at.

- **bundle** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the data bundle to use to load the data to run the backtest
with. This defaults to ‘quantopian-quandl’.

- **bundle\_timestamp** ( _datetime_ _,_ _optional_) – The datetime to lookup the bundle data for. This defaults to the
current time.

- **trading\_calendar** ( _TradingCalendar_ _,_ _optional_) – The trading calendar to use for your backtest.

- **metrics\_set** ( _iterable_ _\[_ _Metric_ _\] or_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The set of metrics to compute in the simulation. If a string is passed,
resolve the set with [`zipline.finance.metrics.load()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.load "zipline.finance.metrics.load").

- **benchmark\_returns** ( _pd.Series_ _,_ _optional_) – Series of returns to use as the benchmark.

- **default\_extension** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should the default zipline extension be loaded. This is found at
`$ZIPLINE_ROOT/extension.py`

- **extensions** ( _iterable_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_ _,_ _optional_) – The names of any other extensions to load. Each element may either be
a dotted module path like `a.b.c` or a path to a python file ending
in `.py` like `a/b/c.py`.

- **strict\_extensions** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should the run fail if any extensions fail to load. If this is false,
a warning will be raised instead.

- **environ** ( _mapping_ _\[_ _str -> str_ _\]_ _,_ _optional_) – The os environment to use. Many extensions use this to get parameters.
This defaults to `os.environ`.

- **blotter** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _zipline.finance.blotter.Blotter_ _,_ _optional_) – Blotter to use with this algorithm. If passed as a string, we look for
a blotter construction function registered with
`zipline.extensions.register` and call it with no parameters.
Default is a [`zipline.finance.blotter.SimulationBlotter`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter "zipline.finance.blotter.SimulationBlotter") that
never cancels orders.


Returns:

**perf** – The daily performance of the algorithm.

Return type:

pd.DataFrame

See also

[`zipline.data.bundles.bundles`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.bundles "zipline.data.bundles.bundles")

The available data bundles.

## Trading Algorithm API [\#](https://zipline.ml4trading.io/api-reference.html\#trading-algorithm-api "Permalink to this heading")

The following methods are available for use in the `initialize`,
`handle_data`, and `before_trading_start` API functions.

In all listed functions, the `self` argument refers to the
currently executing `TradingAlgorithm` instance.

### Data Object [\#](https://zipline.ml4trading.io/api-reference.html\#data-object "Permalink to this heading")

_class_ zipline.protocol.BarData [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "Permalink to this definition")

Provides methods for accessing minutely and daily price/volume data from
Algorithm API functions.

Also provides utility methods to determine if an asset is alive, and if it
has recent trade data.

An instance of this object is passed as `data` to
`handle_data()` and
`before_trading_start()`.

Parameters:

- **data\_portal** ( [_DataPortal_](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal "zipline.data.data_portal.DataPortal")) – Provider for bar pricing data.

- **simulation\_dt\_func** ( _callable_) – Function which returns the current simulation time.
This is usually bound to a method of TradingSimulation.

- **data\_frequency** ( _{'minute'_ _,_ _'daily'}_) – The frequency of the bar data; i.e. whether the data is
daily or minute bars

- **restrictions** ( _zipline.finance.asset\_restrictions.Restrictions_) – Object that combines and returns restricted list information from
multiple sources


can\_trade() [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.can_trade "Permalink to this definition")

For the given asset or iterable of assets, returns True if all of the
following are true:

1. The asset is alive for the session of the current simulation time
(if current simulation time is not a market minute, we use the next
session).

2. The asset’s exchange is open at the current simulation time or at
the simulation calendar’s next market minute.

3. There is a known last price for the asset.


Parameters:

**assets** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _or_ _iterable_ _of_ [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – Asset(s) for which tradability should be determined.

Notes

The second condition above warrants some further explanation:

- If the asset’s exchange calendar is identical to the simulation
calendar, then this condition always returns True.

- If there are market minutes in the simulation calendar outside of
this asset’s exchange’s trading hours (for example, if the simulation
is running on the CMES calendar but the asset is MSFT, which trades
on the NYSE), during those minutes, this condition will return False
(for example, 3:15 am Eastern on a weekday, during which the CMES is
open but the NYSE is closed).


Returns:

**can\_trade** – Bool or series of bools indicating whether the requested asset(s)
can be traded in the current minute.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") or pd.Series\[ [bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")\]

current() [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.current "Permalink to this definition")

Returns the “current” value of the given fields for the given assets
at the current simulation time.

Parameters:

- **assets** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _or_ _iterable_ _of_ [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset(s) for which data is requested.

- **fields** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _iterable_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_ _._) – Requested data field(s). Valid field names are: “price”,
“last\_traded”, “open”, “high”, “low”, “close”, and “volume”.


Returns:

**current\_value** – See notes below.

Return type:

Scalar, pandas Series, or pandas DataFrame.

Notes

The return type of this function depends on the types of its inputs:

- If a single asset and a single field are requested, the returned
value is a scalar (either a float or a `pd.Timestamp` depending on
the field).

- If a single asset and a list of fields are requested, the returned
value is a `pd.Series` whose indices are the requested fields.

- If a list of assets and a single field are requested, the returned
value is a `pd.Series` whose indices are the assets.

- If a list of assets and a list of fields are requested, the returned
value is a `pd.DataFrame`. The columns of the returned frame
will be the requested fields, and the index of the frame will be the
requested assets.


The values produced for `fields` are as follows:

- Requesting “price” produces the last known close price for the asset,
forward-filled from an earlier minute if there is no trade this
minute. If there is no last known value (either because the asset
has never traded, or because it has delisted) NaN is returned. If a
value is found, and we had to cross an adjustment boundary (split,
dividend, etc) to get it, the value is adjusted to the current
simulation time before being returned.

- Requesting “open”, “high”, “low”, or “close” produces the open, high,
low, or close for the current minute. If no trades occurred this
minute, `NaN` is returned.

- Requesting “volume” produces the trade volume for the current
minute. If no trades occurred this minute, 0 is returned.

- Requesting “last\_traded” produces the datetime of the last minute in
which the asset traded, even if the asset has stopped trading. If
there is no last known value, `pd.NaT` is returned.


If the current simulation time is not a valid market time for an asset,
we use the most recent market close instead.

history() [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.history "Permalink to this definition")

Returns a trailing window of length `bar_count` with data for
the given assets, fields, and frequency, adjusted for splits, dividends,
and mergers as of the current simulation time.

The semantics for missing data are identical to the ones described in
the notes for [`current()`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.current "zipline.protocol.BarData.current").

Parameters:

- **assets** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _or_ _iterable_ _of_ [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset(s) for which data is requested.

- **fields** ( _string_ _or_ _iterable_ _of_ _string._) – Requested data field(s). Valid field names are: “price”,
“last\_traded”, “open”, “high”, “low”, “close”, and “volume”.

- **bar\_count** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Number of data observations requested.

- **frequency** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – String indicating whether to load daily or minutely data
observations. Pass ‘1m’ for minutely data, ‘1d’ for daily data.


Returns:

**history** – See notes below.

Return type:

pd.Series or pd.DataFrame or pd.Panel

Notes

The return type of this function depends on the types of `assets` and
`fields`:

- If a single asset and a single field are requested, the returned
value is a `pd.Series` of length `bar_count` whose index is
`pd.DatetimeIndex`.

- If a single asset and multiple fields are requested, the returned
value is a `pd.DataFrame` with shape
`(bar_count, len(fields))`. The frame’s index will be a
`pd.DatetimeIndex`, and its columns will be `fields`.

- If multiple assets and a single field are requested, the returned
value is a `pd.DataFrame` with shape
`(bar_count, len(assets))`. The frame’s index will be a
`pd.DatetimeIndex`, and its columns will be `assets`.

- If multiple assets and multiple fields are requested, the returned
value is a `pd.DataFrame` with a pd.MultiIndex containing
pairs of `pd.DatetimeIndex`, and `assets`, while the columns
while contain the field(s). It has shape `(bar_count * len(assets),
len(fields))`. The names of the pd.MultiIndex are


> - `date` if frequency == ‘1d’\`\` or `date_time` if frequency == ‘1m\`\`, and
>
> - `asset`


If the current simulation time is not a valid market time, we use the last market close instead.

is\_stale() [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.is_stale "Permalink to this definition")

For the given asset or iterable of assets, returns True if the asset
is alive and there is no trade data for the current simulation time.

If the asset has never traded, returns False.

If the current simulation time is not a valid market time, we use the
current time to check if the asset is alive, but we use the last
market minute/day for the trade data check.

Parameters:

**assets** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _or_ _iterable_ _of_ [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – Asset(s) for which staleness should be determined.

Returns:

**is\_stale** – Bool or series of bools indicating whether the requested asset(s)
are stale.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") or pd.Series\[ [bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")\]

### Scheduling Functions [\#](https://zipline.ml4trading.io/api-reference.html\#scheduling-functions "Permalink to this heading")

zipline.api.schedule\_function( _self_, _func_, _date\_rule=None_, _time\_rule=None_, _half\_days=True_, _calendar=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function "Permalink to this definition")

Schedule a function to be called repeatedly in the future.

Parameters:

- **func** ( _callable_) – The function to execute when the rule is triggered. `func` should
have the same signature as `handle_data`.

- **date\_rule** ( _zipline.utils.events.EventRule_ _,_ _optional_) – Rule for the dates on which to execute `func`. If not
passed, the function will run every trading day.

- **time\_rule** ( _zipline.utils.events.EventRule_ _,_ _optional_) – Rule for the time at which to execute `func`. If not passed, the
function will execute at the end of the first market minute of the
day.

- **half\_days** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should this rule fire on half days? Default is True.

- **calendar** ( _Sentinel_ _,_ _optional_) – Calendar used to compute rules that depend on the trading calendar.


See also

[`zipline.api.date_rules`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules "zipline.api.date_rules"), [`zipline.api.time_rules`](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules "zipline.api.time_rules")

_class_ zipline.api.date\_rules [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules "Permalink to this definition")

Factories for date-based [`schedule_function()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function "zipline.api.schedule_function") rules.

See also

[`schedule_function()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function "zipline.api.schedule_function")

_static_ every\_day() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules.every_day) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.every_day "Permalink to this definition")

Create a rule that triggers every day.

Returns:

**rule**

Return type:

zipline.utils.events.EventRule

_static_ month\_end( _days\_offset=0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules.month_end) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.month_end "Permalink to this definition")

Create a rule that triggers a fixed number of trading days before the
end of each month.

Parameters:

**days\_offset** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – Number of trading days prior to month end to trigger. Default is 0,
i.e., trigger on the last day of the month.

Returns:

**rule**

Return type:

zipline.utils.events.EventRule

_static_ month\_start( _days\_offset=0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules.month_start) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.month_start "Permalink to this definition")

Create a rule that triggers a fixed number of trading days after the
start of each month.

Parameters:

**days\_offset** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – Number of trading days to wait before triggering each
month. Default is 0, i.e., trigger on the first trading day of the
month.

Returns:

**rule**

Return type:

zipline.utils.events.EventRule

_static_ week\_end( _days\_offset=0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules.week_end) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.week_end "Permalink to this definition")

Create a rule that triggers a fixed number of trading days before the
end of each week.

Parameters:

**days\_offset** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – Number of trading days prior to week end to trigger. Default is 0,
i.e., trigger on the last trading day of the week.

_static_ week\_start( _days\_offset=0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#date_rules.week_start) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.week_start "Permalink to this definition")

Create a rule that triggers a fixed number of trading days after the
start of each week.

Parameters:

**days\_offset** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – Number of trading days to wait before triggering each week. Default
is 0, i.e., trigger on the first trading day of the week.

_class_ zipline.api.time\_rules [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#time_rules) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules "Permalink to this definition")

Factories for time-based [`schedule_function()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function "zipline.api.schedule_function") rules.

See also

[`schedule_function()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function "zipline.api.schedule_function")

every\_minute [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.every_minute "Permalink to this definition")

alias of `Always`

_static_ market\_close( _offset=None_, _hours=None_, _minutes=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#time_rules.market_close) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.market_close "Permalink to this definition")

Create a rule that triggers at a fixed offset from market close.

The offset can be specified either as a [`datetime.timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta "(in Python v3.11)"), or
as a number of hours and minutes.

Parameters:

- **offset** ( [_datetime.timedelta_](https://docs.python.org/3/library/datetime.html#datetime.timedelta "(in Python v3.11)") _,_ _optional_) – If passed, the offset from market close at which to trigger. Must
be at least 1 minute.

- **hours** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – If passed, number of hours to wait before market close.

- **minutes** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – If passed, number of minutes to wait before market close.


Returns:

**rule**

Return type:

zipline.utils.events.EventRule

Notes

If no arguments are passed, the default offset is one minute before
market close.

If `offset` is passed, `hours` and `minutes` must not be
passed. Conversely, if either `hours` or `minutes` are passed,
`offset` must not be passed.

_static_ market\_open( _offset=None_, _hours=None_, _minutes=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/events.html#time_rules.market_open) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.market_open "Permalink to this definition")

Create a rule that triggers at a fixed offset from market open.

The offset can be specified either as a [`datetime.timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta "(in Python v3.11)"), or
as a number of hours and minutes.

Parameters:

- **offset** ( [_datetime.timedelta_](https://docs.python.org/3/library/datetime.html#datetime.timedelta "(in Python v3.11)") _,_ _optional_) – If passed, the offset from market open at which to trigger. Must be
at least 1 minute.

- **hours** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – If passed, number of hours to wait after market open.

- **minutes** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – If passed, number of minutes to wait after market open.


Returns:

**rule**

Return type:

zipline.utils.events.EventRule

Notes

If no arguments are passed, the default offset is one minute after
market open.

If `offset` is passed, `hours` and `minutes` must not be
passed. Conversely, if either `hours` or `minutes` are passed,
`offset` must not be passed.

### Orders [\#](https://zipline.ml4trading.io/api-reference.html\#orders "Permalink to this heading")

zipline.api.order( _self_, _asset_, _amount_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "Permalink to this definition")

Place an order for a fixed number of shares.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to be ordered.

- **amount** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The amount of shares to order. If `amount` is positive, this is
the number of shares to buy or cover. If `amount` is negative,
this is the number of shares to sell or short.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle") _,_ _optional_) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order, or None if no order was
placed.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None

Notes

The `limit_price` and `stop_price` arguments provide shorthands for
passing common execution styles. Passing `limit_price=N` is
equivalent to `style=LimitOrder(N)`. Similarly, passing
`stop_price=M` is equivalent to `style=StopOrder(M)`, and passing
`limit_price=N` and `stop_price=M` is equivalent to
`style=StopLimitOrder(N, M)`. It is an error to pass both a `style`
and `limit_price` or `stop_price`.

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_value "zipline.api.order_value"), [`zipline.api.order_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_percent "zipline.api.order_percent")

zipline.api.order\_value( _self_, _asset_, _value_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_value "Permalink to this definition")

Place an order for a fixed amount of money.

Equivalent to `order(asset, value / data.current(asset, 'price'))`.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to be ordered.

- **value** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Amount of value of `asset` to be transacted. The number of shares
bought or sold will be equal to `value / current_price`.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Notes

See [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order") for more information about
`limit_price`, `stop_price`, and `style`

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order"), [`zipline.api.order_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_percent "zipline.api.order_percent")

zipline.api.order\_percent( _self_, _asset_, _percent_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_percent "Permalink to this definition")

Place an order in the specified asset corresponding to the given
percent of the current portfolio value.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **percent** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The percentage of the portfolio value to allocate to `asset`.
This is specified as a decimal, for example: 0.50 means 50%.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Notes

See [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order") for more information about
`limit_price`, `stop_price`, and `style`

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order"), [`zipline.api.order_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_value "zipline.api.order_value")

zipline.api.order\_target( _self_, _asset_, _target_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target "Permalink to this definition")

Place an order to adjust a position to a target number of shares. If
the position doesn’t already exist, this is equivalent to placing a new
order. If the position does exist, this is equivalent to placing an
order for the difference between the target number of shares and the
current number of shares.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **target** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The desired number of shares of `asset`.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Notes

`order_target` does not take into account any open orders. For
example:

```
order_target(sid(0), 10)
order_target(sid(0), 10)

```

This code will result in 20 shares of `sid(0)` because the first
call to `order_target` will not have been filled when the second
`order_target` call is made.

See [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order") for more information about
`limit_price`, `stop_price`, and `style`

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order"), [`zipline.api.order_target_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_percent "zipline.api.order_target_percent"), [`zipline.api.order_target_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_value "zipline.api.order_target_value")

zipline.api.order\_target\_value( _self_, _asset_, _target_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_value "Permalink to this definition")

Place an order to adjust a position to a target value. If
the position doesn’t already exist, this is equivalent to placing a new
order. If the position does exist, this is equivalent to placing an
order for the difference between the target value and the
current value.
If the Asset being ordered is a Future, the ‘target value’ calculated
is actually the target exposure, as Futures have no ‘value’.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **target** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The desired total value of `asset`.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Notes

`order_target_value` does not take into account any open orders. For
example:

```
order_target_value(sid(0), 10)
order_target_value(sid(0), 10)

```

This code will result in 20 dollars of `sid(0)` because the first
call to `order_target_value` will not have been filled when the
second `order_target_value` call is made.

See [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order") for more information about
`limit_price`, `stop_price`, and `style`

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order"), [`zipline.api.order_target()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target "zipline.api.order_target"), [`zipline.api.order_target_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_percent "zipline.api.order_target_percent")

zipline.api.order\_target\_percent( _self_, _asset_, _target_, _limit\_price=None_, _stop\_price=None_, _style=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_percent "Permalink to this definition")

Place an order to adjust a position to a target percent of the
current portfolio value. If the position doesn’t already exist, this is
equivalent to placing a new order. If the position does exist, this is
equivalent to placing an order for the difference between the target
percent and the current percent.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **target** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The desired percentage of the portfolio value to allocate to
`asset`. This is specified as a decimal, for example:
0.50 means 50%.

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The limit price for the order.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The stop price for the order.

- **style** ( [_ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.


Returns:

**order\_id** – The unique identifier for this order.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Notes

`order_target_value` does not take into account any open orders. For
example:

```
order_target_percent(sid(0), 10)
order_target_percent(sid(0), 10)

```

This code will result in 20% of the portfolio being allocated to sid(0)
because the first call to `order_target_percent` will not have been
filled when the second `order_target_percent` call is made.

See [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order") for more information about
`limit_price`, `stop_price`, and `style`

See also

[`zipline.finance.execution.ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle"), [`zipline.api.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order"), [`zipline.api.order_target()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target "zipline.api.order_target"), [`zipline.api.order_target_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_value "zipline.api.order_target_value")

_class_ zipline.finance.execution.ExecutionStyle [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#ExecutionStyle) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "Permalink to this definition")

Base class for order execution styles.

_property_ exchange [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.exchange "Permalink to this definition")

The exchange to which this order should be routed.

_abstract_ get\_limit\_price( _is\_buy_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#ExecutionStyle.get_limit_price) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.get_limit_price "Permalink to this definition")

Get the limit price for this order.
Returns either None or a numerical value >= 0.

_abstract_ get\_stop\_price( _is\_buy_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#ExecutionStyle.get_stop_price) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.get_stop_price "Permalink to this definition")

Get the stop price for this order.
Returns either None or a numerical value >= 0.

_class_ zipline.finance.execution.MarketOrder( _exchange=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#MarketOrder) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.MarketOrder "Permalink to this definition")

Execution style for orders to be filled at current market price.

This is the default for orders placed with [`order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order "zipline.api.order").

_class_ zipline.finance.execution.LimitOrder( _limit\_price_, _asset=None_, _exchange=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#LimitOrder) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.LimitOrder "Permalink to this definition")

Execution style for orders to be filled at a price equal to or better than
a specified limit price.

Parameters:

**limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Maximum price for buys, or minimum price for sells, at which the order
should be filled.

_class_ zipline.finance.execution.StopOrder( _stop\_price_, _asset=None_, _exchange=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#StopOrder) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.StopOrder "Permalink to this definition")

Execution style representing a market order to be placed if market price
reaches a threshold.

Parameters:

**stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Price threshold at which the order should be placed. For sells, the
order will be placed if market price falls below this value. For buys,
the order will be placed if market price rises above this value.

_class_ zipline.finance.execution.StopLimitOrder( _limit\_price_, _stop\_price_, _asset=None_, _exchange=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/execution.html#StopLimitOrder) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.StopLimitOrder "Permalink to this definition")

Execution style representing a limit order to be placed if market price
reaches a threshold.

Parameters:

- **limit\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Maximum price for buys, or minimum price for sells, at which the order
should be filled, if placed.

- **stop\_price** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Price threshold at which the order should be placed. For sells, the
order will be placed if market price falls below this value. For buys,
the order will be placed if market price rises above this value.


zipline.api.get\_order( _self_, _order\_id_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_order "Permalink to this definition")

Lookup an order based on the order id returned from one of the
order functions.

Parameters:

**order\_id** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The unique identifier for the order.

Returns:

**order** – The order object.

Return type:

Order

zipline.api.get\_open\_orders( _self_, _asset=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_open_orders "Permalink to this definition")

Retrieve all of the current open orders.

Parameters:

**asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – If passed and not None, return only the open orders for the given
asset instead of all open orders.

Returns:

**open\_orders** – If no asset is passed this will return a dict mapping Assets
to a list containing all the open orders for the asset.
If an asset is passed then this will return a list of the open
orders for this asset.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[ [list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[Order\]\] or [list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[Order\]

zipline.api.cancel\_order( _self_, _order\_param_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.cancel_order "Permalink to this definition")

Cancel an open order.

Parameters:

**order\_param** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _Order_) – The order\_id or order object to cancel.

#### Order Cancellation Policies [\#](https://zipline.ml4trading.io/api-reference.html\#order-cancellation-policies "Permalink to this heading")

zipline.api.set\_cancel\_policy( _self_, _cancel\_policy_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_cancel_policy "Permalink to this definition")

Sets the order cancellation policy for the simulation.

Parameters:

**cancel\_policy** ( [_CancelPolicy_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.cancel_policy.CancelPolicy "zipline.finance.cancel_policy.CancelPolicy")) – The cancellation policy to use.

See also

[`zipline.api.EODCancel`](https://zipline.ml4trading.io/api-reference.html#zipline.api.EODCancel "zipline.api.EODCancel"), [`zipline.api.NeverCancel`](https://zipline.ml4trading.io/api-reference.html#zipline.api.NeverCancel "zipline.api.NeverCancel")

_class_ zipline.finance.cancel\_policy.CancelPolicy [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/cancel_policy.html#CancelPolicy) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.cancel_policy.CancelPolicy "Permalink to this definition")

Abstract cancellation policy interface.

_abstract_ should\_cancel( _event_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/cancel_policy.html#CancelPolicy.should_cancel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.cancel_policy.CancelPolicy.should_cancel "Permalink to this definition")

Should all open orders be cancelled?

Parameters:

**event** ( _enum-value_) –

An event type, one of:

- `zipline.gens.sim_engine.BAR`

- `zipline.gens.sim_engine.DAY_START`

- `zipline.gens.sim_engine.DAY_END`

- `zipline.gens.sim_engine.MINUTE_END`


Returns:

**should\_cancel** – Should all open orders be cancelled?

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")

zipline.api.EODCancel( _warn\_on\_cancel=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/cancel_policy.html#EODCancel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.EODCancel "Permalink to this definition")

This policy cancels open orders at the end of the day. For now,
Zipline will only apply this policy to minutely simulations.

Parameters:

**warn\_on\_cancel** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should a warning be raised if this causes an order to be cancelled?

zipline.api.NeverCancel() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/cancel_policy.html#NeverCancel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.NeverCancel "Permalink to this definition")

Orders are never automatically canceled.

### Assets [\#](https://zipline.ml4trading.io/api-reference.html\#assets "Permalink to this heading")

zipline.api.symbol( _self_, _symbol\_str_, _country\_code=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.symbol "Permalink to this definition")

Lookup an Equity by its ticker symbol.

Parameters:

- **symbol\_str** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ticker symbol for the equity to lookup.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_ _,_ _optional_) – A country to limit symbol searches to.


Returns:

**equity** – The equity that held the ticker symbol on the current
symbol lookup date.

Return type:

[zipline.assets.Equity](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity "zipline.assets.Equity")

Raises:

**SymbolNotFound** – Raised when the symbols was not held on the current lookup date.

See also

[`zipline.api.set_symbol_lookup_date()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_symbol_lookup_date "zipline.api.set_symbol_lookup_date")

zipline.api.symbols( _self_, _\*args_, _\*\*kwargs_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.symbols "Permalink to this definition")

Lookup multuple Equities as a list.

Parameters:

- **\*args** ( _iterable_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_) – The ticker symbols to lookup.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_ _,_ _optional_) – A country to limit symbol searches to.


Returns:

**equities** – The equities that held the given ticker symbols on the current
symbol lookup date.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [zipline.assets.Equity](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity "zipline.assets.Equity")\]

Raises:

**SymbolNotFound** – Raised when one of the symbols was not held on the current
lookup date.

See also

[`zipline.api.set_symbol_lookup_date()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_symbol_lookup_date "zipline.api.set_symbol_lookup_date")

zipline.api.future\_symbol( _self_, _symbol_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.future_symbol "Permalink to this definition")

Lookup a futures contract with a given symbol.

Parameters:

**symbol** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The symbol of the desired contract.

Returns:

**future** – The future that trades with the name `symbol`.

Return type:

[zipline.assets.Future](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future "zipline.assets.Future")

Raises:

**SymbolNotFound** – Raised when no contract named ‘symbol’ is found.

zipline.api.set\_symbol\_lookup\_date( _self_, _dt_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_symbol_lookup_date "Permalink to this definition")

Set the date for which symbols will be resolved to their assets
(symbols may map to different firms or underlying assets at
different times)

Parameters:

**dt** ( _datetime_) – The new symbol lookup date.

zipline.api.sid( _self_, _sid_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.sid "Permalink to this definition")

Lookup an Asset by its unique asset identifier.

Parameters:

**sid** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The unique integer that identifies an asset.

Returns:

**asset** – The asset with the given `sid`.

Return type:

[zipline.assets.Asset](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")

Raises:

**SidsNotFound** – When a requested `sid` does not map to any asset.

### Trading Controls [\#](https://zipline.ml4trading.io/api-reference.html\#trading-controls "Permalink to this heading")

Zipline provides trading controls to ensure that the algorithm
performs as expected. The functions help protect the algorithm from
undesirable consequences of unintended behavior,
especially when trading with real money.

zipline.api.set\_do\_not\_order\_list( _self_, _restricted\_list_, _on\_error='fail'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_do_not_order_list "Permalink to this definition")

Set a restriction on which assets can be ordered.

Parameters:

**restricted\_list** ( _container_ _\[_ [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _\]_ _,_ _SecurityList_) – The assets that cannot be ordered.

zipline.api.set\_long\_only( _self_, _on\_error='fail'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_long_only "Permalink to this definition")

Set a rule specifying that this algorithm cannot take short
positions.

zipline.api.set\_max\_leverage( _self_, _max\_leverage_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_leverage "Permalink to this definition")

Set a limit on the maximum leverage of the algorithm.

Parameters:

**max\_leverage** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The maximum leverage for the algorithm. If not provided there will
be no maximum.

zipline.api.set\_max\_order\_count( _self_, _max\_count_, _on\_error='fail'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_order_count "Permalink to this definition")

Set a limit on the number of orders that can be placed in a single
day.

Parameters:

**max\_count** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The maximum number of orders that can be placed on any single day.

zipline.api.set\_max\_order\_size( _self_, _asset=None_, _max\_shares=None_, _max\_notional=None_, _on\_error='fail'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_order_size "Permalink to this definition")

Set a limit on the number of shares and/or dollar value of any single
order placed for sid. Limits are treated as absolute values and are
enforced at the time that the algo attempts to place an order for sid.

If an algorithm attempts to place an order that would result in
exceeding one of these limits, raise a TradingControlException.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _,_ _optional_) – If provided, this sets the guard only on positions in the given
asset.

- **max\_shares** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – The maximum number of shares that can be ordered at one time.

- **max\_notional** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The maximum value that can be ordered at one time.


zipline.api.set\_max\_position\_size( _self_, _asset=None_, _max\_shares=None_, _max\_notional=None_, _on\_error='fail'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_position_size "Permalink to this definition")

Set a limit on the number of shares and/or dollar value held for the
given sid. Limits are treated as absolute values and are enforced at
the time that the algo attempts to place an order for sid. This means
that it’s possible to end up with more than the max number of shares
due to splits/dividends, and more than the max notional due to price
improvement.

If an algorithm attempts to place an order that would result in
increasing the absolute value of shares/dollar value exceeding one of
these limits, raise a TradingControlException.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _,_ _optional_) – If provided, this sets the guard only on positions in the given
asset.

- **max\_shares** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – The maximum number of shares to hold for an asset.

- **max\_notional** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The maximum value to hold for an asset.


### Simulation Parameters [\#](https://zipline.ml4trading.io/api-reference.html\#simulation-parameters "Permalink to this heading")

zipline.api.set\_benchmark( _self_, _benchmark_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_benchmark "Permalink to this definition")

Set the benchmark asset.

Parameters:

**benchmark** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to set as the new benchmark.

Notes

Any dividends payed out for that new benchmark asset will be
automatically reinvested.

#### Commission Models [\#](https://zipline.ml4trading.io/api-reference.html\#commission-models "Permalink to this heading")

zipline.api.set\_commission( _self_, _us\_equities=None_, _us\_futures=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_commission "Permalink to this definition")

Sets the commission models for the simulation.

Parameters:

- **us\_equities** ( _EquityCommissionModel_) – The commission model to use for trading US equities.

- **us\_futures** ( _FutureCommissionModel_) – The commission model to use for trading US futures.


Notes

This function can only be called during
`initialize()`.

See also

[`zipline.finance.commission.PerShare`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerShare "zipline.finance.commission.PerShare"), [`zipline.finance.commission.PerTrade`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerTrade "zipline.finance.commission.PerTrade"), [`zipline.finance.commission.PerDollar`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerDollar "zipline.finance.commission.PerDollar")

_class_ zipline.finance.commission.CommissionModel [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/commission.html#CommissionModel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel "Permalink to this definition")

Abstract base class for commission models.

Commission models are responsible for accepting order/transaction pairs and
calculating how much commission should be charged to an algorithm’s account
on each transaction.

To implement a new commission model, create a subclass of
[`CommissionModel`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel "zipline.finance.commission.CommissionModel") and implement
[`calculate()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel.calculate "zipline.finance.commission.CommissionModel.calculate").

_abstract_ calculate( _order_, _transaction_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/commission.html#CommissionModel.calculate) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel.calculate "Permalink to this definition")

Calculate the amount of commission to charge on `order` as a result
of `transaction`.

Parameters:

- **order** ( _zipline.finance.order.Order_) –

The order being processed.

The `commission` field of `order` is a float indicating the
amount of commission already charged on this order.

- **transaction** ( _zipline.finance.transaction.Transaction_) – The transaction being processed. A single order may generate
multiple transactions if there isn’t enough volume in a given bar
to fill the full amount requested in the order.


Returns:

**amount\_charged** – The additional commission, in dollars, that we should attribute to
this order.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

_class_ zipline.finance.commission.PerShare( _cost=0.001_, _min\_trade\_cost=0.0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/commission.html#PerShare) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerShare "Permalink to this definition")

Calculates a commission for a transaction based on a per share cost with
an optional minimum cost per trade.

Parameters:

- **cost** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The amount of commissions paid per share traded. Default is one tenth
of a cent per share.

- **min\_trade\_cost** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The minimum amount of commissions paid per trade. Default is no
minimum.


Notes

This is zipline’s default commission model for equities.

_class_ zipline.finance.commission.PerTrade( _cost=0.0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/commission.html#PerTrade) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerTrade "Permalink to this definition")

Calculates a commission for a transaction based on a per trade cost.

For orders that require multiple fills, the full commission is charged to
the first fill.

Parameters:

**cost** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The flat amount of commissions paid per equity trade.

_class_ zipline.finance.commission.PerDollar( _cost=0.0015_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/commission.html#PerDollar) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerDollar "Permalink to this definition")

Model commissions by applying a fixed cost per dollar transacted.

Parameters:

**cost** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – The flat amount of commissions paid per dollar of equities
traded. Default is a commission of $0.0015 per dollar transacted.

#### Slippage Models [\#](https://zipline.ml4trading.io/api-reference.html\#slippage-models "Permalink to this heading")

zipline.api.set\_slippage( _self_, _us\_equities=None_, _us\_futures=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_slippage "Permalink to this definition")

Set the slippage models for the simulation.

Parameters:

- **us\_equities** ( _EquitySlippageModel_) – The slippage model to use for trading US equities.

- **us\_futures** ( _FutureSlippageModel_) – The slippage model to use for trading US futures.


Notes

This function can only be called during
`initialize()`.

See also

[`zipline.finance.slippage.SlippageModel`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel "zipline.finance.slippage.SlippageModel")

_class_ zipline.finance.slippage.SlippageModel [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/slippage.html#SlippageModel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel "Permalink to this definition")

Abstract base class for slippage models.

Slippage models are responsible for the rates and prices at which orders
fill during a simulation.

To implement a new slippage model, create a subclass of
[`SlippageModel`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel "zipline.finance.slippage.SlippageModel") and implement
[`process_order()`](https://zipline.ml4trading.io/api-reference.html#id0 "zipline.finance.slippage.SlippageModel.process_order").

process\_order( _data_, _order_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/slippage.html#SlippageModel.process_order) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel.process_order "Permalink to this definition")volume\_for\_bar [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel.volume_for_bar "Permalink to this definition")

Number of shares that have already been filled for the
currently-filling asset in the current minute. This attribute is
maintained automatically by the base class. It can be used by
subclasses to keep track of the total amount filled if there are
multiple open orders for a single asset.

Type:

[int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")

Notes

Subclasses that define their own constructors should call
`super(<subclass name>, self).__init__()` before performing other
initialization.

_abstract_ process\_order( _data_, _order_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/slippage.html#SlippageModel.process_order) [#](https://zipline.ml4trading.io/api-reference.html#id0 "Permalink to this definition")

Compute the number of shares and price to fill for `order` in the
current minute.

Parameters:

- **data** ( [_zipline.protocol.BarData_](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "zipline.protocol.BarData")) – The data for the given bar.

- **order** ( _zipline.finance.order.Order_) – The order to simulate.


Returns:

- **execution\_price** ( _float_) – The price of the fill.

- **execution\_volume** ( _int_) – The number of shares that should be filled. Must be between `0`
and `order.amount - order.filled`. If the amount filled is less
than the amount remaining, `order` will remain open and will be
passed again to this method in the next minute.


Raises:

**zipline.finance.slippage.LiquidityExceeded** – May be raised if no more orders should be processed for the current
asset during the current bar.

Notes

Before this method is called, [`volume_for_bar`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel.volume_for_bar "zipline.finance.slippage.SlippageModel.volume_for_bar") will be set to the
number of shares that have already been filled for `order.asset` in
the current minute.

[`process_order()`](https://zipline.ml4trading.io/api-reference.html#id0 "zipline.finance.slippage.SlippageModel.process_order") is not called by the base class on bars for which
there was no historical volume.

_class_ zipline.finance.slippage.FixedSlippage( _spread=0.0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/slippage.html#FixedSlippage) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.FixedSlippage "Permalink to this definition")

Simple model assuming a fixed-size spread for all assets.

Parameters:

**spread** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Size of the assumed spread for all assets.
Orders to buy will be filled at `close + (spread / 2)`.
Orders to sell will be filled at `close - (spread / 2)`.

Notes

This model does not impose limits on the size of fills. An order for an
asset will always be filled as soon as any trading activity occurs in the
order’s asset, even if the size of the order is greater than the historical
volume.

_class_ zipline.finance.slippage.VolumeShareSlippage( _volume\_limit=0.025_, _price\_impact=0.1_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/slippage.html#VolumeShareSlippage) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.VolumeShareSlippage "Permalink to this definition")

Model slippage as a quadratic function of percentage of historical volume.

Orders to buy will be filled at:

```
price * (1 + price_impact * (volume_share ** 2))

```

Orders to sell will be filled at:

```
price * (1 - price_impact * (volume_share ** 2))

```

where `price` is the close price for the bar, and `volume_share` is the
percentage of minutely volume filled, up to a max of `volume_limit`.

Parameters:

- **volume\_limit** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Maximum percent of historical volume that can fill in each bar. 0.5
means 50% of historical volume. 1.0 means 100%. Default is 0.025 (i.e.,
2.5%).

- **price\_impact** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Scaling coefficient for price impact. Larger values will result in more
simulated price impact. Smaller values will result in less simulated
price impact. Default is 0.1.


### Pipeline [\#](https://zipline.ml4trading.io/api-reference.html\#pipeline "Permalink to this heading")

For more information, see [Pipeline API](https://zipline.ml4trading.io/api-reference.html#pipeline-api)

zipline.api.attach\_pipeline( _self_, _pipeline_, _name_, _chunks=None_, _eager=True_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.attach_pipeline "Permalink to this definition")

Register a pipeline to be computed at the start of each day.

Parameters:

- **pipeline** ( [_Pipeline_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")) – The pipeline to have computed.

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the pipeline.

- **chunks** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _or_ _iterator_ _,_ _optional_) – The number of days to compute pipeline results for. Increasing
this number will make it longer to get the first results but
may improve the total runtime of the simulation. If an iterator
is passed, we will run in chunks based on values of the iterator.
Default is True.

- **eager** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Whether or not to compute this pipeline prior to
before\_trading\_start.


Returns:

**pipeline** – Returns the pipeline that was attached unchanged.

Return type:

[Pipeline](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")

See also

[`zipline.api.pipeline_output()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.pipeline_output "zipline.api.pipeline_output")

zipline.api.pipeline\_output( _self_, _name_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.pipeline_output "Permalink to this definition")

Get results of the pipeline attached by with name `name`.

Parameters:

**name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – Name of the pipeline from which to fetch results.

Returns:

**results** – DataFrame containing the results of the requested pipeline for
the current simulation date.

Return type:

pd.DataFrame

Raises:

**NoSuchPipeline** – Raised when no pipeline with the name name has been registered.

See also

[`zipline.api.attach_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.attach_pipeline "zipline.api.attach_pipeline"), [`zipline.pipeline.engine.PipelineEngine.run_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_pipeline "zipline.pipeline.engine.PipelineEngine.run_pipeline")

### Miscellaneous [\#](https://zipline.ml4trading.io/api-reference.html\#miscellaneous "Permalink to this heading")

zipline.api.record( _self_, _\*args_, _\*\*kwargs_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.record "Permalink to this definition")

Track and record values each day.

Parameters:

**\*\*kwargs** – The names and values to record.

Notes

These values will appear in the performance packets and the performance
dataframe passed to `analyze` and returned from
[`run_algorithm()`](https://zipline.ml4trading.io/api-reference.html#zipline.run_algorithm "zipline.run_algorithm").

zipline.api.get\_environment( _self_, _field='platform'_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_environment "Permalink to this definition")

Query the execution environment.

Parameters:

- **field** ( _{'platform'_ _,_ _'arena'_ _,_ _'data\_frequency'_ _,_ _'start'_ _,_ _'end'_ _,_) –

- **'capital\_base'** –

- **'platform'** –

- **'\*'}** –

- **meanings** ( _The field to query. The options have the following_) –

- **arena** ( _-_) – The arena from the simulation parameters. This will normally
be `'backtest'` but some systems may use this distinguish
live trading from backtesting.

- **data\_frequency** ( _-_) – data\_frequency tells the algorithm if it is running with
daily data or minute data.

- **start** ( _-_) – The start date for the simulation.

- **end** ( _-_) – The end date for the simulation.

- **capital\_base** ( _-_) – The starting capital for the simulation.

- **-platform** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The platform that the code is running on. By default, this
will be the string ‘zipline’. This can allow algorithms to
know if they are running on the Quantopian platform instead.

- **\*** ( _-_) – Returns all the fields in a dictionary.


Returns:

**val** – The value for the field queried. See above for more information.

Return type:

any

Raises:

[**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.11)") – Raised when `field` is not a valid option.

zipline.api.fetch\_csv( _self_, _url_, _pre\_func=None_, _post\_func=None_, _date\_column='date'_, _date\_format=None_, _timezone='UTC'_, _symbol=None_, _mask=True_, _symbol\_column=None_, _special\_params\_checker=None_, _country\_code=None_, _\*\*kwargs_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.api.fetch_csv "Permalink to this definition")

Fetch a csv from a remote url and register the data so that it is
queryable from the `data` object.

Parameters:

- **url** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The url of the csv file to load.

- **pre\_func** ( _callable_ _\[_ _pd.DataFrame -> pd.DataFrame_ _\]_ _,_ _optional_) – A callback to allow preprocessing the raw data returned from
fetch\_csv before dates are paresed or symbols are mapped.

- **post\_func** ( _callable_ _\[_ _pd.DataFrame -> pd.DataFrame_ _\]_ _,_ _optional_) – A callback to allow postprocessing of the data after dates and
symbols have been mapped.

- **date\_column** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the column in the preprocessed dataframe containing
datetime information to map the data.

- **date\_format** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The format of the dates in the `date_column`. If not provided
`fetch_csv` will attempt to infer the format. For information
about the format of this string, see [`pandas.read_csv()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html#pandas.read_csv "(in pandas v2.0.3)").

- **timezone** ( _tzinfo_ _or_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The timezone for the datetime in the `date_column`.

- **symbol** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – If the data is about a new asset or index then this string will
be the name used to identify the values in `data`. For example,
one may use `fetch_csv` to load data for VIX, then this field
could be the string `'VIX'`.

- **mask** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Drop any rows which cannot be symbol mapped.

- **symbol\_column** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – If the data is attaching some new attribute to each asset then this
argument is the name of the column in the preprocessed dataframe
containing the symbols. This will be used along with the date
information to map the sids in the asset finder.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – Country code to use to disambiguate symbol lookups.

- **\*\*kwargs** – Forwarded to [`pandas.read_csv()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html#pandas.read_csv "(in pandas v2.0.3)").


Returns:

**csv\_data\_source** – A requests source that will pull data from the url specified.

Return type:

zipline.sources.requests\_csv.PandasRequestsCSV

## Blotters [\#](https://zipline.ml4trading.io/api-reference.html\#blotters "Permalink to this heading")

A [blotter](https://www.investopedia.com/terms/b/blotter.asp) documents trades and their details over a period of time, typically one trading day. Trade details include
such things as the time, price, order size, and whether it was a buy or sell order. It is is usually created by a
trading software that records the trades made through a data feed.

_class_ zipline.finance.blotter.blotter.Blotter( _cancel\_policy=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter "Permalink to this definition")batch\_order( _order\_arg\_lists_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.batch_order) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.batch_order "Permalink to this definition")

Place a batch of orders.

Parameters:

**order\_arg\_lists** ( _iterable_ _\[_ [_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.11)") _\]_) – Tuples of args that order expects.

Returns:

**order\_ids** – The unique identifier (or None) for each of the orders placed
(or not placed).

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None\]

Notes

This is required for Blotter subclasses to be able to place a batch
of orders, instead of being passed the order requests one at a time.

_abstract_ cancel( _order\_id_, _relay\_status=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.cancel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.cancel "Permalink to this definition")

Cancel a single order

Parameters:

- **order\_id** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The id of the order

- **relay\_status** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether or not to record the status of the order


_abstract_ cancel\_all\_orders\_for\_asset( _asset_, _warn=False_, _relay\_status=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.cancel_all_orders_for_asset) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.cancel_all_orders_for_asset "Permalink to this definition")

Cancel all open orders for a given asset.

_abstract_ get\_transactions( _bar\_data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.get_transactions) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.get_transactions "Permalink to this definition")

Creates a list of transactions based on the current open orders,
slippage model, and commission model.

Parameters:

**bar\_data** ( [_zipline.\_protocol.BarData_](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "zipline._protocol.BarData")) –

Notes

This method book-keeps the blotter’s open\_orders dictionary, so that

it is accurate by the time we’re done processing open orders.

Returns:

- **transactions\_list** ( _List_) – transactions\_list: list of transactions resulting from the current
open orders. If there were no open orders, an empty list is
returned.

- **commissions\_list** ( _List_) – commissions\_list: list of commissions resulting from filling the
open orders. A commission is an object with “asset” and “cost”
parameters.

- **closed\_orders** ( _List_) – closed\_orders: list of all the orders that have filled.


_abstract_ hold( _order\_id_, _reason=''_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.hold) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.hold "Permalink to this definition")

Mark the order with order\_id as ‘held’. Held is functionally similar
to ‘open’. When a fill (full or partial) arrives, the status
will automatically change back to open/filled as necessary.

_abstract_ order( _asset_, _amount_, _style_, _order\_id=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.order) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.order "Permalink to this definition")

Place an order.

Parameters:

- **asset** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **amount** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The amount of shares to order. If `amount` is positive, this is
the number of shares to buy or cover. If `amount` is negative,
this is the number of shares to sell or short.

- **style** ( [_zipline.finance.execution.ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.

- **order\_id** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The unique identifier for this order.


Returns:

**order\_id** – The unique identifier for this order, or None if no order was
placed.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None

Notes

amount > 0 : Buy/Cover
amount < 0 : Sell/Short
Market order : order(asset, amount)
Limit order : order(asset, amount, style=LimitOrder(limit\_price))
Stop order : order(asset, amount, style=StopOrder(stop\_price))
StopLimit order : order(asset, amount,
style=StopLimitOrder(limit\_price, stop\_price))

_abstract_ process\_splits( _splits_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.process_splits) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.process_splits "Permalink to this definition")

Processes a list of splits by modifying any open orders as needed.

Parameters:

**splits** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")) – A list of splits. Each split is a tuple of (asset, ratio).

Return type:

None

_abstract_ prune\_orders( _closed\_orders_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.prune_orders) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.prune_orders "Permalink to this definition")

Removes all given orders from the blotter’s open\_orders list.

Parameters:

**closed\_orders** ( _iterable_ _of_ _orders that are closed._) –

Return type:

None

_abstract_ reject( _order\_id_, _reason=''_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/blotter.html#Blotter.reject) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.reject "Permalink to this definition")

Mark the given order as ‘rejected’, which is functionally similar to
cancelled. The distinction is that rejections are involuntary (and
usually include a message from a broker indicating why the order was
rejected) while cancels are typically user-driven.

_class_ zipline.finance.blotter.SimulationBlotter( _equity\_slippage=None_, _future\_slippage=None_, _equity\_commission=None_, _future\_commission=None_, _cancel\_policy=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter "Permalink to this definition")cancel( _order\_id_, _relay\_status=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.cancel) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.cancel "Permalink to this definition")

Cancel a single order

Parameters:

- **order\_id** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The id of the order

- **relay\_status** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether or not to record the status of the order


cancel\_all\_orders\_for\_asset( _asset_, _warn=False_, _relay\_status=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.cancel_all_orders_for_asset) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.cancel_all_orders_for_asset "Permalink to this definition")

Cancel all open orders for a given asset.

get\_transactions( _bar\_data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.get_transactions) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.get_transactions "Permalink to this definition")

Creates a list of transactions based on the current open orders,
slippage model, and commission model.

Parameters:

**bar\_data** ( [_zipline.\_protocol.BarData_](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData "zipline._protocol.BarData")) –

Notes

This method book-keeps the blotter’s open\_orders dictionary, so that

it is accurate by the time we’re done processing open orders.

Returns:

- **transactions\_list** ( _List_) – transactions\_list: list of transactions resulting from the current
open orders. If there were no open orders, an empty list is
returned.

- **commissions\_list** ( _List_) – commissions\_list: list of commissions resulting from filling the
open orders. A commission is an object with “asset” and “cost”
parameters.

- **closed\_orders** ( _List_) – closed\_orders: list of all the orders that have filled.


hold( _order\_id_, _reason=''_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.hold) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.hold "Permalink to this definition")

Mark the order with order\_id as ‘held’. Held is functionally similar
to ‘open’. When a fill (full or partial) arrives, the status
will automatically change back to open/filled as necessary.

order( _asset_, _amount_, _style_, _order\_id=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.order) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.order "Permalink to this definition")

Place an order.

Parameters:

- **asset** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset that this order is for.

- **amount** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The amount of shares to order. If `amount` is positive, this is
the number of shares to buy or cover. If `amount` is negative,
this is the number of shares to sell or short.

- **style** ( [_zipline.finance.execution.ExecutionStyle_](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle "zipline.finance.execution.ExecutionStyle")) – The execution style for the order.

- **order\_id** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The unique identifier for this order.


Returns:

**order\_id** – The unique identifier for this order, or None if no order was
placed.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None

Notes

amount > 0 :: Buy/Cover
amount < 0 :: Sell/Short
Market order: order(asset, amount)
Limit order: order(asset, amount, style=LimitOrder(limit\_price))
Stop order: order(asset, amount, style=StopOrder(stop\_price))
StopLimit order: order(asset, amount, style=StopLimitOrder(limit\_price,
stop\_price))

process\_splits( _splits_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.process_splits) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.process_splits "Permalink to this definition")

Processes a list of splits by modifying any open orders as needed.

Parameters:

**splits** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")) – A list of splits. Each split is a tuple of (asset, ratio).

Return type:

None

prune\_orders( _closed\_orders_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.prune_orders) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.prune_orders "Permalink to this definition")

Removes all given orders from the blotter’s open\_orders list.

Parameters:

**closed\_orders** ( _iterable_ _of_ _orders that are closed._) –

Return type:

None

reject( _order\_id_, _reason=''_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/blotter/simulation_blotter.html#SimulationBlotter.reject) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.reject "Permalink to this definition")

Mark the given order as ‘rejected’, which is functionally similar to
cancelled. The distinction is that rejections are involuntary (and
usually include a message from a broker indicating why the order was
rejected) while cancels are typically user-driven.

## Pipeline API [\#](https://zipline.ml4trading.io/api-reference.html\#pipeline-api "Permalink to this heading")

A [`Pipeline`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline") enables faster and more memory-efficient execution by optimizing the computation
of factors during a backtest.

_class_ zipline.pipeline.Pipeline( _columns=None_, _screen=None_, _domain=GENERIC_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "Permalink to this definition")

A Pipeline object represents a collection of named expressions to be
compiled and executed by a PipelineEngine.

A Pipeline has two important attributes: ‘columns’, a dictionary of named
[`Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term") instances, and ‘screen’, a
[`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") representing criteria for
including an asset in the results of a Pipeline.

To compute a pipeline in the context of a TradingAlgorithm, users must call
`attach_pipeline` in their `initialize` function to register that the
pipeline should be computed each trading day. The most recent outputs of an
attached pipeline can be retrieved by calling `pipeline_output` from
`handle_data`, `before_trading_start`, or a scheduled function.

Parameters:

- **columns** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _,_ _optional_) – Initial columns.

- **screen** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – Initial screen.


add( _term_, _name_, _overwrite=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.add) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.add "Permalink to this definition")

Add a column.

The results of computing `term` will show up as a column in the
DataFrame produced by running this pipeline.

Parameters:

- **column** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – A Filter, Factor, or Classifier to add to the pipeline.

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – Name of the column to add.

- **overwrite** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether to overwrite the existing entry if we already have a column
named name.


domain( _default_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.domain) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.domain "Permalink to this definition")

Get the domain for this pipeline.

- If an explicit domain was provided at construction time, use it.

- Otherwise, infer a domain from the registered columns.

- If no domain can be inferred, return `default`.


Parameters:

**default** ( _zipline.pipeline.domain.Domain_) – Domain to use if no domain can be inferred from this pipeline by
itself.

Returns:

**domain** – The domain for the pipeline.

Return type:

zipline.pipeline.domain.Domain

Raises:

- **AmbiguousDomain** –

- [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.11)") – If the terms in `self` conflict with self.\_domain.


remove( _name_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.remove) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.remove "Permalink to this definition")

Remove a column.

Parameters:

**name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the column to remove.

Raises:

[**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError "(in Python v3.11)") – If name is not in self.columns.

Returns:

**removed** – The removed term.

Return type:

[zipline.pipeline.Term](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")

set\_screen( _screen_, _overwrite=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.set_screen) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.set_screen "Permalink to this definition")

Set a screen on this Pipeline.

Parameters:

- **filter** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")) – The filter to apply as a screen.

- **overwrite** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether to overwrite any existing screen. If overwrite is False
and self.screen is not None, we raise an error.


show\_graph( _format='svg'_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.show_graph) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.show_graph "Permalink to this definition")

Render this Pipeline as a DAG.

Parameters:

**format** ( _{'svg'_ _,_ _'png'_ _,_ _'jpeg'}_) – Image format to render with. Default is ‘svg’.

to\_execution\_plan( _domain_, _default\_screen_, _start\_date_, _end\_date_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.to_execution_plan) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.to_execution_plan "Permalink to this definition")

Compile into an ExecutionPlan.

Parameters:

- **domain** ( _zipline.pipeline.domain.Domain_) – Domain on which the pipeline will be executed.

- **default\_screen** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – Term to use as a screen if self.screen is None.

- **all\_dates** ( _pd.DatetimeIndex_) – A calendar of dates to use to calculate starts and ends for each
term.

- **start\_date** ( _pd.Timestamp_) – The first date of requested output.

- **end\_date** ( _pd.Timestamp_) – The last date of requested output.


Returns:

**graph** – Graph encoding term dependencies, including metadata about extra
row requirements.

Return type:

zipline.pipeline.graph.ExecutionPlan

to\_simple\_graph( _default\_screen_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/pipeline.html#Pipeline.to_simple_graph) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.to_simple_graph "Permalink to this definition")

Compile into a simple TermGraph with no extra row metadata.

Parameters:

**default\_screen** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – Term to use as a screen if self.screen is None.

Returns:

**graph** – Graph encoding term dependencies.

Return type:

zipline.pipeline.graph.TermGraph

_property_ columns [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.columns "Permalink to this definition")

The output columns of this pipeline.

Returns:

**columns** – Map from column name to expression computing that column’s output.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[ [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)"), zipline.pipeline.ComputableTerm\]

_property_ screen [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.screen "Permalink to this definition")

The screen of this pipeline.

Returns:

**screen** – Term defining the screen for this pipeline. If `screen` is a
filter, rows that do not pass the filter (i.e., rows for which the
filter computed `False`) will be dropped from the output of this
pipeline before returning results.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") or None

Notes

Setting a screen on a Pipeline does not change the values produced for
any rows: it only affects whether a given row is returned. Computing a
pipeline with a screen is logically equivalent to computing the
pipeline without the screen and then, as a post-processing-step,
filtering out any rows for which the screen computed `False`.

_class_ zipline.pipeline.CustomFactor( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#CustomFactor) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.CustomFactor "Permalink to this definition")

Base class for user-defined Factors.

Parameters:

- **inputs** ( _iterable_ _,_ _optional_) – An iterable of BoundColumn instances (e.g. USEquityPricing.close),
describing the data to load and pass to self.compute. If this
argument is not passed to the CustomFactor constructor, we look for a
class-level attribute named inputs.

- **outputs** ( _iterable_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_ _,_ _optional_) – An iterable of strings which represent the names of each output this
factor should compute and return. If this argument is not passed to the
CustomFactor constructor, we look for a class-level attribute named
outputs.

- **window\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – Number of rows to pass for each input. If this argument is not passed
to the CustomFactor constructor, we look for a class-level attribute
named window\_length.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing the assets on which we should compute each day.
Each call to `CustomFactor.compute` will only receive assets for
which `mask` produced True on the day for which compute is being
called.


Notes

Users implementing their own Factors should subclass CustomFactor and
implement a method named compute with the following signature:

```
def compute(self, today, assets, out, *inputs):
   ...

```

On each simulation date, `compute` will be called with the current date,
an array of sids, an output array, and an input array for each expression
passed as inputs to the CustomFactor constructor.

The specific types of the values passed to compute are as follows:

```
today : np.datetime64[ns]
    Row label for the last row of all arrays passed as `inputs`.
assets : np.array[int64, ndim=1]
    Column labels for `out` and`inputs`.
out : np.array[self.dtype, ndim=1]
    Output array of the same shape as `assets`.  `compute` should write
    its desired return values into `out`. If multiple outputs are
    specified, `compute` should write its desired return values into
    `out.<output_name>` for each output name in `self.outputs`.
*inputs : tuple of np.array
    Raw data arrays corresponding to the values of `self.inputs`.

```

`compute` functions should expect to be passed NaN values for dates on
which no data was available for an asset. This may include dates on which
an asset did not yet exist.

For example, if a CustomFactor requires 10 rows of close price data, and
asset A started trading on Monday June 2nd, 2014, then on Tuesday, June
3rd, 2014, the column of input data for asset A will have 9 leading NaNs
for the preceding days on which data was not yet available.

Examples

A CustomFactor with pre-declared defaults:

```
class TenDayRange(CustomFactor):
    """
    Computes the difference between the highest high in the last 10
    days and the lowest low.

    Pre-declares high and low as default inputs and `window_length` as
    10.
    """

    inputs = [USEquityPricing.high, USEquityPricing.low]
    window_length = 10

    def compute(self, today, assets, out, highs, lows):
        from numpy import nanmin, nanmax

        highest_highs = nanmax(highs, axis=0)
        lowest_lows = nanmin(lows, axis=0)
        out[:] = highest_highs - lowest_lows

# Doesn't require passing inputs or window_length because they're
# pre-declared as defaults for the TenDayRange class.
ten_day_range = TenDayRange()

```

A CustomFactor without defaults:

```
class MedianValue(CustomFactor):
    """
    Computes the median value of an arbitrary single input over an
    arbitrary window..

    Does not declare any defaults, so values for `window_length` and
    `inputs` must be passed explicitly on every construction.
    """

    def compute(self, today, assets, out, data):
        from numpy import nanmedian
        out[:] = data.nanmedian(data, axis=0)

# Values for `inputs` and `window_length` must be passed explicitly to
# MedianValue.
median_close10 = MedianValue([USEquityPricing.close], window_length=10)
median_low15 = MedianValue([USEquityPricing.low], window_length=15)

```

A CustomFactor with multiple outputs:

```
class MultipleOutputs(CustomFactor):
    inputs = [USEquityPricing.close]
    outputs = ['alpha', 'beta']
    window_length = N

    def compute(self, today, assets, out, close):
        computed_alpha, computed_beta = some_function(close)
        out.alpha[:] = computed_alpha
        out.beta[:] = computed_beta

# Each output is returned as its own Factor upon instantiation.
alpha, beta = MultipleOutputs()

# Equivalently, we can create a single factor instance and access each
# output as an attribute of that instance.
multiple_outputs = MultipleOutputs()
alpha = multiple_outputs.alpha
beta = multiple_outputs.beta

```

Note: If a CustomFactor has multiple outputs, all outputs must have the
same dtype. For instance, in the example above, if alpha is a float then
beta must also be a float.

dtype _=dtype('float64')_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.CustomFactor.dtype "Permalink to this definition")_class_ zipline.pipeline.Filter( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _domain=sentinel('NotSpecified')_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#Filter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "Permalink to this definition")

Pipeline expression computing a boolean output.

Filters are most commonly useful for describing sets of assets to include
or exclude for some particular purpose. Many Pipeline API functions accept
a `mask` argument, which can be supplied a Filter indicating that only
values passing the Filter should be considered when performing the
requested computation. For example, [`zipline.pipeline.Factor.top()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.top "zipline.pipeline.Factor.top")
accepts a mask indicating that ranks should be computed only on assets that
passed the specified Filter.

The most common way to construct a Filter is via one of the comparison
operators ( `<`, `<=`, `!=`, `eq`, `>`, `>=`) of
[`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor"). For example, a natural way to construct
a Filter for stocks with a 10-day VWAP less than $20.0 is to first
construct a Factor computing 10-day VWAP and compare it to the scalar value
20.0:

```
>>> from zipline.pipeline.factors import VWAP
>>> vwap_10 = VWAP(window_length=10)
>>> vwaps_under_20 = (vwap_10 <= 20)

```

Filters can also be constructed via comparisons between two Factors. For
example, to construct a Filter producing True for asset/date pairs where
the asset’s 10-day VWAP was greater than it’s 30-day VWAP:

```
>>> short_vwap = VWAP(window_length=10)
>>> long_vwap = VWAP(window_length=30)
>>> higher_short_vwap = (short_vwap > long_vwap)

```

Filters can be combined via the `&` (and) and `|` (or) operators.

`&`-ing together two filters produces a new Filter that produces True if
**both** of the inputs produced True.

`|`-ing together two filters produces a new Filter that produces True if
**either** of its inputs produced True.

The `~` operator can be used to invert a Filter, swapping all True values
with Falses and vice-versa.

Filters may be set as the `screen` attribute of a Pipeline, indicating
asset/date pairs for which the filter produces False should be excluded
from the Pipeline’s output. This is useful both for reducing noise in the
output of a Pipeline and for reducing memory consumption of Pipeline
results.

\_\_and\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.__and__ "Permalink to this definition")

Binary Operator: ‘&’

\_\_or\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.__or__ "Permalink to this definition")

Binary Operator: ‘\|’

if\_else( _if\_true_, _if\_false_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#Filter.if_else) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.if_else "Permalink to this definition")

Create a term that selects values from one of two choices.

Parameters:

- **if\_true** ( _zipline.pipeline.term.ComputableTerm_) – Expression whose values should be used at locations where this
filter outputs True.

- **if\_false** ( _zipline.pipeline.term.ComputableTerm_) – Expression whose values should be used at locations where this
filter outputs False.


Returns:

**merged** – A term that computes by taking values from either `if_true` or
`if_false`, depending on the values produced by `self`.

The returned term draws from\`\`if\_true\`\` at locations where `self`
produces True, and it draws from `if_false` at locations where
`self` produces False.

Return type:

zipline.pipeline.term.ComputableTerm

Example

Let `f` be a Factor that produces the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0    2.0    3.0    4.0
2017-03-14    5.0    6.0    7.0    8.0

```

Let `g` be another Factor that produces the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13   10.0   20.0   30.0   40.0
2017-03-14   50.0   60.0   70.0   80.0

```

Finally, let `condition` be a Filter that produces the following
output:

```
             AAPL   MSFT    MCD     BK
2017-03-13   True  False   True  False
2017-03-14   True   True  False  False

```

Then, the expression `condition.if_else(f, g)` produces the following
output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0   20.0    3.0   40.0
2017-03-14    5.0    6.0   70.0   80.0

```

See also

[`numpy.where`](https://numpy.org/doc/stable/reference/generated/numpy.where.html#numpy.where "(in NumPy v1.25)"), [`Factor.fillna`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.fillna "zipline.pipeline.Factor.fillna")

_class_ zipline.pipeline.Factor( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _domain=sentinel('NotSpecified')_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "Permalink to this definition")

Pipeline API expression producing a numerical or date-valued output.

Factors are the most commonly-used Pipeline term, representing the result
of any computation producing a numerical result.

Factors can be combined, both with other Factors and with scalar values,
via any of the builtin mathematical operators ( `+`, `-`, `*`, etc).

This makes it easy to write complex expressions that combine multiple
Factors. For example, constructing a Factor that computes the average of
two other Factors is simply:

```
>>> f1 = SomeFactor(...)
>>> f2 = SomeOtherFactor(...)
>>> average = (f1 + f2) / 2.0

```

Factors can also be converted into [`zipline.pipeline.Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") objects
via comparison operators: ( `<`, `<=`, `!=`, `eq`, `>`, `>=`).

There are many natural operators defined on Factors besides the basic
numerical operators. These include methods for identifying missing or
extreme-valued outputs ( `isnull()`, `notnull()`, [`isnan()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.isnan "zipline.pipeline.Factor.isnan"),
[`notnan()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.notnan "zipline.pipeline.Factor.notnan")), methods for normalizing outputs ( [`rank()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank "zipline.pipeline.Factor.rank"),
[`demean()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.demean "zipline.pipeline.Factor.demean"), [`zscore()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore "zipline.pipeline.Factor.zscore")), and methods for constructing Filters based
on rank-order properties of results ( [`top()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.top "zipline.pipeline.Factor.top"), [`bottom()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.bottom "zipline.pipeline.Factor.bottom"),
[`percentile_between()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.percentile_between "zipline.pipeline.Factor.percentile_between")).

eq( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.eq "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self == other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self == other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

demean( _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.demean) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.demean "Permalink to this definition")

Construct a Factor that computes `self` and subtracts the mean from
row of the result.

If `mask` is supplied, ignore values where `mask` returns False
when computing row means, and output NaN anywhere the mask is False.

If `groupby` is supplied, compute by partitioning each row based on
the values produced by `groupby`, de-meaning the partitioned arrays,
and stitching the sub-results back together.

Parameters:

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter defining values to ignore when computing means.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to compute means.


Examples

Let `f` be a Factor which would produce the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0    2.0    3.0    4.0
2017-03-14    1.5    2.5    3.5    1.0
2017-03-15    2.0    3.0    4.0    1.5
2017-03-16    2.5    3.5    1.0    2.0

```

Let `c` be a Classifier producing the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13      1      1      2      2
2017-03-14      1      1      2      2
2017-03-15      1      1      2      2
2017-03-16      1      1      2      2

```

Let `m` be a Filter producing the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13  False   True   True   True
2017-03-14   True  False   True   True
2017-03-15   True   True  False   True
2017-03-16   True   True   True  False

```

Then `f.demean()` will subtract the mean from each row produced by
`f`.

```
             AAPL   MSFT    MCD     BK
2017-03-13 -1.500 -0.500  0.500  1.500
2017-03-14 -0.625  0.375  1.375 -1.125
2017-03-15 -0.625  0.375  1.375 -1.125
2017-03-16  0.250  1.250 -1.250 -0.250

```

`f.demean(mask=m)` will subtract the mean from each row, but means
will be calculated ignoring values on the diagonal, and NaNs will
written to the diagonal in the output. Diagonal values are ignored
because they are the locations where the mask `m` produced False.

```
             AAPL   MSFT    MCD     BK
2017-03-13    NaN -1.000  0.000  1.000
2017-03-14 -0.500    NaN  1.500 -1.000
2017-03-15 -0.166  0.833    NaN -0.666
2017-03-16  0.166  1.166 -1.333    NaN

```

`f.demean(groupby=c)` will subtract the group-mean of AAPL/MSFT and
MCD/BK from their respective entries. The AAPL/MSFT are grouped
together because both assets always produce 1 in the output of the
classifier `c`. Similarly, MCD/BK are grouped together because they
always produce 2.

```
             AAPL   MSFT    MCD     BK
2017-03-13 -0.500  0.500 -0.500  0.500
2017-03-14 -0.500  0.500  1.250 -1.250
2017-03-15 -0.500  0.500  1.250 -1.250
2017-03-16 -0.500  0.500 -0.500  0.500

```

`f.demean(mask=m, groupby=c)` will also subtract the group-mean of
AAPL/MSFT and MCD/BK, but means will be calculated ignoring values on
the diagonal , and NaNs will be written to the diagonal in the output.

```
             AAPL   MSFT    MCD     BK
2017-03-13    NaN  0.000 -0.500  0.500
2017-03-14  0.000    NaN  1.250 -1.250
2017-03-15 -0.500  0.500    NaN  0.000
2017-03-16 -0.500  0.500  0.000    NaN

```

Notes

Mean is sensitive to the magnitudes of outliers. When working with
factor that can potentially produce large outliers, it is often useful
to use the `mask` parameter to discard values at the extremes of the
distribution:

```
>>> base = MyFactor(...)
>>> normalized = base.demean(
...     mask=base.percentile_between(1, 99),
... )

```

`demean()` is only supported on Factors of dtype float64.

See also

[`pandas.DataFrame.groupby()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby "(in pandas v2.0.3)")

zscore( _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.zscore) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore "Permalink to this definition")

Construct a Factor that Z-Scores each day’s results.

The Z-Score of a row is defined as:

```
(row - row.mean()) / row.stddev()

```

If `mask` is supplied, ignore values where `mask` returns False
when computing row means and standard deviations, and output NaN
anywhere the mask is False.

If `groupby` is supplied, compute by partitioning each row based on
the values produced by `groupby`, z-scoring the partitioned arrays,
and stitching the sub-results back together.

Parameters:

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter defining values to ignore when Z-Scoring.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to compute Z-Scores.


Returns:

**zscored** – A Factor producing that z-scores the output of self.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Notes

Mean and standard deviation are sensitive to the magnitudes of
outliers. When working with factor that can potentially produce large
outliers, it is often useful to use the `mask` parameter to discard
values at the extremes of the distribution:

```
>>> base = MyFactor(...)
>>> normalized = base.zscore(
...    mask=base.percentile_between(1, 99),
... )

```

`zscore()` is only supported on Factors of dtype float64.

Examples

See [`demean()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.demean "zipline.pipeline.Factor.demean") for an in-depth
example of the semantics for `mask` and `groupby`.

See also

[`pandas.DataFrame.groupby()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby "(in pandas v2.0.3)")

rank( _method='ordinal'_, _ascending=True_, _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.rank) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank "Permalink to this definition")

Construct a new Factor representing the sorted rank of each column
within each row.

Parameters:

- **method** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _{'ordinal'_ _,_ _'min'_ _,_ _'max'_ _,_ _'dense'_ _,_ _'average'}_) – The method used to assign ranks to tied elements. See
scipy.stats.rankdata for a full description of the semantics for
each ranking method. Default is ‘ordinal’.

- **ascending** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Whether to return sorted rank in ascending or descending order.
Default is True.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing ranks.
If mask is supplied, ranks are computed ignoring any asset/date
pairs for which mask produces a value of False.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to perform ranking.


Returns:

**ranks** – A new factor that will compute the ranking of the data produced by
self.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Notes

The default value for method is different from the default for
scipy.stats.rankdata. See that function’s documentation for a full
description of the valid inputs to method.

Missing or non-existent data on a given day will cause an asset to be
given a rank of NaN for that day.

See also

[`scipy.stats.rankdata()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html#scipy.stats.rankdata "(in SciPy v1.11.1)")

pearsonr( _target_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.pearsonr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.pearsonr "Permalink to this definition")

Construct a new Factor that computes rolling pearson correlation
coefficients between `target` and the columns of `self`.

Parameters:

- **target** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – The term used to compute correlations against each column of data
produced by self. This may be a Factor, a BoundColumn or a Slice.
If target is two-dimensional, correlations are computed
asset-wise.

- **correlation\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Length of the lookback window over which to compute each
correlation coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should have their correlation with
the target slice computed each day.


Returns:

**correlations** – A new Factor that will compute correlations between `target` and
the columns of `self`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Notes

This method can only be called on expressions which are deemed safe for use
as inputs to windowed [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") objects. Examples
of such expressions include This includes
[`BoundColumn`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn") [`Returns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns "zipline.pipeline.factors.Returns") and any factors created from
[`rank()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank "zipline.pipeline.Factor.rank") or
[`zscore()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore "zipline.pipeline.Factor.zscore").

Examples

Suppose we want to create a factor that computes the correlation
between AAPL’s 10-day returns and the 10-day returns of all other
assets, computing each correlation over 30 days. This can be achieved
by doing the following:

```
returns = Returns(window_length=10)
returns_slice = returns[sid(24)]
aapl_correlations = returns.pearsonr(
    target=returns_slice, correlation_length=30,
)

```

This is equivalent to doing:

```
aapl_correlations = RollingPearsonOfReturns(
    target=sid(24), returns_length=10, correlation_length=30,
)

```

See also

[`scipy.stats.pearsonr()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html#scipy.stats.pearsonr "(in SciPy v1.11.1)"), [`zipline.pipeline.factors.RollingPearsonOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns "zipline.pipeline.factors.RollingPearsonOfReturns"), [`Factor.spearmanr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.spearmanr "zipline.pipeline.Factor.spearmanr")

spearmanr( _target_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.spearmanr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.spearmanr "Permalink to this definition")

Construct a new Factor that computes rolling spearman rank correlation
coefficients between `target` and the columns of `self`.

Parameters:

- **target** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – The term used to compute correlations against each column of data
produced by self. This may be a Factor, a BoundColumn or a Slice.
If target is two-dimensional, correlations are computed
asset-wise.

- **correlation\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Length of the lookback window over which to compute each
correlation coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should have their correlation with
the target slice computed each day.


Returns:

**correlations** – A new Factor that will compute correlations between `target` and
the columns of `self`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Notes

This method can only be called on expressions which are deemed safe for use
as inputs to windowed [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") objects. Examples
of such expressions include This includes
[`BoundColumn`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn") [`Returns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns "zipline.pipeline.factors.Returns") and any factors created from
[`rank()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank "zipline.pipeline.Factor.rank") or
[`zscore()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore "zipline.pipeline.Factor.zscore").

Examples

Suppose we want to create a factor that computes the correlation
between AAPL’s 10-day returns and the 10-day returns of all other
assets, computing each correlation over 30 days. This can be achieved
by doing the following:

```
returns = Returns(window_length=10)
returns_slice = returns[sid(24)]
aapl_correlations = returns.spearmanr(
    target=returns_slice, correlation_length=30,
)

```

This is equivalent to doing:

```
aapl_correlations = RollingSpearmanOfReturns(
    target=sid(24), returns_length=10, correlation_length=30,
)

```

See also

[`scipy.stats.spearmanr()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html#scipy.stats.spearmanr "(in SciPy v1.11.1)"), [`Factor.pearsonr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.pearsonr "zipline.pipeline.Factor.pearsonr")

linear\_regression( _target_, _regression\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.linear_regression) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.linear_regression "Permalink to this definition")

Construct a new Factor that performs an ordinary least-squares
regression predicting the columns of self from target.

Parameters:

- **target** ( [_zipline.pipeline.Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – The term to use as the predictor/independent variable in each
regression. This may be a Factor, a BoundColumn or a Slice. If
target is two-dimensional, regressions are computed asset-wise.

- **regression\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Length of the lookback window over which to compute each
regression.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should be regressed with the
target slice each day.


Returns:

**regressions** – A new Factor that will compute linear regressions of target
against the columns of self.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Notes

This method can only be called on expressions which are deemed safe for use
as inputs to windowed [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") objects. Examples
of such expressions include This includes
[`BoundColumn`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn") [`Returns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns "zipline.pipeline.factors.Returns") and any factors created from
[`rank()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank "zipline.pipeline.Factor.rank") or
[`zscore()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore "zipline.pipeline.Factor.zscore").

Examples

Suppose we want to create a factor that regresses AAPL’s 10-day returns
against the 10-day returns of all other assets, computing each
regression over 30 days. This can be achieved by doing the following:

```
returns = Returns(window_length=10)
returns_slice = returns[sid(24)]
aapl_regressions = returns.linear_regression(
    target=returns_slice, regression_length=30,
)

```

This is equivalent to doing:

```
aapl_regressions = RollingLinearRegressionOfReturns(
    target=sid(24), returns_length=10, regression_length=30,
)

```

See also

[`scipy.stats.linregress()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html#scipy.stats.linregress "(in SciPy v1.11.1)")

winsorize( _min\_percentile_, _max\_percentile_, _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.winsorize) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.winsorize "Permalink to this definition")

Construct a new factor that winsorizes the result of this factor.

Winsorizing changes values ranked less than the minimum percentile to
the value at the minimum percentile. Similarly, values ranking above
the maximum percentile are changed to the value at the maximum
percentile.

Winsorizing is useful for limiting the impact of extreme data points
without completely removing those points.

If `mask` is supplied, ignore values where `mask` returns False
when computing percentile cutoffs, and output NaN anywhere the mask is
False.

If `groupby` is supplied, winsorization is applied separately
separately to each group defined by `groupby`.

Parameters:

- **min\_percentile** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Entries with values at or below this percentile will be replaced
with the (len(input) \* min\_percentile)th lowest value. If low
values should not be clipped, use 0.

- **max\_percentile** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Entries with values at or above this percentile will be replaced
with the (len(input) \* max\_percentile)th lowest value. If high
values should not be clipped, use 1.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter defining values to ignore when winsorizing.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to winsorize.


Returns:

**winsorized** – A Factor producing a winsorized version of self.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

Examples

```
price = USEquityPricing.close.latest
columns={
    'PRICE': price,
    'WINSOR_1: price.winsorize(
        min_percentile=0.25, max_percentile=0.75
    ),
    'WINSOR_2': price.winsorize(
        min_percentile=0.50, max_percentile=1.0
    ),
    'WINSOR_3': price.winsorize(
        min_percentile=0.0, max_percentile=0.5
    ),

}

```

Given a pipeline with columns, defined above, the result for a
given day could look like:

```
        'PRICE' 'WINSOR_1' 'WINSOR_2' 'WINSOR_3'
Asset_1    1        2          4          3
Asset_2    2        2          4          3
Asset_3    3        3          4          3
Asset_4    4        4          4          4
Asset_5    5        5          5          4
Asset_6    6        5          5          4

```

See also

[`scipy.stats.mstats.winsorize()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mstats.winsorize.html#scipy.stats.mstats.winsorize "(in SciPy v1.11.1)"), [`pandas.DataFrame.groupby()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html#pandas.DataFrame.groupby "(in pandas v2.0.3)")

quantiles( _bins_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.quantiles) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quantiles "Permalink to this definition")

Construct a Classifier computing quantiles of the output of `self`.

Every non-NaN data point the output is labelled with an integer value
from 0 to (bins - 1). NaNs are labelled with -1.

If `mask` is supplied, ignore data points in locations for which
`mask` produces False, and emit a label of -1 at those locations.

Parameters:

- **bins** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Number of bins labels to compute.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – Mask of values to ignore when computing quantiles.


Returns:

**quantiles** – A classifier producing integer labels ranging from 0 to (bins - 1).

Return type:

zipline.pipeline.Classifier

quartiles( _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.quartiles) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quartiles "Permalink to this definition")

Construct a Classifier computing quartiles over the output of `self`.

Every non-NaN data point the output is labelled with a value of either
0, 1, 2, or 3, corresponding to the first, second, third, or fourth
quartile over each row. NaN data points are labelled with -1.

If `mask` is supplied, ignore data points in locations for which
`mask` produces False, and emit a label of -1 at those locations.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – Mask of values to ignore when computing quartiles.

Returns:

**quartiles** – A classifier producing integer labels ranging from 0 to 3.

Return type:

zipline.pipeline.Classifier

quintiles( _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.quintiles) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quintiles "Permalink to this definition")

Construct a Classifier computing quintile labels on `self`.

Every non-NaN data point the output is labelled with a value of either
0, 1, 2, or 3, 4, corresonding to quintiles over each row. NaN data
points are labelled with -1.

If `mask` is supplied, ignore data points in locations for which
`mask` produces False, and emit a label of -1 at those locations.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – Mask of values to ignore when computing quintiles.

Returns:

**quintiles** – A classifier producing integer labels ranging from 0 to 4.

Return type:

zipline.pipeline.Classifier

deciles( _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.deciles) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.deciles "Permalink to this definition")

Construct a Classifier computing decile labels on `self`.

Every non-NaN data point the output is labelled with a value from 0 to
9 corresonding to deciles over each row. NaN data points are labelled
with -1.

If `mask` is supplied, ignore data points in locations for which
`mask` produces False, and emit a label of -1 at those locations.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – Mask of values to ignore when computing deciles.

Returns:

**deciles** – A classifier producing integer labels ranging from 0 to 9.

Return type:

zipline.pipeline.Classifier

top( _N_, _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.top) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.top "Permalink to this definition")

Construct a Filter matching the top N asset values of self each day.

If `groupby` is supplied, returns a Filter matching the top N asset
values for each group.

Parameters:

- **N** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Number of assets passing the returned filter each day.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing ranks.
If mask is supplied, top values are computed ignoring any
asset/date pairs for which mask produces a value of False.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to perform ranking.


Returns:

**filter**

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

bottom( _N_, _mask=sentinel('NotSpecified')_, _groupby=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.bottom) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.bottom "Permalink to this definition")

Construct a Filter matching the bottom N asset values of self each day.

If `groupby` is supplied, returns a Filter matching the bottom N
asset values **for each group** defined by `groupby`.

Parameters:

- **N** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Number of assets passing the returned filter each day.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing ranks.
If mask is supplied, bottom values are computed ignoring any
asset/date pairs for which mask produces a value of False.

- **groupby** ( _zipline.pipeline.Classifier_ _,_ _optional_) – A classifier defining partitions over which to perform ranking.


Returns:

**filter**

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

percentile\_between( _min\_percentile_, _max\_percentile_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.percentile_between) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.percentile_between "Permalink to this definition")

Construct a Filter matching values of self that fall within the range
defined by `min_percentile` and `max_percentile`.

Parameters:

- **min\_percentile** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _\[_ _0.0_ _,_ _100.0_ _\]_) – Return True for assets falling above this percentile in the data.

- **max\_percentile** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _\[_ _0.0_ _,_ _100.0_ _\]_) – Return True for assets falling below this percentile in the data.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when percentile
calculating thresholds. If mask is supplied, percentile cutoffs
are computed each day using only assets for which `mask` returns
True. Assets for which `mask` produces False will produce False
in the output of this Factor as well.


Returns:

**out** – A new filter that will compute the specified percentile-range mask.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

isnan() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.isnan) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.isnan "Permalink to this definition")

A Filter producing True for all values where this Factor is NaN.

Returns:

**nanfilter**

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

notnan() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.notnan) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.notnan "Permalink to this definition")

A Filter producing True for values where this Factor is not NaN.

Returns:

**nanfilter**

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

isfinite() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.isfinite) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.isfinite "Permalink to this definition")

A Filter producing True for values where this Factor is anything but
NaN, inf, or -inf.

clip( _min\_bound_, _max\_bound_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.clip) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.clip "Permalink to this definition")

Clip (limit) the values in a factor.

Given an interval, values outside the interval are clipped to the
interval edges. For example, if an interval of `[0, 1]` is specified,
values smaller than 0 become 0, and values larger than 1 become 1.

Parameters:

- **min\_bound** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The minimum value to use.

- **max\_bound** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The maximum value to use.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when clipping.


Notes

To only clip values on one side, ```-np.inf` and ``np.inf``` may be
passed. For example, to only clip the maximum value but not clip a
minimum value:

```
factor.clip(min_bound=-np.inf, max_bound=user_provided_max)

```

See also

[`numpy.clip`](https://numpy.org/doc/stable/reference/generated/numpy.clip.html#numpy.clip "(in NumPy v1.25)")

clip( _min\_bound_, _max\_bound_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Factor.clip) [#](https://zipline.ml4trading.io/api-reference.html#id2 "Permalink to this definition")

Clip (limit) the values in a factor.

Given an interval, values outside the interval are clipped to the
interval edges. For example, if an interval of `[0, 1]` is specified,
values smaller than 0 become 0, and values larger than 1 become 1.

Parameters:

- **min\_bound** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The minimum value to use.

- **max\_bound** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The maximum value to use.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when clipping.


Notes

To only clip values on one side, ```-np.inf` and ``np.inf``` may be
passed. For example, to only clip the maximum value but not clip a
minimum value:

```
factor.clip(min_bound=-np.inf, max_bound=user_provided_max)

```

See also

[`numpy.clip`](https://numpy.org/doc/stable/reference/generated/numpy.clip.html#numpy.clip "(in NumPy v1.25)")

\_\_add\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__add__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self + other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self + other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_sub\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__sub__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self - other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self - other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_mul\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__mul__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self * other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self * other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_div\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__div__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self / other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self / other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_mod\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__mod__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self % other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self % other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_pow\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__pow__ "Permalink to this definition")

Construct a [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") computing `self ** other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**factor** – Factor computing `self ** other` with outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

\_\_lt\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__lt__ "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self < other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self < other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

\_\_le\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__le__ "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self <= other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self <= other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

\_\_ne\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__ne__ "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self != other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self != other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

\_\_ge\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__ge__ "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self >= other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self >= other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

\_\_gt\_\_( _other_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__gt__ "Permalink to this definition")

Construct a [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") computing `self > other`.

Parameters:

**other** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – Right-hand side of the expression.

Returns:

**filter** – Filter computing `self > other` with the outputs of `self` and
`other`.

Return type:

[zipline.pipeline.Filter](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

fillna( _fill\_value_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.fillna "Permalink to this definition")

Create a new term that fills missing values of this term’s output with
`fill_value`.

Parameters:

**fill\_value** ( _zipline.pipeline.ComputableTerm_ _, or_ _object._) –

Object to use as replacement for missing values.

If a ComputableTerm (e.g. a Factor) is passed, that term’s results
will be used as fill values.

If a scalar (e.g. a number) is passed, the scalar will be used as a
fill value.

Examples

**Filling with a Scalar:**

Let `f` be a Factor which would produce the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0    NaN    3.0    4.0
2017-03-14    1.5    2.5    NaN    NaN

```

Then `f.fillna(0)` produces the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0    0.0    3.0    4.0
2017-03-14    1.5    2.5    0.0    0.0

```

**Filling with a Term:**

Let `f` be as above, and let `g` be another Factor which would
produce the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13   10.0   20.0   30.0   40.0
2017-03-14   15.0   25.0   35.0   45.0

```

Then, `f.fillna(g)` produces the following output:

```
             AAPL   MSFT    MCD     BK
2017-03-13    1.0   20.0    3.0    4.0
2017-03-14    1.5    2.5   35.0   45.0

```

Returns:

**filled** – A term computing the same results as `self`, but with missing
values filled in using values from `fill_value`.

Return type:

zipline.pipeline.ComputableTerm

mean( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.mean "Permalink to this definition")

Create a 1-dimensional factor computing the mean of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

stddev( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.stddev "Permalink to this definition")

Create a 1-dimensional factor computing the stddev of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

max( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.max "Permalink to this definition")

Create a 1-dimensional factor computing the max of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

min( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.min "Permalink to this definition")

Create a 1-dimensional factor computing the min of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

median( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.median "Permalink to this definition")

Create a 1-dimensional factor computing the median of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

sum( _mask=sentinel('NotSpecified')_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.sum "Permalink to this definition")

Create a 1-dimensional factor computing the sum of self, each day.

Parameters:

**mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter representing assets to consider when computing results.
If supplied, we ignore asset/date pairs where `mask` produces
`False`.

Returns:

**result**

Return type:

[zipline.pipeline.Factor](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

_class_ zipline.pipeline.Term( _domain=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _window\_safe=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/term.html#Term) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "Permalink to this definition")

Base class for objects that can appear in the compute graph of a
[`zipline.pipeline.Pipeline`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline").

Notes

Most Pipeline API users only interact with [`Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term") via subclasses:

- [`BoundColumn`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")

- [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")

- [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter")

- `Classifier`


Instances of [`Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term") are **memoized**. If you call a Term’s
constructor with the same arguments twice, the same object will be returned
from both calls:

**Example:**

```
>>> from zipline.pipeline.data import EquityPricing
>>> from zipline.pipeline.factors import SimpleMovingAverage
>>> x = SimpleMovingAverage(inputs=[EquityPricing.close], window_length=5)
>>> y = SimpleMovingAverage(inputs=[EquityPricing.close], window_length=5)
>>> x is y
True

```

Warning

Memoization of terms means that it’s generally unsafe to modify
attributes of a term after construction.

graph\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/term.html#Term.graph_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term.graph_repr "Permalink to this definition")

A short repr to use when rendering GraphViz graphs.

recursive\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/term.html#Term.recursive_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term.recursive_repr "Permalink to this definition")

A short repr to use when recursively rendering terms with inputs.

_class_ zipline.pipeline.data.DataSet [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#DataSet) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "Permalink to this definition")

Base class for Pipeline datasets.

A [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet") is defined by two parts:

1. A collection of [`Column`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column "zipline.pipeline.data.Column") objects that
describe the queryable attributes of the dataset.

2. A `Domain` describing the assets and
calendar of the data represented by the [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet").


To create a new Pipeline dataset, define a subclass of [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet") and
set one or more [`Column`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column "zipline.pipeline.data.Column") objects as class-level attributes. Each
column requires a `np.dtype` that describes the type of data that should
be produced by a loader for the dataset. Integer columns must also provide
a “missing value” to be used when no value is available for a given
asset/date combination.

By default, the domain of a dataset is the special singleton value,
`GENERIC`, which means that they can be used
in a Pipeline running on **any** domain.

In some cases, it may be preferable to restrict a dataset to only allow
support a single domain. For example, a DataSet may describe data from a
vendor that only covers the US. To restrict a dataset to a specific domain,
define a domain attribute at class scope.

You can also define a domain-specific version of a generic DataSet by
calling its `specialize` method with the domain of interest.

Examples

The built-in EquityPricing dataset is defined as follows:

```
class EquityPricing(DataSet):
    open = Column(float)
    high = Column(float)
    low = Column(float)
    close = Column(float)
    volume = Column(float)

```

The built-in USEquityPricing dataset is a specialization of
EquityPricing. It is defined as:

```
from zipline.pipeline.domain import US_EQUITIES
USEquityPricing = EquityPricing.specialize(US_EQUITIES)

```

Columns can have types other than float. A dataset containing assorted
company metadata might be defined like this:

```
class CompanyMetadata(DataSet):
    # Use float for semantically-numeric data, even if it's always
    # integral valued (see Notes section below). The default missing
    # value for floats is NaN.
    shares_outstanding = Column(float)

    # Use object for string columns. The default missing value for
    # object-dtype columns is None.
    ticker = Column(object)

    # Use integers for integer-valued categorical data like sector or
    # industry codes. Integer-dtype columns require an explicit missing
    # value.
    sector_code = Column(int, missing_value=-1)

    # Use bool for boolean-valued flags. Note that the default missing
    # value for bool-dtype columns is False.
    is_primary_share = Column(bool)

```

Notes

Because numpy has no native support for integers with missing values, users
are strongly encouraged to use floats for any data that’s semantically
numeric. Doing so enables the use of NaN as a natural missing value,
which has useful propagation semantics.

_classmethod_ get\_column( _name_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#DataSet.get_column) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet.get_column "Permalink to this definition")

Look up a column by name.

Parameters:

**name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – Name of the column to look up.

Returns:

**column** – Column with the given name.

Return type:

[zipline.pipeline.data.BoundColumn](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")

Raises:

[**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError "(in Python v3.11)") – If no column with the given name exists.

_class_ zipline.pipeline.data.Column( _dtype_, _missing\_value=sentinel('NotSpecified')_, _doc=None_, _metadata=None_, _currency\_aware=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#Column) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column "Permalink to this definition")

An abstract column of data, not yet associated with a dataset.

bind( _name_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#Column.bind) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column.bind "Permalink to this definition")

Bind a Column object to its name.

_class_ zipline.pipeline.data.BoundColumn( _dtype_, _missing\_value_, _dataset_, _name_, _doc_, _metadata_, _currency\_conversion_, _currency\_aware_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "Permalink to this definition")

A column of data that’s been concretely bound to a particular dataset.

dtype [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.dtype "Permalink to this definition")

The dtype of data produced when this column is loaded.

Type:

[numpy.dtype](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v1.25)")

latest [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.latest "Permalink to this definition")

A [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter"), [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor"),
or `Classifier` computing the most recently
known value of this column on each date.
See `zipline.pipeline.mixins.LatestMixin` for more details.

Type:

zipline.pipeline.LoadableTerm

dataset [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.dataset "Permalink to this definition")

The dataset to which this column is bound.

Type:

[zipline.pipeline.data.DataSet](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet")

name [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.name "Permalink to this definition")

The name of this column.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

metadata [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.metadata "Permalink to this definition")

Extra metadata associated with this column.

Type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")

currency\_aware [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.currency_aware "Permalink to this definition")

Whether or not this column produces currency-denominated data.

Type:

[bool](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")

Notes

Instances of this class are dynamically created upon access to attributes
of [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet"). For example,
[`close`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.close "zipline.pipeline.data.EquityPricing.close") is an instance of this
class. Pipeline API users should never construct instances of this
directly.

_property_ currency\_aware [#](https://zipline.ml4trading.io/api-reference.html#id3 "Permalink to this definition")

Whether or not this column produces currency-denominated data.

_property_ currency\_conversion [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.currency_conversion "Permalink to this definition")

Specification for currency conversions applied for this term.

_property_ dataset [#](https://zipline.ml4trading.io/api-reference.html#id4 "Permalink to this definition")

The dataset to which this column is bound.

fx( _currency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn.fx) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.fx "Permalink to this definition")

Construct a currency-converted version of this column.

Parameters:

**currency** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _zipline.currency.Currency_) – Currency into which to convert this column’s data.

Returns:

**column** – Column producing the same data as `self`, but currency-converted
into `currency`.

Return type:

[BoundColumn](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")

graph\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn.graph_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.graph_repr "Permalink to this definition")

Short repr to use when rendering Pipeline graphs.

_property_ metadata [#](https://zipline.ml4trading.io/api-reference.html#id5 "Permalink to this definition")

A copy of the metadata for this column.

_property_ name [#](https://zipline.ml4trading.io/api-reference.html#id6 "Permalink to this definition")

The name of this column.

_property_ qualname [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.qualname "Permalink to this definition")

The fully-qualified name of this column.

recursive\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn.recursive_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.recursive_repr "Permalink to this definition")

Short repr used to render in recursive contexts.

specialize( _domain_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn.specialize) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.specialize "Permalink to this definition")

Specialize `self` to a concrete domain.

unspecialize() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#BoundColumn.unspecialize) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.unspecialize "Permalink to this definition")

Unspecialize a column to its generic form.

This is equivalent to `column.specialize(GENERIC)`.

_class_ zipline.pipeline.data.DataSetFamily [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#DataSetFamily) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "Permalink to this definition")

Base class for Pipeline dataset families.

Dataset families are used to represent data where the unique identifier for
a row requires more than just asset and date coordinates. A
[`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "zipline.pipeline.data.DataSetFamily") can also be thought of as a collection of
[`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet") objects, each of which has the same
columns, domain, and ndim.

[`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "zipline.pipeline.data.DataSetFamily") objects are defined with one or more
[`Column`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column "zipline.pipeline.data.Column") objects, plus one additional field:
`extra_dims`.

The `extra_dims` field defines coordinates other than asset and date that
must be fixed to produce a logical timeseries. The column objects determine
columns that will be shared by slices of the family.

`extra_dims` are represented as an ordered dictionary where the keys are
the dimension name, and the values are a set of unique values along that
dimension.

To work with a [`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "zipline.pipeline.data.DataSetFamily") in a pipeline expression, one must
choose a specific value for each of the extra dimensions using the
[`slice()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily.slice "zipline.pipeline.data.DataSetFamily.slice") method.
For example, given a [`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "zipline.pipeline.data.DataSetFamily"):

```
class SomeDataSet(DataSetFamily):
    extra_dims = [\
        ('dimension_0', {'a', 'b', 'c'}),\
        ('dimension_1', {'d', 'e', 'f'}),\
    ]

    column_0 = Column(float)
    column_1 = Column(bool)

```

This dataset might represent a table with the following columns:

```
sid :: int64
asof_date :: datetime64[ns]
timestamp :: datetime64[ns]
dimension_0 :: str
dimension_1 :: str
column_0 :: float64
column_1 :: bool

```

Here we see the implicit `sid`, `asof_date` and `timestamp` columns
as well as the extra dimensions columns.

This [`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily "zipline.pipeline.data.DataSetFamily") can be converted to a regular [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet")
with:

```
DataSetSlice = SomeDataSet.slice(dimension_0='a', dimension_1='e')

```

This sliced dataset represents the rows from the higher dimensional dataset
where `(dimension_0 == 'a') & (dimension_1 == 'e')`.

_classmethod_ slice( _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/dataset.html#DataSetFamily.slice) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily.slice "Permalink to this definition")

Take a slice of a DataSetFamily to produce a dataset
indexed by asset and date.

Parameters:

- **\*args** –

- **\*\*kwargs** – The coordinates to fix along each extra dimension.


Returns:

**dataset** – A regular pipeline dataset indexed by asset and date.

Return type:

[DataSet](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet")

Notes

The extra dimensions coords used to produce the result are available
under the `extra_coords` attribute.

_class_ zipline.pipeline.data.EquityPricing [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/data/equity_pricing.html#EquityPricing) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing "Permalink to this definition")

[`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet "zipline.pipeline.data.DataSet") containing daily trading prices and
volumes.

close _=EquityPricing.close::float64_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.close "Permalink to this definition")high _=EquityPricing.high::float64_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.high "Permalink to this definition")low _=EquityPricing.low::float64_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.low "Permalink to this definition")open _=EquityPricing.open::float64_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.open "Permalink to this definition")volume _=EquityPricing.volume::float64_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.volume "Permalink to this definition")

### Built-in Factors [\#](https://zipline.ml4trading.io/api-reference.html\#built-in-factors "Permalink to this heading")

Factors aim to transform the input data in a way that extracts a signal on which the algorithm can trade.

_class_ zipline.pipeline.factors.AverageDollarVolume( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#AverageDollarVolume) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.AverageDollarVolume "Permalink to this definition")

Average Daily Dollar Volume

**Default Inputs:** \[EquityPricing.close, EquityPricing.volume\]

**Default Window Length:** None

compute( _today_, _assets_, _out_, _close_, _volume_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#AverageDollarVolume.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.AverageDollarVolume.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.BollingerBands( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/technical.html#BollingerBands) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BollingerBands "Permalink to this definition")

Bollinger Bands technical indicator.
[https://en.wikipedia.org/wiki/Bollinger\_Bands](https://en.wikipedia.org/wiki/Bollinger_Bands)

**Default Inputs:** [`zipline.pipeline.data.EquityPricing.close`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.close "zipline.pipeline.data.EquityPricing.close")

Parameters:

- **inputs** ( _length-1 iterable_ _\[_ [_BoundColumn_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn") _\]_) – The expression over which to compute bollinger bands.

- **window\_length** ( _int > 0_) – Length of the lookback window over which to compute the bollinger
bands.

- **k** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The number of standard deviations to add or subtract to create the
upper and lower bands.


compute( _today_, _assets_, _out_, _close_, _k_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/technical.html#BollingerBands.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BollingerBands.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.BusinessDaysSincePreviousEvent( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _domain=sentinel('NotSpecified')_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/events.html#BusinessDaysSincePreviousEvent) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysSincePreviousEvent "Permalink to this definition")

Abstract class for business days since a previous event.
Returns the number of **business days** (not trading days!) since
the most recent event date for each asset.

This doesn’t use trading days for symmetry with
BusinessDaysUntilNextEarnings.

Assets which announced or will announce the event today will produce a
value of 0.0. Assets that announced the event on the previous business
day will produce a value of 1.0.

Assets for which the event date is NaT will produce a value of NaN.

Example

`BusinessDaysSincePreviousEvent` can be used to create an event-driven
factor. For instance, you may want to only trade assets that have
a data point with an asof\_date in the last 5 business days. To do this,
you can create a `BusinessDaysSincePreviousEvent` factor, supplying
the relevant asof\_date column from your dataset as input, like this:

```
# Factor computing number of days since most recent asof_date
# per asset.
days_since_event = BusinessDaysSincePreviousEvent(
    inputs=[MyDataset.asof_date]
)

# Filter returning True for each asset whose most recent asof_date
# was in the last 5 business days.
recency_filter = (days_since_event <= 5)

```

dtype _=dtype('float64')_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysSincePreviousEvent.dtype "Permalink to this definition")_class_ zipline.pipeline.factors.BusinessDaysUntilNextEvent( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _domain=sentinel('NotSpecified')_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/events.html#BusinessDaysUntilNextEvent) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysUntilNextEvent "Permalink to this definition")

Abstract class for business days since a next event.
Returns the number of **business days** (not trading days!) until
the next known event date for each asset.

This doesn’t use trading days because the trading calendar includes
information that may not have been available to the algorithm at the time
when compute is called.

For example, the NYSE closings September 11th 2001, would not have been
known to the algorithm on September 10th.

Assets that announced or will announce the event today will produce a value
of 0.0. Assets that will announce the event on the next upcoming business
day will produce a value of 1.0.

Assets for which the event date is NaT will produce a value of NaN.

dtype _=dtype('float64')_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysUntilNextEvent.dtype "Permalink to this definition")_class_ zipline.pipeline.factors.DailyReturns( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#DailyReturns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.DailyReturns "Permalink to this definition")

Calculates daily percent change in close price.

**Default Inputs**: \[EquityPricing.close\]

_class_ zipline.pipeline.factors.ExponentialWeightedMovingAverage( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#ExponentialWeightedMovingAverage) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingAverage "Permalink to this definition")

Exponentially Weighted Moving Average

**Default Inputs:** None

**Default Window Length:** None

Parameters:

- **inputs** ( _length-1 list/tuple_ _of_ [_BoundColumn_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")) – The expression over which to compute the average.

- **window\_length** ( _int > 0_) – Length of the lookback window over which to compute the average.

- **decay\_rate** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _0 < decay\_rate <= 1_) –

Weighting factor by which to discount past observations.

When calculating historical averages, rows are multiplied by the
sequence:





```
decay_rate, decay_rate ** 2, decay_rate ** 3, ...

```


Notes

- This class can also be imported under the name `EWMA`.


See also

[`pandas.DataFrame.ewm()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html#pandas.DataFrame.ewm "(in pandas v2.0.3)")

compute( _today_, _assets_, _out_, _data_, _decay\_rate_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#ExponentialWeightedMovingAverage.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingAverage.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.ExponentialWeightedMovingStdDev( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#ExponentialWeightedMovingStdDev) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingStdDev "Permalink to this definition")

Exponentially Weighted Moving Standard Deviation

**Default Inputs:** None

**Default Window Length:** None

Parameters:

- **inputs** ( _length-1 list/tuple_ _of_ [_BoundColumn_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")) – The expression over which to compute the average.

- **window\_length** ( _int > 0_) – Length of the lookback window over which to compute the average.

- **decay\_rate** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _0 < decay\_rate <= 1_) –

Weighting factor by which to discount past observations.

When calculating historical averages, rows are multiplied by the
sequence:





```
decay_rate, decay_rate ** 2, decay_rate ** 3, ...

```


Notes

- This class can also be imported under the name `EWMSTD`.


See also

`pandas.DataFrame.ewm()`

compute( _today_, _assets_, _out_, _data_, _decay\_rate_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#ExponentialWeightedMovingStdDev.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingStdDev.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.Latest( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Latest) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Latest "Permalink to this definition")

Factor producing the most recently-known value of inputs\[0\] on each day.

The .latest attribute of DataSet columns returns an instance of this
Factor.

compute( _today_, _assets_, _out_, _data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/factor.html#Latest.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Latest.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

zipline.pipeline.factors.MACDSignal [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MACDSignal "Permalink to this definition")

alias of `MovingAverageConvergenceDivergenceSignal`

_class_ zipline.pipeline.factors.MaxDrawdown( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#MaxDrawdown) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MaxDrawdown "Permalink to this definition")

Max Drawdown

**Default Inputs:** None

**Default Window Length:** None

compute( _today_, _assets_, _out_, _data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#MaxDrawdown.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MaxDrawdown.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.Returns( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#Returns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns "Permalink to this definition")

Calculates the percent change in close price over the given window\_length.

**Default Inputs**: \[EquityPricing.close\]

compute( _today_, _assets_, _out_, _close_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#Returns.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.RollingPearson( _base\_factor_, _target_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingPearson) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearson "Permalink to this definition")

A Factor that computes pearson correlation coefficients between the columns
of a given Factor and either the columns of another Factor/BoundColumn or a
slice/single column of data.

Parameters:

- **base\_factor** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")) – The factor for which to compute correlations of each of its columns
with target.

- **target** ( _zipline.pipeline.Term with a numeric dtype_) – The term with which to compute correlations against each column of data
produced by base\_factor. This term may be a Factor, a BoundColumn or
a Slice. If target is two-dimensional, correlations are computed
asset-wise.

- **correlation\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Length of the lookback window over which to compute each correlation
coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets (columns) of base\_factor should have
their correlation with target computed each day.


See also

[`scipy.stats.pearsonr()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html#scipy.stats.pearsonr "(in SciPy v1.11.1)"), `Factor.pearsonr()`, [`zipline.pipeline.factors.RollingPearsonOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns "zipline.pipeline.factors.RollingPearsonOfReturns")

Notes

Most users should call Factor.pearsonr rather than directly construct an
instance of this class.

compute( _today_, _assets_, _out_, _base\_data_, _target\_data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingPearson.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearson.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.RollingSpearman( _base\_factor_, _target_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingSpearman) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearman "Permalink to this definition")

A Factor that computes spearman rank correlation coefficients between the
columns of a given Factor and either the columns of another
Factor/BoundColumn or a slice/single column of data.

Parameters:

- **base\_factor** ( [_zipline.pipeline.Factor_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor "zipline.pipeline.Factor")) – The factor for which to compute correlations of each of its columns
with target.

- **target** ( _zipline.pipeline.Term with a numeric dtype_) – The term with which to compute correlations against each column of data
produced by base\_factor. This term may be a Factor, a BoundColumn or
a Slice. If target is two-dimensional, correlations are computed
asset-wise.

- **correlation\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Length of the lookback window over which to compute each correlation
coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets (columns) of base\_factor should have
their correlation with target computed each day.


See also

[`scipy.stats.spearmanr()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html#scipy.stats.spearmanr "(in SciPy v1.11.1)"), `Factor.spearmanr()`, [`zipline.pipeline.factors.RollingSpearmanOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearmanOfReturns "zipline.pipeline.factors.RollingSpearmanOfReturns")

Notes

Most users should call Factor.spearmanr rather than directly construct an
instance of this class.

compute( _today_, _assets_, _out_, _base\_data_, _target\_data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingSpearman.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearman.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.RollingLinearRegressionOfReturns( _target_, _returns\_length_, _regression\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingLinearRegressionOfReturns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingLinearRegressionOfReturns "Permalink to this definition")

Perform an ordinary least-squares regression predicting the returns of all
other assets on the given asset.

Parameters:

- **target** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to regress against all other assets.

- **returns\_length** ( _int >= 2_) – Length of the lookback window over which to compute returns. Daily
returns require a window length of 2.

- **regression\_length** ( _int >= 1_) – Length of the lookback window over which to compute each regression.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should be regressed against the target
asset each day.


Notes

Computing this factor over many assets can be time consuming. It is
recommended that a mask be used in order to limit the number of assets over
which regressions are computed.

This factor is designed to return five outputs:

- alpha, a factor that computes the intercepts of each regression.

- beta, a factor that computes the slopes of each regression.

- r\_value, a factor that computes the correlation coefficient of each
regression.

- p\_value, a factor that computes, for each regression, the two-sided
p-value for a hypothesis test whose null hypothesis is that the slope is
zero.

- stderr, a factor that computes the standard error of the estimate of each
regression.


For more help on factors with multiple outputs, see
[`zipline.pipeline.CustomFactor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.CustomFactor "zipline.pipeline.CustomFactor").

Examples

Let the following be example 10-day returns for three different assets:

```
               SPY    MSFT     FB
2017-03-13    -.03     .03    .04
2017-03-14    -.02    -.03    .02
2017-03-15    -.01     .02    .01
2017-03-16       0    -.02    .01
2017-03-17     .01     .04   -.01
2017-03-20     .02    -.03   -.02
2017-03-21     .03     .01   -.02
2017-03-22     .04    -.02   -.02

```

Suppose we are interested in predicting each stock’s returns from SPY’s
over rolling 5-day look back windows. We can compute rolling regression
coefficients (alpha and beta) from 2017-03-17 to 2017-03-22 by doing:

```
regression_factor = RollingRegressionOfReturns(
    target=sid(8554),
    returns_length=10,
    regression_length=5,
)
alpha = regression_factor.alpha
beta = regression_factor.beta

```

The result of computing `alpha` from 2017-03-17 to 2017-03-22 gives:

```
               SPY    MSFT     FB
2017-03-17       0    .011   .003
2017-03-20       0   -.004   .004
2017-03-21       0    .007   .006
2017-03-22       0    .002   .008

```

And the result of computing `beta` from 2017-03-17 to 2017-03-22 gives:

```
               SPY    MSFT     FB
2017-03-17       1      .3   -1.1
2017-03-20       1      .2     -1
2017-03-21       1     -.3     -1
2017-03-22       1     -.3    -.9

```

Note that SPY’s column for alpha is all 0’s and for beta is all 1’s, as the
regression line of SPY with itself is simply the function y = x.

To understand how each of the other values were calculated, take for
example MSFT’s `alpha` and `beta` values on 2017-03-17 (.011 and .3,
respectively). These values are the result of running a linear regression
predicting MSFT’s returns from SPY’s returns, using values starting at
2017-03-17 and looking back 5 days. That is, the regression was run with
x = \[-.03, -.02, -.01, 0, .01\] and y = \[.03, -.03, .02, -.02, .04\], and it
produced a slope of .3 and an intercept of .011.

See also

[`zipline.pipeline.factors.RollingPearsonOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns "zipline.pipeline.factors.RollingPearsonOfReturns"), [`zipline.pipeline.factors.RollingSpearmanOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearmanOfReturns "zipline.pipeline.factors.RollingSpearmanOfReturns")

_class_ zipline.pipeline.factors.RollingPearsonOfReturns( _target_, _returns\_length_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingPearsonOfReturns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns "Permalink to this definition")

Calculates the Pearson product-moment correlation coefficient of the
returns of the given asset with the returns of all other assets.

Pearson correlation is what most people mean when they say “correlation
coefficient” or “R-value”.

Parameters:

- **target** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to correlate with all other assets.

- **returns\_length** ( _int >= 2_) – Length of the lookback window over which to compute returns. Daily
returns require a window length of 2.

- **correlation\_length** ( _int >= 1_) – Length of the lookback window over which to compute each correlation
coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should have their correlation with the
target asset computed each day.


Notes

Computing this factor over many assets can be time consuming. It is
recommended that a mask be used in order to limit the number of assets over
which correlations are computed.

Examples

Let the following be example 10-day returns for three different assets:

```
               SPY    MSFT     FB
2017-03-13    -.03     .03    .04
2017-03-14    -.02    -.03    .02
2017-03-15    -.01     .02    .01
2017-03-16       0    -.02    .01
2017-03-17     .01     .04   -.01
2017-03-20     .02    -.03   -.02
2017-03-21     .03     .01   -.02
2017-03-22     .04    -.02   -.02

```

Suppose we are interested in SPY’s rolling returns correlation with each
stock from 2017-03-17 to 2017-03-22, using a 5-day look back window (that
is, we calculate each correlation coefficient over 5 days of data). We can
achieve this by doing:

```
rolling_correlations = RollingPearsonOfReturns(
    target=sid(8554),
    returns_length=10,
    correlation_length=5,
)

```

The result of computing `rolling_correlations` from 2017-03-17 to
2017-03-22 gives:

```
               SPY   MSFT     FB
2017-03-17       1    .15   -.96
2017-03-20       1    .10   -.96
2017-03-21       1   -.16   -.94
2017-03-22       1   -.16   -.85

```

Note that the column for SPY is all 1’s, as the correlation of any data
series with itself is always 1. To understand how each of the other values
were calculated, take for example the .15 in MSFT’s column. This is the
correlation coefficient between SPY’s returns looking back from 2017-03-17
(-.03, -.02, -.01, 0, .01) and MSFT’s returns (.03, -.03, .02, -.02, .04).

See also

[`zipline.pipeline.factors.RollingSpearmanOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearmanOfReturns "zipline.pipeline.factors.RollingSpearmanOfReturns"), [`zipline.pipeline.factors.RollingLinearRegressionOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingLinearRegressionOfReturns "zipline.pipeline.factors.RollingLinearRegressionOfReturns")

_class_ zipline.pipeline.factors.RollingSpearmanOfReturns( _target_, _returns\_length_, _correlation\_length_, _mask=sentinel('NotSpecified')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#RollingSpearmanOfReturns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearmanOfReturns "Permalink to this definition")

Calculates the Spearman rank correlation coefficient of the returns of the
given asset with the returns of all other assets.

Parameters:

- **target** ( [_zipline.assets.Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset to correlate with all other assets.

- **returns\_length** ( _int >= 2_) – Length of the lookback window over which to compute returns. Daily
returns require a window length of 2.

- **correlation\_length** ( _int >= 1_) – Length of the lookback window over which to compute each correlation
coefficient.

- **mask** ( [_zipline.pipeline.Filter_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter "zipline.pipeline.Filter") _,_ _optional_) – A Filter describing which assets should have their correlation with the
target asset computed each day.


Notes

Computing this factor over many assets can be time consuming. It is
recommended that a mask be used in order to limit the number of assets over
which correlations are computed.

See also

[`zipline.pipeline.factors.RollingPearsonOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns "zipline.pipeline.factors.RollingPearsonOfReturns"), [`zipline.pipeline.factors.RollingLinearRegressionOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingLinearRegressionOfReturns "zipline.pipeline.factors.RollingLinearRegressionOfReturns")

_class_ zipline.pipeline.factors.SimpleBeta( _target_, _regression\_length_, _allowed\_missing\_percentage=0.25_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#SimpleBeta) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta "Permalink to this definition")

Factor producing the slope of a regression line between each asset’s daily
returns to the daily returns of a single “target” asset.

Parameters:

- **target** ( _zipline.Asset_) – Asset against which other assets should be regressed.

- **regression\_length** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Number of days of daily returns to use for the regression.

- **allowed\_missing\_percentage** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _,_ _optional_) – Percentage of returns observations (between 0 and 1) that are allowed
to be missing when calculating betas. Assets with more than this
percentage of returns observations missing will produce values of
NaN. Default behavior is that 25% of inputs can be missing.


compute( _today_, _assets_, _out_, _all\_returns_, _target\_returns_, _allowed\_missing\_count_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#SimpleBeta.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

dtype _=dtype('float64')_ [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.dtype "Permalink to this definition")graph\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/statistical.html#SimpleBeta.graph_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.graph_repr "Permalink to this definition")

Short repr to use when rendering Pipeline graphs.

_property_ target [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.target "Permalink to this definition")

Get the target of the beta calculation.

_class_ zipline.pipeline.factors.RSI( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/technical.html#RSI) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RSI "Permalink to this definition")

Relative Strength Index

**Default Inputs**: [`zipline.pipeline.data.EquityPricing.close`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.close "zipline.pipeline.data.EquityPricing.close")

**Default Window Length**: 15

compute( _today_, _assets_, _out_, _closes_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/technical.html#RSI.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RSI.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.SimpleMovingAverage( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#SimpleMovingAverage) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleMovingAverage "Permalink to this definition")

Average Value of an arbitrary column

**Default Inputs**: None

**Default Window Length**: None

compute( _today_, _assets_, _out_, _data_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#SimpleMovingAverage.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleMovingAverage.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.VWAP( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#VWAP) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.VWAP "Permalink to this definition")

Volume Weighted Average Price

**Default Inputs:** \[EquityPricing.close, EquityPricing.volume\]

**Default Window Length:** None

_class_ zipline.pipeline.factors.WeightedAverageValue( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#WeightedAverageValue) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.WeightedAverageValue "Permalink to this definition")

Helper for VWAP-like computations.

**Default Inputs:** None

**Default Window Length:** None

compute( _today_, _assets_, _out_, _base_, _weight_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#WeightedAverageValue.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.WeightedAverageValue.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.PercentChange( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#PercentChange) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PercentChange "Permalink to this definition")

Calculates the percent change over the given window\_length.

**Default Inputs:** None

**Default Window Length:** None

Notes

Percent change is calculated as `(new - old) / abs(old)`.

compute( _today_, _assets_, _out_, _values_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#PercentChange.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PercentChange.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.factors.PeerCount( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#PeerCount) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PeerCount "Permalink to this definition")

Peer Count of distinct categories in a given classifier. This factor
is returned by the classifier instance method peer\_count()

**Default Inputs:** None

**Default Window Length:** 1

compute( _today_, _assets_, _out_, _classifier\_values_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/factors/basic.html#PeerCount.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PeerCount.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

### Built-in Filters [\#](https://zipline.ml4trading.io/api-reference.html\#built-in-filters "Permalink to this heading")

_class_ zipline.pipeline.filters.All( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#All) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.All "Permalink to this definition")

A Filter requiring that assets produce True for `window_length`
consecutive days.

**Default Inputs:** None

**Default Window Length:** None

compute( _today_, _assets_, _out_, _arg_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#All.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.All.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.filters.AllPresent( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#AllPresent) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AllPresent "Permalink to this definition")

Pipeline filter indicating input term has data for a given window.

compute( _today_, _assets_, _out_, _value_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#AllPresent.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AllPresent.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.filters.Any( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#Any) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.Any "Permalink to this definition")

A Filter requiring that assets produce True for at least one day in the
last `window_length` days.

**Default Inputs:** None

**Default Window Length:** None

compute( _today_, _assets_, _out_, _arg_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#Any.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.Any.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.filters.AtLeastN( _inputs=sentinel('NotSpecified')_, _outputs=sentinel('NotSpecified')_, _window\_length=sentinel('NotSpecified')_, _mask=sentinel('NotSpecified')_, _dtype=sentinel('NotSpecified')_, _missing\_value=sentinel('NotSpecified')_, _ndim=sentinel('NotSpecified')_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#AtLeastN) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AtLeastN "Permalink to this definition")

A Filter requiring that assets produce True for at least N days in the
last `window_length` days.

**Default Inputs:** None

**Default Window Length:** None

compute( _today_, _assets_, _out_, _arg_, _N_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/smoothing.html#AtLeastN.compute) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AtLeastN.compute "Permalink to this definition")

Override this method with a function that writes a value into out.

_class_ zipline.pipeline.filters.SingleAsset( _asset_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#SingleAsset) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.SingleAsset "Permalink to this definition")

A Filter that computes to True only for the given asset.

graph\_repr() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#SingleAsset.graph_repr) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.SingleAsset.graph_repr "Permalink to this definition")

A short repr to use when rendering GraphViz graphs.

_class_ zipline.pipeline.filters.StaticAssets( _assets_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#StaticAssets) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.StaticAssets "Permalink to this definition")

A Filter that computes True for a specific set of predetermined assets.

`StaticAssets` is mostly useful for debugging or for interactively
computing pipeline terms for a fixed set of assets that are known ahead of
time.

Parameters:

**assets** ( _iterable_ _\[_ [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _\]_) – An iterable of assets for which to filter.

_class_ zipline.pipeline.filters.StaticSids( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/filters/filter.html#StaticSids) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.StaticSids "Permalink to this definition")

A Filter that computes True for a specific set of predetermined sids.

`StaticSids` is mostly useful for debugging or for interactively
computing pipeline terms for a fixed set of sids that are known ahead of
time.

Parameters:

**sids** ( _iterable_ _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_) – An iterable of sids for which to filter.

### Pipeline Engine [\#](https://zipline.ml4trading.io/api-reference.html\#pipeline-engine "Permalink to this heading")

Computation engines for executing a [`Pipeline`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline") define the core computation algorithms.

The primary entrypoint is SimplePipelineEngine.run\_pipeline, which
implements the following algorithm for executing pipelines:

1. Determine the domain of the pipeline.

2. Build a dependency graph of all terms in pipeline, with
information about how many extra rows each term needs from its
inputs.

3. Combine the domain computed in (2) with our AssetFinder to produce
a “lifetimes matrix”. The lifetimes matrix is a DataFrame of
booleans whose labels are dates x assets. Each entry corresponds
to a (date, asset) pair and indicates whether the asset in
question was tradable on the date in question.

4. Produce a “workspace” dictionary with cached or otherwise pre-computed
terms.

5. Topologically sort the graph constructed in (1) to produce an
execution order for any terms that were not pre-populated.

6. Iterate over the terms in the order computed in (5). For each term:

1. Fetch the term’s inputs from the workspace.

2. Compute each term and store the results in the workspace.

3. Remove the results from the workspace if their are no longer needed to reduce memory use during execution.
7. Extract the pipeline’s outputs from the workspace and convert them
into “narrow” format, with output labels dictated by the Pipeline’s
screen.


_class_ zipline.pipeline.engine.PipelineEngine [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#PipelineEngine) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine "Permalink to this definition")_abstract_ run\_pipeline( _pipeline_, _start\_date_, _end\_date_, _hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#PipelineEngine.run_pipeline) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_pipeline "Permalink to this definition")

Compute values for `pipeline` from `start_date` to `end_date`.

Parameters:

- **pipeline** ( [_zipline.pipeline.Pipeline_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")) – The pipeline to run.

- **start\_date** ( _pd.Timestamp_) – Start date of the computed matrix.

- **end\_date** ( _pd.Timestamp_) – End date of the computed matrix.

- **hooks** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ _implements_ _(_ _PipelineHooks_ _)_ _\]_ _,_ _optional_) – Hooks for instrumenting Pipeline execution.


Returns:

**result** – A frame of computed results.

The `result` columns correspond to the entries of
pipeline.columns, which should be a dictionary mapping strings to
instances of [`zipline.pipeline.Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term").

For each date between `start_date` and `end_date`, `result`
will contain a row for each asset that passed pipeline.screen.
A screen of `None` indicates that a row should be returned for
each asset that existed each day.

Return type:

pd.DataFrame

_abstract_ run\_chunked\_pipeline( _pipeline_, _start\_date_, _end\_date_, _chunksize_, _hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#PipelineEngine.run_chunked_pipeline) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_chunked_pipeline "Permalink to this definition")

Compute values for `pipeline` from `start_date` to `end_date`, in
date chunks of size `chunksize`.

Chunked execution reduces memory consumption, and may reduce
computation time depending on the contents of your pipeline.

Parameters:

- **pipeline** ( [_Pipeline_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")) – The pipeline to run.

- **start\_date** ( _pd.Timestamp_) – The start date to run the pipeline for.

- **end\_date** ( _pd.Timestamp_) – The end date to run the pipeline for.

- **chunksize** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The number of days to execute at a time.

- **hooks** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ _implements_ _(_ _PipelineHooks_ _)_ _\]_ _,_ _optional_) – Hooks for instrumenting Pipeline execution.


Returns:

**result** – A frame of computed results.

The `result` columns correspond to the entries of
pipeline.columns, which should be a dictionary mapping strings to
instances of [`zipline.pipeline.Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term").

For each date between `start_date` and `end_date`, `result`
will contain a row for each asset that passed pipeline.screen.
A screen of `None` indicates that a row should be returned for
each asset that existed each day.

Return type:

pd.DataFrame

See also

[`zipline.pipeline.engine.PipelineEngine.run_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_pipeline "zipline.pipeline.engine.PipelineEngine.run_pipeline")

_class_ zipline.pipeline.engine.SimplePipelineEngine( _get\_loader_, _asset\_finder_, _default\_domain=GENERIC_, _populate\_initial\_workspace=None_, _default\_hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#SimplePipelineEngine) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine "Permalink to this definition")

PipelineEngine class that computes each term independently.

Parameters:

- **get\_loader** ( _callable_) – A function that is given a loadable term and returns a PipelineLoader
to use to retrieve raw data for that term.

- **asset\_finder** ( [_zipline.assets.AssetFinder_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder "zipline.assets.AssetFinder")) – An AssetFinder instance. We depend on the AssetFinder to determine
which assets are in the top-level universe at any point in time.

- **populate\_initial\_workspace** ( _callable_ _,_ _optional_) – A function which will be used to populate the initial workspace when
computing a pipeline. See
[`zipline.pipeline.engine.default_populate_initial_workspace()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.default_populate_initial_workspace "zipline.pipeline.engine.default_populate_initial_workspace")
for more info.

- **default\_hooks** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _,_ _optional_) – List of hooks that should be used to instrument all pipelines executed
by this engine.


See also

[`zipline.pipeline.engine.default_populate_initial_workspace()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.default_populate_initial_workspace "zipline.pipeline.engine.default_populate_initial_workspace")

\_\_init\_\_( _get\_loader_, _asset\_finder_, _default\_domain=GENERIC_, _populate\_initial\_workspace=None_, _default\_hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#SimplePipelineEngine.__init__) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.__init__ "Permalink to this definition")run\_chunked\_pipeline( _pipeline_, _start\_date_, _end\_date_, _chunksize_, _hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#SimplePipelineEngine.run_chunked_pipeline) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.run_chunked_pipeline "Permalink to this definition")

Compute values for `pipeline` from `start_date` to `end_date`, in
date chunks of size `chunksize`.

Chunked execution reduces memory consumption, and may reduce
computation time depending on the contents of your pipeline.

Parameters:

- **pipeline** ( [_Pipeline_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")) – The pipeline to run.

- **start\_date** ( _pd.Timestamp_) – The start date to run the pipeline for.

- **end\_date** ( _pd.Timestamp_) – The end date to run the pipeline for.

- **chunksize** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The number of days to execute at a time.

- **hooks** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ _implements_ _(_ _PipelineHooks_ _)_ _\]_ _,_ _optional_) – Hooks for instrumenting Pipeline execution.


Returns:

**result** – A frame of computed results.

The `result` columns correspond to the entries of
pipeline.columns, which should be a dictionary mapping strings to
instances of [`zipline.pipeline.Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term").

For each date between `start_date` and `end_date`, `result`
will contain a row for each asset that passed pipeline.screen.
A screen of `None` indicates that a row should be returned for
each asset that existed each day.

Return type:

pd.DataFrame

See also

[`zipline.pipeline.engine.PipelineEngine.run_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_pipeline "zipline.pipeline.engine.PipelineEngine.run_pipeline")

run\_pipeline( _pipeline_, _start\_date_, _end\_date_, _hooks=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#SimplePipelineEngine.run_pipeline) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.run_pipeline "Permalink to this definition")

Compute values for `pipeline` from `start_date` to `end_date`.

Parameters:

- **pipeline** ( [_zipline.pipeline.Pipeline_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline")) – The pipeline to run.

- **start\_date** ( _pd.Timestamp_) – Start date of the computed matrix.

- **end\_date** ( _pd.Timestamp_) – End date of the computed matrix.

- **hooks** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ _implements_ _(_ _PipelineHooks_ _)_ _\]_ _,_ _optional_) – Hooks for instrumenting Pipeline execution.


Returns:

**result** – A frame of computed results.

The `result` columns correspond to the entries of
pipeline.columns, which should be a dictionary mapping strings to
instances of [`zipline.pipeline.Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term").

For each date between `start_date` and `end_date`, `result`
will contain a row for each asset that passed pipeline.screen.
A screen of `None` indicates that a row should be returned for
each asset that existed each day.

Return type:

pd.DataFrame

zipline.pipeline.engine.default\_populate\_initial\_workspace( _initial\_workspace_, _root\_mask\_term_, _execution\_plan_, _dates_, _assets_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/engine.html#default_populate_initial_workspace) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.default_populate_initial_workspace "Permalink to this definition")

The default implementation for `populate_initial_workspace`. This
function returns the `initial_workspace` argument without making any
modifications.

Parameters:

- **initial\_workspace** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _\[_ _array-like_ _\]_) – The initial workspace before we have populated it with any cached
terms.

- **root\_mask\_term** ( [_Term_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term "zipline.pipeline.Term")) – The root mask term, normally `AssetExists()`. This is needed to
compute the dates for individual terms.

- **execution\_plan** ( _ExecutionPlan_) – The execution plan for the pipeline being run.

- **dates** ( _pd.DatetimeIndex_) – All of the dates being requested in this pipeline run including
the extra dates for look back windows.

- **assets** ( _pd.Int64Index_) – All of the assets that exist for the window being computed.


Returns:

**populated\_initial\_workspace** – The workspace to begin computations with.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[term, array-like\]

### Data Loaders [\#](https://zipline.ml4trading.io/api-reference.html\#data-loaders "Permalink to this heading")

There are several loaders to feed data to a [`Pipeline`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline "zipline.pipeline.Pipeline") that need to implement the interface
defined by the [`PipelineLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader "zipline.pipeline.loaders.base.PipelineLoader").

_class_ zipline.pipeline.loaders.base.PipelineLoader( _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/base.html#PipelineLoader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader "Permalink to this definition")

Interface for PipelineLoaders.

load\_adjusted\_array( _domain_, _columns_, _dates_, _sids_, _mask_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/base.html#PipelineLoader.load_adjusted_array) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader.load_adjusted_array "Permalink to this definition")

Load data for `columns` as AdjustedArrays.

Parameters:

- **domain** ( _zipline.pipeline.domain.Domain_) – The domain of the pipeline for which the requested data must be
loaded.

- **columns** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ [_zipline.pipeline.data.dataset.BoundColumn_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.dataset.BoundColumn") _\]_) – Columns for which data is being requested.

- **dates** ( _pd.DatetimeIndex_) – Dates for which data is being requested.

- **sids** ( _pd.Int64Index_) – Asset identifiers for which data is being requested.

- **mask** ( _np.array_ _\[_ _ndim=2_ _,_ _dtype=bool_ _\]_) – Boolean array of shape (len(dates), len(sids)) indicating dates on
which we believe the requested assets were alive/tradeable. This is
used for optimization by some loaders.


Returns:

**arrays** – Map from column to an AdjustedArray representing a point-in-time
rolling view over the requested dates for the requested sids.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[BoundColumn -> zipline.lib.adjusted\_array.AdjustedArray\]

\_\_init\_\_() [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader.__init__ "Permalink to this definition")_class_ zipline.pipeline.loaders.frame.DataFrameLoader( _column_, _baseline_, _adjustments=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/frame.html#DataFrameLoader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader "Permalink to this definition")

A PipelineLoader that reads its input from DataFrames.

Mostly useful for testing, but can also be used for real work if your data
fits in memory.

Parameters:

- **column** ( [_zipline.pipeline.data.BoundColumn_](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn "zipline.pipeline.data.BoundColumn")) – The column whose data is loadable by this loader.

- **baseline** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)")) – A DataFrame with index of type DatetimeIndex and columns of type
Int64Index. Dates should be labelled with the first date on which a
value would be **available** to an algorithm. This means that OHLCV
data should generally be shifted back by a trading day before being
supplied to this class.

- **adjustments** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _,_ _default=None_) –
A DataFrame with the following columns:

sid : int
value : any
kind : int (zipline.pipeline.loaders.frame.ADJUSTMENT\_TYPES)
start\_date : datetime64 (can be NaT)
end\_date : datetime64 (must be set)
apply\_date : datetime64 (must be set)


The default of None is interpreted as “no adjustments to the baseline”.


\_\_init\_\_( _column_, _baseline_, _adjustments=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/frame.html#DataFrameLoader.__init__) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.__init__ "Permalink to this definition")format\_adjustments( _dates_, _assets_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/frame.html#DataFrameLoader.format_adjustments) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.format_adjustments "Permalink to this definition")

Build a dict of Adjustment objects in the format expected by
AdjustedArray.

Returns a dict of the form:
{
\# Integer index into dates for the date on which we should
\# apply the list of adjustments.
1 : \[\
Float64Multiply(first\_row=2, last\_row=4, col=3, value=0.5),\
Float64Overwrite(first\_row=3, last\_row=5, col=1, value=2.0),\
…\
\],
…
}

load\_adjusted\_array( _domain_, _columns_, _dates_, _sids_, _mask_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/frame.html#DataFrameLoader.load_adjusted_array) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.load_adjusted_array "Permalink to this definition")

Load data from our stored baseline.

_class_ zipline.pipeline.loaders.equity\_pricing\_loader.EquityPricingLoader( _raw\_price\_reader_, _adjustments\_reader_, _fx\_reader_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/equity_pricing_loader.html#EquityPricingLoader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader "Permalink to this definition")

A PipelineLoader for loading daily OHLCV data.

Parameters:

- **raw\_price\_reader** ( _zipline.data.session\_bars.SessionBarReader_) – Reader providing raw prices.

- **adjustments\_reader** ( [_zipline.data.adjustments.SQLiteAdjustmentReader_](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader "zipline.data.adjustments.SQLiteAdjustmentReader")) – Reader providing price/volume adjustments.

- **fx\_reader** ( _zipline.data.fx.FXRateReader_) – Reader providing currency conversions.


\_\_init\_\_( _raw\_price\_reader_, _adjustments\_reader_, _fx\_reader_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/equity_pricing_loader.html#EquityPricingLoader.__init__) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader.__init__ "Permalink to this definition")zipline.pipeline.loaders.equity\_pricing\_loader.USEquityPricingLoader [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.USEquityPricingLoader "Permalink to this definition")

alias of [`EquityPricingLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader "zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader")

_class_ zipline.pipeline.loaders.events.EventsLoader( _events_, _next\_value\_columns_, _previous\_value\_columns_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/events.html#EventsLoader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.events.EventsLoader "Permalink to this definition")

Base class for PipelineLoaders that supports loading the next and previous
value of an event field.

Does not currently support adjustments.

Parameters:

- **events** ( _pd.DataFrame_) –

A DataFrame representing events (e.g. share buybacks or
earnings announcements) associated with particular companies.
`events` must contain at least three columns::sidint64

The asset id associated with each event.

event\_datedatetime64\[ns\]

The date on which the event occurred.

timestampdatetime64\[ns\]

The date on which we learned about the event.

- **next\_value\_columns** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _\[_ _BoundColumn -> str_ _\]_) – Map from dataset columns to raw field names that should be used when
searching for a next event value.

- **previous\_value\_columns** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _\[_ _BoundColumn -> str_ _\]_) – Map from dataset columns to raw field names that should be used when
searching for a previous event value.


\_\_init\_\_( _events_, _next\_value\_columns_, _previous\_value\_columns_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/events.html#EventsLoader.__init__) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.events.EventsLoader.__init__ "Permalink to this definition")_class_ zipline.pipeline.loaders.earnings\_estimates.EarningsEstimatesLoader( _estimates_, _name\_map_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/earnings_estimates.html#EarningsEstimatesLoader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.earnings_estimates.EarningsEstimatesLoader "Permalink to this definition")

An abstract pipeline loader for estimates data that can load data a
variable number of quarters forwards/backwards from calendar dates
depending on the num\_announcements attribute of the columns’ dataset.
If split adjustments are to be applied, a loader, split-adjusted columns,
and the split-adjusted asof-date must be supplied.

Parameters:

- **estimates** ( _pd.DataFrame_) –
The raw estimates data; must contain at least 5 columns:sidint64

The asset id associated with each estimate.

event\_datedatetime64\[ns\]

The date on which the event that the estimate is for will/has
occurred.

timestampdatetime64\[ns\]

The datetime where we learned about the estimate.

fiscal\_quarterint64

The quarter during which the event has/will occur.

fiscal\_yearint64

The year during which the event has/will occur.

- **name\_map** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _\[_ _str -> str_ _\]_) – A map of names of BoundColumns that this loader will load to the
names of the corresponding columns in events.


\_\_init\_\_( _estimates_, _name\_map_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/pipeline/loaders/earnings_estimates.html#EarningsEstimatesLoader.__init__) [#](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.earnings_estimates.EarningsEstimatesLoader.__init__ "Permalink to this definition")

## Exchange and Asset Metadata [\#](https://zipline.ml4trading.io/api-reference.html\#exchange-and-asset-metadata "Permalink to this heading")

_class_ zipline.assets.ExchangeInfo( _name_, _canonical\_name_, _country\_code_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/exchange_info.html#ExchangeInfo) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo "Permalink to this definition")

An exchange where assets are traded.

Parameters:

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_) – The full name of the exchange, for example ‘NEW YORK STOCK EXCHANGE’ or
‘NASDAQ GLOBAL MARKET’.

- **canonical\_name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The canonical name of the exchange, for example ‘NYSE’ or ‘NASDAQ’. If
None this will be the same as the name.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The country code where the exchange is located.


name [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.name "Permalink to this definition")

The full name of the exchange, for example ‘NEW YORK STOCK EXCHANGE’ or
‘NASDAQ GLOBAL MARKET’.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None

canonical\_name [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.canonical_name "Permalink to this definition")

The canonical name of the exchange, for example ‘NYSE’ or ‘NASDAQ’. If
None this will be the same as the name.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

country\_code [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.country_code "Permalink to this definition")

The country code where the exchange is located.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

calendar [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.calendar "Permalink to this definition")

The trading calendar the exchange uses.

Type:

TradingCalendar

_property_ calendar [#](https://zipline.ml4trading.io/api-reference.html#id7 "Permalink to this definition")

The trading calendar that this exchange uses.

_class_ zipline.assets.Asset [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "Permalink to this definition")

Base class for entities that can be owned by a trading algorithm.

sid [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.sid "Permalink to this definition")

Persistent unique identifier assigned to the asset.

Type:

[int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")

symbol [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.symbol "Permalink to this definition")

Most recent ticker under which the asset traded. This field can change
without warning if the asset changes tickers. Use `sid` if you need a
persistent identifier.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

asset\_name [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.asset_name "Permalink to this definition")

Full name of the asset.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

exchange [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange "Permalink to this definition")

Canonical short name of the exchange on which the asset trades (e.g.,
‘NYSE’).

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

exchange\_full [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange_full "Permalink to this definition")

Full name of the exchange on which the asset trades (e.g., ‘NEW YORK
STOCK EXCHANGE’).

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

exchange\_info [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange_info "Permalink to this definition")

Information about the exchange this asset is listed on.

Type:

[zipline.assets.ExchangeInfo](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo "zipline.assets.ExchangeInfo")

country\_code [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.country_code "Permalink to this definition")

Two character code indicating the country in which the asset trades.

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

start\_date [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.start_date "Permalink to this definition")

Date on which the asset first traded.

Type:

pd.Timestamp

end\_date [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.end_date "Permalink to this definition")

Last date on which the asset traded. On Quantopian, this value is set
to the current (real time) date for assets that are still trading.

Type:

pd.Timestamp

tick\_size [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.tick_size "Permalink to this definition")

Minimum amount that the price can change for this asset.

Type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

auto\_close\_date [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.auto_close_date "Permalink to this definition")

Date on which positions in this asset will be automatically liquidated
to cash during a simulation. By default, this is three days after
`end_date`.

Type:

pd.Timestamp

from\_dict() [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.from_dict "Permalink to this definition")

Build an Asset instance from a dict.

is\_alive\_for\_session() [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.is_alive_for_session "Permalink to this definition")

Returns whether the asset is alive at the given dt.

Parameters:

**session\_label** ( _pd.Timestamp_) – The desired session label to check. (midnight UTC)

Returns:

**boolean**

Return type:

whether the asset is alive at the given dt.

is\_exchange\_open() [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.is_exchange_open "Permalink to this definition")Parameters:

**dt\_minute** ( _pd.Timestamp_ _(_ _UTC_ _,_ _tz-aware_ _)_) – The minute to check.

Returns:

**boolean**

Return type:

whether the asset’s exchange is open at the given minute.

to\_dict() [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.to_dict "Permalink to this definition")

Convert to a python dict containing all attributes of the asset.

This is often useful for debugging.

Returns:

**as\_dict**

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")

_class_ zipline.assets.Equity [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity "Permalink to this definition")

Asset subclass representing partial ownership of a company, trust, or
partnership.

_class_ zipline.assets.Future [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future "Permalink to this definition")

Asset subclass representing ownership of a futures contract.

to\_dict() [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future.to_dict "Permalink to this definition")

Convert to a python dict.

_class_ zipline.assets.AssetConvertible [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetConvertible) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetConvertible "Permalink to this definition")

ABC for types that are convertible to integer-representations of
Assets.

Includes Asset, str, and Integral

## Trading Calendar API [\#](https://zipline.ml4trading.io/api-reference.html\#trading-calendar-api "Permalink to this heading")

The events that generate the timeline of the algorithm execution adhere to a
given `TradingCalendar`.

## Data API [\#](https://zipline.ml4trading.io/api-reference.html\#data-api "Permalink to this heading")

### Writers [\#](https://zipline.ml4trading.io/api-reference.html\#writers "Permalink to this heading")

_class_ zipline.data.bcolz\_daily\_bars.BcolzDailyBarWriter( _filename_, _calendar_, _start\_session_, _end\_session_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarWriter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter "Permalink to this definition")

Class capable of writing daily OHLCV data to disk in a format that can
be read efficiently by BcolzDailyOHLCVReader.

Parameters:

- **filename** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The location at which we should write our output.

- **calendar** ( _zipline.utils.calendar.trading\_calendar_) – Calendar to use to compute asset calendar offsets.

- **start\_session** ( _pd.Timestamp_) – Midnight UTC session label.

- **end\_session** ( _pd.Timestamp_) – Midnight UTC session label.


See also

[`zipline.data.bcolz_daily_bars.BcolzDailyBarReader`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader "zipline.data.bcolz_daily_bars.BcolzDailyBarReader")

write( _data_, _assets=None_, _show\_progress=False_, _invalid\_data\_behavior='warn'_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarWriter.write) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter.write "Permalink to this definition")Parameters:

- **data** ( _iterable_ _\[_ [_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.11)") _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _or_ _bcolz.ctable_ _\]_ _\]_) – The data chunks to write. Each chunk should be a tuple of sid
and the data for that asset.

- **assets** ( [_set_](https://docs.python.org/3/library/stdtypes.html#set "(in Python v3.11)") _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_ _,_ _optional_) – The assets that should be in `data`. If this is provided
we will check `data` against the assets and provide better
progress information.

- **show\_progress** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Whether or not to show a progress bar while writing.

- **invalid\_data\_behavior** ( _{'warn'_ _,_ _'raise'_ _,_ _'ignore'}_ _,_ _optional_) – What to do when data is encountered that is outside the range of
a uint32.


Returns:

**table** – The newly-written table.

Return type:

bcolz.ctable

write\_csvs( _asset\_map_, _show\_progress=False_, _invalid\_data\_behavior='warn'_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarWriter.write_csvs) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter.write_csvs "Permalink to this definition")

Read CSVs as DataFrames from our asset map.

Parameters:

- **asset\_map** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)") _\[_ _int -> str_ _\]_) – A mapping from asset id to file path with the CSV data for that
asset

- **show\_progress** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether or not to show a progress bar while writing.

- **invalid\_data\_behavior** ( _{'warn'_ _,_ _'raise'_ _,_ _'ignore'}_) – What to do when data is encountered that is outside the range of
a uint32.


_class_ zipline.data.adjustments.SQLiteAdjustmentWriter( _conn\_or\_path_, _equity\_daily\_bar\_reader_, _overwrite=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentWriter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter "Permalink to this definition")

Writer for data to be read by SQLiteAdjustmentReader

Parameters:

- **conn\_or\_path** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ [_sqlite3.Connection_](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection "(in Python v3.11)")) – A handle to the target sqlite database.

- **equity\_daily\_bar\_reader** ( _SessionBarReader_) – Daily bar reader to use for dividend writes.

- **overwrite** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_ _,_ _default=False_) – If True and conn\_or\_path is a string, remove any existing files at the
given path before connecting.


See also

[`zipline.data.adjustments.SQLiteAdjustmentReader`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader "zipline.data.adjustments.SQLiteAdjustmentReader")

calc\_dividend\_ratios( _dividends_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentWriter.calc_dividend_ratios) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.calc_dividend_ratios "Permalink to this definition")

Calculate the ratios to apply to equities when looking back at pricing
history so that the price is smoothed over the ex\_date, when the market
adjusts to the change in equity value due to upcoming dividend.

Returns:

A frame in the same format as splits and mergers, with keys
\- sid, the id of the equity
\- effective\_date, the date in seconds on which to apply the ratio.
\- ratio, the ratio to apply to backwards looking pricing data.

Return type:

DataFrame

write( _splits=None_, _mergers=None_, _dividends=None_, _stock\_dividends=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentWriter.write) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write "Permalink to this definition")

Writes data to a SQLite file to be read by SQLiteAdjustmentReader.

Parameters:

- **splits** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _,_ _optional_) –
Dataframe containing split data. The format of this dataframe is:effective\_dateint

The date, represented as seconds since Unix epoch, on which
the adjustment should be applied.

ratiofloat

A value to apply to all data earlier than the effective date.
For open, high, low, and close those values are multiplied by
the ratio. Volume is divided by this value.

sidint

The asset id associated with this adjustment.

- **mergers** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _,_ _optional_) –
DataFrame containing merger data. The format of this dataframe is:effective\_dateint

The date, represented as seconds since Unix epoch, on which
the adjustment should be applied.

ratiofloat

A value to apply to all data earlier than the effective date.
For open, high, low, and close those values are multiplied by
the ratio. Volume is unaffected.

sidint

The asset id associated with this adjustment.

- **dividends** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _,_ _optional_) –
DataFrame containing dividend data. The format of the dataframe is:sidint

The asset id associated with this adjustment.

ex\_datedatetime64

The date on which an equity must be held to be eligible to
receive payment.

declared\_datedatetime64

The date on which the dividend is announced to the public.

pay\_datedatetime64

The date on which the dividend is distributed.

record\_datedatetime64

The date on which the stock ownership is checked to determine
distribution of dividends.

amountfloat

The cash amount paid for each share.


Dividend ratios are calculated as:
`1.0 - (dividend_value / "close on day prior to ex_date")`

- **stock\_dividends** ( [_pandas.DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.0.3)") _,_ _optional_) –

DataFrame containing stock dividend data. The format of the
dataframe is:


> sidint
>
> The asset id associated with this adjustment.
>
> ex\_datedatetime64
>
> The date on which an equity must be held to be eligible to
> receive payment.
>
> declared\_datedatetime64
>
> The date on which the dividend is announced to the public.
>
> pay\_datedatetime64
>
> The date on which the dividend is distributed.
>
> record\_datedatetime64
>
> The date on which the stock ownership is checked to determine
> distribution of dividends.
>
> payment\_sidint
>
> The asset id of the shares that should be paid instead of
> cash.
>
> ratiofloat
>
> The ratio of currently held shares in the held sid that
> should be paid with new shares of the payment\_sid.


See also

[`zipline.data.adjustments.SQLiteAdjustmentReader`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader "zipline.data.adjustments.SQLiteAdjustmentReader")

write\_dividend\_data( _dividends_, _stock\_dividends=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentWriter.write_dividend_data) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write_dividend_data "Permalink to this definition")

Write both dividend payouts and the derived price adjustment ratios.

write\_dividend\_payouts( _frame_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentWriter.write_dividend_payouts) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write_dividend_payouts "Permalink to this definition")

Write dividend payout data to SQLite table dividend\_payouts.

_class_ zipline.assets.AssetDBWriter( _engine_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/asset_writer.html#AssetDBWriter) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter "Permalink to this definition")

Class used to write data to an assets db.

Parameters:

**engine** ( _Engine_ _or_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – An SQLAlchemy engine or path to a SQL database.

init\_db( _txn=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/asset_writer.html#AssetDBWriter.init_db) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.init_db "Permalink to this definition")

Connect to database and create tables.

Parameters:

**txn** ( _sa.engine.Connection_ _,_ _optional_) – The transaction block to execute in. If this is not provided, a new
transaction will be started with the engine provided.

Returns:

**metadata** – The metadata that describes the new assets db.

Return type:

sa.MetaData

write( _equities=None_, _futures=None_, _exchanges=None_, _root\_symbols=None_, _equity\_supplementary\_mappings=None_, _chunk\_size=999_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/asset_writer.html#AssetDBWriter.write) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.write "Permalink to this definition")

Write asset metadata to a sqlite database.

Parameters:

- **equities** ( _pd.DataFrame_ _,_ _optional_) –

The equity metadata. The columns for this dataframe are:


> symbolstr
>
> The ticker symbol for this equity.
>
> asset\_namestr
>
> The full name for this asset.
>
> start\_datedatetime
>
> The date when this asset was created.
>
> end\_datedatetime, optional
>
> The last date we have trade data for this asset.
>
> first\_tradeddatetime, optional
>
> The first date we have trade data for this asset.
>
> auto\_close\_datedatetime, optional
>
> The date on which to close any positions in this asset.
>
> exchangestr
>
> The exchange where this asset is traded.


The index of this dataframe should contain the sids.

- **futures** ( _pd.DataFrame_ _,_ _optional_) –

The future contract metadata. The columns for this dataframe are:


> symbolstr
>
> The ticker symbol for this futures contract.
>
> root\_symbolstr
>
> The root symbol, or the symbol with the expiration stripped
> out.
>
> asset\_namestr
>
> The full name for this asset.
>
> start\_datedatetime, optional
>
> The date when this asset was created.
>
> end\_datedatetime, optional
>
> The last date we have trade data for this asset.
>
> first\_tradeddatetime, optional
>
> The first date we have trade data for this asset.
>
> exchangestr
>
> The exchange where this asset is traded.
>
> notice\_datedatetime
>
> The date when the owner of the contract may be forced
> to take physical delivery of the contract’s asset.
>
> expiration\_datedatetime
>
> The date when the contract expires.
>
> auto\_close\_datedatetime
>
> The date when the broker will automatically close any
> positions in this contract.
>
> tick\_sizefloat
>
> The minimum price movement of the contract.
>
> multiplier: float
>
> The amount of the underlying asset represented by this
> contract.

- **exchanges** ( _pd.DataFrame_ _,_ _optional_) –

The exchanges where assets can be traded. The columns of this
dataframe are:


> exchangestr
>
> The full name of the exchange.
>
> canonical\_namestr
>
> The canonical name of the exchange.
>
> country\_codestr
>
> The ISO 3166 alpha-2 country code of the exchange.

- **root\_symbols** ( _pd.DataFrame_ _,_ _optional_) –

The root symbols for the futures contracts. The columns for this
dataframe are:


> root\_symbolstr
>
> The root symbol name.
>
> root\_symbol\_idint
>
> The unique id for this root symbol.
>
> sectorstring, optional
>
> The sector of this root symbol.
>
> descriptionstring, optional
>
> A short description of this root symbol.
>
> exchangestr
>
> The exchange where this root symbol is traded.

- **equity\_supplementary\_mappings** ( _pd.DataFrame_ _,_ _optional_) – Additional mappings from values of abitrary type to assets.

- **chunk\_size** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – The amount of rows to write to the SQLite table at once.
This defaults to the default number of bind params in sqlite.
If you have compiled sqlite3 with more bind or less params you may
want to pass that value here.


See also

`zipline.assets.asset_finder`

write\_direct( _equities=None_, _equity\_symbol\_mappings=None_, _equity\_supplementary\_mappings=None_, _futures=None_, _exchanges=None_, _root\_symbols=None_, _chunk\_size=999_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/asset_writer.html#AssetDBWriter.write_direct) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.write_direct "Permalink to this definition")

Write asset metadata to a sqlite database in the format that it is
stored in the assets db.

Parameters:

- **equities** ( _pd.DataFrame_ _,_ _optional_) –

The equity metadata. The columns for this dataframe are:


> symbolstr
>
> The ticker symbol for this equity.
>
> asset\_namestr
>
> The full name for this asset.
>
> start\_datedatetime
>
> The date when this asset was created.
>
> end\_datedatetime, optional
>
> The last date we have trade data for this asset.
>
> first\_tradeddatetime, optional
>
> The first date we have trade data for this asset.
>
> auto\_close\_datedatetime, optional
>
> The date on which to close any positions in this asset.
>
> exchangestr
>
> The exchange where this asset is traded.


The index of this dataframe should contain the sids.

- **futures** ( _pd.DataFrame_ _,_ _optional_) –

The future contract metadata. The columns for this dataframe are:


> symbolstr
>
> The ticker symbol for this futures contract.
>
> root\_symbolstr
>
> The root symbol, or the symbol with the expiration stripped
> out.
>
> asset\_namestr
>
> The full name for this asset.
>
> start\_datedatetime, optional
>
> The date when this asset was created.
>
> end\_datedatetime, optional
>
> The last date we have trade data for this asset.
>
> first\_tradeddatetime, optional
>
> The first date we have trade data for this asset.
>
> exchangestr
>
> The exchange where this asset is traded.
>
> notice\_datedatetime
>
> The date when the owner of the contract may be forced
> to take physical delivery of the contract’s asset.
>
> expiration\_datedatetime
>
> The date when the contract expires.
>
> auto\_close\_datedatetime
>
> The date when the broker will automatically close any
> positions in this contract.
>
> tick\_sizefloat
>
> The minimum price movement of the contract.
>
> multiplier: float
>
> The amount of the underlying asset represented by this
> contract.

- **exchanges** ( _pd.DataFrame_ _,_ _optional_) –

The exchanges where assets can be traded. The columns of this
dataframe are:


> exchangestr
>
> The full name of the exchange.
>
> canonical\_namestr
>
> The canonical name of the exchange.
>
> country\_codestr
>
> The ISO 3166 alpha-2 country code of the exchange.

- **root\_symbols** ( _pd.DataFrame_ _,_ _optional_) –

The root symbols for the futures contracts. The columns for this
dataframe are:


> root\_symbolstr
>
> The root symbol name.
>
> root\_symbol\_idint
>
> The unique id for this root symbol.
>
> sectorstring, optional
>
> The sector of this root symbol.
>
> descriptionstring, optional
>
> A short description of this root symbol.
>
> exchangestr
>
> The exchange where this root symbol is traded.

- **equity\_supplementary\_mappings** ( _pd.DataFrame_ _,_ _optional_) – Additional mappings from values of abitrary type to assets.

- **chunk\_size** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – The amount of rows to write to the SQLite table at once.
This defaults to the default number of bind params in sqlite.
If you have compiled sqlite3 with more bind or less params you may
want to pass that value here.


### Readers [\#](https://zipline.ml4trading.io/api-reference.html\#readers "Permalink to this heading")

_class_ zipline.data.bcolz\_daily\_bars.BcolzDailyBarReader( _table_, _read\_all\_threshold=3000_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader "Permalink to this definition")

Reader for raw pricing data written by BcolzDailyOHLCVWriter.

Parameters:

- **table** ( _bcolz.ctable_) – The ctable contaning the pricing data, with attrs corresponding to the
Attributes list below.

- **read\_all\_threshold** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The number of equities at which; below, the data is read by reading a
slice from the carray per asset. above, the data is read by pulling
all of the data for all assets into memory and then indexing into that
array for each day and asset pair. Used to tune performance of reads
when using a small or large number of equities.


Thetablewithwhichthisloaderinteractscontainsthefollowingattributes [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.attributes "Permalink to this definition")first\_row [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.first_row "Permalink to this definition")

Map from asset\_id -> index of first row in the dataset with that id.

Type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")

last\_row [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.last_row "Permalink to this definition")

Map from asset\_id -> index of last row in the dataset with that id.

Type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")

calendar\_offset [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.calendar_offset "Permalink to this definition")

Map from asset\_id -> calendar index of first row.

Type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")

start\_session\_ns [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.start_session_ns "Permalink to this definition")

Epoch ns of the first session used in this dataset.

Type:

[int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")

end\_session\_ns [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.end_session_ns "Permalink to this definition")

Epoch ns of the last session used in this dataset.

Type:

[int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")

calendar\_name [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.calendar_name "Permalink to this definition")

String identifier of trading calendar used (ie, “NYSE”).

Type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")

Weusefirst\_rowandlast\_rowtogethertoquicklyfindrangesofrowstoloadwhenreadinganasset'sdataintomemory.Weusecalendar\_offsetandcalendartoorientloadedblockswithinarangeofquerieddates.

Notes

A Bcolz CTable is comprised of Columns and Attributes.
The table with which this loader interacts contains the following columns:

\[‘open’, ‘high’, ‘low’, ‘close’, ‘volume’, ‘day’, ‘id’\].

The data in these columns is interpreted as follows:

- Price columns (‘open’, ‘high’, ‘low’, ‘close’) are interpreted as 1000 \*
as-traded dollar value.

- Volume is interpreted as as-traded volume.

- Day is interpreted as seconds since midnight UTC, Jan 1, 1970.

- Id is the asset id of the row.


The data in each column is grouped by asset and then sorted by day within
each asset block.

The table is built to represent a long time range of data, e.g. ten years
of equity data, so the lengths of each asset block is not equal to each
other. The blocks are clipped to the known start and end date of each asset
to cut down on the number of empty values that would need to be included to
make a regular/cubic dataset.

When read across the open, high, low, close, and volume with the same
index should represent the same asset and day.

See also

[`zipline.data.bcolz_daily_bars.BcolzDailyBarWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter "zipline.data.bcolz_daily_bars.BcolzDailyBarWriter")

currency\_codes( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader.currency_codes) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.currency_codes "Permalink to this definition")

Get currencies in which prices are quoted for the requested sids.

Assumes that a sid’s prices are always quoted in a single currency.

Parameters:

**sids** ( _np.array_ _\[_ _int64_ _\]_) – Array of sids for which currencies are needed.

Returns:

**currency\_codes** – Array of currency codes for listing currencies of
`sids`. Implementations should return None for sids whose
currency is unknown.

Return type:

np.array\[ [object](https://docs.python.org/3/library/functions.html#object "(in Python v3.11)")\]

get\_last\_traded\_dt( _asset_, _day_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader.get_last_traded_dt) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.get_last_traded_dt "Permalink to this definition")

Get the latest minute on or before `dt` in which `asset` traded.

If there are no trades on or before `dt`, returns `pd.NaT`.

Parameters:

- **asset** ( _zipline.asset.Asset_) – The asset for which to get the last traded minute.

- **dt** ( _pd.Timestamp_) – The minute at which to start searching for the last traded minute.


Returns:

**last\_traded** – The dt of the last trade for the given asset, using the input
dt as a vantage point.

Return type:

pd.Timestamp

get\_value( _sid_, _dt_, _field_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader.get_value) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.get_value "Permalink to this definition")Parameters:

- **sid** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The asset identifier.

- **day** ( _datetime64-like_) – Midnight of the day for which data is requested.

- **colname** ( _string_) – The price field. e.g. (‘open’, ‘high’, ‘low’, ‘close’, ‘volume’)


Returns:

The spot price for colname of the given sid on the given day.
Raises a NoDataOnDate exception if the given day and sid is before
or after the date range of the equity.
Returns -1 if the day is within the date range, but the price is
0.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

_property_ last\_available\_dt [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.last_available_dt "Permalink to this definition")

returns: **dt** – The last session for which the reader can provide data.
:rtype: pd.Timestamp

load\_raw\_arrays( _columns_, _start\_date_, _end\_date_, _assets_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader.load_raw_arrays) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.load_raw_arrays "Permalink to this definition")Parameters:

- **columns** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _of_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – ‘open’, ‘high’, ‘low’, ‘close’, or ‘volume’

- **start\_date** ( _Timestamp_) – Beginning of the window range.

- **end\_date** ( _Timestamp_) – End of the window range.

- **assets** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _of_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The asset identifiers in the window.


Returns:

A list with an entry per field of ndarrays with shape
(minutes in range, sids) with a dtype of float64, containing the
values for the respective field over start and end dt range.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") of np.ndarray

sid\_day\_index( _sid_, _day_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/bcolz_daily_bars.html#BcolzDailyBarReader.sid_day_index) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.sid_day_index "Permalink to this definition")Parameters:

- **sid** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The asset identifier.

- **day** ( _datetime64-like_) – Midnight of the day for which data is requested.


Returns:

Index into the data tape for the given sid and day.
Raises a NoDataOnDate exception if the given day and sid is before
or after the date range of the equity.

Return type:

[int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")

_class_ zipline.data.adjustments.SQLiteAdjustmentReader( _conn_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentReader) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader "Permalink to this definition")

Loads adjustments based on corporate actions from a SQLite database.

Expects data written in the format output by SQLiteAdjustmentWriter.

Parameters:

**conn** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ [_sqlite3.Connection_](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection "(in Python v3.11)")) – Connection from which to load data.

See also

[`zipline.data.adjustments.SQLiteAdjustmentWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter "zipline.data.adjustments.SQLiteAdjustmentWriter")

load\_adjustments( _dates_, _assets_, _should\_include\_splits_, _should\_include\_mergers_, _should\_include\_dividends_, _adjustment\_type_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentReader.load_adjustments) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader.load_adjustments "Permalink to this definition")

Load collection of Adjustment objects from underlying adjustments db.

Parameters:

- **dates** ( _pd.DatetimeIndex_) – Dates for which adjustments are needed.

- **assets** ( _pd.Int64Index_) – Assets for which adjustments are needed.

- **should\_include\_splits** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether split adjustments should be included.

- **should\_include\_mergers** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether merger adjustments should be included.

- **should\_include\_dividends** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Whether dividend adjustments should be included.

- **adjustment\_type** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – Whether price adjustments, volume adjustments, or both, should be
included in the output.


Returns:

**adjustments** – A dictionary containing price and/or volume adjustment mappings
from index to adjustment objects to apply at that index.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[str -> dict\[int -> Adjustment\]\]

unpack\_db\_to\_component\_dfs( _convert\_dates=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/adjustments.html#SQLiteAdjustmentReader.unpack_db_to_component_dfs) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader.unpack_db_to_component_dfs "Permalink to this definition")

Returns the set of known tables in the adjustments file in DataFrame
form.

Parameters:

**convert\_dates** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – By default, dates are returned in seconds since EPOCH. If
convert\_dates is True, all ints in date columns will be converted
to datetimes.

Returns:

**dfs** – Dictionary which maps table name to the corresponding DataFrame
version of the table, where all date columns have been coerced back
from int to datetime.

Return type:

dict{str->DataFrame}

_class_ zipline.assets.AssetFinder( _engine_, _future\_chain\_predicates={'AD':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'BP':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'CD':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'EL':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'GC':functools.partial(<built-infunctiondelivery\_predicate>_, _{'M'_, _'Z'_, _'Q'_, _'V'_, _'G'_, _'J'})_, _'JY':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'ME':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'PA':functools.partial(<built-infunctiondelivery\_predicate>_, _{'Z'_, _'U'_, _'H'_, _'M'})_, _'PL':functools.partial(<built-infunctiondelivery\_predicate>_, _{'J'_, _'F'_, _'V'_, _'N'})_, _'SV':functools.partial(<built-infunctiondelivery\_predicate>_, _{'H'_, _'N'_, _'Z'_, _'U'_, _'K'})_, _'XG':functools.partial(<built-infunctiondelivery\_predicate>_, _{'M'_, _'Z'_, _'Q'_, _'V'_, _'G'_, _'J'})_, _'YS':functools.partial(<built-infunctiondelivery\_predicate>_, _{'H'_, _'N'_, _'Z'_, _'U'_, _'K'})}_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder "Permalink to this definition")

An AssetFinder is an interface to a database of Asset metadata written by
an `AssetDBWriter`.

This class provides methods for looking up assets by unique integer id or
by symbol. For historical reasons, we refer to these unique ids as ‘sids’.

Parameters:

- **engine** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _SQLAlchemy.engine_) – An engine with a connection to the asset database to use, or a string
that can be parsed by SQLAlchemy as a URI.

- **future\_chain\_predicates** ( [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")) – A dict mapping future root symbol to a predicate function which accepts

- **be** ( _a contract as a parameter and returns whether_ _or_ _not the contract should_) –

- **chain.** ( _included in the_) –


See also

[`zipline.assets.AssetDBWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter "zipline.assets.AssetDBWriter")

_property_ equities\_sids [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids "Permalink to this definition")

All of the sids for equities in the asset finder.

equities\_sids\_for\_country\_code( _country\_code_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.equities_sids_for_country_code) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids_for_country_code "Permalink to this definition")

Return all of the sids for a given country.

Parameters:

**country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – An ISO 3166 alpha-2 country code.

Returns:

The sids whose exchanges are in this country.

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.11)")\[ [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")\]

equities\_sids\_for\_exchange\_name( _exchange\_name_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.equities_sids_for_exchange_name) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids_for_exchange_name "Permalink to this definition")

Return all of the sids for a given exchange\_name.

Parameters:

**exchange\_name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) –

Returns:

The sids whose exchanges are in this country.

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.11)")\[ [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")\]

_property_ futures\_sids [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.futures_sids "Permalink to this definition")

All of the sids for futures consracts in the asset finder.

get\_supplementary\_field( _sid_, _field\_name_, _as\_of\_date_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.get_supplementary_field) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.get_supplementary_field "Permalink to this definition")

Get the value of a supplementary field for an asset.

Parameters:

- **sid** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The sid of the asset to query.

- **field\_name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – Name of the supplementary field.

- **as\_of\_date** ( _pd.Timestamp_ _,_ _None_) – The last known value on this date is returned. If None, a
value is returned only if we’ve only ever had one value for
this sid. If None and we’ve had multiple values,
MultipleValuesFoundForSid is raised.


Raises:

- **NoValueForSid** – If we have no values for this asset, or no values was known
on this as\_of\_date.

- **MultipleValuesFoundForSid** – If we have had multiple values for this asset over time, and
None was passed for as\_of\_date.


group\_by\_type( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.group_by_type) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.group_by_type "Permalink to this definition")

Group a list of sids by asset type.

Parameters:

**sids** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_) –

Returns:

**types** – A dict mapping unique asset types to lists of sids drawn from sids.
If we fail to look up an asset, we assign it a key of None.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[ [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") or None -> list\[ [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")\]\]

lifetimes( _dates_, _include\_start\_date_, _country\_codes_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lifetimes) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lifetimes "Permalink to this definition")

Compute a DataFrame representing asset lifetimes for the specified date
range.

Parameters:

- **dates** ( _pd.DatetimeIndex_) – The dates for which to compute lifetimes.

- **include\_start\_date** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) –

Whether or not to count the asset as alive on its start\_date.

This is useful in a backtesting context where lifetimes is being
used to signify “do I have data for this asset as of the morning of
this date?” For many financial metrics, (e.g. daily close), data
isn’t available for an asset until the end of the asset’s first
day.

- **country\_codes** ( _iterable_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_) – The country codes to get lifetimes for.


Returns:

**lifetimes** – A frame of dtype bool with dates as index and an Int64Index of
assets as columns. The value at lifetimes.loc\[date, asset\] will
be True iff asset existed on date. If include\_start\_date is
False, then lifetimes.loc\[date, asset\] will be false when date ==
asset.start\_date.

Return type:

pd.DataFrame

See also

[`numpy.putmask`](https://numpy.org/doc/stable/reference/generated/numpy.putmask.html#numpy.putmask "(in NumPy v1.25)"), `zipline.pipeline.engine.SimplePipelineEngine._compute_root_mask`

lookup\_asset\_types( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lookup_asset_types) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_asset_types "Permalink to this definition")

Retrieve asset types for a list of sids.

Parameters:

**sids** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_) –

Returns:

**types** – Asset types for the provided sids.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[sid -> str or None\]

lookup\_future\_symbol( _symbol_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lookup_future_symbol) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_future_symbol "Permalink to this definition")

Lookup a future contract by symbol.

Parameters:

**symbol** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The symbol of the desired contract.

Returns:

**future** – The future contract referenced by `symbol`.

Return type:

[Future](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future "zipline.assets.Future")

Raises:

**SymbolNotFound** – Raised when no contract named ‘symbol’ is found.

lookup\_generic( _obj_, _as\_of\_date_, _country\_code_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lookup_generic) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_generic "Permalink to this definition")

Convert an object into an Asset or sequence of Assets.

This method exists primarily as a convenience for implementing
user-facing APIs that can handle multiple kinds of input. It should
not be used for internal code where we already know the expected types
of our inputs.

Parameters:

- **obj** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _,_ _ContinuousFuture_ _, or_ _iterable_) – The object to be converted into one or more Assets.
Integers are interpreted as sids. Strings are interpreted as
tickers. Assets and ContinuousFutures are returned unchanged.

- **as\_of\_date** ( _pd.Timestamp_ _or_ _None_) – Timestamp to use to disambiguate ticker lookups. Has the same
semantics as in lookup\_symbol.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_) – ISO-3166 country code to use to disambiguate ticker lookups. Has
the same semantics as in lookup\_symbol.


Returns:

**matches, missing** –

`matches` is the result of the conversion. `missing` is a list

containing any values that couldn’t be resolved. If `obj` is not
an iterable, `missing` will be an empty list.

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.11)")

lookup\_symbol( _symbol_, _as\_of\_date_, _fuzzy=False_, _country\_code=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lookup_symbol) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_symbol "Permalink to this definition")

Lookup an equity by symbol.

Parameters:

- **symbol** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ticker symbol to resolve.

- **as\_of\_date** ( [_datetime.datetime_](https://docs.python.org/3/library/datetime.html#datetime.datetime "(in Python v3.11)") _or_ _None_) – Look up the last owner of this symbol as of this datetime.
If `as_of_date` is None, then this can only resolve the equity
if exactly one equity has ever owned the ticker.

- **fuzzy** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should fuzzy symbol matching be used? Fuzzy symbol matching
attempts to resolve differences in representations for
shareclasses. For example, some people may represent the `A`
shareclass of `BRK` as `BRK.A`, where others could write
`BRK_A`.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_ _,_ _optional_) – The country to limit searches to. If not provided, the search will
span all countries which increases the likelihood of an ambiguous
lookup.


Returns:

**equity** – The equity that held `symbol` on the given `as_of_date`, or the
only equity to hold `symbol` if `as_of_date` is None.

Return type:

[Equity](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity "zipline.assets.Equity")

Raises:

- **SymbolNotFound** – Raised when no equity has ever held the given symbol.

- **MultipleSymbolsFound** – Raised when no `as_of_date` is given and more than one equity
has held `symbol`. This is also raised when `fuzzy=True` and
there are multiple candidates for the given `symbol` on the
`as_of_date`. Also raised when no `country_code` is given and
the symbol is ambiguous across multiple countries.


lookup\_symbols( _symbols_, _as\_of\_date_, _fuzzy=False_, _country\_code=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.lookup_symbols) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_symbols "Permalink to this definition")

Lookup a list of equities by symbol.

Equivalent to:

```
[finder.lookup_symbol(s, as_of, fuzzy) for s in symbols]

```

but potentially faster because repeated lookups are memoized.

Parameters:

- **symbols** ( _sequence_ _\[_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _\]_) – Sequence of ticker symbols to resolve.

- **as\_of\_date** ( _pd.Timestamp_) – Forwarded to `lookup_symbol`.

- **fuzzy** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Forwarded to `lookup_symbol`.

- **country\_code** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _or_ _None_ _,_ _optional_) – The country to limit searches to. If not provided, the search will
span all countries which increases the likelihood of an ambiguous
lookup.


Returns:

**equities**

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [Equity](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity "zipline.assets.Equity")\]

retrieve\_all( _sids_, _default\_none=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.retrieve_all) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_all "Permalink to this definition")

Retrieve all assets in sids.

Parameters:

- **sids** ( _iterable_ _of_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – Assets to retrieve.

- **default\_none** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – If True, return None for failed lookups.
If False, raise SidsNotFound.


Returns:

**assets** – A list of the same length as sids containing Assets (or Nones)
corresponding to the requested sids.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [Asset](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") or None\]

Raises:

**SidsNotFound** – When a requested sid is not found and default\_none=False.

retrieve\_asset( _sid_, _default\_none=False_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.retrieve_asset) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_asset "Permalink to this definition")

Retrieve the Asset for a given sid.

retrieve\_equities( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.retrieve_equities) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_equities "Permalink to this definition")

Retrieve Equity objects for a list of sids.

Users generally shouldn’t need to this method (instead, they should
prefer the more general/friendly retrieve\_assets), but it has a
documented interface and tests because it’s used upstream.

Parameters:

**sids** ( _iterable_ _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_) –

Returns:

**equities**

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[int -> Equity\]

Raises:

**EquitiesNotFound** – When any requested asset isn’t found.

retrieve\_futures\_contracts( _sids_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/assets/assets.html#AssetFinder.retrieve_futures_contracts) [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_futures_contracts "Permalink to this definition")

Retrieve Future objects for an iterable of sids.

Users generally shouldn’t need to this method (instead, they should
prefer the more general/friendly retrieve\_assets), but it has a
documented interface and tests because it’s used upstream.

Parameters:

**sids** ( _iterable_ _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_) –

Returns:

**equities**

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\[int -> Equity\]

Raises:

**EquitiesNotFound** – When any requested asset isn’t found.

_property_ sids [#](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.sids "Permalink to this definition")

All the sids in the asset finder.

_class_ zipline.data.data\_portal.DataPortal( _asset\_finder_, _trading\_calendar_, _first\_trading\_day_, _equity\_daily\_reader=None_, _equity\_minute\_reader=None_, _future\_daily\_reader=None_, _future\_minute\_reader=None_, _adjustment\_reader=None_, _last\_available\_session=None_, _last\_available\_minute=None_, _minute\_history\_prefetch\_length=1560_, _daily\_history\_prefetch\_length=40_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal "Permalink to this definition")

Interface to all of the data that a zipline simulation needs.

This is used by the simulation runner to answer questions about the data,
like getting the prices of assets on a given day or to service history
calls.

Parameters:

- **asset\_finder** ( [_zipline.assets.assets.AssetFinder_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder "zipline.assets.assets.AssetFinder")) – The AssetFinder instance used to resolve assets.

- **trading\_calendar** ( _zipline.utils.calendar.exchange\_calendar.TradingCalendar_) – The calendar instance used to provide minute->session information.

- **first\_trading\_day** ( _pd.Timestamp_) – The first trading day for the simulation.

- **equity\_daily\_reader** ( [_BcolzDailyBarReader_](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader "zipline.data.bcolz_daily_bars.BcolzDailyBarReader") _,_ _optional_) – The daily bar reader for equities. This will be used to service
daily data backtests or daily history calls in a minute backetest.
If a daily bar reader is not provided but a minute bar reader is,
the minutes will be rolled up to serve the daily requests.

- **equity\_minute\_reader** ( _BcolzMinuteBarReader_ _,_ _optional_) – The minute bar reader for equities. This will be used to service
minute data backtests or minute history calls. This can be used
to serve daily calls if no daily bar reader is provided.

- **future\_daily\_reader** ( [_BcolzDailyBarReader_](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader "zipline.data.bcolz_daily_bars.BcolzDailyBarReader") _,_ _optional_) – The daily bar ready for futures. This will be used to service
daily data backtests or daily history calls in a minute backetest.
If a daily bar reader is not provided but a minute bar reader is,
the minutes will be rolled up to serve the daily requests.

- **future\_minute\_reader** ( _BcolzFutureMinuteBarReader_ _,_ _optional_) – The minute bar reader for futures. This will be used to service
minute data backtests or minute history calls. This can be used
to serve daily calls if no daily bar reader is provided.

- **adjustment\_reader** ( [_SQLiteAdjustmentWriter_](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter "zipline.data.adjustments.SQLiteAdjustmentWriter") _,_ _optional_) – The adjustment reader. This is used to apply splits, dividends, and
other adjustment data to the raw data from the readers.

- **last\_available\_session** ( _pd.Timestamp_ _,_ _optional_) – The last session to make available in session-level data.

- **last\_available\_minute** ( _pd.Timestamp_ _,_ _optional_) – The last minute to make available in minute-level data.


get\_adjusted\_value( _asset_, _field_, _dt_, _perspective\_dt_, _data\_frequency_, _spot\_value=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_adjusted_value) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_adjusted_value "Permalink to this definition")

Returns a scalar value representing the value
of the desired asset’s field at the given dt with adjustments applied.

Parameters:

- **asset** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset whose data is desired.

- **field** ( _{'open'_ _,_ _'high'_ _,_ _'low'_ _,_ _'close'_ _,_ _'volume'_ _,_ _'price'_ _,_ _'last\_traded'}_) – The desired field of the asset.

- **dt** ( _pd.Timestamp_) – The timestamp for the desired value.

- **perspective\_dt** ( _pd.Timestamp_) – The timestamp from which the data is being viewed back from.

- **data\_frequency** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The frequency of the data to query; i.e. whether the data is
‘daily’ or ‘minute’ bars


Returns:

**value** – The value of the given `field` for `asset` at `dt` with any
adjustments known by `perspective_dt` applied. The return type is
based on the `field` requested. If the field is one of ‘open’,
‘high’, ‘low’, ‘close’, or ‘price’, the value will be a float. If
the `field` is ‘volume’ the value will be a int. If the `field`
is ‘last\_traded’ the value will be a Timestamp.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)"), [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)"), or pd.Timestamp

get\_adjustments( _assets_, _field_, _dt_, _perspective\_dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_adjustments) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_adjustments "Permalink to this definition")

Returns a list of adjustments between the dt and perspective\_dt for the
given field and list of assets

Parameters:

- **assets** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _of_ _type Asset_ _, or_ [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset, or assets whose adjustments are desired.

- **field** ( _{'open'_ _,_ _'high'_ _,_ _'low'_ _,_ _'close'_ _,_ _'volume'_ _,_ _'price'_ _,_ _'last\_traded'}_) – The desired field of the asset.

- **dt** ( _pd.Timestamp_) – The timestamp for the desired value.

- **perspective\_dt** ( _pd.Timestamp_) – The timestamp from which the data is being viewed back from.


Returns:

**adjustments** – The adjustments to that field.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[Adjustment\]

get\_current\_future\_chain( _continuous\_future_, _dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_current_future_chain) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_current_future_chain "Permalink to this definition")

Retrieves the future chain for the contract at the given dt according
the continuous\_future specification.

Returns:

**future\_chain** – A list of active futures, where the first index is the current
contract specified by the continuous future definition, the second
is the next upcoming contract and so on.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [Future](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future "zipline.assets.Future")\]

get\_fetcher\_assets( _dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_fetcher_assets) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_fetcher_assets "Permalink to this definition")

Returns a list of assets for the current date, as defined by the
fetcher data.

Returns:

**list**

Return type:

a list of Asset objects.

get\_history\_window( _assets_, _end\_dt_, _bar\_count_, _frequency_, _field_, _data\_frequency_, _ffill=True_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_history_window) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_history_window "Permalink to this definition")

Public API method that returns a dataframe containing the requested
history window. Data is fully adjusted.

Parameters:

- **assets** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _of_ _zipline.data.Asset objects_) – The assets whose data is desired.

- **bar\_count** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The number of bars desired.

- **frequency** ( _string_) – “1d” or “1m”

- **field** ( _string_) – The desired field of the asset.

- **data\_frequency** ( _string_) – The frequency of the data to query; i.e. whether the data is
‘daily’ or ‘minute’ bars.

- **ffill** ( _boolean_) – Forward-fill missing values. Only has effect if field
is ‘price’.


Return type:

A dataframe containing the requested data.

get\_last\_traded\_dt( _asset_, _dt_, _data\_frequency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_last_traded_dt) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_last_traded_dt "Permalink to this definition")

Given an asset and dt, returns the last traded dt from the viewpoint
of the given dt.

If there is a trade on the dt, the answer is dt provided.

get\_scalar\_asset\_spot\_value( _asset_, _field_, _dt_, _data\_frequency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_scalar_asset_spot_value) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_scalar_asset_spot_value "Permalink to this definition")

Public API method that returns a scalar value representing the value
of the desired asset’s field at either the given dt.

Parameters:

- **assets** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset")) – The asset or assets whose data is desired. This cannot be
an arbitrary AssetConvertible.

- **field** ( _{'open'_ _,_ _'high'_ _,_ _'low'_ _,_ _'close'_ _,_ _'volume'_ _,_) – ‘price’, ‘last\_traded’}
The desired field of the asset.

- **dt** ( _pd.Timestamp_) – The timestamp for the desired value.

- **data\_frequency** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The frequency of the data to query; i.e. whether the data is
‘daily’ or ‘minute’ bars


Returns:

**value** – The spot value of `field` for `asset` The return type is based
on the `field` requested. If the field is one of ‘open’, ‘high’,
‘low’, ‘close’, or ‘price’, the value will be a float. If the
`field` is ‘volume’ the value will be a int. If the `field` is
‘last\_traded’ the value will be a Timestamp.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)"), [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)"), or pd.Timestamp

get\_splits( _assets_, _dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_splits) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_splits "Permalink to this definition")

Returns any splits for the given sids and the given dt.

Parameters:

- **assets** ( _container_) – Assets for which we want splits.

- **dt** ( _pd.Timestamp_) – The date for which we are checking for splits. Note: this is
expected to be midnight UTC.


Returns:

**splits** – List of splits, where each split is a (asset, ratio) tuple.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[(asset, [float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)"))\]

get\_spot\_value( _assets_, _field_, _dt_, _data\_frequency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_spot_value) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_spot_value "Permalink to this definition")

Public API method that returns a scalar value representing the value
of the desired asset’s field at either the given dt.

Parameters:

- **assets** ( [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _,_ _ContinuousFuture_ _, or_ _iterable_ _of_ _same._) – The asset or assets whose data is desired.

- **field** ( _{'open'_ _,_ _'high'_ _,_ _'low'_ _,_ _'close'_ _,_ _'volume'_ _,_) – ‘price’, ‘last\_traded’}
The desired field of the asset.

- **dt** ( _pd.Timestamp_) – The timestamp for the desired value.

- **data\_frequency** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The frequency of the data to query; i.e. whether the data is
‘daily’ or ‘minute’ bars


Returns:

**value** – The spot value of `field` for `asset` The return type is based
on the `field` requested. If the field is one of ‘open’, ‘high’,
‘low’, ‘close’, or ‘price’, the value will be a float. If the
`field` is ‘volume’ the value will be a int. If the `field` is
‘last\_traded’ the value will be a Timestamp.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)"), [int](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)"), or pd.Timestamp

get\_stock\_dividends( _sid_, _trading\_days_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.get_stock_dividends) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_stock_dividends "Permalink to this definition")

Returns all the stock dividends for a specific sid that occur
in the given trading range.

Parameters:

- **sid** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)")) – The asset whose stock dividends should be returned.

- **trading\_days** ( _pd.DatetimeIndex_) – The trading range.


Returns:

- **list** ( _A list of objects with all relevant attributes populated._)

- _All timestamp fields are converted to pd.Timestamps._


handle\_extra\_source( _source\_df_, _sim\_params_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/data/data_portal.html#DataPortal.handle_extra_source) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.handle_extra_source "Permalink to this definition")

Extra sources always have a sid column.

We expand the given data (by forward filling) to the full range of
the simulation dates, so that lookup is fast during simulation.

_class_ zipline.sources.benchmark\_source.BenchmarkSource( _benchmark\_asset_, _trading\_calendar_, _sessions_, _data\_portal_, _emission\_rate='daily'_, _benchmark\_returns=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/sources/benchmark_source.html#BenchmarkSource) [#](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource "Permalink to this definition")daily\_returns( _start_, _end=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/sources/benchmark_source.html#BenchmarkSource.daily_returns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.daily_returns "Permalink to this definition")

Returns the daily returns for the given period.

Parameters:

- **start** ( _datetime_) – The inclusive starting session label.

- **end** ( _datetime_ _,_ _optional_) – The inclusive ending session label. If not provided, treat
`start` as a scalar key.


Returns:

**returns** – The returns in the given period. The index will be the trading
calendar in the range \[start, end\]. If just `start` is provided,
return the scalar value on that day.

Return type:

pd.Series or [float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

get\_range( _start\_dt_, _end\_dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/sources/benchmark_source.html#BenchmarkSource.get_range) [#](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.get_range "Permalink to this definition")

Look up the returns for a given period.

Parameters:

- **start\_dt** ( _datetime_) – The inclusive start label.

- **end\_dt** ( _datetime_) – The inclusive end label.


Returns:

**returns** – The series of returns.

Return type:

pd.Series

See also

[`zipline.sources.benchmark_source.BenchmarkSource.daily_returns`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.daily_returns "zipline.sources.benchmark_source.BenchmarkSource.daily_returns")

``

This method expects minute inputs if `emission_rate == 'minute'` and session labels when `emission_rate == 'daily`.

get\_value( _dt_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/sources/benchmark_source.html#BenchmarkSource.get_value) [#](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.get_value "Permalink to this definition")

Look up the returns for a given dt.

Parameters:

**dt** ( _datetime_) – The label to look up.

Returns:

**returns** – The returns at the given dt or session.

Return type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

See also

[`zipline.sources.benchmark_source.BenchmarkSource.daily_returns`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.daily_returns "zipline.sources.benchmark_source.BenchmarkSource.daily_returns")

``

This method expects minute inputs if `emission_rate == 'minute'` and session labels when `emission_rate == 'daily`.

### Bundles [\#](https://zipline.ml4trading.io/api-reference.html\#bundles "Permalink to this heading")

zipline.data.bundles.register( _name='\_\_no\_\_default\_\_'_, _f='\_\_no\_\_default\_\_'_, _calendar\_name='NYSE'_, _start\_session=None_, _end\_session=None_, _minutes\_per\_day=390_, _create\_writers=True_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.register "Permalink to this definition")

Register a data bundle ingest function.

Parameters:

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the bundle.

- **f** ( _callable_) –

The ingest function. This function will be passed:


> environmapping
>
> The environment this is being run with.
>
> asset\_db\_writerAssetDBWriter
>
> The asset db writer to write into.
>
> minute\_bar\_writerBcolzMinuteBarWriter
>
> The minute bar writer to write into.
>
> daily\_bar\_writerBcolzDailyBarWriter
>
> The daily bar writer to write into.
>
> adjustment\_writerSQLiteAdjustmentWriter
>
> The adjustment db writer to write into.
>
> calendartrading\_calendars.TradingCalendar
>
> The trading calendar to ingest for.
>
> start\_sessionpd.Timestamp
>
> The first session of data to ingest.
>
> end\_sessionpd.Timestamp
>
> The last session of data to ingest.
>
> cacheDataFrameCache
>
> A mapping object to temporarily store dataframes.
> This should be used to cache intermediates in case the load
> fails. This will be automatically cleaned up after a
> successful load.
>
> show\_progressbool
>
> Show the progress for the current load where possible.

- **calendar\_name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of a calendar used to align bundle data.
Default is ‘NYSE’.

- **start\_session** ( _pd.Timestamp_ _,_ _optional_) – The first session for which we want data. If not provided,
or if the date lies outside the range supported by the
calendar, the first\_session of the calendar is used.

- **end\_session** ( _pd.Timestamp_ _,_ _optional_) – The last session for which we want data. If not provided,
or if the date lies outside the range supported by the
calendar, the last\_session of the calendar is used.

- **minutes\_per\_day** ( [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _,_ _optional_) – The number of minutes in each normal trading day.

- **create\_writers** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should the ingest machinery create the writers for the ingest
function. This can be disabled as an optimization for cases where
they are not needed, like the `quantopian-quandl` bundle.


Notes

This function my be used as a decorator, for example:

```
@register('quandl')
def quandl_ingest_function(...):
    ...

```

See also

[`zipline.data.bundles.bundles`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.bundles "zipline.data.bundles.bundles")

zipline.data.bundles.ingest( _name_, _environ=os.environ_, _date=None_, _show\_progress=True_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.ingest "Permalink to this definition")

Ingest data for a given bundle.

Parameters:

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the bundle.

- **environ** ( _mapping_ _,_ _optional_) – The environment variables. By default this is os.environ.

- **timestamp** ( _datetime_ _,_ _optional_) – The timestamp to use for the load.
By default this is the current time.

- **assets\_versions** ( _Iterable_ _\[_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.11)") _\]_ _,_ _optional_) – Versions of the assets db to which to downgrade.

- **show\_progress** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Tell the ingest function to display the progress where possible.


zipline.data.bundles.load( _name_, _environ=os.environ_, _date=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.load "Permalink to this definition")

Loads a previously ingested bundle.

Parameters:

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the bundle.

- **environ** ( _mapping_ _,_ _optional_) – The environment variables. Defaults of os.environ.

- **timestamp** ( _datetime_ _,_ _optional_) – The timestamp of the data to lookup.
Defaults to the current time.


Returns:

**bundle\_data** – The raw data readers for this bundle.

Return type:

BundleData

zipline.data.bundles.unregister( _name_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.unregister "Permalink to this definition")

Unregister a bundle.

Parameters:

**name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the bundle to unregister.

Raises:

**UnknownBundle** – Raised when no bundle has been registered with the given name.

See also

[`zipline.data.bundles.bundles`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.bundles "zipline.data.bundles.bundles")

zipline.data.bundles.bundles [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.bundles "Permalink to this definition")

The bundles that have been registered as a mapping from bundle name to bundle
data. This mapping is immutable and may only be updated through
[`register()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.register "zipline.data.bundles.register") or
[`unregister()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.unregister "zipline.data.bundles.unregister").

## Risk Metrics [\#](https://zipline.ml4trading.io/api-reference.html\#risk-metrics "Permalink to this heading")

### Algorithm State [\#](https://zipline.ml4trading.io/api-reference.html\#algorithm-state "Permalink to this heading")

_class_ zipline.finance.ledger.Ledger( _trading\_sessions_, _capital\_base_, _data\_frequency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger "Permalink to this definition")

The ledger tracks all orders and transactions as well as the current
state of the portfolio and positions.

portfolio [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.portfolio "Permalink to this definition")

The updated portfolio being managed.

Type:

[zipline.protocol.Portfolio](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio "zipline.protocol.Portfolio")

account [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.account "Permalink to this definition")

The updated account being managed.

Type:

[zipline.protocol.Account](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Account "zipline.protocol.Account")

position\_tracker [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.position_tracker "Permalink to this definition")

The current set of positions.

Type:

[PositionTracker](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker "zipline.finance.ledger.PositionTracker")

todays\_returns [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.todays_returns "Permalink to this definition")

The current day’s returns. In minute emission mode, this is the partial
day’s returns. In daily emission mode, this is
`daily_returns[session]`.

Type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

daily\_returns\_series [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.daily_returns_series "Permalink to this definition")

The daily returns series. Days that have not yet finished will hold
a value of `np.nan`.

Type:

pd.Series

daily\_returns\_array [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.daily_returns_array "Permalink to this definition")

The daily returns as an ndarray. Days that have not yet finished will
hold a value of `np.nan`.

Type:

np.ndarray

orders( _dt=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.orders) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.orders "Permalink to this definition")

Retrieve the dict-form of all of the orders in a given bar or for
the whole simulation.

Parameters:

**dt** ( _pd.Timestamp_ _or_ _None_ _,_ _optional_) – The particular datetime to look up order for. If not passed, or
None is explicitly passed, all of the orders will be returned.

Returns:

**orders** – The order information.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\]

override\_account\_fields( _settled\_cash=sentinel('not\_overridden')_, _accrued\_interest=sentinel('not\_overridden')_, _buying\_power=sentinel('not\_overridden')_, _equity\_with\_loan=sentinel('not\_overridden')_, _total\_positions\_value=sentinel('not\_overridden')_, _total\_positions\_exposure=sentinel('not\_overridden')_, _regt\_equity=sentinel('not\_overridden')_, _regt\_margin=sentinel('not\_overridden')_, _initial\_margin\_requirement=sentinel('not\_overridden')_, _maintenance\_margin\_requirement=sentinel('not\_overridden')_, _available\_funds=sentinel('not\_overridden')_, _excess\_liquidity=sentinel('not\_overridden')_, _cushion=sentinel('not\_overridden')_, _day\_trades\_remaining=sentinel('not\_overridden')_, _leverage=sentinel('not\_overridden')_, _net\_leverage=sentinel('not\_overridden')_, _net\_liquidation=sentinel('not\_overridden')_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.override_account_fields) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.override_account_fields "Permalink to this definition")

Override fields on `self.account`.

_property_ portfolio [#](https://zipline.ml4trading.io/api-reference.html#id8 "Permalink to this definition")

Compute the current portfolio.

Notes

This is cached, repeated access will not recompute the portfolio until
the portfolio may have changed.

process\_commission( _commission_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.process_commission) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_commission "Permalink to this definition")

Process the commission.

Parameters:

**commission** ( _zp.Event_) – The commission being paid.

process\_dividends( _next\_session_, _asset\_finder_, _adjustment\_reader_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.process_dividends) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_dividends "Permalink to this definition")

Process dividends for the next session.

This will earn us any dividends whose ex-date is the next session as
well as paying out any dividends whose pay-date is the next session

process\_order( _order_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.process_order) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_order "Permalink to this definition")

Keep track of an order that was placed.

Parameters:

**order** ( _zp.Order_) – The order to record.

process\_splits( _splits_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.process_splits) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_splits "Permalink to this definition")

Processes a list of splits by modifying any positions as needed.

Parameters:

**splits** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)") _\[_ _(_ [_Asset_](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset "zipline.assets.Asset") _,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)") _)_ _\]_) – A list of splits. Each split is a tuple of (asset, ratio).

process\_transaction( _transaction_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.process_transaction) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_transaction "Permalink to this definition")

Add a transaction to ledger, updating the current state as needed.

Parameters:

**transaction** ( _zp.Transaction_) – The transaction to execute.

transactions( _dt=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.transactions) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.transactions "Permalink to this definition")

Retrieve the dict-form of all of the transactions in a given bar or
for the whole simulation.

Parameters:

**dt** ( _pd.Timestamp_ _or_ _None_ _,_ _optional_) – The particular datetime to look up transactions for. If not passed,
or None is explicitly passed, all of the transactions will be
returned.

Returns:

**transactions** – The transaction information.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")\[ [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.11)")\]

update\_portfolio() [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#Ledger.update_portfolio) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.update_portfolio "Permalink to this definition")

Force a computation of the current portfolio state.

_class_ zipline.protocol.Portfolio( _start\_date=None_, _capital\_base=0.0_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/protocol.html#Portfolio) [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio "Permalink to this definition")

Object providing read-only access to current portfolio state.

Parameters:

- **start\_date** ( _pd.Timestamp_) – The start date for the period being recorded.

- **capital\_base** ( [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")) – The starting value for the portfolio. This will be used as the starting
cash, current cash, and portfolio value.


positions [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.positions "Permalink to this definition")

Dict-like object containing information about currently-held positions.

Type:

zipline.protocol.Positions

cash [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.cash "Permalink to this definition")

Amount of cash currently held in portfolio.

Type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

portfolio\_value [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.portfolio_value "Permalink to this definition")

Current liquidation value of the portfolio’s holdings.
This is equal to `cash + sum(shares * price)`

Type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

starting\_cash [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.starting_cash "Permalink to this definition")

Amount of cash in the portfolio at the start of the backtest.

Type:

[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.11)")

_property_ current\_portfolio\_weights [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.current_portfolio_weights "Permalink to this definition")

Compute each asset’s weight in the portfolio by calculating its held
value divided by the total value of all positions.

Each equity’s value is its price times the number of shares held. Each
futures contract’s value is its unit price times number of shares held
times the multiplier.

_class_ zipline.protocol.Account [\[source\]](https://zipline.ml4trading.io/_modules/zipline/protocol.html#Account) [#](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Account "Permalink to this definition")

The account object tracks information about the trading account. The
values are updated as the algorithm runs and its keys remain unchanged.
If connected to a broker, one can update these values with the trading
account values as reported by the broker.

_class_ zipline.finance.ledger.PositionTracker( _data\_frequency_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#PositionTracker) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker "Permalink to this definition")

The current state of the positions held.

Parameters:

**data\_frequency** ( _{'daily'_ _,_ _'minute'}_) – The data frequency of the simulation.

earn\_dividends( _cash\_dividends_, _stock\_dividends_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#PositionTracker.earn_dividends) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.earn_dividends "Permalink to this definition")

Given a list of dividends whose ex\_dates are all the next trading
day, calculate and store the cash and/or stock payments to be paid on
each dividend’s pay date.

Parameters:

- **cash\_dividends** ( _iterable_ _of_ _(_ _asset_ _,_ _amount_ _,_ _pay\_date_ _)_ _namedtuples_) –

- **stock\_dividends** ( _iterable_ _of_ _(_ _asset_ _,_ _payment\_asset_ _,_ _ratio_ _,_ _pay\_date_ _)_) – namedtuples.


handle\_splits( _splits_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#PositionTracker.handle_splits) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.handle_splits "Permalink to this definition")

Processes a list of splits by modifying any positions as needed.

Parameters:

**splits** ( [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.11)")) – A list of splits. Each split is a tuple of (asset, ratio).

Returns:

**int** – position.

Return type:

The leftover cash from fractional shares after modifying each

pay\_dividends( _next\_trading\_day_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/ledger.html#PositionTracker.pay_dividends) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.pay_dividends "Permalink to this definition")

Returns a cash payment based on the dividends that should be paid out
according to the accumulated bookkeeping of earned, unpaid, and stock
dividends.

_property_ stats [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.stats "Permalink to this definition")

The current status of the positions.

Returns:

**stats** – The current stats position stats.

Return type:

[PositionStats](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats "zipline.finance._finance_ext.PositionStats")

Notes

This is cached, repeated access will not recompute the stats until
the stats may have changed.

_class_ zipline.finance.\_finance\_ext.PositionStats [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats "Permalink to this definition")

Computed values from the current positions.

gross\_exposure [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.gross_exposure "Permalink to this definition")

The gross position exposure.

Type:

float64

gross\_value [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.gross_value "Permalink to this definition")

The gross position value.

Type:

float64

long\_exposure [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.long_exposure "Permalink to this definition")

The exposure of just the long positions.

Type:

float64

long\_value [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.long_value "Permalink to this definition")

The value of just the long positions.

Type:

float64

net\_exposure [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.net_exposure "Permalink to this definition")

The net position exposure.

Type:

float64

net\_value [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.net_value "Permalink to this definition")

The net position value.

Type:

float64

short\_exposure [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.short_exposure "Permalink to this definition")

The exposure of just the short positions.

Type:

float64

short\_value [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.short_value "Permalink to this definition")

The value of just the short positions.

Type:

float64

longs\_count [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.longs_count "Permalink to this definition")

The number of long positions.

Type:

int64

shorts\_count [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.shorts_count "Permalink to this definition")

The number of short positions.

Type:

int64

position\_exposure\_array [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.position_exposure_array "Permalink to this definition")

The exposure of each position in the same order as
`position_tracker.positions`.

Type:

np.ndarray\[float64\]

position\_exposure\_series [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.position_exposure_series "Permalink to this definition")

The exposure of each position in the same order as
`position_tracker.positions`. The index is the numeric sid of each
asset.

Type:

pd.Series\[float64\]

Notes

`position_exposure_array` and `position_exposure_series` share the same
underlying memory. The array interface should be preferred if you are doing
access each minute for better performance.

`position_exposure_array` and `position_exposure_series` may be mutated
when the position tracker next updates the stats. Do not rely on these
objects being preserved across accesses to `stats`. If you need to freeze
the values, you must take a copy.

### Built-in Metrics [\#](https://zipline.ml4trading.io/api-reference.html\#built-in-metrics "Permalink to this heading")

_class_ zipline.finance.metrics.metric.SimpleLedgerField( _ledger\_field_, _packet\_field=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#SimpleLedgerField) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.SimpleLedgerField "Permalink to this definition")

Emit the current value of a ledger field every bar or every session.

Parameters:

- **ledger\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ledger field to read.

- **packet\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the field to populate in the packet. If not provided,
`ledger_field` will be used.


_class_ zipline.finance.metrics.metric.DailyLedgerField( _ledger\_field_, _packet\_field=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#DailyLedgerField) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.DailyLedgerField "Permalink to this definition")

Like [`SimpleLedgerField`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.SimpleLedgerField "zipline.finance.metrics.metric.SimpleLedgerField") but
also puts the current value in the `cumulative_perf` section.

Parameters:

- **ledger\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ledger field to read.

- **packet\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the field to populate in the packet. If not provided,
`ledger_field` will be used.


_class_ zipline.finance.metrics.metric.StartOfPeriodLedgerField( _ledger\_field_, _packet\_field=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#StartOfPeriodLedgerField) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.StartOfPeriodLedgerField "Permalink to this definition")

Keep track of the value of a ledger field at the start of the period.

Parameters:

- **ledger\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ledger field to read.

- **packet\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the field to populate in the packet. If not provided,
`ledger_field` will be used.


_class_ zipline.finance.metrics.metric.StartOfPeriodLedgerField( _ledger\_field_, _packet\_field=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#StartOfPeriodLedgerField) [#](https://zipline.ml4trading.io/api-reference.html#id9 "Permalink to this definition")

Keep track of the value of a ledger field at the start of the period.

Parameters:

- **ledger\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The ledger field to read.

- **packet\_field** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the field to populate in the packet. If not provided,
`ledger_field` will be used.


_class_ zipline.finance.metrics.metric.Returns [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#Returns) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Returns "Permalink to this definition")

Tracks the daily and cumulative returns of the algorithm.

_class_ zipline.finance.metrics.metric.BenchmarkReturnsAndVolatility [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#BenchmarkReturnsAndVolatility) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.BenchmarkReturnsAndVolatility "Permalink to this definition")

Tracks daily and cumulative returns for the benchmark as well as the
volatility of the benchmark returns.

_class_ zipline.finance.metrics.metric.CashFlow [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#CashFlow) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.CashFlow "Permalink to this definition")

Tracks daily and cumulative cash flow.

Notes

For historical reasons, this field is named ‘capital\_used’ in the packets.

_class_ zipline.finance.metrics.metric.Orders [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#Orders) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Orders "Permalink to this definition")

Tracks daily orders.

_class_ zipline.finance.metrics.metric.Transactions [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#Transactions) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Transactions "Permalink to this definition")

Tracks daily transactions.

_class_ zipline.finance.metrics.metric.Positions [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#Positions) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Positions "Permalink to this definition")

Tracks daily positions.

_class_ zipline.finance.metrics.metric.ReturnsStatistic( _function_, _field\_name=None_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#ReturnsStatistic) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.ReturnsStatistic "Permalink to this definition")

A metric that reports an end of simulation scalar or time series
computed from the algorithm returns.

Parameters:

- **function** ( _callable_) – The function to call on the daily returns.

- **field\_name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The name of the field. If not provided, it will be
`function.__name__`.


_class_ zipline.finance.metrics.metric.AlphaBeta [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#AlphaBeta) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.AlphaBeta "Permalink to this definition")

End of simulation alpha and beta to the benchmark.

_class_ zipline.finance.metrics.metric.MaxLeverage [\[source\]](https://zipline.ml4trading.io/_modules/zipline/finance/metrics/metric.html#MaxLeverage) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.MaxLeverage "Permalink to this definition")

Tracks the maximum account leverage.

### Metrics Sets [\#](https://zipline.ml4trading.io/api-reference.html\#metrics-sets "Permalink to this heading")

zipline.finance.metrics.register( _name_, _function=None_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.register "Permalink to this definition")

Register a new metrics set.

Parameters:

- **name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the metrics set

- **function** ( _callable_) – The callable which produces the metrics set.


Notes

This may be used as a decorator if only `name` is passed.

See also

`zipline.finance.metrics.get_metrics_set`, `zipline.finance.metrics.unregister_metrics_set`

zipline.finance.metrics.load( _name_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.load "Permalink to this definition")

Return an instance of the metrics set registered with the given name.

Returns:

**metrics** – A new instance of the metrics set.

Return type:

[set](https://docs.python.org/3/library/stdtypes.html#set "(in Python v3.11)")\[Metric\]

Raises:

[**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.11)") – Raised when no metrics set is registered to `name`

zipline.finance.metrics.unregister( _name_) [#](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.unregister "Permalink to this definition")

Unregister an existing metrics set.

Parameters:

**name** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The name of the metrics set

See also

`zipline.finance.metrics.register_metrics_set`

zipline.data.finance.metrics.metrics\_sets [#](https://zipline.ml4trading.io/api-reference.html#zipline.data.finance.metrics.metrics_sets "Permalink to this definition")

The metrics sets that have been registered as a mapping from metrics set name
to load function. This mapping is immutable and may only be updated through
[`register()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.register "zipline.finance.metrics.register") or
[`unregister()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.unregister "zipline.finance.metrics.unregister").

## Utilities [\#](https://zipline.ml4trading.io/api-reference.html\#utilities "Permalink to this heading")

### Caching [\#](https://zipline.ml4trading.io/api-reference.html\#caching "Permalink to this heading")

_class_ zipline.utils.cache.CachedObject( _value_, _expires_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cache.html#CachedObject) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.CachedObject "Permalink to this definition")

A simple struct for maintaining a cached object with an expiration date.

Parameters:

- **value** ( [_object_](https://docs.python.org/3/library/functions.html#object "(in Python v3.11)")) – The object to cache.

- **expires** ( _datetime-like_) – Expiration date of value. The cache is considered invalid for dates
**strictly greater** than expires.


Examples

```
>>> from pandas import Timestamp, Timedelta
>>> expires = Timestamp('2014', tz='UTC')
>>> obj = CachedObject(1, expires)
>>> obj.unwrap(expires - Timedelta('1 minute'))
1
>>> obj.unwrap(expires)
1
>>> obj.unwrap(expires + Timedelta('1 minute'))
...
Traceback (most recent call last):
    ...
Expired: 2014-01-01 00:00:00+00:00

```

_class_ zipline.utils.cache.ExpiringCache( _cache=None_, _cleanup=<functionExpiringCache.<lambda>>_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cache.html#ExpiringCache) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.ExpiringCache "Permalink to this definition")

A cache of multiple CachedObjects, which returns the wrapped the value
or raises and deletes the CachedObject if the value has expired.

Parameters:

- **cache** ( _dict-like_ _,_ _optional_) – An instance of a dict-like object which needs to support at least:
\_\_del\_\_, \_\_getitem\_\_, \_\_setitem\_\_
If None, than a dict is used as a default.

- **cleanup** ( _callable_ _,_ _optional_) – A method that takes a single argument, a cached object, and is called
upon expiry of the cached object, prior to deleting the object. If not
provided, defaults to a no-op.


Examples

```
>>> from pandas import Timestamp, Timedelta
>>> expires = Timestamp('2014', tz='UTC')
>>> value = 1
>>> cache = ExpiringCache()
>>> cache.set('foo', value, expires)
>>> cache.get('foo', expires - Timedelta('1 minute'))
1
>>> cache.get('foo', expires + Timedelta('1 minute'))
Traceback (most recent call last):
    ...
KeyError: 'foo'

```

_class_ zipline.utils.cache.dataframe\_cache( _path=None_, _lock=None_, _clean\_on\_failure=True_, _serialization='pickle'_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cache.html#dataframe_cache) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.dataframe_cache "Permalink to this definition")

A disk-backed cache for dataframes.

`dataframe_cache` is a mutable mapping from string names to pandas
DataFrame objects.
This object may be used as a context manager to delete the cache directory
on exit.

Parameters:

- **path** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)") _,_ _optional_) – The directory path to the cache. Files will be written as
`path/<keyname>`.

- **lock** ( _Lock_ _,_ _optional_) – Thread lock for multithreaded/multiprocessed access to the cache.
If not provided no locking will be used.

- **clean\_on\_failure** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)") _,_ _optional_) – Should the directory be cleaned up if an exception is raised in the
context manager.

- **serialize** ( _{'msgpack'_ _,_ _'pickle:<n>'}_ _,_ _optional_) – How should the data be serialized. If `'pickle'` is passed, an
optional pickle protocol can be passed like: `'pickle:3'` which says
to use pickle protocol 3.


Notes

The syntax `cache[:]` will load all key:value pairs into memory as a
dictionary.
The cache uses a temporary file format that is subject to change between
versions of zipline.

_class_ zipline.utils.cache.working\_file( _final\_path_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cache.html#working_file) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.working_file "Permalink to this definition")

A context manager for managing a temporary file that will be moved
to a non-temporary location if no exceptions are raised in the context.

Parameters:

- **final\_path** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The location to move the file when committing.

- **\*args** – Forwarded to NamedTemporaryFile.

- **\*\*kwargs** – Forwarded to NamedTemporaryFile.


Notes

The file is moved on \_\_exit\_\_ if there are no exceptions.
`working_file` uses [`shutil.move()`](https://docs.python.org/3/library/shutil.html#shutil.move "(in Python v3.11)") to move the actual files,
meaning it has as strong of guarantees as [`shutil.move()`](https://docs.python.org/3/library/shutil.html#shutil.move "(in Python v3.11)").

_class_ zipline.utils.cache.working\_dir( _final\_path_, _\*args_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cache.html#working_dir) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.working_dir "Permalink to this definition")

A context manager for managing a temporary directory that will be moved
to a non-temporary location if no exceptions are raised in the context.

Parameters:

- **final\_path** ( [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.11)")) – The location to move the file when committing.

- **\*args** – Forwarded to tmp\_dir.

- **\*\*kwargs** – Forwarded to tmp\_dir.


Notes

The file is moved on \_\_exit\_\_ if there are no exceptions.
`working_dir` uses `dir_util.copy_tree()` to move the actual files,
meaning it has as strong of guarantees as `dir_util.copy_tree()`.

### Command Line [\#](https://zipline.ml4trading.io/api-reference.html\#command-line "Permalink to this heading")

zipline.utils.cli.maybe\_show\_progress( _it_, _show\_progress_, _\*\*kwargs_) [\[source\]](https://zipline.ml4trading.io/_modules/zipline/utils/cli.html#maybe_show_progress) [#](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cli.maybe_show_progress "Permalink to this definition")

Optionally show a progress bar for the given iterator.

Parameters:

- **it** ( _iterable_) – The underlying iterator.

- **show\_progress** ( [_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.11)")) – Should progress be shown.

- **\*\*kwargs** – Forwarded to the click progress bar.


Returns:

**itercontext** – A context manager whose enter is the actual iterator to use.

Return type:

context manager

Examples

```
with maybe_show_progress([1, 2, 3], True) as ns:
     for n in ns:
         ...

```

[previous\\
\\
Development](https://zipline.ml4trading.io/development-guidelines.html "previous page") [next\\
\\
Releases](https://zipline.ml4trading.io/releases.html "next page")

On this page


- [Running a Backtest](https://zipline.ml4trading.io/api-reference.html#running-a-backtest)
  - [`run_algorithm()`](https://zipline.ml4trading.io/api-reference.html#zipline.run_algorithm)
- [Trading Algorithm API](https://zipline.ml4trading.io/api-reference.html#trading-algorithm-api)
  - [Data Object](https://zipline.ml4trading.io/api-reference.html#data-object)
    - [`BarData`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData)
      - [`BarData.can_trade()`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.can_trade)
      - [`BarData.current()`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.current)
      - [`BarData.history()`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.history)
      - [`BarData.is_stale()`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.BarData.is_stale)
  - [Scheduling Functions](https://zipline.ml4trading.io/api-reference.html#scheduling-functions)
    - [`schedule_function()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.schedule_function)
    - [`date_rules`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules)
      - [`date_rules.every_day()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.every_day)
      - [`date_rules.month_end()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.month_end)
      - [`date_rules.month_start()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.month_start)
      - [`date_rules.week_end()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.week_end)
      - [`date_rules.week_start()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.date_rules.week_start)
    - [`time_rules`](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules)
      - [`time_rules.every_minute`](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.every_minute)
      - [`time_rules.market_close()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.market_close)
      - [`time_rules.market_open()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.time_rules.market_open)
  - [Orders](https://zipline.ml4trading.io/api-reference.html#orders)
    - [`order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order)
    - [`order_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_value)
    - [`order_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_percent)
    - [`order_target()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target)
    - [`order_target_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_value)
    - [`order_target_percent()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.order_target_percent)
    - [`ExecutionStyle`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle)
      - [`ExecutionStyle.exchange`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.exchange)
      - [`ExecutionStyle.get_limit_price()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.get_limit_price)
      - [`ExecutionStyle.get_stop_price()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.ExecutionStyle.get_stop_price)
    - [`MarketOrder`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.MarketOrder)
    - [`LimitOrder`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.LimitOrder)
    - [`StopOrder`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.StopOrder)
    - [`StopLimitOrder`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.execution.StopLimitOrder)
    - [`get_order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_order)
    - [`get_open_orders()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_open_orders)
    - [`cancel_order()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.cancel_order)
    - [Order Cancellation Policies](https://zipline.ml4trading.io/api-reference.html#order-cancellation-policies)
      - [`set_cancel_policy()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_cancel_policy)
      - [`CancelPolicy`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.cancel_policy.CancelPolicy)
        - [`CancelPolicy.should_cancel()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.cancel_policy.CancelPolicy.should_cancel)
      - [`EODCancel()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.EODCancel)
      - [`NeverCancel()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.NeverCancel)
  - [Assets](https://zipline.ml4trading.io/api-reference.html#assets)
    - [`symbol()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.symbol)
    - [`symbols()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.symbols)
    - [`future_symbol()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.future_symbol)
    - [`set_symbol_lookup_date()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_symbol_lookup_date)
    - [`sid()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.sid)
  - [Trading Controls](https://zipline.ml4trading.io/api-reference.html#trading-controls)
    - [`set_do_not_order_list()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_do_not_order_list)
    - [`set_long_only()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_long_only)
    - [`set_max_leverage()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_leverage)
    - [`set_max_order_count()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_order_count)
    - [`set_max_order_size()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_order_size)
    - [`set_max_position_size()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_max_position_size)
  - [Simulation Parameters](https://zipline.ml4trading.io/api-reference.html#simulation-parameters)
    - [`set_benchmark()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_benchmark)
    - [Commission Models](https://zipline.ml4trading.io/api-reference.html#commission-models)
      - [`set_commission()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_commission)
      - [`CommissionModel`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel)
        - [`CommissionModel.calculate()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.CommissionModel.calculate)
      - [`PerShare`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerShare)
      - [`PerTrade`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerTrade)
      - [`PerDollar`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.commission.PerDollar)
    - [Slippage Models](https://zipline.ml4trading.io/api-reference.html#slippage-models)
      - [`set_slippage()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.set_slippage)
      - [`SlippageModel`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel)
        - [`SlippageModel.process_order()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel.process_order)
        - [`SlippageModel.volume_for_bar`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.SlippageModel.volume_for_bar)
        - [`SlippageModel.process_order()`](https://zipline.ml4trading.io/api-reference.html#id0)
      - [`FixedSlippage`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.FixedSlippage)
      - [`VolumeShareSlippage`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.slippage.VolumeShareSlippage)
  - [Pipeline](https://zipline.ml4trading.io/api-reference.html#pipeline)
    - [`attach_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.attach_pipeline)
    - [`pipeline_output()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.pipeline_output)
  - [Miscellaneous](https://zipline.ml4trading.io/api-reference.html#miscellaneous)
    - [`record()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.record)
    - [`get_environment()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.get_environment)
    - [`fetch_csv()`](https://zipline.ml4trading.io/api-reference.html#zipline.api.fetch_csv)
- [Blotters](https://zipline.ml4trading.io/api-reference.html#blotters)
  - [`Blotter`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter)
    - [`Blotter.batch_order()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.batch_order)
    - [`Blotter.cancel()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.cancel)
    - [`Blotter.cancel_all_orders_for_asset()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.cancel_all_orders_for_asset)
    - [`Blotter.get_transactions()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.get_transactions)
    - [`Blotter.hold()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.hold)
    - [`Blotter.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.order)
    - [`Blotter.process_splits()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.process_splits)
    - [`Blotter.prune_orders()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.prune_orders)
    - [`Blotter.reject()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.blotter.Blotter.reject)
  - [`SimulationBlotter`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter)
    - [`SimulationBlotter.cancel()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.cancel)
    - [`SimulationBlotter.cancel_all_orders_for_asset()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.cancel_all_orders_for_asset)
    - [`SimulationBlotter.get_transactions()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.get_transactions)
    - [`SimulationBlotter.hold()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.hold)
    - [`SimulationBlotter.order()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.order)
    - [`SimulationBlotter.process_splits()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.process_splits)
    - [`SimulationBlotter.prune_orders()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.prune_orders)
    - [`SimulationBlotter.reject()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.blotter.SimulationBlotter.reject)
- [Pipeline API](https://zipline.ml4trading.io/api-reference.html#pipeline-api)
  - [`Pipeline`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline)
    - [`Pipeline.add()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.add)
    - [`Pipeline.domain()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.domain)
    - [`Pipeline.remove()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.remove)
    - [`Pipeline.set_screen()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.set_screen)
    - [`Pipeline.show_graph()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.show_graph)
    - [`Pipeline.to_execution_plan()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.to_execution_plan)
    - [`Pipeline.to_simple_graph()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.to_simple_graph)
    - [`Pipeline.columns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.columns)
    - [`Pipeline.screen`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Pipeline.screen)
  - [`CustomFactor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.CustomFactor)
    - [`CustomFactor.dtype`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.CustomFactor.dtype)
  - [`Filter`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter)
    - [`Filter.__and__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.__and__)
    - [`Filter.__or__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.__or__)
    - [`Filter.if_else()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Filter.if_else)
  - [`Factor`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor)
    - [`Factor.eq()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.eq)
    - [`Factor.demean()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.demean)
    - [`Factor.zscore()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.zscore)
    - [`Factor.rank()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.rank)
    - [`Factor.pearsonr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.pearsonr)
    - [`Factor.spearmanr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.spearmanr)
    - [`Factor.linear_regression()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.linear_regression)
    - [`Factor.winsorize()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.winsorize)
    - [`Factor.quantiles()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quantiles)
    - [`Factor.quartiles()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quartiles)
    - [`Factor.quintiles()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.quintiles)
    - [`Factor.deciles()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.deciles)
    - [`Factor.top()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.top)
    - [`Factor.bottom()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.bottom)
    - [`Factor.percentile_between()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.percentile_between)
    - [`Factor.isnan()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.isnan)
    - [`Factor.notnan()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.notnan)
    - [`Factor.isfinite()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.isfinite)
    - [`Factor.clip()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.clip)
    - [`Factor.clip()`](https://zipline.ml4trading.io/api-reference.html#id2)
    - [`Factor.__add__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__add__)
    - [`Factor.__sub__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__sub__)
    - [`Factor.__mul__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__mul__)
    - [`Factor.__div__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__div__)
    - [`Factor.__mod__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__mod__)
    - [`Factor.__pow__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__pow__)
    - [`Factor.__lt__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__lt__)
    - [`Factor.__le__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__le__)
    - [`Factor.__ne__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__ne__)
    - [`Factor.__ge__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__ge__)
    - [`Factor.__gt__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.__gt__)
    - [`Factor.fillna()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.fillna)
    - [`Factor.mean()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.mean)
    - [`Factor.stddev()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.stddev)
    - [`Factor.max()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.max)
    - [`Factor.min()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.min)
    - [`Factor.median()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.median)
    - [`Factor.sum()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Factor.sum)
  - [`Term`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term)
    - [`Term.graph_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term.graph_repr)
    - [`Term.recursive_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.Term.recursive_repr)
  - [`DataSet`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet)
    - [`DataSet.get_column()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSet.get_column)
  - [`Column`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column)
    - [`Column.bind()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.Column.bind)
  - [`BoundColumn`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn)
    - [`BoundColumn.dtype`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.dtype)
    - [`BoundColumn.latest`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.latest)
    - [`BoundColumn.dataset`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.dataset)
    - [`BoundColumn.name`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.name)
    - [`BoundColumn.metadata`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.metadata)
    - [`BoundColumn.currency_aware`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.currency_aware)
    - [`BoundColumn.currency_aware`](https://zipline.ml4trading.io/api-reference.html#id3)
    - [`BoundColumn.currency_conversion`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.currency_conversion)
    - [`BoundColumn.dataset`](https://zipline.ml4trading.io/api-reference.html#id4)
    - [`BoundColumn.fx()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.fx)
    - [`BoundColumn.graph_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.graph_repr)
    - [`BoundColumn.metadata`](https://zipline.ml4trading.io/api-reference.html#id5)
    - [`BoundColumn.name`](https://zipline.ml4trading.io/api-reference.html#id6)
    - [`BoundColumn.qualname`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.qualname)
    - [`BoundColumn.recursive_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.recursive_repr)
    - [`BoundColumn.specialize()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.specialize)
    - [`BoundColumn.unspecialize()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.BoundColumn.unspecialize)
  - [`DataSetFamily`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily)
    - [`DataSetFamily.slice()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.DataSetFamily.slice)
  - [`EquityPricing`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing)
    - [`EquityPricing.close`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.close)
    - [`EquityPricing.high`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.high)
    - [`EquityPricing.low`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.low)
    - [`EquityPricing.open`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.open)
    - [`EquityPricing.volume`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.data.EquityPricing.volume)
  - [Built-in Factors](https://zipline.ml4trading.io/api-reference.html#built-in-factors)
    - [`AverageDollarVolume`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.AverageDollarVolume)
      - [`AverageDollarVolume.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.AverageDollarVolume.compute)
    - [`BollingerBands`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BollingerBands)
      - [`BollingerBands.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BollingerBands.compute)
    - [`BusinessDaysSincePreviousEvent`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysSincePreviousEvent)
      - [`BusinessDaysSincePreviousEvent.dtype`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysSincePreviousEvent.dtype)
    - [`BusinessDaysUntilNextEvent`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysUntilNextEvent)
      - [`BusinessDaysUntilNextEvent.dtype`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.BusinessDaysUntilNextEvent.dtype)
    - [`DailyReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.DailyReturns)
    - [`ExponentialWeightedMovingAverage`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingAverage)
      - [`ExponentialWeightedMovingAverage.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingAverage.compute)
    - [`ExponentialWeightedMovingStdDev`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingStdDev)
      - [`ExponentialWeightedMovingStdDev.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.ExponentialWeightedMovingStdDev.compute)
    - [`Latest`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Latest)
      - [`Latest.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Latest.compute)
    - [`MACDSignal`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MACDSignal)
    - [`MaxDrawdown`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MaxDrawdown)
      - [`MaxDrawdown.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.MaxDrawdown.compute)
    - [`Returns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns)
      - [`Returns.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.Returns.compute)
    - [`RollingPearson`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearson)
      - [`RollingPearson.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearson.compute)
    - [`RollingSpearman`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearman)
      - [`RollingSpearman.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearman.compute)
    - [`RollingLinearRegressionOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingLinearRegressionOfReturns)
    - [`RollingPearsonOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingPearsonOfReturns)
    - [`RollingSpearmanOfReturns`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RollingSpearmanOfReturns)
    - [`SimpleBeta`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta)
      - [`SimpleBeta.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.compute)
      - [`SimpleBeta.dtype`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.dtype)
      - [`SimpleBeta.graph_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.graph_repr)
      - [`SimpleBeta.target`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleBeta.target)
    - [`RSI`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RSI)
      - [`RSI.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.RSI.compute)
    - [`SimpleMovingAverage`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleMovingAverage)
      - [`SimpleMovingAverage.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.SimpleMovingAverage.compute)
    - [`VWAP`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.VWAP)
    - [`WeightedAverageValue`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.WeightedAverageValue)
      - [`WeightedAverageValue.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.WeightedAverageValue.compute)
    - [`PercentChange`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PercentChange)
      - [`PercentChange.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PercentChange.compute)
    - [`PeerCount`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PeerCount)
      - [`PeerCount.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.factors.PeerCount.compute)
  - [Built-in Filters](https://zipline.ml4trading.io/api-reference.html#built-in-filters)
    - [`All`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.All)
      - [`All.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.All.compute)
    - [`AllPresent`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AllPresent)
      - [`AllPresent.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AllPresent.compute)
    - [`Any`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.Any)
      - [`Any.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.Any.compute)
    - [`AtLeastN`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AtLeastN)
      - [`AtLeastN.compute()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.AtLeastN.compute)
    - [`SingleAsset`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.SingleAsset)
      - [`SingleAsset.graph_repr()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.SingleAsset.graph_repr)
    - [`StaticAssets`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.StaticAssets)
    - [`StaticSids`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.filters.StaticSids)
  - [Pipeline Engine](https://zipline.ml4trading.io/api-reference.html#pipeline-engine)
    - [`PipelineEngine`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine)
      - [`PipelineEngine.run_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_pipeline)
      - [`PipelineEngine.run_chunked_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.PipelineEngine.run_chunked_pipeline)
    - [`SimplePipelineEngine`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine)
      - [`SimplePipelineEngine.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.__init__)
      - [`SimplePipelineEngine.run_chunked_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.run_chunked_pipeline)
      - [`SimplePipelineEngine.run_pipeline()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.SimplePipelineEngine.run_pipeline)
    - [`default_populate_initial_workspace()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.engine.default_populate_initial_workspace)
  - [Data Loaders](https://zipline.ml4trading.io/api-reference.html#data-loaders)
    - [`PipelineLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader)
      - [`PipelineLoader.load_adjusted_array()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader.load_adjusted_array)
      - [`PipelineLoader.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.base.PipelineLoader.__init__)
    - [`DataFrameLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader)
      - [`DataFrameLoader.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.__init__)
      - [`DataFrameLoader.format_adjustments()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.format_adjustments)
      - [`DataFrameLoader.load_adjusted_array()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.frame.DataFrameLoader.load_adjusted_array)
    - [`EquityPricingLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader)
      - [`EquityPricingLoader.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.EquityPricingLoader.__init__)
    - [`USEquityPricingLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.equity_pricing_loader.USEquityPricingLoader)
    - [`EventsLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.events.EventsLoader)
      - [`EventsLoader.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.events.EventsLoader.__init__)
    - [`EarningsEstimatesLoader`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.earnings_estimates.EarningsEstimatesLoader)
      - [`EarningsEstimatesLoader.__init__()`](https://zipline.ml4trading.io/api-reference.html#zipline.pipeline.loaders.earnings_estimates.EarningsEstimatesLoader.__init__)
- [Exchange and Asset Metadata](https://zipline.ml4trading.io/api-reference.html#exchange-and-asset-metadata)
  - [`ExchangeInfo`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo)
    - [`ExchangeInfo.name`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.name)
    - [`ExchangeInfo.canonical_name`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.canonical_name)
    - [`ExchangeInfo.country_code`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.country_code)
    - [`ExchangeInfo.calendar`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.ExchangeInfo.calendar)
    - [`ExchangeInfo.calendar`](https://zipline.ml4trading.io/api-reference.html#id7)
  - [`Asset`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset)
    - [`Asset.sid`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.sid)
    - [`Asset.symbol`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.symbol)
    - [`Asset.asset_name`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.asset_name)
    - [`Asset.exchange`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange)
    - [`Asset.exchange_full`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange_full)
    - [`Asset.exchange_info`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.exchange_info)
    - [`Asset.country_code`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.country_code)
    - [`Asset.start_date`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.start_date)
    - [`Asset.end_date`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.end_date)
    - [`Asset.tick_size`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.tick_size)
    - [`Asset.auto_close_date`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.auto_close_date)
    - [`Asset.from_dict()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.from_dict)
    - [`Asset.is_alive_for_session()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.is_alive_for_session)
    - [`Asset.is_exchange_open()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.is_exchange_open)
    - [`Asset.to_dict()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Asset.to_dict)
  - [`Equity`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Equity)
  - [`Future`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future)
    - [`Future.to_dict()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.Future.to_dict)
  - [`AssetConvertible`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetConvertible)
- [Trading Calendar API](https://zipline.ml4trading.io/api-reference.html#trading-calendar-api)
- [Data API](https://zipline.ml4trading.io/api-reference.html#data-api)
  - [Writers](https://zipline.ml4trading.io/api-reference.html#writers)
    - [`BcolzDailyBarWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter)
      - [`BcolzDailyBarWriter.write()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter.write)
      - [`BcolzDailyBarWriter.write_csvs()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarWriter.write_csvs)
    - [`SQLiteAdjustmentWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter)
      - [`SQLiteAdjustmentWriter.calc_dividend_ratios()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.calc_dividend_ratios)
      - [`SQLiteAdjustmentWriter.write()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write)
      - [`SQLiteAdjustmentWriter.write_dividend_data()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write_dividend_data)
      - [`SQLiteAdjustmentWriter.write_dividend_payouts()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentWriter.write_dividend_payouts)
    - [`AssetDBWriter`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter)
      - [`AssetDBWriter.init_db()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.init_db)
      - [`AssetDBWriter.write()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.write)
      - [`AssetDBWriter.write_direct()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetDBWriter.write_direct)
  - [Readers](https://zipline.ml4trading.io/api-reference.html#readers)
    - [`BcolzDailyBarReader`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader)
      - [`BcolzDailyBarReader.attributes`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.attributes)
      - [`BcolzDailyBarReader.first_row`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.first_row)
      - [`BcolzDailyBarReader.last_row`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.last_row)
      - [`BcolzDailyBarReader.calendar_offset`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.calendar_offset)
      - [`BcolzDailyBarReader.start_session_ns`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.start_session_ns)
      - [`BcolzDailyBarReader.end_session_ns`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.end_session_ns)
      - [`BcolzDailyBarReader.calendar_name`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.calendar_name)
      - [`BcolzDailyBarReader.currency_codes()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.currency_codes)
      - [`BcolzDailyBarReader.get_last_traded_dt()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.get_last_traded_dt)
      - [`BcolzDailyBarReader.get_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.get_value)
      - [`BcolzDailyBarReader.last_available_dt`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.last_available_dt)
      - [`BcolzDailyBarReader.load_raw_arrays()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.load_raw_arrays)
      - [`BcolzDailyBarReader.sid_day_index()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bcolz_daily_bars.BcolzDailyBarReader.sid_day_index)
    - [`SQLiteAdjustmentReader`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader)
      - [`SQLiteAdjustmentReader.load_adjustments()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader.load_adjustments)
      - [`SQLiteAdjustmentReader.unpack_db_to_component_dfs()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.adjustments.SQLiteAdjustmentReader.unpack_db_to_component_dfs)
    - [`AssetFinder`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder)
      - [`AssetFinder.equities_sids`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids)
      - [`AssetFinder.equities_sids_for_country_code()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids_for_country_code)
      - [`AssetFinder.equities_sids_for_exchange_name()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.equities_sids_for_exchange_name)
      - [`AssetFinder.futures_sids`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.futures_sids)
      - [`AssetFinder.get_supplementary_field()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.get_supplementary_field)
      - [`AssetFinder.group_by_type()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.group_by_type)
      - [`AssetFinder.lifetimes()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lifetimes)
      - [`AssetFinder.lookup_asset_types()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_asset_types)
      - [`AssetFinder.lookup_future_symbol()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_future_symbol)
      - [`AssetFinder.lookup_generic()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_generic)
      - [`AssetFinder.lookup_symbol()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_symbol)
      - [`AssetFinder.lookup_symbols()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.lookup_symbols)
      - [`AssetFinder.retrieve_all()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_all)
      - [`AssetFinder.retrieve_asset()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_asset)
      - [`AssetFinder.retrieve_equities()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_equities)
      - [`AssetFinder.retrieve_futures_contracts()`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.retrieve_futures_contracts)
      - [`AssetFinder.sids`](https://zipline.ml4trading.io/api-reference.html#zipline.assets.AssetFinder.sids)
    - [`DataPortal`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal)
      - [`DataPortal.get_adjusted_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_adjusted_value)
      - [`DataPortal.get_adjustments()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_adjustments)
      - [`DataPortal.get_current_future_chain()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_current_future_chain)
      - [`DataPortal.get_fetcher_assets()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_fetcher_assets)
      - [`DataPortal.get_history_window()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_history_window)
      - [`DataPortal.get_last_traded_dt()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_last_traded_dt)
      - [`DataPortal.get_scalar_asset_spot_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_scalar_asset_spot_value)
      - [`DataPortal.get_splits()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_splits)
      - [`DataPortal.get_spot_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_spot_value)
      - [`DataPortal.get_stock_dividends()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.get_stock_dividends)
      - [`DataPortal.handle_extra_source()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.data_portal.DataPortal.handle_extra_source)
    - [`BenchmarkSource`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource)
      - [`BenchmarkSource.daily_returns()`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.daily_returns)
      - [`BenchmarkSource.get_range()`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.get_range)
      - [`BenchmarkSource.get_value()`](https://zipline.ml4trading.io/api-reference.html#zipline.sources.benchmark_source.BenchmarkSource.get_value)
  - [Bundles](https://zipline.ml4trading.io/api-reference.html#bundles)
    - [`register()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.register)
    - [`ingest()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.ingest)
    - [`load()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.load)
    - [`unregister()`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.unregister)
    - [`zipline.data.bundles.bundles`](https://zipline.ml4trading.io/api-reference.html#zipline.data.bundles.bundles)
- [Risk Metrics](https://zipline.ml4trading.io/api-reference.html#risk-metrics)
  - [Algorithm State](https://zipline.ml4trading.io/api-reference.html#algorithm-state)
    - [`Ledger`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger)
      - [`Ledger.portfolio`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.portfolio)
      - [`Ledger.account`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.account)
      - [`Ledger.position_tracker`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.position_tracker)
      - [`Ledger.todays_returns`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.todays_returns)
      - [`Ledger.daily_returns_series`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.daily_returns_series)
      - [`Ledger.daily_returns_array`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.daily_returns_array)
      - [`Ledger.orders()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.orders)
      - [`Ledger.override_account_fields()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.override_account_fields)
      - [`Ledger.portfolio`](https://zipline.ml4trading.io/api-reference.html#id8)
      - [`Ledger.process_commission()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_commission)
      - [`Ledger.process_dividends()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_dividends)
      - [`Ledger.process_order()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_order)
      - [`Ledger.process_splits()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_splits)
      - [`Ledger.process_transaction()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.process_transaction)
      - [`Ledger.transactions()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.transactions)
      - [`Ledger.update_portfolio()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.Ledger.update_portfolio)
    - [`Portfolio`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio)
      - [`Portfolio.positions`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.positions)
      - [`Portfolio.cash`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.cash)
      - [`Portfolio.portfolio_value`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.portfolio_value)
      - [`Portfolio.starting_cash`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.starting_cash)
      - [`Portfolio.current_portfolio_weights`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Portfolio.current_portfolio_weights)
    - [`Account`](https://zipline.ml4trading.io/api-reference.html#zipline.protocol.Account)
    - [`PositionTracker`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker)
      - [`PositionTracker.earn_dividends()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.earn_dividends)
      - [`PositionTracker.handle_splits()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.handle_splits)
      - [`PositionTracker.pay_dividends()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.pay_dividends)
      - [`PositionTracker.stats`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.ledger.PositionTracker.stats)
    - [`PositionStats`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats)
      - [`PositionStats.gross_exposure`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.gross_exposure)
      - [`PositionStats.gross_value`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.gross_value)
      - [`PositionStats.long_exposure`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.long_exposure)
      - [`PositionStats.long_value`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.long_value)
      - [`PositionStats.net_exposure`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.net_exposure)
      - [`PositionStats.net_value`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.net_value)
      - [`PositionStats.short_exposure`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.short_exposure)
      - [`PositionStats.short_value`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.short_value)
      - [`PositionStats.longs_count`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.longs_count)
      - [`PositionStats.shorts_count`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.shorts_count)
      - [`PositionStats.position_exposure_array`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.position_exposure_array)
      - [`PositionStats.position_exposure_series`](https://zipline.ml4trading.io/api-reference.html#zipline.finance._finance_ext.PositionStats.position_exposure_series)
  - [Built-in Metrics](https://zipline.ml4trading.io/api-reference.html#built-in-metrics)
    - [`SimpleLedgerField`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.SimpleLedgerField)
    - [`DailyLedgerField`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.DailyLedgerField)
    - [`StartOfPeriodLedgerField`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.StartOfPeriodLedgerField)
    - [`StartOfPeriodLedgerField`](https://zipline.ml4trading.io/api-reference.html#id9)
    - [`Returns`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Returns)
    - [`BenchmarkReturnsAndVolatility`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.BenchmarkReturnsAndVolatility)
    - [`CashFlow`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.CashFlow)
    - [`Orders`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Orders)
    - [`Transactions`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Transactions)
    - [`Positions`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.Positions)
    - [`ReturnsStatistic`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.ReturnsStatistic)
    - [`AlphaBeta`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.AlphaBeta)
    - [`MaxLeverage`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.metric.MaxLeverage)
  - [Metrics Sets](https://zipline.ml4trading.io/api-reference.html#metrics-sets)
    - [`register()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.register)
    - [`load()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.load)
    - [`unregister()`](https://zipline.ml4trading.io/api-reference.html#zipline.finance.metrics.unregister)
    - [`zipline.data.finance.metrics.metrics_sets`](https://zipline.ml4trading.io/api-reference.html#zipline.data.finance.metrics.metrics_sets)
- [Utilities](https://zipline.ml4trading.io/api-reference.html#utilities)
  - [Caching](https://zipline.ml4trading.io/api-reference.html#caching)
    - [`CachedObject`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.CachedObject)
    - [`ExpiringCache`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.ExpiringCache)
    - [`dataframe_cache`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.dataframe_cache)
    - [`working_file`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.working_file)
    - [`working_dir`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cache.working_dir)
  - [Command Line](https://zipline.ml4trading.io/api-reference.html#command-line)
    - [`maybe_show_progress()`](https://zipline.ml4trading.io/api-reference.html#zipline.utils.cli.maybe_show_progress)

[Show Source](https://zipline.ml4trading.io/_sources/api-reference.rst.txt)


© Copyright 2020, Quantopian Inc..


Created using [Sphinx](https://www.sphinx-doc.org/) 7.0.1.


Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.13.3.