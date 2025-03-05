import random
class PLC_Out:
    def __init__(self, plc_in):
        self.plc_in = plc_in  #Store plc_in as an instance variable

        #Initialize variables
        self.Light_Control = [0, 0]
        self.Actual_Switch_Position = [self.plc_in.Switch_Position()] * 6
        self.Suggested_Speed =plc_in.Speed()[:]
        self.Suggested_Authority = plc_in.Authority()[:]
        self.Track_Failure = [False] * 26
        self.Cross_Bar_Control = 0
        self.Temp_Occupancy = [0] * 26

    #Return each variable
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
    
    #Determines the lights
    def Update_Light_Control(self):
        if (self.plc_in.Occupancy()[4] or self.plc_in.Occupancy()[5] or self.plc_in.Occupancy()[6]) and self.Actual_Switch_Position == 0:
            self.Light_Control = [1, 0]
        elif (self.plc_in.Occupancy()[4] or self.plc_in.Occupancy()[10] or self.plc_in.Occupancy()[11]) and self.Actual_Switch_Position == 1:
            self.Light_Control = [0, 1]
        else:
            self.Light_Control = [0, 0]

    def Update_Actual_Switch_Position(self):
        if self.Temp_Occupancy[4] and self.plc_in.Occupancy()[3]:
            self.Actual_Switch_Position[0] = 1
        else:
            self.Actual_Switch_Position[0] = 0
        if self.Temp_Occupancy[24] and self.plc_in.Occupancy()[25]:
            self.Actual_Switch_Position[1] = 1
        else:
            self.Actual_Switch_Position[1] = 0
        if self.Temp_Occupancy[7] and self.plc_in.Occupancy()[8]:
            self.Actual_Switch_Position[1] = 0
        else:
            self.Actual_Switch_Position[1] = 1
        if self.Temp_Occupancy[8] and self.plc_in.Occupancy()[9]:
            self.Actual_Switch_Position[1] = 0
        else:
            self.Actual_Switch_Position[1] = 1
        if self.Temp_Occupancy[11] and self.plc_in.Occupancy()[12]:
            self.Actual_Switch_Position[1] = 0
        else:
            self.Actual_Switch_Position[1] = 1
        if self.Temp_Occupancy[15] and self.plc_in.Occupancy()[16]:
            self.Actual_Switch_Position[1] = 1
        else:
            self.Actual_Switch_Position[1] = 0
        for Block_Number in range (26):
            self.Temp_Occupancy[Block_Number] = self.plc_in.Occupancy()[Block_Number]

    #Determines the cross bar
    def Update_Cross_Bar(self):
        self.Cross_Bar_Control = 1 if any(self.plc_in.Occupancy()[i] for i in [1, 2, 3]) else 0

    #Determines the speed and authority
    def Update_Speed_Authority(self):
    #Create new temporary lists to avoid overwriting while iterating
        Temp_suggested_speed = self.Suggested_Speed[:]  
        Temp_suggested_authority = self.Suggested_Authority[:]
        
        #New suggetsed speed and authority calculations
        if self.plc_in.Occupancy()[1] == 1:
            Temp_suggested_speed[0] = "0"
            Temp_suggested_authority[0] = "0"
        else:
            Temp_suggested_speed[0] = "110010"
            Temp_suggested_authority[0] = "110010"
            Temp_suggested_speed[1] = "110010"
            Temp_suggested_authority[1] = "110010"

        if self.plc_in.Occupancy()[25] == 1:
            Temp_suggested_speed[24] = "0"
            Temp_suggested_authority[24] = "0"
            Temp_suggested_speed[23] = "1010"
            Temp_suggested_authority[23] = "11001"
        else:
            Temp_suggested_speed[24] = "110010"
            Temp_suggested_authority[24] = "110010"

        for x in range(2, 24):
            if self.plc_in.Occupancy()[x]:
                Temp_suggested_speed[x-2] = "1010"
                Temp_suggested_authority[x-2] = "11001"
                Temp_suggested_speed[x-1] = "0"
                Temp_suggested_authority[x-1] = "0"
                Temp_suggested_speed[x+2] = "1010"
                Temp_suggested_authority[x+2] = "11001"
                Temp_suggested_speed[x+1] = "0"
                Temp_suggested_authority[x+1] = "0"
            else:
                Temp_suggested_speed[x] = "110010"
                Temp_suggested_authority[x] = "110010"

        #Temp list to actual list
        self.Suggested_Speed = Temp_suggested_speed
        self.Suggested_Authority = Temp_suggested_authority

def Get_PLC_In():
    from Wayside_Controller import PLC_IN  #Delayed import to avoid circular dependency
    return PLC_IN()

#Get input values from PLC_IN
plc_in = Get_PLC_In()

#Create an instance of PLC_Out
plc_out = PLC_Out(plc_in)