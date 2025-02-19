class PLC_Out:
    def __init__(self, plc_in):
        self.plc_in = plc_in  # ✅ Store plc_in as an instance variable

        self.Light_Control = [0, 0]
        self.Actual_Switch_Position = plc_in.Switch_Position()
        self.Suggested_Speed =plc_in.Speed()[:]
        self.Suggested_Authority = plc_in.Authority()[:]
        self.Track_Failure = [False] * 15
        self.Cross_Bar_Control = 0

    def Lights(self):
        return self.Light_Control

    def Switches(self):
        return self.Actual_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Failure(self):
        return self.Track_Failure

    def Crossbar(self):
        return self.Cross_Bar_Control
    
    def Update_Light_Control(self):
        if (self.plc_in.Occupancy()[4] or self.plc_in.Occupancy()[5] or self.plc_in.Occupancy()[6]) and self.Actual_Switch_Position == 0:
            self.Light_Control = [1, 0]
        elif (self.plc_in.Occupancy()[4] or self.plc_in.Occupancy()[10] or self.plc_in.Occupancy()[11]) and self.Actual_Switch_Position == 1:
            self.Light_Control = [0, 1]
        else:
            self.Light_Control = [0, 0]

    def Update_Cross_Bar(self):
        self.Cross_Bar_Control = 1 if any(self.plc_in.Occupancy()[i] for i in [1, 2, 3]) else 0

    def Update_Speed_Authority(self):
    # Step 1: Create new temporary lists (to avoid overwriting while iterating)
        Temp_suggested_speed = self.Suggested_Speed[:]  
        Temp_suggested_authority = self.Suggested_Authority[:]
        for x in range(2, 15):
            if self.plc_in.Occupancy()[x]:
                Temp_suggested_speed[x-2] = format(10, 'b')
                Temp_suggested_authority[x-2] = format(25, 'b')
                Temp_suggested_speed[x-1] = format(0, 'b')
                Temp_suggested_authority[x-1] = format(0, 'b')
            else:
                Temp_suggested_speed[x-2] = format(50, 'b')
                Temp_suggested_authority[x-2] = format(50, 'b')
                Temp_suggested_speed[x-1] = format(50, 'b')
                Temp_suggested_authority[x-1] = format(50, 'b')
        self.Suggested_Speed = Temp_suggested_speed
        self.Suggested_Authority = Temp_suggested_authority
        #print("SPEED---------",(self.Suggested_Speed))
        #print("Authority---------",(self.Suggested_Authority))

def Get_PLC_In():
    from Wayside_Controller import PLC_IN  # Delayed import to avoid circular dependency
    return PLC_IN()

# ✅ Get input values from PLC_IN
plc_in = Get_PLC_In()

# ✅ Create an instance of PLC_Out
plc_out = PLC_Out(plc_in)
