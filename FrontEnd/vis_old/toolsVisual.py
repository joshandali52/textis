from plotly.graph_objs import *
import networkx as nx
import numpy as np
import textTools
from Config import *
import pickle
from time import gmtime, strftime
import nltk

#imat, vmat, itow,amat,vamat = coocc.loadgraphDat()

with open(dataPath+"peradOcc"+fendingF+".pic", "rb") as f: perAdOcc=pickle.load(f)


with open(fpath+coiTowname,"rb") as f: coitow=pickle.load(f)
cowtoi = {i: w for w, i in coitow.items()}

imat=np.load(fpath+igname+fending+".npy")
amat = np.load(fpath + agname + fending + ".npy")
vamat = np.load(fpath + vagname + fending + ".npy")
vmat = np.load(fpath + vgname+fending+".npy")


with open(dataPath+"wordPhr"+fendingF+".pic", "rb") as f:  wordPhrases = pickle.load(f)
logfile = dataPath+"serverLog_"+strftime("%Y_%m_%d__%H_%M_%S", gmtime()) + ".txt"
#with open(dataPath+"oWordMap"+fendingF+".pic", "rb") as f: oWordMap = pickle.load(f)

def logActivity(logtxt):
    t=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    try:
        with open(logfile, "a+") as f:
            f.write(t+","+logtxt+"\n")
    except IOError:
        print("Could not read file!")

rawhoverData={dw: "<br>".join(["..." + ad.replace(dw, "<i><b>" + dw + "</b></i>").replace(dw.title(), "<i><b>" + dw.title() + "</b></i>")+ "..." for iad, ad in enumerate(v) if iad<10]) for dw,v in wordPhrases.items()}
hoverData={}
for dw in rawhoverData:
    ow = textTools.convertWord(dw) #oWordMap[dw] if dw in oWordMap else dw
    normvmat=vmat[wtoi[dw], : ]/(1e-10+np.sum(vmat[wtoi[dw], :])) if dw in wtoi else ""
    wf=  list(zip(imat[wtoi[dw], :],normvmat))[:assWords] if dw in wtoi else [] #[(dw,wCounts[dw])]+
    wfmap = [(textTools.convertWord(w), y) if isinstance(w, str) else (textTools.convertWord(itow[w]),y) for w,y in wf]
    hstr=ow +" occurs "+str(perad[dw] if dw in perad else "--")+" times on average per ad"
    hoverData[dw]=hstr+"</br>Associated[%]: " +  ", ".join([(dw if isinstance(dw, str) else itow[dw]) +":"+str(np.round(nu*100,1)) for dw,nu in wfmap]) +"<br>Job Ads:<br>"+rawhoverData[dw]


#Given a raw graph of nodes and edges create a nice looking graph for output in dash, ie. set colors of nodes, size etc.
def getStyledGraph(Gc, currW, wnodes=None, nocolor=False, tree=False):  #oWordMap
    #pos = nx.spring_layout(Gc)
    pos = nx.nx_pydot.graphviz_layout(Gc, prog='twopi') #good for trees no intersection of lines
    colorsForThresholds = []; symbolForThresholds = []
    symbolsizes = []; textsizes = []
    edge_trace = Scatter(x=[], y=[], line=Line(width=0.25, color='rgba(0,0,0,0.2)'), hoverinfo='none', mode='lines')  # color='#888'
    node_trace = Scatter(x=[], y=[], text=[], mode='markers', textposition='top', hoverinfo='text', marker={"opacity": 0.8, "color": colorsForThresholds, "symbol": symbolForThresholds, "size": symbolsizes, "colorscale": 'Greens'},textfont={"color": colorsForThresholds, "size": textsizes})
    for edge in Gc.edges():
        x0, y0 = pos[edge[0]]; x1, y1 = pos[edge[1]]
        edge_trace['x'] += [x0, x1, None]; edge_trace['y'] += [y0, y1, None]
    maxCircleSize = 30 #maxSize of circle
    minCircleSize = 10
    maxTextSize = 16 #max text Size
    minTextSize = 16
    treeNodeSizeCoeff = 5 if tree else 1
    global hoverData
    labels=[]
    mval = max([1] + list(wnodes.values())) # need the +[0] in case wnodes is empty
    taggedtext = nltk.pos_tag([t for t in currW if len(t) > 0])
    taggedtext = [(w, textTools.get_wordnet_pos(t)) for w, t in taggedtext]
    tWords = [textTools.changeWord(w, t) for w, t in taggedtext]  # tWords = [oWordMap.get(w, "") for w in tWords]
    changedW = [t for t in tWords if len(t) > 0]
    #changedW=[oWordMap.get(textTools.changeWord(w),"") for w in currW] #get representation of a word
    tcurrW = set(changedW)-set([""])
    for i, node in enumerate(Gc.nodes()):
        x, y = pos[node]
        node_trace['x'].append(x);  node_trace['y'].append(y)
        nodeNormedWeight = np.sqrt(wnodes.get(node, 0) * 1.0 / mval) #normalize node weights in [0,1]
        nodeNormedWeight += 0.15 if node in currW else 0  # nodes that occur should be better visible
        symbolsizes.append(minCircleSize + (maxCircleSize * nodeNormedWeight * treeNodeSizeCoeff))  ; textsizes.append((minTextSize + maxTextSize * nodeNormedWeight)/2)
        symbolForThresholds.append(0) #not used
        copaque = 0.15 if tree else 0.2# + nodeNormedWeight / 3 #opaque setting
        rawName = node.split(nsep)[0]  #might have sth appended
        #nodeName = oWordMap.get(rawName,rawName)
        nodeName = textTools.convertWord(rawName)
        #print("occ",rawName,nodeName,nodeName in tcurrW,nodeName.lower() in currW, currW, tcurrW)
        if nocolor: textCol= 'rgba(50,50,50,' + str(0.5) + ')' #GREY
        else: textCol= 'rgba(0,180,0,' + str(0.5) + ')' if nodeName in tcurrW or (nodeName.lower() in currW) else 'rgba(180,0,0,' + str(0.5) + ')'
        colorsForThresholds.append(textCol)  # ('green' if node in words else 'red')
        #node_trace['text'].append(hoverData[textTools.changeWord(node)] if textTools.changeWord(node) in hoverData else node)
        node_trace['text'].append(hoverData[rawName] if rawName in hoverData else rawName)
        labels.append(nodeName)
    anno = [dict(x=xpos,y=ypos,xref="x",yref="y",text=lab,showarrow=True,arrowhead=0,arrowsize=0,arrowwidth=0,ax=0,ay=-ts*2,font=dict(size=ts*2,color=c)) for xpos,ypos,lab,ts,ls,c in zip(node_trace['x'],node_trace['y'],labels,textsizes,symbolsizes,colorsForThresholds)]
    return (node_trace, edge_trace),anno


#create grid graph for assocations of words
def getGridOverviewGraphs(greenw, wnodes, grid):  #oWordMap
        grid = list(reversed(grid))
        nCols = max([len(x) for x in grid])
        G = nx.grid_2d_graph(len(grid), nCols)
        G = nx.convert_node_labels_to_integers(G, ordering='sorted')
        pos = {k: ((i % nCols)/2, i // nCols / 4) for i, k in enumerate(G.nodes())}
        colorsForThresholds = []; symbolForThresholds = []
        sizes = [];        tsizes = []
        edge_trace = Scatter(x=[], y=[], line=Line(width=0.5, color='rgba(0,0,0,0.2)'), hoverinfo='none', mode='lines')  # color='#888'
        node_trace = Scatter(x=[], y=[], text=[], mode='markers', textposition='top', hoverinfo='text',
                             marker={"opacity": 0.8, "color": colorsForThresholds, "symbol": symbolForThresholds,"size": sizes, "colorscale": 'Greens'},
                             textfont={"color": colorsForThresholds, "size": tsizes})
        for i in range(len(grid)):
            for j in range(len(grid[i])-1):
                x0, y0 = pos[i*nCols+j];
                x1, y1 = pos[i*nCols+j+1]
                edge_trace['x'] += [x0, x1, None];
                edge_trace['y'] += [y0, y1, None]
        for i in range(len(grid)-1):
            x0, y0 = pos[i * nCols];
            x1, y1 = pos[(i+1) * nCols]
            edge_trace['x'] += [x0, x1, None];
            edge_trace['y'] += [y0, y1, None]
        msize = 24  # maxSize of circle
        mtsize = 10  # minSize of circle
        global hoverData
        labels = []
        mval = max([1] + list(wnodes.values()))  # need the +[0] in case wnodes is empty
        currW = greenw
        taggedtext = nltk.pos_tag([t for t in currW if len(t) > 0])
        taggedtext = [(w, textTools.get_wordnet_pos(t)) for w, t in taggedtext]
        tWords = [textTools.changeWord(w, t) for w, t in taggedtext]  # tWords = [oWordMap.get(w, "") for w in tWords]
        changedW = [t for t in tWords if len(t) > 0]
        #changedW = [oWordMap.get(textTools.changeWord(w), "") for w in currW]  # get representation of a word
        tcurrW = set(changedW) - set([""])
        toMatch = currW + [w for w in tcurrW]
        wnodes["NotSetNode"] = 0
        for i, nodeID in enumerate(G.nodes()):
            #nodeID=nodeID.strip() #there might be trailing spaces, this is because we might have duplicates nodes that should have a different id which is done by adding spaces
            x, y = pos[nodeID]
            node_trace['x'].append(x);
            node_trace['y'].append(y)
            cnode = grid[i//nCols]
         #   if len(cnode) > i % nCols - 1:
          #      print("out",len(cnode),i,nCols,i%nCols)
           #     print(len(cnode[i%nCols]),[cnode[i%nCols]])
            node = cnode[i%nCols][0] if len(cnode) > i%nCols -1 else "NotSetNode"
            noderel = np.sqrt(wnodes.get(node, 0) * 1.0 / mval)
            noderel += 0.15 if node in currW else 0  # nodes that occur should be better visible
            sizes.append(6 + msize * noderel);
            tsizes.append((24 + mtsize * noderel) / 2)
            symbolForThresholds.append(0)
            copaque = 0.5 + noderel / 3
            rawName = node.split(nsep)[0].strip(' ')  # might have sth appended
            #nodeName = oWordMap.get(rawName, rawName)
            nodeName = textTools.convertWord(rawName)
            wordBag = [rawName, rawName.lower(), nodeName, nodeName.lower()]
            #print("occ", rawName, nodeName, nodeName in tcurrW, nodeName.lower() in currW, currW, tcurrW)
            textcol= 'rgba(0,180,0,' + str(copaque) + ')' if np.any(np.isin(wordBag, toMatch)) else 'rgba(180,0,0,' + str(copaque) + ')'
            colorsForThresholds.append(textcol)  # ('green' if node in words else 'red')
            # node_trace['text'].append(hoverData[textTools.changeWord(node)] if textTools.changeWord(node) in hoverData else node)
            node_trace['text'].append(hoverData[rawName] if rawName in hoverData else rawName)
            labels.append(nodeName)
        anno = [dict(x=xpos, y=ypos, xref="x", yref="y", text=lab, showarrow=True, arrowhead=0, arrowsize=0, arrowwidth=0,
                 ax=0, ay=-(ts+1) * 2, font=dict(size=ts * 2, color=c)) for xpos, ypos, lab, ts, ls, c in
            zip(node_trace['x'], node_trace['y'], labels, tsizes, sizes, colorsForThresholds)]
        return (node_trace, edge_trace), anno


#get tree like graph of words, e.g. for topic words
def getFullGraphs(greenw,edges,wnodes,unitWeights=False,nocolor=False): #oWordMap
        G = nx.Graph()
        for w in wnodes: G.add_node(w)
        for e in edges: #add all edges, use sum of both weights
            weight=edges[e]
            if weight==0: continue
            nodes = e.split(esep)
            eid2=nodes[1]+esep+nodes[0]
            if eid2 in edges:
                weight+=edges[eid2]
                edges[eid2]=0
            edges[e]=0
            #G.add_edge(oWordMap.get(nodes[0],nodes[0]), oWordMap.get(nodes[1],nodes[1]), weight=weight)
            G.add_edge(nodes[0], nodes[1], weight=1 if unitWeights else weight)
        #keep large graph components
        #Gcomp= sorted(, key=len,reverse=True)
        Gcomp = sorted(nx.connected_component_subgraphs(G), key=len,reverse=True)
        if not len(Gcomp): return None
        Gc=Gcomp[0]
        Gc = nx.maximum_spanning_tree(Gc)
        if len(Gcomp)>1:
            for g in Gcomp[1:4]:
                if len(g)>0.1*len(Gcomp[0]) and len(g)>10: Gc= nx.compose(Gc,nx.maximum_spanning_tree(g)) #keep graph if at least 10% of largest component
        return getStyledGraph(Gc, greenw, wnodes,nocolor=nocolor, tree=True) #oWordMap