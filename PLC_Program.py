from Wayside_Controller import PLC_IN

class PLC_Out:
    def Lights(Light_Control):
        Light_Control
    def Switches(Actual_Switch_Position):
        Actual_Switch_Position
    def Speed(Binary_Suggested_Speed):
        Binary_Suggested_Speed
    def Authority(Binary_Suggested_Authority):
        Binary_Suggested_Authority
    def Failure(Track_Failure):
        Track_Failure
    def Crossbar(Cross_Bar_Control):
        Cross_Bar_Control

Default_Switch_Position = PLC_IN.Switch_Position([])
Binary_Suggested_Speed = PLC_IN.Speed([])
Binary_Suggested_Authority = PLC_IN.Authority([])
Block_Occupancy = PLC_IN.Occupancy([])
Track_Failure = [bool(x) for x in [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
Actual_Switch_Position = Default_Switch_Position
Light_Control = [bool(x) for x in [0,0]]
Cross_Bar_Control = 0

for x in range(14):
    if Block_Occupancy[x] == 1 and (Block_Occupancy[x+1] == 1 or Track_Failure[x+1] == 1):
        Binary_Suggested_Speed[x-1] = 101
        Binary_Suggested_Speed[x] = 0
        Binary_Suggested_Authority[x-1] = 11001
        Binary_Suggested_Authority[x] = 0
    else:
        Binary_Suggested_Speed[x-1] = 110010
        Binary_Suggested_Speed[x] = 110010
        Binary_Suggested_Authority[x-1] = 110010
        Binary_Suggested_Authority[x] = 110010


        

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
