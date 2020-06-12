#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PDR.modules.QuaternionCalculator import *


class HeadingCalculator:
    def __init__(self):
        self.heading = 0  # raw gyro z를 적분한 heading
        self.processed_heading = 0  # rotaion M 을 거친 gyro z를 적분한 heading
        self.step_before = [np.NaN, np.Nan, np.Nan]
        # heading을 저장하기 위한 DataFrame
        self.heading_df = pd.DataFrame(
            columns=("time", "body", "nav", "azimuth"))
        self.step_count_before = 0

    def step(self, time, gyro, rot_vec, game_rot_vec, step_count):
        # RotationVector를 이용한 Roll, Pitch 계산
        rotationMatrix = getRotationMatrixFromVector(game_rot_vec, 16)
        processed_gyro = np.matmul(rotationMatrix, gyro)
        rot_vec_orientation = getOrientation(rotationMatrix)

        # 처리된 자이로 적분하면 heading이 나온다
        if not np.isnan(self.step_before[0]):
            self.heading += (self.step_count_before[1] + gyro[2]) * (
                time - self.step_before[0]) * 1e-3 / 2
            self.processed_heading += (self.step_before[2] + processed_gyro[2]) * (
                time - self.step_before[0]) * 1e-3 / 2

        # 걸음이 발생할 때 마다
        if step_count - self.step_count_before != 0:
            self.heading_df.loc[step_count] = [time, np.rad2deg(self.heading),
                                               np.rad2deg(
                                                   self.processed_heading),
                                               np.rad2deg(-rot_vec_orientation[0])]
            self.step_count_before = step_count

        self.step_before = [time, gyro[2], processed_gyro[2]]
