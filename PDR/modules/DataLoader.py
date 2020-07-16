import sqlite3 as sql
import pandas as pd


class DataLoader:
    def __init__(self, file_loc, file_name):
        self.file_loc = file_loc
        self.file_name = file_name
        self.sensor_df = pd.DataFrame

    def loader(self):
        if self.file_loc[-3:] == "csv" or self.file_loc[-3:] == "txt":
            print("Data parsing... ")
            self.sensor_df = pd.read_csv(self.file_loc, names=['experiment', 'time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy',
                                                               'gyroz', 'magx', 'magy', 'magz', 'rot0', 'rot1', 'rot2', 'rot3', 'game0', 'game1', 'game2', 'game3', 'light','pressure', "x_uncalib", "y_uncalib","z_uncalib","x_bias","y_bias","z_bias"])
            print("Data parsing done!")

        elif self.file_loc[-2:] == "db":
            conn = sql.connect(self.file_loc)
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
        else:
            pass
