import logging
import pandas as pd


class config:
    # Backtest time window
    tz_local = 'US/Eastern'
    backtest_start = pd.to_datetime('2015-01-01').tz_localize(tz_local)
    backtest_end = pd.to_datetime('2018-03-01').tz_localize(tz_local)

    # Computation windows
    port_rebalancing_period = 21  # days
    backtest_frequency = 'daily'  # Must be either 'daily' or 'minute'


    # Portfolio configuration
    capital_base = 1e10
    optim_tol = 1e-6  # Optimization tolerance

    # Sector universe (set at backtest initialization)
    sector_universe = None

    # Synthetic ETF
    setf_base_value = 125.0  # Identical to NASDAQ base value
    setf_lookback_window = 252  # days (1 work year)
    setf_data_frequency = '1d'  # '1m' or '1d' for minute/daily respectively
    setf_restructure_window = setf_lookback_window / 12  # days (12 times / year)

    # Restructuring and rebalancing triggers
    # NOTE: The 'week' key indicates the week of the rebalance; counting here
    #       starts at 1; i.e., 'week': 1 indicates the first week of the month.
    # NOTE: The day can either be the day name (with first letter capitalized),
    #       or the wildcard character, '*' for any day in the supplied week.

    # Synthetic ETF restructuring trigger
    setf_restructure_trigger = {
        'day': 'Friday',
        'week': 3
    }

    # Portfolio of ETFs rebalancing trigger
    rebalance_trigger = {
        'day': '*',
        'week': 1
    }
