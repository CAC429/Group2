import tkinter as tk
from tkinter import ttk

#Gets the output from PLC
def Get_PLC_Out():
    from PLC_Program import PLC_Out  #Import PLC_Out
    from Wayside_Testbench import Input  #Import Testbench input
    Plc_Out_Input = Input()  #Create an instance of Testbench Input
    return PLC_Out(Plc_Out_Input)  #Pass PLC_IN to PLC_Out

#Imports from the Testbench, will import from other members file
def Get_Testbench_In():
    from Wayside_Testbench import Input #Import Testbench
    return Input()  #Return TestBench

#Input to the PLC file
class PLC_IN:
    def __init__(Self):
        #Store variables properly
        Self.Default_Switch_Position = Testbench_In.Switch_Position()
        Self.Suggested_Speed = [format(Number, 'b') for Number in Testbench_In.Speed()] #Speed integer to binary
        Self.Suggested_Authority = [format(Number, 'b') for Number in Testbench_In.Authority()] #Authority integer to binary
        Self.Block_Occupancy = Testbench_In.Occupancy()

    #Return each variable
    def Switch_Position(Self):
        return Self.Default_Switch_Position  #Returns default switch position

    def Speed(Self):
        return list(Self.Suggested_Speed)  #Returns binary speed list

    def Authority(Self):
        return list(Self.Suggested_Authority)  #Returns binary authority list

    def Occupancy(Self):
        return list(Self.Block_Occupancy)   #Returns block occupancy list

#This is the UI setup, has data driven arguments as well
class DataGridUI:
    def __init__(Self, Root, Testbench_In):
        #Needed initializations
        Self.Root = Root
        Self.Root.title("Wayside Controller")
        Self.Testbench_In = Testbench_In
        Self.Test_Occupancy = [0] * 150

        #Initialize toggle variables

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
        Self.Default_Switch_Position.set(f"Default Switch Position: {Testbench_In.Switch_Position()}")
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
        Test_Block = Self.Block_Selector.get()-1  #Get the selected block number
        if Self.Test_Occupancy[Test_Block] == 0:
            Self.Test_Occupancy[Test_Block] = 1
        elif Self.Test_Occupancy[Test_Block] == 1:
            Self.Test_Occupancy[Test_Block] = 0
        Self.Update_UI()

    #Gets the speed the user inputs at the block they choose
    def Get_Speed_Input(Self):
        Test_Block = Self.Block_Selector.get()-1
        Self.User_Speed[Test_Block] = Self.Speed_User_Input.get()
        Self.Update_UI()

    #Gets the authority the user inputs at the block they choose
    def Get_Authority_Input(Self):
        Test_Block = Self.Block_Selector.get()-1
        Self.User_Authority[Test_Block] = Self.Authority_User_Input.get()
        Self.Update_UI()

    #Update the UI
    def Update_UI(Self):
        #Check if occupancy or user entered data has changed for user inputs or testbench(team combined code)
        New_Occupancy = [a | b for a, b in zip(Testbench_In.Occupancy(), Self.Test_Occupancy)] # Get updated occupancy
        Testbench_In.UpdateOccupancy()
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

        # Initialize values if not already done
        if not hasattr(Self, 'initialized'):
            Self.Cross_Bar = [""] * 150
            Self.occupancy_data = New_Occupancy
            Self.Speed_Data = Testbench_In.Speed()
            Self.Authority_Data = Testbench_In.Authority()
            Self.Switch_Data = [""] * 150
            Self.Switch_Data[11] = Testbench_In.Default_Switch_Position
            Self.Switch_Data[27] = Testbench_In.Default_Switch_Position
            Self.Switch_Data[57] = 1
            Self.Switch_Data[61] = 1
            Self.Switch_Data[75] = Testbench_In.Default_Switch_Position
            Self.Switch_Data[84] = Testbench_In.Default_Switch_Position
            Self.Cross_Bar[18] = 0
            Self.Cross_Bar[107] = PLC_Out.Crossbar()[1]
            Self.Failure = [""] * 150
            Self.Lights = [1] * 150
            Self.initialized = True  # Mark initialization done
        else:
            # Update using PLC_Out values
            PLC_Out.Update_Actual_Switch_Position(New_Occupancy)
            PLC_Out.Update_Failure(New_Occupancy)
            PLC_Out.Update_Cross_Bar(New_Occupancy)
            PLC_Out.Update_Light_Control(New_Occupancy)
            PLC_Out.Update_Speed_Authority()
            PLC_Out.Update_Previous_Occupancy(New_Occupancy)
            Binary_Temp_Speed = PLC_Out.Speed()[:]
            Binary_Temp_Authority = PLC_Out.Authority()[:]

            # Update UI values
            Self.Switch_Data[11] = PLC_Out.Switches()[0]
            Self.Switch_Data[27] = PLC_Out.Switches()[1]
            Self.Switch_Data[57] = PLC_Out.Switches()[2]
            Self.Switch_Data[61] = PLC_Out.Switches()[3]
            Self.Switch_Data[75] = PLC_Out.Switches()[4]
            Self.Switch_Data[84] = PLC_Out.Switches()[5]
            Self.Cross_Bar[18] = PLC_Out.Crossbar()[0]
            Self.Cross_Bar[107] = PLC_Out.Crossbar()[1]
            Self.Lights = PLC_Out.Lights()
            Self.Failure = PLC_Out.Failure()  # Reset failures (Adjust logic if needed)

            # Convert binary speed to integer
            Temp_Speed = [1] * 150
            Temp_Authority = [1] * 150
            for Find_Failure in range(len(PLC_Out.Failure())):
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

            for Combine in range(len(New_Occupancy)):
                if Temp_Speed[Combine] == 1:
                    Temp_Speed[Combine] = Testbench_In.Speed()[Combine]
                if Temp_Authority[Combine] == 1:
                    Temp_Authority[Combine] = Testbench_In.Authority()[Combine]

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

#Get testbench input properly
Testbench_In = Get_Testbench_In()

#Start UI
if __name__ == "__main__":
#Create an instance of the Get_PLC_Out
    PLC_Out = Get_PLC_Out()

    #Use PLC_Out for updates
    PLC_Out.Update_Actual_Switch_Position(Testbench_In.Occupancy())
    PLC_Out.Update_Failure(Testbench_In.Occupancy())
    PLC_Out.Update_Cross_Bar(Testbench_In.Occupancy())
    PLC_Out.Update_Light_Control(Testbench_In.Occupancy())
    PLC_Out.Update_Speed_Authority()
    PLC_Out.Update_Previous_Occupancy(Testbench_In.Occupancy())
    Root = tk.Tk()
    App = DataGridUI(Root,Testbench_In)
    #Ensure PLC process stops when UI closes
    def on_closing():
        Root.destroy()  #Destroy the UI
    #Start background task
    Root.protocol("WM_DELETE_WINDOW", on_closing)  #Detect window close
    Root.mainloop()