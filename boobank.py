#! /usr/bin/python3.7

from weboob.core import Weboob
import pickle
from weboob.capabilities.base import NotLoadedType
from weboob.capabilities.base import NotAvailableType
from collections import defaultdict

import boobank_cate

# ~/git/weboob-git/src/weboob/weboob/capabilities/bank.py

def obj_to_dict(obj):
    dct = {}
    for name, val in obj.iter_fields():
        if not val: continue
        if isinstance(val, NotLoadedType): continue
        if isinstance(val, NotAvailableType): continue
        dct[name] = val
    return dct

def save():
    weboob = Weboob()
    print("Logging in ...")
    weboob.load_backends(names=['creditcooperatif'])
    
    print("Get the account list ...")
    accounts = []
    for acc in weboob.do("iter_accounts"):
        accounts.append(acc)
        print("Get '{}' transactions ...".format(acc.label))
        
        trans = [obj_to_dict(trans) for trans in weboob.do("iter_history", acc)]
        
        print("Save transactions from '{}' ...".format(acc.label))
        pickle.dump(trans, open("in/{}.pickle".format(acc.id), "wb"))
        print('')
        
    pickle.dump(accounts, open("in/accounts.pickle", "wb"))


    
def print_account(acc):
    print(f"# {acc.id} | {acc.label}\t| {acc.balance}€")


summary = defaultdict(float)
    
def print_transaction(trans):


    trans_cate = "Autres"
    trans_label = trans['label']    

    summary_key = str(trans['date'])[:7] + " "+ trans_cate
    summary[summary_key] += float(trans['amount'])


def print_summary(account_filter):
    cate_filter = [f for f in account_filter if f.startswith("+")]
    prev_month = ""
    for k, v in summary.items():
        month, _, cate = k.partition(" ")
        if prev_month != month:
            print()
            print(month)
            prev_month = month

        if cate_filter and "+"+cate not in cate_filter:
            continue
        print(f"     {v:8.2f}€ - {cate}")

def cate(trans):
    label = trans["label"]
    for cate, name_lst in boobank_cate.CATEGORIES.items():
        for name in name_lst:
            if (label.startswith(name)
                or label.endswith(name)
                or f" {name} " in label):
                return cate
    return ''

def prep(trans):
    trans_str = {}
    
    trans_str['date'] = str(trans['date'])
    try:
        trans_type = trans['type'].name
    except KeyError:
        trans_type = ""
    trans_str['type'] = f"{trans_type:<13}"
    trans_str['amount'] = f"{float(trans['amount']):8.2f}€"
    trans_str['label'] = "{:<32s}".format(boobank_cate.RENAME.get(trans['label'], trans['label']))
    trans_str['category'] = cate(trans_str)

    return trans_str

FILE_KEYS = ('date', 'type', 'amount', 'label',  'category')

def trans2string(trans_str):
    return " | ".join([trans_str[key] for key in FILE_KEYS])


def save2(acc, transactions):
     with open("in/{}.csv".format(acc.id), "w") as out_f:
         for trans in transactions:
             print(trans2string(prep(trans)), file=out_f)


             
def parse(line):
    return {k: v for k, v in zip(FILE_KEYS, line[:-1].split("|"))}

def load2(acc):
    return [parse(line) for line in
            open("in/{}.csv".format(acc.id), "r").readlines()]


def load(account_filter):
    RELOAD_ACCOUNTS = False
    if RELOAD_ACCOUNTS:
        print("Get the account list ...")
        weboob = Weboob()
        print("Logging in ...")
        weboob.load_backends(names=['creditcooperatif'])
        accounts = weboob.do("iter_accounts")
    else:
        accounts = pickle.load(open("in/accounts.pickle", "rb"))
        
    account_only = account_filter and account_filter[0] == "-"
        
    for acc in accounts:
        if account_only:
            pass
        elif account_filter and acc.id not in account_filter:
            continue
        else:
            print("")
        print_account(acc)
        if account_only: continue
        
        for trans in load2(acc):
            print(trans2string(trans))
        
    print_summary(account_filter)
    
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "save":
        print("SAVE")
        save()
    else:
        load(sys.argv[1:])



