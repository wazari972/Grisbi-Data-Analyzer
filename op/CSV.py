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
    def currentKey():
        assert Operator.currentDay is not None
        assert Operator.currentMonth is not None
        assert Operator.currentYear is not None

        return "%s-%s-%s" % (Operator.currentYear,
                             Operator.currentMonth,
                             Operator.currentDay)
    def __init__(self):
        Operator.__init__(self)
        self.transacs = []
        self.uid = CSV.uid
        self.current = None
        self.length = 1
        CSV.uid += 1
    
    def process(self, transac):           
        assert self.current is not None
        coef = self.inverted() and -1 or 1
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
            
        self.current = DateValue(self.currentKey(), self.newDayValues(previous))
    #do the same for YEAR and MONTH
    month = day
    year = day

    def name(self):
        return self.uid

    def dump(self):
        import csv
        fname = "out/data-%s.csv" % self.name()
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
        

class CSV_All_Account(CSV):
    def __init__(self):
        CSV.__init__(self)
        
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
    def __init__(self):
        CSV_Cumul.__init__(self)
        CSV_All_Account.__init__(self)
    
    def name(self):
            return "Accounts"
    
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_account.r", fname], stdout=subprocess.PIPE).communicate()
        split = out.split("\"")
        
        return [split[i] for i in range(1, len(split), 2)]
##########################################

class CSV_Category(CSV):
    
    def __init__(self, category):
        CSV.__init__(self)
        self.cat = category
        
    def accept(self, transac):
        return self.cat == transac.cat

    def getKey(self, transac):
        return transac.subcat.uid
        
    def getKeySet(self):
        return self.cat.subcats.keys()
            
    def getNameSet(self):            
        return [x.name for x in self.cat.subcats.values()]
        
    def inverted(self):
        return self.cat.inverted
        
class CSV_Cumul_Category(CSV_Cumul, CSV_Category):
    def __init__(self, category):
        CSV_Cumul.__init__(self)
        CSV_Category.__init__(self, category)
        
    def name(self):
        return "Category-%s" % self.cat.name
        
    def do_plot(self, fname):
        out, err = subprocess.Popen(["./plot_cate.r", fname], stdout=subprocess.PIPE).communicate()
        return [out.split("\"")[1]]