import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 as sql
import PeakValleyDetector


if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
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
    print(sensor_df.describe())
    
    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    for index, row in sensor_df[['time', 'accx', 'accy', 'accz']].iterrows():
        if (index % 1000 == 0):
            print("now it`s {0} step.".format(index))
        pvdetect.step(index, row)
    print(pvdetect.peak_df)
    print(pvdetect.valley_df)
    plt.figure(1)
    plt.plot(pvdetect.norm_df['time'], pvdetect.norm_df['value'], c='y', linewidth=0.5)
    plt.scatter(pvdetect.peak_df['time'], pvdetect.peak_df['value'], c='red')
    plt.scatter(pvdetect.valley_df['time'], pvdetect.valley_df['value'], c='blue')
   
    plt.show()
    