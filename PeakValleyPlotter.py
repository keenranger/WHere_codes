import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import numpy as np
rcParams['animation.convert_path'] = r'C:\Program Files\ImageMagick\magick.exe'
rcParams['animation.ffmpeg_path'] = r'C:\Program Files\ImageMagick\ffmpeg.exe'
class PeakValleyPlotter():
    def __init__(self, pvdetect, norm_df):
        self.pvdetect = pvdetect
        self.fig, self.ax = plt.subplots()
        self.norm_df = norm_df
        plt.plot(self.norm_df['time'], self.norm_df['value'], c='y', linewidth=0.5)

    def plot(self):
        plt.scatter(self.pvdetect.peak_df['time'], self.pvdetect.peak_df['value'], c='red')
        plt.scatter(self.pvdetect.valley_df['time'], self.pvdetect.valley_df['value'], c='blue')
        plt.show()
    def ani(self):
        temp = plt.axvline(self.norm_df['time'].loc[0], c='b')
        temp2 = plt.scatter(self.norm_df['time'].loc[0] ,self.norm_df['value'].loc[0], c = 'r')
        temp3 = plt.scatter(self.norm_df['time'].loc[0] ,self.norm_df['value'].loc[0], c = 'g')
        def animate(i):
            temp.set_data([self.norm_df['time'].loc[i*10], self.norm_df['time'].loc[i*10]], [0, 1])
            peak_now = (self.pvdetect.peak_df[self.pvdetect.peak_df['time'] < self.norm_df.loc[i*10]['time']] )
            valley_now = (self.pvdetect.valley_df[self.pvdetect.valley_df['time'] < self.norm_df.loc[i*10]['time']] )
            temp2.set_offsets(peak_now)
            temp3.set_offsets(valley_now)
            return temp, temp2, temp3,
        myAnimation = animation.FuncAnimation(self.fig, animate, frames=np.arange(0.0, len(self.norm_df)/10), \
                                        interval=10, blit=True, repeat=True)
        plt.show()
    def ani_save(self):
        temp = plt.axvline(self.norm_df['time'].loc[0], c='b')
        temp2 = plt.scatter(self.norm_df['time'].loc[0] ,self.norm_df['value'].loc[0], c = 'r')
        temp3 = plt.scatter(self.norm_df['time'].loc[0] ,self.norm_df['value'].loc[0], c = 'g')
        def animate(i):
            temp.set_data([self.norm_df['time'].loc[i*10], self.norm_df['time'].loc[i*10]], [0, 1])
            peak_now = (self.pvdetect.peak_df[self.pvdetect.peak_df['time'] < self.norm_df.loc[i*10]['time']] )
            valley_now = (self.pvdetect.valley_df[self.pvdetect.valley_df['time'] < self.norm_df.loc[i*10]['time']] )
            temp2.set_offsets(peak_now)
            temp3.set_offsets(valley_now)
            return temp, temp2, temp3,
        myAnimation = animation.FuncAnimation(self.fig, animate, frames=np.arange(0.0, len(self.norm_df)/10), \
                                        interval=10, blit=True, repeat=False)
        myAnimation.save('myAnimation.gif', writer='imagemagick', fps=30)