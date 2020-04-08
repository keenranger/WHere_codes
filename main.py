import PeakValleyDetector
import PeakValleyPlotter
import PeakValleyLoader

if __name__ == "__main__":
    ## sql을 통해 dataframe으로 db 가져오기
    pvloader = PeakValleyLoader.PeakValleyLoader("./data/headingtest.db", "heading1")
    sensor_df = pvloader.sensor_df
    # 피크 밸리 검출
    pvdetect = PeakValleyDetector.PeakValleyDetector()

    for index, row in sensor_df[['time', 'accx', 'accy', 'accz', 'gyrox', 'gyroy', 'gyroz']].iterrows():
        if (index % 1000 == 0):
            print("now it`s {0} step.".format(index))
        pvdetect.step(index, row[:4])

    pvplotter = PeakValleyPlotter.PeakValleyPlotter(pvdetect)
    pvplotter.ani()

