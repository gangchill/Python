import pickle
import os
from newsgroups import *

logging=False

def log(msg):
    if logging:
        print(msg)

class block:
    def __init__(self, address,base_dir='/tmp/'):
	# dictonary
        self.content=dict()
	# base dir name
        self.base_dir=base_dir
	# adress w.r.t. binary tree
        self.address=address
    # delete file from disc
    def removeFile(self):
	try:
	   os.remove(self.base_dir+self.address)
	except OSError:
	   pass
    # load dictonary from hdd
    def load(self):
        try:
            with open(self.base_dir+self.address) as f:
                self.content=pickle.load(f)
            # delete file after reading
	    removeFile()
        except IOError:
            pass
    # save dictonary to hdd
    def write(self):
        with open(self.base_dir+self.address,'w') as f:
            pickle.dump(self.content, f)
    # store the key
    def put(self,k,v):
        self.content[k]=v
    # get the value for the given key
    def get(self,k,default=None):
        return self.content.get(k,default)

class block_storage:
    def __init__(self, mem_size, base_dir='/tmp/'):
	# dictonary holding #mem_size blocks
        self.blocks=dict()
	# base dir name
        self.base_dir=base_dir
	# mem size
        self.mem_size=mem_size
    # adds an block to the dictonary
    def add_block(self, address):
	# create block with given adress
        b=block(address)
	# store block in dictonary
        self.blocks[address]=b
	# handle overrun
        self.handle_overrun(address)
	# return the block
        return b
    # delete block from dictonary
    def del_block(self, address):
	# remove from hdd
	self.blocks[address].removeFile()
	# remove block from dic
        del self.blocks[address]
    # get the block for the given adress
    def get_block(self,address):
	# get the block from the dictonary
        b=self.blocks.get(address,None)
	# if no block with given adress in
	# dic load it and handle overrun
        if not b:
            b=block(address)
            b.load()
            self.blocks[address]=b
            self.handle_overrun(address)
        return b
    # handle overrun
    def handle_overrun(self, active_block):
	# number of blocks in mem vs mem_size
        diff=len(self.blocks)-self.mem_size
	# if mem_size < blocks in mem
        if diff>0:
	    # choose max(5,diff) blocks at random
            bs=random.sample(self.blocks.keys(),max(5,diff))
            for b in bs:
		# write block to hdd and remove it from dic
                if b != active_block:
                    self.blocks[b].write()
                    del self.blocks[b]
            
def binary(n):
    ''' return binary digits of n as array '''
    l=[]; t=n
    for _ in xrange(64):
        l=l+[t&1]
        t=t>>1                
    return l

def nbit(h,n):
    ''' return n th bit of the number h '''
    return (h>>n)&1

def get_address(h,n=None):
    if n:
        return ''.join([str(t) for t in h[0:n]])
    return ''.join([str(t) for t in h])

class ehash:
    def __init__(self, block_size=10, mem_size=100):
	# block size
        self.block_size=block_size
	# total number of blocks
        self.total_blocks=2
	# binary tree represented by a list
        self.index=['0','1']
	# storage
        self.storage=block_storage(mem_size)
	# initial blocks
        self.storage.add_block('0')
        self.storage.add_block('1')
    
    # calculate the block adress by traversing
    # the binary tree        
    def get_block_address(self,h):
        i=1
        b=self.index[h[i]]
	# search for the leaf with the
	# given hash
        while isinstance(b,list):
            b=b[h[i]]
            i+=1
        return b
    
    # return the block
    def get_block(self, h):
        return self.storage.get_block(self.get_block_address(h))

    # split a block
    def split(self,h):
        log('split'+''.join([str(x) for x in h]))
        i=1
	# 
        container=self.index
        container_index=h[0]
        b=self.index[container_index]
        while isinstance(b,list):
            container=b
            container_index=h[i]
            b=b[container_index]
            i+=1
	# get the i least significant bits
        address=get_address(h,i)
	# create new leaves
        c=[address+'0', address+'1']
	# create the two new blocks
        split_blocks=[self.storage.get_block(b) for b in c]
	# store the new leaves
        container[container_index]=c
	# get the block to split
        b=self.storage.get_block(address)
	# rehash blocks
        for k,v in b.content.iteritems():
            split_blocks[nbit(hash(k),i)].put(k,v)
	# remove block
        self.storage.del_block(address)
	# increase total number of blocks
        self.total_blocks+=1

    # add a key value pair to the proper block
    def put(self,key,value):
	# calculate the binary hash representation
        h=binary(hash(key))
	# get the block for the given hash 
        b=self.get_block(h)
	# add the key value to pair
        b.put(key,value)
	# handle block size overruns
        if len(b.content)>self.block_size:
            self.split(h)
   
    # return the value for a given key
    def get(self, key, default=None):
	# calculate the binary hash representation
        h=binary(hash(key))
	# get the block for the given adress
        b=self.get_block(h)
	# return the value
        return b.content.get(key,default)
    
def test_ehash():
    eh=ehash(block_size=1e4,mem_size=1e4)
    counter=0
    articles=load_newsgroups()
    tokenizer=CountVectorizer().build_tokenizer()
    for article,text in articles.iteritems():
        for index,word in enumerate(tokenizer(text)):
            string=article+word+'-'+str(index)
            eh.put(string,string)
            counter+=1
            if counter%1e4==0:
                print('inserts '+str(counter)+' blocks: '+str(eh.total_blocks)+' in mem: '+str(len(eh.storage.blocks)))
    return eh

test_ehash()
