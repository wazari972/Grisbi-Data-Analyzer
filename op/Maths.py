from op import Operator

from Bank import *

class Maths(Operator):
    def __init__(self):
        global Do_Maths
        Operator.__init__(self)
        self.doers = []
        
        for doer in self.get_doers():
            self.doers.append(doer)
        self.daily = 0
        
    def get_doers(self):
        return ()
        
    def process(self, transac):
        self.daily += transac.montant
    
    def day(self):
        coef = self.inverted() and -1 or 1
        for doer in self.doers:
            doer.do(self.daily*coef)
        self.daily = 0

    def dump(self):
        ret = {}
        for doer in self.doers:
            ret = dict(ret.items() + doer.dump().items())
        return ret
        
    def init_value():
        return None
###########################################


        
class MathsCatSubCat(Maths):
    def __init__(self, cat):
        Maths.__init__(self)
        self.cat = cat
        self.do = True
        
        if isinstance(cat, Category):
            self.subcats = [MathsCatSubCat(subcat) for subcat in cat.subcats.values()]
        else:
            assert isinstance(cat, SubCategory)
            
    def accept(self, transac):
        if isinstance(self.cat, Category):
            return self.cat == transac.cat
        else:
            return self.cat == transac.subcat
            
    def get_doers(self):
        return (Max(), Total(), Avg())
        
    def inverted(self):
        return self.cat.inverted

class MathsAccount(Maths):
    def __init__(self, account):
        self.acc = account
        if account is None:
            self.init_value = 0
            for acc in Account.accounts.values():
                self.init_value += acc.init_value
        else:
            self.init_value = account.init_value
        Maths.__init__(self)

    def accept(self, transac):
        return self.acc is None or self.acc == transac.account

    def get_doers(self):
        return (Total(self.init_value), MinMaxTotal(self.init_value))
        
    def inverted(self):
        return False
        
##############################################

class Total:
    def __init__(self, init_value=0):
        self.total = init_value
        
    def do(self, montant):
        self.total +=  montant
    
    def dump(self):
        return {"Total": self.total}

class MinMaxTotal:
    def __init__(self, init_value=0):
        self.total = init_value
        self.mintot = None
        self.maxtot = None
        
    def do(self, montant):
        self.total +=  montant
        if self.mintot > self.total or self.mintot is None:
            self.mintot = self.total
        if self.maxtot < self.total or self.maxtot is None:
            self.maxtot = self.total
            
    def dump(self):
        return {"Min value": self.mintot, "Max value": self.maxtot}

class Max:
    def __init__(self):
        self.max = None
        
    def do(self, montant):
        if self.max < montant or self.max is None:
            self.max = montant

    def dump(self):
        return {"Max": self.max}

class Avg:
    def __init__(self):
        self.total = 0
        self.count = 0
        
    def do(self, montant):
        self.total += montant
        self.count += 1
        
    def dump(self):
        daily = self.total/self.count
        return {"Daily": daily,
                "Monthly": daily*30.5
                }