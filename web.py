#! /usr/bin/python2
"""
0 Accounts;
--------
O 1.
0 2.
O 3.

O Categories:
----------
X 1.
X 1.1
X 1.2
X 1.3
X 2. 
X 2.1
X 2.2

Action:
------
X Graph
X Maths

Date:
----
- Start: DD/MM/YY
- Stop : DD/MM/YY

X Monthly
X Legend
X Cumul
================================
last graph
--------------------------------
penultimate graph
--------------------------------
maths
--------------------------------
older maths
--------------------------------
"""

import sys

import Bank
from Bank import Account, Category, SubCategory, Transaction
import Grisbi
from op import Operators, Operator, Maths, CSV
import Latex

################################
try:
    filename = sys.argv[1]
except:
    filename = "kevin.gsb"
Grisbi.do_import(filename)
###############################

class Request:
    def __init__(self, monthly, start, stop, subcategories=None, accounts=None):
        self.monthly = monthly
        self.subcategories = subcategories
        self.accounts = accounts
        self.start = start
        self.stop = stop
        
class MathRequest(Request):
    def __init__(self, monthly, start, stop, subcategories=None, accounts=None):
        Request.__init__(self, monthly, start, stop, subcategories, accounts)

class GraphRequest(Request):
    def __init__(self, monthly, start, stop, inverted=False, legend=False, subcategories=None, accounts=None):
        Request.__init__(self, monthly, start, stop, subcategories, accounts)
        self.legend = legend
        self.inverted = inverted
    
    
requests = (GraphRequest(False, (2011, 8, 1), (2012, 8, 1), inverted=True, subcategories=["6.9", "8.2","18.12"]),
            MathRequest(False, (2011, 8, 1), (2012, 8, 1), subcategories=["6.9", "8.2","18.12"]),
            MathRequest(True, (2011, 8, 1), (2012, 8, 1), accounts=["2", "6"]),
            GraphRequest(True, (2011, 8, 1), (2012, 8, 1), accounts=["2", "6"]))


print "Categories"
print "=========="
for key, cat in Category.categories.items():
    print "%s --> %s" % (key, cat.name)
    for sub_key, sub_cat in cat.subcats.items():
        print "\t%s --> %s" % (sub_key, sub_cat.name)

print "Accounts"
print "========"
for key, acc in Account.accounts.items():
    print "%s --> %s" % (key, acc.name)

    
while True:
    pass