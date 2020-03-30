import json
from collections import OrderedDict

from django.forms import ModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from textis.models import Syllables
from BackEnd.jobads import getTerms
from FrontEnd.webapp.textis.jobads import getJobAdds, prepareScatterData
from FrontEnd.webapp.textis.apps import compwords, wToL, longPhrases, wordOcc, association, wordToIndex, coitow, \
	wordCounts
from FrontEnd.webapp.textis.wordCompare import getAssociationsAll, precision


class syllablesForm(ModelForm):
	class Meta:
		model = Syllables
		fields = '__all__'



def analyzeSyllables(request):
	'''
	Analyzes a syllables request and returns the single word results in the syllabusResults.html
	:param request: django request object with request form
	:return: django rendered html template
	'''
	if request.method == "POST":
		form = syllablesForm(request.POST)

		if form.is_valid():
			# generate chart
			syllables = form.save(commit=False)
			rtext = syllables.text.replace("\n", " ").replace("\t", " ").replace("  ", " ").replace("  ", " ")
			tokenizedWords = getTerms(rtext, wordCounts, wToL)

			#save syllables in the database
			syllables.save()

			context = {
				'rawText' : rtext,
	            'foundwords': tokenizedWords,
	        }
			return HttpResponse(render(request, 'syllabusResults.html', context))
	else:
		form = syllablesForm()

		context = {
			'form' : form
		}

	return  HttpResponse(render(request, 'syllabus.html', context))



def syllabusSingle(request):
	'''
	Analyzes a single word from the previous analyzeSyllables() method an returns the
	results in syllabusResults.html
	:param request: django request object with request form
	:return: django rendered html template
	'''

	if request.POST:
		word1 = request.POST['word']
		tokenizedWords = request.POST['foundwords'].split("),")

		foundwords = list()
		for item in tokenizedWords:
			value = item.split(',')[0].replace("'","")
			key = item.split(',')[1].replace("'","")

			if "None" in key:
				key = None

			foundwords.append((value[1:], key))

		lem1 = wToL[word1]
		ass1 = getAssociationsAll(word1, wToL, coitow, association)
		bars1 = [{"word": coitow[x[0]], "val": x[1], "otherval": 0} for x in ass1]
		bars1 = bars1[::-1]

		jobads1 = ""
		if lem1 in longPhrases:
			jobads1 = getJobAdds(lem1)

		# get compound words of lem1
		newCompWords1 = dict()

		for word in compwords[lem1]['in']:
			compWord = word[1]
			if compWord in wordCounts:
				count = wordCounts[compWord]
				newCompWords1[compWord] = count

		scatterList = prepareScatterData(bars1, lem1, word1)

		# word occurance with precision
		b = wordOcc[lem1]
		i1 = precision(b)

	context = {
		'foundwords': foundwords,
		'word1': word1,
		'bar1': bars1[:50],
		'occWord1': round(wordOcc[lem1], i1),
		'countWord1': wordCounts[lem1],
		'compWords1' : OrderedDict(sorted(newCompWords1.items(), key=lambda x: x[1], reverse=True)),
        'jobads1': jobads1,
		'wordCounts' : wordCounts,
		'scatterList' : scatterList,
	}

	return HttpResponse(render(request, 'syllabusResults.html', context))



@DeprecationWarning
#################
# ajax requests
#################
def getjobads(request):
	if request.POST:
		word = request.POST['Word']

		# create a form instance and populate it with data from the request:

		if request.is_ajax():
			response = dict()

			phrases = ""
			response['word'] = word
			response['wordOcc'] = 0
			response['frequentWords'] = "-"
			response['mediumWords'] =  "-"
			response['rareWords'] =  "-"
			response['compoundsWords'] =  "-"

			if word in wToL:
				lem = wToL[word]

				if lem in longPhrases:
					#get job add phrases (limit to 3)
					for phrase in longPhrases[lem][:3]:
						phrases = phrases + "..." + phrase + "...<br><br>"

				# initialize response with empty data
				response['phrases'] = phrases

				#find word association
				newWord = wordToIndex[wToL[word]] if wToL[word] in wordToIndex else ""
				if newWord in association:
					wDict = association[newWord]
					ass = 'Freq'
					data = [coitow[wDict[ass][j][0]] for j in range(len(wDict[ass]))]
					response['frequentWords'] = ", ".join(str(x) for x in data)

					ass = 'Med'
					data = [coitow[wDict[ass][j][0]] for j in range(len(wDict[ass]))]
					response['mediumWords'] = ", ".join(str(x) for x in data)

					ass = 'Rare'
					data = [coitow[wDict[ass][j][0]] for j in range(len(wDict[ass]))]
					response['rareWords'] = ", ".join(str(x) for x in data)

				# get occourancy of the word
				if lem in wordOcc:
					response['wordOcc'] = wordOcc[lem]

				# find compounds
				if lem in compwords:
					response['compoundsWordsIn'] = ", ".join(str(x) for x in compwords[lem]['in'])
					response['compoundsWordsParts'] = ", ".join(str(x) for x in compwords[lem]['parts'])

			# return as json format
			return JsonResponse(json.dumps(response), safe=False)
