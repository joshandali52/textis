"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : Academic Free License ("AFL") v. 3.0

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

# Python libs
import re, string

# 3rd Party libs
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader import wordnet
#from stemming.porter2 import stem
import nltk.data
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet") #used for lemmatization in case Stanfordparser not installed
lem = WordNetLemmatizer()

stemmMap = {'ADJ':'a', 'ADJ_SAT':'a', 'ADV':'r', 'NOUN':'n', 'VERB':'v'}
stemmer = WordNetLemmatizer()

engStop = stopwords.words('english')
setStopWords = set(engStop+["also"])


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

rep = {"-":" ", "_":" ", ".": " ", "!": " ", "?":" ", ")":" ", "(":" ", ",":" ", ";":" ", ":":" ", "`":" ", "'":" ", '"':" ", "\t":" "} # define desired replacements
rep = dict((re.escape(k), v) for k, v in rep.items())
pattern = re.compile("|".join(rep.keys()))

repSpace = {k:k+" " for k in rep}
repSpace = dict((re.escape(k), v) for k, v in repSpace.items())
patternSpace = re.compile("|".join(repSpace.keys()))

alphaNumericpattern = re.compile(r'[^a-zA-Z0-9_ +]+')
bsep="_"

#Functions to replace multiple identical chars, ie. spaces, line endings and tabs, with a single occurrence
def toSingleSpace(text): return re.sub(' +', ' ', text)
def toSingleLine(text): return re.sub('\n\n+', '\n\n', text)
def removeTabs(text): return re.sub('\t+', ' \n', text)


toWordNet = {'J': wordnet.ADJ, 'V':wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}
def get_wordnet_pos(treebank_tag):

    """
    Gets word-type from wordnet.

    :param treebank_tag: Part-of-speech tag

    :returns: Word-type from wordnet
    """

    firstChar = treebank_tag[0]

    return toWordNet[firstChar] if firstChar in toWordNet else wordnet.NOUN


def changeWord(t, pos=wordnet.NOUN):

    """
    Gets lemmatized form of a word using word-type.

    :param t: Part-of-speech tag
    :param pos: word-type

    :returns: lemma
    """

    w = ""
    t = t.lower() if not t.isupper() else t #abbreviations like IT should not be lower-cased since otherwise they are treated as stop word
    if t not in setStopWords: #ignore stop words
        w = pattern.sub(lambda m: rep[re.escape(m.group(0))], t).replace(" ", "") #remove punctuation
        w = alphaNumericpattern.sub('', w)
        if len(w) > 0:
            w = w if w[0].isalpha() else "" #lower case, ignore non-chars
            if len(w) < 3 and not w.isupper(): w=""
            w = lem.lemmatize(w, pos) if not "_" in w else w #lemmatize
            #w = stem(w) if not "_" in w else w

    return w


def transWord(w):

    """
    Extracts a word's lemmatized form from its word-type.
    Also returns original word if lemmatized form is not found.

    :param w: Word (String)

    :returns: lemma, lemma or original word
    """

    tag = get_wordnet_pos(nltk.pos_tag([w])[0][1])
    chw = changeWord(w, tag)
    dw = chw if len(chw) else w

    return chw, dw


def convertWord(w):

    """
    Extracts a word's lemmatized form from its word-type.

    :param w: Word (String)

    :returns: lemma
    """

    tag = get_wordnet_pos(nltk.pos_tag([w])[0][1])
    chw = changeWord(w, tag)
    return chw


def docSpacePunctuation(doc):

    """
    Splits document into tokens, ie. list of words using punctuation symbols like ".", "!"

    :param doc: Document (String)

    :returns: String
    """

    nopunctuation = pattern.sub(lambda m: rep[re.escape(m.group(0))], doc)
    text = alphaNumericpattern.sub(' ', nopunctuation)
    text = toSingleSpace(text)

    return text

    #Split words that are put together -> only helping in few cases
    # words=text.split(" ")
    # allw=[]
    # for w in words:
    #     if w.isupper():
    #         allw.append(w)
    #     else:
    #         splitws=re.findall('[a-zA-Z][a-z][a-z]*[A-Z][a-z][a-z]*', w)
    #         allw+=splitws
    #         if len(splitws)>1:
    #             print(w,splitws)
    #return allw


def docToWords(doc, biterms, oWordCount=None):

    """
    Creates a list of tokens from a document and updates dictionary mapping lemma to list of orginal words.
    Token can be lemmatized words, words, or bi-terms.

    :param doc: Document (String)
    :param biterms: List of valid composite words (bi-terms)
    :param oWordCount: Dictionary mapping lemma to list of original words

    :returns: List of words/bi-terms

    Example:
    Input:
    doc = "Hello world! Computer Science rocks."
    biterms = {"Computer Science"}
    oWordCount = {}

    Output:
    print(docToWords(doc, biterms, oWordCount)) >> ['hello', 'world', '\n', 'computer', 'science', 'rock', '\n']
    print(oWordCount) >> {"hello":["Hello"],"world":["world"],"computer":["Computer"],"science":["Science"],"rock":["rocks"]}
    
    """

    lines = doc.split("\n")
    d = []
    for l in lines:
        sentences = tokenizer.tokenize(l)
        for sen in sentences:
            s = []
            text = docSpacePunctuation(sen).split(" ") #split into tokens
            taggedtext = nltk.pos_tag([t for t in text if len(t) > 0])
            taggedtext = [(w,get_wordnet_pos(t)) for w, t in taggedtext]
            #text = doc.split(" ")
            matches = [(word, changeWord(word, tag)) for word, tag in taggedtext]
            matches = [(rm, m) for rm, m in matches if len(m) > 0]
            if not oWordCount is None:
                for raw, w in matches:
                    if not w in oWordCount: oWordCount[w] = []
                    oWordCount[w].append(raw)
            #matches = [t.lower() for t in text if t.isalpha()] #lower case, remove non-letters, words of length 1
            if len(matches) == 0: continue
            doskip = False
            for iw,(rw, w) in enumerate(matches):
                if doskip:
                    doskip=False
                    continue
                bt = rw.lower()+bsep+matches[iw+1][0].lower() if iw < len(matches)-1 else ""
                if bt in biterms: #we add only raw words
                    d.append(bt)
                    doskip = True
                    continue
                s.append(w)
            if len(s):
                s.append("\n")
                d += s
            #matches = [lem(t) for t in matches] #lemmatize words
            #matches = [stem(t) for t in matches]  # stem words
            #matches = [t for t in matches if not t in setStopWords]  # remove stop words again, due to stemming this seems to happen...

    return d


if __name__ == '__main__':
    doc = "Hello world! Computer Science rocks."
    biterms={"Computer Science"}
    oWordCount={}
    print(docToWords(doc, biterms, oWordCount)) # ['hello', 'world', '\n', 'computer', 'science', 'rock', '\n'] 
    print(oWordCount) # {"hello":["Hello"],"world":["world"],"computer":["Computer"],"science":["Science"],"rock":["rocks"]}

    # var="""This analysis and the standard reports are then presented to clients by Sales Consultants and Client Service Specialists for actionable items related to their consumer checking strategy and tool of product solutions.
    # Skip to main content
    # Newspaper logo is conditionally rendered if needed
    # Monster
    # Sr. Business Intelligence Architect at Uline
    # Pleasant Prairie, WI 53158
    #
    # About the Job
    #
    # Sr. Business Intelligence Architect
    #  
    # Uline – Shipping Supply Specialists
    #  
    # "The people I work with are as passionate as I am."
    # "I came to Uline for a job. Instead, I found a career."
    #  
    # Uline is North America's leading distributor of shipping, packaging and industrial supplies. We're a family-owned company known for our incredible customer service and quality products. Our people make the difference.
    #  
    # We're looking for the best and brightest to take our IT department to the next level. If you have passion and expertise in Java and .NET development, database modeling, business systems analysis, or solution architecture, Uline is the company for you.
    # Uline seeks a Sr. Business Intelligence Architect at its Corporate Headquarters in Pleasant Prairie, Wisconsin (just over the IL WI state line).
    #  
    # Join us to experience why Uline has been designated with the Forbes 2016 America’s Best Employers award.
    #  
    # POSITION RESPONSIBILITIES
    #  
    # Develop a practical roadmap for an enterprise-wide BI reporting and analytics platform.
    # Define the overall BI data architecture, including ETL processes, ODS, EDW, data marts and data lakes.
    # Recommend appropriate technologies to support the implementation of the BI roadmap.
    # Work with the data architect to insure that logical and physical data models support the analytic needs of the business.
    # Provide BI technical and architectural guidance to projects and teams, ensuring that new initiatives enable effective data reporting.
    # Collaborate with key business users to identify needs and opportunities for improved data management and delivery.
    # Design and build ETL processes.
    # Develop reporting solutions as needed.
    # Provide technical knowledge and business support to the BI team.
    # Ensure effective communication of user requirements.
    #  
    # MINIMUM REQUIREMENTS
    #  
    # Bachelor's degree in IT or related major.
    # Experience in the design and building of enterprise data warehouses.
    # Excellent understanding of data modeling, SQL and ETL.
    # Experience in multiple database platforms, including SQL Server, Oracle and DB2.
    # Experience working with end users to gather requirements and build technical solutions from concept to implementation.
    # Ability to facilitate meetings and delegate responsibilities.
    # Available for travel to Uline's domestic and international branches."""
    # var2=" Permanent role with growing services firm.Central location next to all transport links.Broad exposure to technologies and industry verticals.Apex&nbsp;Resource&nbsp;Solutions specialises in recruitment and related services across the Business Intelligence, Information Management and Analytics sectors, with over 7 years experience placing highly skilled professionals to an extensive list of clients."
    # #var2 = " Permanent role with growing services firm."
    # #getCompoundsAndWords(var.split("\n"))
    # print(var2)
    # parseSentences((1,[var2]))