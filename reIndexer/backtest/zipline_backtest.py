from ..cfg import config
from ..portfolio import MinimumVariance
from ..sector_universe import Universe
from ..synthetic_etf import PriceWeightedETF

from zipline import run_algorithm
from zipline.algorithm import TradingAlgorithm
from zipline.api import order_target_percent, record, set_long_only, symbol
from zipline.data.bar_reader import NoDataForSid
from zipline.finance.execution import MarketOrder
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

        # Zipline context namespace variables
        context.first_run = True  # First run flag
        context.synthetics = dict()  # Dictionary to store synthetic ETF objects
        context.counter = 0  # Counter
        context.port = MinimumVariance()  # Initializing portfolio

        # Enforcing long trades only
        set_long_only()

    @staticmethod
    def zipline_handle_data(context: TradingAlgorithm, data: BarData):
        # First run operations
        if (context.first_run):
            # Validate sector universe
            config.sector_universe = Backtest.__validateSectorUniverse(
                candidate_sector_universe=config.sector_universe,
                data=data
            )

            # Building synthetic sector ETFs
            Backtest.buildSyntheticETFs(context=context, zipline_data=data)

            # Computing initial portfolio, updating positions
            Backtest.rebalancePortfolio(
                context=context,
                zipline_data=data,
                update_positions=True
            )

            # Update first run flag
            context.first_run = False

        # Portfolio Rebalancing
        if ((context.counter % config.port_rebalancing_period) == 0):
            Backtest.rebalancePortfolio(context=context, zipline_data=data)

        # Synthetic ETF restructuring
        if ((context.counter % config.setf_restructure_window) == 0):
            Backtest.rebalancePortfolio(context=context, zipline_data=data)
        
        # Bookkeepign (w/ zipline record; make separate module of course)

        # Update counter each iteration
        context.counter += 1

    @staticmethod
    def buildSyntheticETFs(context: TradingAlgorithm, zipline_data: BarData):
        # Looping through each sector
        for sector_label in config.sector_universe.getSectorLabels():
            # Initializing synthetic ETF, storing in dictionary
            context.synthetics[sector_label] = PriceWeightedETF(
                sector_label=sector_label,
                tickers=config.sector_universe.getTickersInSector(
                    sector_label=sector_label
                ),
                zipline_data=zipline_data
            )

    @staticmethod
    def rebalancePortfolio(context: TradingAlgorithm, zipline_data: BarData,
        update_positions: bool=True) -> np.array:
        # Updating parameters for each of the sectors
        [context.synthetics[i].updateParameters(zipline_data=zipline_data)
            for i in config.sector_universe.getSectorLabels()]
        
        # Building log returns matrix
        log_rets = np.array([context.synthetics[i].getLogReturns()
            for i in config.sector_universe.getSectorLabels()])
        
        # Rebalancing portfolio, getting new weights
        context.port_w = context.port.computeWeights(
            log_rets=log_rets
        )

        # Adding new weights to dictionary corresponding to sector list
        context.port_weights = dict(zip(
            config.sector_universe.getSectorLabels(),
            context.port_w
        ))

        # Update positions if requested
        if update_positions:
            Backtest.updatePositions(context=context)

        # Return positions
        return context.port_w

    @staticmethod
    def restructureETF(context: TradingAlgorithm, zipline_data: BarData,
        update_positions: bool=True):
        # Updating weights for each of the synthetic ETF components
        [context.synthetics[i].updateWeights(zipline_data=zipline_data)
            for i in config.sector_universe.getSectorLabels()]

        # Update positions if requested
        if update_positions:
            Backtest.updatePositions(context=context)

    @staticmethod
    def updatePositions(context: TradingAlgorithm):
        # Looping through each sector
        for sector_label in config.sector_universe.getSectorLabels():
            # Isolating current sector synthetic ETF
            sector = context.synthetics[sector_label]
            # Isolating portfolio weight for current sector
            sector_weight = context.port_weights[sector_label]
            for ticker in sector.getTickerList():
                # Computing current portfolio percentage of the given ticker
                # NOTE: This is the product of the synthetic ETF weight in the
                #       portfolio and the component weight in the synthetic ETF
                port_ticker_weight = sector_weight *\
                    sector.getTickerWeight(ticker)

                # Executing trade to update weight in the portfolio
                order_target_percent(
                    asset=symbol(ticker),
                    target=port_ticker_weight
                )
                logging.debug('Updated portfolio ticker {0} weight to {1}%'.
                    format(ticker, port_ticker_weight * 100))

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
