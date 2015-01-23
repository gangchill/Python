#!/usr/bin/python2.7
import pymongo as mo
import networkx as nx
import matplotlib.pyplot as plt
import re
from math import log

# count unique elements in both lists
def count_commons(l1,l2):
    #the & operator on sets denotes intersection
    return len(set(l1)&set(l2))

# get occurrences of keyword as id's of the corresponding tweets
def get_occurrences(word):
    col=db.tag_occurrences
    if re.match('^@',word):
        col=db.user_occurrences
    d=col.find_one({'keyword':word})
    return(d['occurrences'])


def create_network(keywords):
    g=nx.Graph()
    #cache node occurrences to avoid multiple db lookups
    occurrence_cache=dict()
    for w in keywords:
        occ=get_occurrences(w)
        occurrence_cache[w]=occ
        g.add_node(w, count=len(occ))
    for w in keywords:
        for u in keywords:
            if u==w: continue
            edge_weight=count_commons(occurrence_cache[w],occurrence_cache[u])
            if edge_weight>0:
                g.add_edge(w,u,count=edge_weight)
    return(g)

#if __name__ == '__main__':
def show_top500():
    n=500
    client=mo.MongoClient()
    db=client.twitter

    from twitter_extract import top_tweets
    g=create_network(top_tweets(n))
    positions=nx.spring_layout(g)
    ew=[ log(1+e[2]['count']) for e in g.edges(data=True)]
    ew_max=max(ew)
    ew=[10*e/ew_max for e in ew]

    ns=[float(n[1]['count']) for n in g.nodes(data=True)]
    ns_max=max(ns)
    ns=[400*n/ns_max for n in ns]

    colors={'@':(1,0.5,0.5), '#':(0.5,0.5,1)}
    node_colors=[colors[l[0]] for l in g.nodes()]
    
    plt.clf()
    fig=plt.figure(frameon=False)
    ax=fig.add_axes([0,0,1,1])
    ax.axis('off')
    nx.draw_networkx_nodes(g,positions, node_size=ns, alpha=1, node_color=node_colors)
    nx.draw_networkx_edges(g,positions, width=ew, alpha=0.3, edge_color='k')
    nx.draw_networkx_labels(g,positions, font_size=8)
    plt.savefig("/tmp/plot.pdf")

