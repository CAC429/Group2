class PLC_Out:
    def __init__(self, Light_Control=None, Actual_Switch_Position=None, 
                 Suggested_Speed=None, Suggested_Authority=None, 
                 Track_Failure=None, Cross_Bar_Control=None):
        
        self.Light_Control = Light_Control if Light_Control else [0, 0]
        self.Actual_Switch_Position = Actual_Switch_Position if Actual_Switch_Position else 0
        self.Suggested_Speed = Suggested_Speed
        self.Suggested_Authority = Suggested_Authority
        self.Track_Failure = Track_Failure if Track_Failure else [0] * 15
        self.Cross_Bar_Control = Cross_Bar_Control if Cross_Bar_Control else 0

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

def Get_PLC_In():
    from Wayside_Controller import PLC_IN  # Delayed import to avoid circular dependency
    return PLC_IN()

plc_in = Get_PLC_In()

Default_Switch_Position = plc_in.Switch_Position()
Suggested_Speed = plc_in.Speed()
Suggested_Authority = plc_in.Authority()
Block_Occupancy = plc_in.Occupancy()
Track_Failure = [bool(x) for x in [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
Actual_Switch_Position = Default_Switch_Position
Light_Control = [bool(x) for x in [0,0]]
Cross_Bar_Control = 0

print("--------------------",(Suggested_Speed[0][0]))

for x in range(1, 13):
    if Block_Occupancy[x] == True and (Block_Occupancy[x+1] == True or Track_Failure[x+1] == 1):
        Suggested_Speed[0][x-1] = format(5, 'b')
        Suggested_Speed[0][x] = format(0, 'b')
        Suggested_Authority[0][x-1] = format(25, 'b')
        Suggested_Authority[0][x] = format(0, 'b')
    else:
        Suggested_Speed[0][x-1] = format(50, 'b')
        Suggested_Speed[0][x] = format(50, 'b')
        Suggested_Authority[0][x-1] = format(50, 'b')
        Suggested_Authority[0][x] = format(50, 'b')

if (Block_Occupancy[4] == True or Block_Occupancy[5] == True or Block_Occupancy[6] == True) and Actual_Switch_Position == 0:
    PLC_Out.Light_Control = [1,0]
elif (Block_Occupancy[4] == True or Block_Occupancy[10] == True or Block_Occupancy[11] == True) and Actual_Switch_Position == 1:
    PLC_Out.Light_Control = [0,1]
else:
    PLC_Out.Light_Control = [0,0]

if Block_Occupancy[1] or Block_Occupancy[2] or Block_Occupancy[3]:
    PLC_Out.Cross_Bar_Control = 1
else:
    PLC_Out.Cross_Bar_Control = 0

