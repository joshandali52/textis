import sys
sys.path.append('../')
from Config import  Cfg
import pickle as pl
import numpy as np
doPrint=False
#useDummyData=True
useDummyData=False
print("Use dummy data?",useDummyData)
Conf=Cfg(useDummyData)

def getAllFilenames():
    #print(get_book_variable_module_name("benchConfig"))
    items=[(item,getattr(Conf, item)) for item in dir(Conf) if not item.startswith("__") and item.endswith("name")]
    return items


fnames=getAllFilenames()
#print("All Files generated from Backend",fnames)
path = Conf.fpath
paths = [Conf.rpath + 'results/resultsjobads18plus19_curr/', Conf.rpath + 'results/resultsjobads2013_curr/']

def printDict(path, rawName,samples=5):
    fname=path+rawName+Conf.fending+".pic"
    with open(fname,"rb") as f:
        data=pl.load(f)
        if doPrint: print("\n", fname, len(data), type(data))
        if isinstance(data,dict):
            for k in list(data.keys())[:samples]:
                #print(data[k])
                kdat= [l[:samples*4]+"..." for l in data[k][:samples]] if isinstance(data[k], list) else data[k]
                if doPrint: print("  ", k, ": ", kdat)
        else:
            for k in data[:samples]: print("  ", k)
        return data


coitow=printDict(path, Conf.coiTowname)
assTreeWin=printDict(path, Conf.asstreename+"_win",samples=0) # not in 2013
assAbsTreeWin=printDict(path, Conf.assAbstreename+"_win",samples=0)  # not in 2013
assTreeDoc=printDict(path, Conf.asstreename+"_doc",samples=0)  # not in 2013
assAbsTreeDoc=printDict(path, Conf.assAbstreename+"_doc",samples=0)  # not in 2013
wToL=printDict(path, Conf.wToLemmaname)
# globDat=printDict(path, Conf.globalDat,samples=0)
# nDocs=globDat['nUsedDocs']





printDict(path, Conf.iTowname)
wcounts=printDict(path, Conf.wcountsname)
perAd=printDict(path, Conf.perAdOccname)
compwords=printDict(path, Conf.compoundsname)


phrl=printDict(path, Conf.longwordPhrname,samples=0)
#phrlDoc=printDict(Conf.longwordPhrDocsname,samples=0)
assDictWin=printDict(path, Conf.assSurname+"_win", samples=0) # not in 2013
assAbsDictWin=printDict(path, Conf.assAbsname+"_win",samples=0) # not in 2013
assDictDoc=printDict(path, Conf.assSurname+"_doc", samples=0) # not in 2013
assAbsDictDoc=printDict(path, Conf.assAbsname+"_doc",samples=0) # not in 2013
clToRaw=printDict(path, Conf.cleanToRaw,samples=0)
print(clToRaw.keys())


text="Python, R and machine learning algorithms#is what is taught in the data mining course."# Big data and visualization are also a topic. Data skills matter. Communication and text mining."
import BackEnd.jobads
print("Raw Words in job ads",BackEnd.jobads.getTerms(text,wcounts,wToL))
print(wcounts)
def showAll(word):
    print("\n\n",word)
    if not word in wToL:
        print("No Info found")
        return
    lem=wToL[word]
    print("   lem",lem)
    print("   Count",wcounts[lem])
    print("   perAd",perAd[lem])
    print("   compounds", compwords[lem])
    showAssociations(word, wToL, coitow,  assDictWin,perAd)
    for phr in phrl[lem][:5]:
        jobid=phr[0]
        phraseText=phr[1]
        print("   Ad-Phrase: ",phraseText, "JobID",jobid)
    print("  ShowFullAd for Ad-Phrase")
    for phr in phrl[lem][:5]:
        jobID=phr[0]
        print("  Fullad Name Path",jobID, " AdText",clToRaw[jobID].replace("\n", "  ")[:150] if jobID in clToRaw else "ID not found")
        #with open(jobID,"r") as f:
        #    dat=f.read()
        #    print("   Full AdText", dat[:200].replace("\n","  "))

doPrint=True
#for w in foundwords: showAll(w) #Show info for each found word


def showAssociations(word, wToL, coitow, assDict, perAd, samples=500):
    wtoi = {k:i for i,k in coitow.items()}
    k=wtoi[wToL[word]] if wToL[word] in wtoi else ""
    if k=="":
        if doPrint: print("  Not found/frequent", word, wToL[word])#, w in wtoi)
        return
    wDict=assDict[k]
    #print("min(samples,len(wDict[ass]))", samples, len(wDict[ass]))
    for ass in wDict:
        wass=wDict[ass]
        data=[coitow[wass[j][0]] + ", Ass:" + str(np.round(wass[j][1], 6)) + ", Freq:" + str(np.round(perAd[coitow[wass[j][0]]], 3)) for j in range(min(samples, len(wass)))]
        #if len(data):
        if doPrint: print( word, " Co-occ:", ass, ":", " ; ".join(data))


def getAssociationsAll(word, wToL, coitow, assDict, samples=15):
    wtoi = {k:i for i,k in coitow.items()}
    k=wtoi[wToL[word]] if wToL[word] in wtoi else ""
    if k=="":
        if doPrint: print("  Not found/frequent", word, wToL[word])
        return []
    allAss=sum([v for v in assDict[k].values()],[])
    allAss.sort(key=lambda x: x[1])
    return allAss


def compare(word,word2):
    print("\n\nCompare: ", word,word2)
    if (not word in wToL) or (not word2 in wToL):
        print("No Info found")
        return
    lem = wToL[word]
    lem2 = wToL[word2]
    print("lem", lem,lem2)
    print("Count", wcounts[lem],wcounts[lem2])
    print("perAd", perAd[lem], perAd[lem2])
    print("compounds", compwords[lem], compwords[lem2])
    def showAss(word, wToL, coitow, assDict):
        ass=getAssociationsAll(word, wToL, coitow, assDict)
        dass = {x[0]: x[1] for x in ass}
        ass1 = getAssociationsAll(word2, wToL, coitow, assDict)
        dass1 = {x[0]: x[1] for x in ass1}
        bars=[{"word":coitow[x[0]],"val":x[1],"otherval":dass1[x[0]] if x[0] in dass1 else 0} for x in ass]
        bars2=[{"word":coitow[x[0]],"val":x[1],"otherval":dass[x[0]] if x[0] in dass else 0} for x in ass1]
        print("word",word,bars)
        print("word",word2,bars2)
    print("Surprise")
    showAss(word, wToL, coitow, assDictWin)
    #print("Absolute") #showAss(word, wToL, coitow, assAbsDict)



def showAssTree(word,assTree,dist):
    print("\nTree for word: ",word,"  dist",dist)
    if word in wToL:
        lem = wToL[word]
        if lem in assTree:
            #print(assTree[lem],assTree[lem]["children"]) #(Recursive) Tree structure node and list of children (children are nodes themselves)
            print(assTree[lem], str(assTree[lem]["children"]).replace("'name'","").replace("'children'",""))  # (Recursive) Tree structure node and list of children (children are nodes themselves)
        else:
            print("not found in treedict",lem)
    else: print("not found in wToL",word)

#testwords= ["Python","machine learning","communication","data science","Scala"]
#testwords= ["work","relate","data"]
testwords= ["machine learning","big data","data"]

#Tests
for w in testwords: showAll(w)
for w in testwords: compare(w,"R")
for w in testwords: showAssTree(w,assAbsTreeWin,"Absolute - Win")
for w in testwords: showAssTree(w,assTreeWin,"Surprise - Win")
for w in testwords: showAssTree(w,assAbsTreeDoc,"Absolute - Doc")
for w in testwords: showAssTree(w,assTreeDoc,"Surprise - Doc")



