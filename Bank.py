import calendar

IN_FOLDER = "in"
OUT_FOLDER = "out/"

name = None
def set_name(name_):
    global name, OUT_FOLDER
    assert name is None
    name = name_
    OUT_FOLDER += name
    import os
    try:
        os.mkdir(OUT_FOLDER)
    except OSError:
        pass
    
def get_name():
    global name
    return name
    
class Date:
    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
    def __str__(self):
        return "%s/%02d/%02d" % (self.year, self.month, self.day)
    def __repr__(self):
        return str(self)

class UIDName:
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name
        self.ops = []

    def registerOp(self, op):
        self.ops.append(op)
        op.register()

    def operations(self):
        return self.ops

class Account(UIDName):
    accounts = {}
        
    def __init__(self, uid, name, init_value=0):
        UIDName.__init__(self, uid, name)
        Account.accounts[uid] = self
        self.init_value = init_value
            
    @staticmethod
    def getAccount(acc_uid):
        global defaultAccount
        try:
            return Account.accounts[acc_uid]
        except:
            global defaultAccount
            if defaultAccount is None:
                defaultAccount = Account("-1", "Default")
            return defaultAccount
defaultAccount = None

class Category(UIDName):
    categories = {}
    def __init__(self, uid, name, inverted=False, skip=False):
        UIDName.__init__(self, uid, name)
        Category.categories[uid] = self
        self.inverted = inverted
        self.subcats = {}
        self.skip = skip
            
    def addSubCat(self, subcat):
        self.subcats["%s.%s" % (self.uid, subcat.uid)] = subcat

    def getSubCat(self, uid):
        try:
            return self.subcats[uid] 
        except:
            return SubCategory("0", "Default", uid)

    def getSubCats(self):
        return self.subcats.values()

    @staticmethod
    def getCat(uid):
        global defaultCat
        try:
            return Category.categories[uid]
        except KeyError:
            global defaultCat
            if defaultCat is None:
                defaultCat = Category("-1", "Default")
            return defaultCat
defaultCat = None 

class SubCategory(UIDName):
    subcategories = {}
    def __init__(self, uid, name, cat_uid):
        UIDName.__init__(self, uid, name)
        SubCategory.subcategories["%s.%s" % (cat_uid, uid)] = self
        self.cat = Category.getCat(cat_uid)
        self.cat.addSubCat(self)
        self.inverted = self.cat.inverted
        
transferCat = Category("0", "Transfer", skip=True)
transferSubCat = SubCategory("0", "Transfer", "0")

class Transaction:
    transactions = []
    def __init__(self, uid, name, date,
                 cat_uid, subcat_uid, acc_uid,
                 montant, internal):
        Transaction.transactions.append(self)

        self.montant = montant
        self.uid = uid
        self.name = name
        self.date = date
        self.cat = Category.getCat(cat_uid)
        self.subcat = self.cat.getSubCat(subcat_uid)
        self.account = Account.getAccount(acc_uid)
        self.internal = bool(internal)
        
    @staticmethod
    def import_finish():
        Transaction.transactions = sorted(Transaction.transactions, lambda x, y : cmp(str(x.date), str(y.date)))

def get_first_last_date():
    if len(Transaction.transactions) == 0:
        return None, None
    
    return Transaction.transactions[0].date, Transaction.transactions[-1].date
    
def processTransactions(ops, start=None, stop=None):
    if len(Transaction.transactions) == 0:
        return
    from op import Operator
    
    
    if start is None:
        start = Transaction.transactions[0].date
    if stop is None:
        stop = Transaction.transactions[-1].date
        
    first = True
    for transac in Transaction.transactions:
        if first:
            currentDay = transac.date.day
            currentMonth = transac.date.month
            currentYear = transac.date.year
            
            if (currentYear < start.year
             or currentYear == start.year and currentMonth < start.month
             or currentYear == start.year and currentMonth == start.month and currentDay < start.day):
                 #continue until we reach the start date
                 continue
            
        while not (currentDay == transac.date.day
               and currentMonth == transac.date.month
               and currentYear == transac.date.year):
            currentDay += 1
            if currentDay > calendar.monthrange(currentYear, currentMonth)[1]:
                currentDay = 1
                currentMonth += 1
                if currentMonth == 13:
                    currentMonth = 1
                    currentYear += 1
                    ops.new_year(currentYear, currentMonth, currentDay)
                else:
                    ops.new_month(currentMonth, currentDay)
            else:
                ops.new_day(currentDay)
                
        if first:
            #print "Start: ", (currentYear, currentMonth, currentDay)
            ops.init_date(currentYear, currentMonth, currentDay)
            first = False
            
        ops.newTransaction(transac)
        if (currentYear > stop.year
         or currentYear == stop.year and currentMonth > stop.month
         or currentYear == stop.year and currentMonth == stop.month and currentDay > stop.day):
            #break if we're after the stop date
            break

def printOperationResults():
    
    for acc in Account.accounts.values():
        for op in acc.operations():
            op.dump()
    for cat in Category.categories.values():
        for op in cat.operations():
            op.dump()
        for subcat in cat.getSubCats():
            for op in subcat.operations():
                op.dump()
