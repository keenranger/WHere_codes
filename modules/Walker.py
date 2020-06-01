import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Walker:
    def __init__(self, step_length=0.65):
        self.step_length = step_length
        self.step_count = 0
        self.pre_step_count = 0
        self.pdr_df = pd.DataFrame(columns=('pos_x', 'pos_y'))
        self.pos_xy = [0, 0]

    def step(self, step_count, heading):
        self.PDR(step_count, heading)

    def PDR(self, step_count, heading):
        if step_count == 0: #초기 걸음이 발생되지 않았을때 좌표 (0,0)
            self.pdr_df.loc[step_count] = [self.pos_xy[0], self.pos_xy[1]]
        else:
            if step_count - self.pre_step_count != 0:
                self.pos_xy[0] += np.cos(heading) * self.step_length
                self.pos_xy[1] += np.sin(heading) * self.step_length
                self.pdr_df.loc[step_count] = [self.pos_xy[0], self.pos_xy[1]]
                self.pre_step_count = step_count

    def PDR_plot(self, file_name):
        plt.plot(self.pdr_df['pos_x'], self.pdr_df['pos_y'],marker='*')
        plt.xlabel('m')
        plt.ylabel('m')
        plt.axis('equal')
        # plt.xlim(-15, 55)
        # plt.ylim(-15, 55)

        plt.title(file_name)
