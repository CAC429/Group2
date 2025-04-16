import importlib
import PLC_Program2_A_E  # Import the script
import PLC_Program2_F_J  # Import the script
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import shutil
import importlib
#import global_variables
#import numpy as np
import json

Occupancy_In = [0] * 76
Cross_Bar_Control_Out = [0] * 2
Actual_Switch_Position_Out = [0] * 7
Light_Control_Out = [0] * 14
Suggested_Speed_Out = [0] * 76
Suggested_Authority_Out = [0] * 76
Track_Failure_Out = [0] * 76

#This is the UI setup, has data driven arguments as well
class DataGridUI:

    def __init__(Self, Root):
        #Needed initializations
        Self.Root = Root
        Self.Root.title("Wayside Controller")
        Self.Test_Occupancy = [0] * 76

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
        Self.Block_Selector = tk.Scale(Root, from_=1, to=76, orient="horizontal", length=700, width=20, sliderlength=30, font=("Arial", 14))
        Self.Block_Selector.pack(pady=10)
        Self.Block_Button = tk.Button(Root, text="Toggle Block", command=Self.Toggle_block, font=("Arial", 12))
        Self.Block_Button.pack(pady=10)

        #Create a StringVar for the default switch position
        Default_Switch_In = Actual_Switch_Position_Out
        Self.Default_Switch_Position = tk.StringVar()
        Self.Default_Switch_Position.set(f"Default Switch Position: {Default_Switch_In}")
        Self.Button_Label = tk.Label(Root, textvariable=Self.Default_Switch_Position)
        Self.Button_Label.pack(padx=10)

        #Create an entry widget (text box)
        Self.Speed_User_Input = tk.Entry(Root, width=30)
        Self.Speed_User_Input.pack(side="left", pady=10)
        Self.Speed_Submit_Button = tk.Button(Root, text=":Enter Block Speed", command=Self.Get_Speed_Input)
        Self.Speed_Submit_Button.pack(side="left", pady=10)
        Self.User_Speed = [""] * 76

        #Create an entry widget (text box)
        Self.Authority_User_Input = tk.Entry(Root, width=30)
        Self.Authority_User_Input.pack(side="right", pady=10)
        Self.Authority_Submit_Button = tk.Button(Root, text="Enter Block Authority:", command=Self.Get_Authority_Input)
        Self.Authority_Submit_Button.pack(side="right", pady=10)
        Self.User_Authority = [""] * 76

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
        Self.Tree.delete(*Self.Tree.get_children())
        # Define text colors for specific blocks
        Self.Tree.tag_configure("Green", foreground="green")  # Default green text
        Self.Tree.tag_configure("Orange", foreground="orange")  # Default orange text
        Self.Tree.tag_configure("Red", foreground="red")  # Default red text
        Self.Tree.tag_configure("Brown", foreground="brown")  # Default green text
        Self.Tree.tag_configure("Blue", foreground="blue")  # Default orange text
        Self.Tree.tag_configure("Purple", foreground="purple")  # Default red text
        # Initialize lists correctly
        Suggested_Speed_In = [0] * 76
        Suggested_Authority_In = [0] * 76
        Occupancy_In = [0] * 76
        # Read PLC_INPUTS.json
        try:
            with open("PLC_INPUTS2.json", "r") as file:
                inputs = json.load(file)
                Suggested_Speed_In = inputs.get("Suggested_Speed", [])
                Suggested_Authority_In = inputs.get("Suggested_Authority", [])
                Occupancy_In = inputs.get("Occupancy", [])
                Default_Switch_In = inputs.get("Default_Switch_Position", [])
                Train_Instance = inputs.get("Train_Instance")
        except FileNotFoundError:
            print("Error: PLC_INPUTS2.json not found! Please check the file path.")
        except Exception as e:
            print(f"Unexpected error in input file: {e}")

        if os.path.getsize("PLC_OUTPUTS2.json") != 0:
            # Read PLC_OUTPUTS.json
            try:
                with open("PLC_OUTPUTS2.json", "r") as file:
                    outputs = json.load(file)
                    Suggested_Speed_Out = outputs.get("Suggested_Speed", [])
                    Suggested_Authority_Out = outputs.get("Suggested_Authority", [])
                    Occupancy_Out = outputs.get("Occupancy", [])
                    Track_Failure_Out = outputs.get("Track_Failure", [])
                    Light_Control_Out = outputs.get("Light_Control", [])
                    Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
                    Cross_Bar_Control_Out = outputs.get("Cross_Bar_Control", [])
            except FileNotFoundError:
                print("Error: PLC_OUTPUTS2.json not found! Please check the file path.")
            except Exception as e:
                print(f"Unexpected error in output file: {e}")

            outputs = {
                "Suggested_Speed": Suggested_Speed_In,
                "Suggested_Authority": Suggested_Authority_In,
                "Occupancy": Occupancy_In,
                "Track_Failure": Track_Failure_Out,
                "Light_Control": Light_Control_Out,
                "Actual_Switch_Position": Actual_Switch_Position_Out,
                "Cross_Bar_Control": Cross_Bar_Control_Out
            }
            
            # Write to PLC_OUTPUTS.json
            try:
                with open("PLC_OUTPUTS2.json", "w") as file:
                    json.dump(outputs, file, indent=2)
            except FileNotFoundError:
                print("Error: PLC_OUTPUTS2.json not found! Please check the file path.")
            except Exception as e:
                print(f"Unexpected error while writing to output file: {e}")

        if Self.Toggled == True:
            # Read PLC_INPUTS.json
            try:
                with open("PLC_INPUTS2.json", "r") as file:
                    inputs = json.load(file)
                    Suggested_Speed_In = inputs.get("Suggested_Speed", [])
                    Suggested_Authority_In = inputs.get("Suggested_Authority", [])
                    Occupancy_In = inputs.get("Occupancy", [])
                    Default_Switch_In = inputs.get("Default_Switch_Position", [])
                    Train_Instance = inputs.get("Train_Instance")
            except FileNotFoundError:
                print("Error: PLC_INPUTS.json not found! Please check the file path.")
            except Exception as e:
                print(f"Unexpected error in input file: {e}")

            Occupancy_In[Self.Test_Block] = Self.Test_Occupancy[Self.Test_Block]

            # Prepare the data to write
            inputs = {
                "Suggested_Speed": Suggested_Speed_In,
                "Suggested_Authority": Suggested_Authority_In,
                "Occupancy": Occupancy_In,
                "Default_Switch_Position": Default_Switch_In,
                "Train_Instance": Train_Instance
            }

            # Write to PLC_INPUTS.json
            try:
                with open("PLC_INPUTS2.json", "w") as file:
                    json.dump(inputs, file, indent=4)
            except Exception as e:
                print(f"Unexpected error while writing to input file: {e}")

            Self.Toggled = False

        importlib.reload(PLC_Program2_A_E)
        importlib.reload(PLC_Program2_F_J)
        # Open and read the Output file
        # Read the file and store its content
        try:
        # Read PLC_OUTPUTS.json
            with open("PLC_OUTPUTS2.json", "r") as file:
                outputs = json.load(file)
                Suggested_Speed_Out = outputs.get("Suggested_Speed", [])
                Suggested_Authority_Out = outputs.get("Suggested_Authority", [])
                Occupancy_Out = outputs.get("Occupancy", [])
                Track_Failure_Out = outputs.get("Track_Failure", [])
                Light_Control_Out = outputs.get("Light_Control", [])
                Actual_Switch_Position_Out = outputs.get("Actual_Switch_Position", [])
                Cross_Bar_Control_Out = outputs.get("Cross_Bar_Control", [])
            if Self.Speed_Change == True:
                Suggested_Speed_Out[Self.Test_Block] = Self.User_Speed[Self.Test_Block]
                Self.Speed_Change = False
            if Self.Authority_Change == True:
                Suggested_Authority_Out[Self.Test_Block] = Self.User_Authority[Self.Test_Block]
                Self.Speed_Change = False                
        except FileNotFoundError:
            print("Error: File not found! Please check the file path.")
        except Exception as e:
            print(f"Unexpected Error: {e}")

        # Prepare the data to write
        outputs = {
            "Suggested_Speed": Suggested_Speed_In,
            "Suggested_Authority": Suggested_Authority_In,
            "Occupancy": Occupancy_Out,
            "Track_Failure": Track_Failure_Out,
            "Light_Control": Light_Control_Out,
            "Actual_Switch_Position": Actual_Switch_Position_Out,
            "Cross_Bar_Control": Cross_Bar_Control_Out
        }

        # Write to PLC_OUTPUTS.json
        try:
            with open("PLC_OUTPUTS2.json", "w") as file:
                json.dump(outputs, file, indent=2)
        except FileNotFoundError:
            print("Error: PLC_OUTPUTS2.json not found! Please check the file path.")
        except Exception as e:
            print(f"Unexpected error while writing to output file: {e}")

        #Check if occupancy or user entered data has changed for user inputs or testbench(team combined code)
        New_Occupancy = [a | b for a, b in zip(Occupancy_In, Self.Test_Occupancy)] # Get updated occupancy

        New_Occupancy = Occupancy_In
        # Update UI values
        Self.occupancy_data = New_Occupancy
        if Suggested_Speed_Out != []:
            Binary_Temp_Speed = Suggested_Speed_Out
        if Suggested_Authority_Out != []:
            Binary_Temp_Authority = Suggested_Authority_Out
        Self.Lights = [""] * 76
        Self.Cross_Bar = [""] * 76
        Self.Switch_Data = [""] * 76
        Self.Lights[8] = Light_Control_Out[0]
        Self.Lights[9] = Light_Control_Out[1]
        Self.Lights[0] = Light_Control_Out[2]
        Self.Lights[14] = Light_Control_Out[3]
        Self.Lights[75] = Light_Control_Out[4]
        Self.Lights[27] = Light_Control_Out[5]
        Self.Lights[31] = Light_Control_Out[6]
        Self.Lights[71] = Light_Control_Out[7]
        Self.Lights[70] = Light_Control_Out[8]
        Self.Lights[38] = Light_Control_Out[9]
        Self.Lights[42] = Light_Control_Out[10]
        Self.Lights[66] = Light_Control_Out[11]
        Self.Lights[52] = Light_Control_Out[12]
        Self.Lights[65] = Light_Control_Out[13]
        Self.Cross_Bar[10] = Cross_Bar_Control_Out[0]
        Self.Cross_Bar[46] = Cross_Bar_Control_Out[1]
        Self.Switch_Data[8] = Actual_Switch_Position_Out[0]
        Self.Switch_Data[14] = Actual_Switch_Position_Out[1]
        Self.Switch_Data[26] = Actual_Switch_Position_Out[2]
        Self.Switch_Data[32] = Actual_Switch_Position_Out[3]
        Self.Switch_Data[37] = Actual_Switch_Position_Out[4]
        Self.Switch_Data[42] = Actual_Switch_Position_Out[5]
        Self.Switch_Data[51] = Actual_Switch_Position_Out[6]
        Self.Failure = Track_Failure_Out
        # Convert binary speed to integer
        Temp_Speed = [1] * 76
        Temp_Authority = [1] * 76
        for Find_Failure in range(len(Track_Failure_Out)):
            if Binary_Temp_Speed[Find_Failure] == "1111":
                Temp_Speed[Find_Failure] = 15
            elif Binary_Temp_Speed[Find_Failure] == "1010":
                Temp_Speed[Find_Failure] = 10
            elif Binary_Temp_Speed[Find_Failure] == "0":
                Temp_Speed[Find_Failure] = 0
            if Binary_Temp_Authority[Find_Failure] == "1111":
                Temp_Authority[Find_Failure] = 15
            elif Binary_Temp_Authority[Find_Failure] == "1010":
                Temp_Authority[Find_Failure] = 10
            elif Binary_Temp_Authority[Find_Failure] == "0":
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

        Self.Speed_Data = [round(speed * 0.621371, 2) for speed in Temp_Speed]  
        Self.Authority_Data = [round(authority * 3.28084, 2) for authority in Temp_Authority]

        for i in range(len(New_Occupancy)):
            Block_ID = i + 1  # Block IDs are 1-based
            if i >= 0 and i <= 14:
                Row_Tag = "Green"  # Default green text
            elif (i >= 15 and i <=47) or (i >= 66  and i <= 75):
                Row_Tag = "Blue"  # Default green text
            else:
                Row_Tag = "Purple"  # Default green text
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