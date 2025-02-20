import tkinter as tk
from tkinter import ttk
import subprocess

Track_Button = 0
Failure_Button = 0

def Get_PLC_Out():
    from PLC_Program import PLC_Out  #Import PLC_Out
    from Wayside_Testbench import Input  #Import Testbench input
    plc_in = Input(Track_Button)  #Create an instance of Testbench Input
    return PLC_Out(plc_in)  #Pass plc_in to PLC_Out

def Get_Testbench_In(Button_Callback_Track):
    from Wayside_Testbench import Input #Import Testbench
    return Input(Button_Callback_Track)  #Return TestBench

class PLC_IN:
    def __init__(self):
        # Store variables properly
        self.Default_Switch_Position=Testbench_In.Switch_Position()
        self.Suggested_Speed = [format(num, 'b') for num in Testbench_In.Speed()] #Speed integer to binary
        self.Suggested_Authority = [format(num, 'b') for num in Testbench_In.Authority()] #Authority integer to binary
        self.Block_Occupancy = Testbench_In.Occupancy()
        self.Toggle_Switch = 0

    #Return each variable
    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return list(self.Suggested_Speed)  #Returns binary speed list

    def Authority(self):
        return list(self.Suggested_Authority)  #Returns binary authority list

    def Occupancy(self):
        return list(self.Block_Occupancy)   #Returns block occupancy list
    
    def Switch(self):
        return app.Toggle_Track_Button() if app and app.Toggle_Track_Button() else self.Toggle_Switch

class DataGridUI:
    def __init__(self, root, Testbench_In):
        self.root = root
        self.root.title("Live Data Grid")
        self.Testbench_In = Testbench_In

        #Initialize toggle variables
        self.Toggle_Track_Switch = 0  
        self.Toggle_Failure_Switch = 0

        #Create Treeview (Table)
        self.tree = ttk.Treeview(root, columns=("Block", "Cross Bars", "Switch Position", "Suggested Speed", "Suggested Authority", "Track Failure", "Occupancy"), show="headings")
        self.tree.pack(fill="both", expand=True)

        #Define Column Headings
        self.tree.heading("Block", text="Block")
        self.tree.heading("Cross Bars", text="Cross Bars")
        self.tree.heading("Switch Position", text="Switch Position")
        self.tree.heading("Suggested Speed", text="Suggested Speed")
        self.tree.heading("Suggested Authority", text="Suggested Authority")
        self.tree.heading("Track Failure", text="Track Failure")
        self.tree.heading("Occupancy", text="Occupied?")

        #Define Column Widths
        self.tree.column("Block", width=100, anchor="center")
        self.tree.column("Cross Bars", width=100, anchor="center")
        self.tree.column("Switch Position", width=100, anchor="center")
        self.tree.column("Suggested Speed", width=100, anchor="center")
        self.tree.column("Suggested Authority", width=100, anchor="center")
        self.tree.column("Track Failure", width=100, anchor="center")
        self.tree.column("Occupancy", width=100, anchor="center")

        #Add Track Toggle
        self.Toggle_Track = tk.Button(root, text="Switch Train Direction", command=self.Toggle_Track_Button)
        self.Toggle_Track.pack(pady=10)

        #Add Track Toggle
        self.Toggle_Failure = tk.Button(root, text="Cause Failure", command=self.Toggle_Failure_Button)
        self.Toggle_Failure.pack(pady=10)

        #Get Initial Data
        self.update_ui()

    def Toggle_Failure_Button(self):
        if self.Toggle_Failure_Switch == 0:
            self.Toggle_Failure_Switch = 1
        elif self.Toggle_Failure_Switch == 1:
            self.Toggle_Failure_Switch = 0
        global Failure_Button
        Failure_Button = self.Toggle_Failure_Switch
        return self.Toggle_Failure_Switch
        

    def Toggle_Track_Button(self):
        if self.Toggle_Track_Switch == 0:
            self.Toggle_Track_Switch = 1
        elif self.Toggle_Track_Switch == 1:
            self.Toggle_Track_Switch = 0
        global Track_Button
        Track_Button = self.Toggle_Track_Switch
        return self.Toggle_Track_Switch

    #Update the UI
    def update_ui(self):
        self.tree.delete(*self.tree.get_children())  #Clear existing table data

        #Define text colors for specific blocks
        self.tree.tag_configure("red_blocks", foreground="red")  #Red blocks 6-10
        self.tree.tag_configure("blue_blocks", foreground="blue")  #Blue blocks 11-15
        self.tree.tag_configure("normal", foreground="black")  #Default black text            

        #Use Testbench_In for the initial occupancy values or initialize values not already done so
        if not hasattr(self, 'initialized'):
            self.Cross_Bar = [""] * 15
            self.occupancy_data = Testbench_In.Occupancy()
            self.speed_data = Testbench_In.Speed()
            self.authority_data = Testbench_In.Authority()
            self.switch_data = [""] * 15
            self.switch_data[4] = Testbench_In.Switch_Position()
            self.Failure = [""] * 15
            self.initialized = True  #Mark initialization done
        else:
            #Use plc_out for updates, ensures plc_out is valid
            plc_out.Update_Cross_Bar()
            plc_out.Update_Light_Control()
            plc_out.Update_Speed_Authority()
            Binary_Temp_Speed = plc_out.Speed()[:]

            #Speed from binary to integer, uses a temporary list
            Temp_Speed = [0] * 15
            for i in range(len(Binary_Temp_Speed)):
                if Binary_Temp_Speed[i] == "110010":
                    Temp_Speed[i] = 50
                if Binary_Temp_Speed[i] == "1010":
                    Temp_Speed[i] = 10
                if Binary_Temp_Speed[i] == "0":
                    Temp_Speed[i] = 0

            #Authority from binary to integer, uses a temporary list
            Binary_Temp_Authority = plc_out.Authority()[:]
            Temp_Authority = [0] * 15
            for i in range(len(Binary_Temp_Authority)):
                if Binary_Temp_Authority[i] == "110010":
                    Temp_Authority[i] = 50
                if Binary_Temp_Authority[i] == "11001":
                    Temp_Authority[i] = 25
                if Binary_Temp_Authority[i] == "0":
                    Temp_Authority[i] = 0

            #initializing the varibles with the correct variables otherwise sets a default value
            self.speed_data = Temp_Speed if plc_out and plc_out.Speed() else [0] * 15
            self.authority_data = Temp_Authority if plc_out and plc_out.Authority() else [0] * 15
            self.switch_data[4] = self.Toggle_Track_Switch
            self.Cross_Bar[2] = plc_out.Crossbar() if plc_out and plc_out.Crossbar() else 0
            if Testbench_In.Failure_Block() == 100:    
                self.Failure = [""] * 15
            else:
                self.Failure[Testbench_In.Failure_Block()] = Testbench_In.Failure if Testbench_In and Testbench_In.Failure else [0] * 15

        #Insert rows with specific colors based on Block ID
        for i in range(len(self.occupancy_data)):
            block_id = i + 1  #Block IDs are 1-based

            #Set text color based on block ID
            if 6 <= block_id <= 10:  # Blocks 6-10 go to red
                row_tag = "red_blocks"
            elif 11 <= block_id <= 15:  #Blocks 11-15 go to blue
                row_tag = "blue_blocks"
            else:
                row_tag = "normal"  #Default black text

            self.tree.insert("", "end", values=(
                f"Block {block_id}",  #Block ID
                self.Cross_Bar[i],    #Cross Bar
                self.switch_data[i],  #Switch Position
                self.speed_data[i],   #Speed in binary
                self.authority_data[i],  #Authority in binary
                "Failure" if self.Failure[i] else "",  #Failure
                "Yes" if self.occupancy_data[i] else "No"  #Occupancy status
            ), tags=(row_tag,))  #Apply text color tag

        self.root.after(1000, self.update_ui)  #Refresh every second

#Get testbench input properly
Testbench_In = Get_Testbench_In(Track_Button)

#Start PLC Program in the background
PLC_RUN = subprocess.Popen(["python", "PLC_Program.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Create an instance of the Get_PLC_Out
plc_out = Get_PLC_Out()

#Use plc_out for updates
plc_out.Update_Cross_Bar()
plc_out.Update_Light_Control()
plc_out.Update_Speed_Authority()
plc_out.Update_Actual_Switch_Position()

#Start UI
if __name__ == "__main__":
    temp = Testbench_In.Occupancy()
    root = tk.Tk()
    app = DataGridUI(root,Testbench_In)
    #Ensure PLC process stops when UI closes
    def on_closing():
        PLC_RUN.terminate()  #Stops the background process
        PLC_RUN.wait()  #Ensures cleanup
        root.destroy()  #Close the UI
    #Start background task
    root.protocol("WM_DELETE_WINDOW", on_closing)  #Detect window close
    root.mainloop()