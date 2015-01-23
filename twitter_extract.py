import pymongo as mo
import re
from multiprocessing import Pool

#number of cores to use
proc=3
#number of docs to process (per thread)
#1e4 runs in under one minute on a single thread
limit=int(1e9/proc)

# key extraction (added underscore _ to allowed chars)
def extract_keys(text, char='@'):
    return re.findall(char+'[a-zA-Z_1-9]+',text)


# first version only indexing
# def index_tweets():
#    client=mo.MongoClient()
#    db=client.twitter
#     for doc in db.tweets.find():
#         #create the desired fields
#         doc['referenced_users']=extract_keys(doc['TWEET_CONTENT'],char='@')
#         doc['referenced_tags']=extract_keys(doc['TWEET_CONTENT'],char='#')
#         #save back to collection
#         db.tweets.save(doc)

#client=mo.MongoClient()

# second, extended version
def index_tweets(client=mo.MongoClient()):
    db=client.twitter
    # indexing saves about 50% time
    for c in [db.user_occurrences,db.user_occurrences]:
        c.ensure_index([('keyword', mo.ASCENDING),
                        ('occurrences', mo.ASCENDING),
                        ('count', mo.ASCENDING)])
    p=Pool(proc)
    p.map(insert, range(proc))

# the actual insertions
#    
def insert(mod):
    db=mo.MongoClient().twitter
    count=0;
    for doc in db.tweets.find({'_id':{'$mod' : [proc,mod]}} ,limit=limit):
        #create the desired fields
        count+=1 #entertainment
        if count%int(limit/20)==0:
            print(count)
        doc['referenced_users']=extract_keys(doc['TWEET_CONTENT'],char='@')
        doc['referenced_tags']=extract_keys(doc['TWEET_CONTENT'],char='#')
        #save back to collection
        db.tweets.save(doc)
        for keywords,collection in [
                (doc['referenced_users'],db.user_occurrences),
                (doc['referenced_tags'],db.tag_occurrences)]:
            for word in keywords:
                collection.update({'keyword':word},
                                    {'$push' : {'occurrences' : doc['_id']},
                                    '$inc' : {'count' :1 } }
                                    ,upsert=True)

    
def top_tweets(n=10,client=mo.MongoClient()):
    db=client.twitter
    query={'$query':{},'$orderby':{'count':-1}}
    projection={'keyword':1,'count':1,'_id':0}
    results={}
    for col in [db.user_occurrences,db.tag_occurrences]:
        for i in col.find(query,projection,limit=n):
            results[i['keyword']]=i['count']
    top=sorted(results, key=results.get,reverse=True)
    return(top[:n])

if __name__ == '__main__':
    client=mo.MongoClient()
    client.twitter.user_occurrences.drop()
    client.twitter.tag_occurrences.drop()
    index_tweets(client)
