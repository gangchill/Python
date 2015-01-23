#!/usr/bin/python2.7
import pymongo as mo

client = mo.MongoClient()
db = client.warehouse
db.aggregate.drop()
db.aggregate.insert(db.products.aggregate({
    '$group' : { '_id' : '$category',
                'numOfArticles' : {'$sum' : 1},
                'sumOfQuantities' : {'$sum' : '$quantity'},
                'articlesList' : { '$push' : {'_id': '$_id', 'quantity' : '$quantity'}} 
	}})['result'])

