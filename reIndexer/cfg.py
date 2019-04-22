import logging
import pandas as pd


class config:
    # Backtest time window
    tz_local = 'US/Eastern'
    backtest_start = pd.to_datetime('2018-01-01').tz_localize(tz_local)
    backtest_end = pd.to_datetime('2018-03-01').tz_localize(tz_local)

    # Computation windows
    rebalancing_period = 30  # days
    backtest_frequency = 'daily'  # Must be either 'daily' or 'minute'


    # Portfolio configuration
    capital_base = 1e10

    # Current sector universe (set at backtest initialization)
    current_universe = None
