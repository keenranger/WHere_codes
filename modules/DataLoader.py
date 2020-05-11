import sqlite3 as sql
import pandas as pd


class DataLoader:
    def __init__(self, file_location, file_name, seperator=' '):
        self.file_location = file_location
        self.file_name = file_name
        self.sep = seperator
        self.sensor_df = pd.DataFrame

    def DBLoader(self):
        conn = sql.connect(self.file_location)
        cur = conn.cursor()
        print("Data parsing... ")
        sql_command = 'SELECT * FROM sensordata\
                          WHERE filename = "' + self.file_name + '" ORDER BY time'
        query = cur.execute(sql_command)
        cols = [column[0] for column in query.description]
        self.sensor_df = pd.DataFrame.from_records(
            data=query.fetchall(), columns=cols)
        conn.close()
        print("Data parsing done!")

    def TxTLoader(self):
        print("Data parsing... ")
        self.sensor_df = pd.read_csv(self.file_location,
                                     sep=self.sep,
                                     names=['none', 'time', 'accx', 'accy', 'accz', 'magx', 'magy', 'magz', 'yaw',
                                            'pitch',
                                            'roll', 'gyrox', 'gyroy', 'gyroz', 'pres', 'gps1', 'gps2', 'gps3', 'gps4',
                                            'gps5'])
        print("Data parsing done!")