import tkinter as tk
import subprocess
import threading
import time

def get_plc_out():
    from PLC_Program import PLC_Out  # Delayed import to avoid circular dependency
    return PLC_Out()

def Get_Testbench_In():
    from Wayside_Testbench import Input
    return Input()

class PLC_IN:
    def __init__(self, Default_Switch_Position=None, Suggested_Speed=None, Suggested_Authority=None, Block_Occupancy=None):
        # Store variables properly
        self.Default_Switch_Position=Testbench_In.Switch_Position(),
        self.Suggested_Speed = [format(num, 'b') for num in Testbench_In.Speed()],
        self.Suggested_Authority = [format(num, 'b') for num in Testbench_In.Authority()], 
        self.Block_Occupancy = Testbench_In.Occupancy()

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return list(self.Suggested_Speed)  # Returns binary speed list

    def Authority(self):
        return list(self.Suggested_Authority)  # Returns binary authority list

    def Occupancy(self):
        return list(self.Block_Occupancy)

def create_ui():
    root = tk.Tk()
    root.title("Box UI")
    root.geometry("300x200")

    canvas = tk.Canvas(root, width=300, height=200)
    canvas.pack()
    
    canvas.create_rectangle(50, 50, 250, 150, outline="black", width=3)

    root.mainloop()

# ✅ Get testbench input properly
Testbench_In = Get_Testbench_In()

# ✅ Run PLC_Program in background (Non-blocking)
PLC_RUN = subprocess.Popen(["python", "PLC_Program.py"])

# ✅ Get PLC output
plc_out = get_plc_out()

# ✅ Run PLC updates in a separate threads
def update_plc_data():
    while True:
        time.sleep(1)  # Prevent CPU overload
        Actual_Speed = [int(b, 2) for b in plc_out.Speed()]
        Actual_Authority = [int(b, 2) for b in plc_out.Authority()]

threading.Thread(target=update_plc_data, daemon=True).start()

# ✅ Run UI only once
if __name__ == "__main__":
    create_ui()
