
# readline test
import numpy as np
import math
import matplotlib.pyplot as plt


################################################
#텍스트 파일 읽어오기
################################################
f = open("C:/Users/changsoo/PDR_test/Sensor_2020_03_11_01_51_47_50s.txt", 'r')
All = f.readlines()
num_row = len(All)  # epoch 개수
print('num_row : {0}'.format(num_row))
f.close()

################################################
Nan = np.nan
RtoD = 180 / math.pi
DtoR = math.pi / 180
################################################

sys_time = [0 for i in range(num_row)]  #시스템 시간 data
acc_data = np.zeros((num_row, 3))       #가속도 data
gyro_data = np.zeros((num_row, 3))      #자이로 data


norm = [0 for i in range(num_row)]      #가속도 norm data
smoothing_norm = [0 for i in range(num_row)] #norm smoothing data

findpeak = np.zeros((num_row-1,2))        #peak data(findpeak[i,0] = peak, findpeak[i,1] = valley
findpeak[0,0] = Nan
findpeak[0,1] = Nan

peaktime = np.zeros((num_row-1,2))       #peak가 발생된 시간 check (peaktime[i,0] = peak 가 발생된 시간, peaktime[i,1] = valley 가 발생된 시간
peakvalley = [0 for i in range(num_row)]  #peak - valley 순서 확인용


step_detect = np.zeros((num_row-1,1))    #step detection 알고리즘을 모두 거친 후 찾은 peak data 저장

step_count = [0 for i in range(num_row)] #step counting
peak_count = [0 for i in range(num_row)] #peak_counting
valley_count = [0 for i in range(num_row)] #valley counting

position = np.zeros((num_row, 2))
################################################

def cal_movmean(data, window_size):  # 이동평균함수 #수정 3/16  np.nean(norm[]) 부분 인덱스
    data_len = len(data)
    for i in range(0, data_len):
        if i == 0:
            smoothing_norm[0] = norm[0]
        elif i < window_size:
            smoothing_norm[i] = np.mean(norm[0:i+1])
        else:
            smoothing_norm[i] = np.mean(norm[i-window_size : i+1])

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

smoothing_norm = cal_movmean(norm,10)

d_norm = np.sign(np.diff(smoothing_norm)) #차분값이기 때문에 길이가 1 작음


upper_threshold = 10.35 #peak threshold
lower_threshold = 9.1   #valley threshold


######################################
#센서데이터 로깅 100Hz

#걸음 검출 알고리즘 조건
# 1. peak > peak_threshold & valley < valley_threshold
# 2. 현재 peak(valley) 시간 - 이전 peak(valley) 시간 이 time_threshold(0.25s)보다 작으면 비교 후 값이 큰(작은) peak(valley) 로 업데이트
# 3. peak 다음에는 valley 가 온다
######################################



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

######################################
#peak 간 시간 차이
######################################
time_threshold = 25
for i in range(1,num_row-1) :
    if ~np.isnan(findpeak[i,1]):
        for j in range(1,i+1):
            if ~np.isnan(findpeak[i-j,1]):
                if j > time_threshold or j == 0 :
                    peaktime[i,0] = j
                else :
                    peaktime[i,1] = j
                break


plt.figure(1)
plt.plot(peaktime[:,0],c = 'blue')
plt.plot(peaktime[:,1],c = 'red')

print("peaktime_fake_max = {0}".format(np.max(peaktime[:,1])))

######################################
#peak 간 시간 차이를 이용하여 update
######################################
windowisze = 25 #(= time_threshold)

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

######################################
#peak = 1, valley = -1
######################################
for i in range(0,num_row - 1) :
    if ~np.isnan(findpeak[i,0]) :
        peakvalley[i] = 1
    if ~np.isnan(findpeak[i,1]) :
        peakvalley[i] = -1


######################################
#peak - valley 를 기준으로 step count (peak 다음에는 valley 가 나와야한다)

######################################
for i in range(0,num_row - 1) :
    step_detect[i,0] = Nan

for i in range(1,num_row-1) :
    if peakvalley[i] == -1: #valley 를 먼저 찾고
        for j in range(1,i+1): #이전 값들 중에
            if peakvalley[i-j] == 1: #peak 를 발견하면
                step_detect[i-j,0] = findpeak[i-j,0] #step_detect 에 그 때의 peak 값을 저장
                break
            elif peakvalley[i-j] == -1: #valley 가 발견되면 break
                break

######################################
######################################
plt.figure(2)
# plt.plot(norm)
plt.plot(smoothing_norm)
plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),0],c='red')
plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),1],c='green')
plt.scatter(range(0,num_row-1),step_detect[range(0,num_row-1),0],c='yellow')


######################################
#peak,valley,step counting
######################################
for i in range(0,num_row-1):
    if ~np.isnan(findpeak[i,0]):
        peak_count[i] = 1

    else:
        peak_count[i] = 0
    if ~np.isnan(findpeak[i, 1]):
        valley_count[i] = 1

    else:
        valley_count[i] = 0

    if ~np.isnan(step_detect[i, 0]):
        step_count[i] = 1

    else:
        step_count[i] = 0

step = step_count.count(1)
peak = peak_count.count(1)
valley = valley_count.count(1)

# print(acc_data[:, 0])
print("step counting : {0}".format(step))
print("peak counting : {0}".format(peak))
print("valley counting : {0}".format(valley))



#########################################################
# Heading
#########################################################

dt = 0.01
z_angle = [0 for i in range(num_row)]

for i in range(1,num_row):
    z_angle[i] = z_angle[i-1] + gyro_data[i,2]*RtoD*dt


# plt.figure(2)
# plt.plot(z_angle)

#############################################################
n = peak_count
L = 0.67
theta = z_angle

for i in range(1,num_row):
    position[i,0] = position[i-1,0] + n[i-1]*L*math.cos(theta[i-1] * DtoR)
    position[i,1] = position[i-1,1] + n[i-1]*L*math.sin(theta[i-1] * DtoR)


# plt.figure(3)
# plt.plot(position[range(0,num_row),0],position[range(0,num_row),1])


plt.show()