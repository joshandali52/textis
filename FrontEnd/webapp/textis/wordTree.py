from collections import OrderedDict

from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render

from FrontEnd.webapp.textis.apps import wToL, longPhrases, assTreeWin, assAbsTreeWin, assTreeDoc, \
	assAbsTreeDoc, wordCounts, compwords
from textis.models import WordTree
import json


class wordForm(ModelForm):
	class Meta:
		model = WordTree
		fields = '__all__'


def tree(request):

	if request.method == "POST":
		form = wordForm(request.POST)

		if form.is_valid():
			# generate chart
			tree = form.save(commit=False)

			word = tree.word

			#save syllables in the database
			tree.save()

			#if one word is missing, no compare can be executed
			if (not word in wToL):
				context = {
					'error': "No Info found",
					'word': word,
				}
			else:
				dataAssTreeWin = dataAssAbsTreeWin = dataAssTreeDoc = dataAssAbsTreeDoc = None
				lem = wToL[word]

				if lem in assTreeWin:
					dataAssTreeWin = json.dumps(assTreeWin[lem])
					#print(assAbsTree[lem])  # (Recursive) Tree structure node and list of children (children are nodes themselves)

				if lem in assAbsTreeWin:
					dataAssAbsTreeWin = json.dumps(assAbsTreeWin[lem])
					#print(assAbsTree[lem])  # (Recursive) Tree structure node and list of children (children are nodes themselves)

				if lem in assTreeDoc:
					dataAssTreeDoc = json.dumps(assTreeDoc[lem])
					#print(assAbsTree[lem])  # (Recursive) Tree structure node and list of children (children are nodes themselves)

				if lem in assAbsTreeDoc:
					dataAssAbsTreeDoc = json.dumps(assAbsTreeDoc[lem])
					#print(assAbsTree[lem])  # (Recursive) Tree structure node and list of children (children are nodes themselves)

				#context variables passing to the rendering
				context = {
					'word' : word,
					'dataAssTreeWin' : dataAssTreeWin,
					'dataAssAbsTreeWin' : dataAssAbsTreeWin,
					'dataAssTreeDoc' : dataAssTreeDoc,
					'dataAssAbsTreeDoc' : dataAssAbsTreeDoc,
					'longPhrases' : longPhrases,
					'wordCounts' : wordCounts,
					'compWords': compwords,
				}
			#return results
			return HttpResponse(render(request, 'treeResults.html', context))
	else:
		form = wordForm()

		context = {
			'form' : form
		}
	#return form
	return  HttpResponse(render(request, 'tree.html', context))
