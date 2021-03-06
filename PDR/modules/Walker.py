import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PDR.modules.PeakValleyDetector import *
from PDR.modules.HeadingCalculator import *

correlation_window = 10 # 10개의 헤딩이 비스하고 
reliable_window = 3 #그 비슷한 헤딩이 세번연속면


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
        self.pdr_df = pd.DataFrame(columns=('idx', 'length'))
        self.mag_df = pd.DataFrame(
            columns=("time", "magx", "magy", "magz", "rmagx", "rmagy", "rmagz"))
        self.corner_df = pd.DataFrame(
            columns=('idx', 'body', 'nav', 'rot', 'game', 'fusion'))
        self.correlation_df = pd.DataFrame(
            columns=('idx', 'correlation'))
        self.data_array = np.zeros([3, 5])
        self.pass_count = np.zeros(5)
        self.mode_df = pd.DataFrame(columns=(
            'time', 'roll_peak', 'roll_valley', 'pitch_peak', 'pitch_valley', 'mode'))
        self.time_before = 0
        self.roll_pitch_pv_count_before = np.zeros(4)

    def step(self, idx, time, acc, gyro, mag, rot_vec, game_vec):
        # 뒤에 사용하기위해 미리 데이터 처리
        acc_norm = np.sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)
        rotationMatrix = getRotationMatrixFromVector(rot_vec, 9)
        gameRotationMatrix = getRotationMatrixFromVector(game_vec, 9)
        rotOrientation = getOrientation(rotationMatrix)
        gameOrientation = getOrientation(gameRotationMatrix)
        # step 검출을 위해 알맞은 값들을 pvdetector에 넣어줌
        self.pitchpvdetect.step(idx, time, -gameOrientation[1])
        self.rollpvdetect.step(idx, time, -gameOrientation[2])
        # heading 계산을 위해 값들을 넣어줌
        self.headingcalc.step(time, gyro, mag, rot_vec, game_vec)

        # 2초마다 모드 검사
        if time - self.time_before >= 2000:
            # roll peak, roll valley, pitch peak, pitch valley
            roll_pitch_pv_count_now = np.array([len(self.rollpvdetect.peak_df), len(
                self.rollpvdetect.valley_df), len(self.pitchpvdetect.peak_df), len(self.pitchpvdetect.valley_df)])
            roll_pitch_pv_count = roll_pitch_pv_count_now - self.roll_pitch_pv_count_before
            mode = sum(roll_pitch_pv_count)
            if mode >= 2:
                mode = 1
            else:
                mode = 0
            self.mode_df.loc[len(self.mode_df)] = [time, roll_pitch_pv_count[0], roll_pitch_pv_count[1],
                                                   roll_pitch_pv_count[2], roll_pitch_pv_count[3], mode]
            self.time_before = time
            self.roll_pitch_pv_count_before = roll_pitch_pv_count_now

        if self.pvdetect.step(idx, time, acc_norm):  # peak나 valley 갯수 변화 있을때만 실행
            peak_cnt = len(self.pvdetect.peak_df)
            if peak_cnt >= 1:  # 피크가 들어온 이후 부터는
                if peak_cnt != self.peak_cnt_before:  # 새 피크가 들어왔다면
                    # peak들을 통해 PDR 하는 부분
                    peak_idx = int(
                        self.pvdetect.peak_df["idx"].loc[peak_cnt - 1])
                    self.pdr_df.loc[len(self.pdr_df)] = [
                        peak_idx, self.step_length]
                    # 헤딩 보정 할까?
                    if peak_cnt >= correlation_window:
                        idx_window = self.pdr_df['idx'].tail(
                            correlation_window)
                        nav_arr = self.headingcalc.heading_array[list(
                            map(int, idx_window)), 2].copy()
                        rot_arr = self.headingcalc.heading_array[list(
                            map(int, idx_window)), 3].copy()
                        correlation = diff_angles(
                            rot_arr - rot_arr[0], nav_arr - nav_arr[0]).sum()/correlation_window
                        self.correlation_df.loc[len(self.correlation_df)] = [
                            idx, correlation]
                        
                        if correlation < 0.1:
                            modify_idx = int(
                                self.pdr_df.loc[len(self.pdr_df)-correlation_window]['idx'])
                            coefficient = 2 * \
                                (sigmoid(-(correlation - 0.1)) - 0.5)
                            # 45도 차이 이상 나게 되면
                            if diff_angles(self.headingcalc.heading_array[modify_idx, 3], self.headingcalc.heading_array[modify_idx, 5]) >= np.deg2rad(15):
                                self.headingcalc.fusion_compensation = rot_angles(
                                    self.headingcalc.heading_array[modify_idx, 3], self.headingcalc.heading_array[modify_idx, 2])

                            # mean_angle = mean_angles(
                            #     self.headingcalc.heading_df.loc[modify_idx]['nav'], self.headingcalc.heading_df.loc[modify_idx]['rot'], alpha=coefficient)
                            # angle_difference = self.headingcalc.heading_df.loc[
                            #     modify_idx]['nav'] - mean_angle
                            # self.headingcalc.heading_df.loc[modify_idx:] -= angle_difference

                    # 코너 판단하기
                    peak_heading_list = self.headingcalc.heading_array[peak_idx, 1:]
                    self.data_array = np.insert(
                        self.data_array[:2], 0, peak_heading_list).reshape(3, 5)
                    corner_heading_list = diff_angles(
                        self.data_array[0, :], self.data_array[2, :])
                    is_corner = np.array([False, False, False, False, False])
                    for idx, corner_heading in enumerate(corner_heading_list):
                        if self.pass_count[idx] == 0:
                            if self.data_array[2:, idx] != 0:  # 데이터 채워지는거 대기
                                if corner_heading >= np.deg2rad(30):
                                    is_corner[idx] = True
                                    self.pass_count[idx] += 5  # 이건 5번동안 검사 안함
                                    self.data_array[:, idx] = np.zeros(3)
                    self.pass_count[self.pass_count >
                                    0] -= 1  # 5번 검사안하는거 한번 줄임
                    self.corner_df.loc[len(self.corner_df)] = np.insert(  # 코너 상태 업로드
                        is_corner, 0, peak_idx)
            self.peak_cnt_before = peak_cnt


if __name__ == "__main__":
    pass
