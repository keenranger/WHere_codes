import numpy as np
import pandas as pd

class Walker:
    def __init__(self, initial_heading = 0, step_length = 70):
        self.initial_heading = initial_heading
        self.step_length = step_length
        self.angle_gyro = pd.DataFrame(columns=("time", "value_x", "value_y", "value_z"))
        self.angle_gyro_init = [0, 0, 0]
        self.time_before = 0
        self.Ms2S = 0.001

    def step(self, index, time, row, df1, df2):
        self.time = time
        self.gyrox = row[0]
        self.gyroy = row[1]
        self.gyroz = row[2]
        self.CalAngle()
        self.time_before = self.time

    def CalAngle(self):
        self.angle_gyro_init[0] += self.gyrox * (self.time - self.time_before) * self.Ms2S
        self.angle_gyro_init[1] += self.gyrox * (self.time - self.time_before) * self.Ms2S
        self.angle_gyro_init[2] += self.gyrox * (self.time - self.time_before) * self.Ms2S
        self.angle_gyro.loc[len(self.angle_gyro)] = [self.time,
                                                     np.rad2deg(self.angle_gyro_init[0]),
                                                     np.rad2deg(self.angle_gyro_init[1]),
                                                     np.rad2deg(self.angle_gyro_init[2])]



