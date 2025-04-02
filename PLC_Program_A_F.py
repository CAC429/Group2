import os
# Open and read the Input file
Occupancy_In = [0] * 150
Default_Switch_In = [0] * 6
with open("PLC_INPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Occupancy="):
            # Extract values, split, and convert to integers
            Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Default_Switch_Position="):
            # Extract values, split, and convert to integers
            Default_Switch_In = list(map(int, line.strip().split("=")[1].split(",")))

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
        elif line.startswith("Actual_Switch_Position="):
            # Extract values, split, and convert to integers
            Actual_Switch_Position_Out = list(map(int, line.strip().split("=")[1].split(",")))

#Initialize variables
Light_Control = [0] * 12
Actual_Switch_Position = Actual_Switch_Position_Out
Suggested_Speed = [100] * 150
Suggested_Authority = [100] * 150
Track_Failure = Track_Failure_Out
Cross_Bar_Control = [0] * 2
Temp_Occupancy = Occupancy_Out

#Switch Control and Light Control
if Occupancy_In[1] == 1 and Occupancy_In[2] == 1:
    Actual_Switch_Position[0] = 1
    Light_Control[0] = 1
    Light_Control[1] = 0
elif Actual_Switch_Position[0] == 1 and (Occupancy_In[1] == 1 or Occupancy_In[0] == 1):
    Actual_Switch_Position[0] = 1
    Light_Control[0] = 1
    Light_Control[1] = 0
else:
    Actual_Switch_Position[0] = 0
    Light_Control[0] = 0
    Light_Control[1] = 1

if Occupancy_In[25] == 1 and Occupancy_In[26] == 1:
    Actual_Switch_Position[1] = 0
    Light_Control[2] = 1
    Light_Control[3] = 0
elif Actual_Switch_Position[1] == 0 and (Occupancy_In[26] == 1 or Occupancy_In[27] == 1):
    Actual_Switch_Position[1] = 0
    Light_Control[2] = 1
    Light_Control[3] = 0
else:
    Actual_Switch_Position[1] = 1
    Light_Control[2] = 0
    Light_Control[3] = 1

#Cross Bar Control
Cross_Bar_Control[0] = 1 if any(Occupancy_In[i] for i in [17, 18, 19]) else 0

#Detects the failures that occur
#General failure check for most cases
for i in range(28):
    if Track_Failure[i] != 1 and Occupancy_In[i] != 1:

        for Occupancy_Check in range(0,28):
            if Occupancy_Check != {12,27}:
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

#Determines the speed and authority based on a failure      
for Failure_Check in range(3, 28):
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

Find_Occupancy = 0
for i in range(28):
    if Occupancy_In[i] == 1:
        Find_Occupancy = 1
if Find_Occupancy > 0:
    Suggested_Speed[149] = "0"
    Suggested_Speed[148] = "1010"
    Suggested_Speed[147] = "1111"
    Suggested_Authority[149] = "0"

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

for i in range(150):
    if i > 3 and i < 12:
        Light_Control[i] = Light_Control_Out[i]
    if i > 1 and i < 6:
        Actual_Switch_Position[i] = Actual_Switch_Position_Out[i]
    if i == 1:
        Cross_Bar_Control[i] = Cross_Bar_Control_Out[i]
    if i > 27 and i != 149 and i != 148 and i != 147:
        Suggested_Speed[i] = Suggested_Speed_Out[i]
        Suggested_Authority[i] = Suggested_Authority_Out[i]
        Track_Failure[i] = Track_Failure_Out[i]
    if i <= 27 or i == 149 or i == 148 or i == 147:
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
    elif line.startswith("Track_Failure="):
        lines[i] = f"Track_Failure={','.join(map(str, Track_Failure))}\n"
    elif line.startswith("Light_Control="):
        lines[i] = f"Light_Control={','.join(map(str, Light_Control))}\n"
    elif line.startswith("Actual_Switch_Position="):
        lines[i] = f"Actual_Switch_Position={','.join(map(str, Actual_Switch_Position))}\n"
    elif line.startswith("Cross_Bar_Control="):
        lines[i] = f"Cross_Bar_Control={','.join(map(str, Cross_Bar_Control))}\n"

# Write the modified lines back to the file
with open("PLC_OUTPUTS.txt", "w") as file:
    file.writelines(lines)  # Writes the updated content back to the file
    file.flush()  # Ensure data is written
    os.fsync(file.fileno())  # Finalize writing