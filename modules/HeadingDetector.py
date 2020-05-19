#########Heading detect##################
import numpy as np
import pandas as pd


class HeadingDetector:
    def __init__(self):
        self.heading = 0
        self.time_before = 0
        self.time = 0
        self.heading_df = pd.DataFrame(columns=("time", "value"))
        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.cal_gyro = [0, 0, 0]
        self.step_count = 0
        self.step_count_before = 0
        self.rho = 0
        self.phi = 0
        self.RotationX = np.zeros((3, 3))
        self.RotationY = np.zeros((3, 3))
        self.Ms2S = 10 ** -3
        self.Ns2S = 10 ** -9
        self.RtoD = 180 / np.pi
        self.DtoR = np.pi / 180
        self.count = 0

    def step(self, idx, row, step_count):  # row[0] : time ,row[1,2,3] = acc 3 axis, row[4,5,6] = gyro 3 axis
        self.time = row[0]
        self.step_count = step_count
        self.acc = [row[1], row[2], row[3]]
        self.gyro = [row[4], row[5], row[6]]

        self.cal_heading(self.acc, self.gyro)
        self.time_before = self.time

    def cal_heading(self, acc, gyro):  # Calculation heading
        self.tilting(acc)
        self.rmatrix(self.rho, self.phi, gyro)
        # 처리된 자이로 적분하면 heading이 나온다
        self.heading += gyro[2] * (self.time - self.time_before) * self.Ns2S

        #초기 시간이 0이 아니기 때문에
        if self.count == 0:
            self.heading = 0
            self.count = 1

        if self.step_count - self.step_count_before != 0:
            self.heading_df.loc[self.step_count] = [self.time, self.heading * self.RtoD]
            self.step_count_before = self.step_count

    def tilting(self, acc):  # Calculation tilting
        self.rho = np.arctan(acc[0] / np.sqrt(acc[1] ** 2 + acc[2] ** 2))
        self.phi = np.arctan(acc[1] / np.sqrt(acc[0] ** 2 + acc[2] ** 2))

    def rmatrix(self, rho, phi, gyro):  # RotationMatrix
        self.RotationX = [[1, 0, 0], [0, np.cos(rho), np.sin(rho)], [0, -np.sin(rho), np.cos(rho)]]
        self.RotationY = [[np.cos(phi), 0, -np.sin(phi)], [0, 1, 0], [np.sin(phi), 0, np.cos(phi)]]
