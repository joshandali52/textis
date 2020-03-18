"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

# -*- coding: utf-8 -*-
import dash
import json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly.graph_objs import *
import networkx as nx
import numpy as np
import pickle
import hashlib
import re, string, nltk

from Config import * #own libs
import textTools
import FrontEnd.vis_old.toolsVisual as wtools
import FrontEnd.vis_old.topicVisual as aT

#There are 3 representationss of a word:with the same stem: 1) wmf: most frequent word form (e.g. house out of houses, House) 2) wt: transformed word (no plural word, stemmed) 3) ws: Word as given in sylabelles
#There are transformers from 1->2
#Possible improvement check if uppe case word exists or completly upper, this fixes Pyhton vs python and sql vs SQL


#load stored data
with open(dataPath+"longwordPhr"+fending+".pic", "rb") as f: longPhrases = pickle.load(f)
with open(dataPath+"biterms"+fending+".pic", "rb") as f: biterms = pickle.load(f)
with open(dataPath+"wcounts"+fending+".pic", "rb") as f: wCounts = pickle.load(f)
#with open(dataPath+"oWordMap.pic","rb") as f: oWordMap=pickle.load(f)


#global settings
initWords = [""]*maxW
unitWeights = True #use the same weight for all edges
initMap = [str(i) for i in range(maxT)]
initTop = aT.getTopTxt("")+initWords

#Overview of Webpage
app = dash.Dash()
#for icon not working from: https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648/8
#server = app.server
#@server.route('/favicon.ico')
#def favicon():
#    return flask.send_from_directory(os.path.join(server.root_path, 'static'),
#                                     'favicon.ico')
app.title = 'CUUL'
app.layout = html.Div([
    html.H2("Course Syllabus"),
    #html.Div(className='divtextA', children=dcc.Textarea(id='textA', placeholder='Enter a value...', value='supervision supervising',style={'width': '100%'})),#'Python and R is all we teach. But Big data matters, too, and also quick data queries using sql! Soft skills like communication and team work should also be taught.',style={'width': '100%'})),
    html.Div(className='divtextA', children=dcc.Textarea(id='textA',placeholder='Enter a value...',value='R SQL Python',style={'width': '100%'})),
    #----Topics Part-----
    html.H2("Topic Analysis of Job Ads"),
    html.P("Show topics and their importance/weight; Click button to compute difference in topics of syllables and Job ads; Click Topic to see some info about it"),
    html.Button(id='topJobButton', children='Sort topics by job ads relevance', n_clicks=0),
    html.Button(id='topButton', children='Sort by difference "syllables - job ads"', n_clicks=0),
    html.Div(id='butTText', children=[html.Button(id="ButT" + str(i), children=initTop[i], n_clicks=0,style={'white-space': 'normal', 'width': '200px', 'color': 'grey','fontSize': 15, 'padding': 5,'border': '0.5px solid rgba(0,0,0,0.1)', 'background': 'none'}) for i in range(maxT)]),  #
    html.Div(id='cacheB', children='tjb:0 tb:0 last:nan', style={'display': 'none'}),
    html.Div(id='Word graphsT', children=[dcc.Graph(id="gr2"), html.Br()]),
    html.Div(id='Word barT', children=[dcc.Graph(id="gr3"), html.Br(), html.P('Matching Job Ads',  style={'font-weight': 'bold', 'color': 'grey', 'fontSize': 18})]),
    #----Association Part-----
    html.H2("Association Analysis"),
    html.Button(id='sylButton', children='Show Overview', n_clicks=0),
    html.P("Find words not in sylables that are associated with it"),
    html.Div(id='butWText', children=[html.Button(id="ButW"+str(i), children=" ", n_clicks=0, style={'color': 'grey', 'fontSize': 15, 'padding': 5, 'border': 'none', 'background': 'none'}) for i in range(maxW)]), #
    html.Br(),
    html.Div(id='Word graphsW', children=[dcc.Graph(id="gr1"), html.Br(), html.P('Matching Job Ads', style={'font-weight':'bold', 'color': 'grey', 'fontSize': 18})]),#,figure=fig)
    html.Div(id='cacheW', children=[html.P(','.join(["0"]*maxW)), html.P(','.join([""]*maxW))], style={'display': 'none'}),
    html.Div(id='dummyOut', style={'display': 'none'}),
    html.Div(id='cacheT', children=[html.P(','.join(["0"] * maxT)), html.P(','.join([""] * maxT))],  style={'display': 'none'})
    #, html.Div(id='cache2',children=[html.P(','.join(initMap))], style={'display': 'none'})
])


#---------------------------------
#Associationgraph Functionality
#---------------------------------

def getSingleWordGraphs(win, currW): #get graph of a single word w
    G = nx.Graph()
    G.add_node(win) #displayed word
    tag = textTools.get_wordnet_pos(nltk.pos_tag(win)[0][1])
    wt = textTools.changeWord(win, tag) #internal reference
    wnodes = {}
    if wt in wtools.wtoi: #if the word is not part of job ads, the graph will be just one word
        ids = wtools.imat[wtools.wtoi[wt], :singleWordMaxAssociations] #get a limited number of related words
        for id, weight in zip(ids, wtools.vmat[wtools.wtoi[wt], :singleWordMaxAssociations]):
            G.add_node(wtools.itow[id])
            G.add_edge(wt, wtools.itow[id], weight=1 if unitWeights else weight)
            wnodes[wtools.itow[id]] = weight #the weight of a node is given by how much it is associated with the term
    wnodes[wt] = max(wnodes.values()) if len(wnodes) else 1 #the center word shoudl be biggest
    return wtools.getStyledGraph(G, currW, wnodes, tree=False)  #wtools.oWordMap

dummyGraph,dummyanno = getSingleWordGraphs("EmptyValue", [])

def getMultiWordsOverview(ws):
    nMatchEdges = overviewMaxMissAssociations#3*overviewMaxMissAssociations
    edges = {};  wnodes = {}
    matchwords = []
    for cw in ws:
        if cw in wtools.wtoi: matchwords.append(cw)
        elif cw.lower() in wtools.wtoi: matchwords.append(cw.lower())
        else: continue
    griddata=[]
    for w in matchwords: #add for each words strongest  missing associations
        if not w in wnodes: #add each word only once
            wnodes[w] = np.mean(wtools.vamat[wtools.wtoi[w], :nMatchEdges])
            cgrid = []
            ids = wtools.amat[wtools.wtoi[w], :]  # overviewMaxMissAssociations]
            missFound = 0
            #nEdges = 0
            # wadd=[]
            for ni, (id, weight) in enumerate(zip(ids, wtools.vamat[wtools.wtoi[w], :])):  # overviewMaxMissAssociations]):
                nodeID = wtools.itow[id]
                while(nodeID in wnodes): nodeID+=" " #a missing word has already occurred, we duplicate it here by changing its ID
                if nodeID not in matchwords and (missFound < overviewMaxMissAssociations):
                    missFound += 1
                    if wtools.itow[id] not in wtools.wtoi: wnodes[nodeID] = weight / 2
                    else: wnodes[nodeID] = np.mean(wtools.vamat[wtools.wtoi[wtools.itow[id]], :])
                    cgrid.append((nodeID if weight>0 else "NotFound", wnodes[nodeID]))
                  #  if ni==nMatchEdges//2:
                   #     cgrid.append((w, np.mean(wtools.vamat[wtools.wtoi[w], :nMatchEdges])))
                    # G.add_node(itow[id]) #duplicates are ignored by networkx #G.add_edge(w,itow[id],weight=weight)
                    eid = w + esep + nodeID  # if w<itow[id] else itow[id]+esep+w
                    edges[eid] = 1 if unitWeights else weight
                    #nEdges += 1
                    #if nEdges >= nMatchEdges: break
            while(len(cgrid)<overviewMaxMissAssociations): cgrid.append(("NotFound",0))
            cgrid.insert(overviewMaxMissAssociations // 2, ((w, np.mean(wtools.vamat[wtools.wtoi[w], :nMatchEdges]))))
            griddata.append(cgrid)
            # if w in list(matchwords)[:15]: print(w,wadd)
    allw = sorted(wnodes.items(), key=lambda x: x[1], reverse=True)
    mw = [x[0] for x in allw[:maxDrawNodes]]
    mw = set(mw).union(matchwords)
    #for w in mw: G.add_node(w)  # duplicates are ignored by networkx
    wnodes={k: v for k, v in wnodes.items() if k in mw}
    if griddata is None or len(griddata) == 0:
        global dummyGraph
        return dummyGraph
    else:
        return wtools.getGridOverviewGraphs(ws, wnodes, griddata) #wtools.oWordMap


#Analyze sylabelles -> Handle click
@app.callback(Output('butWText', 'children'), [Input('sylButton', 'n_clicks')], [State('textA', 'value')]) #,[Input('testSubmit', 'id'),Input('textA', 'value')]
def display_graphs(id, text):
    graphs = []
    global biterms
    rtext = text.replace("\n", " ").replace("\t", " ").replace("  ", " ").replace("  ", " ")
    words = textTools.docSpacePunctuation(rtext).split(" ")
    words = words+initWords
    fwords = []
    lw = words[0] if len(words) else ""
    doskip = False
    for w in words[1:]:
        bt = lw.lower() + textTools.bsep + w.lower()
        if bt  in biterms:
            fwords.append(bt)
            doskip = True
        else:
            if not doskip: fwords.append(lw)
            doskip = False
        lw = w

    currW = fwords[:maxW]
    allt = "".join(currW)
    hash_object = hashlib.md5(allt.encode()).hexdigest()
    wtools.logActivity(str(hash_object) + ","+text)
    for iw, w in enumerate(currW):
        if len(w):
            #chw, chwMap, dw = textTools.transWord(w, wtools.oWordMap)
            chw, dw = textTools.transWord(w)#, wtools.oWordMap)
            wInAds = (dw in wtools.wtoi or chw.lower() in wtools.wtoi or chw in wtools.wtoi)#chwMap.lower() in wtools.wtoi or chwMap in wtools.wtoi or
            #print(w, chw, dw, wInAds)
            ccol = 'grey' if (len(chw) == 0 and not wInAds) else ('lightgreen' if wInAds else 'red') #green if occurs, grey if stopword or so, red if not occurring
        graphs.append(html.Button(id="ButW"+str(iw), children=w, n_clicks=0, style={'font-weight': 'bold', 'color': ccol, 'fontSize': 14, 'padding': 4 if len(w) else 0, 'border': '0.5px solid rgba(0,0,0,0.1)' if len(w) else 'none', 'background': 'none'}))
    return graphs

#Analyze a word  -> Handle click on word button
@app.callback(dash.dependencies.Output('Word graphsW', 'children'), [Input('ButW'+str(i), 'n_clicks') for i in range(maxW)], [State('ButW'+str(i), 'children') for i in range(maxW)]+[State('cacheW', 'children')]) #textContent
def update_output(*args):
    global dummyGraph, wordPhrases#,biterms
    clicks = args[:maxW]
    currW = args[maxW:2*maxW]
    caChildren = args[2*maxW]
    lclicks = [int(v) for v in caChildren[0]['props']['children'].split(",")]
    savedWords = caChildren[1]['props']['children']
    found = False
    tjobads = [html.P('Matching Job Ads', style={'font-weight':'bold','color': 'grey', 'fontSize': 18})]

    def handleSingleWord(word):
        #chw, chwMap, dw = textTools.transWord(word, wtools.oWordMap)
        chw, dw = textTools.transWord(word)#, wtools.oWordMap)
        G, anno = getSingleWordGraphs(chw, currW)#(chwMap, currW)
        tit = "Associations with <b>" + dw + "</b>"
        wordBag = [chw, dw]#chwMap, dw]
        #print(chwMap, chwMap in longPhrases, dw in longPhrases, chw in longPhrases, word in longPhrases, len(longPhrases))
        matches = np.isin(wordBag, list(longPhrases.keys()))
        if np.any(matches):#if dw in wordPhrases:
            wInLong = wordBag[np.where(matches)[0][0]]
            for iad, ad in enumerate(longPhrases[wInLong]):#wordPhrases[dw]):
                # tjobads.append(html.P(str(iad)+"..."+ad+"...", style={'color': 'grey', 'fontSize': 15}))##dcc.Markdown("..."+ad+"**...**"))
                tjobads.append(dcc.Markdown(str(iad) + "  ..." + ad.replace(dw, " **_" + word + "_** ").replace(dw.title(), " **_" + dw.title() + "_** ") + "..."))  ##dcc.Markdown("..."+ad+"**...**"))
        return G, anno, tit

    if len(currW) == 1: #just 1 word
        G, anno, tit = handleSingleWord(currW[0])
        found = True
    elif savedWords == ",".join(currW):
        for i, (l1, l2) in enumerate(zip(lclicks, clicks)):
            if l1 < l2:
                G, anno, tit = handleSingleWord(currW[i])
                found = True
                break

    if not found:
        if len(currW) == 0 or (len(currW[0]) == 0 and len(currW[1]) == 0):
            G, anno = (dummyGraph, dummyanno)
        else:
            taggedtext= nltk.pos_tag([t for t in currW if len(t)>0])
            taggedtext=[(w, textTools.get_wordnet_pos(t)) for w, t in taggedtext]
            tWords = [textTools.changeWord(w, t) for w, t in taggedtext] #            tWords = [oWordMap.get(w, "") for w in tWords]
            #print("tW",tWords)
            #print("cW",currW)
            tWords = [t for t in tWords if len(t) > 0]
            res = getMultiWordsOverview(tWords)
            G, anno = (dummyGraph, dummyanno) if res is None else res
        tit = "Overview"

    height = 1000 if found else max(int(10+len(tWords)*50), 225)
    fig = Figure(data=Data([G[0], G[1]]), layout=Layout(title='<br>'+tit, annotations=anno,
                titlefont=dict(size=14), showlegend=False, hovermode='closest', height=height, margin=dict(b=20, l=5, r=5, t=20),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False), yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    allt = "".join(currW)
    hash_object = hashlib.md5(allt.encode()).hexdigest()
    wtools.logActivity(str(hash_object) + ","+tit+","+str(sum(clicks)))
    return [dcc.Graph(id="gr1", figure=fig), html.Br()]+tjobads

@app.callback(dash.dependencies.Output('cacheW','children'),[Input('Word graphsW','children'),Input('butWText', 'children')],[State('cacheW','children')]+[State('ButW'+str(i), 'n_clicks') for i in range(maxW)]+[State('ButW'+str(i), 'children') for i in range(maxW)]) #textContent
def update_output2(*args):
    caChildren = args[1]
    buttonProps = [w['props']['children'] for w in caChildren]
    savedWords = ",".join(buttonProps)
    currW = ",".join([str(c) for c in args[-maxW:]])
    clicks = args[-2*maxW:-maxW] if savedWords == currW else [0]*maxW
    return [html.P(",".join([str(c) for c in clicks])), html.P(currW)]

@app.callback(dash.dependencies.Output('dummyOut', 'children'),[dash.dependencies.Input('gr1', 'hoverData')],[State('ButW'+str(i), 'children') for i in range(maxW)])
def update_text(*args):
    hoverData=args[0]
    if hoverData is not None and "points" in hoverData:
        if len(hoverData["points"])>0 and "text" in hoverData["points"][0]:
            currW = args[1:]
            allt = "".join(currW)
            hash_object = hashlib.md5(allt.encode()).hexdigest()
            wtools.logActivity(str(hash_object) + ","+"hoverJson," + json.dumps(hoverData["points"][0]["text"][:100]))
    return [html.P("a")]


#--------------------------
#Topic functionality (could go into own file)
#---------------------------

def getAllTopicGraphs(tWords, sortByDiff=False): #Empty means get standard
    graphs = []
    topTxt = aT.getTopTxt(tWords, sortByDiff)+initWords ##chw,dw=textTools.transWord(w,wtools.oWordMap)
    for iw, w in enumerate(topTxt[:maxT]):
        #[ for i in range(len(initTop))]),
        #ccol= 'grey' if len(chw)==0 else ('lightgreen' if dw.lower() or dw in wtools.wtoi else 'red') #green if occurs, grey if stopword or so, red if not occurring
        graphs.append(html.Button(id="ButT" + str(iw), children=w, n_clicks=0, style={'white-space': 'normal', 'width': '200px', 'color': 'grey','fontSize': 15, 'padding': 5 if len(w) else 0,'border': '0.5px solid rgba(0,0,0,0.1)' if len(w) else 'none', 'background': 'none'}))
    return graphs

def display_TopicGraphs(id, text, sortbyDiff=False):
    global biterms
    fwords = []
    lines = text.split("\n")
    for l in lines:
        sentences = textTools.tokenizer.tokenize(l)
        for sen in sentences:
            #sen=sen.replace(" ")
            sen = re.sub('['+string.punctuation+']', '', sen)
            words = textTools.docSpacePunctuation(sen).split(" ") #split into tokens
            lw = words[0] if len(words) else ""
            doskip = False
            for w in words[1:]:
                bt = lw.lower() + textTools.bsep + w.lower()
                if bt in biterms:
                    fwords.append(bt)
                    doskip = True
                else:
                    if not doskip: fwords.append(lw)
                    doskip = False
                lw = w
    currW = (fwords+initWords)[:maxW]
    allt = "".join(currW)
    hash_object = hashlib.md5(allt.encode()).hexdigest()
    wtools.logActivity(str(hash_object) + ", TopicGraph,"+text)
    taggedtext = nltk.pos_tag([t for t in currW if len(t) > 0])
    taggedtext = [(w, textTools.get_wordnet_pos(t)) for w, t in taggedtext]
    tWords = [textTools.changeWord(w, t) for w, t in taggedtext]
    return getAllTopicGraphs(tWords, sortbyDiff)

#Topic Stuff Analyze sylabelles -> Handle click on analyze
@app.callback(Output('butTText', 'children'), [Input('cacheB', 'children')], [State('textA', 'value')]) #,[Input('testSubmit', 'id'),Input('textA', 'value')]
def display_diffGraphsSorted(*args):
    prev_clicks = dict([i.split(':') for i in args[0].split(' ')])
    text = args[1]

    if (prev_clicks['last'] == 'tjb'):
        return display_TopicGraphs(prev_clicks['tjb'], text, False)
    elif (prev_clicks['last'] == 'tb'):
        return display_TopicGraphs(prev_clicks['tb'], text, True)
    else:
        return display_TopicGraphs(0, text, False)

@app.callback(dash.dependencies.Output('cacheB', 'children'), [Input('topJobButton', 'n_clicks'), Input('topButton', 'n_clicks')], [State('cacheB', 'children')])
def update_Topbutton(tjb_clicks, tb_clicks, prev_clicks):
    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'
    if tjb_clicks > int(prev_clicks['tjb']):
        last_clicked = 'tjb'
    elif tb_clicks > int(prev_clicks['tb']):
        last_clicked = 'tb'

    cur_clicks = 'tjb:{} tb:{} last:{}'.format(tjb_clicks, tb_clicks, last_clicked)
    return cur_clicks

@app.callback(dash.dependencies.Output('Word graphsT','children'),[Input('ButT'+str(i), 'n_clicks') for i in range(maxT)],[State('cacheT','children')]+[State('ButT'+str(i), 'children') for i in range(maxT)]) #,State('cache2','children')
def update_Topoutput(*args):
    global dummyGraph,wordPhrases,biterms
    found = False
    caChildren = args[maxT]
    lclicks = [int(v) for v in caChildren[0]['props']['children'].split(",")]
    #orderChildren = args[maxT+1]
    #topOrder = [int(v) for v in orderChildren[0]['props']['children'].split(",")]
    for i,(l1,l2) in enumerate(zip(lclicks,args[:maxT])):
        if l1!=l2:
     #       iTo=topOrder[i]
            butT=args[maxT+1+i] #Text of button
            iTo=int(butT[1:].split(" ")[0])
            G,anno=aT.getTopicGraphs(iTo)
            tit = "Topic <b>" +str(iTo)+"</b>"
            found=True
            break
    if not found:
        G, anno = aT.getTopicGraphs(0)
        tit = "Topic <b>" + str(0) + "</b>"
    fig= Figure(data=Data([G[0],G[1]]),layout=Layout(title='<br>'+tit,annotations=anno,
                titlefont=dict(size=14), showlegend=False, hovermode='closest',height= 800,width=800,margin=dict(b=20,l=5,r=5,t=20),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False), yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    return [dcc.Graph(id="gr2",figure=fig),html.Br()]

@app.callback(dash.dependencies.Output('Word barT','children'),[Input('ButT'+str(i), 'n_clicks') for i in range(maxT)],[State('cacheT','children')]+[State('ButT'+str(i), 'children') for i in range(maxT)]) #,State('cache2','children')
def update_Topoutput3(*args):
    global dummyGraph,wordPhrases,biterms
    found = False
    caChildren = args[maxT]
    lclicks = [int(v) for v in caChildren[0]['props']['children'].split(",")]
    #orderChildren = args[maxT+1]
    #topOrder = [int(v) for v in orderChildren[0]['props']['children'].split(",")]
    for i,(l1,l2) in enumerate(zip(lclicks,args[:maxT])):
        if l1!=l2:
     #       iTo=topOrder[i]
            butT=args[maxT+1+i] #Text of button
            iTo=int(butT[1:].split(" ")[0])
            B = aT.getTopicBar(iTo)
            tit = "Topic <b>" +str(iTo)+"</b>"
            found=True
            break
    if not found:
        B = aT.getTopicBar(0)
        tit = "Topic <b>" + str(0) + "</b>"
    fig= Figure(data=[B],layout=Layout(title='<br>'+tit,
                titlefont=dict(size=14), showlegend=False, hovermode='closest', height= 400,width=800,margin=dict(b=20,l=100,r=20,t=50),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=True), yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=True)))
    return [dcc.Graph(id="gr3",figure=fig),html.Br()]

@app.callback(dash.dependencies.Output('cacheT','children'),[Input('Word graphsT','children'),Input('butTText', 'children')],[State('cacheT','children')]+[State('ButT'+str(i), 'n_clicks') for i in range(maxT)]) #textContent
def update_Topoutput2(*args):
    caChildren=args[1]
    buttonProps=[w['props']['children'] for w in caChildren]
#    savedWords=",".join(buttonProps)
    clicks = args[-maxT:]
    return [html.P(",".join([str(c) for c in clicks]))]

if __name__ == '__main__':
    app.run_server(debug=True)