#! /usr/bin/python2
import sys

import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operators, Operator, Maths, CSV
import Latex

###############################
print sys.argv
try:
    filename = sys.argv[1]
except:
    filename = "kevin.gsb"
Grisbi.do_import(filename)
###############################

ops = Operators()

ops.MONTHLY = True
cvs_cat_mops = []
maths_cat_mops = []
for cat in Category.categories.values():
    cvs_cat_mops.append(CSV.CSV_Cumul_Category(ops, cat))
    maths_cat_mops.append(Maths.MathsCatSubCat(ops, cat))
    
mathsTotal_mop = Maths.MathsAccount(ops, None)
maths_acc_mops = []
for acc in Account.accounts.values():
    maths_acc_mops.append(Maths.MathsAccount(ops, acc))
    
ops.MONTHLY = False
cvs_cat_ops = []
maths_cat_ops = []
for cat in Category.categories.values():
    cvs_cat_ops.append(CSV.CSV_Cumul_Category(ops, cat))
    maths_cat_ops.append(Maths.MathsCatSubCat(ops, cat))
        
csvTotal_op = CSV.CSV_Cumul_Account(ops)
mathsTotal_op = Maths.MathsAccount(ops, None)
maths_acc_ops = []
for acc in Account.accounts.values():
    maths_acc_ops.append(Maths.MathsAccount(ops, acc))
    
print "Process the transactions"
Bank.processTransactions(ops,
                         start=Bank.Date(2011, 8, 1), 
                         stop=Bank.Date(2011, 10, 1))

print "Dump account information ..."
acc_files = csvTotal_op.dump()

Latex.new_part("Accounts")
Latex.new_section("Total")
Latex.add_graph(acc_files[-1])
Latex.start_maths()
Latex.add_maths("Total", mathsTotal_op.dump())
Latex.stop_maths()

Latex.start_maths()
Latex.add_maths("Total", mathsTotal_mop.dump())
Latex.stop_maths()
    
for cpt in range(0, len(Account.accounts)):
    acc = Account.accounts.values()[cpt]
    Latex.new_section(acc.name)
    print "\t%s ..." % acc.name
    Latex.add_graph(acc_files[cpt])
    
    Latex.start_maths()
    Latex.add_maths(acc.name, maths_acc_ops[cpt].dump())
    Latex.stop_maths()
    
    Latex.start_maths()
    Latex.add_maths(acc.name, maths_acc_mops[cpt].dump())
    Latex.stop_maths()
    
print "Dump category information ..."
Latex.new_part("Categories")
for cpt in range(0, len(cvs_cat_ops)):
    op = cvs_cat_ops[cpt]
    mop = cvs_cat_mops[cpt]
    if op.cat.skip:
        continue
    print "\t%s ..." % op.cat.name
    Latex.new_section("%s (%s)" % (op.cat.name, op.cat.inverted and "Debit" or "Credit"))
    
    Latex.start_maths()
    Latex.add_maths(op.cat.name, maths_cat_ops[cpt].dump())
        
    for subcat_op in maths_cat_ops[cpt].subcats:
        name = subcat_op.cat.name
        Latex.add_maths(name, subcat_op.dump())
    Latex.stop_maths()
    
    Latex.start_maths()
    Latex.add_maths(op.cat.name, maths_cat_mops[cpt].dump())
    
    for subcat_mop in maths_cat_mops[cpt].subcats:
        name = subcat_mop.cat.name
        Latex.add_maths(name, subcat_mop.dump())
    Latex.stop_maths()
    
    Latex.add_graph(op.dump()[0], mop.dump()[0])
Latex.dump()

