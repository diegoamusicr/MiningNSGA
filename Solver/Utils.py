import pandas as pd
from Objects.Truck import *


def load_trucks_txt(filename):
    dataframe = pd.read_csv(filename, sep=';')
    if not dataframe.empty:
        trucks = []
        for _, row in dataframe.iterrows():
            trucks += [Truck(
                int(row['NODE_START_ID']),
                int(row['TRUCK_ID']),
                row['TRUCK_BRAND'],
                row['TRUCK_MODEL'],
                int(row['TRUCK_CAPACITY']),
            )]
        return trucks
    else:
        raise Exception("File is empty")
