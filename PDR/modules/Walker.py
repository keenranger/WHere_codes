import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PDR.modules.PeakValleyDetector import *
from PDR.modules.HeadingCalculator import *


class Walker:
    def __init__(self, step_length=0.65):
        self.pvdetect = PeakValleyDetector()
        self.headingcalc = HeadingCalculator()
        self.step_length = step_length
        self.peak_cnt_before = np.NaN
        self.pdr_df = pd.DataFrame(
            columns=('body_x', 'body_y', 'nav_x', 'nav_y', 'azimuth_x', 'azimuth_y'))
        self.pdr_df.loc[0] = [0, 0, 0, 0, 0, 0]

    def step(self, idx, time, acc, gyro, rot_vec, game_rot_vec):
        self.pvdetect.step(idx, time, acc)
        self.headingcalc.step(time, gyro, rot_vec, game_rot_vec)

        peak_cnt = len(self.pvdetect.peak_df)
        if peak_cnt >= 2:  # 피크가 들어온 이후 부터는
            if peak_cnt != self.peak_cnt_before:
                xy_list = self.pdr_df.loc[len(self.pdr_df)-1]
                peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt-1]
                last_peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt-2]
                # heading_list = (                    self.headingcalc.heading_df.loc[peak_idx] + self.headingcalc.heading_df.loc[last_peak_idx])/2
                heading_list = self.headingcalc.heading_df.loc[peak_idx]
                xy_list[0] += self.step_length * np.cos(heading_list[1])
                xy_list[1] += self.step_length * np.sin(heading_list[1])
                xy_list[2] += self.step_length * np.cos(heading_list[2])
                xy_list[3] += self.step_length * np.sin(heading_list[2])
                xy_list[4] += self.step_length * np.cos(heading_list[3])
                xy_list[5] += self.step_length * np.sin(heading_list[3])
                self.pdr_df.loc[len(self.pdr_df)] = xy_list
        self.peak_cnt_before = peak_cnt


if __name__ == "__main__":
    pass
