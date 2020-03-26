import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import sqlite3 as sql

## sql을 통해 dataframe으로 db가져오기
conn = sql.connect('./headingtest/database-name.db')
cur = conn.cursor()
print("Data parsing... ")
query = cur.execute('SELECT time, accx, accy, accz, gyrox, gyroy, gyroz,\
        magx, magy, magz, yaw, pitch, roll FROM sensordata\
             WHERE filename = "heading1" ORDER BY time  ')
cols = [column[0] for column in query.description]
sensor_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
print("Data parsing done!")
print(sensor_df)
print(sensor_df[['time', 'magx', 'magy', 'magz']])
plt.figure(1)
sensor_df[['magx', 'magy', 'magz']].plot()
plt.legend(loc = 'best')
plt.show()

