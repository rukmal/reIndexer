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
        self.name = sector_label
        self.tickers = tickers

        # List to store total rolling price
        self.total_asset_price = list()
    
    def setInitialData(self, zipline_data: BarData):
        pass

    def getWeights(self, zipline_data: BarData):
        # Getting current component asset prices
        current_asset_prices = np.array(zipline_data.current(
            symbols(*self.tickers),
        ))

        # Computing current sum
        current_sum = np.sum(current_asset_prices)

        # Computing portfolio weights
        self.alloc_weights = current_asset_prices / current_sum

        print(self.alloc_weights)

        return self.alloc_weights
    
    def getLogReturn(self, zipline_data: BarData):
        return self.log_ret
    
    def getVariance(self, zipline_data: BarData):
        return self.variance

    def updateParameters(self, zipline_data: BarData):
        historical_data = zipline_data.history(
            symbols(*self.tickers),
            'price',
            bar_count=config.setf_lookback_window,
            frequency=config.setf_data_frequency
        )

        # Appending new price to the list
        self.total_asset_price.append(historical_data.ix[-1].sum())
        
        # Computing allocation weights
        w = list(historical_data.ix[-1]) / self.total_asset_price[-1]

        # Computing component log returns
        component_log_ret = np.log(historical_data.pct_change() + 1)

        # Updating ETF variance
        self.variance = np.log(w, np.dot(component_log_ret.cov(), w))

        # Binding weights
        self.alloc_weights = w

        # Computing ETF expected log return
        # NOTE: Simly using asset price total as this is price-weighted
        self.log_ret = np.log((self.total_asset_price[-1]\
            / self.total_asset_price[-2]) + 1)
