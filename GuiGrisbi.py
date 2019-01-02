import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operators, Operator, Maths, CSV
from collections import OrderedDict

class Request:
    def __init__(self, frequence, start, stop, inverted=False, accumulate=False, subcategories=None, accounts=None):
        self.frequence = frequence
        self.subcategories = subcategories
        self.accounts = accounts
        self.start = start
        self.stop = stop
        self.accumulate = accumulate
        self.inverted = inverted

def processRequest(rq):
    ops = Operators()

    ops.END_OF_MONTHLY = rq.frequence == "endofmonth"
    ops.MONTHLY = rq.frequence == "month"
    ops.DAILY = rq.frequence == "day"
    
    if rq.accounts is not None:
        accounts = [Account.accounts[acc] for acc in rq.accounts]
        opMaths = Maths.MathsAccounts(ops, accounts, accumulate=rq.accumulate)
        opGraph = CSV.CSV_Cumul_Accounts(ops, accounts)
    else:
        subcategories = [SubCategory.subcategories[subcat] for subcat in rq.subcategories]
        opMaths = Maths.MathsSubCats(ops, subcategories, invert=rq.inverted, accumulate=rq.accumulate)
        opGraph = CSV.CSV_Cumul_SubCategories(ops, subcategories, invert=rq.inverted)
    
    Bank.processTransactions(ops,
                             start=Bank.Date(*rq.start), 
                             stop=Bank.Date(*rq.stop))
    return {"maths": opMaths.dump(), "graph": opGraph.raw(ops.END_OF_MONTHLY)}

class GrisbiDataProvider:
    def __init__(self, filename):
        self.filename = filename
        self.valid = Grisbi.do_import(filename)
    
    def get_first_last_date(self):
        return Bank.get_first_last_date()
    
    def get_accounts(self):
        dct = OrderedDict()
        for key, acc in Account.accounts.items():
            #print "%s --> %s" % (key, acc.name)
            dct[key] = acc.name
        return dct
    
    def get_categories(self):
        dct = OrderedDict()
        for key, cat in Category.categories.items():
            #print "%s --> %s" % (key, cat.name)
            #dct[key] = cat.name
            for sub_key, sub_cat in cat.subcats.items():
                #print "\t%s --> %s" % (sub_key, sub_cat.name)
                dct[sub_key] = "%s > %s" % (cat.name, sub_cat.name)
        return dct
    
    def get_data(self, inverted, frequence, accumulate, startD, stopD, subcategories=None, accounts=None):
        
        rq = Request(frequence, startD, stopD, accumulate=accumulate, inverted=inverted, subcategories=subcategories, accounts=accounts)
        
        return processRequest(rq)
