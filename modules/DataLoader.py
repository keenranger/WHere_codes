import sqlite3 as sql
import pandas as pd


class DataLoader:
    def __init__(self, file_location, file_name):
        conn = sql.connect(file_location)
        cur = conn.cursor()
        print("Data parsing... ")
        sql_command = 'SELECT * FROM sensordata\
                    WHERE filename = "' + file_name + '" ORDER BY time'
        query = cur.execute(sql_command)
        cols = [column[0] for column in query.description]
        self.sensor_df = pd.DataFrame.from_records(
            data=query.fetchall(), columns=cols)
        conn.close()
        print("Data parsing done!")
