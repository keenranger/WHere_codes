import sqlite3 as sql
import pandas as pd
class PeakValleyLoader:
    def __init__(self, file_location, file_name, limit = None):
        conn = sql.connect(file_location)
        cur = conn.cursor()
        print("Data parsing... ")
        sql_command = 'SELECT time, accx, accy, accz, gyrox, gyroy, gyroz,\
                magx, magy, magz, yaw, pitch, roll, prox FROM sensordata\
                    WHERE filename = "'+ file_name + '" ORDER BY time'
        if (limit is not None):
            sql_command += " LIMIT + %d" %limit
        query = cur.execute(sql_command)
        cols = [column[0] for column in query.description]
        self.sensor_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        conn.close()
        print("Data parsing done!")