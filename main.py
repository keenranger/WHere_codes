from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "0410t1"
    pvloader = DataLoader.DataLoader("./data/0410.db", file_name)
    sensor_df = pvloader.sensor_df
    sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0] #처음시간으로 빼줌 #시간 0부터 시작


    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt( sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] **2)
    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()

    plt.figure(1)
    plt.plot(sensor_df['time'], sensor_df['accx'],c='blue', label='accx')
    plt.plot(sensor_df['time'], sensor_df['accy'],c='green', label='accy')
    plt.plot(sensor_df['time'], sensor_df['accz'],c='orange', label='accz')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('m/s^2')

    for row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].itertuples():
        if (row[0] % 1000 == 0):
            print("now it`s {0} step.".format(row[0]))
        pvdetect.step(row[0], row[1:5])

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    print(len(pvdetect.periodic_peak))
    
    pvplotter.plot()
