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
#import global_variables
#import numpy as np
import json

Occupancy = [0] * 75
Cross_Bars = [0] * 2
Switch = [0] * 7
Light = [0] * 14
Suggested_Speed = [0] * 75
Suggested_Authority = [0] * 75
Failure = [0] * 75

#This is the UI setup, has data driven arguments as well
class DataGridUI:

    def __init__(Self, Root):
        #Needed initializations
        Self.Root = Root
        Self.Root.title("Wayside Controller")
        Self.Test_Occupancy = [0] * 75

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
        Self.Block_Selector = tk.Scale(Root, from_=1, to=75, orient="horizontal", length=700, width=20, sliderlength=30, font=("Arial", 14))
        Self.Block_Selector.pack(pady=10)
        Self.Block_Button = tk.Button(Root, text="Toggle Block", command=Self.Toggle_block, font=("Arial", 12))
        Self.Block_Button.pack(pady=10)

        #Create a StringVar for the default switch position
        Default_Switch_In = Switch
        Self.Default_Switch_Position = tk.StringVar()
        Self.Default_Switch_Position.set(f"Default Switch Position: {Default_Switch_In}")
        Self.Button_Label = tk.Label(Root, textvariable=Self.Default_Switch_Position)
        Self.Button_Label.pack(padx=10)

        #Create an entry widget (text box)
        Self.Speed_User_Input = tk.Entry(Root, width=30)
        Self.Speed_User_Input.pack(side="left", pady=10)
        Self.Speed_Submit_Button = tk.Button(Root, text=":Enter Block Speed", command=Self.Get_Speed_Input)
        Self.Speed_Submit_Button.pack(side="left", pady=10)
        Self.User_Speed = [""] * 75

        #Create an entry widget (text box)
        Self.Authority_User_Input = tk.Entry(Root, width=30)
        Self.Authority_User_Input.pack(side="right", pady=10)
        Self.Authority_Submit_Button = tk.Button(Root, text="Enter Block Authority:", command=Self.Get_Authority_Input)
        Self.Authority_Submit_Button.pack(side="right", pady=10)
        Self.User_Authority = [""] * 75

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

        New_Occupancy = Occupancy
        Self.Lights = [""] * 75
        Self.Cross_Bar = [""] * 75
        Self.Switch_Data = [""] * 75
        Self.Lights[8] = Light[0]
        Self.Lights[9] = Light[1]
        Self.Lights[0] = Light[2]
        Self.Lights[16] = Light[3]
        Self.Lights[25] = Light[4]
        Self.Lights[27] = Light[5]
        Self.Lights[31] = Light[6]
        Self.Lights[71] = Light[7]
        Self.Lights[38] = Light[8]
        Self.Lights[70] = Light[9]
        Self.Lights[42] = Light[10]
        Self.Lights[66] = Light[11]
        Self.Lights[52] = Light[12]
        Self.Lights[65] = Light[13]
        Self.Cross_Bar[10] = Cross_Bars[0]
        Self.Cross_Bar[46] = Cross_Bars[1]
        Self.Switch_Data[8] = Switch[0]
        Self.Switch_Data[14] = Switch[1]
        Self.Switch_Data[26] = Switch[2]
        Self.Switch_Data[32] = Switch[3]
        Self.Switch_Data[37] = Switch[4]
        Self.Switch_Data[42] = Switch[5]
        Self.Switch_Data[51] = Switch[6]
        Self.Speed_Data = Suggested_Speed
        Self.Authority_Data = Suggested_Authority
        Self.Failure = Failure

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