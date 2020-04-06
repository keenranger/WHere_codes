import sqlite3 as sql
import pandas as pd
class PeakValleyLoader:
    def __init__(self):
        conn = sql.connect('./data/headingtest.db')
        cur = conn.cursor()
        print("Data parsing... ")
        query = cur.execute('SELECT time, accx, accy, accz, gyrox, gyroy, gyroz,\
                magx, magy, magz, yaw, pitch, roll FROM sensordata\
                    WHERE filename = "heading1" ORDER BY time LIMIT 2000')
        cols = [column[0] for column in query.description]
        self.sensor_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        conn.close()
        print("Data parsing done!")