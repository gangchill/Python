import numpy as np

from multigauss import Multi_gauss
from wkmeans import wkmeans,cluster_quality,get_center_assignment


def cluster_upwards(cluster_stack,weight_stack,stack_fill,M,rep,k,factor=3,level=0):
    if len(cluster_stack[level])>M:
        c,cw,a,q = wkmeans(np.vstack(cluster_stack[level]),np.vstack(weight_stack[level]),factor*k,rep)
        cluster_stack[level]=[]
        weight_stack[level]=[]
        stack_fill[level]=0
        level+=1
        if level>=len(cluster_stack): #start a new level
            cluster_stack.append([])
            weight_stack.append([])
            stack_fill.append(0)
        cluster_stack[level].extend(c)
        weight_stack[level].extend(cw)
        stack_fill[level]+=len(cw)
        cluster_upwards(cluster_stack,weight_stack,stack_fill,M,rep,k,factor,level)
#        print('level: '+str(level)+' '+str(len(cluster_stack[level])))

def cleanup_stack(cluster_stack,weight_stack,stack_fill,M,rep,k,factor=3):
    '''cleanup the cluster stack until only the desired clustering is left'''
    s=[]; w=[]; n=0
    for i in xrange(len(cluster_stack)):
        s.extend(cluster_stack[i])
        w.extend(np.array(weight_stack[i]))
        n+=stack_fill[i]
        if n>M: #if necessary, compress by clustering
            s,w,a,q=wkmeans(np.vstack(s),np.vstack(w),factor*k,repetitions=rep)
            s=[s]; w=[w]; n=len(w)
    return wkmeans(np.vstack(s),np.vstack(w),k,repetitions=rep)


def recursive_wkmeans(read_input, N=5000, M=50, k=10, rep=4,factor=3):
    '''

    number of repetitions
    '''
    cluster_stack=[[]]
    weight_stack=[[]]
    stack_fill=[0]
    
    read=0
    while read<N:
        s,w=read_input(100)
        cluster_stack[0].extend(s)
        weight_stack[0].extend(w)
        read+=100
        cluster_upwards(cluster_stack,weight_stack,stack_fill,M,rep=rep,k=k,factor=factor)
    return cleanup_stack(cluster_stack,weight_stack,stack_fill,M,rep=rep,k=k,factor=factor)


def create_input_reader(mg=Multi_gauss(25),samples=[],weights=[]):
          
    def read_input(n=100):
        s=mg.sample(n)
        samples.extend(s[0])
        weights.extend(s[1])
        return s
    return read_input

