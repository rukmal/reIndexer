from ..cfg import config

from zipline import run_algorithm
from zipline.algorithm import TradingAlgorithm
from zipline.api import order, record
from zipline.protocol import BarData
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
    def __init__(self):
        pass

    def run(self) -> pd.DataFrame:
        return run_algorithm(
            start=config.backtest_start,
            end=config.backtest_end,
            capital_base=config.capital_base,
            initialize=zipline_initialize,
            handle_data=zipline_handle_data,
            data_frequency=config.capital_base        
        )
