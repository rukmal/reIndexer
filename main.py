from reIndexer import Backtest, Universe
import logging
import numpy as np
import pandas as pd

# Setting log level
logging.getLogger().setLevel(logging.INFO)

# Importing sector universe
sp500 = Universe(
    universe_name='SP500',
    csv_file='sector_universes/learned_sector_candidates/sp500_final.csv'
)

# Runnizng backtest
sim_results = Backtest(sector_universe=sp500).run()
print(sp500.invalid_tickers)

# Saving to excel and pickle
sim_results.to_excel('sector_universes/learned_sectors/excel/sp500.xlsx')
sim_results.to_pickle('sector_universes/learned_sectors/pickle/sp500..pickle')

