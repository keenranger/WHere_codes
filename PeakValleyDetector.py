import numpy as np
import pandas as pd

class PeakValleyDetector:
    def __init__(self, data_len, min_threshold=9, max_threshold = 11, step_interval = 100):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.step_interval = step_interval
        self.peak_df = pd.DataFrame(columns=("time", "value"))
        self.valley_df = pd.DataFrame(columns=("time", "value"))
        self.lastPeak = np.array([-1, 0]) #마지막 피크의 시간과 값이 닮겨있음
        self.lastValley = np.array([-1 ,20]) #마지막 밸리의 시간과 값이 닮겨있음
        self.lastUpdate = 0
        self.acc = np.zeros(3)
        self.finding = 'peak'
        self.norm_df = pd.DataFrame(columns=("time", "value"))

    def step(self, index, row): #row가져와서 class에 저장하는 부분
        self.current_time = row[0]
        self.acc = row[1:4]
        self.euc_norm = np.sqrt( self.acc[0] ** 2 + self.acc[1] ** 2\
        + self.acc[2] **2)
        self.norm_df.loc[index] = [self.current_time, self.euc_norm]
        self.finding_switcher()
        self.norm_threshold()

    def finding_switcher(self): #피크 -> 중간값이하 밸리 ->중간값이상 나오면 change
        if (self.finding == 'peak'): #피크를 찾는 중 이라면
            if (self.lastPeak[0] != -1): #피크가 초기화 이후로 한번이라도 업데이트 됐다면
                if (self.euc_norm < self.min_threshold): #다음 밸리값이 나오면
                    if ( (self.current_time - self.lastUpdate) > self.step_interval):
                        self.peak_df = self.peak_df.append({'time': self.lastPeak[0],\
                        'value': self.lastPeak[1]}, ignore_index=True)
                        self.lastPeak = [-1, 0] #사용했으므로 비워줍시다
                        self.lastUpdate = self.current_time
                        self.finding = 'valley'
        else:
            if (self.lastValley[0] != -1): #밸리가 초기화 이후로 한번이라도 업데이트 됐다면
                if (self.euc_norm > self.max_threshold): #다음 피크값 나오면
                    if ((self.current_time - self.lastUpdate) > self.step_interval):
                        self.valley_df = self.valley_df.append({'time': self.lastValley[0],\
                        'value': self.lastValley[1]}, ignore_index=True)
                        self.lastValley = [-1, 20] #사용했으므로 비워줍시다
                        self.lastUpdate = self.current_time
                        self.finding = 'peak'

    def norm_threshold(self): #여기서 norm 값이 threshold 못넘는 값들은 그냥 넘깁니다.
        if (self.euc_norm > self.max_threshold): #피크 threshold를 넘겼을때
            if (self.euc_norm > self.lastPeak[1]): #최댓값이 아니라면
                self.lastPeak = [self.current_time, self.euc_norm] #최댓값으로 업데이트
        if (self.euc_norm < self.min_threshold): #밸리 threshold 이하일때
            if (self.euc_norm < self.lastValley[1]): #최솟값이 아니라면
                self.lastValley = [self.current_time, self.euc_norm] #최솟값으로 업데이트