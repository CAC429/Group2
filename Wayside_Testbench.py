import time
class Input:
    def __init__(self):
        # Initialize attributes in the constructor
        self.Default_Switch_Position = 0
        self.Suggested_Speed = [50] * 150
        self.Suggested_Authority = [50] * 150
        self.Block_Occupancy = [0] * 150
        self.count = 0

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def UpdateOccupancy(self):
        self.count = self.count + 1
        # if self.count == 10:
        #     self.Block_Occupancy[78] = 1
        # elif self.count == 11:
        #     self.Block_Occupancy[78] = 0
        #     self.Block_Occupancy[77] = 1
        # elif self.count == 12:
        #     self.Block_Occupancy[77] = 0
        #     self.Block_Occupancy[76] = 1
        # elif self.count == 13:
        #     self.Block_Occupancy[20] = 1
        # elif self.count == 25:
        #     self.Block_Occupancy[76] = 0
        #     self.Block_Occupancy[100] = 1
        # elif self.count == 26:
        #     self.Block_Occupancy[100] = 0
        #     self.Block_Occupancy[101] = 1

    def Occupancy(self):
        return self.Block_Occupancy
