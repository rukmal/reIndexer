from ..cfg import config

from zipline.algorithm import TradingAlgorithm
from zipline.api import record
from zipline.protocol import BarData
import numpy as np


class Bookkeeping():
    """Bookkeeping module to handle logging for individual ETF prices,
    commissions, and other necessary data.
    """

    def __init__(self):
        pass
    
    def restructureLog(self, context: TradingAlgorithm, zipline_data: BarData,
        old_prices: np.array, new_prices: np.array):
        """Function to log ETF data during a restructuring process. Records
        individual ETF prices, commisions paid on the trades to restructure
        the ETFs, and total restructuring commission for the portfolio.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            zipline_data {BarData} -- Instance zipline data bundle.
            old_prices {np.array} -- Old ETF prices (for delta computation).
            new_prices {np.array} -- New ETF prices.
        """

        # Computing total delta
        etf_deltas = new_prices - old_prices
        
        # Computing per-ETF commissions
        etf_commission = np.abs(etf_deltas) * config.etf_commission
        
        # Computing commission
        commission = np.sum(etf_commission)

        # Building log object
        log_dict = dict()

        # Building labels for dictionary
        etf_commission_labels = ['_'.join(['etf_commission', i])
            for i in config.sector_universe.getSectorLabels()]

        # Adding to dictionary
        log_dict.update(zip(etf_commission_labels, etf_commission))
        
        # Total commission
        log_dict['etf_commission'] = commission

        # Adding to zipline record
        record(**log_dict)

    def rebalanceLog(self, old_prices: np.array, old_weights: np.array,
        new_prices: np.array, new_weights: np.array):
        """Function to log portfolio commission data during a rebalance event.
        
        Arguments:
            old_prices {np.array} -- Old ETF prices (last rebalance).
            old_weights {np.array} -- Old ETF weights (last rebalance).
            new_prices {np.array} -- New ETF prices (current rebalance).
            new_weights {np.array} -- New ETF weights (current rebalance).
        """
        
        # Computing old weighted price
        old_weighted_price = np.dot(old_prices, old_weights)

        # Computing new weighted price
        new_weighted_price = np.dot(new_prices, new_weights)

        # Computing total absolute delta
        abs_delta = np.abs(old_weighted_price - new_weighted_price)

        # Computing commission
        rebal_commission = abs_delta * config.relative_trade_commission

        # Adding to zipline record
        record(portfolio_rebalance_commission=rebal_commission)

    def etfDataLog(self, etf_prices: np.array, etf_weights: np.array):
        """Function to log ETF data, specifically ETF prices and corresponding
        portfolio weights.
        
        Arguments:
            etf_prices {np.array} -- ETF prices.
            etf_weights {np.array} -- Portfolio ETF weights.
        """

        # Building log object
        log_dict = dict()

        # Building labels for dictionary
        etf_price_labels = ['_'.join(['etf', i])
            for i in config.sector_universe.getSectorLabels()]
        port_weights_label = ['_'.join(['etf_weight', i])
            for i in config.sector_universe.getSectorLabels()]

        # Adding to dictionary
        log_dict.update(zip(etf_price_labels, etf_prices))
        log_dict.update(zip(port_weights_label, etf_weights))

        # Adding to zipline record
        record(**log_dict)
