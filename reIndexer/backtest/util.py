from ..cfg import config

from zipline.api import get_datetime
import logging


class Utilities():
    """Helper utilities for the backtesting module.
    """

    def __init__(self):
        """Initialization method for the 'Utilities' class.

        Handles setting initial flags, and computes date ranges for the target
        weeks for restructuring/rebalancing.
        """

        # Isolating date range for the target restructuring week
        self.restr_week_start = (config.setf_restructure_trigger['week']
            - 1) * 7
        self.restr_week_end = (config.setf_restructure_trigger['week']) * 7

        # Isolating date range for the target rebalancing week
        self.reb_week_start = (config.rebalance_trigger['week'] - 1) * 7
        self.reb_week_end = (config.rebalance_trigger['week']) * 7

        # Flags for keeping track of monthly triggers (to enable day wildcards)
        self.last_month_restructure = 0
        self.last_month_rebalance = 0
    
    def isRestructureTriggered(self) -> bool:
        """Checks if a restructure is triggered at the current backtesting
        date (indicated by `get_datetime`).
        
        Returns:
            bool -- True if restructure is triggered, false otherwise.
        """

        # Checking if correct week
        if (self.restr_week_start < get_datetime().day <= self.restr_week_end):
            # Flag if specific day matches
            is_triggered = (get_datetime().weekday_name ==
                config.setf_restructure_trigger['day'])

            # Handling wildcard (need to check flag)
            if ((config.setf_restructure_trigger['day'] == '*') and
                (self.last_month_restructure != get_datetime().month)):
                # Set flag to true
                is_triggered = True
                # Update flag
                self.last_month_restructure = get_datetime().month

            # Log and return
            if is_triggered:
                logging.info('Synthetic ETF restructure triggered on {0} ({1})'
                    .format(get_datetime().weekday_name, get_datetime().date()))
            
            return is_triggered
        # Not in correct week
        return False

    def isRebalanceTriggered(self) -> bool:
        """Checks if a rebalance is triggered at the current backtesting
        date (indicated by `get_datetime`).
        
        Returns:
            bool -- True if rebalance is triggered, false otherwise.
        """

        # Checking if correct week
        if (self.reb_week_start < get_datetime().day <= self.reb_week_end):
            # Flag if specific day matches
            is_triggered = (get_datetime().weekday_name ==
                config.rebalance_trigger['day'])

            # Handling wildcard (need to check flag)
            if ((config.rebalance_trigger['day'] == '*') and
                (self.last_month_rebalance != get_datetime().month)):
                # Set flag to true
                is_triggered = True
                # Update flag
                self.last_month_rebalance = get_datetime().month

            # Log and return
            if is_triggered:
                logging.info('ETF Portfolio rebalance triggered on {0} ({1})'
                    .format(get_datetime().weekday_name, get_datetime().date()))
        
            return is_triggered
        # Not in correct week
        return False

    def setInitialFlags(self):
        """Set initial flags. This calls the restructuring and rebalancing
        triggers to update wildcard handling flags correctly.

        This is to be called in the first iteration of the backtest only.
        """

        self.isRebalanceTriggered()
        self.isRestructureTriggered()
