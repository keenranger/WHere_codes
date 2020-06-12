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
        self.rot_vec_orientation = [0, 0, 0]
        self.time_before = 0
        self.time = 0
        self.rot_vec = [0, 0, 0, 0]
        self.game_rot_vec = [0, 0, 0, 0]

        self.heading_df = pd.DataFrame(columns=("time", "body", "nav", "azimuth"))  # heading을 저장하기 위한 DataFrame
        self.step_count_before = 0
        self.flag = 0

    # row[0] : time ,row[1,2,3] = acc 3 axis, row[4,5,6] = gyro 3 axis
    # row[7,8,9] = mag 3 axis
    def step(self, idx, row, step_count):
        self.time = row[0]
        self.gyro = [row[4], row[5], row[6], 1]
        self.rot_vec = np.array([row[7], row[8], row[9], row[10]])
        self.game_rot_vec = np.array([row[11], row[12], row[13], row[14]])
        self.cal_heading(self.gyro, step_count)
        self.time_before = self.time

    def cal_heading(self, gyro, step_count):  # Calculation heading
        # RotationVector를 이용한 Roll, Pitch 계산
        rotationMatrix = getRotationMatrixFromVector(self.game_rot_vec, 16)
        self.processed_gyro = np.matmul(rotationMatrix, self.gyro)
        self.rot_vec_orientation = getOrientation(rotationMatrix)

        # 처리된 자이로 적분하면 heading이 나온다
        self.heading += gyro[2] * (self.time - self.time_before) * 1e-3
        self.processed_heading += self.processed_gyro[2] * (self.time - self.time_before) * 1e-3

        # 초기 시간이 0이 아닐 수 있다.
        if self.flag == 0:
            self.heading = 0
            self.processed_heading = 0
            self.flag = 1

        # 걸음이 발생할 때 마다
        if step_count - self.step_count_before != 0:
            self.heading_df.loc[step_count] = [self.time, np.rad2deg(self.heading),
                                               np.rad2deg(self.processed_heading),
                                               np.rad2deg(-self.rot_vec_orientation[0])]
            self.step_count_before = step_count
