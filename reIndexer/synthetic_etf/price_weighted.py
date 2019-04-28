from ..cfg import config
from ..backtest.util import Utilities

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

    def __init__(self, sector_label: str, tickers: list, zipline_data: BarData):
        """Initialization method for the PriceWeightedETF module. Binds
        necessary metadata to class variables.
        
        Arguments:
            sector_label {str} -- Sector label.
            tickers {list} -- List of component tickers.
            zipline_data {BarData} -- Instance zipline data bundle.
        """

        # Binding to class variables
        self.name = sector_label
        self.tickers = tickers

        # Initializing utilities module (for historical restructure flag)
        self.backtest_util = Utilities()

        # Updating ETF parameters on init
        self.updateParameters(zipline_data=zipline_data)

        # Compute allocation weights on initialization
        self.updateWeights(zipline_data=zipline_data)

    def updateWeights(self, zipline_data: BarData) -> np.array:
        """Update current weights of the component assets; this recomputes the
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

        # Binding allocation weights (list and dict)
        self.alloc_weights = current_asset_prices / current_sum
        self.alloc_weights_dict = dict(zip(self.tickers, self.alloc_weights))

        # Return new weights
        return self.alloc_weights
    
    def getComponentAllocation(self) -> np.array:
        """Get the current component allocation weights. Note that the order
        of the weights in the returned array correspond to that of the
        result of `getTickerList()`.
        
        Returns:
            np.array -- ETF component allocation weights.
        """

        return self.alloc_weights

    def getPeriodLogReturn(self) -> float:
        """Get the single-period log return of the ETF.
        
        Returns:
            float -- Single-period log return of the ETF.
        """

        return self.period_log_ret
    
    def getLogReturns(self) -> np.array:
        """Get the log returns series of the ETF.
        
        Returns:
            np.array -- Log returns of the ETF.
        """

        return self.log_rets

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
    
    def getCurrentPrice(self, zipline_data: BarData,
        alloc_weights: np.array=None) -> float:
        """Compute and return the current asset price (using stored
        component asset allocation weights) or supplied override allocation
        weights.
        
        Arguments:
            zipline_data {BarData} -- Instance zipline data bundle.
        
        Keyword Arguments:
            alloc_weights {np.array} -- Alternate allocation weights to be used
                                        instead of stored allocation weights
                                        (default: {None}).
        
        Returns:
            float -- Synthetic ETF price at the current time step.
        """

        # Getting current component asset prices
        current_asset_prices = np.array(zipline_data.current(
            symbols(*self.tickers),
            'price'
        ))

        if alloc_weights is None:
            alloc_weights = self.alloc_weights

        # Comuting current price (dot product b/w current prices and alloc)
        return np.dot(current_asset_prices, alloc_weights)

    def getTickerList(self) -> list:
        """Get the list of tickers (in order; corresponds to asset weights and
        other component-ordered data from the ETF etc.).
        
        Returns:
            list -- List of component asset tickers.
        """

        return self.tickers

    def getTickerWeight(self, ticker: str) -> float:
        """Get the current synthetic ETF allocation weight for the given ticker.
        
        Arguments:
            ticker {str} -- Target ticker.
        
        Raises:
            KeyError: Raised when the given ticker is not found in the ETF.
        
        Returns:
            float -- Allocation weight for `ticker`.
        """

        if ticker not in self.tickers:
            logging.error('Ticker {0} not found in the current synthetic ETF'.
                format(ticker))
            raise KeyError
        
        return self.alloc_weights_dict[ticker]

    def updateParameters(self, zipline_data: BarData):
        """Update ETF parameters; specifically, the asset allocations weights,
        the log return (over the configuration lookback window), the variance,
        and the synthetic ETF prices over the lookback window.
        
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

        # Filling na values
        historical_data = historical_data.fillna(method='bfill')
        historical_data = historical_data.fillna(method='ffill')

        # Computing prices, restructuring per the period in the configuration
        setf_prices = np.array([])
        first_run = True  # Flag for first run
        for idx, row in historical_data.iterrows():
            if (self.backtest_util.isRestructureTriggered(
                current_date=idx, log_flag=False) or first_run):
                # Recompute allocation weights
                alloc_weights = np.array(row / row.sum())
                # Update first run flag
                first_run = False
            # Computing synthetic ETF price
            setf_price = np.dot(alloc_weights, row.values)
            # Appending to prices array
            setf_prices = np.append(setf_prices, setf_price)

        if (np.count_nonzero(np.isnan(setf_prices)) > 0):
            logging.error('NA values detected in Synthetic ETF prices')
            raise Exception

        # Computing ETF log returns
        self.log_rets = np.diff(np.log(setf_prices))

        # Computing single-period ETF log return (sum of log returns)
        self.period_log_ret = np.sum(self.log_rets)

        # Computing ETF variance
        self.variance = np.var(self.log_rets)

        # Casting synthetic ETF prices to DataFrame with original index, binding
        self.setf_prices = pd.DataFrame(setf_prices,
                                        index=historical_data.index)
