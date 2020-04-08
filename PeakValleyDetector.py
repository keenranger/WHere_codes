import numpy as np
import pandas as pd

class PeakValleyDetector:
    def __init__(self, min_threshold=8.5, max_threshold = 11, step_interval = 100):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.step_interval = step_interval
        self.peak_df = pd.DataFrame(columns=("time", "value"))
        self.valley_df = pd.DataFrame(columns=("time", "value"))
        self.lastPeak = np.array([np.inf, -np.inf]) #마지막 피크의 시간과 값이 닮겨있음
        self.lastValley = np.array([-np.inf ,np.inf]) #마지막 밸리의 시간과 값이 닮겨있음
        self.updating = "peak"

    def step(self, index, row): #row가져와서 class에 저장하는 부분
        self.current_time = row[0]
        self.euc_norm = np.sqrt( row[1] ** 2 +row[2] ** 2 + row[3] **2)
        self.norm_threshold()

    def norm_threshold(self): #여기서 norm 값이 threshold 못넘는 값들은 그냥 넘깁니다.
        if (self.euc_norm > self.max_threshold): #피크 threshold를 넘겼을때
            if ( (self.current_time - self.lastValley[0]) > self.step_interval): #시간간격이 충분하면
                self.updating = 'peak'
                self.finder("valley") #finder는 한번만 실행하면 됨
            self.updater()
        if (self.euc_norm < self.min_threshold): #밸리 threshold 이하일때
            if ( (self.current_time - self.lastPeak[0]) > self.step_interval): #시간간격이 충분하면
                self.updating = 'valley'
                self.finder("peak")
            self.updater()
            
    def finder(self, finding):
        if (finding == 'peak'):
            self.peak_df.loc[len(self.peak_df)] = [self.lastPeak[0], self.lastPeak[1]]
            self.finding = None
            self.lastPeak = [np.inf, -np.inf] #시간간격이 부족하거나, 사용했습니다. 비워줘야합니다
        elif (finding == 'valley'):
            self.finding = None
            if (self.lastValley[1] != np.inf): #처음 lastvalley 제외
                self.valley_df.loc[len(self.valley_df)] = [self.lastValley[0], self.lastValley[1]]
            self.lastValley = [np.inf ,np.inf] #시간간격이 부족하거나, 사용했습니다. 비워줘야합니다

    def updater(self):
        if (self.updating == 'peak'):
            if (self.euc_norm > self.lastPeak[1]): #최댓값이 아니라면
                self.lastPeak = [self.current_time, self.euc_norm] #최댓값으로 업데이트
        elif (self.updating == 'valley'):
            if (self.euc_norm < self.lastValley[1]): #최솟값이 아니라면
                self.lastValley = [self.current_time, self.euc_norm] #최솟값으로 업데이트
        

            