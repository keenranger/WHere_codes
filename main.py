import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import sqlite3 as sql
import PeakValleyDetector
import Walker

rcParams['animation.convert_path'] = r'C:\Program Files\ImageMagick\magick.exe'
rcParams['animation.ffmpeg_path'] = r'C:\Program Files\ImageMagick\ffmpeg.exe'

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
        # walker.step(index, row[0], row[4:7], pvdetect.peak_df.tail(1), pvdetect.valley_df.tail(1))

    fig, ax = plt.subplots()
    #plt.plot(pvdetect.norm_df['time'], pvdetect.norm_df['value'], c='y', linewidth=0.5)
    def animate(i):
        #plt.axvline(x = pvdetect.norm_df['time'].loc[i*10], c='r', linewidth=1)
        temp, = plt.plot(pvdetect.norm_df['time'].loc[:i*10], pvdetect.norm_df['value'].loc[:i*10], c='y', linewidth=0.5)
        return temp,
    myAnimation = animation.FuncAnimation(fig, animate, frames=np.arange(0.0, len(sensor_df)/10), \
                                    interval=10, blit=True, repeat=False)
    plt.show()
    #myAnimation.save('myAnimation.gif', writer='imagemagick', fps=60)/
