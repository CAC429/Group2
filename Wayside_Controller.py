import importlib
import PLC_Program_A_F  # Import the script
import PLC_Program_G_M  # Import the script
import PLC_Program_N_Q  # Import the script
import PLC_Program_R_Z  # Import the script
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import shutil
import importlib

Train_Bauds = ["1000000000"]*4
# Open and read the Input file
with open("PLC_INPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Suggested_Speed="):
            Suggested_Speed_In = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Suggested_Authority="):
            Suggested_Authority_In = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Occupancy="):
            Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Default_Switch_Position="):
            Default_Switch_In = list(map(int, line.strip().split("=")[1].split(",")))

# Open and read the Output file
with open("PLC_OUTPUTS.txt", "r") as file:
    for line in file:
        if line.startswith("Suggested_Speed="):
            Suggested_Speed_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Suggested_Authority="):
            Suggested_Authority_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Occupancy="):
            Occupancy_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Track_Failure="):
            Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Light_Control="):
            Light_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Actual_Switch_Position="):
            Actual_Switch_Position_Out = list(map(int, line.strip().split("=")[1].split(",")))
        elif line.startswith("Cross_Bar_Control="):
            Cross_Bar_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))

#This is the UI setup, has data driven arguments as well
class DataGridUI:
    def __init__(Self, Root):
        #Needed initializations
        Self.Root = Root
        Self.Root.title("Wayside Controller")
        Self.Test_Occupancy = [0] * 150

        #Initialize toggle variables
        Self.Toggled = False
        Self.Speed_Change = False
        Self.Authority_Change = False

        #Create Treeview (Table)
        Self.Tree = ttk.Treeview(Root, columns=("Block", "Lights", "Cross Bars", "Switch Position", "Suggested Speed", "Suggested Authority", "Track Failure", "Occupancy"), show="headings")
        Self.Tree.pack(fill="both", expand=True)

        #Define Column Headings
        Self.Tree.heading("Block", text="Block")
        Self.Tree.heading("Lights", text="Lights")
        Self.Tree.heading("Cross Bars", text="Cross Bars")
        Self.Tree.heading("Switch Position", text="Switch Position")
        Self.Tree.heading("Suggested Speed", text="Suggested Speed")
        Self.Tree.heading("Suggested Authority", text="Suggested Authority")
        Self.Tree.heading("Track Failure", text="Track Failure")
        Self.Tree.heading("Occupancy", text="Occupied?")

        #Define Column Widths
        Self.Tree.column("Block", width=100, anchor="center")
        Self.Tree.column("Lights", width=100, anchor="center")
        Self.Tree.column("Cross Bars", width=100, anchor="center")
        Self.Tree.column("Switch Position", width=100, anchor="center")
        Self.Tree.column("Suggested Speed", width=100, anchor="center")
        Self.Tree.column("Suggested Authority", width=100, anchor="center")
        Self.Tree.column("Track Failure", width=100, anchor="center")
        Self.Tree.column("Occupancy", width=100, anchor="center")

        #Add Block Toggle
        Self.Block_Selector = tk.Scale(Root, from_=1, to=150, orient="horizontal", length=700, width=20, sliderlength=30, font=("Arial", 14))
        Self.Block_Selector.pack(pady=10)
        Self.Block_Button = tk.Button(Root, text="Toggle Block", command=Self.Toggle_block, font=("Arial", 12))
        Self.Block_Button.pack(pady=10)

        #Create a StringVar for the default switch position
        Self.Default_Switch_Position = tk.StringVar()
        Self.Default_Switch_Position.set(f"Default Switch Position: {Default_Switch_In}")
        Self.Button_Label = tk.Label(Root, textvariable=Self.Default_Switch_Position)
        Self.Button_Label.pack(padx=10)

        #Create an entry widget (text box)
        Self.Speed_User_Input = tk.Entry(Root, width=30)
        Self.Speed_User_Input.pack(side="left", pady=10)
        Self.Speed_Submit_Button = tk.Button(Root, text=":Enter Block Speed", command=Self.Get_Speed_Input)
        Self.Speed_Submit_Button.pack(side="left", pady=10)
        Self.User_Speed = [""] * 150

        #Create an entry widget (text box)
        Self.Authority_User_Input = tk.Entry(Root, width=30)
        Self.Authority_User_Input.pack(side="right", pady=10)
        Self.Authority_Submit_Button = tk.Button(Root, text="Enter Block Authority:", command=Self.Get_Authority_Input)
        Self.Authority_Submit_Button.pack(side="right", pady=10)
        Self.User_Authority = [""] * 150

        #Get Initial Data
        Self.Update_UI()

    #Toggles block to on or off if the user presses the turn on block button
    def Toggle_block(Self):
        Self.Toggled = True
        Self.Test_Block = Self.Block_Selector.get()-1  #Get the selected block number
        if Self.Test_Occupancy[Self.Test_Block] == 0:
            Self.Test_Occupancy[Self.Test_Block] = 1
        elif Self.Test_Occupancy[Self.Test_Block] == 1:
            Self.Test_Occupancy[Self.Test_Block] = 0

    #Gets the speed the user inputs at the block they choose
    def Get_Speed_Input(Self):
        Self.Speed_Change = True
        Self.Test_Block = Self.Block_Selector.get()-1
        Self.User_Speed[Self.Test_Block] = Self.Speed_User_Input.get()

    #Gets the authority the user inputs at the block they choose
    def Get_Authority_Input(Self):
        Self.Authority_Change = True
        Self.Test_Block = Self.Block_Selector.get()-1
        Self.User_Authority[Self.Test_Block] = Self.Authority_User_Input.get()

    #Update the UI
    def Update_UI(Self):
        with open("PLC_OUTPUTS.txt", "r") as file:
            lines = file.readlines()  # Read all lines into a list

        # Parse the data
        for line in lines:
            if line.startswith("Suggested_Speed="):
                Suggested_Speed_Out = list(map(int, line.strip().split("=")[1].split(",")))
            elif line.startswith("Suggested_Authority="):
                Suggested_Authority_Out = list(map(int, line.strip().split("=")[1].split(",")))
            elif line.startswith("Occupancy="):
                Occupancy_Out = list(map(int, line.strip().split("=")[1].split(",")))
            elif line.startswith("Track_Failure="):
                Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))
        if (Occupancy_Out[0] == 1 and Track_Failure_Out[0] == 0 or (Occupancy_Out[0] == 1 and Occupancy_Out[1] == 1 and Track_Failure_Out[0] == 1 and Track_Failure_Out[1] == 0)) and Train_Bauds[0][0] == "1":
            Train_Bauds[0] = "0"+str(Suggested_Speed_Out[0])
        elif (Occupancy_Out[0] == 1 and Track_Failure_Out[0] == 0 or (Occupancy_Out[0] == 1 and Occupancy_Out[1] == 1 and Track_Failure_Out[0] == 1 and Track_Failure_Out[1] == 0)) and Train_Bauds[0][0] == "0":
            Train_Bauds[0] = "1"+str(Suggested_Authority_Out[0]+Suggested_Authority_Out[12])
        for i in range(1, 11):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[0][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[0] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[0] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[0][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == 0:
                        Train_Bauds[0] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1])[2:])
                    break
        for i in range(12, 28):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[0][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[0] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[0] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[0][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0:
                        Train_Bauds[0] = "1" + "0"
                    elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1])[2:])
                    elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1])[2:])
                    break
        for i in range(28, 57):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[1][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[1] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[1] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[1][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i+1] == 1:
                        Train_Bauds[1] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                            Train_Bauds[1] = "1" + "111111111"
                        else:
                            Train_Bauds[1] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    break
        for i in range(62, 76):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[1][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[1] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[1] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[1][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i+1] == 0:
                        Train_Bauds[1] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                            Train_Bauds[1] = "1" + "111111111"
                        else:
                            Train_Bauds[1] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    break
        for i in range(76, 85):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[2][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[2] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[2] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[2][0] == "0":  # Should only execute if the first if does not
                    if (Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0) and i != 76:
                        Train_Bauds[2] = "1" + "0"
                    elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[2] = "1" + "111111111"
                        else:
                            Train_Bauds[2] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1])[2:])
                    elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                            Train_Bauds[2] = "1" + "111111111"
                        else:
                            Train_Bauds[2] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[2] = "1" + "111111111"
                        else:
                            Train_Bauds[2] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1])[2:])
                    break
        for i in range(85, 100):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[2][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[2] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[2] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[2][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i+1] == 0:
                        Train_Bauds[2] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                            Train_Bauds[2] = "1" + "111111111"
                        else:
                            Train_Bauds[2] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    break
        for i in range(100, 149):
            if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                if Train_Bauds[3][0] == "1":
                    if Suggested_Speed_Out[i] == 1111 or Suggested_Speed_Out[i] == 1010:
                        Train_Bauds[3] = "0" + str(Suggested_Speed_Out[i])
                    else:
                        Train_Bauds[3] = "0" + str(bin(Suggested_Speed_Out[i])[2:])
                    break
                elif Train_Bauds[3][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i+1] == 0:
                        Train_Bauds[3] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                            Train_Bauds[3] = "1" + "111111111"
                        else:
                            Train_Bauds[3] = "1" + str(bin(Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1])[2:])
                    break

        # Open and read the Output file
        with open("PLC_INPUTS.txt", "r") as file:
            lines = file.readlines()  # Read all lines into a list
        # Modify the lines
        for i, line in enumerate(lines):
            if line.startswith("Train_Instance="):
                Train_Instance = list(map(int, line.strip().split("=")[1].split(",")))
        
        with open("PLC_OUTPUTS_Baud_Train_Instance.txt", "r") as file:
            lines = file.readlines()  # Read all lines into a list

        for i, line in enumerate(lines):
            if line.startswith("Train_Instance="):
                lines[i] = f"Train_Instance={','.join(map(str, Train_Instance))}\n"
            elif line.startswith("1-28-Baud1="):
                lines[i] = f"1-28-Baud1={','.join(map(str, Train_Bauds[0]))}\n"
            elif line.startswith("29-76-Baud2="):
                lines[i] = f"29-76-Baud2={','.join(map(str, Train_Bauds[1]))}\n"
            elif line.startswith("77-100-Baud3="):
                lines[i] = f"77-100-Baud3={','.join(map(str, Train_Bauds[2]))}\n"
            elif line.startswith("100-150-Baud4="):
                lines[i] = f"100-150-Baud4={','.join(map(str, Train_Bauds[3]))}\n"

        # **Write the modified lines back to the file**
        with open("PLC_OUTPUTS_Baud_Train_Instance.txt", "w") as file:
            file.writelines(lines)  # Ensure the updated content is written
            file.flush()  # Ensure data is written
            os.fsync(file.fileno())  # Finalize writing
        # Define file paths
        original_file = "PLC_OUTPUTS.txt"
        backup_file = "PLC_OUTPUTS_backup.txt"

        # Step 1: Backup the file (only if it exists and is not empty)
        if os.path.exists(original_file) and os.path.getsize(original_file) > 0:
            shutil.copy(original_file, backup_file)  # Make a backup

        # Step 2: Check if original file is empty or missing
        if not os.path.exists(original_file) or os.path.getsize(original_file) == 0:
            print("Original file is missing or empty. Restoring from backup...")
            if os.path.exists(backup_file):  # Ensure backup exists
                shutil.copy(backup_file, original_file)  # Restore from backup
            else:
                print("Backup file does not exist! Cannot restore data.")
        if os.path.getsize("PLC_INPUTS.txt") != 0:
            # Initialize lists correctly
            Suggested_Speed_In = [0] * 150
            Suggested_Authority_In = [0] * 150
            Occupancy_In = [0] * 150

            # Open and read the Input file
            with open("PLC_INPUTS.txt", "r") as file:
                for line in file:
                    if line.startswith("Suggested_Speed="):
                        Suggested_Speed_In = list(map(int, line.strip().split("=")[1].split(",")))
                    elif line.startswith("Suggested_Authority="):
                        Suggested_Authority_In = list(map(int, line.strip().split("=")[1].split(",")))
                    elif line.startswith("Occupancy="):
                        Occupancy_In = list(map(int, line.strip().split("=")[1].split(",")))

            if os.path.getsize("PLC_OUTPUTS.txt") != 0:
                # Open and read the Output file
                with open("PLC_OUTPUTS.txt", "r") as file:
                    lines = file.readlines()  # Read all lines into a list
                # Modify the lines
                for i, line in enumerate(lines):
                    if line.startswith("Suggested_Speed="):
                        lines[i] = f"Suggested_Speed={','.join(map(str, Suggested_Speed_In))}\n"
                    elif line.startswith("Suggested_Authority="):
                        lines[i] = f"Suggested_Authority={','.join(map(str, Suggested_Authority_In))}\n"

                # **Write the modified lines back to the file**
                with open("PLC_OUTPUTS.txt", "w") as file:
                    file.writelines(lines)  # Ensure the updated content is written
                    file.flush()  # Ensure data is written
                    os.fsync(file.fileno())  # Finalize writing

            if Self.Toggled == True:
                # Read the file
                with open("PLC_INPUTS.txt", "r") as file:
                    lines = file.readlines()

                Occupancy_In[Self.Test_Block] = Self.Test_Occupancy[Self.Test_Block]

                # Modify the lines
                for i, line in enumerate(lines):
                    if line.startswith("Occupancy="):
                        lines[i] = f"Occupancy={','.join(map(str, Occupancy_In))}\n"

                # Write the modified lines back to the file
                with open("PLC_INPUTS.txt", "w") as file:
                    file.writelines(lines)  # Writes the updated content back to the file
                    file.flush()  # Ensure data is written
                    os.fsync(file.fileno())  # Finalize writing

                Self.Toggled = False

            importlib.reload(PLC_Program_A_F)  # Reloads the module to apply updates
            importlib.reload(PLC_Program_G_M)  # Reloads the module to apply updates
            importlib.reload(PLC_Program_N_Q)  # Reloads the module to apply updates
            importlib.reload(PLC_Program_R_Z)  # Reloads the module to apply updates
            # Open and read the Output file
            # Read the file and store its content
            with open("PLC_OUTPUTS.txt", "r") as file:
                lines = file.readlines()  # Read all lines into a list

            # Parse the data
            for line in lines:
                if line.startswith("Suggested_Speed="):
                    Suggested_Speed_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Suggested_Authority="):
                    Suggested_Authority_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Occupancy="):
                    Occupancy_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Track_Failure="):
                    Track_Failure_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Light_Control="):
                    Light_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Actual_Switch_Position="):
                    Actual_Switch_Position_Out = list(map(int, line.strip().split("=")[1].split(",")))
                elif line.startswith("Cross_Bar_Control="):
                    Cross_Bar_Control_Out = list(map(int, line.strip().split("=")[1].split(",")))
            if Self.Speed_Change == True:
                Suggested_Speed_Out[Self.Test_Block] = Self.User_Speed[Self.Test_Block]
                Self.Speed_Change = False
            if Self.Authority_Change == True:
                Suggested_Authority_Out[Self.Test_Block] = Self.User_Authority[Self.Test_Block]
                Self.Speed_Change = False                

            # Modify the lines
            for i, line in enumerate(lines):
                if line.startswith("Suggested_Speed="):
                    lines[i] = f"Suggested_Speed={','.join(map(str, Suggested_Speed_Out))}\n"
                elif line.startswith("Suggested_Authority="):
                    lines[i] = f"Suggested_Authority={','.join(map(str, Suggested_Authority_Out))}\n"

            # Write the modified lines back to the file
            with open("PLC_OUTPUTS.txt", "w") as file:
                file.writelines(lines)  # Writes the updated content back to the file
                file.flush()  # Ensure data is written
                os.fsync(file.fileno())  # Finalize writing

            #Check if occupancy or user entered data has changed for user inputs or testbench(team combined code)
            New_Occupancy = [a | b for a, b in zip(Occupancy_In, Self.Test_Occupancy)] # Get updated occupancy

            # Update previous occupancy record
            Self.Prev_Occupancy = New_Occupancy[:]
            Self.Prev_User_Speed = Self.User_Speed[:]
            Self.Prev_User_Authority = Self.User_Authority[:]

            Self.Tree.delete(*Self.Tree.get_children())  # Clear existing table data

            # Define text colors for specific blocks
            Self.Tree.tag_configure("Green", foreground="green")  # Default green text
            Self.Tree.tag_configure("Orange", foreground="orange")  # Default orange text
            Self.Tree.tag_configure("Red", foreground="red")  # Default red text

            # Update UI values
            Self.occupancy_data = New_Occupancy
            if Suggested_Speed_Out != []:
                Binary_Temp_Speed = Suggested_Speed_Out
            if Suggested_Authority_Out != []:
                Binary_Temp_Authority = Suggested_Authority_Out
            Self.Cross_Bar = [""] * 150
            Self.Switch_Data = [""] * 150
            Self.Lights = [""] * 150
            Self.Switch_Data[11] = Actual_Switch_Position_Out[0]
            Self.Switch_Data[27] = Actual_Switch_Position_Out[1]
            Self.Switch_Data[57] = Actual_Switch_Position_Out[2]
            Self.Switch_Data[61] = Actual_Switch_Position_Out[3]
            Self.Switch_Data[75] = Actual_Switch_Position_Out[4]
            Self.Switch_Data[84] = Actual_Switch_Position_Out[5]
            Self.Cross_Bar[18] = Cross_Bar_Control_Out[0]
            Self.Cross_Bar[107] = Cross_Bar_Control_Out[1]
            Self.Lights[0] = Light_Control_Out[0]
            Self.Lights[11] = Light_Control_Out[1]
            Self.Lights[28] = Light_Control_Out[2]
            Self.Lights[149] = Light_Control_Out[3]
            Self.Lights[56] = Light_Control_Out[4]
            Self.Lights[57] = Light_Control_Out[5]
            Self.Lights[62] = Light_Control_Out[6]
            Self.Lights[61] = Light_Control_Out[7]
            Self.Lights[75] = Light_Control_Out[8]
            Self.Lights[100] = Light_Control_Out[9]
            Self.Lights[99] = Light_Control_Out[10]
            Self.Lights[85] = Light_Control_Out[11]
            Self.Failure = Track_Failure_Out  # Reset failures (Adjust logic if needed)
            # Convert binary speed to integer
            Temp_Speed = [1] * 150
            Temp_Authority = [1] * 150
            for Find_Failure in range(len(Track_Failure_Out)):
                if Binary_Temp_Speed[Find_Failure] == 1111:
                    Temp_Speed[Find_Failure] = 15
                elif Binary_Temp_Speed[Find_Failure] == 1010:
                    Temp_Speed[Find_Failure] = 10
                elif Binary_Temp_Speed[Find_Failure] == 0:
                    Temp_Speed[Find_Failure] = 0
                if Binary_Temp_Authority[Find_Failure] == 1111:
                    Temp_Authority[Find_Failure] = 15
                elif Binary_Temp_Authority[Find_Failure] == 1010:
                    Temp_Authority[Find_Failure] = 10
                elif Binary_Temp_Authority[Find_Failure] == 0:
                    Temp_Authority[Find_Failure] = 0

            for Combine in range(len(Occupancy_In)):
                if Temp_Speed[Combine] == 1:
                    Temp_Speed[Combine] = Suggested_Speed_In[Combine]
                if Temp_Authority[Combine] == 1:
                    Temp_Authority[Combine] = Suggested_Authority_In[Combine]

            #Integrate user inputed speed into the main speed
            for Find_Speed in range(len(Self.User_Speed)):
                if Self.User_Speed[Find_Speed] != "":
                    Temp_Speed[Find_Speed] = Self.User_Speed[Find_Speed]

            #Integrate user inputed authority into the main authority
            for Find_Authority in range(len(Self.User_Authority)):
                if Self.User_Authority[Find_Authority] != "":
                    Temp_Authority[Find_Authority] = Self.User_Authority[Find_Authority]

            Self.Speed_Data = Temp_Speed
            Self.Authority_Data = Temp_Authority

            # Insert rows with color tags
            for i in range(len(New_Occupancy)):
                Block_ID = i + 1  # Block IDs are 1-based
                Row_Tag = "Green"  # Default green text
                if New_Occupancy[i] == 1:
                    Row_Tag = "Orange"
                if Self.Failure[i] == 1:
                    Row_Tag = "Red"

                Self.Tree.insert("", "end", values=(
                    f"Block {Block_ID}",                    #Block ID
                    Self.Lights[i],                         #Lights
                    Self.Cross_Bar[i],                      #Cross Bar
                    Self.Switch_Data[i],                    #Switch Position
                    Self.Speed_Data[i],                     #Speed
                    Self.Authority_Data[i],                 #Authority
                    "Failure" if Self.Failure[i] else "",   #Failure
                    "Yes" if New_Occupancy[i] else "No"     #Occupancy status
                ), tags=(Row_Tag))                          #Apply text color tag

        #Re-run the function to check for updates periodically
        Self.Root.after(1000, Self.Update_UI)  #Check for updates every 500ms

#Start UI
if __name__ == "__main__":
    Root = tk.Tk()
    App = DataGridUI(Root)
    #Ensure PLC process stops when UI closes
    def on_closing():
        Root.destroy()  #Destroy the UI
    #Start background task
    Root.protocol("WM_DELETE_WINDOW", on_closing)  #Detect window close
    Root.mainloop()