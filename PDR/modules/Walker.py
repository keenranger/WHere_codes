import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PDR.modules.PeakValleyDetector import *
from PDR.modules.HeadingCalculator import *


class Walker:
    def __init__(self, step_length=0.65):
        self.pvdetect = PeakValleyDetector()
        self.pitchpvdetect = PeakValleyDetector(
            amp_threshold=0.2, step_interval=300)
        self.headingcalc = HeadingCalculator()
        self.step_length = step_length
        self.swing_step_length = step_length * 2
        self.peak_cnt_before = np.NaN
        self.swing_peak_cnt_before = np.NaN
        self.pdr_df = pd.DataFrame(
            columns=('length', 'body', 'nav', 'rot', 'game', 'fusion'))

    def step(self, idx, time, acc, gyro, rot_vec, game_rot_vec):
        acc_norm = np.sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)
        mrz = np.sign(acc[2]) * (acc[2] ** 2) / \
            (acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)

        rotationMatrix = getRotationMatrixFromVector(game_rot_vec, 9)
        rot_vec_orientation = getOrientation(rotationMatrix)

        self.pvdetect.step(idx, time, acc_norm)
        self.headingcalc.step(time, gyro, rot_vec, game_rot_vec)
        self.pitchpvdetect.step(idx, time, -rot_vec_orientation[1])

        peak_cnt = len(self.pvdetect.peak_df)
        swing_peak_cnt = len(self.pitchpvdetect.peak_df)

        if peak_cnt == 1:  #첫 피크일때 game과 rot을 동일하게 맞춰주는 작업을 한다
            if peak_cnt != self.peak_cnt_before:
                peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 1]
                peak_heading = self.headingcalc.heading_df.loc[peak_idx]
                self.headingcalc.rot_reference = peak_heading['game'] - peak_heading['rot']
                self.headingcalc.heading_df.loc[peak_idx]['game'] -= self.headingcalc.rot_reference
            
        # mrz = 1
        # if mrz >= 0.5:  # 보고걷기
        if peak_cnt >= 2:  # 피크가 들어온 이후 부터는
            if peak_cnt != self.peak_cnt_before:

                peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 1]
                last_peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 2]
                heading_list = mean_angles(
                    self.headingcalc.heading_df.loc[peak_idx], self.headingcalc.heading_df.loc[last_peak_idx])
                # heading_list = self.headingcalc.heading_df.loc[peak_idx]
                self.pdr_df.loc[len(self.pdr_df)] = [
                    self.step_length, heading_list[1], heading_list[2], heading_list[3], heading_list[4], heading_list[4]]
        self.peak_cnt_before = peak_cnt
        # else:
        #     if swing_peak_cnt >= 1:
        #         if swing_peak_cnt != self.swing_peak_cnt_before:
        #             swing_peak_idx = self.pitchpvdetect.peak_df["idx"].loc[swing_peak_cnt - 1]
        #             heading_list = self.headingcalc.heading_df.loc[swing_peak_idx]
        #             self.pdr_df.loc[len(self.pdr_df)] = [
        #                 self.swing_step_length, heading_list[1], heading_list[2], heading_list[3], heading_list[4], heading_list[4]]
        #     self.swing_peak_cnt_before = swing_peak_cnt


def pdr_to_displacement(pdr_df):
    displacement_df = pd.DataFrame(
        columns=('body_x', 'body_y', 'nav_x', 'nav_y', 'rot_x', 'rot_y', 'game_x', 'game_y', 'fusion_x', 'fusion_y'))
    displacement_df['body_x'] = pdr_df['length'] * np.cos(pdr_df['body'])
    displacement_df['body_y'] = pdr_df['length'] * np.sin(pdr_df['body'])
    displacement_df['nav_x'] = pdr_df['length'] * np.cos(pdr_df['nav'])
    displacement_df['nav_y'] = pdr_df['length'] * np.sin(pdr_df['nav'])
    displacement_df['rot_x'] = pdr_df['length'] * np.cos(pdr_df['rot'])
    displacement_df['rot_y'] = pdr_df['length'] * np.sin(pdr_df['rot'])
    displacement_df['game_x'] = pdr_df['length'] * np.cos(pdr_df['game'])
    displacement_df['game_y'] = pdr_df['length'] * np.sin(pdr_df['game'])
    displacement_df['fusion_x'] = pdr_df['length'] * np.cos(pdr_df['fusion'])
    displacement_df['fusion_y'] = pdr_df['length'] * np.sin(pdr_df['fusion'])
    return displacement_df


def mean_angles(angle_list1, angle_list2):
    complex_list = np.exp(1j*angle_list1) + np.exp(1j*angle_list2)
    mean_angle_list = np.angle(complex_list)
    return mean_angle_list


if __name__ == "__main__":
    pass
