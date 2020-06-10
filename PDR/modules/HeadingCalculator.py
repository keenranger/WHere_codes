#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PDR.modules import getOrientationFromVector as gOFV


class HeadingCalculator:
    def __init__(self):
        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0, 1]
        self.mag = [0, 0, 0, 1]
        self.heading = 0  # raw gyro z를 적분한 heading
        self.processed_heading = 0  # rotaion M 을 거친 gyro z를 적분한 heading

        self.processed_gyro = [0, 0, 0, 1]  # rotaion M 을 거친 gyro data
        self.processed_mag = [0, 0, 0, 1]
        self.rotvec_ypr = [0,0,0]
        self.time_before = 0
        self.time = 0
        self.heading_df = pd.DataFrame(columns=("time", "value"))  # heading을 저장하기 위한 DataFrame
        self.processed_heading_df = pd.DataFrame(columns=("time", "value"))
        self.rotvec_heading_df = pd.DataFrame(columns=("time", "value"))

        self.rollpitch_df = pd.DataFrame(columns=("time", "roll", "pitch", "azimuth"))
        self.processed_mag_df = pd.DataFrame(columns=("time", "magx", "magy", "magz"))
        self.step_count = 0
        self.step_count_before = 0
        self.RotationX = np.zeros((3, 3))
        self.RotationY = np.zeros((3, 3))
        self.Ms2S = 10 ** -3
        self.Ns2S = 10 ** -9
        self.RtoD = 180 / np.pi
        self.DtoR = np.pi / 180
        self.flag = 0
        self.windowsize = 20
        self.avg_value_roll = []  # Moving avg 를 위한 데이터 저장소
        self.avg_value_pitch = []  # Moving avg 를 위한 데이터 저장소
        self.pre_avg_roll = 0
        self.pre_avg_pitch = 0
        self.index_count = 1

    # row[0] : time ,row[1,2,3] = acc 3 axis, row[4,5,6] = gyro 3 axis
    # row[7,8,9] = mag 3 axis
    def step(self, idx, row, step_count):
        self.time = row[0]
        self.step_count = step_count
        self.acc = [row[1], row[2], row[3]]
        self.gyro = [row[4], row[5], row[6], 1]
        self.mag = [row[7], row[8], row[9], 1]
        self.rotvec = np.array([row[10], row[11], row[12], row[13]])
        self.game_rotvec = np.array([row[15], row[16], row[17], row[18]])

        self.cal_heading(self.acc, self.gyro)

        ## averaging F 를 위한 counter
        if self.index_count < self.windowsize:
            self.index_count += 1
        else:
            self.index_count = 100

        self.time_before = self.time

    def cal_heading(self, acc, gyro):  # Calculation heading
        # self.tilting(acc)
        # RotationVector를 이용한 Roll, Pitch 계산
        # self.rollpitch_df.loc[len(self.rollpitch_df)] = [self.time, self.ypr[2], self.ypr[1], self.ypr[0]]
        self.processed_gyro = np.matmul(gOFV.getRotationMatrixFromVector(self.game_rotvec), self.gyro)
        self.rotvec_ypr = gOFV.getOrientation(gOFV.getRotationMatrixFromVector(self.game_rotvec))

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

    def tilting(self, acc):  # Calculation tilting
        self.ypr[2] = self.Averaging_F("roll", -np.arctan(acc[0] / np.sqrt(acc[1] ** 2 + acc[2] ** 2)), self.windowsize)
        self.ypr[1] = self.Averaging_F("pitch", np.arctan(acc[1] / np.sqrt(acc[0] ** 2 + acc[2] ** 2)), self.windowsize)

        pass

    def Rotation_m(self, roll, pitch, data):  # RotationMatrix
        self.RotationX = [[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]]
        self.RotationY = [[np.cos(roll), 0, np.sin(roll)], [0, 1, 0], [-np.sin(roll), 0, np.cos(roll)]]

        rotation_data = np.matmul(self.RotationY, data)
        rotation_data = np.matmul(self.RotationX, rotation_data)
        return rotation_data

    def Moving_avg_F(self, value_name, value, windowsize):
        if value_name == 'roll':
            value_len = len(self.avg_value_roll)
            if value_len != 0:
                if value_len <= windowsize:
                    return sum(self.avg_value_roll) / value_len
                else:
                    self.avg_value_roll = self.avg_value_roll[1:]
                    return sum(self.avg_value_roll) / windowsize

        if value_name == 'pitch':
            self.avg_value_pitch.append(value)
            value_len = len(self.avg_value_pitch)
            if value_len != 0:
                if value_len <= windowsize:
                    return sum(self.avg_value_pitch) / value_len

                else:
                    self.avg_value_pitch = self.avg_value_pitch[1:]
                    return sum(self.avg_value_pitch) / windowsize

    def Averaging_F(self, data_name, data, windowsize):
        if data_name == "roll":
            if self.index_count == 1:
                self.pre_avg_roll = data
                return data
            elif self.index_count < windowsize:
                avg_data = self.pre_avg_roll * (self.index_count - 1) / self.index_count + data / self.index_count
                self.pre_avg_roll = avg_data
                return avg_data
            else:
                avg_data = self.pre_avg_roll * (self.windowsize - 1) / self.windowsize + data / self.windowsize
                self.pre_avg_roll = avg_data
                return avg_data

        if data_name == "pitch":
            if self.index_count == 1:
                self.pre_avg_pitch = data
                return data
            elif self.index_count < windowsize:
                avg_data = self.pre_avg_pitch * (self.index_count - 1) / self.index_count + data / self.index_count
                self.pre_avg_pitch = avg_data
                return avg_data
            else:
                avg_data = self.pre_avg_pitch * (windowsize - 1) / windowsize + data / windowsize
                self.pre_avg_pitch = avg_data
                return avg_data

    def Heading_plot(self, file_name):
        plt.figure()
        plt.plot(self.heading_df['time'], self.heading_df['value'], c='blue',label='only_gyro')
        plt.plot(self.processed_heading_df['time'], self.processed_heading_df['value'], c='green', label='rotM_gyro')
        plt.plot(self.rotvec_heading_df['time'], self.rotvec_heading_df['value'], c='orange',label='rotM_azimuth')
        plt.xlabel('time')
        plt.ylabel('degree')

        plt.title(file_name)
