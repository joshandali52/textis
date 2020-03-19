"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

# Python libs
import multiprocessing as mp
import sys,os,glob
sys.path.append(os.getcwd()+"/../")
print("Current Rootpath", os.getcwd()+"../")
import numpy as np
import operator
import pickle
from collections import Counter
import BackEnd.compoundsAndWords as cw
import re
from bs4 import BeautifulSoup

# Project libs
import BackEnd.coocc
import textTools

bsep = "___"


def readJobAds(Config, number=99999999):

    """
    Reads all job advertisements (documents), each file contains one job advertisement.
	
    :param Config: Configuration object
    :param number: Maximum number of documents

    :returns: List of tuples containing filename and document
    """
	
    import os,glob    #print os.getcwd()
    docs = []
    fnames = [y for x in os.walk(Config.fpath+Config.cleanedPath) for y in glob.glob(os.path.join(x[0], '*.txt')) ]
    for fname in sorted(fnames)[:number]:
        with open(fname,"r",encoding="utf8") as f:
            d= f.read()
            docs.append((fname,d))

    return docs


def tokenDoc(doc, mapWord, biterms, oWordCount):

    """
    Splits document into tokens.
    Updates dictionary mapping token to occurence and returns list of lemmas.
	
    :param doc: String
    :param mapWord: Dictionary mapping token to frequency
    :param biterms: List of valid composite words (bi-terms), ie. a bi-term is composed of two words
    :param oWordCount: Dictionary mapping lemma to list of original word

    :returns: List of lemmas

    Example:
    Input:
    doc = "Hello world! Computer Science rocks."
    biterms = {"Computer Science"}
    oWordCount, mapWord = {}, {}

    Output:
    print(tokenDoc(doc, mapWord, biterms, oWordCount)) >> ['hello', 'world', '\n', 'computer', 'science', 'rock', '\n']
    print(mapWord) >> {'hello': 1, 'world': 1, '\n': 2, 'computer': 1, 'science': 1, 'rock': 1}
    print(oWordCount) >> {'hello': ['Hello'], 'world': ['world'], 'computer': ['Computer'], 'science': ['Science'], 'rock': ['rocks']}
    """

    words = []
    wo = textTools.docToWords(doc, biterms, oWordCount)
    for stWord in wo:
        if not stWord in mapWord:
            mapWord[stWord] = 1
            words.append(stWord)
        else:
            words.append(stWord)
            mapWord[stWord] += 1
			
    return words

# def processGentle(corpus,bterms): #less aggressive than for topic Modeling
#     import BackEnd.tkm.algTools
#     mapWord = {}
#     oWordCount ={}
#     tokDocs = [tokenDoc(d, mapWord,bterms,oWordCount) for d in corpus]
#     mapWord["\n"]=1 #make return unimportant
#     idocs, iToWordDict, wordToiDict,wCounts = BackEnd.tkm.algTools.wordsToIndex(tokDocs)
#     #we have a map of stemmed/lemmatized words to their originals, pick the most frequent word as representative
#
#     def most_common(lst):
#         data = Counter(lst)
#         return max(lst, key=data.get)
#     oWordMap = {k:most_common(v) for k,v in oWordCount.items()}
#     #Remove short docs and words that only occur once
#     # wco = {}
#     # mindoclen = 1
#     # for i,d in enumerate(idocs):
#     #     if (len(d)<mindoclen): #filter short docs, they only cause trouble later on
#     #         continue
#     #     for w in d:
#     #         if len(iToWordDict[w])>1: #remove words of length 1
#     #             wco[w]=wco.get(w,0)+1
#
#     #wMoreOnce = set(range(len(iToWordDict))) - set([w for w,c in wco.items() if c < 2]) #newMap = { w:i for i,w in enumerate(wMoreOnce)}
#     #newdocs = [[iToWordDict[w] for w in d if w in wMoreOnce]  for d in idocs] #remove unique words
#     #idocs, iToWordDict, wordToiDict,wCounts = tkm.algTools.wordsToIndex(newdocs)
#     return idocs,iToWordDict,wCounts,oWordMap



def getDocPhr(docs, longPhrases, wmap, Config, procID=0, rdocs=0):

    """
    Gets phrases, ie. a word and its context.
    For example, with the word 'data', its context could be "I like data science a lot", "Data augmentation is important", etc.
	
    :param docs: List of documents
    :param longPhrases: Dictionary mapping word to list of tuples containing document id and word's context
    :param wmap: Dictionary mapping tokens to their lemmatized forms
    :param Config: Configuration object
    :param procID: Process id
    :param rdocs: Total count of processed documents
	
    :returns: Count of processed documents
    """

    ndocs = 0
    for id,(docid, d) in enumerate(docs):
        if id%200 == 0: print(" ", id)
        #words = textTools.docSpacePunctuation(d).split(" ")  #textTools.patternSpace.sub(lambda m: textTools.repSpace[re.escape(m.group(0))], d).replace("  "," ").split(" ")
        #if len(words) < 2*phrwid:  continue
        if (rdocs+ndocs+1) % 1000 == 0:  print("Docs processed", rdocs+ndocs, procID)
        ndocs += 1
        for l in d:
            parts = l.split(" ")
            j = 0
            while j < len(parts):
                w, off = cw.checkComp(parts, j, wmap)
                if len(w):
                    if not w in longPhrases: longPhrases[w] = []    #if len(longPhrases[w]) <longMaxPhrPerWord: longPhrases[w].append((id," ".join(parts[max(0, j - longphrwid):min(len(parts), j + longphrwid + 1)])))
                    if len(longPhrases[w]) < Config.longMaxPhrPerWord:
                        firstPart = " ".join(parts[max(0, j - Config.longphrwid):j])
                        word = "<b> " + w + " </b>"
                        secondPart = " ".join(parts[off:min(len(parts), off + Config.longphrwid + 1)])
                        longPhrases[w].append((docid, firstPart+word+secondPart))    #longPhrases[w].append((id, " ".join(parts[max(0, j - longphrwid):min(len(parts), j + longphrwid + 1)])))
                j+=1 #was +off before, but this is wrong if words overlap ie. "machine learning" "learning algorithm" is not both detected for machine learnign algorithm
    print("skipped", len(docs)-ndocs, " of ",len(docs))

    return ndocs

# Example:
#docs= [["Hello","world"],["Computer science","rocks"]]
#wmap={"Hello":"hello","world":"world","Computer science":"computer science","rocks":"rock"}
#Output:
#wCounts={"Hello":"1,"world":1,"Computer science":1,"rocks":1}
# actual output: %TODO%
# print(getWCounts(docs, wmap) >> {'hello': 0, 'world': 0, 'computer science': 0, 'rock': 0}
def getWCounts(docs, wmap):

    """
    Gets counts of each token (either a word or compound).
	
    :param docs: List of tuples containing document id and documents (String)
    :param wmap: Dictionary mapping token to lemma
	
    :returns: Dictionary mapping token to frequency
    """

    ndocs = 0
    maxStoreMissing = 20
    wCounts = {k:0 for k in wmap.values()} #this should strictly be not necessary, but with the compounds it avoids some special cases
    miss = []
    for id,(_, d) in enumerate(docs):
        #if id%800==0: print(" ",id)
        if (ndocs+1) % 1000 == 0: print("Docs processed", ndocs)
        ndocs += 1
        for l in d:
            parts = l.split()
            j = 0
            oktil = 0
            while j < len(parts):
                w, off = cw.checkComp(parts, j, wmap)
                if len(w): wCounts[w] = wCounts.get(w, 0) + 1
                else:
                    if not parts[j].lower() in textTools.engStop and parts[j].isalpha():
                        if len(miss) < maxStoreMissing and j >= oktil:
                            miss.append((parts[j], parts[j-3:j+3]))
                j += 1 #was +off before, but this is wrong if words overlap ie. "machine learning" "learning algorithm" is not both detected for machine learning algorithm
                oktil = max(off, oktil)
    print("Missing in wmap", miss)
    print("skipped", len(docs)-ndocs, " of ", len(docs))
	
    return wCounts


def removeDuplicates(docs):

    """
    Remove identical documents (duplicates).
	
    :param docs: List of documents (String)
	
    :returns: List of tuples containing document id and document, where document id is the document's position in the input list
    """
	
    import hashlib
    def hsh(txt):
        a = hashlib.md5()
        a.update(txt.encode('utf-8'))
        return a.hexdigest()
    uniqueDocs = {}
    idDocs = {}
    for id, d in docs:
        hval = hsh(d)
        uniqueDocs[hval] = d #just overwrite
        idDocs[hval] = id

    return [(idDocs[hval], uniqueDocs[hval]) for hval in uniqueDocs]


def removeIrrelevant(Config, docs):

    """
    Paralleliezs removal of irrelevant parts of job advertisements.
    This is done by using i) a pre-trained classifier and ii) manual examples and manual rules.
	
    :param Config: Configuration object
    :param docs: List of documents (String)
	
    :returns: List of documents (String)
    """

    def chunkIt(seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0
        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg
        return out

    nProc = Config.nProc
    pool = mp.Pool(processes = nProc)
    joblist = chunkIt(docs, nProc)
    print("Removing irrelevant content")
    res = pool.map(removeIrrelevantJob, joblist)  # run in parallel
 
    return sum(res, [])


def isIrrelevantManualRules(s, cdoc):

    """
    Hand-crafted rules to remove paragraphs or entire documents from job advertisements
	
    :param s: String
    :param cdoc: List of parts of document (String)
	
    :returns: Boolean (ie. True if removal is needed), list of parts of documents (String), length of irrelevant parts
    """

    if len(s) < 4: return True, cdoc, len(s) #too short
    if "Monster" in s[:15]: return True, cdoc, len(s) #Paragraph with monster
    if "Newspaper logo is conditionally" in s:
        return True, [], sum([0]+[len(s) for s in cdoc]) # reset doc, everything above is not relevant for monster jobs, this also includes "Skip to main content" in s: continue
    if "About the Job" in s: return True, cdoc, len(s)
    if '="' in s: return True, cdoc, len(s)  # often html gets not removed properly, what remains is sth like &lt; link rel="stylesheet" href="https:, , coda. newjobs. com,

    return False, cdoc, 0


def removeIrrelevantJob(docs):

    """
    Removes irrelevant parts of job advertisement.
    This is done by using i) a pre-trained classifier and ii) manual examples and manual rules.
	
    :param docs: List of tuples containing document id and documents (String)
	
    :returns: List of tuples containing document id and documents (String)
    """


    import BackEnd.cleaning.classifier as classifier
    count_vect, tfidf_transformer, enc, m = classifier.getClassifier()

    ndocs = []
    remHard = 0
    remML = 0
    for i,(id, d) in enumerate(docs):
        if (i+1)%(len(docs)//5+1) == 0: print(i, "of", len(docs))
        parts = d.split("\n\n")
        cdoc = []
        for s in parts:
            #Remove irrelevant parts based on manual rules
            doContinue, ndoc, crem = isIrrelevantManualRules(s, cdoc)
            remHard += crem
            if doContinue:continue
            # Remove irrelevant parts based on a trained classifier
            lower = re.sub(r'([^\s\w]|_)+', '', s).lower() #remove initial chars if not alphanumeric
            cv = count_vect.transform([lower])
            tfidf = tfidf_transformer.transform(cv)
            cl = enc.classes_[m.predict(tfidf)][0]
            pmax = max(m.predict_proba(tfidf)[0])
            if cl == "incl" or pmax < 0.7: #Only remove if probability of removal is larger a threshold!
                cdoc.append(s)
            else:
                remML += len(s)
        ndocs.append((id, "\n".join(cdoc)))
    for t,rem in [("Classifier", remML), ("ManualRules", remHard)]:
        print(t +" removed", rem, "  ;%", np.round(100 * rem / (1e-10 + rem + sum([len(d) for d in ndocs]))))

    return ndocs


def getText(html, splitter="\n"): 

    """
    Extracts and cleans text from html.
	
    :param html: HTML file
    :param splitter: Delimiter
	
    :returns: String

    Example:
    Input:
    html = "<font color=\"#222222\" face=\"Arial\" style=\"background-color: rgb(255, 255, 255); font-size: 9pt;\">• </font><font color=\"#222222\" face=\"Arial\" style=\"background-color: rgb(255, 255, 255); font-size: 9pt;\">D</font><font color=\"#222222\" face=\"Arial\" style=\"background-color: rgb(255, 255, 255); font-size: 9pt;\">evelopment of conceptual, logical and physical data models support our existing and future Enterprise Data Architecture</font><font color=\"#222222\" face=\"Arial\" style=\"background-color: rgb(255, 255, 255); font-size: 9pt;\"> </font><br><font color=\"#222222\" face=\"Arial\" style=\"background-color: rgb(255, 255, 255);"
    
    Output:
    print(getText(html)) >>
        .
        Development of conceptual, logical and physical data models support our existing and future Enterprise Data Architecture
    """

    #Remove HTML
    html = html.replace("</li>", "\n ").replace("</br>", "\n ").replace("<br/>", "\n ").replace("</p>", "\n ").replace("&#13", "\n ")  # replace things that indicate a new paragraph by return
    soup = BeautifulSoup(html, "html.parser")
    data = soup.findAll(text=True)
    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']: return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))): return False
        return True
    result = list(filter(visible, data)) #get shown text

    #Clean txt
    txt = "".join(result)
    txt = txt.replace(u'\xa0', ' ') #unicode xa0 = Non-breaking space
    txt = txt.replace(u'\x02', ' ') #unicode x02 = start of text
    txt = textTools.toSingleLine(txt)
    txt = re.sub(r'([·•●*])', '.'+splitter+' ', txt) #list enumerations, #txt = re.sub(r'([a-z])(·)', r'\1 \2', txt)
    txt = re.sub(r'-([^a-z])', '.'+splitter+r'\1', txt)
    txt = re.sub(r' ([a-z]+)([A-Z])', r' \1'+"."+splitter+r'\2', txt) #sometimes no dots between words, eg. "This is greatDiscounts are good"
    txt = re.sub(r'([a-z]{2,99})([\.:,;\?!])([A-Z])', r'\1\2 \3', txt) #sometimes no spaces between dots etc. #often there is no space between something like "This is good.But this is not", this screws up the Stanford parser, which gets "good.But" as a word; need {2,99} for e.g. and i.e.; we only do this for small to capitla, e.g. ...good.But...  but not for urls like abb.com
    if len(txt) == 0: return ""

    def remove_html_tags(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    txt = remove_html_tags(txt) #some tags are not removed by prior step
    txt = txt.replace("/",", ") #often have stuff like "Spark/Hadoop/R/Python"
    txt = txt.replace("‘", "").replace("’", "")  # sometimes have apostrophes ‘big data’ (note: they are not identical
    txt = textTools.removeTabs(txt)
    txt = textTools.toSingleSpace(txt).replace("\n ", "\n").replace(" \n", "\n").replace("\r", "")
    txt = textTools.toSingleLine(txt)
 
    return txt


def cleanJobAd(dat):

    """
    Extracts and cleans text from html.
    Stores cleaned text.
	
    :param dat: Path to html file, filename for cleaned text, folder of html file
    :param splitter: Delimiter
	
    :returns: List of tuple containing filename for cleaned text and html file
    """

    cpath, outname, rawp = dat
    with open(cpath, "r", encoding="utf8") as f:
        html = f.read()
        #splitter = "\n\n" if "original_text_without" in rawp else "\n"  #
        splitter = "\n"
        text = getText(html, splitter)
        text = text.split("View more info")[0]
        #print("\n<newad><fname,"+cpath+">\n", text) #for training of classification
        #if ind>1: break
        if not text is None:
            #if ind%10==0: print(ind," of ",len(files)," in ",dirs,subdir)
            with open(outname, "w", encoding="utf-8") as f2: f2.write(text)
			
    return [(outname,html)]


def cleanJobAds(Config):

    """
    Preprocess job advertisements (html files) into text by removing html tags, pre-defined characters, extra whitespace, etc-
    Store the resulting text.
	
    :param Config: Configuration object
    """

    #delete old cleaned files and create path
    #for rawp in rawPaths:
    outdir = Config.fpath+Config.cleanedPath
    os.makedirs(outdir, exist_ok=True)
    files = glob.glob(outdir)
    for f in files:
        if os.path.isfile(f): os.remove(f)

    #create job list, ie. path with all files to be cleaned
    joblist = []
    outdir = Config.fpath+Config.cleanedPath
    for subdir, dirs, files in os.walk(Config.rpath): #clean files
        if len(Config.terms)!= 0:
            isIn=[t.upper() in subdir.upper() for t in Config.terms]
            if sum(isIn) == 0: continue
        for file in files:
            if file.endswith("html") or file.endswith("htm") or file.endswith("txt"):
                cpath= os.path.join(subdir, file)
                if Config.cleanedPath[:-1] in subdir:
                    print("Skip", subdir)
                    break
                outname = outdir+"jobad"+str(len(joblist))+".txt"
                joblist.append([cpath, outname, Config.rpath, ])
                if len(joblist) > 1.5*Config.nDoc: break #limit files to clean, some will be redundant

    print("Read docs/ads", len(joblist))
    pool = mp.Pool(processes=Config.nProc)
    print("Cleaning files #jobs", len(joblist), " #proc", Config.nProc)
    li = pool.map(cleanJobAd, joblist)  # run in parallel
    allads = sum(li, [])
    clToRaw = {k:v for k, v in allads}
    with open(Config.fpath+Config.cleanToRaw+Config.fending+".pic", "wb") as f:
        pickle.dump(clToRaw, f)


def getContainMap(wmap, woCounts):

    """
    Creates two lists for a target token (ie. word or compound):
    i) list of tokens contained in the target token and another,
    ii) list of tokens the target token is a part of.
    Both lists are sorted by frequency.
	
    :param wmap: Dictionary mapping token to lemma
    :param woCounts: Dictionary mapping token to frequency
	
    :returns: Dictionary mapping tokens to lists

    Example:
    Input:
    wmap = {"Computer science":"computer science","rocks":"rock", 'science':'science', 'rocked':'rock'}
    woCounts = {"computer science":1,"rocks":1,"science":2,"rocked":1}

    Output:
    cmap = {'science': {'in': [(0.5, 'computer science')], 'parts': []}, 'rock': {'in': [], 'parts': []}, 'computer science': {'in': [], 'parts': [(2.0, 'science')]}}
    """

    mappedw = set(wmap.values())
    cmap = {k:{"in":[], "parts":[]} for k in list(mappedw)}
    for k in mappedw:
        parts = k.split()
        if len(parts) > 1:
            allw = parts + [" ".join(parts[i:i+2]) for i in range(len(parts)-2)]
            for k2 in allw:
                    if k2 in mappedw:
                        if woCounts[k2] == 0: print("Error 0 count", k2)
                        if woCounts[k] == 0: print("Error 0 count", k)
                        cmap[k2]["in"].append((np.round(woCounts[k]/(woCounts[k2]+1e-10), 4), k))
                        cmap[k]["parts"].append((np.round(woCounts[k2]/(woCounts[k]+1e-10), 1), k2))
    for k in cmap:
        for v in cmap[k]:
            cmap[k][v] = sorted(cmap[k][v],reverse=True)

    return cmap


def wordsToIndex(docs, wCounts ,wmap):

    """
    Converts documents into numbers.
    For example, converts ["Hello World", "World says Hello] into, eg. [[0,1], [1,2,0]].
	
    :param docs: List of tuples containing document id and document (String)
    :param wCounts: Dictionary mapping word to frequency
    :param wmap: Dictionary mapping word to lemma
	
    :returns: List of lists of numbers, dictionary mapping number to word, dictionary mapping word to number
    """

    mdocs = [] #[array('I', [0] * len(docs[d])) for d in range(len(docs))]
    sorted_co = sorted(wCounts.items(), key=operator.itemgetter(1), reverse=True)  # create words in sorted manner by frequency, since freq are accesssed more, thus this reduces cache misses
    wordToiDict = {}
    iToWordDict = {}
    for i, (w, _) in enumerate(sorted_co):
        wordToiDict[w] = i
        iToWordDict[i] = w
    for id, d in docs:
        cdoc = []
        for iw, s in enumerate(d):
            parts = s.split()
            j = 0
            while j < len(parts):
               w, newind = cw.checkComp(parts, j, wmap)
               if len(w): cdoc.append(wordToiDict[w])
               j = newind
        mdocs.append((id, np.array(cdoc)))

    return mdocs, iToWordDict, wordToiDict


def postProcessCompounds(Config, allocc, wordToLemma, newdocs):

    """
    Removes compounds which are either too long or rare.
    Updates counts after removal.
	
    :param Config: Configuration object
    :param allocc: Counter object of compund words
    :param wordToLemma: Dictionary mapping word to lemma
    :param newdocs: List of tuples containing document id and documents (String)
	
    :returns: List of lists of numbers, dictionary mapping number to word, dictionary mapping word to frequency
    """

    #print(wordToLemma.keys())
    #print([k for k in wordToLemma.keys() if k[:2].upper() == "PY"])

    #fix capitalization => Data visualization, data visualization => data visualization
    allocc = cw.removeLongCompounds(Config, allocc, wordToLemma)
    allocc = cw.removeLongCompounds(Config, allocc, wordToLemma) #2nd iter still removes some, but not many

    # Shortcutting mapping
    invDict = cw.getInv(wordToLemma)
    print("Before Shortcutting", len(set(wordToLemma.values())))
    for k, v in invDict.items():
        if k in wordToLemma and wordToLemma[k] != k:
            for mv in v:  wordToLemma[mv] = wordToLemma[k]
    #invDict = cw.getInv(wordToLemma)
    print("After Shortcutting", len(set(wordToLemma.values())))
    # invDict = cw.getInv(wordToLemma)
    # print("Before Shortcutting", len(set(wordToLemma.values())))
    # for k, v in invDict.items():
    #     if k in wordToLemma and wordToLemma[k] != k:
    #         for mv in v:  wordToLemma[mv] = wordToLemma[k]
    # invDict = cw.getInv(wordToLemma)
    # print("After Shortcutting", len(set(wordToLemma.values())))

    woCounts = getWCounts(newdocs, wordToLemma)
    # remove rare words
    nsingrem = 0
    for k in list(wordToLemma.keys()):
        if woCounts[wordToLemma[k]] < Config.minOcc:
            nsingrem += 1
            del wordToLemma[k]

    # remove rare compositions of words
    nrem = 0
    conthres = np.percentile(list(woCounts.values()), 70) #combination should be frequent
    for k in list(wordToLemma.keys()):
        if len(k.split()) > 1:
            ratio = woCounts[wordToLemma[k]]/min([(1e-20 + woCounts[wordToLemma[p]]) if p in wordToLemma and wordToLemma[p] in woCounts else 1 for p in k.split()])
            if  ratio < 0.1 and woCounts[wordToLemma[k]] < conthres: #is a part rare?
                        for toadd in zip(k.split(), wordToLemma[k].split()):
                            cw.addWord(wordToLemma, toadd[0], toadd[1])
                        del wordToLemma[k]
                        nrem += 1
                        print("Del", k, k.split())
                        break
    print("Removed biterms", nrem, "single", nsingrem, " thres", conthres)

    wset = set(wordToLemma.values())
    nstop = 0
    # for s in textTools.setStopWords:
    #     if s in wordToLemma:
    #         nstop+=1
    #         del wordToLemma[s]
    for s in list(wordToLemma.keys()):
        parts = s.split()
        if parts[0] in textTools.setStopWords: #kills a lot of IT, eg. it consultant etc.
            if len(parts) > 1:
                newp = " ".join(parts[1:])
                if not newp in wordToLemma:
                    cw.addWord(wordToLemma, newp, " ".join(wordToLemma[s].split()[1:]))
                    #print("added",newp)
            del wordToLemma[s]
            nstop += 1
    print("Removed stopwords", nstop)
    print("wToL, wCounts - should be same", len(list(wset)), len(woCounts), " Diff", list(set(woCounts.keys())-wset)[:50], list(wset-set(woCounts.keys()))[:50])
    print("Total Compounds identified:", len(allocc), "  Freq:", len(allocc)) #, "thres", thres)
    os.makedirs(Config.fpath + "/remirr/", exist_ok=True)
    with open(Config.fpath + "/remirr/alldocsComps" + Config.fending + ".pic", "wb") as f:  pickle.dump(newdocs, f)
    woCounts = getWCounts(newdocs, wordToLemma) #count again
    with open(Config.fpath + Config.wcountsname + Config.fending + ".pic", "wb") as f:  pickle.dump(woCounts, f)
    containmap = getContainMap(wordToLemma, woCounts)  # compute again
    with open(Config.fpath + Config.compoundsname + Config.fending + ".pic", "wb") as f:  pickle.dump(containmap, f)  # freqcomp.keys()
    perAdOcc = {w: np.round(v * 1.0 / len(newdocs), 6) for w,v in woCounts.items()}  # percentage of jobAds that word occurs
    with open(Config.fpath + Config.perAdOccname + Config.fending + ".pic", "wb") as f:  pickle.dump(perAdOcc, f)
    with open(Config.fpath + Config.wToLemmaname + Config.fending + ".pic", "wb") as f:  pickle.dump(wordToLemma, f)

    print("Words to Index")
    idocs, iToWord, wtoi = wordsToIndex(newdocs, woCounts, wordToLemma)
    print("Distinct words", len(wtoi), " Total words", np.sum([len(d) for d in idocs]))
    with open(Config.fpath + Config.iTowname + Config.fending + ".pic", "wb") as f: pickle.dump(iToWord, f)
    return idocs, iToWord, woCounts


def generateFiles(Config):

    """
    Generates and stores files needed for the frontend.
	
    :param Config: Configuration object
    """

    print("Reading jobads - Max Ads to keep:", Config.nDoc)
    dupdocs = readJobAds(Config, Config.nDoc)

    print("Number of read jobads:", len(dupdocs))
    docs= removeDuplicates(dupdocs)

    print("Unique Docs/Ads", len(docs))
    docs=docs[:Config.nDoc] #limit docs

    print("Removing irrelevant content")
    docs = removeIrrelevant(Config, docs)
    os.makedirs(Config.fpath+"/remirr/", exist_ok=True)
    with open(Config.fpath + "/remirr/" + Config.remName + Config.fending + ".pic", 'wb') as f: pickle.dump(docs, f)

    #Get compound words, ie. "data mining","machine learning"
    print("Parsing to get compounds...")
    res = cw.getCompoundsAndWords(Config, docs) #get compound words
    #with open(Config.fpath + "/remirr/debug" + Config.fending + ".pic", "wb") as f: pickle.dump(res, f)  # mainly for debugging or storing state to resume since parsing takes long
    #with open(Config.fpath + "/remirr/debug" + Config.fending + ".pic", "rb") as f:  res=pickle.load(f)

    allocc, wordToLemma, newdocs = res
    idocs, iToWord, woCounts = postProcessCompounds(Config, allocc, wordToLemma, newdocs)
    with open(Config.fpath + Config.globalDat + Config.fending + ".pic", "wb") as f:
        pickle.dump({"nUsedDocs":len(idocs)}, f)

    #get Phrases, ie. a word and its context, e.g. for "data"   get "I like data science a lot", "Data augmentation is important"
    longPhrases = {}
    getDocPhr(newdocs, longPhrases, wordToLemma,Config)
    with open(Config.fpath+Config.longwordPhrname+Config.fending+".pic", "wb") as f: pickle.dump(longPhrases, f)

    # create coocc matrix
    BackEnd.coocc.getCoocc(Config, [[iToWord[w] for w in d] for _, d in idocs], woCounts, wordToLemma)



def getTerms(text, wcounts, wToL):

    """
    Gets words or compounds of a text.
	
    :param text: String
    :param wcounts: Counter object of words/compounds
    :param wToL: Dictionary mapping word to lemma
	
    :returns: List of tuples containing original text snippet and extracted word/compound
    """

    rtext = text.replace("\n", " ").replace("\t", " ").replace("  ", " ").replace("  ", " ")
    words = textTools.docSpacePunctuation(rtext).split(" ")
    foundwords = []
    words = [w for w in words if len(w)>0]
    i = 0
    while i < len(words):
        w0, off = cw.checkComp(words, i, wToL)
        if len(w0.split()) > 1: #compound, check if it overlaps with a more frequent one: :"maching learning algorithm" -> "machine learning" "learning algorithm:
            w1, off1 = cw.checkComp(words, i+1, wToL)
            if len(w1.split()) > 1:
                if wcounts[w0] < wcounts[w1]:
                    w0 = w1
                    off = off1
                    if words[i] in wToL:
                        foundwords.append((words[i], wToL[words[i]])) #foundwords.append(wToL[words[i]])
        if len(w0): foundwords.append((" ".join(words[i:off]), w0))
        else: foundwords.append((words[i], None))
        i=off

    return foundwords

if __name__ == '__main__':
    from Config import Cfg
    cfg = Cfg()

    docs= [["Hello","world"],["Computer science","rocks"]]
    wmap={"Hello":"hello","world":"world","Computer science":"computer science","rocks":"rock"}
    print(getWCounts(docs, wmap)) # %TODO%

    #generateFiles(cfg)
    #with open(fpath + "wcounts" + fending + ".pic", "rb") as f:  woCounts=pickle.load( f)
    #for k,v in woCounts.items():        print(k,v)