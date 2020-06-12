#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PDR.modules.QuaternionCalculator import *


class HeadingCalculator:
    def __init__(self):
        self.step_before = np.array([np.NaN, np.NaN, np.NaN])
        self.heading_df = pd.DataFrame(
            columns=("time", "body", "nav", "azimuth"))

    def step(self, time, gyro, rot_vec, game_rot_vec):
        # RotationVector를 이용한 Roll, Pitch 계산
        rotationMatrix = getRotationMatrixFromVector(game_rot_vec, 9)
        processed_gyro = np.matmul(rotationMatrix, gyro)
        rot_vec_orientation = getOrientation(rotationMatrix)

        # 처리된 자이로 적분하면 heading이 나온다
        if not np.isnan(self.step_before[0]):
            heading = self.heading_df["body"].loc[len(self.heading_df)-1]
            processed_heading = self.heading_df["nav"].loc[len(
                self.heading_df)-1]
            heading += (self.step_before[1] + gyro[2]) * \
                (time - self.step_before[0]) * 1e-3 / 2
            processed_heading += (self.step_before[2] + processed_gyro[2]) * (
                time - self.step_before[0]) * 1e-3 / 2
        else:
            heading = -rot_vec_orientation[0]
            processed_heading = -rot_vec_orientation[0]
        self.step_before = [time, gyro[2], processed_gyro[2]]

        self.heading_df.loc[len(self.heading_df)] = [
            time, heading, processed_heading, -rot_vec_orientation[0]]
