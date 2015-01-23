from storage import GreedyHash, AdaptiveHashing
from sklearn.feature_extraction.text import CountVectorizer
from time import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from numpy import var

#this is probably different on other systems
newsgroup_file='data'

def read_newsgroups(from_file=newsgroup_file, limit=None):
    '''
    read and split/recombine text data
    limit, if given takes only the first limit words of each document
    return list of strings for experiment
    '''
    values=[]
    cv=CountVectorizer(stop_words='english')
    tokenizer=cv.build_tokenizer()
    with open(from_file) as f:
        text=f.read()
        for a in text.split('\n'):
            p=a.find('\t')
            doc_id=a[0:p]
            #split to words
            doc_content=tokenizer(a[p:])
            # reduce number of entries is limit is set
            if limit and len(doc_content)>limit:
                doc_content=doc_content[:limit]
            # append entry
            for index,word in enumerate(doc_content):
                values.append(doc_id+'-'+word+'-'+str(index))
    return values

def timer(func):
    ''' measure and return runtime of func()
    return time or time,result if func() has return value result
    '''
    t=time()
    r=func()
    t=time()-t
    if not r:
        return t
    return t,r


#skip this (long) part, when executing file in console
#if recalculate is a defined variable, the process is skipped
if not 'recalculate' in locals():
    values=read_newsgroups(limit=2)
    n_positions=[1,2,3,4,5,10,20]
    n_alternatives=[1,2,3,4,5,10,20]
    capacities=[10,100,1000]
    n_nodes=[2*len(values)/c for c in capacities]

    results=[]

    def insert_all(struct):
        for v in values:
            struct.put(v,v)

    def retrieve_all(struct):
        for v in values:
            struct.get(v)
    # zip returns list of tuples, where the i-th tuple contains the i-th element of both lists
    for cap,nodes in zip(capacities,n_nodes):
        for pos in n_positions:
            s=AdaptiveHashing(nodes=nodes,capacity=cap,pos=pos)
            tins=timer(lambda: insert_all(s))
            tret=timer(lambda: retrieve_all(s))
            results.append({'method':'adaptive', 'capacity':cap, 'positions':pos
                            ,'insert':tins, 'retrieve':tret ,'variance':var(s.get_fill_states())})
        for a in n_alternatives:
            s=GreedyHash(nodes=nodes,capacity=cap,alternatives=a)
            tins=timer(lambda: insert_all(s))
            tret=timer(lambda: retrieve_all(s))
            results.append({'method':'greedy', 'capacity':cap, 'alternatives':a
                            ,'insert':tins, 'retrieve':tret,'variance':var(s.get_fill_states())})
        print('.')

### end of if recalculate
        
def extract(results, capacity, method, field):
    '''
    from the experimental results, extract a list containing the field-values
    but only for documents in results with the given capacity and method
    '''
    return [r[field] for r in results if r['capacity']==capacity and r['method']==method]
    
def plot_results(results):
# this should be modified to use 2 different axes for positions and alternatives
# since they are on different scales anyway, but that code is a little overkill:
# http://stackoverflow.com/questions/9103166/multiple-axis-in-matplotlib-with-different-scales
    p=PdfPages('/tmp/results.pdf')
    #iterate over capacity fields and comparison/method fields
    for capacity in capacities:
        for compare_field in ['variance','insert','retrieve']:
            fig=plt.figure()
            for method,parameter in [('adaptive','positions'),('greedy','alternatives')]:
                
                ext=lambda m : extract(results, capacity, method,m)
                #label is for the legend
                plt.plot(ext(parameter),ext(compare_field),label=method)
            #add labels and a legend
            plt.xlabel('positions/alternatives')
            plt.ylabel(compare_field)
            plt.title('node capacity '+str(capacity))
            plt.legend()
            p.savefig(fig)
    p.close()

# call the actual plotting process
plot_results(results)

'''
results:

Remark: when the greedy measurements are invisible, they are just too close to zero. This could have been fixed with a logarithmic scaling, but that would hide the general trends.

Variance goes down with more alternatives/positions, but is extremely small for greedy, while adaptive approaches a seemingly asymptotical border with more positions

Insertion is in general faster with greedy, but becomes measureably slower with additional alternatives. For adaptive it almost seems to be independent of the number of positions (bin search).

Retrieval is very similar to insertion.

For the time measurements it is important to recognize that in a network scenario the additional communication of the greedy approach is much more costly.
In comparison, the adaptive can identify the exact node containing the block and thereby minimizes communication costs.
'''
