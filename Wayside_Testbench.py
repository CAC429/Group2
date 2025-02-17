class Input:
    def __init__(self):
        # Initialize attributes in the constructor
        self.Default_Switch_Position = False
        self.Suggested_Speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Suggested_Authority = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Block_Occupancy = [bool(x) for x in [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Occupancy(self):
        return self.Block_Occupancy
