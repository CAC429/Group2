import importlib
import PLC_Program_A_F  # Import the script
import PLC_Program_G_M  # Import the script
import PLC_Program_N_Q  # Import the script
import PLC_Program_R_Z  # Import the script
import tkinter as tk
from tkinter import ttk
import threading
import time

Train_Bauds = ["0000000000"]*3
def update_in_background():
    while True:
        Suggested_Speed_Out = [0] * 150
        Suggested_Authority_Out = [0] * 150
        Occupancy_Out = [0] * 150
        Track_Failure_Out = [0] * 150
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
        Train_Baud_Select = 0
        Train_Count = 0
        for i in range(150):
            if Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0:
                Train_Count = Train_Count + 1
        if Train_Bauds[0][0] == "1":
            for i in range(150):
                if Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0 and Train_Count <= 3:
                    Train_Bauds[Train_Baud_Select] = "0"+str(Suggested_Speed_Out[i])
                    Train_Baud_Select = Train_Baud_Select+1
        elif Train_Bauds[0][0] == "0":
            for i in range(150):
                if Occupancy_Out[i] == 1 and Track_Failure_Out[i] == 0 and Train_Count <= 3:
                    Train_Bauds[Train_Baud_Select] = "1"+str(Suggested_Authority_Out[i])
                    Train_Baud_Select = Train_Baud_Select+1
        if Train_Count == 2:
            Train_Bauds[2] = "0000000000"
        elif Train_Count == 1:
            Train_Bauds[1] = "0000000000"
            Train_Bauds[2] = "0000000000"
        elif Train_Count == 0:
            Train_Bauds[0] = "0000000000"
            Train_Bauds[1] = "0000000000"
            Train_Bauds[2] = "0000000000"
        print(Train_Bauds)
        time.sleep(1)  # Wait for 1 second before updating again

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

        #Check if occupancy or user entered data has changed for user inputs or testbench(team combined code)
        New_Occupancy = [a | b for a, b in zip(Occupancy_In, Self.Test_Occupancy)] # Get updated occupancy
        if hasattr(Self, "Prev_Occupancy") and New_Occupancy == Self.Prev_Occupancy and Self.User_Speed == Self.Prev_User_Speed and Self.User_Authority == Self.Prev_User_Authority:
            # No change in occupancy, so don't update the UI
            Self.Root.after(500, Self.Update_UI)  # Re-check after 500ms
            return

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
        Binary_Temp_Speed = Suggested_Speed_Out
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
        Self.Root.after(500, Self.Update_UI)  #Check for updates every 500ms

# Create a thread that will run the update_in_background function
background_thread = threading.Thread(target=update_in_background, daemon=True)
background_thread.start()

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