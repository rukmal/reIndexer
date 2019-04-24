from ..cfg import config
from ..portfolio import MinimumVariance
from ..sector_universe import Universe
from ..synthetic_etf import PriceWeightedETF

from zipline import run_algorithm
from zipline.algorithm import TradingAlgorithm
from zipline.api import order, record, symbol
from zipline.data.bar_reader import NoDataForSid
from zipline.errors import SymbolNotFound
from zipline.protocol import BarData
import logging
import numpy as np
import pandas as pd


class Backtest():
    def __init__(self, sector_universe: Universe):
        # Binding sector universe to class variable
        logging.debug('Successfully loaded sector universe {0}'
            .format(sector_universe.getUniverseName()))
        config.sector_universe = sector_universe

    @staticmethod
    def zipline_initialize(context: TradingAlgorithm):
        """Zipline backtest initialization method override.
        
        Arguments:
            context {TradingAlgorithm} -- Context variable for the algorithm
        """
        
        # First run flag
        context.first_run = True

        # Dictionary to store synthetic ETF objects
        context.synthetics = dict()

        # Array to store ETF weights
        context.setf_weights = dict()

        # Dictionary to store positions
        context.positions = dict()

        # Counter
        context.counter = 0

        # Initializing portfolio
        context.port = MinimumVariance()

        # Previous weights
        context.prev_weights = None

    @staticmethod
    def zipline_handle_data(context: TradingAlgorithm, data: BarData):
        # First run operations
        if (context.first_run):
            # Validate sector universe
            config.sector_universe = Backtest.__validateSectorUniverse(
                candidate_sector_universe=config.sector_universe,
                data=data
            )

            # Building synthetic ETFs
            for sector_label in config.sector_universe.getSectorLabels():
                context.synthetics[sector_label] = PriceWeightedETF(
                    sector_label=sector_label,
                    tickers=config.sector_universe.getTickersInSector(
                        sector_label=sector_label
                    ),
                    zipline_data=data
                )

            # Update first run flag
            context.first_run = False

        # Portfolio Rebalancing
        if ((context.counter % config.port_rebalancing_period) == 0):
            # Updating parameters
            [context.synthetics[l].updateParameters(data)
                for l in config.sector_universe.getSectorLabels()]
            # Building log returns matrix
            log_rets = np.array([context.synthetics[l].getLogReturns()
                for l in config.sector_universe.getSectorLabels()])
            # Rebalancing portfolio
            context.w = context.port.computeWeights(
                log_rets=log_rets,
                prev_weights=context.prev_weights            
            )
            # Update holdings here (function obviously as you're doing this twice)

        # Synthetic ETF restructuring
        if ((context.counter % config.setf_restructure_window) == 0):
            for sector_label in config.sector_universe.getSectorLabels():
                new_w = context.synthetics[sector_label].getWeights()
                # Iterate through holdings dictionary; update necessary values
                for idx, ticker in context.synthetics[sector_label]\
                    .getTickersInSector():
                    # Update key value (ticker, position) pair of the (unscaled) positions here
                    # Need to multiply ETF component weight by sETF weight in the portfolio
                    pass
        
        # Bookkeepign (w/ zipline record; make separate module of course)

        # Update counter each iteration
        context.counter += 1

    def run(self) -> pd.DataFrame:
        return run_algorithm(
            start=config.backtest_start,
            end=config.backtest_end,
            capital_base=config.capital_base,
            initialize=self.zipline_initialize,
            handle_data=self.zipline_handle_data,
            data_frequency=config.backtest_frequency,
            bundle='quandl'
        )

    @staticmethod
    def __validateSectorUniverse(candidate_sector_universe: Universe, data):
        """Function to validate a candidate sector universe. Ensures that
        Zipline can look up all tickers.
        
        Arguments:
            candidate_sector_universe {Universe} -- Candidate sector universe.
        
        Raises:
            SymbolNotFound -- Raised when a symbol is not found.
        """

        for ticker in candidate_sector_universe.getUniqueTickers():
            try:
                symbol(ticker)
                if not data.can_trade(symbol(ticker)):
                    raise NoDataForSid
            except (SymbolNotFound, NoDataForSid):
                # Updating invalid ticker in the universe
                candidate_sector_universe.removeInvalidTicker(
                    invalid_ticker=ticker
                )
                logging.info('Ticker {0} in universe not in Zipline; removing'
                    .format(ticker))
        
        # Return 'clean' sector universe
        return candidate_sector_universe
