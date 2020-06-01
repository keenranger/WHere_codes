from PDR.modules import PeakValleyDetector
from PDR.modules import PeakValleyPlotter
from PDR.modules import SensorPlotter
from PDR.modules import DataLoader
from PDR.modules import HeadingCalculator
from PDR.modules import Walker

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "rr4"
    pvloader = DataLoader.DataLoader("c:/Users/user/Desktop/ssrc_PDR/PDR/data/200601_c.db", file_name)
    pvloader.DBLoader()
    sensor_df = pvloader.sensor_df
    # sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0]  # 처음시간으로 빼줌 #시간 0부터 시작
    sensor_df = sensor_df[0:]

    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    tilting_df = pd.DataFrame(columns=("time", "roll", 'pitch'))
    tilting_avg_df = pd.DataFrame(columns=("time", "roll", "pitch"))

    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)

    tilting_df['time'] = sensor_df['time']
    tilting_avg_df['time'] = sensor_df['time']

    #
    tilting_df['roll'] = np.rad2deg(
        np.arctan(sensor_df['accx'] / np.sqrt(sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)))
    tilting_df['pitch'] = np.rad2deg(
        np.arctan(sensor_df['accy'] / np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accz'] ** 2)))

    tilting_avg_df['roll'] = tilting_df['roll'].rolling(30, min_periods=1).mean()

    # plt.figure()
    # plt.plot(tilting_df['time'], tilting_df['roll'], c='blue', label="roll")
    # plt.plot(tilting_df['time'], tilting_df['pitch'], c='green', label="pitch")
    # plt.plot(sensor_df['time'], np.rad2deg(sensor_df['roll']), c='orange', label="roll_out")
    # plt.plot(sensor_df['time'], np.rad2deg(sensor_df['pitch']), c='cyan', label="pitch_out")
    # plt.xlabel('time')
    # plt.ylabel('degree')
    # plt.legend(loc='best')

    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    # heading 검출
    hdetect = HeadingCalculator.HeadingCalculator()
    # PDR
    walker = Walker.Walker()
    processed_walker = Walker.Walker()

    for row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'roll', 'pitch']].itertuples():
        if row[0] % 1000 == 0:
            print("now it`s {0} step.".format(row[0]))
        pvdetect.step(row[0], row[1:5])
        hdetect.step(row[0], row[1:10], pvdetect.step_count)  # int(len(pvdetect.peak_df)) = stepcount
        walker.step(pvdetect.step_count, hdetect.heading)
        processed_walker.step(pvdetect.step_count, hdetect.processed_heading)

    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    print(len(pvdetect.periodic_peak))

    plt.figure()
    plt.plot(tilting_avg_df['time'], tilting_avg_df['roll'], c='green',linewidth=2.5)
    plt.plot(hdetect.rollpitch_df['time'], hdetect.rollpitch_df['roll'], c='orange')

    sensorplot = SensorPlotter.SensorPlotter(sensor_df, file_name)
    # sensorplot.AccPlot()
    # sensorplot.GyroPlot()

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    # pvplotter.plot()  # norm & peak & valley plot
    # hdetect.Heading_plot(file_name)

    # plt.figure()
    # walker.PDR_plot(file_name, "Body.f")
    # processed_walker.PDR_plot(file_name, "Nav.f")

    plt.show()
