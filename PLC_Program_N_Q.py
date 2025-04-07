import json

# Open and read the Input file
Occupancy_In = [0] * 150
Default_Switch_In = [0] * 6
# Read PLC_INPUTS.json
try:
    with open("PLC_INPUTS.json", "r") as file:
        inputs = json.load(file)
        Occupancy_In = inputs.get("Occupancy", [])
        Default_Switch_In = inputs.get("Default_Switch_Position", [])
except FileNotFoundError:
    print("Error: PLC_INPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error in input file: {e}")

Occupancy_Out = [0] * 150
Track_Failure_Out = [0] * 150
Actual_Switch_Position_Out = [0] * 6

# Read PLC_OUTPUTS.json
try:
    with open("PLC_OUTPUTS.json", "r") as file:
        outputs = json.load(file)
        Occupancy_Out = outputs.get("Occupancy", [])
        Track_Failure_Out = outputs.get("Track_Failure", [])
        Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
except FileNotFoundError:
    print("Error: PLC_OUTPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error in output file: {e}")

#Initialize variables
Light_Control = [0] * 12
Actual_Switch_Position = Actual_Switch_Position_Out
Suggested_Speed = [100] * 150
Suggested_Authority = [100] * 150
Track_Failure = Track_Failure_Out
Temp_Occupancy = Occupancy_Out

#Switch Control
if Occupancy_In[97] and Occupancy_In[98]:
    Actual_Switch_Position[5] = 1
    Light_Control[10] = 1
    Light_Control[11] = 0
elif Actual_Switch_Position[5] == 1 and (Occupancy_In[98] or Occupancy_In[99]):
    Actual_Switch_Position[5] = 1
    Light_Control[10] = 1
    Light_Control[11] = 0
else:
    Actual_Switch_Position[5] = 0
    Light_Control[10] = 0
    Light_Control[11] = 1

#Detects the failures that occur
#General failure check for most cases

for i in range(76,100):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(76,100):
            if Occupancy_Check != {99,84}:
                if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                    Track_Failure[Occupancy_Check] = 0
                elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                    Track_Failure[Occupancy_Check] = 1
                else:
                    Track_Failure[Occupancy_Check] = 0

        if Occupancy_In[99] == 1 and Temp_Occupancy[99] == 1 and Track_Failure[99] == 0:
            Track_Failure[99] = 0
        elif Temp_Occupancy[98] == 0 and Temp_Occupancy[84] == 0 and Occupancy_In[99] == 1:
            Track_Failure[99] = 1
        else:
            Track_Failure[99] = 0

        if Occupancy_In[84] == 1 and Temp_Occupancy[84] == 1 and Track_Failure[84] == 0:
            Track_Failure[84] = 0
        elif Temp_Occupancy[99] == 0 and Temp_Occupancy[83] == 0 and Occupancy_In[84] == 1:
            Track_Failure[84] = 1
        else:
            Track_Failure[84] = 0

#Determines the speed and authority based on a failure      
for Failure_Check in range(76,100):
    if Track_Failure[Failure_Check] == 1 and Failure_Check != 99 and Failure_Check != 98 and Failure_Check != 97:
        Suggested_Speed[Failure_Check] = "0"
        Suggested_Authority[Failure_Check] = "0"
        Suggested_Speed[Failure_Check-1] = "0"
        Suggested_Authority[Failure_Check-1] = "0"
        Suggested_Speed[Failure_Check-2] = "1010"
        Suggested_Speed[Failure_Check-3] = "1111"
        Suggested_Speed[Failure_Check+1] = "0"
        Suggested_Authority[Failure_Check+1] = "0"
        Suggested_Speed[Failure_Check+2] = "1010"
        Suggested_Speed[Failure_Check+3] = "1111"

if Track_Failure[84] == 1:
    Suggested_Speed[99] = "0"
    Suggested_Authority[99] = "0"
    Suggested_Speed[98] = "1010"
    Suggested_Speed[97] = "1111"

if Track_Failure[83] == 1:
    Suggested_Speed[99] = "1010"
    Suggested_Speed[98] = "1111"

if Track_Failure[82] == 1:
    Suggested_Speed[99] = "1111"

if Track_Failure[99] == 1:
    Suggested_Speed[99] = "0"
    Suggested_Authority[99] = "0"
    Suggested_Speed[98] = "0"
    Suggested_Authority[98] = "0"
    Suggested_Speed[97] = "1010"
    Suggested_Speed[96] = "1111"

if Track_Failure[98] == 1:
    Suggested_Speed[99] = "0"
    Suggested_Authority[99] = "0"
    Suggested_Speed[98] = "0"
    Suggested_Authority[98] = "0"
    Suggested_Speed[97] = "0"
    Suggested_Authority[97] = "0"
    Suggested_Speed[96] = "1010"
    Suggested_Speed[95] = "1111"

if Track_Failure[97] == 1:
    Suggested_Speed[99] = "1010"
    Suggested_Speed[98] = "0"
    Suggested_Authority[98] = "0"
    Suggested_Speed[97] = "0"
    Suggested_Authority[97] = "0"
    Suggested_Speed[96] = "0"
    Suggested_Authority[96] = "0"
    Suggested_Speed[95] = "1010"
    Suggested_Speed[94] = "1111"

Find_Occupancy = 0
for i in range(76,100):
    if Occupancy_In[i] == 1:
        Find_Occupancy = 1
if Find_Occupancy > 0:
    Suggested_Speed[75] = "0"
    Suggested_Speed[74] = "1010"
    Suggested_Speed[73] = "1111"
    Suggested_Authority[75] = "0"

try:
    with open("PLC_OUTPUTS.json", "r") as file:
        outputs = json.load(file)
        Suggested_Speed_Out = outputs.get("Suggested_Speed", [])
        Suggested_Authority_Out = outputs.get("Suggested_Authority", [])
        Track_Failure_Out = outputs.get("Track_Failure", [])
        Light_Control_Out = outputs.get("Light_Control", [])
        Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
        Cross_Bar_Control_Out = outputs.get("Cross_Bar_Control", [])

    for i in range(150):
        if i != 10 and i != 11 and i < 12:
            Light_Control[i] = Light_Control_Out[i]
        if (i != 5) and i < 6:
            Actual_Switch_Position[i] = Actual_Switch_Position_Out[i]
        if i > 99 or i < 73:
            Suggested_Speed[i] = Suggested_Speed_Out[i]
            Suggested_Authority[i] = Suggested_Authority_Out[i]
            Track_Failure[i] = Track_Failure_Out[i]
        if i <= 99 and i >= 73:
            if Suggested_Speed[i] != 100:
                Suggested_Speed_Out[i] = Suggested_Speed[i]
            if Suggested_Authority[i] != 100:
                Suggested_Authority_Out[i] = Suggested_Authority[i]

    outputs["Suggested_Speed"] = Suggested_Speed_Out
    outputs["Suggested_Authority"] = Suggested_Authority_Out
    outputs["Track_Failure"] = Track_Failure
    outputs["Light_Control"] = Light_Control
    outputs["Actual_Switch_Position"] = Actual_Switch_Position
    outputs["Cross_Bar_Control"] = Cross_Bar_Control_Out
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")

# Write to PLC_OUTPUTS.json
try:
    with open("PLC_OUTPUTS.json", "w") as file:
        json.dump(outputs, file, indent=2)
except FileNotFoundError:
    print("Error: PLC_OUTPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error while writing to output file: {e}")