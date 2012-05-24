from collections import OrderedDict
from collections import defaultdict
from op import Operator
from Bank import *

class Maths(Operator):
    def __init__(self, ops, accumulate):
        global Do_Maths
        Operator.__init__(self, ops)
        self.doers = []
        
        for doer in self.get_doers():
            self.doers.append(doer)
        self.daily_val = defaultdict(lambda : 0)
        self.dumps = defaultdict(lambda : [])
        self.accumulate = accumulate
        
    def get_doers(self):
        return ()
        
    def process(self, transac):
        self.daily_val[self.getKey(transac)] += transac.montant
    
    def getKey(self, transac):
        return "All"
    
    def getKeys(self):
        return ["All"]
    
    def day(self):
        coef = self.inverted() and -1 or 1
        
        for key in self.getKeys():
            for doer in self.doers:
                doer.do(key, self.daily_val[key]*coef)
                
        for key in self.daily_val.keys():
            self.daily_val[key] = 0

    def dump(self, intermediate=False):
        for key in self.getKeys():
            ret = {}
            for doer in self.doers:
                ret = OrderedDict(ret.items() + doer.dump(key).items())
            self.dumps[key].append(ret)
            
        dumps = self.dumps
        if not intermediate:
            self.dumps = defaultdict(lambda : [])
        return dumps
        
    def init_value():
        return None
        
    def rotate(self):
        self.dump(intermediate=True)
###########################################

class MathsSubCats(Maths):
    def __init__(self, ops, subcats, accumulate=False, invert=False):
        Maths.__init__(self, ops, accumulate)
        self.do = True
        self.subcats = subcats
        self.invert = invert
        
    def accept(self, transac):
        return transac.subcat in self.subcats
    
    def getKey(self, transac):
        if self.accumulate: return "All"
        
        return "%s.%s" % (transac.subcat.cat.uid, transac.subcat.uid)
    
    def getKeys(self):
        if self.accumulate: return ["All"]
        
        return ["%s.%s" % (subcat.cat.uid, subcat.uid) for subcat in self.subcats]
    
    def get_doers(self):
        doers = [Max(), Total()]
        
        if not self.ops.DAILY:
            if not self.ops.MONTHLY:
                doers.append(Avg(is_daily=False))
            doers.append(Avg(is_daily=True))
        
        return doers
            
    def inverted(self):
        return self.invert

class MathsAccounts(Maths):
    def __init__(self, ops, accounts, accumulate=False):
        self.accounts = accounts
        self.init_val = 0
        for acc in accounts:
            self.init_val += acc.init_value
        self.empty = len(accounts) == 0
        Maths.__init__(self, ops, accumulate)
        
    def accept(self, transac):
        return self.empty or transac.account in self.accounts
        
    def getKey(self, transac):
        if self.accumulate or self.empty:
            return "All"
        else:
            return transac.account.uid
            
    def getKeys(self):
        if self.accumulate or self.empty:
            return ["All"]
        else:
            return [account.uid for account in self.accounts]
            
    def get_doers(self):
        return [MinMaxTotal(self.init_val), InOut()]
        
    def inverted(self):
        return False
        
##############################################

class Total:
    def __init__(self, init_value=0):
        self.init_value = init_value
        self.total = defaultdict(lambda : init_value)
        
    def do(self, key, montant):
        self.total[key] +=  montant
    
    def dump(self, key):
        ret = {"Total": self.total[key]}
        self.total = defaultdict(lambda : 0)
        return ret

class MinMaxTotal:
    def __init__(self, init_value=0):
        self.init_value = init_value
        self.total = defaultdict(lambda : init_value)
        self.mintot = defaultdict(lambda : init_value)
        self.maxtot = defaultdict(lambda : init_value)
        
    def do(self, key, montant):
        self.total[key] +=  montant
        self.mintot[key] = min(self.mintot[key], self.total[key])
        self.maxtot[key] = max(self.maxtot[key], self.total[key])
            
    def dump(self, key):
        ret = OrderedDict([("Mini", self.mintot[key]), ("Maxi", self.maxtot[key]), ("Total", self.total[key])])
        self.mintot[key] = self.total[key]
        self.maxtot[key] = self.total[key]
        return ret

class Max:
    def __init__(self):
        self.max = defaultdict(lambda : None)
        
    def do(self, key, montant):
        if self.max[key] is None or abs(self.max[key]) < abs(montant):
            self.max[key] = montant

    def dump(self, key):
        ret = {"Max": self.max[key]}
        self.max[key] = None
        return ret

class InOut:
    def __init__(self):
        self.in_ = defaultdict(lambda : 0)
        self.out_ = defaultdict(lambda : 0)
        
    def do(self, key, montant):
        if montant > 0:
            self.in_[key] +=  montant
        else:
            self.out_[key] +=  montant
            
    def dump(self, key):
        ret = OrderedDict([("In", self.in_[key]), ("Out", self.out_[key]), ("Diff", self.in_[key]+self.out_[key])])
        self.in_[key] = 0
        self.out_[key] = 0
        return ret
        
class Avg:
    def __init__(self, is_daily):
        self.total = defaultdict(lambda : 0)
        self.count = defaultdict(lambda : 0)
        self.is_daily = is_daily
        
    def do(self, key, montant):
        self.total[key] += montant
        self.count[key] += 1
        
    def dump(self, key):
        if self.count[key] != 0:
            daily = self.total[key]/self.count[key]
        else:
            daily = 0
            
        self.total[key] = 0
        self.count[key] = 0
        if self.is_daily:
            return {"Daily": daily}
        else:
            return {"Monthly": daily*30.5}