class PLC_Out:
    def __init__(Self, Plc_In):
        Self.Plc_In = Plc_In  #Store Plc_In as an instance variable

        #Initialize variables
        Self.Light_Control = [0] * 150
        Self.Actual_Switch_Position = [Self.Plc_In.Switch_Position()] * 6
        Self.Suggested_Speed = Plc_In.Speed()[:]
        Self.Suggested_Authority = Plc_In.Authority()[:]
        Self.Track_Failure = [0] * 150
        Self.Cross_Bar_Control = [0] * 2
        Self.Temp_Occupancy = [0] * 150

    #Return each variable
    def Lights(Self):
        return Self.Light_Control

    def Switches(Self):
        return Self.Actual_Switch_Position

    def Speed(Self):
        return Self.Suggested_Speed

    def Authority(Self):
        return Self.Suggested_Authority

    def Failure(Self):
        return Self.Track_Failure

    def Crossbar(Self):
        return Self.Cross_Bar_Control
    
    #Determines the lights
    def Update_Light_Control(Self, Occupancy):
        for Occupancy_Check in range (len(Occupancy)):
            if Occupancy[Occupancy_Check]:
                Self.Light_Control[Occupancy_Check] = 0
            else:
                Self.Light_Control[Occupancy_Check] = 1

    #Determines the switch positions
    def Update_Actual_Switch_Position(Self, Occupancy):
        if Self.Temp_Occupancy[1] and Occupancy[0]:
            Self.Actual_Switch_Position[0] = 1
        elif Self.Actual_Switch_Position[0] == 1:
            if Self.Temp_Occupancy[0] != 1 and Occupancy[12] != 1:
                Self.Actual_Switch_Position[0] = 0
        else:
            Self.Actual_Switch_Position[0] = Plc_In.Default_Switch_Position

        if Self.Temp_Occupancy[148] and Occupancy[149]:
            Self.Actual_Switch_Position[1] = 1
        elif Self.Actual_Switch_Position[1] == 1:
            if Self.Temp_Occupancy[149] != 1 and Occupancy[27] != 1:
                Self.Actual_Switch_Position[1] = 0
        else:
            Self.Actual_Switch_Position[1] = Plc_In.Default_Switch_Position

        Self.Actual_Switch_Position[2] = 1

        Self.Actual_Switch_Position[3] = 1

        if Self.Temp_Occupancy[77] and Occupancy[76]:
            Self.Actual_Switch_Position[4] = 1
        elif Self.Actual_Switch_Position[4] == 1:
            if Self.Temp_Occupancy[76] != 1 and Occupancy[100] != 1:
                Self.Actual_Switch_Position[4] = 0
        else:
            Self.Actual_Switch_Position[4] = Plc_In.Default_Switch_Position

        if Self.Temp_Occupancy[98] and Occupancy[99]:
            Self.Actual_Switch_Position[5] = 1
        elif Self.Actual_Switch_Position[5] == 1:
            if Self.Temp_Occupancy[99] != 1 and Occupancy[84] != 1:
                Self.Actual_Switch_Position[5] = 0
        else:
            Self.Actual_Switch_Position[5] = Plc_In.Default_Switch_Position

    def Update_Previous_Occupancy(Self, Occupancy):
        for Block_Number in range (150):
            Self.Temp_Occupancy[Block_Number] = Occupancy[Block_Number]

    #Determines the cross bar
    def Update_Cross_Bar(Self, Occupancy):
        Self.Cross_Bar_Control[0] = 1 if any(Occupancy[i] for i in [17, 18, 19]) else 0
        Self.Cross_Bar_Control[1] = 1 if any(Occupancy[i] for i in [106, 107, 108]) else 0

    #Determines the speed and authority based on a failure
    def Update_Speed_Authority(Self):        
        Self.Suggested_Speed = Plc_In.Speed()[:]
        Self.Suggested_Authority = Plc_In.Authority()[:]

        for Failure_Check in range(3, len(Self.Track_Failure)-3):
            if Self.Track_Failure[Failure_Check] == 1 and Failure_Check != 100 and Failure_Check != 101 and Failure_Check != 102 and Failure_Check != 99 and Failure_Check != 98 and Failure_Check != 97:
                Self.Suggested_Speed[Failure_Check] = "0"
                Self.Suggested_Authority[Failure_Check] = "0"
                Self.Suggested_Speed[Failure_Check-1] = "0"
                Self.Suggested_Authority[Failure_Check-1] = "0"
                Self.Suggested_Speed[Failure_Check-2] = "1010"
                Self.Suggested_Speed[Failure_Check-3] = "1111"
                Self.Suggested_Speed[Failure_Check+1] = "0"
                Self.Suggested_Authority[Failure_Check+1] = "0"
                Self.Suggested_Speed[Failure_Check+2] = "1010"
                Self.Suggested_Speed[Failure_Check+3] = "1111"

        if Self.Track_Failure[0] == 1:
            Self.Suggested_Speed[0] = "0"
            Self.Suggested_Authority[0] = "0"
            Self.Suggested_Speed[1] = "0"
            Self.Suggested_Authority[1] = "0"
            Self.Suggested_Speed[2] = "1010"
            Self.Suggested_Speed[3] = "1111"

        if Self.Track_Failure[1] == 1:
            Self.Suggested_Speed[1] = "0"
            Self.Suggested_Authority[1] = "0"
            Self.Suggested_Speed[0] = "0"
            Self.Suggested_Authority[0] = "0"
            Self.Suggested_Speed[2] = "0"
            Self.Suggested_Authority[2] = "0"
            Self.Suggested_Speed[3] = "1010"
            Self.Suggested_Speed[4] = "1111"

        if Self.Track_Failure[2] == 1:
            Self.Suggested_Speed[2] = "0"
            Self.Suggested_Authority[2] = "0"
            Self.Suggested_Speed[1] = "0"
            Self.Suggested_Authority[1] = "0"
            Self.Suggested_Speed[3] = "0"
            Self.Suggested_Authority[3] = "0"
            Self.Suggested_Speed[0] = "1010"
            Self.Suggested_Speed[4] = "1010"
            Self.Suggested_Speed[5] = "1111"
        
        if Self.Track_Failure[10] == 1:
            Self.Suggested_Speed[0] = "1111"

        if Self.Track_Failure[11] == 1:
            Self.Suggested_Speed[0] = "1010"
            Self.Suggested_Speed[1] = "1111"

        if Self.Track_Failure[12] == 1:
            Self.Suggested_Speed[0] = "0"
            Self.Suggested_Authority[0] = "0"
            Self.Suggested_Speed[1] = "1010"
            Self.Suggested_Speed[2] = "1111"

        if Self.Track_Failure[13] == 1:
            Self.Suggested_Speed[0] = "1010"
            Self.Suggested_Speed[1] = "1111"

        if Self.Track_Failure[14] == 1:
            Self.Suggested_Speed[0] = "1111"

        if Self.Track_Failure[29] == 1:
            Self.Suggested_Speed[149] = "1111"

        if Self.Track_Failure[28] == 1:
            Self.Suggested_Speed[149] = "1010"
            Self.Suggested_Speed[148] = "1111"

        if Self.Track_Failure[27] == 1:
            Self.Suggested_Speed[149] = "0"
            Self.Suggested_Authority[149] = "0"
            Self.Suggested_Speed[148] = "1010"
            Self.Suggested_Speed[147] = "1111"

        if Self.Track_Failure[26] == 1:
            Self.Suggested_Speed[149] = "1010"
            Self.Suggested_Speed[148] = "1111"

        if Self.Track_Failure[25] == 1:
            Self.Suggested_Speed[149] = "1111"

        if Self.Track_Failure[100] == 1:
            Self.Suggested_Speed[100] = "0"
            Self.Suggested_Authority[100] = "0"
            Self.Suggested_Speed[101] = "0"
            Self.Suggested_Authority[101] = "0"
            Self.Suggested_Speed[102] = "1010"
            Self.Suggested_Speed[103] = "1111"
            Self.Suggested_Speed[76] = "0"
            Self.Suggested_Authority[76] = "0"
            Self.Suggested_Speed[77] = "1010"
            Self.Suggested_Speed[78] = "1111"

        if Self.Track_Failure[101] == 1:
            Self.Suggested_Speed[101] = "0"
            Self.Suggested_Authority[101] = "0"
            Self.Suggested_Speed[102] = "0"
            Self.Suggested_Authority[102] = "0"
            Self.Suggested_Speed[103] = "1010"
            Self.Suggested_Speed[104] = "1111"
            Self.Suggested_Speed[100] = "0"
            Self.Suggested_Authority[100] = "0"
            Self.Suggested_Speed[76] = "1010"
            Self.Suggested_Speed[77] = "1111"

        if Self.Track_Failure[102] == 1:
            Self.Suggested_Speed[102] = "0"
            Self.Suggested_Authority[102] = "0"
            Self.Suggested_Speed[103] = "0"
            Self.Suggested_Authority[103] = "0"
            Self.Suggested_Speed[104] = "1010"
            Self.Suggested_Speed[105] = "1111"
            Self.Suggested_Speed[101] = "0"
            Self.Suggested_Authority[101] = "0"
            Self.Suggested_Speed[100] = "1010"
            Self.Suggested_Speed[76] = "1111"

        if Self.Track_Failure[84] == 1:
            Self.Suggested_Speed[99] = "0"
            Self.Suggested_Authority[99] = "0"
            Self.Suggested_Speed[98] = "1010"
            Self.Suggested_Speed[97] = "1111"

        if Self.Track_Failure[83] == 1:
            Self.Suggested_Speed[99] = "1010"
            Self.Suggested_Speed[98] = "1111"

        if Self.Track_Failure[82] == 1:
            Self.Suggested_Speed[99] = "1111"

        if Self.Track_Failure[99] == 1:
            Self.Suggested_Speed[99] = "0"
            Self.Suggested_Authority[99] = "0"
            Self.Suggested_Speed[98] = "0"
            Self.Suggested_Authority[98] = "0"
            Self.Suggested_Speed[97] = "1010"
            Self.Suggested_Speed[96] = "1111"

        if Self.Track_Failure[98] == 1:
            Self.Suggested_Speed[99] = "0"
            Self.Suggested_Authority[99] = "0"
            Self.Suggested_Speed[98] = "0"
            Self.Suggested_Authority[98] = "0"
            Self.Suggested_Speed[97] = "0"
            Self.Suggested_Authority[97] = "0"
            Self.Suggested_Speed[96] = "1010"
            Self.Suggested_Speed[95] = "1111"

        if Self.Track_Failure[97] == 1:
            Self.Suggested_Speed[99] = "1010"
            Self.Suggested_Speed[98] = "0"
            Self.Suggested_Authority[98] = "0"
            Self.Suggested_Speed[97] = "0"
            Self.Suggested_Authority[97] = "0"
            Self.Suggested_Speed[96] = "0"
            Self.Suggested_Authority[96] = "0"
            Self.Suggested_Speed[95] = "1010"
            Self.Suggested_Speed[94] = "1111"

        if Self.Track_Failure[149] == 1:
            Self.Suggested_Speed[149] = "0"
            Self.Suggested_Authority[149] = "0"
            Self.Suggested_Speed[148] = "0"
            Self.Suggested_Authority[148] = "0"
            Self.Suggested_Speed[147] = "1010"
            Self.Suggested_Speed[146] = "1111"

        if Self.Track_Failure[148] == 1:
            Self.Suggested_Speed[149] = "0"
            Self.Suggested_Authority[149] = "0"
            Self.Suggested_Speed[148] = "0"
            Self.Suggested_Authority[148] = "0"
            Self.Suggested_Speed[147] = "0"
            Self.Suggested_Authority[147] = "0"
            Self.Suggested_Speed[146] = "1010"
            Self.Suggested_Speed[145] = "1111"

        if Self.Track_Failure[147] == 1:
            Self.Suggested_Speed[149] = "0"
            Self.Suggested_Authority[149] = "0"
            Self.Suggested_Speed[148] = "0"
            Self.Suggested_Authority[148] = "0"
            Self.Suggested_Speed[147] = "0"
            Self.Suggested_Authority[147] = "0"
            Self.Suggested_Speed[146] = "1010"
            Self.Suggested_Speed[145] = "1111"

    #Detects the failures that occur
    def Update_Failure(Self,Occupancy):
        #General failure check for most cases
        for Occupancy_Check in range(0,149):
            if Occupancy_Check != {12,27,100,99,84}:
                if Occupancy[Occupancy_Check] == 1 and Self.Temp_Occupancy[Occupancy_Check] == 1 and Self.Track_Failure[Occupancy_Check] == 0:
                    Self.Track_Failure[Occupancy_Check] = 0
                elif Self.Temp_Occupancy[Occupancy_Check-1] == 0 and Self.Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy[Occupancy_Check] == 1:
                    Self.Track_Failure[Occupancy_Check] = 1
                else:
                    Self.Track_Failure[Occupancy_Check] = 0
        
        if Occupancy[0] == 1 and Self.Temp_Occupancy[0] == 1 and Self.Track_Failure[0] == 0:
            Self.Track_Failure[12] = 0
        elif Self.Temp_Occupancy[1] == 0 and Self.Temp_Occupancy[0] == 0 and Occupancy[0] == 1:
            Self.Track_Failure[0] = 1
        
        if Occupancy[12] == 1 and Self.Temp_Occupancy[12] == 1 and Self.Track_Failure[12] == 0:
            Self.Track_Failure[12] = 0
        elif Self.Temp_Occupancy[11] == 0 and Self.Temp_Occupancy[13] == 0 and Self.Temp_Occupancy[0] == 0 and Occupancy[12] == 1 and Self.Actual_Switch_Position[0] == 0:
            Self.Track_Failure[12] = 1
        else:
            Self.Track_Failure[12] = 0
        
        if Occupancy[27] == 1 and Self.Temp_Occupancy[27] == 1 and Self.Track_Failure[27] == 0:
            Self.Track_Failure[27] = 0
        elif Self.Temp_Occupancy[26] == 0 and Self.Temp_Occupancy[28] == 0 and Self.Temp_Occupancy[149] == 0 and Occupancy[27] == 1:
            Self.Track_Failure[27] = 1
        else:
            Self.Track_Failure[27] = 0

        if Occupancy[100] == 1 and Self.Temp_Occupancy[100] == 1 and Self.Track_Failure[100] == 0:
            Self.Track_Failure[100] = 0
        elif Self.Temp_Occupancy[76] == 0 and Self.Temp_Occupancy[101] == 0 and Occupancy[100] == 1:
            Self.Track_Failure[100] = 1
        else:
            Self.Track_Failure[100] = 0

        if Occupancy[99] == 1 and Self.Temp_Occupancy[99] == 1 and Self.Track_Failure[99] == 0:
            Self.Track_Failure[99] = 0
        elif Self.Temp_Occupancy[98] == 0 and Self.Temp_Occupancy[84] == 0 and Occupancy[99] == 1:
            Self.Track_Failure[99] = 1
        else:
            Self.Track_Failure[99] = 0

        if Occupancy[84] == 1 and Self.Temp_Occupancy[84] == 1 and Self.Track_Failure[84] == 0:
            Self.Track_Failure[84] = 0
        elif Self.Temp_Occupancy[99] == 0 and Self.Temp_Occupancy[83] == 0 and Occupancy[84] == 1:
            Self.Track_Failure[84] = 1
        else:
            Self.Track_Failure[84] = 0

        if Occupancy[149] == 1 and Self.Temp_Occupancy[149] == 1 and Self.Track_Failure[149] == 0:
            Self.Track_Failure[149] = 0
        elif Self.Temp_Occupancy[148] == 0 and Self.Temp_Occupancy[27] == 0 and Occupancy[149] == 1:
            Self.Track_Failure[149] = 1
        else:
            Self.Track_Failure[149] = 0

        if Occupancy[62] == 1:
            Self.Track_Failure[62] = 0


#Delayed import to avoid circular dependency
def Get_PLC_In():
    from Wayside_Controller import PLC_IN
    return PLC_IN()

#Get input values from PLC_IN
Plc_In = Get_PLC_In()

#Create an instance of PLC_Out
plc_out = PLC_Out(Plc_In)