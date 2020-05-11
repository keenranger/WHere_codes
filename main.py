from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import DataLoader
from modules import TextLoader
from modules import Walker
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "prc"
    pvloader = DataLoader.DataLoader("./data/200504-50.db", file_name)
    pvloader.DBLoader()
    sensor_df = pvloader.sensor_df
    sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0]  # 처음시간으로 빼줌 #시간 0부터 시작

    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)

    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    # heading 검출
    hdetect = Walker.Walker()

    # acc_value = pd.DataFrame(columns=("time", "value_x","value_y","value_z"))
    # acc_value['time'] = sensor_df['time']
    # acc_value['value_x'] = sensor_df['accx'] ** 2 / norm_df['value'] ** 2
    # acc_value['value_y'] = sensor_df['accy'] ** 2 / norm_df['value'] ** 2
    # acc_value['value_z'] = sensor_df['accz'] ** 2 / norm_df['value'] ** 2

    plt.figure(1)
    plt.plot(sensor_df['time'], sensor_df['accx'], c='blue', label='accx')
    plt.plot(sensor_df['time'], sensor_df['accy'], c='green', label='accy')
    plt.plot(sensor_df['time'], sensor_df['accz'], c='orange', label='accz')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('m/s^2')

    plt.figure(2)
    plt.plot(sensor_df['time'], sensor_df['gyrox'], c='blue', label='gyrox')
    plt.plot(sensor_df['time'], sensor_df['gyroy'], c='green', label='gyroy')
    plt.plot(sensor_df['time'], sensor_df['gyroz'], c='orange', label='gyroz')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('rad/s')

    for row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].itertuples():
        if row[0] % 1000 == 0:
            print("now it`s {0} step.".format(row[0]))
        pvdetect.step(row[0], row[1:5])
        hdetect.step(row[0], row[1], row[5:8], 0, 0)

    plt.figure()
    # plt.scatter(pvdetect.acc_sq_df['time'], pvdetect.acc_sq_df['value_x'], c='blue')
    # plt.scatter(pvdetect.acc_sq_df['time'], pvdetect.acc_sq_df['value_y'], c='green')
    plt.scatter(pvdetect.acc_sq_df['time'], pvdetect.acc_sq_df['value_z'], c='orange')
    plt.xlabel('time')
    # plt.plot(sensor_df['time'], sensor_df['prox']/8)
    plt.title(file_name)

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    print(len(pvdetect.periodic_peak))
    pvplotter.plot()
    plt.show()

    # plt.figure()
    # for idx, row in pvdetect.peak_df.iterrows():
    #     if idx >= 5:
    #         plt.scatter(row['time'], np.var(np.diff(pvdetect.peak_df.loc[idx - 5: idx]['time']), ddof=1),c='orange')
    #         #plt.ylim(0, 1000)
    #         plt.title(file_name)
    #         plt.xlabel('time')
    #         plt.ylabel('dev')
