import time
class Input:
    def __init__(self):
        # Initialize attributes in the constructor
        self.Default_Switch_Position = False
        self.Suggested_Speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Suggested_Authority = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
        self.Block_Occupancy = [bool(x) for x in [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

    def Switch_Position(self):
        return self.Default_Switch_Position

    def Speed(self):
        return self.Suggested_Speed

    def Authority(self):
        return self.Suggested_Authority

    def Occupancy(self):
        return self.Block_Occupancy

    def update_block_occupancy(self):
        """Updates Block_Occupancy from left to right every 1 second."""
        for i in range():
            self.Block_Occupancy[i] = True  # Set the current block to True
            if i > 0:
                self.Block_Occupancy[i-1] = False
            print(self.Block_Occupancy)  # Print updated list
            time.sleep(1)  # Wait for 1 second before updating the next one

# Create an instance
testbench = Input()

# Start updating Block_Occupancy
testbench.update_block_occupancy()
