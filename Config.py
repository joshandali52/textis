"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : Academic Free License ("AFL") v. 3.0

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

import multiprocessing as mp

class Cfg:
   def __init__(self, isBackendDummy = True):
    #self.isLocal = mp.cpu_count()<9
    #parameters FrontEnd
    self.assWords=5 #number of words to left and right in hoverdata
    #assThres=0.00002
    #singleWordMaxAssociations = 20 #number of words per matching word

    self.esep="___"
    self.nsep="***"
    self.maxT =100 #maximum allowed topics
    self.wPerTopic =30 #words per topic

    #For words, a context is extracted giving more meaning, ie. "Python" -> Job Ad1: "Applicants need Python programming skills", Job Ad2: "C++,Java,Python,C# should be mastered"
    self.longphrwid = 10 #number of words per context
    self.longMaxPhrPerWord = 200 #max contexts per word

    #self.dataPath = "/Users/michaelgau/Documents/workspace/textis/data/"  if self.isLocal else "../../data/"#on server check: /mnt/data3/currData/
    self.dataPath = "../../data/"

    #parameters BackEnd
    #self.rpath = "C:/Users/jschneid/MYDATA/Liecht/Various/ErasmusPlus/data/" if self.isLocal else "/mnt/data2/public/jobads/" #"/mnt/data3/public/currData/"
    self.rpath = "../data/"

    #create only small files, this is fast for debugging
    self.isBackendDummy = isBackendDummy
    self.fpath = self.rpath + "results/website/"
    self.fpath += "allData/" if not self.isBackendDummy else "dummyData/"
    self.fending = "_dummy" if self.isBackendDummy else ""
    self.nDoc=15000 if not self.isBackendDummy else 20
    self.nWords = 8000 if not self.isBackendDummy else 200 #number of words with co-occ data
    self.minCompoundCount = 20 if not self.isBackendDummy else 200
    self.minOcc = 10 #minimum number of times a word must occur - otherwise ignored
    self.maxWordsCoocc = 500 if not self.isBackendDummy else 30 #maximum number of words in a job ad so that compute all pairwise co-occ
    self.overviewMaxMissAssociations = 140 if not self.isBackendDummy else 40 #number of associations shown
    self.nProc=7
    self.terms=[] #restrict to certain search terms
    self.rawPaths=[self.rpath+"raw/"] #,self.rpath+"original_text_without_duplicates/"
    #rawPaths=[fpath+"original_text_without_duplicates/"]
    self.cleanedPath="cleanedAll" + self.fending + "/"

    self.remName="allDoc"

    #Data about isolated words
    self.iTowname = "iTow" #mapping of index to words for documents
    self.wToLemmaname="wordToLemma" #word to lemma map, e.g. houses to house
    self.wcountsname="wcounts" #counts of lemmatized words
    self.perAdOccname = "perAdOcc" #occurrences of a word per ad (normalized), ie. in [0,1]
    self.compoundsname="compounds" #compound words, e.g. business intelligence, data science, machine learning,
    self.assSurname= "ass" #Visualized using: http://bl.ocks.org/d3noob/8375092 ; https://gist.github.com/mdml/7537455
    self.assAbsname="assAbs"
    self.asstreename= "asstree"
    self.assAbstreename= "assAbstree"
    self.cooccVecs= "coen" #co-occurrence vector for a word
    self.cleanToRaw="clToRaw"

    self.globalDat="globDat" #sum overall info, eg. #docs

    #Stanford Dependency Parser (needed to get compounds), see https://github.com/Lynten/stanford-corenlp
    self.parserPath = r'C:/apps/anaconda3/Lib/site-packages/stanfordcorenlp/'

    #cooccurrence data
    self.coiTowname = "coiTow" #mapping index to word  for co-occurrence data, e.g. coiTowname[0]="data" meaning that value 0 is mapped to "data"
    self.agname = "agraph" #word association data as matrix, weight given by PMI row index or matrix value to word stored in file coiTowname, e.g coiTowname[0]="data" meaning that value 0 is mapped to "data"
                      #a row consists of 3 parts of equal size,e.g [0,2,9,5,6,7] is logically[0,2],[9,5],[6,7], each part stores the indexes of words with strongest associations among the most frequent words (part 1), the not so frequent words (part 2) and the rare words; decreasing order
                      #example with words instead of indeces: row with "Python" [excellent,job,R,machine_learning,matplotlib,scipy] => [excellent,skills] these words are very common and often occcur together with Python, [R,machine_learning] less common and often cooccur ...
    self.vagname = "vagraph" #values of word association data as matrix, giving strength of association
    #igname = "igraph" #words associated with a word computed using frequency of occurrence * inv freq of words; rest as for a grpah but there is only a single part, ie. one list of words per row
    #vgname = "vgraph"

    #Phrases
    self.longwordPhrname="longwordPhr" #long word phrases, Phrases, ie. a word and its context, e.g. for "data"   get sth like "I like data science a lot", "Data augmentation is important"
    self.longwordPhrDocsname="longwordPhrDocs" #Docs that contain extracted phrase
    #wordPhrname="wordPhr" #(short) word phrases, Phrases, ie. a word and its context, e.g. for "data"   get sth like "I like data science a lot", "Data augmentation is important"


