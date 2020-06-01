import numpy as np
import pandas as pd


class PeakValleyDetector:
    def __init__(self, amp_threshold=3, step_interval=100):
        self.amp_threshold = amp_threshold
        self.step_interval = step_interval
        self.peak_df = pd.DataFrame(columns=("time", "value"))
        self.valley_df = pd.DataFrame(columns=("time", "value"))
        self.periodic_peak = pd.DataFrame(columns=("time", "value"))
        self.acc_sq_df = pd.DataFrame(columns=("time", "value_x", "value_y", "value_z"))
        self.acc_sq_sum = 0
        self.euc_norm = 0
        self.data_array = np.array([np.nan, np.nan, np.nan])
        self.mr_x_array = np.array([np.nan, np.nan, np.nan])    # Motion ratio 를 구하기위한 array
        self.mr_y_array = np.array([np.nan, np.nan, np.nan])
        self.mr_z_array = np.array([np.nan, np.nan, np.nan])
        self.time_before = -np.inf
        self.lastPeak = np.array([np.inf, -np.inf])  # 마지막 피크의 시간과 값이 닮겨있음
        self.lastValley = np.array([-np.inf, 7])  # 마지막 밸리의 시간과 값이 닮겨있음
        self.lastAcc = np.array([np.inf, -np.inf, -np.inf, -np.inf])
        self.updating = "peak"
        self.step_count = 0

    def step(self, index, row):  # row가져와서 class에 저장하는 부분
        self.acc_sq_sum = row[1] ** 2 + row[2] ** 2 + row[3] ** 2   # row[1] : x ,row[2] : y, row[3] : z
        self.euc_norm = np.sqrt(self.acc_sq_sum)
        self.data_array = np.insert(self.data_array[:2], 0, self.euc_norm)
        if self.acc_sq_sum != 0:
            self.mr_x_array = np.insert(self.mr_x_array[:2], 0, np.sign(row[1]) * (row[1] ** 2) / self.acc_sq_sum)
            self.mr_y_array = np.insert(self.mr_y_array[:2], 0, np.sign(row[2]) * (row[2] ** 2) / self.acc_sq_sum)
            self.mr_z_array = np.insert(self.mr_z_array[:2], 0, np.sign(row[3]) * (row[3] ** 2) / self.acc_sq_sum)

        self.local_minmax_finder()
        self.time_before = row[0]

    def local_minmax_finder(self):
        if self.data_array[1] > self.data_array[0] and \
                self.data_array[1] >= self.data_array[2]:  # local peak
            if (self.data_array[1] - self.lastValley[1]) > self.amp_threshold:
                if (self.time_before - self.lastValley[0]) > self.step_interval:
                    self.updating = 'peak'
                    self.finder("valley")
            self.updater()
        elif self.data_array[1] < self.data_array[0] and \
                self.data_array[1] <= self.data_array[2]:  # local valley
            if (self.lastPeak[1] - self.data_array[1]) > self.amp_threshold:
                # 시간간격이 충분하면
                if (self.time_before - self.lastPeak[0]) > self.step_interval:
                    self.updating = 'valley'
                    self.finder("peak")
            self.updater()


    def finder(self, finding):
        if finding == 'peak':
            self.peak_df.loc[len(self.peak_df)] = [self.lastPeak[0], self.lastPeak[1]]
            self.acc_sq_df.loc[len(self.acc_sq_df)] = [self.lastAcc[0], self.lastAcc[1], self.lastAcc[2],
                                                       self.lastAcc[3]]
            self.step_count += 1
            self.lastPeak = [np.inf, -np.inf]  # 시간간격이 부족하거나, 사용했습니다. 비워줘야합니다
            self.peroid_checker()
        elif finding == 'valley':
            self.valley_df.loc[len(self.valley_df)] = [
                self.lastValley[0], self.lastValley[1]]
            self.lastValley = [np.inf, np.inf]  # 시간간격이 부족하거나, 사용했습니다. 비워줘야합니다

    def updater(self):
        if self.updating == 'peak':
            if self.data_array[1] > self.lastPeak[1]:  # 최댓값이 아니라면
                self.lastPeak = [self.time_before,
                                 self.data_array[1]]  # 최댓값으로 업데이트
                self.lastAcc = [self.time_before, self.mr_x_array[1], self.mr_y_array[1], self.mr_z_array[1]]
        elif self.updating == 'valley':
            if self.data_array[1] < self.lastValley[1]:  # 최솟값이 아니라면
                self.lastValley = [self.time_before,
                                   self.data_array[1]]  # 최솟값으로 업데이트

    def peroid_checker(self):
        if len(self.peak_df) >= 5:
            if np.var(np.diff(self.peak_df.loc[len(self.peak_df) - 5:]['time']), ddof=1) < 35000:
                self.periodic_peak = self.periodic_peak.append(
                    self.peak_df.loc[len(self.peak_df) - 5:])
                self.periodic_peak = self.periodic_peak.drop_duplicates()
