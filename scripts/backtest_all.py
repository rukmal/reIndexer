# Script to run a complete backtest on all candidate sector universes in the
# `sector_universes/learned_sector_candidates`
# This script isolates a list of common denominator companies (that are common
# across all candidate sectorization schemes, and only uses these)

import logging
import os
import pandas as pd

from context import reIndexer


# Setting logging output to a file, setting level
logging.basicConfig(filename='tmp/out.log', level=logging.INFO)

# Folder containing candidate sector universe files
sector_folder = 'sector_universes/learned_sector_candidates/'
# Output folder for pickled backtest results dataframes
pickle_out_folder = 'sector_universes/learned_sectors/pickle/'
# Output folder for excel backtest result files
excel_out_folder = 'sector_universes/learned_sectors/excel/'

# Override list of completed universes (for resolution on crash)
completed_universes = [f.split('.')[0] for f in os.listdir(excel_out_folder)
    if f.endswith('.xlsx')]

def backtestAll():
    candidate_files = [f for f in os.listdir(sector_folder)
        if f.endswith('.csv')]
    print('Found {0} candidate sector files'.format(len(candidate_files)))

    print('Removing {0} previously completed universes'.format(
        len(completed_universes)))
    
    candidate_files = [f for f in candidate_files
        if f.split('.')[0] not in completed_universes]
    
    print('Running backtest on {0} candidate sector files'.format(
        len(candidate_files)))

    counter = 0

    for f in candidate_files:
        print('Currently backtesting {0}'.format(f))

        # Isolating sector universe name
        universe_name, _ = f.split('.')

        # Creating reIndexer sector from file
        candidate_universe = reIndexer.Universe(
            universe_name=universe_name,
            csv_file=os.path.join(sector_folder, f)
        )

        # Running backtest
        backtest_results = reIndexer.Backtest(
            sector_universe=candidate_universe
        ).run()

        # Saving output data to excel and pickle
        backtest_results.to_excel(os.path.join(
            excel_out_folder,
            '.'.join([universe_name, 'xlsx'])
        ))
        backtest_results.to_pickle(os.path.join(
            pickle_out_folder,
            '.'.join([universe_name, '.pickle'])
        ))

        print('Completed backtesting {0}'.format(f))
        counter += 1 # Increment counter (for percentage)
        print('Backtest (all) {0}% complete'.format(counter /
            len(candidate_files) * 100))
        print('Completed {0} candidate universes; {1} remaining out of {2}'.\
            format(counter, len(candidate_files) - counter,
                   len(candidate_files)))

if __name__ == '__main__':
    backtestAll()
