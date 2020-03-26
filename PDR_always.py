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
             WHERE filename = "heading1" ORDER BY time')
cols = [column[0] for column in query.description]
sensor_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
conn.close()
print("Data parsing done!")
print(sensor_df)

class PeakValleyDetector:
    def __init__(self, min_threshold=9, max_threshold = 11, step_interval = 30):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.step_interval = step_interval
        self.peak_df = pd.DataFrame(columns=("time", "value"))
        self.valley_df = pd.DataFrame(columns=("time", "value"))
        self.acc = np.zeros(3)

    def step(self, row): #row가져와서 class에 저장하는 부분
        self.current_time = row[0]
        self.acc = row[1:4]
        self.norm_threshold()

    def norm_threshold(self): #여기서 norm 값이 threshold 못넘는 값들은 그냥 넘깁니다.
        self.euc_norm = np.sqrt( self.acc[0] ** 2 + self.acc[1] ** 2\
        + self.acc[2] **2)
        if (self.euc_norm > self.max_threshold):
            self.peak_df = self.peak_df.append\
                ({'time': self.current_time, 'value': self.euc_norm}, ignore_index=True)
        elif (self.euc_norm < self.min_threshold):
            self.valley_df = self.valley_df.append\
                ({'time': self.current_time, 'value': self.euc_norm}, ignore_index=True)
        else:
            pass
    def temp(self):
        if (self.euc_norm > 0): #피크쪽 처리할 떄
            pass
        else: #밸리쪽 처리할 때
            pass
## 피크 검출
pvdetect = PeakValleyDetector()
for index, row in sensor_df[['time', 'accx', 'accy', 'accz']].iterrows():
    pvdetect.step(row)
print(pvdetect.peak_df)
print(pvdetect.valley_df)



        

#plt.figure(1)
# sensor_df[['magx', 'magy', 'magz']].plot()
#plt.legend(loc = 'best')
