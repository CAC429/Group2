class Input:
    def __init__(self, Power, Passenger_Number, Cabin_Temp, Exterior_Lights, Interior_lights, Right_Door, Left_Door, Beacon, Suggested_Speed, Suggested_Authority):
        self.Power = 75000 #in Watts
        self.Passenger_Number = 20
        self.Cabin_Temp = 40 #in Celsius
        self.Exterior_Lights = True 
        self.Interior_Lights = True
        self.Right_Door = False 
        self.Left_Door = False
        self.Beacon = 0 #Max bits is 128
        self.Suggested_Speed = 35 #in kilometers per hour 
        self.Suggested_Authority = 2000 #in meters