import numpy as np
import sqlite3 as sql
import pandas as pd
import matplotlib.pyplot as plt
import sys


class MapGym:
    def __init__(self, action_size):
        super().__init__()
        self.map = pd.read_csv("./Map/data/map.csv", header=None).to_numpy()
        self.height = self.map.shape[0]  # 높이
        self.width = self.map.shape[1]  # 넓이
        self.action_size = action_size
        self.action_length = 40  # 4미터
        self.available_seed = np.where(self.map != -100)
        seed_order = np.random.choice(
            np.arange(self.available_seed[0].shape[0]))
        self.state = [self.available_seed[0][seed_order],
                      self.available_seed[1][seed_order]]

    def step(self, action):
        reward = 0.0
        done = False
        for _ in np.arange(2+np.random.randint(7)):  # 2번~8번 동안 = 1미터 4미터 = 평균 2.5미터
            if self.action_size == 4:
                if action == 0:
                    self.state[0] += 1
                elif action == 1:
                    self.state[1] += 1
                elif action == 2:
                    self.state[0] -= 1
                elif action == 3:
                    self.state[1] -= 1
                else:
                    print("invalid action")
                    sys.exit()
            if (0 <= self.state[0] < self.height) and (0 <= self.state[1] < self.width):  # 범위 안에 있고
                if self.map[self.state[0]][self.state[1]] > -100:  # lte가 있는곳이면
                    reward += 0.2  # reward에 0.2추가
                else:
                    reward -= 3
                    done = True
                    break
            else:
                reward -= 10
                done = True
                break
        return round(reward,1), self.state, done

    def reset(self):
        seed_order = np.random.choice(
            np.arange(self.available_seed[0].shape[0]))
        self.state = [self.available_seed[0][seed_order],
                      self.available_seed[1][seed_order]]
        return self.state  # [h,w]로 return


gym = MapGym(4)
state = gym.state
print("시작 위치 : " + str(state))
while True:
    old_state = state.copy()
    action = np.random.randint(4)
    reward, state, done = gym.step(action)
    print(old_state, action, reward, state, done, gym.map[state[0]][state[1]])
    plt.scatter(gym.available_seed[1], gym.available_seed[0])
    plt.scatter(state[1], state[0], c='r')
    plt.axis('equal')
    plt.show()
    if done:
        break
