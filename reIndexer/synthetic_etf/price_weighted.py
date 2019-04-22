from ..cfg import config

from zipline.api import symbols
from zipline.protocol import BarData
import logging
import numpy as np
import pandas as pd


class PriceWeightedETF():
    """Class to model a synthetic price-weighted ETF.

    This module encapsulates computation necessary to simulate a synthetic
    price-weighted exchange traded fund of a given list of assets. This includes
    dynamic asset allocation weights computation, log returns computation, and
    ETF variance computation.

    The ETF log return and variance may be used as parameters to compute
    portfolios of ETFs to be used for analysis.
    """

    def __init__(self, sector_label: str, tickers: list):
        """Initialization method for the PriceWeightedETF module. Binds
        necessary metadata to class variables.
        
        Arguments:
            sector_label {str} -- Sector label.
            tickers {list} -- List of component tickers.
        """

        self.name = sector_label
        self.tickers = tickers

    def getWeights(self, zipline_data: BarData) -> np.array:
        """Get the current weights of the component assets; this recomputes the
        price-weighted allocation as of the date of the current `zipline_data`.
        
        Arguments:
            zipline_data {BarData} -- Instance zipline data bundle.
        
        Returns:
            np.array -- Array of asset weights.
        """

        # Getting current component asset prices
        current_asset_prices = np.array(zipline_data.current(
            symbols(*self.tickers),
            'price'
        ))

        # Computing current sum
        current_sum = np.sum(current_asset_prices)

        # Computing portfolio weights
        self.alloc_weights = current_asset_prices / current_sum

        # Return new weights
        return self.alloc_weights
    
    def getPeriodLogReturn(self) -> float:
        """Get the single-period log return of the ETF.
        
        Returns:
            float -- Single-period log return of the ETF.
        """

        return self.period_log_ret
    

    def getStdDev(self) -> float:
        """Get the standard deviation of the ETF.
        
        Returns:
            float -- Standard deviation of the ETF.
        """

        return np.sqrt(self.variance)

    def getVariance(self) -> float:
        """Get the variance of the ETF.
        
        Returns:
            float -- Variance of the ETF.
        """

        return self.variance

    def updateParameters(self, zipline_data: BarData):
        """Update ETF parameters; specifically, the asset allocations weights,
        the log return (over the configuration lookback window),
        and the variance.
        
        Arguments:
            zipline_data {BarData} -- Instance zipline data bundle.
        """

        # Get historical price data for lookback window from config
        historical_data = zipline_data.history(
            symbols(*self.tickers),
            'price',
            bar_count=config.setf_lookback_window,
            frequency=config.setf_data_frequency
        )

        # Computing ETF log returns
        # NOTE: Simply using asset price total as this is price-weighted
        self.log_ret = np.array(np.log(
            historical_data.apply(np.sum, axis=1).pct_change() + 1
        )[1:])

        # Computing single-period ETF log return (sum of log returns)
        self.period_log_ret = np.sum(self.log_ret)

        # Computing ETF variance
        self.variance = np.var(self.log_ret)
