
# readline test
import numpy as np
import math
import matplotlib.pyplot as plt
import sqlite3 as sql

################################################
Nan = np.nan
RtoD = 180 / math.pi
DtoR = math.pi / 180
################################################


################################################
#텍스트 파일 읽어오기
################################################
conn = sql.connect('./0344/database-name.db')
c= conn.cursor()


print("Data parsing... ")
row_list = np.zeros((1, 16))
for row in c.execute('SELECT time, accx, accy, accz, linaccx,linaccy, linaccz, gyrox, gyroy, gyroz, magx, magy, magz, yaw, pitch, roll FROM sensordata WHERE filename = "e1" ORDER BY time  '):
    row_list = np.append(row_list, np.asarray(row).reshape((1, 16)), axis=0)

row_list = row_list[1:, :]
num_row = len(row_list)

print("Data parsing finished!")
print("data size : {0}".format(num_row) )

sys_time = row_list[:,0]  #시스템 시간 data
acc_data = row_list[:,1:4]       #acc data
lin_acc_data = row_list[:,4:7]       #Linear acc data
gyro_data = row_list[:,7:10]     #gyro data
mag_data = row_list[:,10:13]      #Mag data
ori_data = row_list[:,13:16]     #ori data

norm = [0 for i in range(num_row)]      #가속도 norm data
smoothing_norm = [0 for i in range(num_row)] #norm smoothing data

findpeak = np.zeros((num_row-1,2))        #peak data(findpeak[i,0] = peak, findpeak[i,1] = valley
findpeak[0,0] = Nan
findpeak[0,1] = Nan

peaktime = np.zeros((num_row-1,2))       #peak가 발생된 시간 check (peaktime[i,0] = peak 가 발생된 시간, peaktime[i,1] = valley 가 발생된 시간
peakvalley = [0 for i in range(num_row)]  #peak - valley 순서 확인용

step_detect = np.zeros((num_row-1,2))    #step detection 알고리즘을 모두 거친 후 찾은 peak data 저장
step_count = [0 for i in range(num_row)] #step counting
peak_count = [0 for i in range(num_row)] #peak_counting
valley_count = [0 for i in range(num_row)] #valley counting

position = np.zeros((num_row, 2))
################################################

def cal_norm(data):  #norm 구하기
    for i in range(0,len(data)):
        norm[i] = math.sqrt(math.pow(data[i, 0], 2) + math.pow(data[i, 1], 2) + math.pow(data[i, 2], 2))

    return norm

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

norm = cal_norm(acc_data)
smoothing_norm = cal_movmean(norm,10)
d_norm = np.sign(np.diff(smoothing_norm)) #차분값이기 때문에 길이가 1 작음


upper_threshold = 10.35 #peak threshold
lower_threshold = 9.1   #valley threshold


for i in range(0,num_row):
    gyro_data[i,0] = gyro_data[i,0]* RtoD
    gyro_data[i,1] = gyro_data[i,1]* RtoD
    gyro_data[i,2] = gyro_data[i,2]* RtoD

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
plt.plot(norm)

# plt.figure(2)
# plt.plot(gyro_data[:,1],c = 'red')
#
# plt.figure(3)
# plt.plot(gyro_data[:,2],c = 'green')



# plt.plot(peaktime[:,0],c = 'blue')
# plt.plot(peaktime[:,1],c = 'red')

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

# plt.figure(2)
# # plt.plot(norm)
# plt.plot(smoothing_norm)
# plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),0],c='red')
# plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),1],c='green')
######################################
#peak - valley 를 기준으로 step count (peak 다음에는 valley 가 나와야한다)
#추가적인 고민 필요 
######################################
# for i in range(0,num_row - 1) :
    # step_detect[i,0] = Nan
    # step_detect[i,1] = Nan

for i in range(1,num_row-1) :
    if peakvalley[i] == -1: #valley 를 먼저 찾고
        for j in range(1,i+1): #이전 값들 중에
            if peakvalley[i-j] == 1: #peak 를 발견하면
                # step_detect[i-j,0] = findpeak[i-j,0] #step_detect 에 그 때의 peak 값을 저장
                break
            elif peakvalley[i-j] == -1: #valley 가 발견되면 두 개 비교 후 업데이트 break
                if findpeak[i-j,1] > findpeak[i,1] :
                    findpeak[i-j,1] = Nan
                else :  findpeak[i,1] = Nan
                break

for i in range(1,num_row-1) :
    if peakvalley[i] == 1: #peak 를 먼저 찾고
        for j in range(1,i+1): #이전 값들 중에
            if peakvalley[i-j] == -1: #valley 를 발견하면
                # step_detect[i-j,1] = findpeak[i-j,1] #step_detect 에 그 때의 valley 값을 저장
                break
            elif peakvalley[i-j] == 1: #peak 가 발견되면 두 개 비교 후 업데이트 break
                if findpeak[i-j,0] < findpeak[i,0] :
                    findpeak[i-j,0] = Nan
                else :  findpeak[i,0] = Nan
                break




######################################
######################################
# plt.figure(3)
# plt.plot(smoothing_norm)
# plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),0],c='red')
# plt.scatter(range(0,num_row-1),findpeak[range(0,num_row-1),1],c='green')
# plt.scatter(range(0,num_row-1),step_detect[range(0,num_row-1),0],c='yellow')


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

    # if ~np.isnan(step_detect[i, 0]):
    #     step_count[i] = 1
    #
    # else:
    #     step_count[i] = 0

# step = step_count.count(1)
peak = peak_count.count(1)
valley = valley_count.count(1)

# print(acc_data[:, 0])
# print("step counting : {0}".format(step))
print("peak counting : {0}".format(peak))
print("valley counting : {0}".format(valley))



#########################################################
# Heading
#########################################################

dt = 0.01
z_angle = [0 for i in range(num_row)]
z_angle_2 = [0 for i in range(num_row)]
for i in range(1,num_row):
    z_angle[i] = z_angle[i-1] + gyro_data[i,2]*dt
    z_angle_2[i]  = z_angle_2[i - 1] + ((gyro_data[i, 2] + gyro_data[i - 1, 2])/2 * dt )


# plt.figure(4)
# plt.plot(z_angle)
# plt.plot(z_angle_2)

#############################################################
n = peak_count
L = 0.67
theta = z_angle

for i in range(1,num_row):
    position[i,0] = position[i-1,0] + n[i-1]*L*math.cos(theta[i-1] * DtoR)
    position[i,1] = position[i-1,1] + n[i-1]*L*math.sin(theta[i-1] * DtoR)


# plt.figure(5)
# plt.plot(position[range(0,num_row),0],position[range(0,num_row),1])
plt.show()

