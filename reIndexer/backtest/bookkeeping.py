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
        # Label lists (i.e. log column titles)
        # ETF restructuring turnover
        self.etf_restr_turnover_labels = ['_'.join(['etf_restr_turnover', i])
            for i in config.sector_universe.getSectorLabels()]
        # Total restructuring turnover
        self.total_etf_restr_turnover_label = ['total_etf_restr_turnover']
        # Portfolio rebalancing commission
        self.port_rebal_turnover_labels = ['_'.join(['port_rebal_turnover', i])
            for i in config.sector_universe.getSectorLabels()]
        # Total portfolio turnover
        self.total_port_rebal_turnover_label = ['total_port_rebal_turnover']

        # Zero value tickers
        # NOTE: Because of a 'feature' of zipline's `record` function, all
        #       values are forward-filled. For things like commissions, this
        #       needs to be suppressed. The following list is set to 0 at the
        #       beginning of each iteration
        self.clean_labels = self.etf_restr_turnover_labels + \
                            self.total_etf_restr_turnover_label + \
                            self.port_rebal_turnover_labels + \
                            self.total_port_rebal_turnover_label
        # Dictionary of zero-ed key-value paris
        self.clean_dict = dict(zip(self.clean_labels,
                                   [0] * len(self.clean_labels)))

    def cleanLog(self):
        record(**self.clean_dict)

    def restructureLog(self, context: TradingAlgorithm, zipline_data: BarData,
        old_weights: np.array, new_weights: np.array):
        """Function to log ETF data during a restructuring process. Records
        dollar value turnover (i.e. the trades) to restructure
        the ETFs, and total restructuring turnover for the portfolio.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            zipline_data {BarData} -- Instance zipline data bundle.
            old_weights {np.array} -- Old ETF asset allocation weights.
            new_weights {np.array} -- New ETF asset allocation weights.
        """
        
        # Computing absolute weight delta
        abs_weights_delta = np.abs(new_weights - old_weights)

        # Computing dollar value change, using current asset prices
        etf_restr_turnover = [context.synthetics[i].getCurrentPrice(
                zipline_data=zipline_data,
                alloc_weights=abs_weights_delta[idx])
            for idx, i in enumerate(config.sector_universe.getSectorLabels())]

        # Computing total ETF restructure turnover
        etf_restr_total_turnover = np.sum(etf_restr_turnover)

        # Building log object
        log_dict = dict()

        # Adding to dictionary
        log_dict.update(zip(self.etf_restr_turnover_labels, etf_restr_turnover))
        
        # Total turnover
        log_dict[self.total_etf_restr_turnover_label[0]] = \
            etf_restr_total_turnover

        # Adding to zipline record
        record(**log_dict)

    def rebalanceLog(self, old_weights: np.array, new_weights: np.array,
        new_prices: np.array):
        """Function to log portfolio data during a rebalancing process. Records
        dollar value turnover (i.e. the trades) to rebalance
        the portfolio, and total rebalancing turnover for the portfolio.
        
        Arguments:
            old_weights {np.array} -- Old ETF weights (last rebalance).
            new_weights {np.array} -- New ETF weights (current rebalance).
            new_prices {np.array} -- New ETF prices (current rebalance).
        """

        # Computing absolute weights delta
        abs_weights_delta = np.abs(new_weights - old_weights)

        # Computing portfolio turnover (dollar value) for each of the ETFs,
        # using current asset prices
        port_rebal_turnover = np.multiply(abs_weights_delta, new_prices)

        # Computing total turnover
        port_rebal_total_turnover = np.sum(port_rebal_turnover)

        # Building log object
        log_dict = dict()

        # Adding to dictionary
        log_dict.update(zip(self.port_rebal_turnover_labels,
                            port_rebal_turnover))

        # Total turnover
        log_dict[self.total_port_rebal_turnover_label[0]] = \
            port_rebal_total_turnover

        # Adding to zipline record
        record(**log_dict)

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
