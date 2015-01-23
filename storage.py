import random
import sys
import numpy as np

#Logging flag
logging=False

def log(msg):
    if logging:
        print(msg)

class Node(dict):
    def __init__(self, capacity):
        self.capacity=capacity
    def put(self, k, v):
        if len(self) == self.capacity:
            log("exceeded capacity")
	else:
	    self[k] = v

class AdaptiveHashing:
    def __init__(self, nodes=100, capacity=20, pos=4):
	# the nodes
        self.nodes = [Node(capacity) for _ in xrange(nodes)]
	# mapping between node and its position
        self.nodesMap = range(0,nodes)*pos
        random.shuffle(self.nodesMap)
        self.positions = None
	# draw nodes*pos unique random numbers (positions)
        while True:
            self.positions = set(np.random.rand(len(self.nodes)*(pos+1)))
            if len(self.positions) >= len(self.nodes)*pos:
                break;
        self.positions = sorted(random.sample(self.positions,len(self.nodes)*pos))


    def put(self, k, v):
	# find closest node
        pos = self.find(hash(k))
	# store the key value pair
        self.nodes[self.nodesMap[pos]].put(k,v)
	# log the fill state
        log('fill states: '+', '.join([str(x) for x in self.get_fill_states()]))

    def get(self, k):
	# find closest node
        pos = self.find(hash(k))
	# return the value, or None of key does not exist
        return self.nodes[self.nodesMap[pos]].get(k)

    def find(self, h):
	# map the hashvalue to [0,1] interval
        h=(1.0+float(h)/float(sys.maxint))/2.0
	# perform binary search
        pos = self.binsearch(h)
	# return the position of the closest node
        return self.findMinDist(h,pos)

    def binsearch(self, h):
	# binary search
        low = 0
        high = len(self.positions)-1
        while low <= high:
            mid = (low+high)/2
            midVal = self.positions[mid]
            if midVal < h:
                low = mid+1
            elif midVal > h:
                high = mid-1
            else:
                return mid
	# if we did not find the element low
	# points to the position with the first
	# value greater than h
        return low%len(self.positions)

    def findMinDist(self, h, pos):
	# pos is the position of the first value >= h
	# calculate "ring distance"
        d=abs(h-self.positions[pos])
        d1 = min(d,1-d)
	# pos-1 is the position of the last value < h
	# calculate ring distance
        d=abs(h-self.positions[(pos-1)%len(self.positions)])
        d2 = min(d,1-d)
	# return the position of the node with the smaller distance
        if d1<=d2:
            return pos
        return pos-1
    
    def get_fill_states(self):
	# return fill states of each node
        return([len(n) for n in self.nodes])

    
class GreedyHash:
    def __init__(self, nodes, capacity, alternatives):
        self.nodes=[Node(capacity) for _ in xrange(nodes)]
        self.capacity=capacity
        self.alternatives=alternatives
    def put(self, key, value):
        self.get_block(hash(key))[key]=value
        log('fill states: '+', '.join([str(x) for x in self.get_fill_states()]))
    def get_block(self, h):
	# calculate the node index
        node_index=h%len(self.nodes)
        mini=node_index;
	# test alternatives
        for i in xrange(h+1,h+self.alternatives+1):
	    # map i to a valid index
            index=i%len(self.nodes)
	    # if current node has less entries then current min
	    # update current min
            if len(self.nodes[index])<len(self.nodes[mini]):
                mini=index
	# return the node with the smallest number of entries
        return(self.nodes[mini])
    def get(self,key):
        h=hash(key)%len(self.nodes)
	# check matching node + alternatives
        for i in xrange(h,h+self.alternatives+1):
            index=i%len(self.nodes)
            if key in self.nodes[index]:
		return self.nodes[index][key]
        return None
    def get_fill_states(self):
	# return fill states of each node
        return([len(n) for n in self.nodes])

def test():
    for g in [GreedyHash(10,100,3), AdaptiveHashing(10,100,3)]:
        for _ in xrange(100):
            r=str(random.random())
            g.put(r,r+'_value')
            log(str(g.get(r)))

test()
