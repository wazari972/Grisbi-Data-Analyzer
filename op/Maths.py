from op import Operator

from Bank import *

class Maths(Operator):
    def __init__(self):
        global Do_Maths
        Operator.__init__(self)
        self.doers = []
        
        for cls in Do_Maths:
            self.doers.append(cls())

    def process(self, transac):
        for doer in self.doers:
            doer.do(transac.montant)

    def dump(self):
        return [doer.dump() for doer in self.doers]

###########################################

class MathsCat(Maths):
    def __init__(self, cat):
        Maths.__init__(self)
        self.cat = cat
    
    def accept(self, transac):
        return self.cat == transac.cat


class MathsAccount(Maths):
    def __init__(self, account):
        Maths.__init__(self)
        self.acc = account

    def accept(self, transac):
        return self.acc == transac.account

##############################################
        
Do_Maths = []

class Total:
    def __init__(self):
        self.total = 0
        
    def do(self, montant):
        self.total +=  montant
    
    def dump(self):
        return ("Total", self.total)
Do_Maths.append(Total)

class Min:
    def __init__(self):
        self.min = None
        
    def do(self, montant):
        if self.min > montant or self.min is None:
            self.min = montant
    
    def dump(self):
        return ("Min", self.min)
Do_Maths.append(Min)

class Max:
    def __init__(self):
        self.max = None
        
    def do(self, montant):
        if self.max < montant or self.max is None:
            self.max = montant

    def dump(self):
        return ("Max", self.max)
Do_Maths.append(Max)