"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

# -*- coding: utf-8 -*-
import numpy as np
from Config import *
import FrontEnd.vis_old.toolsVisual as wtools
import pickle
import textTools
from plotly.graph_objs import Bar

#load stored data
#with open(dataPath+"topiciToW"+fendingF+".pic", "rb") as f: itowTopic=pickle.load(f)
#wtoiTopic = {i: w for w, i in itowTopic.items()}
with open(dataPath+topTopicDocname+fendingF+".pic", "rb") as f: topXdt=pickle.load(f)
with open(dataPath+topicWorname+fendingF+".pic", "rb") as f: topsort=pickle.load(f)
with open(dataPath+topTopicname+fendingF+".pic", "rb") as f: topTopics=pickle.load(f)
#with open(dataPath+"oWordMap"+fendingF+".pic","rb") as f: oWordMap=pickle.load(f)
pwt=np.load(dataPath+topicWorname+fendingF+".npy")
pt=np.load(dataPath+topicDistname+fendingF+".npy")

sTopics = list(sorted(topTopics, key=lambda x: x[0], reverse=True))
topvals = np.sort(np.array([x[1] for x in sTopics]))[::-1]

def getTop(words,pwt):
    #words=doc.split(" ")
    topd = np.zeros(np.shape(pwt)[1])
    for w in words:
        if w in wtoiTopic:
            ind = wtoiTopic[w]
            topd += pwt[ind, :]
    topd /= 1.0*np.sum(topd)
    return topd

#get text shown for topic "buttons"
def getTopTxt(words, sortByDiff=False):
    global topvals
    if len(words):
        doTopics = getTop(words, pwt)
        doTopics = (doTopics * pt) / np.sum(doTopics * pt)
        topvals = topvals * 1.0 / np.sum(topvals)
        diff = doTopics - topvals
    else:
        diff = np.repeat(0, len(topvals))
    #print(diff)
    if sortByDiff:
        sorTop = np.argsort(diff)[::-1]  # reverse
        topTopics = [(it, diff[it], topvals[it]) for it in sorTop]
    else:
        topTopics = [(it, diff[it], vals) for it, vals in enumerate(topvals)]
    topTxt = [[] for _ in range(len(topTopics))]
    it = 0
    for (t, diff, topScore) in topTopics:
       if topScore > 0.01:
            #topTxt[it]="Rel: "+str(np.round(v,2))+"  TopWords: "+" ".join([itowTopic[wid] for _,wid in t[:5]])
            toWords = [itowTopic[wid] for _, wid in topsort[t][:7]]
            #toWords = [w if w not in wtools.oWordMap else wtools.oWordMap[w] for w in toWords]
            toWords = [textTools.convertWord(w) for w in toWords]
            topTxt[it] = "T"+str(t)+" Wei.: "+str(np.round(topScore, 2)) + " Diff.:"+str(np.round(diff, 2)) + " " + " ".join(toWords)
            it += 1
    return topTxt

#get graph showing a topic
def getTopicGraphs(it):
    wnodes={}
    for weight, wid in topsort[it][:wPerTopic]:
            wnodes[itowTopic[wid]]=weight
    maxConn = int(wPerTopic/2)
    edges={}
    for w0 in wnodes:
            if w0 in wtools.wtoi:
              ids=wtools.imat[wtools.wtoi[w0],:]
              cConn=0
              for id,weight in zip(ids,wtools.vmat[wtools.wtoi[w0],:]):
                  w1=wtools.itow[id]
                  if w1 in wtoiTopic and w1 in wnodes:
                      cConn+=1
                      edges[w0 + esep + w1]=weight
                      if cConn>=maxConn: break

    if len(wnodes): #ensure connected graph
        ks=list(wnodes.keys())
        minval = min(edges.values())/3 if len(edges) else 1e-10
        for w1 in ks[1:]:
                    edges[ks[0] + esep + w1] = minval
    okedges={}
    for e,weight in edges.items(): #add all edges, use sum of both weights
        if weight==0: continue
        nodes = e.split(esep)
        sece = nodes[1] + esep + nodes[0]
        okedges[e] = weight
        if sece in edges:
            okedges[e] += edges[sece]
    return wtools.getFullGraphs(wnodes, okedges, wnodes,nocolor=True) #oWordMap

# get bar chart for a topic
def getTopicBar(it):
    bar_chart = Bar(x=[], y=[], orientation='h', hoverinfo='text')

    wlist = []
    weightlist = []
    hoverlist = []
    for weight, wid in topsort[it][:7]:
        weightlist.append(weight)
        wlist.append(itowTopic[wid])
        chw = textTools.convertWord(itowTopic[wid])
        hoverlist.append(wtools.hoverData[chw] if chw in wtools.hoverData else itowTopic[wid])

    bar_chart['x'] = weightlist[::-1]
    bar_chart['y'] = wlist[::-1]
    bar_chart['text'] = hoverlist[::-1]

    return bar_chart