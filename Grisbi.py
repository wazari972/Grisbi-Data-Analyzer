import lxml
from lxml import etree

from Bank import Account, Category, SubCategory, Transaction, Date

def do_import(filename):
    Grisbi = etree.parse(filename).getroot()

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
        sub_cat_id = transaction.get("Sca")
        acc_id = transaction.get("Ac")
        
        uid = transaction.get("Nb")
        name = transaction.get("No").encode('ascii', "replace")
        dt = transaction.get("Dt").split("/")
        date = Date(dt[2], dt[0], dt[1])
        Transaction(uid, name, date,
                    cat_id, sub_cat_id, acc_id,
                    float(transaction.get("Am")))

