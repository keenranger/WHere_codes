import pandas as pd


class TextLoader:
    def __init__(self, file_location, seperator=' '):
        self.textData = pd.read_csv(file_location,
                                    sep=seperator,
                                    names=['none', 'time', 'accx', 'accy', 'accz', 'magx', 'magy', 'magz', 'yaw',
                                           'pitch',
                                           'roll', 'gyrox', 'gyroy', 'gyroz', 'pres', 'gps1', 'gps2', 'gps3', 'gps4',
                                           'gps5'])
