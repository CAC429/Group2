import importlib
import PLC_Program2_A_E  # Import the script
import PLC_Program2_F_J  # Import the script
import PLC_Program_J_N  # Import the script
import tkinter as tk
from tkinter import ttk
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
Train_Bauds = ["1000000000"]*8

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
        # All Baud Functionallity
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

            #0
            if ((Occupancy_Out[0] == 1 and Track_Failure_Out[0] == 0) or 
                (Occupancy_Out[0] == 1 and Occupancy_Out[1] == 1 and Track_Failure_Out[1] == 1 and Track_Failure_Out[0] == 0) or
                (Occupancy_Out[0] == 1 and Occupancy_Out[15] == 1 and Track_Failure_Out[15] == 1 and Track_Failure_Out[0] == 0)):
                if Train_Bauds[0][0] == "1":
                    if Suggested_Speed_Out[0] == "1111" or Suggested_Speed_Out[0] == "1010" or Suggested_Speed_Out[0] == "0":
                        Train_Bauds[0] = "0" + str(Suggested_Speed_Out[0])
                    else:
                        Train_Bauds[0] = "0" + str(bin(int(Suggested_Speed_Out[0]))[2:])
                elif Train_Bauds[0][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[15] == 0 or Suggested_Authority_Out[1] == 0 or Suggested_Authority_Out[0] == 0 or Suggested_Authority_Out[15] == "0" or Suggested_Authority_Out[1] == "0" or Suggested_Authority_Out[0] == "0":
                        Train_Bauds[0] = "1" + "0"
                    elif Suggested_Authority_Out[15] < Suggested_Authority_Out[1]:
                        if Suggested_Authority_Out[0] + Suggested_Authority_Out[15] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[0]) + int(Suggested_Authority_Out[15]))[2:])
                    elif Suggested_Authority_Out[15] > Suggested_Authority_Out[1]:
                        if Suggested_Authority_Out[0] + Suggested_Authority_Out[1] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[0]) + int(Suggested_Authority_Out[1]))[2:])
                    else:
                        if Suggested_Authority_Out[0] + Suggested_Authority_Out[15] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[0]) + int(Suggested_Authority_Out[15]))[2:])
            #15
            if ((Occupancy_Out[15] == 1 and Track_Failure_Out[15] == 0) or 
                (Occupancy_Out[15] == 1 and Occupancy_Out[0] == 1 and Track_Failure_Out[0] == 1 and Track_Failure_Out[15] == 0) or
                (Occupancy_Out[15] == 1 and Occupancy_Out[16] == 1 and Track_Failure_Out[16] == 1 and Track_Failure_Out[15] == 0)):
                if Train_Bauds[0][0] == "1":
                    if Suggested_Speed_Out[15] == "1111" or Suggested_Speed_Out[15] == "1010" or Suggested_Speed_Out[15] == "0":
                        Train_Bauds[0] = "0" + str(Suggested_Speed_Out[15])
                    else:
                        Train_Bauds[0] = "0" + str(bin(int(Suggested_Speed_Out[15]))[2:])
                elif Train_Bauds[0][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[16] == 0 or Suggested_Authority_Out[0] == 0 or Suggested_Authority_Out[15] == 0 or Suggested_Authority_Out[16] == "0" or Suggested_Authority_Out[0] == "0" or Suggested_Authority_Out[15] == "0":
                        Train_Bauds[0] = "1" + "0"
                    elif Suggested_Authority_Out[16] < Suggested_Authority_Out[0]:
                        if Suggested_Authority_Out[15] + Suggested_Authority_Out[16] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[15]) + int(Suggested_Authority_Out[16]))[2:])
                    elif Suggested_Authority_Out[16] > Suggested_Authority_Out[0]:
                        if Suggested_Authority_Out[15] + Suggested_Authority_Out[0] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[15]) + int(Suggested_Authority_Out[0]))[2:])
                    else:
                        if Suggested_Authority_Out[15] + Suggested_Authority_Out[0] > 511:
                            Train_Bauds[0] = "1" + "111111111"
                        else:
                            Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[15]) + int(Suggested_Authority_Out[16]))[2:])

            for i in list(range(1, 9)) + list(range(16, 27)):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[0][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[0] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[0] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[0][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[0] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[0] = "1" + "111111111"
                            else:
                                Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[0] = "1" + "111111111"
                            else:
                                Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[0] = "1" + "111111111"
                            else:
                                Train_Bauds[0] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break
           
            #71 and 75
            if ((Occupancy_Out[71] == 1 and Track_Failure_Out[71] == 0) or 
                (Occupancy_Out[71] == 1 and Occupancy_Out[32] == 1 and Track_Failure_Out[32] == 1 and Track_Failure_Out[71] == 0)):
                if Train_Bauds[1][0] == "1":
                    if Suggested_Speed_Out[71] == "1111" or Suggested_Speed_Out[71] == "1010" or Suggested_Speed_Out[71] == "0":
                        Train_Bauds[1] = "0" + str(Suggested_Speed_Out[71])
                    else:
                        Train_Bauds[1] = "0" + str(bin(int(Suggested_Speed_Out[71]))[2:])
                elif Train_Bauds[1][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[71] == 0 or Suggested_Authority_Out[32] == 0 or Suggested_Authority_Out[71] == "0" or Suggested_Authority_Out[32] == "0":
                        Train_Bauds[1] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[71] + Suggested_Authority_Out[32] > 511:
                            Train_Bauds[1] = "1" + "111111111"
                        else:
                            Train_Bauds[1] = "1" + str(bin(int(Suggested_Authority_Out[71]) + int(Suggested_Authority_Out[32]))[2:])

            if ((Occupancy_Out[75] == 1 and Track_Failure_Out[75] == 0) or 
                (Occupancy_Out[75] == 1 and Occupancy_Out[74] == 1 and Track_Failure_Out[74] == 1 and Track_Failure_Out[75] == 0)):
                if Train_Bauds[1][0] == "1":
                    if Suggested_Speed_Out[75] == "1111" or Suggested_Speed_Out[75] == "1010" or Suggested_Speed_Out[75] == "0":
                        Train_Bauds[1] = "0" + str(Suggested_Speed_Out[75])
                    else:
                        Train_Bauds[1] = "0" + str(bin(int(Suggested_Speed_Out[75]))[2:])
                elif Train_Bauds[1][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[75] == 0 or Suggested_Authority_Out[74] == 0 or Suggested_Authority_Out[75] == "0" or Suggested_Authority_Out[74] == "0":
                        Train_Bauds[1] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[75] + Suggested_Authority_Out[74] > 511:
                            Train_Bauds[1] = "1" + "111111111"
                        else:
                            Train_Bauds[1] = "1" + str(bin(int(Suggested_Authority_Out[75]) + int(Suggested_Authority_Out[74]))[2:])

            for i in range(72, 75):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[1][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[1] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[1] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[1][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[1] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[1] = "1" + "111111111"
                            else:
                                Train_Bauds[1] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[1] = "1" + "111111111"
                            else:
                                Train_Bauds[1] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[1] = "1" + "111111111"
                            else:
                                Train_Bauds[1] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

            for i in range(27, 33):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[2][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[2] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[2] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[2][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[2] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[2] = "1" + "111111111"
                            else:
                                Train_Bauds[2] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[2] = "1" + "111111111"
                            else:
                                Train_Bauds[2] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[2] = "1" + "111111111"
                            else:
                                Train_Bauds[2] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

            for i in range(33, 38):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[3][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[3] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[3] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[3][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[3] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[3] = "1" + "111111111"
                            else:
                                Train_Bauds[3] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[3] = "1" + "111111111"
                            else:
                                Train_Bauds[3] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[3] = "1" + "111111111"
                            else:
                                Train_Bauds[3] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break
            
            #66 and 70
            if ((Occupancy_Out[66] == 1 and Track_Failure_Out[66] == 0) or 
                (Occupancy_Out[66] == 1 and Occupancy_Out[43] == 1 and Track_Failure_Out[43] == 1 and Track_Failure_Out[66] == 0)):
                if Train_Bauds[4][0] == "1":
                    if Suggested_Speed_Out[66] == "1111" or Suggested_Speed_Out[66] == "1010" or Suggested_Speed_Out[66] == "0":
                        Train_Bauds[4] = "0" + str(Suggested_Speed_Out[66])
                    else:
                        Train_Bauds[4] = "0" + str(bin(int(Suggested_Speed_Out[66]))[2:])
                elif Train_Bauds[4][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[66] == 0 or Suggested_Authority_Out[43] == 0 or Suggested_Authority_Out[66] == "0" or Suggested_Authority_Out[43] == "0":
                        Train_Bauds[4] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[66] + Suggested_Authority_Out[43] > 511:
                            Train_Bauds[4] = "1" + "111111111"
                        else:
                            Train_Bauds[4] = "1" + str(bin(int(Suggested_Authority_Out[66]) + int(Suggested_Authority_Out[43]))[2:])

            if ((Occupancy_Out[70] == 1 and Track_Failure_Out[70] == 0) or 
                (Occupancy_Out[70] == 1 and Occupancy_Out[37] == 1 and Track_Failure_Out[37] == 1 and Track_Failure_Out[70] == 0)):
                if Train_Bauds[4][0] == "1":
                    if Suggested_Speed_Out[70] == "1111" or Suggested_Speed_Out[70] == "1010" or Suggested_Speed_Out[70] == "0":
                        Train_Bauds[4] = "0" + str(Suggested_Speed_Out[70])
                    else:
                        Train_Bauds[4] = "0" + str(bin(int(Suggested_Speed_Out[70]))[2:])
                elif Train_Bauds[4][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[70] == 0 or Suggested_Authority_Out[37] == 0 or Suggested_Authority_Out[70] == "0" or Suggested_Authority_Out[37] == "0":
                        Train_Bauds[4] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[70] + Suggested_Authority_Out[37] > 511:
                            Train_Bauds[4] = "1" + "111111111"
                        else:
                            Train_Bauds[4] = "1" + str(bin(int(Suggested_Authority_Out[70]) + int(Suggested_Authority_Out[37]))[2:])

            for i in range(67, 70):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[4][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[4] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[4] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[4][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[4] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[4] = "1" + "111111111"
                            else:
                                Train_Bauds[4] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[4] = "1" + "111111111"
                            else:
                                Train_Bauds[4] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[4] = "1" + "111111111"
                            else:
                                Train_Bauds[4] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

            for i in range(38, 44):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[5][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[5] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[5] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[5][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[5] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[5] = "1" + "111111111"
                            else:
                                Train_Bauds[5] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[5] = "1" + "111111111"
                            else:
                                Train_Bauds[5] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[5] = "1" + "111111111"
                            else:
                                Train_Bauds[5] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

            for i in range(44, 52):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0) or
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i-1] == 1 and Track_Failure_Out[i-1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[6][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[6] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[6] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[6][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i+1] == 0 or Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == "0" or Suggested_Authority_Out[i+1] == "0" or Suggested_Authority_Out[i] == "0":
                            Train_Bauds[6] = "1" + "0"
                        elif Suggested_Authority_Out[i-1] < Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[6] = "1" + "111111111"
                            else:
                                Train_Bauds[6] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        elif Suggested_Authority_Out[i-1] > Suggested_Authority_Out[i+1]:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i+1] > 511:
                                Train_Bauds[6] = "1" + "111111111"
                            else:
                                Train_Bauds[6] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i+1]))[2:])
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[6] = "1" + "111111111"
                            else:
                                Train_Bauds[6] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

            #65
            if ((Occupancy_Out[65] == 1 and Track_Failure_Out[65] == 0) or 
                (Occupancy_Out[65] == 1 and Occupancy_Out[51] == 1 and Track_Failure_Out[51] == 1 and Track_Failure_Out[65] == 0)):
                if Train_Bauds[7][0] == "1":
                    if Suggested_Speed_Out[65] == "1111" or Suggested_Speed_Out[65] == "1010" or Suggested_Speed_Out[65] == "0":
                        Train_Bauds[7] = "0" + str(Suggested_Speed_Out[65])
                    else:
                        Train_Bauds[7] = "0" + str(bin(int(Suggested_Speed_Out[65]))[2:])
                elif Train_Bauds[7][0] == "0":  # Should only execute if the first if does not
                    if Suggested_Authority_Out[65] == 0 or Suggested_Authority_Out[51] == 0 or Suggested_Authority_Out[65] == "0" or Suggested_Authority_Out[51] == "0":
                        Train_Bauds[7] = "1" + "0"
                    else:
                        if Suggested_Authority_Out[65] + Suggested_Authority_Out[51] > 511:
                            Train_Bauds[7] = "1" + "111111111"
                        else:
                            Train_Bauds[7] = "1" + str(bin(int(Suggested_Authority_Out[65]) + int(Suggested_Authority_Out[51]))[2:])

            for i in range(52, 65):
                if ((Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0) or 
                    (Occupancy_Out[i] == 1 and Occupancy_Out[i+1] == 1 and Track_Failure_Out[i+1] == 1 and Track_Failure_Out[i] == 0)):
                    if Train_Bauds[7][0] == "1":
                        if Suggested_Speed_Out[i] == "1111" or Suggested_Speed_Out[i] == "1010" or Suggested_Speed_Out[i] == "0":
                            Train_Bauds[7] = "0" + str(Suggested_Speed_Out[i])
                        else:
                            Train_Bauds[7] = "0" + str(bin(int(Suggested_Speed_Out[i]))[2:])
                        break
                    elif Train_Bauds[7][0] == "0":  # Should only execute if the first if does not
                        if Suggested_Authority_Out[i] == 0 or Suggested_Authority_Out[i-1] == 0 or Suggested_Authority_Out[i] == "0" or Suggested_Authority_Out[i-1] == "0":
                            Train_Bauds[7] = "1" + "0"
                        else:
                            if Suggested_Authority_Out[i] + Suggested_Authority_Out[i-1] > 511:
                                Train_Bauds[7] = "1" + "111111111"
                            else:
                                Train_Bauds[7] = "1" + str(bin(int(Suggested_Authority_Out[i]) + int(Suggested_Authority_Out[i-1]))[2:])
                        break

        except FileNotFoundError:
            print("Error: File not found! Please check the file path.")
        except Exception as e:
            print(f"Unexpected Error: {e}")

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
        
        try:
            # Load existing JSON
            with open("PLC_OUTPUTS_Baud_Train_Instance2.json", "r") as file:
                data = json.load(file)

            # Update Train_Instance
            data["Train_Instance"] = Train_Instance

            # Update Train_Bauds assuming list of lists: [Baud1-Baud8]
            data["Train_Bauds"] = {
                "1-27-Baud1=": Train_Bauds[0],
                "72-76-Baud2=": Train_Bauds[1],
                "28-33-Baud3=": Train_Bauds[2],
                "34-38-Baud4=": Train_Bauds[3],
                "67-71-Baud5=": Train_Bauds[4],
                "39-44-Baud6=": Train_Bauds[5],
                "45-52-Baud7=": Train_Bauds[6],
                "53-66-Baud8=": Train_Bauds[7]
            }

            # Write back to JSON
            with open("PLC_OUTPUTS_Baud_Train_Instance2.json", "w") as file:
                json.dump(data, file, indent=2)

        except FileNotFoundError:
            print("Error: JSON file not found! Please check the file path.")
        except Exception as e:
            print(f"Unexpected Error: {e}")

        # Define file paths
        original_file = "PLC_OUTPUTS2.json"
        backup_file = "PLC_OUTPUTS_backup2.json"

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
        importlib.reload(PLC_Program_J_N)
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