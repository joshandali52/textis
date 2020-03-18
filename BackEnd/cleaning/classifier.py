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
import re
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold, GridSearchCV
from sklearn.metrics import accuracy_score, roc_auc_score
import pickle
import os



def parseAnnotated(doc):
    
    """
    Parses annotated documents to extract labels for document segments.

    :param doc: List of documents (String)

    :returns: List of parsed documents. Each parsed document is a list of tuples containing document segment and its label
    """
	
    header = '<newad>'
    tags = ['code', 'coof', 'jode', 'jores', 'joreq', 'eqop', 'otir', 'tit', 'unc']
    res, jobad, tag, par = [], [], '', ''

    fh = open(file=doc, encoding='utf-8')
    i = 0
    for line in fh:
        #if i == 2: break
        if len(line) == 0: continue

        if header in line:
            i += 1
            if jobad: res.append(jobad)  # append job ad to result
            jobad = []  # reset job ad container
            tag = ''  # reset leftover tag
            continue

        if line[0] == '<':
            if len(par) > 0: jobad.append((par, tag))
            par = ''  # reset paragraph
            tag = [s.strip('>') for s in line.split('<')][-1]
        elif len(line)<2:
            if len(par) > 0: jobad.append((par, tag))
            par = ''  # reset paragraph
        else:
            par = par + '\n' + line

    fh.close()
    res.append(jobad)  # append last jobad
	
    return res
	

def runTrial(tarStr, docs, fname):
    
    """
    Creates tf-idf matrix for the input document.
    Trains classifiers (Random Forest and/or Multinomial Naive Bayes) for document segments.
    Stores matrix of token counts, tf-idf matrix, label encoder, and classifier object into a file.

    :param tarStr: List of labels of document segments
    :param docs: List of document segments (String)
    :param fname: filename to store results

    Example
    Input:
    docs = ["MS or PhD in quantitative field of study (mathematics, physical or biological sciences, data science etc.) from an accredited institution", "The Senior Data Engineer will work with the Regulatory Affairs", "department to deliver forecasting models to support rate case fil", "company to create forecasting models to support rate case fil", "The Director of Data Science will lead the Data Science area within this premium cable channel's Data Science & Analytics Department."]
    tarstr = ["joreq", "joreq","jode","jode","jode"]
    fname = 'example'

    Output:
    "training 0.0 2  test 0.0 5"
    """

    #Prepare data -> encode using tfidf
    enc = LabelEncoder()
    tar = enc.fit(tarStr).transform(tarStr)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(docs) #term-doc : senior:1, the: 2
    print(X_train_counts.shape)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts) #tf-idf: senior: 1, the: 0.03

    #Compare classifiers
    mnb = MultinomialNB(alpha=0.15) #.fit(X_train_tfidf, tar)
    rfc = RandomForestClassifier(n_estimators=200, random_state=42)
    models = [rfc] #,mnb]



#    for m in models:
#        scores = cross_val_score(m, X_train_tfidf, tar, cv=20)
#        print('{} me: {}, std: {}'.format(str(m)[:15], np.mean(scores), np.std(scores)))

    #Run classifiers using prob estimates

    kf = KFold(n_splits=3)
    X = X_train_tfidf; y = tar
    thres = 0.8

    for m in models:
        tok = 0
        tsc = 0
        ntok = 0
        ntsc = 0
        for train_index, test_index in kf.split(X_train_tfidf):
        #print("TRAIN:", train_index, "TEST:", test_index)
           X_train, X_test = X[train_index], X[test_index]
           y_train, y_test = y[train_index], y[test_index]
           m.fit(X_train, y_train)
           pred = m.predict_proba(X_test)
           ok = 0
           sc = 0
           for i, (est, cor) in enumerate(zip(pred, y_test)):
               if np.max(est) > thres:
                   cl = np.argmax(est)
                   #print(cl,cor)
                   ok += int(cl == cor)
                   sc += 1
           acc = accuracy_score(m.predict(X_test), y_test)
           print(str(m)[:10], np.round(ok/sc, 2) if sc > 0 else -1, np.round(acc, 2), sc)
           print(str(m)[:10], classification_report(y_test, m.predict(X_test), target_names=enc.classes_))
           tok += ok
           tsc += sc
           ntok += acc*len(y_test)
           ntsc += len(y_test)
           #store full model
           m.fit(X, y)
           pickle.dump([count_vect, tfidf_transformer, enc, m], open(fname+str(m)[:3]+".pic", 'wb'))
        print("training", np.round(tok/tsc,2) if tsc > 0 else -1, tsc, " test", np.round(ntok/ntsc, 2), ntsc)


def getClassifier(retrain=False):
    if retrain or not os.path.exists("cleaning/irrelevantClassifier_Ran.pic"): #Train and store classifier
        text = 'classifier_TrainAndTestData.txt'
        parsed = parseAnnotated(text)
        docs, tarStr = [], []
        toRemove = ['\xa0', '>']
        check = True

        for jobad in parsed:
            for s, tag in jobad:
                for s_ in toRemove:
                    tag = tag.replace(s_, '')
                tag = tag.strip()
                # clen=str(int(np.log10(np.sum([len(k) for k in s])+1)/np.log10(5)))
                # docs.append(clen+" "+clen+" \n" +s) #(1571, 4605)

                if len(s) < 4: continue
                if "Monster" in s[:15]: continue
                if "Newspaper logo is conditionally" in s: continue
                if "Skip to main content" in s: continue
                if "About the Job" in s: continue
                s = re.sub(r'([^\s\w]|_)+', '', s).lower()
                docs.append(s)  # .replace("\n"," <RET> "))
                # print(docs[-1])
                tarStr.append(tag)
        from collections import Counter
        print(Counter(tarStr))
        newTar = ["excl" if k == "otir" or k == "unc" or k == "eqop" or k == "code" else "incl" for k in tarStr]
        runTrial(newTar, docs, "inexclassifier_")
        fdat = [(t, d) for t, d in zip(tarStr, docs) if not (t == "otir" or t == "unc" or t == "eqop" or t == "code")]
        runTrial([t for t, _ in fdat], [d for _, d in fdat], "restclassifier_")

    with open("cleaning/irrelevantClassifier_Ran.pic", "rb") as f: #load classifier
        [count_vect, tfidf_transformer, enc, m] = pickle.load(f)
    return count_vect, tfidf_transformer, enc, m

if __name__ == '__main__':
    getClassifier(retrain=True)