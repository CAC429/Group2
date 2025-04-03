class Train_Comp:
    def __init__(self,one): #one is only used for making the UI function as intended
        self.one = one

    def Set_Cabin_Temp(self,Cabin_Temp): #Temp variable will get from Train Control
        print(f"Cabin temperature will be {Cabin_Temp}°F")
        return Cabin_Temp
    
    def Set_Exterior_Lights(self,Exterior_Lights): #Temp variable will get from Train Control
        if Exterior_Lights:
            print("Exterior lights are on")
        else:
            print("Exterior lights are off")
        return Exterior_Lights

    def Set_Interior_Lights(self,Interior_Lights): #Temp variable will get from Train Control
        if Interior_Lights:
            print("Interior lights are on")
        else:
            print("Interior lights are off")
        return Interior_Lights
    
    def Open_Right_Door(self,Right_Door): #Temp variable will get from Train Control
        if Right_Door:
            print("Right door is open")
        else:
            print("Right door is closed")
        return Right_Door
    
    def Open_Left_Door(self,Left_Door): #Temp variable will get from Train Control
        if Left_Door:
            print("Left door is open")
        else:
            print("Left door is closed")
        return Left_Door