#!/usr/bin/python2.7
from zipfile import ZipFile
import pymongo as mo
import bson
import csv
import sys

client=mo.MongoClient()
db=client.twitter

#for testing
input_file='/home/nagelu/data/twitter/2013_02_08_01.csv'

#read the input file from command line argument
if len(sys.argv)>1 :
    input_file=sys.argv[1]

db.tweets.drop()
i=0
# working with a zipped file
#with ZipFile('/home/nagelu/data/twitter/2013_02_08_01.zip','r') as zf:
#   with zf.open(zf.namelist()[0]) as f:

# working with pure text file
with open(input_file,'r') as f:
        field_names=None
        for line in f:
            l=line.decode('ISO-8859-1').split('\t')
            if not field_names:
                field_names=l
                continue
            document=dict(zip(field_names,l))
            document['_id']=i
            i+=1
            db.tweets.insert(document)

