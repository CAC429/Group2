import tkinter as tk
import subprocess
from Wayside_Testbench import Input

def get_plc_out():
    from PLC_Program import PLC_Out  # Delayed import to avoid circular dependency
    return PLC_Out()

class PLC_IN:
    def __init__(self, Suggested_Speed=None, Suggested_Authority=None, Block_Occupancy=None):
        # Default values if none are provided
        self.Default_Switch_Position = False  
        
        # Store speed and convert to binary
        self.Suggested_Speed = Suggested_Speed
        self.Binary_Suggested_Speed = [format(num, 'b') for num in self.Suggested_Speed]

        # Store authority and convert to binary
        self.Suggested_Authority = Suggested_Authority
        self.Binary_Suggested_Authority = [format(num, 'b') for num in self.Suggested_Authority]

        # Store occupancy
        self.Block_Occupancy = Block_Occupancy

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Binary_Suggested_Speed  # Returns binary speed list

    def Authority(self):
        return self.Binary_Suggested_Authority  # Returns binary authority list

    def Occupancy(self):
        return self.Block_Occupancy


def create_ui():
    root = tk.Tk()
    root.title("Box UI")
    root.geometry("300x200")
    
    canvas = tk.Canvas(root, width=300, height=200)
    canvas.pack()
    
    canvas.create_rectangle(50, 50, 250, 150, outline="black", width=3)
    
    root.mainloop()

while True:
    PLC_RUN = subprocess.run(["python", "PLC_Program.py"])

    plc_out = get_plc_out()
    Actual_Speed = [int(b, 2) for b in plc_out.Speed()]
    Actual_Authority = [int(b, 2) for b in plc_out.Authority()]
    
    
    if __name__ == "__main__":
        create_ui()


