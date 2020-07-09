import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PDR.modules.PeakValleyDetector import *
from PDR.modules.HeadingCalculator import *


class Walker:
    def __init__(self, step_length=0.65):
        self.pvdetect = PeakValleyDetector()
        self.pitchpvdetect = PeakValleyDetector(
            amp_threshold=0.8, step_interval=100)
        self.rollpvdetect = PeakValleyDetector(
            amp_threshold=0.8, step_interval=100)
        self.headingcalc = HeadingCalculator()
        self.step_length = step_length
        self.swing_step_length = step_length * 2
        self.peak_cnt_before = np.NaN
        self.swing_peak_cnt_before = np.NaN
        self.pdr_df = pd.DataFrame(
            columns=('idx', 'length', 'body', 'nav', 'rot', 'game', 'fusion'))
        self.mag_df = pd.DataFrame(
            columns=("time", "magx", "magy", "magz", "rmagx", "rmagy", "rmagz"))
        self.corner_df = pd.DataFrame(
            columns=('idx', 'body', 'nav', 'rot', 'game', 'fusion'))
        self.data_array = np.zeros([3, 5])
        self.pass_count = np.zeros(5)
        self.mode_df = pd.DataFrame(columns=(
            'time', 'roll_peak', 'roll_valley', 'pitch_peak', 'pitch_valley', 'mode'))
        self.time_before = 0
        self.roll_peak_count_before = 0
        self.roll_valley_count_before = 0
        self.pitch_peak_count_before = 0
        self.pitch_valley_count_before = 0

    def step(self, idx, time, acc, gyro, mag, vec, game_vec):
        acc_norm = np.sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)
        rotationMatrix = getRotationMatrixFromVector(game_vec, 9)
        vec_orientation = getOrientation(rotationMatrix)

        self.pvdetect.step(idx, time, acc_norm)
        self.headingcalc.step(time, gyro, mag, vec, game_vec)
        self.pitchpvdetect.step(idx, time, -vec_orientation[1])
        self.rollpvdetect.step(idx, time, -vec_orientation[2])
        rot_mag = rotate_mag(mag, vec)
        self.mag_df.loc[len(self.mag_df)] = [time, mag[0],
                                             mag[1], mag[2], rot_mag[0], rot_mag[1], rot_mag[2]]

        peak_cnt = len(self.pvdetect.peak_df)

        if time - self.time_before >= 2000:
            roll_peak_count = len(self.rollpvdetect.peak_df) - \
                self.roll_peak_count_before
            roll_valley_count = len(
                self.rollpvdetect.valley_df) - self.roll_valley_count_before
            pitch_peak_count = len(
                self.pitchpvdetect.peak_df) - self.pitch_peak_count_before
            pitch_valley_count = len(
                self.pitchpvdetect.valley_df) - self.pitch_valley_count_before
            mode = roll_peak_count + roll_valley_count + \
                pitch_peak_count + pitch_valley_count
            if mode > 2:
                mode = 1
            else:
                mode = 0
            self.mode_df.loc[len(self.mode_df)] = [time, roll_peak_count, roll_valley_count, pitch_peak_count,
                                                   pitch_valley_count, mode]
            self.time_before = time
            self.roll_peak_count_before = len(self.rollpvdetect.peak_df)
            self.roll_valley_count_before = len(self.rollpvdetect.valley_df)
            self.pitch_peak_count_before = len(self.pitchpvdetect.peak_df)
            self.pitch_valley_count_before = len(self.pitchpvdetect.valley_df)

        if peak_cnt >= 2:  # 피크가 들어온 이후 부터는
            if peak_cnt != self.peak_cnt_before:  # 새 피크가 들어왔다면
                peak_idx = self.pvdetect.peak_df["idx"].loc[peak_cnt - 1]
                peak_heading = self.headingcalc.heading_df.loc[peak_idx]
                heading_list = peak_heading
                self.pdr_df.loc[len(self.pdr_df)] = [
                    peak_idx, self.step_length, heading_list[1], heading_list[2], heading_list[3], heading_list[5], heading_list[6]]
                # 코너 판단하기
                peak_heading_list = self.pdr_df.loc[len(self.pdr_df) - 1][2:]
                self.data_array = np.insert(
                    self.data_array[:2], 0, peak_heading_list).reshape(3, 5)
                corner_heading_list = diff_angles(
                    self.data_array[0, :], self.data_array[2, :])
                is_corner = np.array([False, False, False, False, False])
                for idx, corner_heading in enumerate(corner_heading_list):
                    if self.pass_count[idx] == 0:
                        if self.data_array[2:, idx] != 0:  # 데이터 채워지는거 대기
                            if corner_heading >= 20 / (180 / np.pi):
                                is_corner[idx] = True
                                self.pass_count[idx] += 5  # 이건 5번동안 검사 안함
                                self.data_array[:, idx] = np.zeros(3)
                self.pass_count[self.pass_count > 0] -= 1  # 5번 검사안하는거 한번 줄임
                self.corner_df.loc[len(self.corner_df)] = np.insert(  # 코너 상태 업로드
                    is_corner, 0, peak_idx)
        self.peak_cnt_before = peak_cnt


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


def rotate_mag(mag, vec):
    rot_mag = np.matmul(getRotationMatrixFromVector(vec, 9), mag)
    return rot_mag


if __name__ == "__main__":
    pass
