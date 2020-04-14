from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import PeakValleyLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "cc2"
    pvloader = PeakValleyLoader.PeakValleyLoader("./data/0414.db", file_name)
    sensor_df = pvloader.sensor_df
    sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0] #처음시간으로 빼줌 #시간 0부터 시작
    sensor_df = sensor_df.loc[150:]

    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt( sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] **2)
    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()

    plt.figure(1)
    plt.plot(sensor_df['time'], sensor_df['accx'],c='blue')
    plt.plot(sensor_df['time'], sensor_df['accy'],c='green')
    plt.plot(sensor_df['time'], sensor_df['accz'],c='orange')
    plt.xlabel('time')
    plt.ylabel('m/s^2')

    plt.figure(2)
    plt.plot(sensor_df['time'], sensor_df['prox'])

    for index, row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].iterrows():
        if (index % 1000 == 0):
            print("now it`s {0} step.".format(index))
        pvdetect.step(index, row[:4])
    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    pvplotter.plot()

