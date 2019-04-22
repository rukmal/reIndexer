import pandas as pd
import logging


class Universe():
    def __init__(self, csv_file: str):
        self.universe = pd.read_csv(filepath_or_buffer=csv_file)

        print(self.universe.shape)
