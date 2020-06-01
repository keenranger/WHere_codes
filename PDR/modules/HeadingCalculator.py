#########Heading Calculation##################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class HeadingCalculator:
    def __init__(self):
        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.heading = 0  # raw gyro z를 적분한 heading
        self.processed_heading = 0  # rotaion M 을 거친 gyro z를 적분한 heading
        self.processed_gyro = [0, 0, 0]  # rotaion M 을 거친 gyro data
        self.time_before = 0
        self.time = 0
        self.heading_df = pd.DataFrame(columns=("time", "value"))  # heading을 저장하기 위한 DataFrame
        self.processed_heading_df = pd.DataFrame(columns=("time", "value"))
        self.rollpitch_df = pd.DataFrame(columns=("time", "roll", "pitch"))
        self.step_count = 0
        self.step_count_before = 0
        self.roll = 0
        self.pitch = 0
        self.roll_out = 0
        self.pitch_out = 0
        self.RotationX = np.zeros((3, 3))
        self.RotationY = np.zeros((3, 3))
        self.Ms2S = 10 ** -3
        self.Ns2S = 10 ** -9
        self.RtoD = 180 / np.pi
        self.DtoR = np.pi / 180
        self.flag = 0
        self.avg_value_roll = [] # Moving avg 를 위한 데이터 저장소
        self.avg_value_pitch = [] # Moving avg 를 위한 데이터 저장소

    def step(self, idx, row, step_count):  # row[0] : time ,row[1,2,3] = acc 3 axis, row[4,5,6] = gyro 3 axis
        self.time = row[0]
        self.step_count = step_count
        self.acc = [row[1], row[2], row[3]]
        self.gyro = [row[4], row[5], row[6]]

        self.cal_heading(self.acc, self.gyro)
        self.time_before = self.time

    def cal_heading(self, acc, gyro):  # Calculation heading
        self.tilting(acc)
        self.rollpitch_df.loc[len(self.rollpitch_df)] = [self.time, self.roll * self.RtoD, self.pitch * self.RtoD]
        self.processed_gyro = self.Rotation_m(self.roll, self.pitch, gyro)

        # 처리된 자이로 적분하면 heading이 나온다
        self.heading += gyro[2] * (self.time - self.time_before) * self.Ms2S
        self.processed_heading += self.processed_gyro[2] * (self.time - self.time_before) * self.Ms2S

        # 초기 시간이 0이 아닐 수 있다.
        if self.flag == 0:
            self.heading = 0
            self.processed_heading = 0
            self.processed_heading2 = 0
            self.flag = 1

        # 걸음이 발생할 때 마다
        if self.step_count - self.step_count_before != 0:
            self.heading_df.loc[self.step_count] = [self.time, self.heading * self.RtoD]
            self.processed_heading_df.loc[self.step_count] = [self.time, self.processed_heading * self.RtoD]
            self.step_count_before = self.step_count

    def tilting(self, acc):  # Calculation tilting
        self.roll = self.Moving_avg("roll", np.arctan(acc[0] / np.sqrt(acc[1] ** 2 + acc[2] ** 2)), 30)
        self.pitch = self.Moving_avg("pitch", np.arctan(acc[1] / np.sqrt(acc[0] ** 2 + acc[2] ** 2)), 30)

    def Rotation_m(self, roll, pitch, gyro):  # RotationMatrix
        self.RotationX = [[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]]
        self.RotationY = [[np.cos(roll), 0, -np.sin(roll)], [0, 1, 0], [np.sin(roll), 0, np.cos(roll)]]

        rotation_gyro = np.matmul(self.RotationY, np.matmul(self.RotationX, gyro))
        return rotation_gyro

    def Moving_avg(self, value_name, value, windowsize):
        if value_name == 'roll':
            self.avg_value_roll.append(value)
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
                    return sum(self.avg_value_pitch) / value_len

    def Heading_plot(self, file_name):
        plt.figure()
        plt.plot(self.heading_df['time'], self.heading_df['value'], c='blue')
        plt.plot(self.processed_heading_df['time'], self.processed_heading_df['value'], c='green')
        plt.xlabel('time')
        plt.ylabel('degree')

        plt.title(file_name)
