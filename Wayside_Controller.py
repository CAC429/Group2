import tkinter as tk
from tkinter import ttk
import subprocess
import time

def get_plc_out():
    from PLC_Program import PLC_Out  # ✅ Import PLC_Out
    from Wayside_Testbench import Input  # ✅ Import Testbench input
    plc_in = Input()  # ✅ Create an instance of Testbench Input
    return PLC_Out(plc_in)  # ✅ Pass plc_in to PLC_Out

def Get_Testbench_In():
    from Wayside_Testbench import Input
    return Input()

class PLC_IN:
    def __init__(self):
        # Store variables properly
        self.Default_Switch_Position=Testbench_In.Switch_Position()
        self.Suggested_Speed = [format(num, 'b') for num in Testbench_In.Speed()]
        self.Suggested_Authority = [format(num, 'b') for num in Testbench_In.Authority()]
        self.Block_Occupancy = Testbench_In.Occupancy()

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return list(self.Suggested_Speed)  # Returns binary speed list

    def Authority(self):
        return list(self.Suggested_Authority)  # Returns binary authority list

    def Occupancy(self):
        return list(self.Block_Occupancy)

class DataGridUI:
    def __init__(self, root, plc_out):
        self.root = root
        self.root.title("Live Data Grid")

        # Create Treeview (Table)
        self.tree = ttk.Treeview(root, columns=("Block", "Cross Bars", "Switch Position", "Suggested Speed", "Suggested Authority", "Track Failure", "Occupancy"), show="headings")
        self.tree.pack(fill="both", expand=True)

        # Define Column Headings
        self.tree.heading("Block", text="Block")
        self.tree.heading("Cross Bars", text="Cross Bars")
        self.tree.heading("Switch Position", text="Switch Position")
        self.tree.heading("Suggested Speed", text="Suggested Speed")
        self.tree.heading("Suggested Authority", text="Suggested Authority")
        self.tree.heading("Track Failure", text="Track Failure")
        self.tree.heading("Occupancy", text="Occupied?")

        # Define Column Widths
        self.tree.column("Block", width=100, anchor="center")
        self.tree.column("Cross Bars", width=100, anchor="center")
        self.tree.column("Switch Position", width=100, anchor="center")
        self.tree.column("Suggested Speed", width=100, anchor="center")
        self.tree.column("Suggested Authority", width=100, anchor="center")
        self.tree.column("Track Failure", width=100, anchor="center")
        self.tree.column("Occupancy", width=100, anchor="center")

        # Get Initial Data
        self.update_ui()

    def update_ui(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing table data

        # ✅ Use Testbench_In for the initial occupancy values
        if not hasattr(self, 'initialized'):
            self.Cross_Bar = [""]*15
            self.occupancy_data = Testbench_In.Occupancy()
            self.speed_data = Testbench_In.Speed()
            self.authority_data = Testbench_In.Authority()
            self.switch_data = Testbench_In.Switch_Position()
            self.Failure = [False]*15
            self.initialized = True  # Mark initialization done
        else:
            # ✅ Use plc_out for updates (ensure plc_out is valid)
            plc_out.Update_Cross_Bar()
            plc_out.Update_Light_Control()
            plc_out.Update_Speed_Authority()
            Binary_Temp_Speed = plc_out.Speed()[:]
            Temp_Speed = [0]*15
            for i in range(len(Binary_Temp_Speed)):
                if Binary_Temp_Speed[i] == "110010":  # Assuming Binary_Temp_Speed[i] is a string
                    Temp_Speed[i] = 50
                if Binary_Temp_Speed[i] == "1010":
                    Temp_Speed[i] = 10
                if Binary_Temp_Speed[i] == "0":
                    Temp_Speed[i] = 0
            Binary_Temp_Authority = plc_out.Authority()[:]
            Temp_Authority = [0]*15
            for i in range(len(Binary_Temp_Authority)):
                if Binary_Temp_Authority[i] == "110010":  # Assuming Binary_Temp_Authority[i] is a string
                    Temp_Authority[i] = 50
                if Binary_Temp_Authority[i] == "11001":
                    Temp_Authority[i] = 25
                if Binary_Temp_Authority[i] == "0":
                    Temp_Authority[i] = 0
            self.speed_data = Temp_Speed if plc_out and plc_out.Speed() else [0] * 15
            self.authority_data = Temp_Authority if plc_out and plc_out.Authority() else [0] * 15
            self.switch_data = plc_out.Switches() if plc_out and plc_out.Switches() else 0
            self.Cross_Bar[2] = plc_out.Crossbar() if plc_out and plc_out.Crossbar() else 0
            self.Failure = plc_out.Failure() if plc_out and plc_out.Failure() else [0] * 15

        for i in range(len(self.occupancy_data)):
            self.tree.insert("", "end", values=(
                f"Block {i+1}",                #Block ID
                self.Cross_Bar[i],             #Cross Bar
                self.switch_data,              #Switch Position
                self.speed_data[i],            #Speed in binary
                self.authority_data[i],        #Authority in binary
                "Failure" if self.Failure[i] else "",      #Failure
                "Yes" if self.occupancy_data[i] else "No"  # Occupancy status
            ))

        self.root.after(1000, self.update_ui)  # Refresh every second

#Get testbench input properly
Testbench_In = Get_Testbench_In()

#Start PLC Program in the background
PLC_RUN = subprocess.Popen(["python", "PLC_Program.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

plc_out = get_plc_out()

plc_out.Update_Cross_Bar()
plc_out.Update_Light_Control()
plc_out.Update_Speed_Authority()

# ✅ Start UI
if __name__ == "__main__":
    temp = Testbench_In.Occupancy()
    root = tk.Tk()
    app = DataGridUI(root,plc_out)
# Ensure PLC process stops when UI closes
    def on_closing():
        PLC_RUN.terminate()  #Stops the background process
        PLC_RUN.wait()  #Ensures cleanup
        root.destroy()  #Close the UI
        #Start background task
    root.protocol("WM_DELETE_WINDOW", on_closing)  #Detect window close
    root.mainloop()