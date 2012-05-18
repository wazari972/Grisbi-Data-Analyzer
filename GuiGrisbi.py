import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operators, Operator, Maths, CSV
from collections import OrderedDict

class Request:
    def __init__(self, monthly, start, stop, subcategories=None, accounts=None):
        self.monthly = monthly
        self.subcategories = subcategories
        self.accounts = accounts
        self.start = start
        self.stop = stop
        
class MathRequest(Request):
    def __init__(self, monthly, start, stop, subcategories=None, accounts=None):
        Request.__init__(self, monthly, start, stop, subcategories, accounts)

class GraphRequest(Request):
    def __init__(self, monthly, start, stop, inverted=False, legend=False, subcategories=None, accounts=None):
        Request.__init__(self, monthly, start, stop, subcategories, accounts)
        self.legend = legend
        self.inverted = inverted

def processRequest(rq):
    ops = Operators()

    ops.MONTHLY = rq.monthly
    
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
            dct[key] = cat.name
            for sub_key, sub_cat in cat.subcats.items():
                #print "\t%s --> %s" % (sub_key, sub_cat.name)
                dct[sub_key] = "%s > %s" % (cat.name, sub_cat.name)
        return dct
    
    def get_data(self, inverted, monthly, startD, stopD, subcategories=None, accounts=None):
        #GraphRequest(False, (2011, 8, 1), (2012, 8, 1), inverted=True, subcategories=["6.9", "8.2","18.12"]),
        #GraphRequest(True, (2011, 8, 1), (2012, 8, 1), accounts=["2"]),
        
        rq = GraphRequest(monthly, startD, stopD, inverted=inverted, subcategories=subcategories, accounts=accounts)
        
        data = processRequest(rq)
        return [dct.values()[0] for dct in data.values() if len(dct.values()) != 0]