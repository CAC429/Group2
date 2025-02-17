from Wayside_Controller import PLC_IN

class PLC_Out:
    def __init__(self, Light_Control=None, Actual_Switch_Position=None, 
                 Binary_Suggested_Speed=None, Binary_Suggested_Authority=None, 
                 Track_Failure=None, Cross_Bar_Control=None):
        
        self.Light_Control = Light_Control if Light_Control else [0, 0]
        self.Actual_Switch_Position = Actual_Switch_Position if Actual_Switch_Position else 0
        self.Binary_Suggested_Speed = Binary_Suggested_Speed
        self.Binary_Suggested_Authority = Binary_Suggested_Authority
        self.Track_Failure = Track_Failure if Track_Failure else [0] * 15
        self.Cross_Bar_Control = Cross_Bar_Control if Cross_Bar_Control else 0

    def Lights(self):
        return self.Light_Control

    def Switches(self):
        return self.Actual_Switch_Position

    def Speed(self):
        return self.Binary_Suggested_Speed

    def Authority(self):
        return self.Binary_Suggested_Authority

    def Failure(self):
        return self.Track_Failure

    def Crossbar(self):
        return self.Cross_Bar_Control

plc_in = PLC_IN()

Default_Switch_Position = plc_in.Switch_Position()
Binary_Suggested_Speed = plc_in.Speed()
Binary_Suggested_Authority = plc_in.Authority()
Block_Occupancy = plc_in.Occupancy()
Track_Failure = [bool(x) for x in [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
Actual_Switch_Position = Default_Switch_Position
Light_Control = [bool(x) for x in [0,0]]
Cross_Bar_Control = 0

for x in range(13):
    if Block_Occupancy[x] == 1 and (Block_Occupancy[x+1] == 1 or Track_Failure[x+1] == 1):
        Binary_Suggested_Speed[x-1] = format(5, 'b')
        Binary_Suggested_Speed[x] = 0
        Binary_Suggested_Authority[x-1] = format(25, 'b')
        Binary_Suggested_Authority[x] = 0
    else:
        Binary_Suggested_Speed[x-1] = format(50, 'b')
        Binary_Suggested_Speed[x] = format(50, 'b')
        Binary_Suggested_Authority[x-1] = format(50, 'b')
        Binary_Suggested_Authority[x] = format(50, 'b')

if (Block_Occupancy[4] == 1 or Block_Occupancy[5] == 1 or Block_Occupancy[6] == 1) and Actual_Switch_Position == 0:
    Light_Control = [1,0]
elif (Block_Occupancy[4] == 1 or Block_Occupancy[10] == 1 or Block_Occupancy[11] == 1) and Actual_Switch_Position == 1:
    Light_Control = [0,1]
else:
    Light_Control = [0,0]

if Block_Occupancy[1] or Block_Occupancy[2] or Block_Occupancy[3]:
    Cross_Bar_Control = 1
else:
    Cross_Bar_Control = 0