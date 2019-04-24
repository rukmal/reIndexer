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
        etf_price_labels = ['_'.join(['etf', i])
            for i in config.sector_universe.getSectorLabels()]
        etf_commission_labels = ['_'.join(['etf_commission', i])
            for i in config.sector_universe.getSectorLabels()]

        # Adding to dictionary
        log_dict.update(zip(etf_price_labels, new_prices))
        log_dict.update(zip(etf_commission_labels, etf_commission))
        
        # Total commission
        log_dict['etf_commission'] = commission

        # Adding to zipline record
        record(**log_dict)

    def rebalanceLog(self, context: TradingAlgorithm,
        zipline_data: BarData):
        pass
