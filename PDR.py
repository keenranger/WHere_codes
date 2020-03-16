# readline test
import numpy as np
import math
import matplotlib.pyplot as plt

f = open("C:/Users/changsoo/PDR_cs/Sensor_2020_03_12_09_21_26_L1.txt", 'r')
All = f.readlines()
num_row = len(All)  # epoch 개수
print('num_row : {0}'.format(num_row))
f.close()

################################################
Nan = np.nan
RtoD = 180 / math.pi
DtoR = math.pi / 180


sys_time = [0 for i in range(num_row)]  #시스템 시간 data
acc_data = np.zeros((num_row, 3))       #가속도 data
gyro_data = np.zeros((num_row, 3))      #자이로 data


norm = [0 for i in range(num_row)]      #가속도 norm data
smoothing_norm = [0 for i in range(num_row)] #norm smoothing data

findpeak = np.zeros((num_row-1,2))        #peak data
findpeak[0,0] = Nan                     #peak
findpeak[0,1] = Nan                     #valley

peak_count = [0 for i in range(num_row)]
valley_count = [0 for i in range(num_row)]

position = np.zeros((num_row, 2))
################################################

def cal_movmean(data, window_size):  # 이동평균함수
    data_len = len(data)
    for i in range(0, data_len):
        if i == 0:
            smoothing_norm[0] = norm[0]
        elif i < window_size:
            smoothing_norm[i] = np.mean(norm[0:i])
        else:
            smoothing_norm[i] = np.mean(norm[i-window_size : i])

    return smoothing_norm

################################################
for i in range(0, num_row):
    line = All[i]
    line = line.split('\t')

    sys_time[i] = line[0]
    acc_data[i, 0] = line[1]
    acc_data[i, 1] = line[2]
    acc_data[i, 2] = line[3]

    gyro_data[i, 0] = line[4]
    gyro_data[i, 1] = line[5]
    gyro_data[i, 2] = line[6]

    norm[i] = math.sqrt(math.pow(acc_data[i, 0], 2) + math.pow(acc_data[i, 1], 2) + math.pow(acc_data[i, 2], 2))

smoothing_norm = cal_movmean(norm,5)

d_norm = np.sign(np.diff(smoothing_norm)) #차분값이기 때문에 길이가 1 작음


upper_threshold = 10.8
lower_threshold = 8.5

windowisze = 20

######################################
#find peak
######################################
for i in range(1,num_row-1):
    if d_norm[i] == -1 and d_norm[i-1] == 1:
        if smoothing_norm[i] >= upper_threshold:
            findpeak[i,0] = smoothing_norm[i]
        else:
            findpeak[i,0] = Nan
    else:
        findpeak[i,0] = Nan

######################################
#find valley
######################################

for i in range(1,num_row-1):
    if d_norm[i] == 1 and d_norm[i-1] == -1:
        if smoothing_norm[i] <= lower_threshold:
            findpeak[i,1] = smoothing_norm[i]
        else:
            findpeak[i,1] = Nan
    else:
        findpeak[i,1] = Nan


for i in range(windowisze + 1 ,num_row-1):
    if ~np.isnan(findpeak[i,0]):
        for j in range(1,windowisze + 1):
            if  ~np.isnan(findpeak[i-j,0]) and findpeak[i-j,0] < findpeak[i,0] :
                findpeak[i-j,0] = Nan
            elif ~np.isnan(findpeak[i-j,0]) and findpeak[i-j,0] > findpeak[i,0]:
                findpeak[i,0] = Nan

    if ~np.isnan(findpeak[i, 1]):
        for j in range(1,windowisze + 1):
            if ~np.isnan(findpeak[i - j, 1]) and findpeak[i - j, 1] > findpeak[i, 1]:
                findpeak[i - j, 1] = Nan
            elif ~np.isnan(findpeak[i - j, 1]) and findpeak[i - j, 1] < findpeak[i, 1]:
                findpeak[i, 1] = Nan




for i in range(0,num_row-1):
    if ~np.isnan(findpeak[i,0]):
        peak_count[i] = 1

    else:
        peak_count[i] = 0
    if ~np.isnan(findpeak[i, 1]):
        valley_count[i] = 1

    else:
        valley_count[i] = 0

peak = peak_count.count(1)
valley = valley_count.count(1)


plt.figure(1)
plt.plot(norm)
plt.plot(smoothing_norm)
plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),0],c='red')
plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),1],c='green')


#########################################################Heading
dt = 0.01
z_angle = [0 for i in range(num_row)]

for i in range(1,num_row):
    z_angle[i] = z_angle[i-1] + gyro_data[i,2]*RtoD*dt
    # z_angle[i] = z_angle[i] % 360
plt.figure(2)
plt.plot(z_angle)

#############################################################
n = peak_count
L = 0.67
theta = z_angle

for i in range(1,num_row):
    position[i,0] = position[i-1,0] + n[i-1]*L*math.cos(theta[i-1] * DtoR)
    position[i,1] = position[i-1,1] + n[i-1]*L*math.sin(theta[i-1] * DtoR)


plt.figure(3)
plt.plot(position[range(0,num_row),0],position[range(0,num_row),1])


# print(acc_data[:, 0])
print("peak counting : {0}".format(peak))
print("valley counting : {0}".format(valley))


plt.show()