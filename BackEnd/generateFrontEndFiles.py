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


