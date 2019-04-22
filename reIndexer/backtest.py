from .cfg import config
from .sector_universe import Universe

from zipline import run_algorithm
from zipline.algorithm import TradingAlgorithm
from zipline.api import order, record, symbols
from zipline.errors import SymbolNotFound
from zipline.protocol import BarData
import logging
import pandas as pd


def zipline_initialize(context: TradingAlgorithm):
    """Zipline backtest initialization method override.
    
    Arguments:
        context {TradingAlgorithm} -- Context variable for the algorithm
    """
    
    pass


def zipline_handle_data(context: TradingAlgorithm, data: BarData):
    pass


class Backtest():
    def __init__(self, sector_universe: Universe):
        # Validating sector unvierse
        self.__validateSectorUniverse(candidate_sector_universe=sector_universe)

        # Binding sector universe to class variable
        logging.debug('Successfully loaded sector universe {0}'
            .format(sector_universe.getUniverseName()))
        self.sector_universe = sector_universe

    def run(self) -> pd.DataFrame:
        return run_algorithm(
            start=config.backtest_start,
            end=config.backtest_end,
            capital_base=config.capital_base,
            initialize=zipline_initialize,
            handle_data=zipline_handle_data,
            data_frequency=config.capital_base        
        )

    def __validateSectorUniverse(self, candidate_sector_universe: Universe):
        """Function to validate a candidate sector universe. Ensures that
        Zipline can look up all tickers.
        
        Arguments:
            candidate_sector_universe {Universe} -- Candidate sector universe.
        
        Raises:
            SymbolNotFound -- Raised when a symbol is not found.
        """

        try:
            symbols(candidate_sector_universe.getUniqueTickers())
        except SymbolNotFound:
            logging.error('Tickers in universe not found by Zipline')
            raise
