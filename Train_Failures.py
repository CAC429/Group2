class Train_Failure:
    def __init__(self, Engine_Fail, Signal_Pickup_Fail, Brake_Fail): #Instantiate failures as false
        self.Engine_Fail = Engine_Fail
        self.Signal_Pickup_Fail = Signal_Pickup_Fail
        self.Brake_Fail = Brake_Fail
    
    
    def Reset(self): #resets all failures to false
        self.Engine_Fail = False
        self.Signal_Pickup_Fail = False
        self.Brake_Fail = False
        print("Failures have been reset")