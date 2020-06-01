from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import SensorPlotter
from modules import DataLoader
from modules import HeadingDetector
from modules import Walker
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    file_name = "h2"
    pvloader = DataLoader.DataLoader("data/0520headingtest.txt", file_name)
    pvloader.TxTLoader()
    sensor_df = pvloader.sensor_df
    # sensor_df['time'] = sensor_df['time'] - sensor_df['time'][0]  # 처음시간으로 빼줌 #시간 0부터 시작
    sensor_df = sensor_df[600:]

    # 알고리즘엔 쓰이지않고 plot만을 위해 사용되는 부분, 처리속도를 위해 따로 뺌
    norm_df = pd.DataFrame(columns=("time", "value"))
    tilting_df = pd.DataFrame(columns=("time", "roll", 'pitch'))
    tilting_avg_df = pd.DataFrame(columns=("time", "roll", "pitch"))
    grav_acc_df = pd.DataFrame(columns=("time", "value_x", "value_y", "value_z"))

    norm_df['time'] = sensor_df['time']
    norm_df['value'] = np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)

    tilting_df['time'] = sensor_df['time']
    tilting_avg_df['time'] = sensor_df['time']

    #   휴대폰에서 제공하는 roll, pitch 와 회전방향을 맞추기위해 -
    tilting_df['roll'] = np.rad2deg(
        np.arctan(sensor_df['accx'] / np.sqrt(sensor_df['accy'] ** 2 + sensor_df['accz'] ** 2)))
    tilting_df['pitch'] = np.rad2deg(
        np.arctan(sensor_df['accy'] / np.sqrt(sensor_df['accx'] ** 2 + sensor_df['accz'] ** 2)))

    plt.figure()
    plt.plot(tilting_df['time'], tilting_df['roll'], c='blue')
    plt.plot(tilting_df['time'], tilting_df['pitch'], c='green')
    plt.plot(sensor_df['time'], np.rad2deg(sensor_df['roll']), c='orange')
    plt.plot(sensor_df['time'], np.rad2deg(sensor_df['pitch']), c='cyan')

    # tilting_avg_df['roll'] = tilting_df['roll'].rolling(30, min_periods=1).mean()
    # tilting_avg_df['pitch'] = tilting_df['pitch'].rolling(30, min_periods=1).mean()

    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()
    # heading 검출
    hdetect = HeadingDetector.HeadingDetector()
    # PDR
    walker = Walker.Walker()
    processed_walker = Walker.Walker()
    processed_walker2 = Walker.Walker()

    for row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz', 'roll', 'pitch']].itertuples():
        if row[0] % 1000 == 0:
            print("now it`s {0} step.".format(row[0]))
        pvdetect.step(row[0], row[1:5])
        hdetect.step(row[0], row[1:10], pvdetect.step_count)  # int(len(pvdetect.peak_df)) = stepcount
        walker.step(pvdetect.step_count, hdetect.heading)
        processed_walker.step(pvdetect.step_count, hdetect.processed_heading)
        processed_walker2.step(pvdetect.step_count, hdetect.processed_heading2)

    print(len(pvdetect.peak_df))
    print(len(pvdetect.valley_df))
    print(len(pvdetect.periodic_peak))

    sensorplot = SensorPlotter.SensorPlotter(sensor_df, file_name)
    sensorplot.AccPlot()
    sensorplot.GyroPlot()

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect, norm_df, file_name)
    pvplotter.plot()  # norm & peak & valley plot
    hdetect.Heading_plot(file_name)

    plt.figure()
    walker.PDR_plot(file_name)
    processed_walker.PDR_plot(file_name)
    processed_walker2.PDR_plot(file_name)
    plt.show()