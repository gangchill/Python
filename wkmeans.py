from multigauss import *
import numpy as np
from numpy.random import choice
from itertools import izip


def get_center_assignment(X,centers):
    ''' get list with index of nearest cluster for each node) '''
    return [np.argmin([np.linalg.norm(x-c) for c in centers]) for x in X]

def get_new_centers(X,weights,assignment):
    '''determine new cluster centers as the weighted mean vector of samples
    using the assignment vector to group samples to clusters

    arguments:
    X -- numpy array of samples (one vector per row)
    weights -- weight of each sample (corresponding to the rows of X)
    assignment -- assignment of samples to clusters (0-(#cluster-1))

    return:
    new center for each cluster as numpy array (order given by assignments)
    '''
    cn=max(assignment)+1
    new_centers=np.zeros((cn,X.shape[1]))
    cweights=np.zeros((cn,))

    for x,w,a in izip(X,weights,assignment):
        new_centers[a,:]+=w*x
        cweights[a]+=w

    new_centers=np.array([c/w for c,w in izip(new_centers,cweights)])
    return new_centers,cweights

def cluster_quality(X,weights,assignment,centers):
    ''' cluster quality as weighted sum of distances between sample and cluster center
    X -- samples
    weights -- sample weights
    assignment -- cluster each sample belongs to
    centers -- cluster centers (index corresponding to assignment)
    '''
    s=sum([np.linalg.norm(x-centers[a,:])*w for x,w,a in izip(X,weights,assignment)])
    if not isinstance(s,float):
        s=s[0]# may happen, if weights have 2D-shape
    assert isinstance(s,float)
    return s

def single_wkmeans(X,weights,k):
    ''' single run of weighted k-means clustering
    arguments:
    X -- samples (numpy-array, one vector per row)
    weights -- sample weights
    k -- number of clusters

    return:
    (cluster centers,cluster weights, assignment, quality)
    '''
    weights.shape=(weights.shape[0],)
    centers=X[choice(X.shape[0],k,replace=False),:]
    qold=0
    qnew=1
    while np.abs(qold-qnew)>qold*1e-6:
#        print("next: "+str(qnew))
        assignment=get_center_assignment(X,centers)
        centers,cweights=get_new_centers(X,weights,assignment)        
        if 0 in cweights: #if there's a center without sample
            for i in [index for index,weight in enumerate(cweights) if weight==0]:
                centers[i,:]=X[choice(X.shape[0],1),:]
            assignment=get_center_assignment(X,centers)
            centers,cweights=get_new_centers(X,weights,assignment)
        qold=qnew
        qnew=cluster_quality(X,weights,assignment,centers)
    return (centers,cweights,assignment,qnew)


def wkmeans(X,weights,k=3,repetitions=3):
    ''' weighted k-means clustering
    arguments:
    X -- samples (numpy-array, one vector per row)
    weights -- sample weights
    k -- number of clusters
    repetitions -- number of repetitions with random start centers

    return:
    (cluster centers,cluster weights, assignment, quality)
    '''
    centers,cweights,assignment,quality=single_wkmeans(X,weights,k)
    for i in xrange(repetitions-1):
        c,w,a,q=single_wkmeans(X,weights,k)
#        print(str(i+1)+'. iteration, quality: '+str(q));
        if(q<quality):
            centers,cweights,assignment,quality==c,w,a,q
    return centers,cweights,assignment,quality

# test code
# mg=Multi_gauss(n_clusters=4,dim=16)
# points,weights=mg.sample(500)
# centroids,cweights, assignments, quality=wkmeans(points,weights,5,3)


# plt.clf()
# plt.scatter(centroids[:,0],centroids[:,1],marker='o',c=range(centroids.shape[0]),s=cweights)
# plt.scatter(points[:,0],points[:,1],marker='o',s=weights,c=assignments)

