class Operators:
    def __init__(self):
        self.MONTHLY = False
        self.DAILY = False
        self.END_OF_MONTHLY = False
        
        self.operations = []
        
        self.currentDay = None
        self.currentMonth = None
        self.currentYear = None    
        
    def init_date(self, year, month, day):
        self.currentYear = year
        self.currentMonth = month
        self.currentDay = day
        for oper in self.operations:
            oper.day()
    
    def new_year(self, year, month, day):
        #print "Year %s" % year
        self.currentYear = year
        self.currentMonth = month
        self.currentDay = day
        for oper in self.operations:
            oper.year()
            if oper.monthly or oper.end_of_monthly:
                oper.rotate(save_last=oper.end_of_monthly)

    def new_month(self, month, day):
        #print "Month %s" % month
        self.currentMonth = month
        self.currentDay = day
        for oper in self.operations:
            oper.month()
            if oper.monthly or oper.end_of_monthly:
                oper.rotate(save_last=oper.end_of_monthly)
            
    def new_day(self, day):
        self.currentDay = day
        for oper in self.operations:
            oper.day()
            if oper.daily:
                oper.rotate()
    
    def newTransaction(self, transac):
        for op in self.operations:
            if op.accept(transac):
                op.process(transac)
               
class Operator:
    def __init__(self, ops):
        self.monthly = ops.MONTHLY
        self.daily = ops.DAILY
        self.end_of_monthly = ops.END_OF_MONTHLY
        self.registered = False
        
        self.ops = ops
        self.ops.operations.append(self)

    def accept(self, transac): 
        return True
        
    def process(self, transac): pass

    def year(self): pass
    def month(self): pass
    def day(self): pass
    
    def raw(self): pass
    def dump(self): pass
    
    def register(self):
        self.registered = True
    
    def rotate(self, save_last=False): pass
    

    

