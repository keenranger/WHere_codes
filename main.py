from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import DataLoader
from modules import TextLoader
from modules import HeadingDetector
from modules import Walker

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "1F"
    pvloader = DataLoader.DataLoader("data/FirstFloor.txt", file_name)
    pvloader.TxTLoader()
    sensor_df = pvloader.sensor_df[800:]
    # sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0]  # 처음시간으로 빼줌 #시간 0부터 시작

    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)

    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    # heading 검출
    hdetect = HeadingDetector.HeadingDetector()
    # PDR
    walker = Walker.Walker()

    plt.figure(1)
    plt.plot(sensor_df['time'], sensor_df['accx'], c='blue', label='accx')
    plt.plot(sensor_df['time'], sensor_df['accy'], c='green', label='accy')
    plt.plot(sensor_df['time'], sensor_df['accz'], c='orange', label='accz')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('m/s^2')
    plt.title(file_name)

    plt.figure(2)
    plt.plot(sensor_df['time'], sensor_df['gyrox'], c='blue', label='gyrox')
    plt.plot(sensor_df['time'], sensor_df['gyroy'], c='green', label='gyroy')
    plt.plot(sensor_df['time'], sensor_df['gyroz'], c='orange', label='gyroz')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('rad/s')
    plt.title(file_name)

    plt.figure(3)
    plt.plot(sensor_df['time'], sensor_df['roll'], c='blue', label='roll')
    plt.plot(sensor_df['time'], sensor_df['pitch'], c='green', label='pitch')
    plt.plot(sensor_df['time'], sensor_df['yaw'], c='orange', label='yaw')
    plt.legend(loc='best')
    plt.xlabel('time')
    plt.ylabel('degree')
    plt.title(file_name)

    for row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].itertuples():
        if row[0] % 1000 == 0:
            print("now it`s {0} step.".format(row[0]))
        pvdetect.step(row[0], row[1:5])
        hdetect.step(row[0], row[1:8], pvdetect.step_count)     # int(len(pvdetect.peak_df)) = stepcount
        walker.step(pvdetect.step_count, hdetect.heading)

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    print(len(pvdetect.periodic_peak))
    pvplotter.plot()

    plt.figure()
    plt.plot(hdetect.heading_df['time'], hdetect.heading_df['value'], c='blue', marker='o')
    plt.plot(pvdetect.peak_df['time'], pvdetect.peak_df['value'], c='green', marker='o')
    print(len(hdetect.heading_df))

    plt.figure()
    plt.plot(walker.pdr_df['pos_x'], walker.pdr_df['pos_y'])
    plt.xlabel('m')
    plt.ylabel('m')
    plt.axis('equal')

    # fig = plt.figure()
    # fig.suptitle(file_name)
    # ax1 = fig.add_subplot(2,1,1)
    # ax2 = fig.add_subplot(2,1,2)
    # ax1.scatter(pvdetect.acc_sq_df['time'], pvdetect.acc_sq_df['value_z'], c='orange')
    # ax1.set_title("Mrz")

    # motion_df = pd.DataFrame(columns=("time", "value"))
    # for idx,row in pvdetect.acc_sq_df.iterrows():
    #     if row['value_z'] > 0.6:
    #         motion_df.loc[idx] = [row['time'], 1]
    #     else:
    #         motion_df.loc[idx] = [row['time'], 0]
    #
    # ax2.plot(motion_df['time'], motion_df['value'], c = 'black')
    # ax2.set_title("Motion")
    # ax2.set_xlabel('time')

    plt.show()

    # plt.figure()
    # for idx, row in pvdetect.peak_df.iterrows():
    #     if idx >= 5:
    #         plt.scatter(row['time'], np.var(np.diff(pvdetect.peak_df.loc[idx - 5: idx]['time']), ddof=1),c='orange')
    #         #plt.ylim(0, 1000)
    #         plt.title(file_name)
    #         plt.xlabel('time')
    #         plt.ylabel('dev')
