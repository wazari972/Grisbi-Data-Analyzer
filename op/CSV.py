from op import Operator
import subprocess
import Bank

class DateValue:
    def __init__(self, date, values):
        self.date = date
        self.values = values
    

class CSV(Operator):
    uid = 1
    @staticmethod
    def currentKey(ops):
        assert ops.currentDay is not None
        assert ops.currentMonth is not None
        assert ops.currentYear is not None

        return "%s-%s-%s" % (ops.currentYear,
                             ops.currentMonth,
                             ops.currentDay)
    def __init__(self, ops):
        Operator.__init__(self, ops)
        self.transacs = []
        self.uid = CSV.uid
        self.current = None
        self.length = 1
        CSV.uid += 1
    
    def process(self, transac):           
        assert self.current is not None
        coef = -1 if self.inverted() else 1
        self.current.values[self.getKey(transac)] += transac.montant*coef
    
    def getKey(self, transac):
        return 0
    
    def getKeySet(self):
        return (0)
        
    def getNameSet(self):
        return ("Total")
            
    def getInitValues(self):
        values = {}
        for key in self.getKeySet():
            values[key] = 0
    
    def newDayValues(self, previousValues):
        values = {}
        
        for key in self.getKeySet():
            values[key] = 0
        return values
      
    def day(self):
        
        if self.current is not None:
            previous = self.current.values
            self.transacs.append(self.current)
        else:
            previous = self.getInitValues()
            
        self.current = DateValue(self.currentKey(self.ops), self.newDayValues(previous))
    #do the same for YEAR and MONTH
    month = day
    year = day

    def reset(self):
        self.current = DateValue(self.currentKey(self.ops), self.newDayValues(None))
    
    def name(self):
        return self.uid

    def dump(self):
        import csv
        fname = Bank.OUT_FOLDER+"/data-%s.csv" % self.name()
        ofile = open(fname, "wb")
        try:
            writer = csv.writer(ofile)
            lstHead = ["Date"]
            for name in self.getNameSet():
                lstHead.append(name.encode('ascii', "replace"))
            
            writer.writerow(lstHead)
                
            for dateValue in self.transacs:
                lst = [dateValue.date]
                for key in self.getKeySet():
                    lst.append(dateValue.values[key])
                writer.writerow(lst)
            ofile.close()
            return self.do_plot(fname)
        finally:
            ofile.close()
            
    def inverted(self):
        return False
class CSV_Cumul:
    def __init__(self):
        pass
        
    def newDayValues(self, previousValues):
        values = {}
        for key in self.getKeySet():
            if previousValues is None:
                values[key] = 0
            else:
                values[key] = previousValues[key]
        return values

class CSV_Accounts(CSV):
    def __init__(self, ops, accounts):
        CSV.__init__(self, ops)
        self.accounts = accounts
        
    def getKey(self, transac):
        return "Key" #transac.account.uid
        
    def getKeySet(self):
        return ["Key"] #[acc.uid for acc in self.accounts]
     
    def getNameSet(self):            
        return ["Accounts"] #[acc.name for acc in self.accounts]
    
    def getInitValues(self):
        return {"Key":0}
        values = {}
        for acc in self.accounts:
            values[acc.uid] = acc.init_value
        return values
    
    def accept(self, transac):
        return transac.account in self.accounts
        
class CSV_All_Account(CSV):
    def __init__(self, ops):
        CSV.__init__(self, ops)
        
    def getKey(self, transac):
        return transac.account.uid
        
    def getKeySet(self):
        return Bank.Account.accounts.keys()
     
    def getNameSet(self):            
        return [x.name for x in Bank.Account.accounts.values()]
    
    def getInitValues(self):
        values = {}
        for acc in Bank.Account.accounts.values():
            values[acc.uid] = acc.init_value
        return values
    
    def accept(self, transac):
        return True

    
class CSV_Cumul_Account(CSV_Cumul, CSV_All_Account):
    def __init__(self, ops):
        CSV_Cumul.__init__(self)
        CSV_All_Account.__init__(self, ops)
    
    def name(self):
        return "Accounts"
    
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_account.r", fname, Bank.OUT_FOLDER], stdout=subprocess.PIPE).communicate()
        split = out.split("\"")
        
        return [split[i] for i in range(1, len(split), 2)]

class CSV_Cumul_Accounts(CSV_Cumul, CSV_Accounts):
    def __init__(self, ops, accounts):
        CSV_Cumul.__init__(self)
        CSV_Accounts.__init__(self, ops, accounts)
    
    def name(self):
        return "Accounts"
    
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_account.r", fname, Bank.OUT_FOLDER], stdout=subprocess.PIPE).communicate()
        split = out.split("\"")
        
        return [split[i] for i in range(1, len(split), 2)]
##########################################

class CSV_Category(CSV):
    
    def __init__(self, ops, category):
        CSV.__init__(self, ops)
        self.cat = category
        
    def accept(self, transac):
        return self.cat == transac.cat

    def getKey(self, transac):
        return "%s.%s" % (transac.subcat.cat.uid, transac.subcat.uid)

        
    def getKeySet(self):
        return self.cat.subcats.keys()
            
    def getNameSet(self):            
        return [x.name for x in self.cat.subcats.values()]
        
    def inverted(self):
        return self.cat.inverted
        
    def rotate(self):
        self.reset()
        self.day()
        
        
class CSV_SubCategories(CSV):
    def __init__(self, ops, subcategories, invert=False):
        CSV.__init__(self, ops)
        self.subcategories = subcategories
        self.invert = invert
        
    def accept(self, transac):
        return transac.subcat in self.subcategories

    def getKey(self, transac):
        return transac.subcat.uid
        
    def getKeySet(self):
        return [subcat.uid for subcat in self.subcategories]
            
    def getNameSet(self):            
        return [subcat.name for subcat in self.subcategories]
        
    def inverted(self):
        return self.invert
        
    def rotate(self):
        self.reset()
        self.day()

class CSV_Cumul_SubCategories(CSV_Cumul, CSV_SubCategories):
    def __init__(self, ops, subcategories, invert=False):
        CSV_Cumul.__init__(self)
        CSV_SubCategories.__init__(self, ops, subcategories, invert)
        
    def name(self):
        return "Category-%s%s" % ("-".join([subcat.name for subcat in self.subcategories]), self.monthly and "_monthly" or "")
        
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_cate.r", fname, Bank.OUT_FOLDER], stdout=subprocess.PIPE).communicate()
        return [out.split("\"")[1]]
        
class CSV_Cumul_Category(CSV_Cumul, CSV_Category):
    def __init__(self, ops, category):
        CSV_Cumul.__init__(self)
        CSV_Category.__init__(self, ops, category)
        
    def name(self):
        return "Category-%s%s" % (self.cat.name, self.monthly and "_monthly" or "")
        
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_cate.r", fname, Bank.OUT_FOLDER], stdout=subprocess.PIPE).communicate()
        return [out.split("\"")[1]]