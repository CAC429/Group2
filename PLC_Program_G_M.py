import os
# Open and read the Input file
Occupancy_In = [0] * 150
Default_Switch_In = [0] * 6
try:
    with open("PLC_INPUTS.txt", "r") as file:
        for line in file:
            if line.startswith("Occupancy="):
                # Extract values, split, and convert to integers
                Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))
            elif line.startswith("Default_Switch_Position="):
                # Extract values, split, and convert to integers
                Default_Switch_In = list(map(int, line.strip().split("=")[1].split(",")))
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")

Occupancy_Out = [0] * 150
Track_Failure_Out = [0] * 150
Actual_Switch_Position_Out = [0] * 6
# Open and read the Output file

try:
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
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")

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
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")

try:
    # Write the modified lines back to the file
    with open("PLC_OUTPUTS.txt", "w") as file:
        file.writelines(lines)  # Writes the updated content back to the file
        file.flush()  # Ensure data is written
        os.fsync(file.fileno())  # Finalize writing
except FileNotFoundError:
    print("Error: File not found! Please check the file path.")
except Exception as e:
    print(f"Unexpected Error: {e}")