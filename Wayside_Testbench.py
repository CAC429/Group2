import time
import threading
import random

class Input:
    def __init__(self, Track_Button):
        # Initialize attributes in the constructor
        self.Default_Switch_Position = 0
        self.Suggested_Speed = [50] * 15
        self.Suggested_Authority = [50] * 15
        self.Block_Occupancy = [0] * 15
        self.Count = 0
        self.Random_Tracker = 0
        self.Failure_Block_Number = 100
        self.Random_Occupancy_Number = 0
        self.lock = threading.Lock()  # Lock for thread synchronization
        self.Track_Button = Track_Button  #Store function reference

        # Start auto-updating all values in a background thread
        threading.Thread(target=self.Train_Send, daemon=True).start()
        threading.Thread(target=self.Random_Occupancy, daemon=True).start()

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Occupancy(self):
        return self.Block_Occupancy
    
    def Failure(self):
        return self.Random_Tracker
    
    def Failure_Block(self):
        return self.Failure_Block_Number
    
    def Train_Send(self):  #Define inside the class
        while True:
            with self.lock:  #Ensure thread safety when accessing Count and Button
                current_button = self.Track_Button  #Fetch Button dynamically
                if self.Count < 4:
                    for i in range(5):  #Block 0-4
                        if i == self.Failure_Block()-1:
                            while self.Failure():
                                time.wait(1)
                        self.Block_Occupancy[i] = 1  # Set the current block to True
                        if i > 0:
                            self.Block_Occupancy[i-1] = 0  # Reset previous block
                        time.sleep(2)  # Wait before updating the next one
                        self.Count += 1
                    self.Block_Occupancy[4] = 0
                else:
                    if current_button == 0 and self.Block_Occupancy[9] != 1:
                        for i in range(5, 10):  # Block 5-9
                            if i == self.Failure_Block()-1:
                                while self.Failure():
                                    time.wait(1)
                            self.Block_Occupancy[i] = 1
                            if i > 4:
                                self.Block_Occupancy[i-1] = 0
                            time.sleep(2)
                            self.Count += 1
                    elif current_button == 1 and self.Block_Occupancy[14] != 1:
                        for i in range(10, 15):  # Block 10-14
                            if i == self.Failure_Block()-1:
                                while self.Failure():
                                    time.wait(1)
                            self.Block_Occupancy[i] = 1
                            if i > 10:
                                self.Block_Occupancy[i-1] = 0
                            time.sleep(2)
                            self.Count += 1
                    else:
                        time.sleep(1)
    
    def Random_Occupancy(self):
        while True:
            time.sleep(5)
            if self.Random_Tracker == 0:
                self.Random_Occupancy_Number = 7 #random.randint(0,14)
                self.Failure_Block_Number = self.Random_Occupancy_Number
                self.Block_Occupancy[self.Random_Occupancy_Number] = 1
                self.Random_Tracker = 1
            elif self.Random_Tracker == 1:
                time.sleep(10)
                self.Failure_Block_Number = 100
                self.Block_Occupancy[self.Random_Occupancy_Number] = 0
                self.Random_Tracker = 0
        
            

#Fix the function reference issue
def Get_Testbench_In(Button_Callback):
    from Wayside_Testbench import Input  # Import Testbench
    return Input(Button_Callback)  #Pass the function reference, NOT the return value

def get_button_value():
    global Button
    return Button  #Fetch latest Button value dynamically

#Use function reference, NOT function call
Testbench_In = Get_Testbench_In(get_button_value)  #Pass function reference
