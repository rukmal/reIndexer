from ..cfg import config
from ..sector_universe import Universe
from ..synthetic_etf import PriceWeightedETF

from zipline import run_algorithm
from zipline.algorithm import TradingAlgorithm
from zipline.api import order, record, symbol
from zipline.data.bar_reader import NoDataForSid
from zipline.errors import SymbolNotFound
from zipline.protocol import BarData
import logging
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

    @staticmethod
    def zipline_handle_data(context: TradingAlgorithm, data: BarData):
        # First run operations
        if (context.first_run):
            # Validate sector universe
            config.sector_universe = Backtest.__validateSectorUniverse(
                candidate_sector_universe=config.sector_universe
            )
            # Building synthetic ETFs
            for sector_label in config.sector_universe.getSectorLabels():
                context.synthetics[sector_label] = PriceWeightedETF(
                    sector_label=sector_label,
                    tickers=config.sector_universe.getTickersInSector(
                        sector_label=sector_label
                    )
                )
                context.synthetics[sector_label].getWeights(
                    zipline_data=data
                )

            context.first_run = False

        raise EOFError

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
    def __validateSectorUniverse(candidate_sector_universe: Universe):
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
            except (SymbolNotFound, NoDataForSid):
                # Updating invalid ticker in the universe
                candidate_sector_universe.removeInvalidTicker(
                    invalid_ticker=ticker
                )
                logging.error('Ticker {0} in universe not in Zipline; removing'
                    .format(ticker))
        
        # Return 'clean' sector universe
        return candidate_sector_universe
