#!/usr/bin/python2.7
import pymongo as mo
from random import randint


client= mo.MongoClient()
db = client.warehouse
db.products.drop()
records = ([({ '_id' : i, 'quantity' : randint(1,1000), 'category' : randint(1,13)}) for i in xrange(1000)])
db.products.insert(records)
