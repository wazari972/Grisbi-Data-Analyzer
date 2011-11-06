#! /usr/bin/python2

import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operator, Maths, CSV
import Latex

###############################
Grisbi.do_import("in/comptes.gsb")
###############################

cvs_cat_ops = []
maths_cat_ops = []
for cat in Category.categories.values():
    cvs_cat_ops.append(CSV.CSV_Cumul_Category(cat))
    maths_cat_ops.append(Maths.MathsCatSubCat(cat))
    
csvTotal = CSV.CSV_Cumul_Account()
mathsTotal = Maths.MathsAccount(None)
maths_acc_ops = []
for acc in Account.accounts.values():
    maths_acc_ops.append(Maths.MathsAccount(acc))


print "Process the transactions"
Bank.processTransactions()

print "Dump account information ..."
acc_files = csvTotal.dump()

Latex.new_part("Accounts")
Latex.new_section("Total")
Latex.add_graph(acc_files[-1])
Latex.start_maths()
Latex.add_maths("Total", mathsTotal.dump())
Latex.stop_maths()
    
    
for cpt in range(0, len(Account.accounts)):
    acc = Account.accounts.values()[cpt]
    Latex.new_section(acc.name)
    print "\t%s ..." % acc.name
    Latex.add_graph(acc_files[cpt])
    
    Latex.start_maths()
    Latex.add_maths(acc.name, maths_acc_ops[cpt].dump())
    Latex.stop_maths()
    
print "Dump category information ..."
Latex.new_part("Categories")
for cpt in range(0, len(cvs_cat_ops)):
    op = cvs_cat_ops[cpt]
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
    Latex.add_graph(op.dump()[0])
Latex.dump()

