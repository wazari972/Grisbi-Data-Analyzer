class Operator:
    MONTHLY = False
    
    operations = []

    currentDay = None
    currentMonth = None
    currentYear = None

    def __init__(self):
        self.monthly = Operator.MONTHLY
        self.registered = False
        Operator.operations.append(self)

    def accept(self, transac): return True
    def process(self, transac): pass

    def year(self): pass
    @staticmethod
    def init_date(year, month, day):
        Operator.currentYear = year
        Operator.currentMonth = month
        Operator.currentDay = day
        for oper in Operator.operations:
            oper.day()
    @staticmethod
    def new_year(year, month, day):
        print "Year %s" % year
        Operator.currentYear = year
        Operator.currentMonth = month
        Operator.currentDay = day
        for oper in Operator.operations:
            oper.year()
            if oper.monthly:
                oper.rotate()
        
    def month(self): pass
    @staticmethod
    def new_month(month, day):
        print "Month %s" % month
        Operator.currentMonth = month
        Operator.currentDay = day
        for op in Operator.operations:
            op.month()
            if op.monthly:
                op.rotate()

    def day(self): pass
    @staticmethod
    def new_day(day):
        Operator.currentDay = day
        for op in Operator.operations:
            op.day()
            
    def dump(self): pass
    def register(self):
        self.registered = True
    
    def rotate(self): pass
    
    @staticmethod
    def inverted():
        return False
    
    @staticmethod
    def newTransaction(transac):
        for op in Operator.operations:
            if op.accept(transac):
                op.process(transac)
