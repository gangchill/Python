#!/usr/bin/python2.7

dicts=[dict(),dict()]

def add_to(di,words):
    if words[0]=='':
        return
    for w in words:
        di[w]=1+di.get(w,0)

def print_stats(di):
    vals=di.itervalues();
    min=vals.next()
    max=min
    sum=min
    ssum=min*min
    for i in vals:
        if i<min: min=i
        if i>max: max=i
        sum+=i
        ssum+=i*i

    print('min= '+str(min))
    print('max= '+str(max))
    mean=float(sum)/len(di)
    print('mean= '+str(mean))
    print('variance= '+str(float(ssum)/len(di)-(mean*mean)))

f=open("extracted_tweets.csv",'r')
for line in f:
    l=line.strip().split("\t")
    for i in xrange(2,min(4,len(l))):
        add_to(dicts[i-2],l[i].split(","))

f.close()

print("# tags:")
print_stats(dicts[0])
print("@ tags:")
print_stats(dicts[1])













