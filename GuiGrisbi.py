import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operators, Operator, Maths, CSV
from collections import OrderedDict

class Request:
    def __init__(self, frequence, start, stop, subcategories=None, accounts=None):
        self.frequence = frequence
        self.subcategories = subcategories
        self.accounts = accounts
        self.start = start
        self.stop = stop
        
class MathRequest(Request):
    def __init__(self, frequence, start, stop, subcategories=None, accounts=None):
        Request.__init__(self, frequence, start, stop, subcategories, accounts)

class GraphRequest(Request):
    def __init__(self, frequence, start, stop, inverted=False, legend=False, subcategories=None, accounts=None):
        Request.__init__(self, frequence, start, stop, subcategories, accounts)
        self.legend = legend
        self.inverted = inverted

def processRequest(rq):
    ops = Operators()

    ops.MONTHLY = rq.frequence == "month"
    ops.DAILY = rq.frequence == "day"
    
    if rq.accounts is not None:
        accounts = [Account.accounts[acc] for acc in rq.accounts]
        if isinstance(rq, MathRequest):
            raise("MathRequest: not yet")
            op = Maths.MathsAccounts(ops, accounts)
        elif isinstance(rq, GraphRequest):
            op = CSV.CSV_Cumul_Accounts(ops, accounts)
        else:
            raise Exception("Unknown request type")
    else:
        subcategories = [SubCategory.subcategories[subcat] for subcat in rq.subcategories]
        if isinstance(rq, MathRequest):
            raise("MathRequest: not yet")
            op = Maths.MathsSubCats(ops, subcategories)
        elif isinstance(rq, GraphRequest):
            op = CSV.CSV_Cumul_SubCategories(ops, subcategories, invert=rq.inverted)
        else:
            raise Exception("Unknown request type")
    
    Bank.processTransactions(ops,
                             start=Bank.Date(*rq.start), 
                             stop=Bank.Date(*rq.stop))
    return op.raw()


class GrisbiDataProvider:
    def __init__(self, filename="kevin.gsb"):
        Grisbi.do_import(filename)
    
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
    
    def get_data(self, inverted, frequence, startD, stopD, subcategories=None, accounts=None):
        
        rq = GraphRequest(frequence, startD, stopD, inverted=inverted, subcategories=subcategories, accounts=accounts)
        
        return processRequest(rq)