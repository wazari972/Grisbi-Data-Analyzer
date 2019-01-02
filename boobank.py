#! /usr/bin/python3.7

from weboob.core import Weboob
import pickle
from weboob.capabilities.base import NotLoadedType
from weboob.capabilities.base import NotAvailableType

weboob = Weboob()
backend = weboob.load_backends(names=['creditcooperatif'])

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
    print("Get the account list ...")
    for acc in weboob.do("iter_accounts"):
        print("Get '{}' transactions ...".format(acc.label))
        
        trans = [obj_to_dict(trans) for trans in weboob.do("iter_history", acc)]
        
        print("Save transactions from '{}' ...".format(acc.label))
        with open("in/{}.pickle".format(acc.id), "wb") as out_f:
            pickle.dump(trans, out_f)
        print('')

def load():
    print("Get the account list ...")
    for acc in weboob.do("iter_accounts"):
        print("Load '{}' transactions ...".format(acc.label))
        print(obj_to_dict(acc))
        with open("in/{}.pickle".format(acc.id), "rb") as in_f:
            trans = pickle.load(in_f)
        for t in trans:
            print(u"{}".format(t))
        import pdb;pdb.set_trace()
        print('')
        
if __name__ == "__main__":
    import sys
    if sys.argv[1] == "save":
        print("SAVE")
        save()
    else:
        print("LOAD")
        load()



