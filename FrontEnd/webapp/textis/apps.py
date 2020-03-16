import os

import numpy as np
from django.apps import AppConfig

# relative project path must be set in pythonpath
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))


import Config as Conf
import pickle as pl

useDummyData=True
#useDummyData=False
Conf = Conf.Cfg(useDummyData)

compwords = dict()
wToL = dict()
longPhrases = dict()
wordOcc = dict()
association = dict()
wordCounts = dict()
wordToIndex = dict()

class TextisConfig(AppConfig):
    name = 'textis'



#######################################################
# init global data structures
#######################################################

def printDict(rawName, samples=5):
    fname = Conf.fpath + rawName + Conf.fending + ".pic"
    with open(fname, "rb") as f:
        data = pl.load(f)
        return data


printDict(Conf.iTowname)
wToL = printDict(Conf.wToLemmaname)
coitow=printDict(Conf.coiTowname)
printDict(Conf.wcountsname)
wordOcc = printDict(Conf.perAdOccname)
compwords = printDict(Conf.compoundsname)

wordCounts=printDict(Conf.wcountsname)

coitow = printDict(Conf.coiTowname)
wordToIndex = {k:i for i,k in coitow.items()}
longPhrases = printDict(Conf.longwordPhrname)

assTreeWin=printDict(Conf.asstreename+"_win",samples=0)
assAbsTreeWin=printDict(Conf.assAbstreename+"_win",samples=0)
assTreeDoc=printDict(Conf.asstreename+"_doc",samples=0)
assAbsTreeDoc=printDict(Conf.assAbstreename+"_doc",samples=0)

association=printDict(Conf.assSurname+"_win", samples=0)
assTree=printDict(Conf.asstreename+"_win",samples=0)