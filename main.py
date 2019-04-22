from reIndexer import Backtest, Universe
import logging
import pandas as pd

# Setting log level
logging.getLogger().setLevel(logging.DEBUG)

# Importing sector universe
sp500 = Universe(
    universe_name='SP500',
    csv_file='sector_universes/load_format/sp500.csv'
)

# Runnizng backtest
sim_results = Backtest(sector_universe=sp500).run()
print(sp500.invalid_tickers)
# Saving to csv
sim_results.to_csv('tmp/out2.csv')
