from collections import OrderedDict

from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render

from FrontEnd.webapp.textis.jobads import getJobAdds, prepareScatterData, precision
from FrontEnd.webapp.textis.apps import compwords, wToL, wordCounts, wordOcc, association, coitow, longPhrases
from textis.models import WordCompare


class wordForm(ModelForm):
	class Meta:
		model = WordCompare
		fields = '__all__'


def getAssociationsAll(word, wToL, coitow, assDict):
	wtoi = {k: i for i, k in coitow.items()}
	k = wtoi[wToL[word]] if wToL[word] in wtoi else ""

	if k == "":
		return []

	allAss = sum([v for v in assDict[k].values()], [])
	allAss.sort(key=lambda x: x[1])

	return allAss


def compare(request):
	'''
	Compares two words with each other and returns the results in compareResults.html
	:param request: django request object with request form
	:return: django rendered html template
	'''
	context = {}

	if request.method == "POST":
		form = wordForm(request.POST)

		if form.is_valid():
			# generate chart
			compare = form.save(commit=False)

			word1 = compare.word1
			word2 = compare.word2

			foundwords = []
			tokenizedWords = []

			# save syllables in the database
			compare.save()

			# if one word is missing, no compare can be executed
			if (not word1 in wToL) or (not word2 in wToL):
				context = {
					'error': "No Info found",
					'word1': word1,
					'word2': word2,
				}
			else:
				lem1 = wToL[word1]
				lem2 = wToL[word2]
				ass1 = getAssociationsAll(word1, wToL, coitow, association)
				dass1 = {x[0]: x[1] for x in ass1}
				ass2 = getAssociationsAll(word2, wToL, coitow, association)
				dass2 = {x[0]: x[1] for x in ass2}
				bars1 = [{"word": coitow[x[0]], "val": x[1], "otherval": dass2[x[0]] if x[0] in dass2 else 0} for x in
				         ass1]
				bars2 = [{"word": coitow[x[0]], "val": x[1], "otherval": dass1[x[0]] if x[0] in dass1 else 0} for x in
				         ass2]

				bars1 = bars1[::-1]
				bars2 = bars2[::-1]

				jobads1 = None
				if lem1 in longPhrases:
					jobads1 = getJobAdds(lem1)

				jobads2 = None
				if lem2 in longPhrases:
					jobads2 = getJobAdds(lem2)

				# get compound words of lem1
				newCompWords1 = dict()
				for word in compwords[lem1]['in']:
					compWord = word[1]
					if compWord in wordCounts:
						newCompWords1[compWord] = wordCounts[compWord]

				# get compound words of lem2
				newCompWords2 = dict()
				for word in compwords[lem2]['in']:
					compWord = word[1]
					if compWord in wordCounts:
						newCompWords2[compWord] = wordCounts[compWord]

				# word occurance with precision
				b = wordOcc[lem1]
				i1 = precision(b)

				b = wordOcc[lem2]
				i2 = precision(b)

				scatterList1 = prepareScatterData(bars1, lem1, word1)
				scatterList2 = prepareScatterData(bars2, lem2, word2)

				# context variables passing to the rendering
				context = {
					'rawWords': tokenizedWords,
					'foundwords': foundwords,
					'word1': word1,
					'word2': word2,
					'bar1': bars1[:50],
					'bar2': bars2[:50],
					'occWord1': round(wordOcc[lem1], i1),
					'occWord2': round(wordOcc[lem2], i2),
					'countWord1': wordCounts[lem1],
					'countWord2': wordCounts[lem2],
					'compWords1': OrderedDict(sorted(newCompWords1.items(), key=lambda x: x[1], reverse=True)),
					'compWords2': OrderedDict(sorted(newCompWords2.items(), key=lambda x: x[1], reverse=True)),
					'jobads1': jobads1,
					'jobads2': jobads2,
					'wordCounts': wordCounts,
					'scatterList1': scatterList1,
					'scatterList2': scatterList2,
					'wordOcc': wordOcc,
				}
			# return results
			return HttpResponse(render(request, 'compareResults.html', context))
	else:
		form = wordForm()

		context = {
			'form': form
		}
	# return form
	return HttpResponse(render(request, 'wordcompare.html', context))

