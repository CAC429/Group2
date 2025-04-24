class Train_Calc:
    def __init__(self, Dt, Train_Mass, Actual_Speed, Actual_Authority, Elevation):
        self.Dt = Dt  # in seconds (changed to 0.1s for better updates)
        self.Train_Mass = Train_Mass  # kg
        self.Actual_Speed = Actual_Speed  # mph
        self.Actual_Authority = Actual_Authority  # ft
        self.Elevation = Elevation  # ft

    def Get_Elevation(self):
        return self.Elevation
        
    def Acceleration_Calc(self, Power, Passenger_Number):
        Total_Mass = self.Train_Mass + Passenger_Number * 75  # in kg
        speed_mps = self.Actual_Speed * 0.44704  # Convert mph to m/s
        
        if speed_mps > 0:
            Force = Power / speed_mps
            Acceleration_m_per_s2 = Force / Total_Mass  # Acceleration in m/s²
        else:
            Acceleration_m_per_s2 = 0
            
        return Acceleration_m_per_s2 * 2.23694  # Convert to mph/s

    def Actual_Speed_Calc(self, Power, Passenger_Number):
        acceleration = self.Acceleration_Calc(Power, Passenger_Number)
        return self.Actual_Speed + acceleration * self.Dt

    def Actual_Authority_Calc(self, Power, Passenger_Number):
        new_speed = self.Actual_Speed_Calc(Power, Passenger_Number)
        speed_fps = new_speed * 1.46667  # mph to ft/s
        return self.Actual_Authority + (speed_fps * self.Dt)

    def Grade_Calc(self):
        delta_pos = self.Get_Elevation()
        if delta_pos != 0:
            return (self.Elevation / delta_pos) * 100
        return 0
    