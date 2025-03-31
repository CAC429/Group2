class Train_Failure:
    def __init__(self,Engine_Fail, Signal_Pickup_Fail, Brake_Fail): #Instantiate failures as false
        self.Engine_Fail = False
        self.Signal_Pickup_Fail = False
        self.Brake_Fail = False
    
    def Cause_Engine_Fail(self): #Engine failure
        self.Engine_Fail = True
    
    def Cause_Signal_Pickup_Fail(self): #signal picup failure
        self.Signal_Pickup_Fail = True
    
    def Cause_Brake_Fail(self): #Brake failure
        self.Brake_Fail = True
    
    def Reset(self): #resets all failures to false
        self.Engine_Fail = False
        self.Signal_Pickup_Fail = False
        self.Brake_Fail = False