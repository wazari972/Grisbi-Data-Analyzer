import os

import lxml
from lxml import etree
import Bank
from Bank import Account, Category, SubCategory, Transaction, Date

def do_import(filename):
    if not os.path.exists(filename):
        return
    Grisbi = etree.parse(filename).getroot()

    Account.empty()
    SubCategory.empty()
    Transaction.empty()
    
    for account in Grisbi.findall("Account"):
        Account(account.get("Number"), account.get("Name"), float(account.get("Initial_balance")))

    for category in Grisbi.findall("Category"):
        Category(category.get("Nb"), category.get("Na"), category.get("Kd") == "1")

    for sub_category in Grisbi.findall("Sub_category"):
        SubCategory(sub_category.get("Nb"),
        sub_category.get("Na"),
        sub_category.get("Nbc"))

    for transaction in Grisbi.findall("Transaction"):
        cat_id = transaction.get("Ca")
        sub_cat_id = "%s.%s" % (cat_id, transaction.get("Sca"))
        acc_id = transaction.get("Ac")
        
        uid = transaction.get("Nb")
        name = transaction.get("No").encode('ascii', "replace")
        dt = transaction.get("Dt").split("/")
        date = Date(dt[2], dt[0], dt[1])
        montant = float(transaction.get("Am"))
        
        internal = cat_id is "0"
        #import random ; montant = montant*(4*random.random()-2)
        Transaction(uid, name, date,
                    cat_id, sub_cat_id, acc_id,
                    montant, internal)

    Transaction.import_finish()
