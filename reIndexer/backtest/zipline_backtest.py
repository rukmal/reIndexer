from .bookkeeping import Bookkeeping
from .util import Utilities
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
    """Module to handle and run the Zipline backtesting framework.

    This module is the main driver for reIndexer. It orchestrates synthetic ETF
    creation, portfolio rebalancing, zipline logging, and sector universe
    validation.

    Backtest initializes with the target simulation sector universe, and reads
    all other configuration information from the reIndexer configuration file.
    """

    def __init__(self, sector_universe: Universe):
        """Initialization method for the Backtest module. Binds the target
        sector universe to an instance variable.
        
        Arguments:
            sector_universe {Universe} -- Target simulation sector universe.
        """

        # Binding sector universe to class variable
        logging.debug('Successfully loaded sector universe {0}'
            .format(sector_universe.getUniverseName()))
        config.sector_universe = sector_universe

    @staticmethod
    def zipline_initialize(context: TradingAlgorithm):
        """Zipline backtest initialization method override.

        Initializes context namespace variables used during the portfolio
        optimization, and sets zipline configuration options for the simulation.
        
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

        # Initializing utilities module
        context.util = Utilities()

        # Initializing bookkeeping module
        context.books = Bookkeeping()

    @staticmethod
    def zipline_handle_data(context: TradingAlgorithm, data: BarData):
        """Zipline `handle_data` method override. Handles all trading
        operations for the algorithm. Additionally, this method also handles
        synthetic ETF initialization, portfolio balancing, and logging.

        In summary, this method initializes all synthetic ETFs on the first
        iteration, balances, and opens positions in the necessary assets. After
        that, it checks the current date of the simulation against the triggers
        for portfolio balancing and ETF restructuring provided in the
        configuration file to initialize a rebalancing or restructuring
        operation, respectively.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            data {BarData} -- Instance zipline data bundle.
        """

        # First run operations
        if (context.first_run):
            # Validate sector universe
            config.sector_universe = Backtest.validateSectorUniverse(
                candidate_sector_universe=config.sector_universe,
                zipline_data=data
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

            # Updating initial flags for rebalancing/restructuring trigger
            context.util.setInitialFlags()

            # Skip rest of logic for first iteration
            return

        # Portfolio Rebalancing
        if context.util.isRebalanceTriggered():
            Backtest.rebalancePortfolio(
                context=context,
                zipline_data=data,
                update_positions=True    
            )

        # Synthetic ETF restructuring
        if context.util.isRestructureTriggered():
            Backtest.restructureETF(
                context=context,
                zipline_data=data,
                update_positions=True
            )
        
        # Bookkeepign (w/ zipline record; make separate module of course)

    @staticmethod
    def buildSyntheticETFs(context: TradingAlgorithm, zipline_data: BarData):
        """Function to build synthetic ETFs. This is the initialization method
        for the ETFs, and is meant to be called during the first iteration of
        the simulation only.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            zipline_data {BarData} -- Instance zipline data bundle.
        """

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
        """Function to rebalance a portfolio of synthetic ETFs, with the option
        to trigger an execution of trades within Zipline to enforce the new
        portfolio synthetic ETF asset allocations.

        This method also handles logging, and binds the new portfolio weights
        to the `context.port_w`, and `context.port_weights` variables.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            zipline_data {BarData} -- Instance zipline data bundle.
        
        Keyword Arguments:
            update_positions {bool} -- Flag to update positions in Zipline
                                       (default: {True}).
        
        Returns:
            np.array -- Portfolio weights.
        """

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
        update_positions: bool=True, log_commission: bool=True):
        """Function to restructure the ETFs. This function calls the internal
        synthetic ETF restructuring method to update weights within each of the
        synthetic ETF objects.

        This function also handles logging, and provides the option to make
        trades to make trades updating asset positions in zipline.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
            zipline_data {BarData} -- Instance zipline data bundle.
        
        Keyword Arguments:
            update_positions {bool} -- Flag to update positions in Zipline
                                       (default: {True}).
            log_commissions {bool} -- Flag to log commissions (default: {True}).
        """

        # Getting old synthetic ETF prices (for logging)
        old_etf_prices = np.array([context.synthetics[i].getCurrentPrice(
            zipline_data) for i in config.sector_universe.getSectorLabels()])

        # Updating weights for each of the synthetic ETF components
        [context.synthetics[i].updateWeights(zipline_data=zipline_data)
            for i in config.sector_universe.getSectorLabels()]

        # Update positions if requested
        if update_positions:
            Backtest.updatePositions(context=context)
        
        # Logging restructuring commissions
        if log_commission:
            context.books.restructureLog(
                context=context,
                zipline_data=zipline_data,
                old_prices=old_etf_prices
            )

    @staticmethod
    def updatePositions(context: TradingAlgorithm):
        """Function to update asset positions in Zipline.

        This function computes specific asset proportions in the final portfolio
        by multiplying the weight of the sector containing the asset by the
        weight of the asset within the sector. Then, it uses zipline's
        `order_target_percent` function to specify the percentage (specified
        as a decimal) of the position for a given asset in the portofolio as a
        whole.
        
        Arguments:
            context {TradingAlgorithm} -- Zipline context namespace variable.
        """

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

    @staticmethod
    def validateSectorUniverse(candidate_sector_universe: Universe,
        zipline_data: BarData):
        """Function to validate a candidate sector universe. Ensures that
        Zipline can look up all tickers.
        
        Arguments:
            candidate_sector_universe {Universe} -- Candidate sector universe.
            zipline_data {BarData} -- Instance zipline data bundle.        

        Raises:
            SymbolNotFound -- Raised when a symbol is not found.
        """

        for ticker in candidate_sector_universe.getUniqueTickers():
            try:
                symbol(ticker)
                if not zipline_data.can_trade(symbol(ticker)):
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

    def run(self) -> pd.DataFrame:
        """Function to run the simulation; triggers zipline's `run_algorithm`,
        with appropriate function overrides.
        
        Returns:
            pd.DataFrame -- Zipline simulation results.
        """

        return run_algorithm(
            start=config.backtest_start,
            end=config.backtest_end,
            capital_base=config.capital_base,
            initialize=self.zipline_initialize,
            handle_data=self.zipline_handle_data,
            data_frequency=config.backtest_frequency,
            bundle='quandl'
        )
