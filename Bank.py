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
    INIT_VALUES_FNAME = "Accounts-init.txt"
    init_values = None
    accounts = {}
    
    @staticmethod
    def init_init_values():
        Account.init_values = {}
        f = open(Account.INIT_VALUES_FNAME, 'r')
        for line in f.readlines():
            vals = line.split("=")
            Account.init_values[vals[0]] = int(vals[1])
        
    def __init__(self, uid, name):
        if Account.init_values is None:
            Account.init_init_values()
            
        UIDName.__init__(self, uid, name)
        Account.accounts[uid] = self
        if Account.init_values.has_key(name):
            self.init_value = Account.init_values[name]
        else:
            self.init_value = 0
            
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
        self.subcats[subcat.uid] = subcat

    def getSubCat(self, uid):
        global defaultSubCat
        try:
            return self.subcats[uid]
        except KeyError:
            return defaultSubCat

    def getSubCats(self):
        return self.subcats.values()

    @staticmethod
    def getCat(uid):
        global defaultCat
        try:
            return Category.categories[uid]
        except KeyError:
            global defaultCat, defaultSubCat
            if defaultCat is None:
                print "default", uid
                defaultCat = Category("-1", "Default")
                defaultSubCat = SubCategory("-1", "Default", "-1")
            return defaultCat
defaultCat = None 
defaultSubCat = None

class SubCategory(UIDName):
    def __init__(self, uid, name, cat_uid):
        UIDName.__init__(self, uid, name)

        self.cat = Category.getCat(cat_uid)
        self.cat.addSubCat(self)

transferCat = Category("0", "Transfer", skip=True)
transferSubCat = SubCategory("0", "Transfer", "0")

class Transaction:
    transactions = []
    def __init__(self, uid, name, date,
                 cat_uid, subcat_uid, acc_uid,
                 montant):
        Transaction.transactions.append(self)

        self.montant = montant
        self.uid = uid
        self.name = name
        self.date = date
        self.cat = Category.getCat(cat_uid)
        self.subcat = self.cat.getSubCat(subcat_uid)
        self.account = Account.getAccount(acc_uid)

def processTransactions():
	if len(Transaction.transactions) == 0:
		return
	from op import Operator
	sorted_transacs = sorted(Transaction.transactions, lambda x, y : cmp(str(x.date), str(y.date)))
	currentDay = sorted_transacs[0].date.day
	currentMonth = sorted_transacs[0].date.month
	currentYear = sorted_transacs[0].date.year

	Operator.new_year(currentYear, currentMonth, currentDay)
	for transac in sorted_transacs:
		while (currentDay != transac.date.day
                    or currentMonth != transac.date.month
                    or currentYear != transac.date.year):
			currentDay = (currentDay + 1) % 32
			if currentDay == 0:
				currentDay += 1
				currentMonth = (currentMonth + 1) % 13
				if currentMonth == 0:
					currentMonth += 1
					currentYear += 1
					Operator.new_year(currentYear, currentMonth, currentDay)
				else:
					Operator.new_month(currentMonth, currentDay)
			else:
				Operator.new_day(currentDay)
		Operator.newTransaction(transac)
	pass

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
