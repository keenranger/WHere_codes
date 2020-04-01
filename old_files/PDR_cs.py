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
print("Data parsing... ")

################################################
# 텍스트 파일 읽어오기
################################################
conn = sql.connect('./0331/database-name.db')
c = conn.cursor()

row_list = np.zeros((1, 16))
for row in c.execute(
        'SELECT time, accx, accy, accz, linaccx,linaccy, linaccz, gyrox, gyroy, gyroz, magx, magy, magz, yaw, pitch, roll FROM sensordata WHERE filename = "0331t4" ORDER BY time  '):
    row_list = np.append(row_list, np.asarray(row).reshape((1, 16)), axis=0)

row_list = row_list[500:, :]

print("Data parsing finished!")

sys_time = row_list[:, 0]  # 시스템 시간 data
acc_data = row_list[:, 1:4]  # acc data
lin_acc_data = row_list[:, 4:7]  # Linear acc data
gyro_data = row_list[:, 7:10]  # gyro data
mag_data = row_list[:, 10:13]  # Mag data
ori_data = row_list[:, 13:16]  # ori data

plt.figure(1)
plt.plot(gyro_data[:,0], c='blue')
plt.plot(gyro_data[:,1], c='green')
plt.plot(gyro_data[:,2], c='orange')


################################################

def cal_norm(data):  # norm 구하기
    norm = [0 for i in range(len(data))]
    for i in range(0, len(data)):
        norm[i] = math.sqrt(math.pow(data[i, 0], 2) + math.pow(data[i, 1], 2) + math.pow(data[i, 2], 2))
    return norm


def cal_movmean(data, window_size):  # 이동평균함수 #수정 3/16  np.nean(norm[]) 부분 인덱스
    data_len = len(data)
    smoothing_data = [0 for i in range(data_len)]
    for i in range(0, data_len):
        if i == 0:
            smoothing_data[0] = data[0]
        elif i < window_size:
            smoothing_data[i] = np.mean(data[0:i + 1])
        else:
            smoothing_data[i] = np.mean(data[i - window_size: i + 1])

    return smoothing_data


def peakcounting():  # peak,valley,step counting
    for i in range(0, num_row - 1):
        if ~np.isnan(findpeak[i, 0]):
            peak_count[i] = 1

        else:
            peak_count[i] = 0
        if ~np.isnan(findpeak[i, 1]):
            valley_count[i] = 1

        else:
            valley_count[i] = 0

    peak = peak_count.count(1)
    valley = valley_count.count(1)

    print("peak counting : {0}".format(peak))
    print("valley counting : {0}".format(valley))


def calBias(data, size):
    bias = [0,0,0]
    bias[0] = np.mean(data[0:size,0])
    bias[1] = np.mean(data[0:size,1])
    bias[2] = np.mean(data[0:size,2])

    return bias

#rotation Matrix
def rotation(roll, pitch, gyro_data):
    xyz = np.asarray(gyro_data).reshape((3,1))
    roll = roll * DtoR
    rotation_roll = [[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]]

    pitch = pitch * DtoR
    rotation_pitch = [[math.cos(pitch), 0, math.sin(pitch)], [0, 1, 0], [-math.sin(pitch), 0, math.cos(pitch)]]

    xyz = np.dot(rotation_roll,xyz)
    xyz = np.dot(rotation_pitch,xyz)

    return xyz[2,0]
################################################
bias_size = 2000  #Bias 계산 끝 지점 설정
startpoint =4400  #PDR 시작 지점 설정

#bias_size 만큼 계산
gyro_bias = calBias(gyro_data, bias_size) #자이로, 가속도센서 Bias 계산 후 저장
acc_bias = calBias(acc_data,bias_size)


#시작지점부터 데이터 자르기
sys_time = row_list[startpoint:, 0]  #시스템 시간 data
acc_data = row_list[startpoint:, 1:4]  # cc data
lin_acc_data = row_list[startpoint:, 4:7]  #Linear acc data
gyro_data = row_list[startpoint:, 7:10]  #gyro data
mag_data = row_list[startpoint:, 10:13]  #Mag data
ori_data = row_list[startpoint:, 13:16]  #ori data    #[0] yaw [1] pitch 인데 자이로센서 x축 방향 기울어짐(센서 기준 roll, 방향도 반대)  [2] roll 인데 (센서기준 pitch)


#시작지점 부터 Bias 가 제거된 data
gyro_data[:, 0] = gyro_data[:, 0] - gyro_bias[0]
gyro_data[:, 1] = gyro_data[:, 1] - gyro_bias[1]
gyro_data[:, 2] = gyro_data[:, 2] - gyro_bias[2]

acc_data[:, 0] = acc_data[:, 0] - acc_bias[0]
acc_data[:, 1] = acc_data[:, 1] - acc_bias[1]

num_row = len(sys_time)

acc_norm = [0 for i in range(num_row)]  # 가속도 norm data
smoothing_norm = [0 for i in range(num_row)]  # norm smoothing data
findpeak = np.zeros((num_row - 1, 2))  # peak data(findpeak[i,0] = peak, findpeak[i,1] = valley
findpeak[0, 0] = Nan #peak 위치 저장
findpeak[0, 1] = Nan #valley 위치 저장
peaktime = np.zeros((num_row - 1, 2))  # peak가 발생된 시간 check (peaktime[i,0] = peak 가 발생된 시간, peaktime[i,1] = valley 가 발생된 시간
peakvalley = [0 for i in range(num_row)]  # peak - valley 순서 확인용
step_detect = np.zeros((num_row - 1, 2))  # step detection 알고리즘을 모두 거친 후 찾은 peak data 저장
euler_angle = np.zeros((num_row , 2))
step_count = [0 for i in range(num_row)]  # step counting
peak_count = [0 for i in range(num_row)]  # peak_counting
valley_count = [0 for i in range(num_row)]  # valley counting

position = np.zeros((num_row, 2)) #위치 좌표 저장

upper_threshold = 11  # peak threshold
lower_threshold = 8.5  # valley threshold

acc_norm = cal_norm(acc_data)
smoothing_norm = acc_norm #스무딩 사용하지 x
# smoothing_norm = cal_movmean(norm, 10)
d_norm = np.sign(np.diff(smoothing_norm))  # 차분값이기 때문에 길이가 1 작음

for i in range(0, num_row):
    gyro_data[i, 0] = gyro_data[i, 0] * RtoD
    gyro_data[i, 1] = gyro_data[i, 1] * RtoD
    gyro_data[i, 2] = gyro_data[i, 2] * RtoD
    ori_data[i, 0] = -(ori_data[i, 0]) * RtoD
    ori_data[i, 1] = -(ori_data[i, 1]) * RtoD
    ori_data[i, 2] = (ori_data[i, 2]) * RtoD

######################################
# 센서데이터 로깅 100Hz

# 걸음 검출 알고리즘 조건
# 1. peak > peak_threshold & valley < valley_threshold
# 2. 현재 peak(valley) 시간 - 이전 peak(valley) 시간 이 time_threshold보다 작으면 비교 후 값이 큰(작은) peak(valley) 로 업데이트
# -> time_threshold 는 현재 짧은 보폭의 peak 간 주기 보다 약간 짧은 30ms 로 설정
# 3. peak 다음에는 valley 가 온다
######################################

######################################
# find peak
######################################
for i in range(1, num_row - 1):
    if smoothing_norm[i] >= upper_threshold:
        if (d_norm[i] == -1 and d_norm[i - 1] == 1) or (d_norm[i] == 0 and d_norm[i - 1] == 1) or (
                d_norm[i] == -1 and d_norm[i - 1] == 0):
            findpeak[i, 0] = smoothing_norm[i]
        else:
            findpeak[i, 0] = Nan
    else:
        findpeak[i, 0] = Nan

######################################
# find valley
######################################

for i in range(1, num_row - 1):
    if smoothing_norm[i] <= lower_threshold:
        if (d_norm[i] == 1 and d_norm[i - 1] == -1) or (d_norm[i] == 0 and d_norm[i - 1] == -1) or (
                d_norm[i] == 1 and d_norm[i - 1] == 0):
            findpeak[i, 1] = smoothing_norm[i]
        else:
            findpeak[i, 1] = Nan
    else:
        findpeak[i, 1] = Nan
print("---------------------------------")
print("걸음검출 조건 1")
peakcounting()
print("---------------------------------")

######################################
# peak 간 시간 차이
######################################
time_threshold = 20
for i in range(1, num_row - 1):
    if ~np.isnan(findpeak[i, 0]):
        for j in range(1, i + 1):
            if ~np.isnan(findpeak[i - j, 0]):
                peaktime[i, 0] = j
                # if j > time_threshold:
                #     peaktime[i,0] = j
                # else :
                #     peaktime[i,1] = j
                break
            else:
                peaktime[i, 0] = 0

######################################
# valley 간 시간 차이
######################################
for i in range(1, num_row - 1):
    if ~np.isnan(findpeak[i, 1]):
        for j in range(1, i + 1):
            if ~np.isnan(findpeak[i - j, 1]):
                peaktime[i, 1] = j
                # if j > time_threshold:
                #     peaktime[i,0] = j
                # else :
                #     peaktime[i,1] = j
                break
            else:
                peaktime[i, 1] = 0


peaktime_sum, valleytime_sum = 0, 0
peaktime_count, valleytime_count = 0, 0
for i in range(len(peaktime)):
    if peaktime[i, 0] != 0 and peaktime[i, 0] <= 500:

        peaktime_sum = peaktime_sum + peaktime[i, 0]
        peaktime_count = peaktime_count + 1
    if peaktime[i, 1] != 0 and peaktime[i, 1] <= 500:
        valleytime_sum = valleytime_sum + peaktime[i, 1]
        valleytime_count = valleytime_count + 1

if peaktime_count != 0:
    peaktime_mean = peaktime_sum / peaktime_count
    valley_mean = valleytime_sum / valleytime_count


######################################
# peak 간 시간 차이를 이용하여 update
######################################
windowisze = time_threshold  # (= time_threshold)

for i in range(windowisze + 1, num_row - 1):
    if ~np.isnan(findpeak[i, 0]):
        for j in range(1, i + 1):
            if ~np.isnan(findpeak[i - j, 0]):
                if j < time_threshold:
                    if findpeak[i - j, 0] < findpeak[i, 0]:
                        findpeak[i - j, 0] = Nan
                    else:
                        findpeak[i, 0] = Nan
                break

    if ~np.isnan(findpeak[i, 1]):
        for j in range(1, i + 1):
            if ~np.isnan(findpeak[i - j, 1]):
                if j < time_threshold:
                    if findpeak[i - j, 1] > findpeak[i, 1]:
                        findpeak[i - j, 1] = Nan
                    else:
                        findpeak[i, 1] = Nan
                break

print("---------------------------------")
print("걸음검출 조건 2")
peakcounting()
print("---------------------------------")

######################################
# peak = 1, valley = -1
######################################
for i in range(0, num_row - 1):
    if ~np.isnan(findpeak[i, 0]):
        peakvalley[i] = 1
    if ~np.isnan(findpeak[i, 1]):
        peakvalley[i] = -1

######################################
# peak - valley 를 기준으로 step count (peak 다음에는 valley 가 나와야한다)
# 추가적인 고민 필요
######################################

for i in range(1, num_row - 1):
    if peakvalley[i] == -1:  # valley 를 먼저 찾고
        for j in range(1, i + 1):  # 이전 값들 중에
            if peakvalley[i - j] == 1:  # peak 를 발견하면
                break
            elif peakvalley[i - j] == -1:  # valley 가 발견되면 두 개 비교 후 업데이트 break
                if findpeak[i - j, 1] > findpeak[i, 1]:
                    findpeak[i - j, 1] = Nan
                else:
                    findpeak[i, 1] = Nan
                break

for i in range(1, num_row - 1):
    if peakvalley[i] == 1:  # peak 를 먼저 찾고
        for j in range(1, i + 1):  # 이전 값들 중에
            if peakvalley[i - j] == -1:  # valley 를 발견하면
                break
            elif peakvalley[i - j] == 1:  # peak 가 발견되면 두 개 비교 후 업데이트 break
                if findpeak[i - j, 0] < findpeak[i, 0]:
                    findpeak[i - j, 0] = Nan
                else:
                    findpeak[i, 0] = Nan
                break

######################################
######################################
plt.figure(2)
plt.plot(smoothing_norm)
plt.scatter(range(0, num_row - 1), findpeak[range(0, num_row - 1), 0], c='orange')
plt.scatter(range(0, num_row - 1), findpeak[range(0, num_row - 1), 1], c='green')

print("---------------------------------")
print("걸음검출 조건 3")
peakcounting()
print("---------------------------------")

###########################################################################################################################################################################
# Heading
###########################################################################################################################################################################
dt = 0.01

gyro_angle = np.zeros((num_row,3))
gyro_rp_angle = np.zeros((num_row,3))
gyro_rp_data = np.zeros((num_row, 3))

gyro_ori_rp_angle = [0 for i in range(num_row)]

z_angle = [0 for i in range(num_row)]
roll = [0 for i in range(num_row)]
pitch = [0 for i in range(num_row)]



print("gyro_bias : {}   acc_bias : {} ".format(gyro_bias, acc_bias))

plt.figure(3)
plt.plot(gyro_data[:,2],c='blue')
# plt.plot(acc_data[:,1],c='orange')
# plt.plot(acc_data[:,2],c='green')

window_size = 100
smoothing_rollpitch = np.zeros((num_row,2))

for i in range(1 , num_row):
    gyro_angle[i,0] = gyro_angle[i - 1,0] + (gyro_data[i, 0]) * ((sys_time[i] - sys_time[i - 1]) / 1000)
    gyro_angle[i,1] = gyro_angle[i - 1,1] + (gyro_data[i, 1]) * ((sys_time[i] - sys_time[i - 1]) / 1000)

    euler_angle[i, 0] = math.atan((acc_data[i, 1] / math.sqrt(pow(acc_data[i, 0], 2) + pow(acc_data[i, 2], 2)))) * RtoD #ROLL
    euler_angle[i, 1] = math.atan((-acc_data[i, 0] / math.sqrt(pow(acc_data[i, 1], 2) + pow(acc_data[i, 2], 2)))) * RtoD #PITCH

    a = 0
    roll[i] = a * gyro_angle[i, 0] + (1 - a) * euler_angle[i, 0]  #자이로 센서와 가속도 센서 상보필터로 결합
    pitch[i] = a * gyro_angle[i, 1] + (1 - a) * euler_angle[i, 1]

    # if i == 0:
    #     smoothing_rollpitch[i,0] = roll[i]
    #     smoothing_rollpitch[i,1] = pitch[i]
    #
    # elif i <= window_size:
    #     smoothing_rollpitch[i, 0] = np.mean(roll[1:i + 1])
    #     smoothing_rollpitch[i, 1] = np.mean(pitch[1:i + 1])
    #
    # else:
    #     smoothing_rollpitch[i, 0] = np.mean(roll[i - window_size: i])
    #     smoothing_rollpitch[i, 1] = np.mean(pitch[i - window_size: i])

    if abs(gyro_data[i,2]) >= 20:
        gyro_rp_data[i,2] = rotation(roll[i], pitch[i], gyro_data[i,:])
    else:
        gyro_rp_data[i,2] = gyro_data[i, 2]

    gyro_angle[i, 2] = gyro_angle[i - 1, 2] + (gyro_data[i, 2]) * ((sys_time[i] - sys_time[i - 1]) / 1000) #자세보정을 거치지 않은 angle
    gyro_rp_angle[i, 2] = gyro_rp_angle[i - 1, 2] + (gyro_rp_data[i, 2]) * ((sys_time[i] - sys_time[i - 1]) / 1000) #gyro_data -> roll,pitch 만큼 회전변환한 값을 적분


for i in range(num_row):  # azimuth 범위 : -180 ~ 180  를 풀어주는 코드
    diff_heading = ori_data[i, 0] - ori_data[i - 1, 0]

    while math.fabs(diff_heading) > 180:
        if diff_heading < 0:
            ori_data[i, 0] = ori_data[i, 0] + 360
        else:
            ori_data[i, 0] = ori_data[i, 0] - 360
        diff_heading = ori_data[i, 0] - ori_data[i - 1, 0]




for i in range(1,num_row):
    alpa = 0.9
    gyro_ori_rp_angle[i] = gyro_ori_rp_angle[i - 1] + alpa * (gyro_rp_data[i, 2]) * ((sys_time[i] - sys_time[i - 1]) / 1000) + (1 - alpa) * (ori_data[i, 0] - ori_data[i - 1, 0])

# plt.plot(z_angle2[bias_size:],c = 'orange')

plt.figure(4)
plt.plot(gyro_angle[:,2],c='blue')
plt.plot(gyro_rp_angle[:,2],c='green')
plt.plot(gyro_ori_rp_angle,c='orange')
plt.ylabel('Degree')
plt.xlabel('Time')



plt.figure(5)
plt.plot(roll,c='green')
plt.plot(smoothing_rollpitch[:,0],c='orange')
plt.ylabel('Degree')
plt.xlabel('Time')
############################################################
n = peak_count
L = 0.67
theta = gyro_angle[:,2]

for i in range(1,num_row):
    position[i, 0] = position[i - 1, 0] + n[i - 1] * L * math.cos(theta[i - 1] * DtoR)
    position[i, 1] = position[i - 1, 1] + n[i - 1] * L * math.sin(theta[i - 1] * DtoR)

# plt.figure(8)
# plt.plot(position[range(0, num_row), 0], position[range(0, num_row), 1],c='blue')
# plt.axis("equal")

theta =  gyro_rp_angle[:,2]
for i in range(1,num_row):
    position[i, 0] = position[i - 1, 0] + n[i - 1] * L * math.cos(theta[i - 1] * DtoR)
    position[i, 1] = position[i - 1, 1] + n[i - 1] * L * math.sin(theta[i - 1] * DtoR)

# plt.figure(8)
# plt.plot(position[range(0, num_row), 0], position[range(0, num_row), 1],c='green')
# plt.axis("equal")

theta =  gyro_ori_rp_angle
for i in range(1,num_row):
    position[i, 0] = position[i - 1, 0] + n[i - 1] * L * math.cos(theta[i - 1] * DtoR)
    position[i, 1] = position[i - 1, 1] + n[i - 1] * L * math.sin(theta[i - 1] * DtoR)

plt.figure(8)
plt.plot(position[range(0, num_row), 0], position[range(0, num_row), 1],c='orange')
plt.axis("equal")

plt.show()
