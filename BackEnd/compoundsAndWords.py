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
import multiprocessing as mp
import textTools as tt
import numpy as np
import json
from collections import Counter

# 3rd Party libs
from stanfordcorenlp import StanfordCoreNLP

# Path setting
import sys
sys.path.append('../')

# Project libs
import textTools as tt


def addWord(wmap, tok, lem):

    """
    Takes a pair of token and its lemmatized form and update dictionary which maps tokens to their lemmas.
    It uses a set of heuristics to deal with conflicts.

    :param wmap: Dictionary which maps tokens to their lemmas
    :param tok: Token
    :param lem: Lemmatized form of the token
    """

    if (not tok in tt.setStopWords) and (not (tok.isupper() and tok.lower() in tt.setStopWords)): #Don't add stopwords - but be carful US vs us
        olem = lem
        lem = lem.lower()  # makes many things simpler
        if tok in wmap:  # tok is mapped already..., this is needed, sometimes the lemmatizing is inconsistent, eg. "prototyping" might go to "prototyping" or "prototype"
            if wmap[tok] != lem: #token exists in map, but is mapped differently
                clem = wmap[tok]
                if len(lem) < len(clem):  ##new word is shorter (usually this means no plural form or so), eg. houses vs house
                    if not clem in wmap or wmap[clem] == clem: #if not exists, add new mapping from old lemma of word to new lemma,eg. if mwords[Houses]=houses then we add mwords[houses]=house
                        wmap[clem] = lem
                else:
                    if not lem in wmap or wmap[lem] == lem: #existing lemma is shorter, we map to new lemma to the existing one
                        wmap[lem] = wmap[tok]
                    lem = wmap[tok]
        wmap[tok] = lem
        wmap[lem] = lem  # a lemma maps to itself (maybe difference in capitalization)
        if olem != lem:  wmap[olem] = lem  # a lemma maps to itself
        if len(tok) > len(lem) and not tok.islower(): #if have Responsibilities -> responsibility, than add  responsibilities -> responsibility, the  ">=" might be changed to ">" without much loss
            addWord(wmap,tok.lower(),lem)

def parseSentences(jobidsentences):

    """
    Parses sentences to get tokens that are lemmatized as well as compounds
    Preferably it uses the StanfordeCoreNLP Parser that must be installed separatedly to get lemmas and compounds
    If the StanfordeCoreNLP Parser is not available, it uses NLTK's lemmatization, which is not as good. No compounds are computed, since heuristic rules showed they are to noisy.


    :param jobidsentences: Contains job ad ID, job ad contents (in json), and configuration object

    :returns: List of lemmas, dictionary mapping token to lemma, and list of tuples containing job ad ID and a list of parsed job ads
    """

    jobid, docs, Config = jobidsentences

    #start stanford server, we need to find an open port through guessing
    maxtries = 12
    tries=0
    err=[]
    while tries <maxtries:
        try:
            np.random.seed()
            jobid = np.random.randint(0, 2000)
            nlp = StanfordCoreNLP(Config.parserPath, port=8000+(jobid%2000), memory='8g', timeout=500000) #https://github.com/Lynten/stanford-corenlp
            maxtries = 0
            print("Starting DepParse", jobid)
        except IOError as e:
            err=e
            tries += 1

    wmap = {}
    #wcou={} #word counts
    compounds = [] #of lemmatized words
    newdocs = []
    useNLTK = not "nlp" in locals()  # check if StanfordCoreParser could be used, if not use NLTK lemmatizer
    if useNLTK:
        print("StanfordCoreNLP parser not found or ioport in use - We automatically try another;", "Message ",err, " Jobid",jobid)
        # from nltk.stem import WordNetLemmatizer
        # lemmatizer=WordNetLemmatizer()
    props = {'annotators': 'tokenize, ssplit, lemma, depparse', 'pipelineLanguage': 'en', 'outputFormat': 'json'} #options for parsing
    failed=0
    for i, (docid, d) in enumerate(docs):
        if i%10 == 9: print(docid, jobid)
        if useNLTK:
            words=tt.docSpacePunctuation(d).split(" ")
            for w in words:
                lem=tt.changeWord(w) #lem = lemmatizer.lemmatize(w)
                if not len(lem): lem=w
                addWord(wmap, w, lem)
            newdocs.append((docid, words))
        else: #Use StanfordCoreParser
            docTokens = []
            parseRes = nlp.annotate(d, properties=props)
            try: var = json.loads(parseRes)
            except json.decoder.JSONDecodeError as e:
                print(" Not parsed", e, str(d)[:30].replace("\n", ""), str(parseRes)[:30].replace("\n", ""))
                failed += 1
                newdocs.append((docid, docTokens))
                continue

            for s in var["sentences"]:
                    csent = []
                    currcomp = []
                    mapTow = {}
                    for i, b in enumerate(s["enhancedPlusPlusDependencies"]):
                        tok = s["tokens"][b["dependent"]-1]["word"]
                        lem = s["tokens"][b["dependent"]-1]["lemma"]
                        #print("t,l",tok,lem,b["dep"],b["dependent"])
                        if b["dep"] == "compound": #if part of compound
                            # compounds should be pure words, Stanford parser often creates clutter words like "Section_1" or so
                            if len(tok) > 1 and tok.isalpha(): #note this skips non-alpha words!
                                currcomp.append((tok, lem)) #tok also ok, but leads to some redundant words => communication skill, communication skills
                                iEnd = b['governor']
                                mapTow[b["dependent"]] = ""
                        elif len(currcomp) > 0 and b['dependent'] == iEnd: #last word of compound
                            rawcomp = " ".join([x[0] for x in currcomp]) #create compounds (except last word)
                            comp = " ".join([x[1] for x in currcomp])
                            if len(tok) > 1 and tok.isalpha(): #last word is alpha => add it
                                rawcomp += " " + tok
                                comp += " " + lem
                            else: addWord(wmap, tok, lem) #add last word as new word if non-alpha => not really needed
                            if len(comp.split()) > 1: #if compound
                                comp = comp.lower() #all lemmas are lower case
                                compounds.append(comp)
                            addWord(wmap, rawcomp, comp)
                           # wcou[tok] = wcou.get(rawcomp, 0) + 1
                            currcomp = []
                            mapTow[b["dependent"]] = rawcomp
                        elif not (b["dep"] == "punct" or (lem in tt.setStopWords and not tok == "IT" ) or (len(tok) == 1 and not tok in ["R", "C"])): #a single word / no compound
                                #wcou[tok]=wcou.get(tok,0)+1
                                addWord(wmap, tok, lem)

                    for i, t in enumerate(s["tokens"]): #add all tokens (single words/compounds)
                         if i+1 in mapTow:
                             if len(mapTow[i+1]) > 0: csent.append(mapTow[i+1])
                         else:
                             if "-lrb-" in t["word"].lower(): csent.append("(") #left bracket
                             elif "-rrb-" in t["word"].lower(): csent.append(")") #right brackt
                             else: csent.append(t["word"])
                    #print("wmap", wmap)
                    docTokens.append(" ".join(csent))
            newdocs.append((docid, docTokens))
    if not useNLTK: nlp.close()
    print(" Parse errors", failed, "out of", len(docs))

    return compounds, wmap, newdocs #,wcou

def getCompoundsAndWords(Config, docs):

    """
    Get compound words from job ads.
    Implements process parallelization and results merging.

    :param Config: Configuration object 
    :param docs: List of strings, each string being a job ad

    :returns: Counter object of compund words, dictionary mapping token to lemma, and list of tuples containing job ad ID and list of parsed sentences

    Example:
    Input:
    docs = [(1, "This is great (Python and R are cool). But brackets (yeah) are changed.")]
    Output:
    print(getCompoundsAndWords(cfg, docs)) >> (Counter(), {'This': 'this', 'this': 'this', 'great': 'great', 'Python': 'python', 'python': 'python', 'R': 'r', 'r': 'r', 'cool': 'cool', 'But': 'but', 'but': 'but', 'brackets': 'bracket', 'bracket': 'bracket', 'yeah': 'yeah', 'changed': 'changed', '': ''}, [(1, ['This', 'is', 'great', 'Python', 'and', 'R', 'are', 'cool', 'But', 'brackets', 'yeah', 'are', 'changed', ''])])
    """

    joblist = docs
    nProc = min(12, Config.nProc)
    pool = mp.Pool(processes=nProc)
    chunkSize = max(1, len(joblist)//(4*nProc))
    chunkedList = [[i, joblist[i:i + chunkSize], Config] for i in range(0, len(joblist), chunkSize)]
    print("Getting compounds #jobs", len(chunkedList), " chunkSize", chunkSize, " #proc", nProc)
    compsWords = pool.map(parseSentences, chunkedList)
    print("Got all compounds")
    # merge results
    compounds = [r[0] for r in compsWords]
    words = [r[1] for r in compsWords]
    newdocs = [r[2] for r in compsWords]
    #wcou = [r[3] for r in compsWords]
    ndocs = sum(newdocs, [])
    allocc = dict(Counter(sum(compounds, [])))
    #allwcou= sum((Counter(dict(x)) for x in wcou), Counter())

    #merge mappings from different processes
    mwords = words[0]
    for ws in words[1:]:
        for k, v in ws.items():
            addWord(mwords, k, v)

    return Counter(allocc), mwords, ndocs

def getInv(wmap):

    """
    Get the inverse map of a dictionary.

    :param wmap: Dictionary

    :returns: Dictionary which is an inverse of the input dictionary
    """

    inv_map = {}
    for k, v in wmap.items():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)

    return inv_map

def removeLongCompounds(Config, comps, wordToLemma):

    """
    Removes lengthy compound terms.

    :param Config: Configuration object
    :param comps: Counter object of compund terms 
    :param wordToLemma: Dictionary mapping token to lemma

    :returns: Counter object of compound terms
    """
    if not len(comps): return Counter(comps)
    thres = max(Config.minCompoundCount//2, comps.most_common(50)[-1][1] // 10)  # use count of 10th most common word
    if thres > Config.minCompoundCount//2: print("Thres",thres)

    #get all possible compound candidates, ie. all compounds split into parts of length 1, 2,3
    splitcomp = [] #only lower case
    for k in comps:
        parts = k.lower().split() #single words
        splitcomp += [parts[k] + " " + parts[k+1] for k in range(len(parts)-2)] #2 parts
        splitcomp += [parts[k] + " " + parts[k + 1] + " " + parts[k+2] for k in range(len(parts)-3)] #3 parts
    countsSplit = Counter(splitcomp) + comps

    allcomp = {}
    rem = 0
    inv_map = getInv(wordToLemma)
    acomps = [w for w in wordToLemma if len(w.split()) > 1]
    for k in acomps: #go through all current compounds
        if k in wordToLemma: parts = wordToLemma[k].split()
        else: parts = k.split()
        remove = False
        replace = []
        if len(parts) == 3: #check if should remove compound, ie. if not very frequent or subcompound much more frequent
                w0l = (parts[0] + " " + parts[1]).lower()
                w1l = (parts[1] + " " + parts[2]).lower()
                nw0 = countsSplit[w0l] if w0l in countsSplit else -1
                nw1 = countsSplit[w1l] if w1l in countsSplit else -1
                if nw0 > 3*countsSplit[k] and nw0 > nw1 and nw0 > thres:# and countsSplit[k]<5*minCompoundCount:
                    replace = [(parts[0] + " " + parts[1], w0l), (parts[2], parts[2].lower())]
                    remove = True
                elif nw1 > 3*countsSplit[k] and nw1 > thres:# and countsSplit[k]<5*minCompoundCount:
                    replace = [(parts[0], parts[0].lower()), (parts[1] + " " + parts[2], w1l)]
                    remove = True
                elif comps[k] <= thres:
                    replace = zip(parts, [p.lower() for p in parts])
                    remove = True
        elif len(parts) > 3: #extremely long compound, Stanford parser creates them often; mainly wrong; replace by most frequent biterm, if non-exists, add single words
            remove = True
            partw = [(parts[k] + " " + parts[k+1], k) for k in range(len(parts)-2)] #bi-terms
            freq = [comps[p.lower()] if p.lower() in comps else -1 for p, k in partw]
            ipart = np.argmax(freq)
            if freq[ipart] > thres:
                singlewords = set(np.arange(len(parts))) - set([partw[ipart][1], partw[ipart][1]+1]) #get indexes of single words
                #upartw = [parts[k] + " " + parts[k+1] for k in range(len(parts)-2)]
                replace = [(partw[ipart][0], partw[ipart][0].lower())] + [(parts[iw], parts[iw].lower()) for iw in singlewords]
            else:
                replace = zip(parts, [p.lower() for p in parts])

        if not remove: allcomp[k] = allcomp.get(k, 0) + comps[k]
        else:
            for t in replace: #replace compound by subterms
                    w, tow = t
                    addWord(wordToLemma, w, tow)
                    if len(w.split()) > 1 and k in wordToLemma: #if a part is itself a compound
                        mcomp = wordToLemma[k]
                        if mcomp in comps:
                            allcomp[mcomp] = allcomp.get(mcomp, 0) + comps[mcomp]
                            del comps[mcomp] #avoid double counting
            if k in inv_map: #we delete the compound, ie. all values that map to it, that's why we need the inverse map
                    for todel in inv_map[k]+[k]:
                       if todel in wordToLemma:
                           del wordToLemma[todel]
            rem += 1
    print("Removed", rem)

    return Counter(allcomp)

def checkComp(parts, ind, wmap):

    """
    Finds longest compound terms from list of tokens starting at an index.

    :param parts: List of tokens
    :param ind: Index of the current token 
    :param wmap: Dictionary mapping token to lemma

    :returns: Longest compound term, index after the longest compound term
    """

    w = ""
    newind = ind + 1
    for i in range(ind, min(ind+4, len(parts))):
        cw = " ".join(parts[ind:i+1])
        if cw in wmap:
            w = wmap[cw]
            newind = i + 1

    return w, newind

# def getTrans(doc,wmap):
#     parts=doc.split()
#     tdoc=[]
#     j=0
#     while j < len(parts):
#         w, newind = checkComp(parts, j, wmap)
#         if len(w): tdoc.append(w.replace(" ","_"))
#         j=newind
#     return  tdoc

if __name__ == '__main__':
    from Config import Cfg
    cfg = Cfg()
    docs = [(1, "This is great (Python and R are cool). But brackets (yeah) are changed.")]
    getCompoundsAndWords(cfg, docs)