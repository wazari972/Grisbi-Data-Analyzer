class Operators:
    def __init__(self):
        self.MONTHLY = False
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
        print "Year %s" % year
        self.currentYear = year
        self.currentMonth = month
        self.currentDay = day
        for oper in self.operations:
            oper.year()
            if oper.monthly:
                oper.rotate()

    def new_month(self, month, day):
        print "Month %s" % month
        self.currentMonth = month
        self.currentDay = day
        for op in self.operations:
            op.month()
            if op.monthly:
                op.rotate()

    def new_day(self, day):
        self.currentDay = day
        for op in self.operations:
            op.day()
   
    def inverted(self):
       return False
    
    def newTransaction(self, transac):
        for op in self.operations:
            if op.accept(transac):
                op.process(transac)
               
class Operator:
    def __init__(self, ops):
        self.monthly = ops.MONTHLY
        self.registered = False
        
        self.ops = ops
        self.ops.operations.append(self)

    def accept(self, transac): 
        return True
        
    def process(self, transac): pass

    def year(self): pass
    def month(self): pass
    def day(self): pass
    
    def dump(self): pass
    
    def register(self):
        self.registered = True
    
    def rotate(self): pass
    

    

