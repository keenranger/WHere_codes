#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PDR.modules.QuaternionCalculator import *

class HeadingCalculator:
    def __init__(self):
        self.gyro = [0, 0, 0, 1]
        self.mag = [0, 0, 0, 1]
        self.heading = 0  # raw gyro z를 적분한 heading
        self.processed_heading = 0  # rotaion M 을 거친 gyro z를 적분한 heading

        self.processed_gyro = [0, 0, 0, 1]  # rotaion M 을 거친 gyro data
        self.rotvec_ypr = [0,0,0]
        self.time_before = 0
        self.time = 0
        
        self.heading_df = pd.DataFrame(columns=("time", "value"))  # heading을 저장하기 위한 DataFrame
        self.processed_heading_df = pd.DataFrame(columns=("time", "value"))
        self.rotvec_heading_df = pd.DataFrame(columns=("time", "value"))

        self.step_count_before = 0
        self.flag = 0

    # row[0] : time ,row[1,2,3] = acc 3 axis, row[4,5,6] = gyro 3 axis
    # row[7,8,9] = mag 3 axis
    def step(self, idx, row, step_count):
        self.time = row[0]
        self.step_count = step_count
        self.gyro = [row[4], row[5], row[6], 1]
        self.mag = [row[7], row[8], row[9], 1]
        self.rotvec = np.array([row[10], row[11], row[12], row[13]])
        self.game_rotvec = np.array([row[15], row[16], row[17], row[18]])
        self.time_before = self.time

    def cal_heading(self, gyro):  # Calculation heading
        # self.tilting(acc)
        # RotationVector를 이용한 Roll, Pitch 계산
        # self.rollpitch_df.loc[len(self.rollpitch_df)] = [self.time, self.ypr[2], self.ypr[1], self.ypr[0]]
        rotationMatrix = getRotationMatrixFromVector(self.game_rotvec, 16)
        self.processed_gyro = np.matmul(rotationMatrix, self.gyro)
        self.rotvec_ypr = getOrientation(rotationMatrix(self.game_rotvec))

        # self.processed_gyro = self.Rotation_m(self.ypr[2], self.ypr[1], self.gyro)

        # self.processed_mag = np.matmul(gOFV.getRotationMatrixFromVector(self.rotvec), self.mag)
        # self.processed_mag_df.loc[len(self.processed_mag_df)] = [self.time, self.processed_mag[0], self.processed_mag[1], self.processed_mag[2]]

        # 처리된 자이로 적분하면 heading이 나온다
        self.heading += gyro[2] * (self.time - self.time_before) * self.Ms2S
        self.processed_heading += self.processed_gyro[2] * (self.time - self.time_before) * self.Ms2S

        # 초기 시간이 0이 아닐 수 있다.
        if self.flag == 0:
            self.heading = 0
            self.processed_heading = 0
            self.flag = 1

        # 걸음이 발생할 때 마다
        if self.step_count - self.step_count_before != 0:
            self.heading_df.loc[self.step_count] = [self.time, self.heading * self.RtoD]
            self.processed_heading_df.loc[self.step_count] = [self.time, self.processed_heading * self.RtoD]
            self.rotvec_heading_df.loc[self.step_count] = [self.time, self.rotvec_ypr[0] * self.RtoD]
            self.step_count_before = self.step_count