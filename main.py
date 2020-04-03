import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 as sql
import PeakValleyDetector
import Walker

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    conn = sql.connect('./data/headingtest.db')
    cur = conn.cursor()
    print("Data parsing... ")
    query = cur.execute('SELECT time, accx, accy, accz, gyrox, gyroy, gyroz,\
            magx, magy, magz, yaw, pitch, roll FROM sensordata\
                WHERE filename = "heading1" ORDER BY time LIMIT 3000')
    cols = [column[0] for column in query.description]
    sensor_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    conn.close()
    print("Data parsing done!")
    print(sensor_df)
    print(sensor_df.describe())
    
    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    walker = Walker.Walker()
    
    for index, row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].iterrows():
        if (index % 1000 == 0):
            print("now it`s {0} step.".format(index))
        pvdetect.step(index, row[:4])
        walker.step(index, row[0], row[4:7], pvdetect.peak_df.tail(1), pvdetect.valley_df.tail(1))
    print(pvdetect.peak_df.tail())
    print(pvdetect.valley_df.tail())
    plt.figure(1)
    plt.plot(pvdetect.norm_df['time'], pvdetect.norm_df['value'], c='y', linewidth=0.5)
    plt.scatter(pvdetect.peak_df['time'], pvdetect.peak_df['value'], c='red')
    plt.scatter(pvdetect.valley_df['time'], pvdetect.valley_df['value'], c='blue')
    plt.axhline(y = pvdetect.max_threshold, color='r', linewidth=1)
    plt.axhline(y = pvdetect.min_threshold, color='b', linewidth=1)
    plt.savefig('pvdetect.png')
    plt.show()
    