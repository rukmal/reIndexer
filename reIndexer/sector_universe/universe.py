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

        # Set to store invalid ticker tuples
        self.invalid_tickers = set()

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

    def getUniqueTickers(self) -> list:
        """Function to get a list of unique tickers in the universe.
        
        Returns:
            list -- List of unique tickers.
        """

        return self.tickers

    def getUniverseName(self) -> str:
        """Function to get the sector universe name.
        
        Returns:
            str -- Sector universe name.
        """

        return self.universe_name

    def getTickersInSector(self, sector_label: str) -> list:
        """Function to get the component tickers for a given sector.
        
        Arguments:
            sector_label {str} -- Sector label.
        
        Returns:
            list -- List of component tickers.

        Raises:
            KeyError -- Raised when an invalid sector label is provided.
        """

        try:
            return self.sectors[sector_label]
        except KeyError:
            logging.error('Invalid sector name {0}'.format(sector_label))
            raise

    def getSectorLabels(self) -> list:
        """Function to get the list of sector labels in the current universe.
        
        Returns:
            list -- List of sector labels.
        """

        return self.sector_labels

    def removeInvalidTicker(self, invalid_ticker: str):
        """Function to remove invalid tickers from the sector universe.

        Note that this does not mean that the ticker is itself 'invalid' in the
        traditional sense of the word; rather, it means that the data bundle
        used by the backtest engine does not have data for the ticker, so it
        will be omitted.
        
        Arguments:
            invalid_ticker {str} -- Ticker to be removed.
        """

        # Iterating over sectors
        for sector_label in self.sector_labels:
            # Iterating over tickers in the sector
            for sector_ticker in self.sectors[sector_label]:
                # Check if the ticker matches, if so remove
                if (sector_ticker == invalid_ticker):
                    self.sectors[sector_label].remove(invalid_ticker)
                    logging.debug('Removed ticker {0} from sector {1}'
                        .format(invalid_ticker, sector_label))
                    # Adding to invalid tickers set
                    self.invalid_tickers.add((invalid_ticker, sector_label))
