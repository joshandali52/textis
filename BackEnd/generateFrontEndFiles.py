"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

import sys
sys.path.append("../")
sys.path.append("/../")
import BackEnd.jobads
import BackEnd.clusterWords
import BackEnd.coocc

if __name__ == '__main__':
    from Config import Cfg
    isDummy=False #run full
    #isDummy=True #run small scale (few docs, few words...), ie. dummy.
    print("Is small scale, dummy data?", isDummy)
    conf = Cfg(isBackendDummy=isDummy)
    BackEnd.jobads.cleanJobAds(conf) #Run with FrontEnd.Config isBackendDummy = False/True, you need to run cleanJobAds only once
    BackEnd.jobads.generateFiles(conf)
    BackEnd.coocc.generateCooccVecs(conf)
    BackEnd.clusterWords.doCluster(conf)


