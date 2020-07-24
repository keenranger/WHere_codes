#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PDR.modules.CalcFunction import *


class HeadingCalculator:
    def __init__(self):
        self.step_before = np.array([np.NaN, np.NaN, np.NaN])
        self.heading_df = pd.DataFrame(
            columns=("time", "body", "nav", "rot", "game", "fusion"))

    def step(self, time, gyro, mag, rot_vec, game_rot_vec):
        # RotationVector를 이용한 Roll, Pitch 계산
        rotationMatrix = getRotationMatrixFromVector(rot_vec, 9)
        rot_vec_orientation = getOrientation(rotationMatrix)
        game_vec_orientation = getOrientation(
            getRotationMatrixFromVector(game_rot_vec, 9))

        processed_gyro = np.matmul(rotationMatrix, gyro)

        # 처리된 자이로 적분하면 heading이 나온다
        if not np.isnan(self.step_before[0]):
            heading = self.heading_df["body"].loc[len(self.heading_df)-1]
            processed_heading = self.heading_df["nav"].loc[len(
                self.heading_df)-1]
            heading += (self.step_before[1] + gyro[2]) * \
                (time - self.step_before[0]) * 1e-3 / 2
            processed_heading += (self.step_before[2] + processed_gyro[2]) * (
                time - self.step_before[0]) * 1e-3 / 2
            if processed_heading >= np.pi:
                processed_heading -= 2 * np.pi
        else:
            heading = 0
            processed_heading = 0

        self.step_before = [time, gyro[2], processed_gyro[2]]
        self.heading_df.loc[len(self.heading_df)] = [
            time, heading, processed_heading, -rot_vec_orientation[0], -game_vec_orientation[0], processed_heading]
