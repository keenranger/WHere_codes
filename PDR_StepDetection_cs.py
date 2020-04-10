import numpy as np
import pandas as pd


######################################
# 센서데이터 로깅 100Hz

# 걸음 검출 알고리즘 조건
# 1. peak > peak_threshold & valley < valley_threshold
# 2. 현재 peak(valley) 시간 - 이전 peak(valley) 시간 이 time_threshold보다 작으면 비교 후 값이 큰(작은) peak(valley) 로 업데이트
# -> time_threshold 는 현재 짧은 보폭의 peak 간 주기 보다 약간 짧은 30ms 로 설정
# 3. peak 다음에는 valley 가 온다
######################################


class StepDetection:
    def __init__(self, lower_threshold=8.8, upper_threshold=11, time_threshold=200):
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.current_time = 0
        self.acc_data = np.zeros((1, 3))
        self.acc_norm = 0
        self.acc_norm_plot = pd.DataFrame(columns=("time", "norm"))  # plot을 위해 저장
        self.peak_plot = pd.DataFrame(columns=("time", "peak"))  # plot을 위해 저장
        self.isvalley = False
        self.pre_peakdata = [np.inf, -np.inf]  # 0 : 시간 1 : 값
        self.time_threshold = time_threshold

    def step(self, index, row):  # row 가져와서 class에 저장하는 부분
        self.current_time = row[0]
        self.acc_data = row[1:]
        self.acc_norm = np.sqrt(pow(self.acc_data[0], 2) + pow(self.acc_data[1], 2) + pow(self.acc_data[2], 2))  # 가속도 센서 norm data 계산
        self.norm_threshold()

    def norm_threshold(self):  # threshold에 따른 상태 구분
        if self.acc_norm > self.upper_threshold:
            if self.isvalley:
                self.timedetect()
                self.updatepeak()  # peak 찾았어 및 update
            else:
                self.updatepeak()

        if self.acc_norm < self.lower_threshold:
            self.isvalley = True

    def updatepeak(self):
        if self.acc_norm >= self.pre_peakdata[1]:
            self.pre_peakdata = [self.current_time, self.acc_norm]

    def timedetect(self):
            if self.current_time - self.pre_peakdata[0] >= self.time_threshold:
                self.peak_plot.loc[len(self.peak_plot)] = [self.pre_peakdata[0], self.pre_peakdata[1]]
                self.pre_peakdata = [np.inf, -np.inf] #사용한거 다시 초기화
                self.isvalley = False
