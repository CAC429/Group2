import os
# Open and read the Input file
Occupancy_In = [0] * 150
Default_Switch_In = [0] * 6
with open("PLC_INPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Occupancy="):
            # Extract values, split, and convert to integers
            Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))

Occupancy_Out = [0] * 150
Track_Failure_Out = [0] * 150
Actual_Switch_Position_Out = [0] * 6
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
Light_Control = [0] * 12
Suggested_Speed = [100] * 150
Suggested_Authority = [100] * 150
Track_Failure = Track_Failure_Out
Cross_Bar_Control = [0] * 2
Temp_Occupancy = Occupancy_Out

#Cross Bar Control
Cross_Bar_Control[1] = 1 if any(Occupancy_In[i] for i in [106, 107, 108]) else 0

#Detects the failures that occur
#General failure check for most cases

for i in range(100,150):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(100,147):
            if Occupancy_Check != {100}:
                if Occupancy_In[Occupancy_Check] == 1 and Temp_Occupancy[Occupancy_Check] == 1 and Track_Failure[Occupancy_Check] == 0:
                    Track_Failure[Occupancy_Check] = 0
                elif Temp_Occupancy[Occupancy_Check-1] == 0 and Temp_Occupancy[Occupancy_Check+1] == 0 and Occupancy_In[Occupancy_Check] == 1:
                    Track_Failure[Occupancy_Check] = 1
                else:
                    Track_Failure[Occupancy_Check] = 0

        if Occupancy_In[100] == 1 and Temp_Occupancy[100] == 1 and Track_Failure[100] == 0:
            Track_Failure[100] = 0
        elif Temp_Occupancy[76] == 0 and Temp_Occupancy[101] == 0 and Occupancy_In[100] == 1:
            Track_Failure[100] = 1
        else:
            Track_Failure[100] = 0

        if Occupancy_In[147] == 1 and Temp_Occupancy[147] == 1 and Track_Failure[147] == 0:
            Track_Failure[147] = 0
        elif Temp_Occupancy[146] == 0 and Temp_Occupancy[148] == 0 and Occupancy_In[147] == 1:
            Track_Failure[147] = 1
        else:
            Track_Failure[147] = 0

        if Occupancy_In[148] == 1 and Temp_Occupancy[148] == 1 and Track_Failure[148] == 0:
            Track_Failure[148] = 0
        elif Temp_Occupancy[147] == 0 and Temp_Occupancy[149] == 0 and Occupancy_In[148] == 1:
            Track_Failure[148] = 1
        else:
            Track_Failure[148] = 0

        if Occupancy_In[149] == 1 and Temp_Occupancy[149] == 1 and Track_Failure[149] == 0:
            Track_Failure[149] = 0
        elif Temp_Occupancy[148] == 0 and Temp_Occupancy[27] == 0 and Occupancy_In[149] == 1:
            Track_Failure[149] = 1
        else:
            Track_Failure[149] = 0

#Determines the speed and authority based on a failure      
for Failure_Check in range(100,147):
    if Track_Failure[Failure_Check] == 1 and Failure_Check != 100 and Failure_Check != 101 and Failure_Check != 102:
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

# Read the file
with open("PLC_OUTPUTS.txt", "r") as file:
    lines = file.readlines()  # Read all lines into a list

# Parse the data
for line in lines:
    if line.startswith("Suggested_Speed="):
        Suggested_Speed_Out = list(map(int, line.strip().split("=")[1].split(",")))
    elif line.startswith("Suggested_Authority="):
        Suggested_Authority_Out = list(map(int, line.strip().split("=")[1].split(",")))
    elif line.startswith("Track_Failure="):
        Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))
    elif line.startswith("Light_Control="):
        Light_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))
    elif line.startswith("Actual_Switch_Position="):
        Actual_Switch_Position_Out = list(map(int, line.strip().split("=")[1].split(",")))
    elif line.startswith("Cross_Bar_Control="):
        Cross_Bar_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))

Find_Occupancy = 0
for i in range(100,150):
    if Occupancy_In[i] == 1:
        Find_Occupancy = 1
if Find_Occupancy > 0:
    Suggested_Speed[99] = "0"
    Suggested_Speed[98] = "1010"
    Suggested_Speed[97] = "1111"
    Suggested_Authority[99] = "0"

for i in range(150):
    if i == 0:
        Cross_Bar_Control[i] = Cross_Bar_Control_Out[i]
    if i < 97:
        Suggested_Speed[i] = Suggested_Speed_Out[i]
        Suggested_Authority[i] = Suggested_Authority_Out[i]
        Track_Failure[i] = Track_Failure_Out[i]
    if i >= 97:
        if Suggested_Speed[i] != 100:
            Suggested_Speed_Out[i] = Suggested_Speed[i]
        if Suggested_Authority[i] != 100:
            Suggested_Authority_Out[i] = Suggested_Authority[i]

# Modify the lines
for i, line in enumerate(lines):
    if line.startswith("Suggested_Speed="):
        lines[i] = f"Suggested_Speed={','.join(map(str, Suggested_Speed_Out))}\n"
    elif line.startswith("Suggested_Authority="):
        lines[i] = f"Suggested_Authority={','.join(map(str, Suggested_Authority_Out))}\n"
    elif line.startswith("Occupancy="):
        lines[i] = f"Occupancy={','.join(map(str, Occupancy_In))}\n"
    elif line.startswith("Track_Failure="):
        lines[i] = f"Track_Failure={','.join(map(str, Track_Failure))}\n"
    elif line.startswith("Cross_Bar_Control="):
        lines[i] = f"Cross_Bar_Control={','.join(map(str, Cross_Bar_Control))}\n"

# Write the modified lines back to the file
with open("PLC_OUTPUTS.txt", "w") as file:
    file.writelines(lines)  # Writes the updated content back to the file
    file.flush()  # Ensure data is written
    os.fsync(file.fileno())  # Finalize writing