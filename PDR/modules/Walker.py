import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PDR.modules.PeakValleyDetector import *
from PDR.modules.HeadingCalculator import *
from PDR.modules.PitchPVDetector import *


class Walker:
    def __init__(self, step_length=0.65):
        self.pvdetect = PeakValleyDetector()
        self.headingcalc = HeadingCalculator()
        self.pitchpvdetect = PitchPVDetector()
        self.step_length = step_length
        self.peak_cnt_before = np.NaN
        self.pdr_df = pd.DataFrame(
            columns=('length', 'body', 'nav', 'azimuth'))

    def step(self, idx, time, acc, gyro, rot_vec, game_rot_vec, orientation):
        self.pvdetect.step(idx, time, acc)
        self.pitchpvdetect.step(idx, time, np.rad2deg(-orientation[1]))
        self.headingcalc.step(time, gyro, rot_vec, game_rot_vec)

        peak_cnt = len(self.pvdetect.peak_df)
        if peak_cnt >= 2:  # 피크가 들어온 이후 부터는
            if peak_cnt != self.peak_cnt_before:
                peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 1]
                last_peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 2]
                heading_list = mean_angles(
                    self.headingcalc.heading_df.loc[peak_idx], self.headingcalc.heading_df.loc[last_peak_idx])
                # heading_list = self.headingcalc.heading_df.loc[peak_idx]
                self.pdr_df.loc[len(self.pdr_df)] = [
                    self.step_length, heading_list[1], heading_list[2], heading_list[3]]
        self.peak_cnt_before = peak_cnt


def pdr_to_displacement(pdr_df):
    displacement_df = pd.DataFrame(
        columns=('body_x', 'body_y', 'nav_x', 'nav_y', 'azimuth_x', 'azimuth_y'))
    displacement_df['body_x'] = pdr_df['length'] * np.cos(pdr_df['body'])
    displacement_df['body_y'] = pdr_df['length'] * np.sin(pdr_df['body'])
    displacement_df['nav_x'] = pdr_df['length'] * np.cos(pdr_df['nav'])
    displacement_df['nav_y'] = pdr_df['length'] * np.sin(pdr_df['nav'])
    displacement_df['azimuth_x'] = pdr_df['length'] * np.cos(pdr_df['azimuth'])
    displacement_df['azimuth_y'] = pdr_df['length'] * np.sin(pdr_df['azimuth'])
    return displacement_df


def mean_angles(angle_list1, angle_list2):
    complex_list = np.exp(1j * angle_list1) + np.exp(1j * angle_list2)
    mean_angle_list = np.angle(complex_list)
    return mean_angle_list


if __name__ == "__main__":
    pass
