"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

# Python libs
import os
import numpy as np
import pickle as pl
import multiprocessing as mp
from matplotlib import pyplot as plt
import scipy.spatial.distance as ssd
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.stats
from scipy import spatial

def loadfile(fpath, rawName):
    fname = fpath + rawName + ".pic"
    with open(fname, "rb") as f: return pl.load(f)

def savefile(fpath, rawName, data):
    fname = fpath + rawName + ".pic"
    with open(fname, "wb") as f: return pl.dump(data,f)

def getJson(clusters, leaflabels, fSuffix, cooccVecs, wtoi, clem, fpath, debugname): #save if fSuffix<>""#https://gist.github.com/mdml/7537455

    """
    Draws and stores a dendrogram of a given hierarchical clustering result.

    :param clusters: Hierarchical clustering result encoded as a linkage matrix
    :param leaflabels: Dictionary mapping index to word
    :param fSuffix: String to append to file name. If this is empty then dendrogram is not stored
    :param cooccVecs: co-occ for words
    :param wtoi: Dictionary mapping word to index
    :param clem: Lemma used for clustering
    :param fpath: folder to store dendrogram
    :param debugname: String to append to file name

    :returns: Nested dictionary of the dendrogram for d3
    """
	
    import scipy.spatial
    import scipy.cluster
    import json
    from functools import reduce
    T = scipy.cluster.hierarchy.to_tree(clusters, rd=False)
    id2name = leaflabels

    # Draw dendrogram using matplotlib to scipy-dendrogram.pdf
    fSuffix = "" #clem+debugname+"_" if np.random.random()>0.98 else "" #debug
    if len(fSuffix):
        os.makedirs(fpath+"debug",exist_ok=True)
        plt.close()
        plt.figure(figsize=(30,15))
        labels = [leaflabels[i] for i in range(len(leaflabels.keys()))]  # Create dictionary for labeling nodes by their IDs
        scipy.cluster.hierarchy.dendrogram(clusters, labels=labels, orientation='right')
        plt.savefig(fpath+"debug/"+fSuffix+"_dendro.png")

    def add_node(node, parent):

        """
        Creates a nested dictionary from the ClusterNode's returned by SciPy.

        :param node: Node to append
        :param parent: Parent of node to append
        """
		
        newNode = dict(node_id=node.id, children=[]) # First create the new node and append it to its parent's children
        parent["children"].append(newNode)
        if node.left: add_node(node.left, newNode) # Recursively add the current node's children
        if node.right: add_node(node.right, newNode)
    d3Dendro = dict(children=[], name=clem) # Initialize nested dictionary for d3, then recursively iterate through tree
    add_node(T, d3Dendro)

    def is2ndLeave(node): return node["children"]==0 or sum([len(k["children"])>0 for k in node["children"]])==0
    def is3rdLeave(node): return sum([not is2ndLeave(k) for k in node["children"]]) == 0

    def compress(node):
        if is3rdLeave(node):
            kids=sum([k["children"] for k in node["children"]],[])
            kidsOfKids=sum([k["children"] if len(k["children"])>0 else [k] for k in kids],[])
            for k in node["children"]:
                if len(k["children"])==0: kidsOfKids.append(k)
            node["children"]=kidsOfKids
        else:
            for k in node["children"]:
                if len(k["children"]): compress(k)
				
    compress(d3Dendro)
    compress(d3Dendro)
    compress(d3Dendro)
    compress(d3Dendro)
	
    def label_tree(n):

        """
        Labels each node with the names of each leaf in its subtree.

        :param n: Nested dictionary of the dendrogram

        :returns: List of leaf names
        """

        if len(n["children"]) == 0: leafNames = [id2name[n["node_id"]]] # If the node is a leaf, then we have its name
        else: # If not, flatten all the leaves in the node's subtree
            leafNames = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])
            #leafNames = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])
        del n["node_id"] # Delete the node id since we don't need it anymore and it makes for cleaner JSON
        #n["name"] = "-".join(sorted(map(str, leafNames))) # Labeling convention: "-"-separated leaf names
        if len(leafNames)>3:
            #print("ERR",[l for l in leafNames if wtoi[l]>=len(coen)])
            #chosen = [coen[wtoi[l]][1] for l in leafNames if wtoi[l]<len(coen)]  # max entropy
            #chosen2 = [coen[wtoi[l]][0] for l in leafNames if wtoi[l]<len(coen)]  # max count
            #names = set([leafNames[0], leafNames[-1], leafNames[len(leafNames) // 2],leafNames[np.argmin(chosen)],leafNames[np.argmin(chosen2)]])-set([leafNames[np.argmin(chosen)],leafNames[np.argmin(chosen2)]])
            #names=[leafNames[np.argmin(chosen)], leafNames[np.argmin(chosen2)],list(names)[0]]
            counts= np.array([cooccVecs[wtoi[l]][0] for l in leafNames if wtoi[l] < len(cooccVecs)])  # max count
            meancounts=np.median(counts)
            lnames = [len(l) for l in leafNames if wtoi[l] < len(cooccVecs)]
            meanlen=np.mean(lnames)
            names=[l for l in leafNames if wtoi[l] < len(cooccVecs) and cooccVecs[wtoi[l]][0] >= meancounts and len(l) < meanlen]
            if len(names)<4: names=leafNames
            names=list(set([names[0],names[len(names)//2],names[-1]]))
        else: names=leafNames
        n["name"] = ", ".join(sorted(map(str, names)))  # Labeling convention: "-"-separated leaf names
        #print(names, ">",[leafNames[0], leafNames[-1], leafNames[len(leafNames) // 2]],leafNames)
        #if len(leafNames)>2:
            #chosen3 = [adit[wos[wtoi[l]]] for l in leafNames]
            #chosen4 = [wcounts[l] for l in leafNames]
            #vecs=[getVec(mats, wtoi[l], upbound, offs, cWords) for l in leafNames]
            #cen=np.sum(vecs)
            #dists=np.array([spatial.distance.cosine(v, cen) for v in vecs])
            #print(leafNames[np.argmin(chosen)]," | ",leafNames[np.argmax(chosen2)]," | ",leafNames[np.argmax(dists)]," | ",leafNames[np.argmax(chosen3)]," | ",leafNames[np.argmax(chosen4)]," -- ",leafNames)
			
        return leafNames

    label_tree(d3Dendro["children"][0])
    if len(fSuffix):
        jname=fSuffix+"_d3-dendro.json"
        json.dump(d3Dendro, open(fpath+"debug/"+jname, "w"), sort_keys=True, indent=4) # Output to JSON
        with open("dendrogram.html", "r") as f: dhtml=f.read()
        dhtml=dhtml.replace("d3-dendrogram.json",jname)
        with open(fpath+"debug/"+fSuffix+"_html_dendro.html", "w") as f: f.writelines(dhtml)

    return d3Dendro

def multicluster(para):
    clems, assDict, storeDebugFile, coitow, coen, wtoi,fpath,debugname = para
    return [cluster((k, assDict, storeDebugFile, coitow, coen, wtoi,fpath,debugname)) for k in clems]

def cluster(para):
    clem,assDict,storeDebugFile,coitow,coen,wtoi,fpath,debugname = para
    if np.random.random()>0.95: print("Clustering word",clem)
    # if not word in wToL:
    #     print("NOT found AS WORD!!!!", word)
    #     return None
    # lem = wToL[word]
    #get Distance matrix of associated terms

    asso=list(assDict[wtoi[clem]]['All'])
    wos = {x[0]:i for i,x in enumerate(asso)}
    itoWID= {v:k for k,v in wos.items()}
    diMat=np.zeros((len(wos),len(wos)))
    for i,iw in enumerate(wos.keys()):
        if iw in assDict:
            distslw=dict(assDict[iw]['All'])
            for j, jw in enumerate(wos.keys()):
                if iw==jw: continue #should always be 0/max value (self association of word)
                if jw in distslw:
                        diMat[wos[iw],wos[jw]]=distslw[jw]
                        diMat[wos[jw],wos[iw]] = diMat[wos[iw],wos[jw]]
    diMat=-diMat
    diMat += np.abs(np.min(diMat))
    np.fill_diagonal(diMat,0)
    infinites=np.where(np.isinf(diMat))
    if len(infinites):
        print("Distances matrix entries infinite Count",len(infinites),"orig word",clem, " Replace them with 1e5")
        diMat[infinites]=1e5
    distArray = ssd.squareform(diMat) # convert the redundant n*n square matrix form into a condensed nC2 array
    Z = linkage(distArray, 'ward')#''ward')
    leaflabels={i:coitow[itoWID[i]] for i in range(len(itoWID.keys()))}
    return getJson(Z,leaflabels,storeDebugFile,coen,wtoi,clem,fpath,debugname)

    # #Plot and save dendrogram
    # labs = [leaflabels[i] for i in range(len(leaflabels.keys()))]
    # plt.figure(figsize=(36,18))
    # plt.title('Dendrogram (truncated) for '+ word)
    # plt.xlabel('sample index')
    # plt.ylabel('distance')
    # dendrogram(
    #     Z,
    #     truncate_mode='lastp',  # show only the last p merged clusters
    #     p=len(wos),#*5//6,  # show only the last p merged clusters
    #     show_leaf_counts=False,  # otherwise numbers in brackets are counts
    #     leaf_rotation=90.,
    #     leaf_font_size=9.,
    #     labels=labs,
    #     show_contracted=True,  # to get a distribution impression in truncated branches
    # )
    # plt.tight_layout()
    # plt.savefig(word+".png")
    # #plt.show()
    # plt.close()


def doCluster(Conf):
    #print(wToL["IT experience"])
    #print(wToL["it experience"])
    # wcounts=loadfile(Conf.wcountsname)
    # compwords=loadfile(Conf.compoundsname)
    #wcounts = loadfile(Conf.wcountsname)
    wToL = loadfile(Conf.fpath,Conf.wToLemmaname+Conf.fending)
    coitow = loadfile(Conf.fpath,Conf.coiTowname+Conf.fending)
    coen = loadfile(Conf.fpath,Conf.cooccVecs+Conf.fending)
    wtoi = {k: i for i, k in coitow.items()}

    lemmas = list(set(wToL.values()))
    existlemmas = [k for k in lemmas if k in wtoi]
    existlemmas = existlemmas if not Conf.isBackendDummy else existlemmas[:10]
    print(existlemmas)
    #existlemmas= [k for k in lemmas if k in ["python","machine learning","communication","data science","scala"]]
    manager = mp.Manager()
    d2 = manager.list()
    for k in coen:  d2.append(k)
    pool = mp.Pool(processes=Conf.nProc // 5 + 1)  # a lot of overhead due to manager and data sync, better not increase this...

    def getCluster(loadfname,fend,savefname):
        d = manager.dict()
        assAbsDict = loadfile(Conf.fpath,loadfname+fend+Conf.fending)
        for k in assAbsDict:  d[k] = assAbsDict[k]
        joblist = [(k, d, "", coitow, d2, wtoi,Conf.fpath,loadfname+Conf.fending+fend) for k in [existlemmas[i:i + 30] for i in range(0, len(existlemmas), 30)]]
        # joblist = [(k, k, "", k, coen, k) for k in [existlemmas[i:i + 50] for i in range(0, len(existlemmas), 50)]]
        print(loadfname,"nJobs", len(joblist)," nWords",len(assAbsDict), "nProc", Conf.nProc // 5 + 1)
        clusters = pool.map(multicluster, joblist)  # run in parallel
        clusters = sum(clusters, [])
        allCls = {k: cl for k, cl in zip(existlemmas, clusters)}
        print("Saving",savefname)
        # allCls={k:cluster(k,assDict) for k in wToL.values()}
        savefile(Conf.fpath,savefname+fend+Conf.fending, allCls)
    for fend in ["_win","_doc"]:
        getCluster(Conf.assSurname,fend,Conf.asstreename)
        getCluster(Conf.assAbsname,fend, Conf.assAbstreename)


if __name__ == '__main__':
    import sys
    sys.path.append("../")
    sys.path.append("/../")
    from Config import Cfg
    Conf = Cfg(False)
    doCluster(Conf)

