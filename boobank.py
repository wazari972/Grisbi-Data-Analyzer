#! /usr/bin/python3.7

from weboob.core import Weboob
import pickle
from weboob.capabilities.base import NotLoadedType
from weboob.capabilities.base import NotAvailableType
from weboob.capabilities.bank import TransactionType
from collections import defaultdict
import os

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


def int_to_TransactionType(val):
    for name, value in TransactionType._items:
        if val == value:
            return name
    return ""

_weboob = None
_accounts = None
def login_weboob():
    global _weboob, _accounts

    if not _weboob:
        _weboob = Weboob()
        print("Logging in with Weboob...")

        _weboob.load_backends(names=['CreditCooperatif', 'creditcooperatif'])

        print("Get the account list ...")
        _accounts = list([web_acc for web_acc in _weboob.do("iter_accounts")])
        if not  _accounts:
            exit(1)
        print("Weboob ready!")

    return _weboob, _accounts


class Account(dict):
    def __init__(self, web_acc):
        super().__init__(self)

        self.web_acc = web_acc
        self.transactions = None
        self._transactions_repr = None
        self.new_transactions = 0

        self.id = self.web_acc.id
        self.label = self.web_acc.label

    def _update_trans_repr(self):
        self._transactions_repr = [repr(trans) for trans in self.transactions]

        self.transactions.sort()
        self._transactions_repr.sort()

    def contains_trans(self, trans):
        return repr(trans) in self._transactions_repr

    def _insert_trans(self, trans):
        print(f"New: {trans}")

        self.transactions.append(trans)

        assert not repr(trans) in self._transactions_repr
        self._transactions_repr.append(repr(trans))

        self.transactions.sort()
        self._transactions_repr.sort()

    def save_to_file(self):
        name = "_".join(self.web_acc.label.strip().split())
        with open("in/{}.csv".format(name), "w") as out_f:
            for trans in sorted(self.transactions):
                print(trans, file=out_f)

    def load_from_file(self):
        name = "_".join(self.web_acc.label.strip().split())
        try:
            self.transactions = [Transaction.from_line(line) for line in
                                 open("in/{}.csv".format(name), "r").readlines()]
        except FileNotFoundError as e:
            print(e)
            self.transactions = []
            return

        for trans in self.transactions:
            trans["amount"] = float(trans["amount"])

        self._update_trans_repr()

    def update_from_web(self):
        weboob, web_accounts = login_weboob()
        print(f"Get transaction updates for {self} ...")
        for web_trans in weboob.do("iter_history", self.web_acc):
            trans = Transaction.from_weboob(web_trans)

            if self.contains_trans(trans): continue

            self.new_transactions += 1
            self._insert_trans(trans)
        print(f"  |> {self.new_transactions} updates ...")

    def __str__(self):
        return f"# {self.web_acc.id} | {self.web_acc.label}\t| {float(self.web_acc.balance):8.2f}€"


class Transaction(dict):
    FILE_KEYS = ('date', 'type', 'amount', 'label',  'category')

    @staticmethod
    def from_weboob(web_trans):
        trans = Transaction()

        trans['date'] = str(web_trans.date)

        trans_type = int_to_TransactionType(web_trans.type)
            
        trans['type'] = trans_type
        trans['amount'] = float(web_trans.amount)
        label = web_trans.label
        trans['label'] = boobank_cate.RENAME.get(label, label)
        trans['category'] = trans.find_category()

        return trans

    @staticmethod
    def from_line(line):
        trans = Transaction({k: v.strip() for k, v in
                             zip(Transaction.FILE_KEYS,
                                 line[:-1].replace("€", "").split("|"))})

        cate = trans.find_category()
        if not trans['category']:
            trans['category'] = cate # no cate yet, find one (or not)
        else:
            # already has a cate, update it only if we can find one
            if trans.find_category():
                trans['category'] = trans.find_category()

        return trans

    def find_category(self):
        label = self["label"]

        try: label = boobank_cate.RENAME[label]
        except KeyError: pass
        label = label.lower()
        for cate, name_lst in boobank_cate.CATEGORIES.items():
            for name in name_lst:
                name = name.lower()
                if (label.startswith(name)
                    or label.endswith(name)
                    or f" {name} " in label):
                    return cate

        return ''

    def __str__(self):
        return " | ".join([self['date'],
                           f"{self['type']:<13}",
                           f"{float(self['amount']):8.2f}€",
                           f"{self['label']:<32s}",
                           self['category']])

    def __repr__(self):
        keys = []
        keys[:] = Transaction.FILE_KEYS
        keys.remove('category')

        return " | ".join([str(self[key]).strip() for key in keys])

    def __lt__(self, other):
         return self["date"] < other["date"]

class Summary():
    def __init__(self, account_filter):
        self.account_filter = account_filter

        self.by_category_amount = defaultdict(float)
        self.by_category_trans = defaultdict(list)

        self.accounts = []

    def add_transaction(self, acc, trans):
        trans_cate = trans['category']
        if not trans_cate: trans_cate = "*"

        cate_key = str(trans['date'])[:7] + " "+ trans_cate
        self.by_category_amount[cate_key] += float(trans['amount'])
        self.by_category_trans[cate_key] += [trans]

    def print_cate(self, details):
        cate_filter = [f for f in self.account_filter if f.startswith("+")]
        prev_month = ""

        month_total = 0
        def print_month_total():
            nonlocal month_total
            print("     * ========= -")
            print(f"     * {month_total:8.2f}€")
            month_total = 0

        for month_cate in sorted(self.by_category_amount.keys()):
            total_amount = self.by_category_amount[month_cate]
            month, _, cate = month_cate.partition(" ")
            if prev_month != month:
                if prev_month:
                    print_month_total()
                    print()
                print(month)
                prev_month = month

            if cate_filter and "+"+cate not in cate_filter:
                continue
            if cate != "Carte/total":
                month_total += total_amount
            print(f"     * {total_amount:8.2f}€ - {cate}")
            if not details: continue

            for trans in self.by_category_trans[month_cate]: print(f"     {trans}")
            print("")
        print_month_total()

    def add_account(self, acc):
        self.accounts.append(acc)

    def print_acc_update(self):
        for acc in self.accounts:
            print(f"{acc} |> {acc.new_transactions} new transactions")


def get_opt(name, default):
    has = name in sys.argv
    if has:
        sys.argv.remove(name)
        return True
    return default

class git():
    @staticmethod
    def pull():
        os.system("git -C in pull | grep -v 'eady up to dat'")

    @staticmethod
    def commit_all_and_push():
        os.system("git -C in diff && git -C in commit -am 'update' && git -C in push")
        
def print_help():
    print("not yet ...")


def main():
    UPDATE_HISTORY = get_opt('update', False)
    RELOAD_ACCOUNTS = get_opt('reload', UPDATE_HISTORY)
    SAVE_HISTORY = get_opt('save', UPDATE_HISTORY)
    PRINT_CATE = get_opt('cate', not UPDATE_HISTORY)
    DETAIL_BY_CATE = get_opt('detail', False)
    HELP = get_opt('--help', get_opt('-h', False))
    
    if HELP:
        print_help()
        return

    git.pull()

    if os.path.exists("in/accounts.pickle") and not RELOAD_ACCOUNTS:
        web_accounts = pickle.load(open("in/accounts.pickle", "rb"))
    else:
        _, web_accounts = login_weboob()
        pickle.dump(web_accounts, open("in/accounts.pickle", "wb"))

    account_filter = sys.argv[1:]

    account_only = account_filter and account_filter[0] == "-"

    summary = Summary(account_filter)

    for web_acc in web_accounts:
        if account_only:  pass
        elif account_filter and web_acc.id not in account_filter: continue

        acc = Account(web_acc)

        summary.add_account(acc)

        if account_only: continue

        acc.load_from_file()

        if UPDATE_HISTORY:
            acc.update_from_web()

        for trans in acc.transactions:
            summary.add_transaction(acc, trans)

        if SAVE_HISTORY:
            acc.save_to_file()

<<<<<<< HEAD
    if PRINT_CATE:
        summary.print_cate(DETAIL_BY_CATE)
    
=======
    summary.print_cate(DETAIL_BY_CATE)

>>>>>>> ca0c3c0... update git
    if UPDATE_HISTORY:
        summary.print_acc_update()

    if SAVE_HISTORY:
        git.commit_all_and_push()

if __name__ == "__main__":
    import sys
    main()
