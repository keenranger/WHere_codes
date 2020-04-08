class Walker:
    def __init__(self, initial_heading = 0, step_length = 70):
        self.initial_heading = initial_heading
        self.step_length = step_length

    def step(self, index, time, row, df1, df2):
        self.time = time
        self.gyrox = row[0]
        self.gyroy = row[1]
        self.gyroz = row[2]
