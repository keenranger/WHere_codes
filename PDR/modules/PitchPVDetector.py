import numpy as np
import pandas as pd


class PitchPVDetector:
    def __init__(self, amp_threshold=10, step_interval=300):
        self.amp_threshold = amp_threshold
        self.step_interval = step_interval
        self.pitch_peak_df = pd.DataFrame(columns=("idx", "time", "value"))
        self.pitch_valley_df = pd.DataFrame(columns=("idx", "time", "value"))
        self.data_array = np.array([np.nan, np.nan, np.nan])
        self.time_before = -np.inf  # 전 스탭의 시간
        self.lastPeak = np.array([-1, np.inf, -np.inf])  # 마지막 피크의 시간과 값이 닮겨있음
        self.lastValley = np.array([-1, -np.inf, 7])  # 마지막 밸리의 시간과 값이 닮겨있음
        self.updating = "peak"

    def step(self, idx, time, pitch):  # row가져와서 class에 저장하는 부분
        self.data_array = np.insert(self.data_array[:2], 0, pitch)
        self.local_pv_finder(idx)
        self.time_before = time

    def local_pv_finder(self, idx):
        # local peak
        if self.data_array[1] > self.data_array[0] and self.data_array[1] >= self.data_array[2]:
            if (self.data_array[1] - self.lastValley[2]) > self.amp_threshold:
                if (self.time_before - self.lastValley[1]) > self.step_interval:
                    self.updating = 'peak'
                    self.finder("valley")
            self.updater(idx)
        # local valley
        elif self.data_array[1] < self.data_array[0] and self.data_array[1] <= self.data_array[2]:
            if (self.lastPeak[2] - self.data_array[1]) > self.amp_threshold:
                # 시간간격이 충분하면
                if (self.time_before - self.lastPeak[1]) > self.step_interval:
                    self.updating = 'valley'
                    self.finder("peak")
            self.updater(idx)

    def finder(self, finding):
        if finding == 'peak':
            self.pitch_peak_df.loc[len(self.pitch_peak_df)] = self.lastPeak
            # 시간간격이 부족하거나, 사용했습니다. 비워줘야합니다
            self.lastPeak = [-1, np.inf, -np.inf]

        elif finding == 'valley':
            self.pitch_valley_df.loc[len(self.pitch_valley_df)] = self.lastValley
            # 시간간격이 부족하거나, 사용했습니다. 비워줘야합니다
            self.lastValley = [-1, np.inf, np.inf]

    def updater(self, idx):
        if self.updating == 'peak':
            if self.data_array[1] > self.lastPeak[2]:  # 최댓값이 아니라면
                self.lastPeak = [idx, self.time_before,
                                 self.data_array[1]]  # 최댓값으로 업데이트

        elif self.updating == 'valley':
            if self.data_array[1] < self.lastValley[2]:  # 최솟값이 아니라면
                self.lastValley = [idx, self.time_before,
                                   self.data_array[1]]  # 최솟값으로 업데이트
