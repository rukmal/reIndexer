import logging
import pandas as pd


class config:
    # Backtest time window
    tz_local = 'US/Eastern'
    backtest_start = pd.to_datetime('2015-01-01').tz_localize(tz_local)
    backtest_end = pd.to_datetime('2018-03-01').tz_localize(tz_local)

    # Backtest frequency configuration
    backtest_frequency = 'daily'  # Must be either 'daily' or 'minute'

    # Commission configuration
    etf_commission = 0.01  # Percent (decimal) of value of component trade
    relative_trade_commission = 0.01  # Percent (decimal) of value of ETF trade
    trade_commission = 0.005  # Commission (in dollars) per dollar of trading

    # Portfolio configuration
    capital_base = 1e10
    optim_tol = 1e-6  # Optimization tolerance

    # Sector universe (set at backtest initialization)
    sector_universe = None

    # Synthetic ETF`
    setf_lookback_window = 252  # days (1 work year)
    setf_data_frequency = '1d'  # '1m' or '1d' for minute/daily respectively

    # Restructuring and rebalancing triggers
    # NOTE: The 'week' key indicates the week of the rebalance; counting here
    #       starts at 1; i.e., 'week': 1 indicates the first week of the month.
    # NOTE: The day can either be the day name (with first letter capitalized),
    #       or the wildcard character, '*' for any day in the supplied week.

    # Synthetic ETF restructuring trigger
    # Current config: Restructure on the third Friday of the month
    setf_restructure_trigger = {
        'day': 'Friday',
        'week': 3
    }

    # Portfolio of ETFs rebalancing trigger
    # Current config: Rebalance on first day of first week of the month
    rebalance_trigger = {
        'day': '*',
        'week': 1
    }
