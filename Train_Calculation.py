class Train_Calc:
    def __init__(self, dt, Train_Mass, Actual_Authority, Passenger_Number, Power): #dt is change in time
        self.dt = dt
        self.Train_Mass = Train_Mass
        self.Actual_Authority = Actual_Authority
        self.Passenger_Number = Passenger_Number #temp, will be given by track model
        self.Power = Power #temp, will be given by train control

    def Get_Total_Mass(self):
        return self.Train_Mass + self.Passenger_Number*75 #in kgs 
    
    def Actual_Speed_Calc(self): #loop in mainfile
        Total_Mass = self.Get_Total_Mass()
        self.Actual_Speed = (((self.Power/self.Actual_Speed)/Total_Mass)*self.dt)+self.Actual_Speed
        return self.Actual_Speed
    
    def Actual_Authority_Calc(self): #calculate actual authority with new speed
        return (self.Actual_SpeedCalc())*self.dt