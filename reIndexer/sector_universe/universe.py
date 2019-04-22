import pandas as pd
import logging


class Universe():
    """Class to handle a sector universe.

    Builds and maintains a map of sector univeses. This class will eventually
    support time-indexed sectors (to model real-world sector reassignments).
    """
    
    def __init__(self, universe_name: str, csv_file: str):
        """Initialization method for the Univese class. Builds a sector map,
        mapping sectors to component tickers.
        
        Arguments:
            universe_name {str} -- Name of the universe.
            csv_file {str} -- Path to CSV file with in the correct
                              format (see README).
        """

        # Binding args to class variables
        self.universe_name = universe_name
        self.universe_csv = pd.read_csv(filepath_or_buffer=csv_file)

        logging.debug('Successfully loaded CSV with shape {0} for universe {1}'
            .format(self.universe_csv.shape, self.universe_name))

        # Isolating sectors
        self.sector_labels = list(self.universe_csv['sector'].unique())

        # Isolating list of tickers in the universe
        self.tickers = list(self.universe_csv['ticker'].unique())

        logging.debug('Isolated {0} unique sectors and {1} unique tickers'
            .format(len(self.sector_labels), len(self.tickers)))

        # Dictionary to store sector mappings
        self.sectors = dict.fromkeys(self.sector_labels)

        # Building dictionary of sector_label -> ticker mappings
        for sector_label in self.sector_labels:
            self.sectors[sector_label] = list(self.universe_csv.loc[
                self.universe_csv['sector'] == sector_label]['ticker'])

        logging.info('Successfully loaded {0} sector universe'
            .format(self.universe_name))
