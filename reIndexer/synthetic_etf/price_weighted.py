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
    
    def getLogReturn(self) -> float:
        """Get the log return of the ETF.
        
        Returns:
            float -- Log return of the ETF.
        """

        return self.log_ret
    
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

        historical_data = zipline_data.history(
            symbols(*self.tickers),
            'price',
            bar_count=config.setf_lookback_window,
            frequency=config.setf_data_frequency
        )

        # Computing current total asset value, and previous total asset value
        # NOTE: This is simply the sum across the asset prices, as this is a
        #       price-weighted synthetic ETF model
        current_sum = historical_data.ix[-1].sum()
        prev_sum = historical_data.ix[0].sum()
        
        # Computing allocation weights
        w = np.array(historical_data.ix[-1]) / current_sum

        # Computing component log returns
        component_log_ret = np.log(historical_data.pct_change() + 1)

        # Updating ETF variance
        self.variance = np.dot(w, np.dot(component_log_ret.cov(), w))

        # Binding weights
        self.alloc_weights = w

        # Computing ETF expected log return
        # NOTE: Simply using asset price total as this is price-weighted
        self.log_ret = np.log((current_sum / prev_sum) + 1)
