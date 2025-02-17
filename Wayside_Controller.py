import tkinter as tk
import subprocess
from Wayside_Testbench import Input

class PLC_IN:
    def Switch_Position(Default_Switch_Position):
        Default_Switch_Position
    def Speed(Binary_Suggested_Speed,Suggested_Speed):
        Binary_Suggested_Speed = [format(num, 'b') for num in Suggested_Speed]
    def Authority(Binary_Suggested_Authority,Suggested_Authority):
        Binary_Suggested_Authority = [format(num, 'b') for num in Suggested_Authority]
    def Occupancy(Block_Occupancy):
        Block_Occupancy

def create_ui():
    root = tk.Tk()
    root.title("Box UI")
    root.geometry("300x200")
    
    canvas = tk.Canvas(root, width=300, height=200)
    canvas.pack()
    
    canvas.create_rectangle(50, 50, 250, 150, outline="black", width=3)
    
    root.mainloop()

class Output:
    def Lights(Light_Control):
        Light_Control
    def Switches(Actual_Switch_Position):
        Actual_Switch_Position
    def Speed(Suggested_Speed):
        Suggested_Speed
    def Authority(Suggested_Authority):
        Suggested_Authority
    def Failure(Track_Failure):
        Track_Failure
    def Crossbar(Cross_Bar_Control):
        Cross_Bar_Control
    def Occupancy(Block_Occupancy):
        Block_Occupancy



while True:
    process = subprocess.run(["python", "PLC_Program.py"])
    if __name__ == "__main__":
        create_ui()


