import time
import threading
class Input:
    def __init__(self):
        #Initialize attributes in the constructor
        self.Default_Switch_Position = False
        self.Suggested_Speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Suggested_Authority = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Block_Occupancy = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        #Start auto-updating all values in a background thread
        threading.Thread(target=self.auto_update, daemon=True).start()

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Occupancy(self):
        return self.Block_Occupancy

    def auto_update(self):  #Instance creation
        """Continuously updates all attributes in a loop"""
        while True:
            # ✅ Simulate Block Occupancy changes
            for i in range(9):
                self.Block_Occupancy[i] = 1  # Set the current block to True
                if i > 0:
                    self.Block_Occupancy[i-1] = 0
                time.sleep(1)  # Wait for 1 second before updating the next one

# Create an instance
testbench = Input()
