class Train_Calc:
    def __init__(self, Dt, Train_Mass, Actual_Speed, Actual_Authority, Elevation):
        self.Dt = Dt  # in seconds
        self.Train_Mass = Train_Mass  # kg
        self.Actual_Speed = Actual_Speed  # mph
        self.Actual_Authority = Actual_Authority  # ft
        self.Elevation = Elevation #ft

    def Get_Elevation(self):
        return self.Elevation
        
        
    def Acceleration_Calc(self, Power, Passenger_Number):
        Total_Mass = self.Train_Mass + Passenger_Number * 75  # in kg

        Force = Power / (self.Actual_Speed * (1000 / 3600))  # Convert kph to m/s
        Acceleration_m_per_s2 = Force / Total_Mass  # Acceleration in m/s²
            
            # Convert acceleration from m/s² to km/h²
        Train_Acceleration = Acceleration_m_per_s2 * (3600 ** 2) / 1000  # (km/h²)
        Train_Acceleration_Imperical = Train_Acceleration*0.386102 #km/h^2 to mph^2

        return Train_Acceleration_Imperical

    def Actual_Speed_Calc(self, Power, Passenger_Number):
        Total_Mass = self.Train_Mass + Passenger_Number * 75  # in kg

        Actual_Speed_Metric = self.Actual_Speed*1.60934
        Force = Power / (Actual_Speed_Metric * (1000 / 3600))  # Convert kph to m/s
        Acceleration_m_per_s2 = Force / Total_Mass  # Acceleration in m/s²
            
            # Convert acceleration from m/s² to km/h²
        Acceleration_km_h2 = Acceleration_m_per_s2 * (3600 ** 2) / 1000  # (km/h²)

        Delta_Velocity = Acceleration_km_h2 * (self.Dt / 3600)
        Delta_Velocity_Imperial = Delta_Velocity*0.621371
        New_Actual_Speed = self.Actual_Speed + Delta_Velocity_Imperial
        return New_Actual_Speed

    def Actual_Authority_Calc(self, Power, Passenger_Number):
        New_Speed_Metric = self.Actual_Speed_Calc(Power, Passenger_Number)*1.60934

        Speed_m_per_s = New_Speed_Metric * (1000 / 3600)  # Convert kph to m/s
        Delta_Position = Speed_m_per_s * self.Dt
        New_Actual_Authority = Delta_Position*3.28084 + self.Actual_Authority
        return New_Actual_Authority

    def Grade_Calc(self, Power, Passenger_Number):
        New_Speed = self.Actual_Speed_Calc(Power, Passenger_Number)
        Speed_ft_per_s = New_Speed * 1.46667
        Delta_Position_ft = Speed_ft_per_s * self.Dt
        Total_Horizontal_Distance_ft = 1000
        Scaled_Elevation_ft = self.Elevation * (Delta_Position_ft / Total_Horizontal_Distance_ft)
        if Delta_Position_ft != 0:
            Grade = (Scaled_Elevation_ft / Delta_Position_ft) * 100
        else:
            Grade = 0
        return Grade
    
    def Delta_Position_Track_Model(self, Power, Passenger_Number):
        New_Speed_Metric = self.Actual_Speed_Calc(Power, Passenger_Number)*1.60934

        Speed_m_per_s = New_Speed_Metric * (1000 / 3600)  # Convert kph to m/s
        Delta_Position = Speed_m_per_s * self.Dt
        return Delta_Position