"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
Handali, Joshua Peter; Schneider, Johannes; Dennehy, Denis; Hoffmeister, Benedikt; Conboy, Kieran; and Becker, Jörg. (2020).
"INDUSTRY DEMAND FOR ANALYTICS: A LONGITUDINAL STUDY"
European Conference on Information Systems (ECIS).
https://aisel.aisnet.org/ecis2020_rp/11
"""

# Python libs
from multiprocessing import Process, Manager
import queue
import numpy as np
import time,pickle
import scipy
from scipy.sparse import dok_matrix
from scipy.sparse import csr_matrix
import datetime

"""
Data structure for co-occurrences of words within documents or short text windows.
It consists of a dense matrix (for co-occurrences of frequent words) and sparse matrices for less frequent words.
Co-occurrence matrix are symmetric, we store only half the matrix. We use rectangular matrixes of different types
Matrix looks like:    
        
      zzzzzzz
      zzzzzzz 
      zzzzzzz
  yyyyzzzzzzz  
  yyyyzzzzzzz 
xxyyyyzzzzzzz
xxyyyyzzzzzzz
      
X is a dense matrix for the most frequent words that can co-occ of millions (int32)
Y is dense, but can store less frequent co-ooc (int16)
Z is sparse


Rough intuition, when it is better to store as dense vs sparse?

Assuming a document-based co-occurrences:

if a word occurs in a doc get about #words in doc pairs ~ 400 (for a doc of length 400 words) @jhandali: unlcear
One entry in sparse document matrix takes about 12 bytes + type-dependent byte size (byte_type).
For dense matrix, ie. in np array, it just takes the byte_type.
Hence, breakeven for a word is roughly as follow:
	The number of documents it occurs (#docs) * 400 (document length) * (12 + byte_type) = number of words (nw) * byte_type
	#docs * 400 * (12/byte_type) = nw
	#docs = nw / (400*12) * byte_type
	#docs = 100000 / (400*12)
	#docs ~ 21, ie. more than 21 better to save in numpy array
	
Dynamic sizing: if a word occurs in X documents, it can co-occur at most X times with any other word
To get ideal size of a type, sort by occurrences then use the following list: [(4294967295, np.uint32), (65535, np.uint16), (255, np.uint8)]
"""

minwperdoc = 15 # documents with less words are ignored
winwid = 7 # window size = #words left and right of center words
minOcc = 0 # minimum number a word has to occur in all docs together to be considered for co-occurrences computation

cooccname ="coocc"
cooccWwithFreqname = "cooccWwithFreq"

tsize = [(4294967295, np.uint32), (65535, np.uint16), (255, np.uint8), (22, "sparse")] # sparse can have at most 255 entries #get upper boundary of indexes of types

def getDataTypeRanges(wused):

    """
    Get data type size ranges.

    :param wused: List of tuples containing words and their occurences

    :returns: List of tuples containing word index and data type, and list of offsetted indices
    """

    cpos = 0
    upbound_type = []
    offs = [0]
    for i, (_, nocc) in enumerate(wused):
        if i%500 == 0:
            arrsize = (i-offs[-1])*i*np.dtype(tsize[cpos][1]).itemsize
            if arrsize > 900*1000*1000: #max 900MB per matrix
                upbound_type.append((i, tsize[cpos][1]))
                offs.append(i)
        while (nocc <= tsize[cpos+1][0]):
            upbound_type.append((i, tsize[cpos][1]))
            offs.append(i)
            cpos += 1
            if cpos == len(tsize)-1: break
        if cpos == len(tsize)-1: break
    upbound_type.append((len(wused), tsize[cpos][1]))
	
    return upbound_type, offs


def save_sparse(filename, array):  # note that .npz extension is added automatically
    np.savez(filename, data=array.data, indices=array.indices,indptr=array.indptr, shape=array.shape)


def load_sparse(filename):  # here we need to add .npz extension manually
    loader = np.load(filename + '.npz')
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


def getMats(upbound, offs, nw):

    """
    Creates empty co-occurrence matrices

    :param upbound: List of tuples containing word index and data type
    :param offs: List of offsetted indices
    :param nw: Number of words

    :returns: List of matrices
    """
	
    mats = []
    for i, (b, t) in enumerate(upbound):
        if t!="sparse":  cmat = np.zeros((b, b - offs[i]), dtype=t)
        else: cmat = dok_matrix((nw, nw - offs[i]), dtype=np.uint8)  # last matrix is sparse matrix
        mats.append(cmat)
		
    return mats


def jobCoocc(inqueue, outqueue, wtoi, procID, lock, upbound, offs, wtol, winocc, Config):

    """
    Job that computes co-occurrences which can be run in parallel.

    :param inqueue: Jobs to do by process
    :param outqueue: Results of process
    :param wtoi: Dictionary mapping word to index
    :param procID: Process ID
    :param lock: Shared lock to manage access to critical resources
    :param upbound: List of tuples containing word index and data type
    :param offs: List of offsetted indices
    :param wtol: Dictionary mapping word to lemma
    :param winocc: Boolean for window-based co-occurrences, ie. True for window-based, False for document-based
    :param Config: Configuration object
    """

    if procID%3 == 1: print("Start ", procID)
    mats = getMats(upbound, offs, len(wtoi))
    rdocs = 0
    while inqueue:
        try:
            (fname, content) = inqueue.get_nowait()
        except queue.Empty:
            time.sleep(0.51)
            continue
        if fname == "Stop":
            inqueue.put((fname, content))
            break
        nrdocs = getWindowOrDocCoocc(content, mats, upbound, offs, wtoi, wtol, procID, rdocs, winocc, Config.maxWordsCoocc)
        rdocs += nrdocs
    print("Done Merge Own", procID, " Read Docs:", rdocs) #aggregate if possible
    pchunk = 1 #chunks of a process
    nmerges = 0
    if upbound[-1][1] == "sparse":  mats[-1] = mats[-1].tocsr() #only if count words
    while True:
        try:
          cmats = []
          lock.acquire()
          (fname, npchunk) = outqueue.get_nowait()
          for i in range(len(mats)):
              m = outqueue.get_nowait()
              if upbound[i][1] == "sparse": m = m.tocsr()
              cmats.append(m)
          lock.release()
          for i, m in enumerate(cmats):
              mats[i] += cmats[i]
          pchunk += npchunk
          nmerges += 1
        except queue.Empty:
            lock.release()
            break
    lock.acquire()
    outqueue.put((fname, pchunk))
    for m in mats: outqueue.put(m)
    lock.release()
    print("Done Merge Other", procID, nmerges)


def getWindowOrDocCoocc(docs, mats, lbound, offs, wtoi, wtol, procID, rdocs, winocc, maxWordsCoocc):

    """
    Computes co-occurences of documents and updates co-occurrence matrices.

    :param docs: List of documents
    :param mats: List of placeholders matrices for co-occurrences
    :param lbound: List of indices, eg. [10,100,1000], where 10 means up to element 10 use mat0, up to ind 100 mat1, ... if lastind use lastmat
    :param offs: List of offsetted indices
    :param wtoi: Dictionary mapping word to index
    :param wtol: Dictionary mapping word to lemma
    :param procID: Process ID
    :param rdocs: Total count of processed documents
    :param winocc: Boolean for window-based co-occurrences, ie. True for window-based, False for document-based
    :param maxWordsCoocc: Maximum number of words to compute
	
    :returns: Count of processed documents
    """

    ndocs=0
    for id,d in enumerate(docs):
        words = d#.split(" ")
        if len(words) < minwperdoc:
            continue
        if (rdocs+ndocs+1) % 1000 == 0:
                print("Docs processed", rdocs+ndocs, procID)
        ndocs+=1
        if winocc:
            #Get window based coocc in one doc
            ocwo = [wtol[w] for w in words if w in wtol and wtol[w] in wtoi]
            for iw,w in enumerate(ocwo):
                indw =wtoi[w]
                for w2 in ocwo[max(0,iw-winwid):min(len(ocwo),iw+winwid+1)]:
                   if w!=w2:
                       (minind, maxind) = (indw, wtoi[w2]) if indw < wtoi[w2] else (wtoi[w2], indw)
                       cb = 0
                       while maxind >= lbound[cb][0]: cb += 1
                       # if minind<offs[cb]:    print(minind,maxind,cb,offs,lbound
                       mats[cb][minind, maxind - offs[cb]] += 1
        else:
            #Get document based coocc
            uwords = list(set(words)) #[:rconfigLar.maxWordsdPerDoc]
            if len(uwords) < maxWordsCoocc:
                ocwo = [w for w in uwords if w in wtoi]
                for iw, w in enumerate(ocwo):  # use set to get only unique words
                    indw = wtoi[w]
                    for w2 in ocwo[iw+1:]:
                         #var lbound looks like [10,100,1000], where 10 means up to ele 10 use mat0, up to ind 100 mat1, ... if lastind use lastmat
                         (minind, maxind) = (indw, wtoi[w2]) if indw < wtoi[w2] else (wtoi[w2], indw)
                         cb=0
                         while maxind >= lbound[cb][0]: cb += 1
                         #if minind<offs[cb]:    print(minind,maxind,cb,offs,lbound
                         mats[cb][minind, maxind-offs[cb]] += 1
    print("skipped", len(docs)-ndocs, " of ", len(docs))
	
    return ndocs


def countReduce(inqueue, upbound):

    """
    Count co-occurrences in each queue

    :param inqueue: Jobs to do by process
    :param upbound: List of tuples containing word index and data type

    :returns: Co-occurrence matrix
    """

    lm = len(upbound) #need only length
    mats = []
    (_, pchunk) = inqueue.get_nowait()
    for i in range(lm):
        mats.append(inqueue.get_nowait())
    while True:
        try:
            (_,  cpchunk) = inqueue.get_nowait()
            for i in range(len(mats)):
                mats[i] += inqueue.get_nowait()
            pchunk += cpchunk
            print("Reduced #", cpchunk)
        except queue.Empty:
            break

    return mats


def scheduleCooccJobs(Config, docs, wtoi, upbound, offs, wtol, wincoocc):

    """
    Parallelizes computations for co-occurrence matrices and stores in files.

    :param Config: Configuration object
    :param docs: List of documents
    :param wtoi: Dictionary mapping word to index
    :param upbound: List of tuples containing word index and data type
    :param offs: List of offsetted indices
    :param wtol: Dictionary mapping word to lemma
    :param wincoocc: Boolean for window-based co-occurrences, ie. True for window-based, False for document-based
    """

    m = Manager()
    q = m.Queue()
    q1 = m.Queue()
    lock = m.Lock()
    q.put(("data",docs))
    q.put(("Stop",None))
    workers = [Process(target=jobCoocc, args=(q, q1, wtoi, i + 1, lock, upbound, offs, wtol, wincoocc, Config,)) for i in range(Config.nProc - 1)]
    print("Starting ")
    for w in workers: w.start()
    jobCoocc(q, q1, wtoi, 99, lock, upbound, offs, wtol, wincoocc, Config)
    print("Joining...")
    for w in workers: w.join()
    print("FinalRed...")
    mats = countReduce(q1, upbound)
    print("Done All cooc, need to store...")
    fend = "_win" if wincoocc else "_doc"
    for i, m in enumerate(mats): #
        if upbound[i][1] == "sparse":
            save_sparse(Config.fpath + cooccname+fend+Config.fending, mats[-1].tocsr())
        else: np.save(Config.fpath + cooccname + "de"+str(i)+fend+Config.fending, mats[i])
    #for m in mats:        print(" su",np.sum(m))
    print("Storing complete")


def GetUsedWords(Config, wcounts):

    """
    Stores most frequent words in a file; these are used in analysis, eg. for co-occ matrix

    :param Config: Configuration object
    :param wcounts: Dictionary mapping word to occurence
    """

    #allws=[w for d in docs for w in d]
    #from collections import Counter
    #wcounts=Counter(allws)
    import operator
    nwcounts = {k: v for k, v in wcounts.items() if v >= minOcc}
    print("NWords ", len(wcounts), "NWords > ", minOcc, ": ", len(nwcounts))  # , " in found words: ", len(nwcounts)
    sorted_all = sorted(nwcounts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_x = sorted_all[:Config.nWords]
    fiveper = int((len(sorted_x) - 1) * 1.0 / 20 - 1)
    print([(sorted_x[i * fiveper], i * fiveper) for i in range(min(len(sorted_x), 20))])
    with open(Config.fpath + cooccWwithFreqname, "wb") as f:  pickle.dump(sorted_x, f)


def loadCooc(Config, wincoocc):

    """
    Loads co-occurence matrices from a given context (ie. window- or document-based).

    :param Config: Configuration object
    :param wincoocc: Boolean for window-based co-occurrences, ie. True for window-based, False for document-based
	
    :returns: List of co-occurence matrices
    """
    print("loading...",datetime.datetime.now())
    with open(Config.fpath + cooccWwithFreqname, "rb") as f: usedWords=pickle.load(f)
    print("loading...", datetime.datetime.now())
    upbounds,offs = getDataTypeRanges(usedWords)
    mats=[]
    fend = "_win" if wincoocc else "_doc"
    for i,b in enumerate(upbounds):
        if b[1] == "sparse": m= load_sparse(Config.fpath + cooccname +fend+Config.fending)
        else: m = np.load( Config.fpath +cooccname+ "de"+str(i)+fend+Config.fending+".npy")
        print("Load mat",m.shape,type(m))
     #   nallp+=np.sum(m)
        mats.append(m)
    #print "loading...", datetime.datetime.now()
    #coocc = scipy.io.mmread(fpath + wikiconfig + "wcoocc.sci.mtx")
    #save_sparse_csr(fpath + wikiconfig + "wcoocc.sci", coocc.tocsr())
    print("Done loading...",datetime.datetime.now())
    return mats


def getVec(mats, iw, upbounds, offs, cWords):

    """
    Gets a word's co-occurences.

    :param mats: List of co-occurence matrices
    :param iw: Target word
    :param upbounds: List of tuples containing word index and data type
    :param offs: List of offsetted indices
    :param cWords: Number of words to analyze
	
    :returns: List of the target word's co-occurences
    """
	
    vec = np.zeros(cWords)
    maxind = iw

    # get all row entries
    #print("nok")
    for cb in range(len(mats)):
        if mats[cb].shape[0]==0 or mats[cb].shape[0]<=iw: continue
        nvpart = mats[cb][iw, :]
        nvpart = np.asarray(nvpart.todense()).squeeze() if scipy.sparse.issparse(nvpart) else nvpart
        #print(type(nvpart),nvpart.shape)
        #nvpart = np.asarray(nvpart).squeeze()  # reshape(max(nvpart.shape),1)
        vec[:nvpart.shape[0]] += nvpart
    cb = 0
    #print("ok")
    #
    # while cb<len(mats)-1 and (not (maxind < offs[cb+1] and maxind>=offs[cb])) or (mats[cb].shape[0]==0): cb += 1 #
    # print(mats[cb].shape,iw,offs[cb],cb)
    # nvpart = mats[cb][iw,:]
    # nvpart = nvpart.todense() if scipy.sparse.issparse(nvpart) else nvpart
    # nvpart = np.asarray(nvpart).squeeze()#reshape(max(nvpart.shape),1)
    # #print(len(nvpart), nvpart.shape,type(nvpart))
    # #nv=nvpart.flatten()
    # #print(len(nv),nv.shape)
    # vec[:len(nvpart)]=nvpart
    # cb+=1
    # if cb==len(mats):return vec
    #print(iw, iw - offs[cb], upbounds[cb][0], "bef", vec)

    # get column for entry iw, ie. all words which are less frequent and have iw'<iw
    while maxind >= upbounds[cb][0]: cb += 1
    #print(" sh",mats[cb][:, iw - offs[cb]].shape)
    nvpart = mats[cb][:, iw - offs[cb]]
    nvpart = np.asarray(nvpart.todense()).squeeze()  if scipy.sparse.issparse(nvpart) else nvpart
    #nvpart = np.asarray(nvpart).squeeze()#nvpart.reshape(max(nvpart.shape), 1)
    vec[:upbounds[cb][0]]+=nvpart#.flatten()
    # print("aft", vec)
    # print("nv",nvpart)
    # while cb<len(mats): #upbounds[cb][0]
    #     nvpart=mats[cb][iw,:]
    #     nvpart = nvpart.todense() if scipy.sparse.issparse(nvpart) else nvpart
    #     #nvpart=nvpart.reshape(max(nvpart.shape),1)
    #     nvpart = np.asarray(nvpart).squeeze()
    #     vec[offs[cb]:upbounds[cb][0]]+=nvpart#.flatten() #[iw, :upbounds[cb][0] - offs[cb]]
    #     cb+=1
    #
    # print("aft2",vec)
    return vec


def getCoocc(Config, docs, wCounts, wtol):

    """
    Gets co-occurence matrices of words and store in files for both contexts (ie. window- or document-based).
	Context dictates the definition of 'co-occurence', ie. either within the same window or the same document.

    :param Config: Configuration object
    :param docs: List of documents
    :param wCounts: Dictionary mapping word to occurence
    :param wtol: Dictionary mapping word to lemma
    """

    #get counts and words
    GetUsedWords(Config, wCounts)
    with open(Config.fpath + cooccWwithFreqname, "rb") as f: sorted_words=pickle.load(f)
    countDict ={k:v for k, v in sorted_words}
    wtoi = {w[0]:i for i, w in enumerate(sorted_words)}
    #get co-occurrences
    #fdocs = [[w for w in d if w in wtoi] for d in docs ]
    upbound, offs = getDataTypeRanges(sorted_words)
    for wincoocc in [True,False]:
        scheduleCooccJobs(Config, docs, wtoi, upbound, offs, wtol, wincoocc)
        #get frequent words for each word as matrix
        itow = {i:w for w, i in wtoi.items()}
        # get weight for each word, eg. smoothed inverse frequency, motivated by pmi, pointwise mutual information
        cWords = min(Config.nWords,len(itow))
        mats = loadCooc(Config, wincoocc)
        assDict = {}
        assDictAbs = {}

        nwin = sum([len(d)-2*winwid for d in docs]) #there are less full wins, since beginning and end only partial; they are still windows, but not as big
        nScale = 1.0 / nwin # a pair occurs in a window with prob #winsize/nwin,

        for i in range(cWords):
            vraw = getVec(mats, i, upbound, offs, cWords) #get co-occurrence vector

            #PMI score
            totalOccs = np.array([countDict[itow[iw]] for iw in range(vraw.shape[0])])
            px = np.clip(countDict[itow[i]]*nScale, 1e-10, 1)
            py = np.clip(totalOccs *nScale, 1e-10, 1)
            pxy = np.clip(vraw *nScale, 1e-30, 1)
            npmi= (np.log(pxy/(px*py)) / -np.log(pxy))

            def removeRare(l, distr): #if words occur very rarely, co-occ can be coincidentially ->
                 pCurr = distr* (totalOccs >= l)
                 vres = np.flip(np.sort(pCurr)[-Config.overviewMaxMissAssociations:], axis=0)
                 ires = np.flip(np.argsort(pCurr)[-Config.overviewMaxMissAssociations:], axis=0)
                 return list(zip(ires, vres))

            assDict[i] = {"All":removeRare(30, npmi)}
            assDictAbs[i] = {"All": removeRare(30, pxy)}
            #print(itow[i],countDict[itow[i]],vraw )

        #print("Percentiles of Occ: Top 20%, Top 80%",np.percentile(totalOccs, 20),np.percentile(totalOccs, 80))
        fend = "_win" if wincoocc else "_doc"
        with open(Config.fpath + Config.assSurname + fend + Config.fending +".pic", "wb") as f:  pickle.dump(assDict, f)
        with open(Config.fpath + Config.assAbsname + fend + Config.fending +".pic", "wb") as f:  pickle.dump(assDictAbs, f)
        with open(Config.fpath + Config.coiTowname + Config.fending + ".pic","wb") as f: pickle.dump(itow, f)


def generateCooccVecs(Config):
    with open(Config.fpath + cooccWwithFreqname, "rb") as f: sorted_words = pickle.load(f)
    #countDict = {k: v for k, v in sorted_words}
    wtoi = {w[0]: i for i, w in enumerate(sorted_words)}
    mats = loadCooc(Config,False)
    cWords = min(Config.nWords, len(wtoi))
    upbound, offs = getDataTypeRanges(sorted_words)
    import scipy.stats
    coen=[]
    for i in range(cWords):
        vraw=getVec(mats,i,upbound,offs,cWords) #get co-occurrence vector
        cou=np.sum(vraw)+1e-20
        ent=scipy.stats.entropy(vraw/cou)
        coen.append((cou,ent))
    with open(Config.fpath + Config.cooccVecs + Config.fending + ".pic", "wb") as f:  pickle.dump(coen, f)


#load all nodes and edges to plot a graph
# def loadgraphDat():
#     imat=np.load(fpath+Config.igname+fending+".npy")
#     amat = np.load(fpath + Config.agname + fending + ".npy")
#     vamat = np.load(fpath + Config.vagname + fending + ".npy")
#     vmat = np.load(fpath + Config.vgname+fending+".npy")
#     with open(fpath+Config.coiTowname,"rb") as f: coitow=pickle.load(f)
#     return imat,vmat,itow,amat,vamat

if __name__ == '__main__':
    #print("Reading jobads - limit", Config.nDoc)
    # import jobads
    # docs = jobads.readJobAds(nDoc)[:500]
    # sdocs=[d.split(" ") for d in docs]
    # sdocs=[[w for w in d if len(w)>1] for d in sdocs]
    # getCoocc(sdocs)
    from Config import Cfg
    import pickle as pl
    Conf = Cfg()
    def printDict(rawName, samples=5):
         fname = Conf.fpath + rawName + Conf.fending + ".pic"
         with open(fname, "rb") as f:
             data = pl.load(f)
         return data

    wToL = printDict(Conf.wToLemmaname)
    #wcounts = printDict(Conf.wcountsname)
    #perAd = printDict(Conf.perAdOccname)
    #compwords = printDict(Conf.compoundsname)

    coitow = printDict(Conf.coiTowname)
    phrl = printDict(Conf.longwordPhrname, samples=0)
    phrlDoc = printDict(Conf.longwordPhrDocsname, samples=0)
    assDictWin = printDict(Conf.assSurname + "_win", samples=0)
    assAbsDictWin = printDict(Conf.assAbsname + "_win", samples=0)
    assDictDoc = printDict(Conf.assSurname + "_doc", samples=0)
    assAbsDictDoc = printDict(Conf.assAbsname + "_doc", samples=0)




