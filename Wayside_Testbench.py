class Input:
    def __init__(self):
        # Initialize attributes in the constructor
        self.Default_Switch_Position = 0
        self.Suggested_Speed = [50] * 26
        self.Suggested_Authority = [50] * 26
        self.Block_Occupancy = [0] * 26
        self.Count = 0
        self.Random_Tracker = 0
        self.Failure_Block_Number = 100
        self.Random_Occupancy_Number = 0

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Occupancy(self):
        return self.Block_Occupancy
    
    def Failure(self):
        return self.Random_Tracker
    
    def Failure_Block(self):
        return self.Failure_Block_Number
