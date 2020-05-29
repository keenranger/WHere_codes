from modules import PeakValleyDetector
from modules import PeakValleyPlotter
from modules import DataLoader
from matplotlib import font_manager, rc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
font_name = font_manager.FontProperties(fname="c:/git/KoPubWorld Dotum Medium.ttf").get_name()
rc('font', family=font_name)
if __name__ == "__main__":
    # sql을 통해 dataframe으로 db 가져오기
    file_name = "0410t1"
    pvloader = DataLoader.DataLoader("./data/0410.db", file_name)
    sensor_df = pvloader.sensor_df
    sensor_df['time'] = sensor_df['time'] - \
        sensor_df['time'][0]  # 처음시간으로 빼줌 #시간 0부터 시작
    fig, ax = plt.subplots(3,2)
    fig.suptitle('보고 걷기 - 전화 - 보고 걷기 - 주머니 - 보고걷기 - 스윙 - 보고 걷기')
    ax[0][0].plot(sensor_df['time'], sensor_df['accx'])
    ax[0][0].set_title('accx')
    ax[1][0].plot(sensor_df['time'], sensor_df['accy'])
    ax[1][0].set_title('accy')
    ax[2][0].plot(sensor_df['time'], sensor_df['accz'])
    ax[2][0].set_title('accz')
    ax[0][1].plot(sensor_df['time'], sensor_df['accx'] - sensor_df['accy'])
    ax[0][1].set_title('accx - accy')
    ax[1][1].plot(sensor_df['time'], sensor_df['accy'] - sensor_df['accz'])
    ax[1][1].set_title('accy - accz')
    ax[2][1].plot(sensor_df['time'], sensor_df['accz'] - sensor_df['accx'])
    ax[2][1].set_title('accz - accx')
    plt.show()