class Reference_Objects:
    def __init__(self,one): 
        self.one = one
        self.Beacon = None
        self.Suggested_Speed_Authority = None

    def Pass_Beacon(self, Beacon): #return beacon
        self.Beacon = Beacon
        return self.Beacon
    
    def Pass_Suggested_Speed_Authority(self, Suggested_Speed_Authority): #return suggested_speed_authority
        self.Suggested_Speed_Authority = Suggested_Speed_Authority
        return self.Suggested_Speed_Authority
    #pitt  tt