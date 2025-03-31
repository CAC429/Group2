class Reference_Objects:
    def __init__(self,one): 
        self.one = one
        self.Beacon = None
        self.Suggested_Speed_Authority = None

    def Pass_Beacon(self, Beacon):
        self.Beacon = Beacon
        return self.Beacon
    
    def Pass_Suggested_Speed(self, Suggested_Speed_Authority):
        self.Suggested_Speed_Authority = Suggested_Speed_Authority
        return self.Suggested_Speed_Authority
    