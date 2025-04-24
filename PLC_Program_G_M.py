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
Actual_Switch_Position[2] = 1
Light_Control[4] = 1
Light_Control[5] = 0

Actual_Switch_Position[3] = 1
Light_Control[6] = 1
Light_Control[7] = 0

if Occupancy_In[73] and Occupancy_In[74]:
    Actual_Switch_Position[4] = 0
    Light_Control[8] = 1
    Light_Control[9] = 0
elif Actual_Switch_Position[4] == 0 and (Occupancy_In[74] or Occupancy_In[75]):
        Actual_Switch_Position[4] = 0
        Light_Control[8] = 1
        Light_Control[9] = 0
else:
    Actual_Switch_Position[4] = 1
    Light_Control[8] = 0
    Light_Control[9] = 1

#Detects the failures that occur
#General failure check for most cases
for i in range(28,76):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(28,76):
            if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                Track_Failure[Occupancy_Check] = 0
            elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                Track_Failure[Occupancy_Check] = 1
            else:
                Track_Failure[Occupancy_Check] = 0

        if Occupancy_In[62] == 1:
            Track_Failure[62] = 0

#Determines the speed and authority based on a failure      
for Failure_Check in range(28,76):
    if Track_Failure[Failure_Check] == 1:
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

if Track_Failure[29] == 1:
    Suggested_Speed[149] = "1111"

if Track_Failure[28] == 1:
    Suggested_Speed[149] = "1010"
    Suggested_Speed[148] = "1111"

Find_Occupancy = 0
for i in range(28,75):
    if Occupancy_In[i] == 1:
        Find_Occupancy = 1
if Find_Occupancy > 0:
    Suggested_Speed[27] = "0"
    Suggested_Speed[26] = "1010"
    Suggested_Speed[25] = "1111"
    Suggested_Authority[27] = "0"

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
        if i < 4 or (i > 9 and i < 12):
            Light_Control[i] = Light_Control_Out[i]
        if (i != 2 and i != 3 and i != 4) and i < 6:
            Actual_Switch_Position[i] = Actual_Switch_Position_Out[i]
        if i > 75 or i < 25:
            Suggested_Speed[i] = Suggested_Speed_Out[i]
            Suggested_Authority[i] = Suggested_Authority_Out[i]
            Track_Failure[i] = Track_Failure_Out[i]
        if i <= 75 and i >= 25:
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