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
if (Occupancy_In[23] == 1 and Occupancy_In[24] == 1) or (Actual_Switch_Position[2] == 1 and Occupancy_In[24] == 1) or (Actual_Switch_Position[2] == 1 and Occupancy_In[25] == 1) or (Actual_Switch_Position[2] == 1 and Occupancy_In[26] == 1):
    Actual_Switch_Position[2] = 1
    Light_Control[4] = 1
    Light_Control[5] = 0
else:
    Actual_Switch_Position[2] = 0
    Light_Control[4] = 0
    Light_Control[5] = 1

if (Occupancy_In[34] == 1 and Occupancy_In[33] == 1) or (Actual_Switch_Position[3] == 0 and Occupancy_In[33] == 1) or (Actual_Switch_Position[3] == 0 and Occupancy_In[32] == 1) or (Actual_Switch_Position[3] == 0 and Occupancy_In[31] == 1):
    Actual_Switch_Position[3] = 0
    Light_Control[6] = 1
    Light_Control[7] = 0
elif (Occupancy_In[73] == 1 and Occupancy_In[72] == 1) or (Actual_Switch_Position[3] == 1 and Occupancy_In[72] == 1) or (Actual_Switch_Position[3] == 1 and Occupancy_In[71] == 1):
    Actual_Switch_Position[3] = 1
    Light_Control[6] = 0
    Light_Control[7] = 1
else:
    Actual_Switch_Position[3] = 0
    Light_Control[6] = 1
    Light_Control[7] = 0 

if (Occupancy_In[34] == 1 and Occupancy_In[35] == 1) or (Actual_Switch_Position[4] == 1 and Occupancy_In[35] == 1) or (Actual_Switch_Position[4] == 1 and Occupancy_In[36] == 1) or (Actual_Switch_Position[4] == 1 and Occupancy_In[37] == 1):
    Actual_Switch_Position[4] = 1
    Light_Control[8] = 1
    Light_Control[9] = 0
else:
    Actual_Switch_Position[4] = 0
    Light_Control[8] = 0
    Light_Control[9] = 1

if (Occupancy_In[49] == 1 and Occupancy_In[48] == 1) or (Actual_Switch_Position[5] == 0 and Occupancy_In[48] == 1) or (Actual_Switch_Position[5] == 0 and Occupancy_In[47] == 1) or (Actual_Switch_Position[5] == 0 and Occupancy_In[46] == 1):
    Actual_Switch_Position[5] = 0
    Light_Control[10] = 1
    Light_Control[11] = 0
elif (Occupancy_In[68] == 1 and Occupancy_In[67] == 1) or (Actual_Switch_Position[5] == 1 and Occupancy_In[67] == 1) or (Actual_Switch_Position[5] == 1 and Occupancy_In[66] == 1):
    Actual_Switch_Position[5] = 1
    Light_Control[10] = 0
    Light_Control[11] = 1
else:
    Actual_Switch_Position[5] = 0
    Light_Control[10] = 1
    Light_Control[11] = 0 

#Cross Bar Control
Cross_Bar_Control[1] = 1 if any(Occupancy_In[i] for i in [45, 46, 47]) else 0
#Detects the failures that occur
#General failure check for most cases
for i in range(15,75):
    if (i >= 15 and i <=47) or (i >= 66  and i <= 74):
        if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

            for Occupancy_Check in range(15,75):
                if (i >= 15 and i <=47) or (i >= 66  and i <= 74):
                    if Occupancy_Check != {0}:
                        if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                            Track_Failure[Occupancy_Check] = 0
                        elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                            Track_Failure[Occupancy_Check] = 1
                        else:
                            Track_Failure[Occupancy_Check] = 0

if Occupancy_In[75] == 1 and Temp_Occupancy[26] == 1 and Track_Failure[75] == 0:
    Track_Failure[75] == 0
elif Track_Failure[75] == 0 and Occupancy_In[75] == 1:
    Track_Failure[75] = 0
elif Occupancy_In[75] == 1 and Temp_Occupancy[26] == 0:
    Track_Failure[75] = 1
else:
    Track_Failure[75] = 0

if Occupancy_In[70] == 1 and Temp_Occupancy[37] == 1 and Track_Failure[70] == 0:
    Track_Failure[70] == 0
elif Track_Failure[70] == 0 and Occupancy_In[70] == 1:
    Track_Failure[70] = 0
elif Occupancy_In[70] == 1 and Temp_Occupancy[37] == 0:
    Track_Failure[70] = 1
else:
    Track_Failure[70] = 0

if Occupancy_In[32] == 1 and Temp_Occupancy[71] == 1 and Track_Failure[32] == 0:
    Track_Failure[32] == 0
elif Track_Failure[32] == 0 and Occupancy_In[32] == 1:
    Track_Failure[32] = 0
elif Occupancy_In[32] == 1 and Temp_Occupancy[71] == 0:
    Track_Failure[32] = 1
else:
    Track_Failure[32] = 0

if Occupancy_In[43] == 1 and Temp_Occupancy[66] == 1 and Track_Failure[43] == 0:
    Track_Failure[43] == 0
elif Track_Failure[43] == 0 and Occupancy_In[43] == 1:
    Track_Failure[43] = 0
elif Occupancy_In[43] == 1 and Temp_Occupancy[66] == 0:
    Track_Failure[43] = 1
else:
    Track_Failure[43] = 0

#Determines the speed and authority based on a failure      
for Failure_Check in range(15,73):
    if (Failure_Check >= 15 and Failure_Check <=47) or (Failure_Check >= 66  and Failure_Check <= 73):
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
    
if Track_Failure[2] == 1:
    Suggested_Speed[2] = "0"
    Suggested_Authority[2] = "0"
    Suggested_Speed[1] = "0"
    Suggested_Authority[1] = "0"
    Suggested_Speed[0] = "1010"
    Suggested_Speed[14] = "1111"
    Suggested_Speed[3] = "0"
    Suggested_Authority[3] = "0"
    Suggested_Speed[4] = "1010"
    Suggested_Speed[5] = "1111"

if Track_Failure[1] == 1:
    Suggested_Speed[1] = "0"
    Suggested_Authority[1] = "0"
    Suggested_Speed[0] = "0"
    Suggested_Authority[0] = "0"
    Suggested_Speed[14] = "1010"
    Suggested_Speed[15] = "1111"
    Suggested_Speed[2] = "0"
    Suggested_Authority[2] = "0"
    Suggested_Speed[3] = "1010"
    Suggested_Speed[4] = "1111"

if Track_Failure[0] == 1:
    Suggested_Speed[0] = "0"
    Suggested_Authority[0] = "0"
    Suggested_Speed[14] = "0"
    Suggested_Authority[14] = "0"
    Suggested_Speed[15] = "1010"
    Suggested_Speed[16] = "1111"
    Suggested_Speed[1] = "0"
    Suggested_Authority[1] = "0"
    Suggested_Speed[2] = "1010"
    Suggested_Speed[3] = "1111"

# Read PLC_OUTPUTS.jsons
try:
    with open("PLC_OUTPUTS2.json", "r") as file:
        outputs = json.load(file)
        Suggested_Speed_Out = outputs.get("Suggested_Speed", [])
        Suggested_Authority_Out = outputs.get("Suggested_Authority", [])
        Track_Failure_Out = outputs.get("Track_Failure", [])
        Light_Control_Out = outputs.get("Light_Control", [])
        Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
        Cross_Bar_Control_Out = outputs.get("Cross_Bar_Control", [])

    for i in range(76):
        if i <= 3 or i == 12 or i == 13:
            Light_Control[i] = Light_Control_Out[i]
        if i == 0 or i == 1 or i == 6:
            Actual_Switch_Position[i] = Actual_Switch_Position_Out[i]
        if i == 1:
            Cross_Bar_Control[i] = Cross_Bar_Control_Out[i]
        if (i >= 15 and i <=47) or (i >= 66  and i <= 75):
            if Suggested_Speed[i] != 100:
                Suggested_Speed_Out[i] = Suggested_Speed[i]
            if Suggested_Authority[i] != 100:
                Suggested_Authority_Out[i] = Suggested_Authority[i]
        else:
            Suggested_Speed[i] = Suggested_Speed_Out[i]
            Suggested_Authority[i] = Suggested_Authority_Out[i]
            Track_Failure[i] = Track_Failure_Out[i]

    outputs["Suggested_Speed"] = Suggested_Speed_Out
    outputs["Suggested_Authority"] = Suggested_Authority_Out
    outputs["Track_Failure"] = Track_Failure
    outputs["Light_Control"] = Light_Control
    outputs["Actual_Switch_Position"] = Actual_Switch_Position
    outputs["Cross_Bar_Control"] = Cross_Bar_Control_Out
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
