import json

# Open and read the Input file
Occupancy_In = [0] * 76
Default_Switch_In = [0] * 7
# Read PLC_INPUTS.json
try:
    with open("PLC_INPUTS2.json", "r") as file:
        inputs = json.load(file)
        Occupancy_In = inputs.get("Occupancy", [])
        Default_Switch_In = inputs.get("Default_Switch_Position", [])
except FileNotFoundError:
    print("Error: PLC_INPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error in input file: {e}")

Occupancy_Out = [0] * 76
Track_Failure_Out = [0] * 76
Actual_Switch_Position_Out = [0] * 7

# Read PLC_OUTPUTS.json
try:
    with open("PLC_OUTPUTS2.json", "r") as file:
        outputs = json.load(file)
        Occupancy_Out = outputs.get("Occupancy", [])
        Track_Failure_Out = outputs.get("Track_Failure", [])
        Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
except FileNotFoundError:
    print("Error: PLC_OUTPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error in output file: {e}")

#Initialize variables
Light_Control = [0] * 14
Actual_Switch_Position = Actual_Switch_Position_Out
Suggested_Speed = [100] * 76
Suggested_Authority = [100] * 76
Track_Failure = Track_Failure_Out
Cross_Bar_Control = [0] * 2
Temp_Occupancy = Occupancy_Out

#Switch Control and Light Control

if Occupancy_In[63] == 1 and Occupancy_In[64] == 1:
    Actual_Switch_Position[6] = 1
    Light_Control[12] = 0
    Light_Control[13] = 1
elif Actual_Switch_Position[6] == 1 and Occupancy_In[64] == 1:
    Actual_Switch_Position[6] = 1
    Light_Control[12] = 0
    Light_Control[13] = 1
elif Actual_Switch_Position[6] == 1 and Occupancy_In[65] == 1:
    Actual_Switch_Position[6] = 1
    Light_Control[12] = 0
    Light_Control[13] = 1
else:
    Actual_Switch_Position[6] = 0
    Light_Control[12] = 1
    Light_Control[13] = 0

#Detects the failures that occur
#General failure check for most cases
for i in range(48,66):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(48,66):
            if Occupancy_Check != 0 and Occupancy_Check != 8:
                if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                    Track_Failure[Occupancy_Check] = 0
                elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                    Track_Failure[Occupancy_Check] = 1
                else:
                    Track_Failure[Occupancy_Check] = 0

#Determines the speed and authority based on a failure      
for Failure_Check in range(48,53):
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
    
for i in range(53,66):
    if Track_Failure[i] == 1:
        Suggested_Speed[i] = "0"
        Suggested_Authority[i] = "0"
        Suggested_Speed[i-1] = "0"
        Suggested_Authority[i-1] = "0"
        Suggested_Speed[i-2] = "1010"
        Suggested_Speed[i-3] = "1111"

for i in range(48, 66):
    if Occupancy_In[i] == 1:
        Suggested_Authority[66] = "0"
        Suggested_Speed[66] = "0"
        Suggested_Authority[67] = "0"
        Suggested_Speed[67] = "0"
        Suggested_Authority[68] = "0"
        Suggested_Speed[68] = "0"
        Suggested_Authority[69] = "0"
        Suggested_Speed[69] = "0"
        Suggested_Authority[70] = "0"
        Suggested_Speed[70] = "0"

# Read PLC_OUTPUTS.jsons
try:
    with open("PLC_OUTPUTS2.json", "r") as file:
        outputs = json.load(file)
        Suggested_Speed_Out = outputs.get("Suggested_Speed", [])
        Suggested_Authority_Out = outputs.get("Suggested_Authority", [])
        Track_Failure_Out = outputs.get("Track_Failure", [])
        Light_Control_Out = outputs.get("Light_Control", [])
        Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
    for i in range(76):
        if i < 12:
            Light_Control[i] = Light_Control_Out[i]
        if i < 6:
            Actual_Switch_Position[i] = Actual_Switch_Position_Out[i]
        if i < 48 or i > 70:
            Suggested_Speed[i] = Suggested_Speed_Out[i]
            Suggested_Authority[i] = Suggested_Authority_Out[i]
            Track_Failure[i] = Track_Failure_Out[i]
        if i >= 48 and i <= 70:
            if Suggested_Speed[i] != 100:
                Suggested_Speed_Out[i] = Suggested_Speed[i]
            if Suggested_Authority[i] != 100:
                Suggested_Authority_Out[i] = Suggested_Authority[i]

    outputs["Suggested_Speed"] = Suggested_Speed_Out
    outputs["Suggested_Authority"] = Suggested_Authority_Out
    outputs["Track_Failure"] = Track_Failure
    outputs["Light_Control"] = Light_Control
    outputs["Actual_Switch_Position"] = Actual_Switch_Position
    outputs["Occupancy"] = Occupancy_In
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")

# Write to PLC_OUTPUTS.json
try:
    with open("PLC_OUTPUTS2.json", "w") as file:
        json.dump(outputs, file, indent=2)
except FileNotFoundError:
    print("Error: PLC_OUTPUTS.json not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected error while writing to output file: {e}")
