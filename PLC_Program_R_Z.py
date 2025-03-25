# Open and read the Input file
with open("PLC_INPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Occupancy="):
            # Extract values, split, and convert to integers
            Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Default_Switch_Position="):
            # Extract values, split, and convert to integers
            Default_Switch_In = list(map(int, line.strip().split("=")[1].split(",")))

# Open and read the Output file
with open("PLC_OUTPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Occupancy="):
            # Extract values, split, and convert to integers
            Occupancy_Out = list(map(int, line.strip().split("=")[1].split(",")))
        if line.startswith("Track_Failure="):
            # Extract values, split, and convert to integers
            Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))

#Initialize variables
Light_Control = [1] * 150
Actual_Switch_Position = [0] * 150
Suggested_Speed = [00] * 150
Suggested_Authority = [00] * 150
Track_Failure = Track_Failure_Out
Cross_Bar_Control = [0] * 2
Temp_Occupancy = Occupancy_Out

#Switch Control
if Temp_Occupancy[1] and Occupancy_In[0]:
    Actual_Switch_Position[0] = 1
elif Actual_Switch_Position[0] == 1:
    if Temp_Occupancy[0] != 1 and Occupancy_In[12] != 1:
        Actual_Switch_Position[0] = 0
else:
    Actual_Switch_Position[0] = Default_Switch_In

if Temp_Occupancy[148] and Occupancy_In[149]:
    Actual_Switch_Position[1] = 1
elif Actual_Switch_Position[1] == 1:
    if Temp_Occupancy[149] != 1 and Occupancy_In[27] != 1:
        Actual_Switch_Position[1] = 0
else:
    Actual_Switch_Position[1] = Default_Switch_In

Actual_Switch_Position[2] = 1

Actual_Switch_Position[3] = 1

if Temp_Occupancy[77] and Occupancy_In[76]:
    Actual_Switch_Position[4] = 1
elif Actual_Switch_Position[4] == 1:
    if Temp_Occupancy[76] != 1 and Occupancy_In[100] != 1:
        Actual_Switch_Position[4] = 0
else:
    Actual_Switch_Position[4] = Default_Switch_In

if Temp_Occupancy[98] and Occupancy_In[99]:
    Actual_Switch_Position[5] = 1
elif Actual_Switch_Position[5] == 1:
    if Temp_Occupancy[99] != 1 and Occupancy_In[84] != 1:
        Actual_Switch_Position[5] = 0
else:
    Actual_Switch_Position[5] = Default_Switch_In

#Cross Bar Control
Cross_Bar_Control[0] = 1 if any(Occupancy_In[i] for i in [17, 18, 19]) else 0
Cross_Bar_Control[1] = 1 if any(Occupancy_In[i] for i in [106, 107, 108]) else 0

#Detects the failures that occur
#General failure check for most cases

for i in range(len(Track_Failure)):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(0,149):
            if Occupancy_Check != {12,27,100,99,84}:
                if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                    Track_Failure[Occupancy_Check] = 0
                elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                    Track_Failure[Occupancy_Check] = 1
                else:
                    Track_Failure[Occupancy_Check] = 0

        if Occupancy_In[0] == 1 and Temp_Occupancy[0] == 1 and Track_Failure[0] == 0:
            Track_Failure[12] = 0
        elif Temp_Occupancy[1] == 0 and Temp_Occupancy[0] == 0 and Occupancy_In[0] == 1:
            Track_Failure[0] = 1

        if Occupancy_In[12] == 1 and Temp_Occupancy[12] == 1 and Track_Failure[12] == 0:
            Track_Failure[12] = 0
        elif Temp_Occupancy[11] == 0 and Temp_Occupancy[13] == 0 and Temp_Occupancy[0] == 0 and Occupancy_In[12] == 1 and Actual_Switch_Position[0] == 0:
            Track_Failure[12] = 1
        else:
            Track_Failure[12] = 0

        if Occupancy_In[27] == 1 and Temp_Occupancy[27] == 1 and Track_Failure[27] == 0:
            Track_Failure[27] = 0
        elif Temp_Occupancy[26] == 0 and Temp_Occupancy[28] == 0 and Temp_Occupancy[149] == 0 and Occupancy_In[27] == 1:
            Track_Failure[27] = 1
        else:
            Track_Failure[27] = 0

        if Occupancy_In[100] == 1 and Temp_Occupancy[100] == 1 and Track_Failure[100] == 0:
            Track_Failure[100] = 0
        elif Temp_Occupancy[76] == 0 and Temp_Occupancy[101] == 0 and Occupancy_In[100] == 1:
            Track_Failure[100] = 1
        else:
            Track_Failure[100] = 0

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

        if Occupancy_In[149] == 1 and Temp_Occupancy[149] == 1 and Track_Failure[149] == 0:
            Track_Failure[149] = 0
        elif Temp_Occupancy[148] == 0 and Temp_Occupancy[27] == 0 and Occupancy_In[149] == 1:
            Track_Failure[149] = 1
        else:
            Track_Failure[149] = 0

        if Occupancy_In[62] == 1:
            Track_Failure[62] = 0


#Determines the speed and authority based on a failure      
for Failure_Check in range(3, len(Track_Failure)-3):
    if Track_Failure[Failure_Check] == 1 and Failure_Check != 100 and Failure_Check != 101 and Failure_Check != 102 and Failure_Check != 99 and Failure_Check != 98 and Failure_Check != 97:
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

if Track_Failure[0] == 1:
    Suggested_Speed[0] = "0"
    Suggested_Authority[0] = "0"
    Suggested_Speed[1] = "0"
    Suggested_Speed[2] = "1010"
    Suggested_Speed[3] = "1111"

if Track_Failure[1] == 1:
    Suggested_Speed[1] = "0"
    Suggested_Authority[1] = "0"
    Suggested_Speed[0] = "0"
    Suggested_Authority[0] = "0"
    Suggested_Speed[2] = "0"
    Suggested_Authority[2] = "0"
    Suggested_Speed[3] = "1010"
    Suggested_Speed[4] = "1111"

if Track_Failure[2] == 1:
    Suggested_Speed[2] = "0"
    Suggested_Authority[2] = "0"
    Suggested_Speed[1] = "0"
    Suggested_Authority[1] = "0"
    Suggested_Speed[3] = "0"
    Suggested_Authority[3] = "0"
    Suggested_Speed[0] = "1010"
    Suggested_Speed[4] = "1010"
    Suggested_Speed[5] = "1111"

if Track_Failure[10] == 1:
    Suggested_Speed[0] = "1111"

if Track_Failure[11] == 1:
    Suggested_Speed[0] = "1010"
    Suggested_Speed[1] = "1111"

if Track_Failure[12] == 1:
    Suggested_Speed[0] = "0"
    Suggested_Authority[0] = "0"
    Suggested_Speed[1] = "1010"
    Suggested_Speed[2] = "1111"

if Track_Failure[13] == 1:
    Suggested_Speed[0] = "1010"
    Suggested_Speed[1] = "1111"

if Track_Failure[14] == 1:
    Suggested_Speed[0] = "1111"

if Track_Failure[29] == 1:
    Suggested_Speed[149] = "1111"

if Track_Failure[28] == 1:
    Suggested_Speed[149] = "1010"
    Suggested_Speed[148] = "1111"

if Track_Failure[27] == 1:
    Suggested_Speed[149] = "0"
    Suggested_Authority[149] = "0"
    Suggested_Speed[148] = "1010"
    Suggested_Speed[147] = "1111"

if Track_Failure[26] == 1:
    Suggested_Speed[149] = "1010"
    Suggested_Speed[148] = "1111"

if Track_Failure[25] == 1:
    Suggested_Speed[149] = "1111"

if Track_Failure[100] == 1:
    Suggested_Speed[100] = "0"
    Suggested_Authority[100] = "0"
    Suggested_Speed[101] = "0"
    Suggested_Authority[101] = "0"
    Suggested_Speed[102] = "1010"
    Suggested_Speed[103] = "1111"
    Suggested_Speed[76] = "0"
    Suggested_Authority[76] = "0"
    Suggested_Speed[77] = "1010"
    Suggested_Speed[78] = "1111"

if Track_Failure[101] == 1:
    Suggested_Speed[101] = "0"
    Suggested_Authority[101] = "0"
    Suggested_Speed[102] = "0"
    Suggested_Authority[102] = "0"
    Suggested_Speed[103] = "1010"
    Suggested_Speed[104] = "1111"
    Suggested_Speed[100] = "0"
    Suggested_Authority[100] = "0"
    Suggested_Speed[76] = "1010"
    Suggested_Speed[77] = "1111"

if Track_Failure[102] == 1:
    Suggested_Speed[102] = "0"
    Suggested_Authority[102] = "0"
    Suggested_Speed[103] = "0"
    Suggested_Authority[103] = "0"
    Suggested_Speed[104] = "1010"
    Suggested_Speed[105] = "1111"
    Suggested_Speed[101] = "0"
    Suggested_Authority[101] = "0"
    Suggested_Speed[100] = "1010"
    Suggested_Speed[76] = "1111"

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

if Track_Failure[149] == 1:
    Suggested_Speed[149] = "0"
    Suggested_Authority[149] = "0"
    Suggested_Speed[148] = "0"
    Suggested_Authority[148] = "0"
    Suggested_Speed[147] = "1010"
    Suggested_Speed[146] = "1111"

if Track_Failure[148] == 1:
    Suggested_Speed[149] = "0"
    Suggested_Authority[149] = "0"
    Suggested_Speed[148] = "0"
    Suggested_Authority[148] = "0"
    Suggested_Speed[147] = "0"
    Suggested_Authority[147] = "0"
    Suggested_Speed[146] = "1010"
    Suggested_Speed[145] = "1111"

if Track_Failure[147] == 1:
    Suggested_Speed[149] = "0"
    Suggested_Authority[149] = "0"
    Suggested_Speed[148] = "0"
    Suggested_Authority[148] = "0"
    Suggested_Speed[147] = "0"
    Suggested_Authority[147] = "0"
    Suggested_Speed[146] = "1010"
    Suggested_Speed[145] = "1111"

#Light Control
for Occupancy_Check in range (len(Occupancy_In)):
    if Occupancy_In[Occupancy_Check] or Suggested_Authority[Occupancy_Check] == 0:
        Light_Control[Occupancy_Check] = 0
    else:
        Light_Control[Occupancy_Check] = 1

# Read the file
with open("PLC_OUTPUTS.txt", "r") as file:
    lines = file.readlines()

# Modify the lines
for i, line in enumerate(lines):
    if line.startswith("Suggested_Speed="):
        lines[i] = f"Suggested_Speed={','.join(map(str, Suggested_Speed))}\n"
    elif line.startswith("Suggested_Authority="):
        lines[i] = f"Suggested_Authority={','.join(map(str, Suggested_Authority))}\n"
    elif line.startswith("Occupancy="):
        lines[i] = f"Occupancy={','.join(map(str, Occupancy_In))}\n"
    elif line.startswith("Track_Failure="):
        lines[i] = f"Track_Failure={','.join(map(str, Track_Failure))}\n"
    elif line.startswith("Light_Control="):
        lines[i] = f"Light_Control={','.join(map(str, Light_Control))}\n"
    elif line.startswith("Actual_Switch_Position=") and i < 5:
        lines[i] = f"Actual_Switch_Position={','.join(map(str, Actual_Switch_Position))}\n"
    elif line.startswith("Cross_Bar_Control=") and i < 5:
        lines[i] = f"Cross_Bar_Control={','.join(map(str, Cross_Bar_Control))}\n"

# Write the modified lines back to the file
with open("PLC_OUTPUTS.txt", "w") as file:
    file.writelines(lines)  # Writes the updated content back to the file
