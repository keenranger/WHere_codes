import matplotlib.pyplot as plt

class SensorPlotter:
    def __init__(self, sensor_df, file_name):
        self.sensor_df = sensor_df
        self.file_name = file_name

    def AccPlot(self):
        plt.figure()
        plt.plot(self.sensor_df['time'], self.sensor_df['accx'], c='blue', label='accx')
        plt.plot(self.sensor_df['time'], self.sensor_df['accy'], c='green', label='accy')
        plt.plot(self.sensor_df['time'], self.sensor_df['accz'], c='orange', label='accz')
        plt.legend(loc='best')
        plt.xlabel('time')
        plt.ylabel('m/s^2')
        plt.title(self.file_name)

    def GyroPlot(self):
        plt.figure()
        plt.plot(self.sensor_df['time'], self.sensor_df['gyrox'], c='blue', label='gyrox')
        plt.plot(self.sensor_df['time'], self.sensor_df['gyroy'], c='green', label='gyroy')
        plt.plot(self.sensor_df['time'], self.sensor_df['gyroz'], c='orange', label='gyroz')
        plt.legend(loc='best')
        plt.xlabel('time')
        plt.ylabel('rad/s')
        plt.title(self.file_name)

    def EulerPlot(self):
        plt.figure()
        plt.plot(self.sensor_df['time'], self.sensor_df['roll'], c='blue', label='roll')
        plt.plot(self.sensor_df['time'], self.sensor_df['pitch'], c='green', label='pitch')
        plt.plot(self.sensor_df['time'], self.sensor_df['yaw'], c='orange', label='yaw')
        plt.legend(loc='best')
        plt.xlabel('time')
        plt.ylabel('degree')
        plt.title(self.file_name)