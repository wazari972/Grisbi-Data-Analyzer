import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operator, Maths, CSV
import Latex

###############################
Grisbi.do_import("comptes.gsb")
###############################



cvs_cat_ops = []
maths_cat_ops = []
for cat in Category.categories.values():
    cvs_cat_ops.append(CSV.CSV_Cumul_Category(cat))
    maths_cat_ops.append(Maths.MathsCat(cat))
    
csvTotal = CSV.CSV_Cumul_Account()
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

for cpt in range(0, len(Account.accounts)):
    acc = Account.accounts.values()[cpt]
    Latex.new_section(acc.name)
    Latex.add_graph(acc_files[cpt])
    Latex.start_maths()
    for math in maths_acc_ops[cpt].dump():
        Latex.add_math(math[0], math[1])

Latex.new_part("Categories")
print "Dump category information ..."
for cpt in range(0, len(cvs_cat_ops)):
    op = cvs_cat_ops[cpt]
    Latex.new_section(op.cat.name)
    Latex.add_graph(op.dump()[0])
    Latex.start_maths()
    for math in maths_cat_ops[cpt].dump():
        Latex.add_math(math[0], math[1])
Latex.dump()

