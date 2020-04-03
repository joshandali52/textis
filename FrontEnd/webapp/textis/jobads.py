from FrontEnd.webapp.textis.apps import longPhrases, Conf, wordOcc, wToL

# calculate precision 2 ob b
def precision(b):
	i = 2
	while b * 10 < 1:
		b = b * 10
		i = i + 1
	return i


def getJobAdds(lem):
	'''
	Helper method to get all job adds of one phrase
	:param lem:
	:return:
	'''
	jobads = list()
	# get job add phrases
	for phrase in longPhrases[lem]:
		itemDict = dict()
		jobID = phrase[0]

		filePath = jobID.replace('/mnt/data2/public/jobads/', Conf.rpath)

		try:
			f = open(filePath)
			itemDict['full'] = f.read()
		except:
			pass

		itemDict['short'] = phrase[1].strip()
		jobads.append(itemDict)

	return jobads


def prepareScatterData(bars, lem, selectedWord):
	scatterList = list()
	for word in bars[:50]:
		if word != '\\':
			key = word['word']
			# word occurance with precision
			try:
				lem1 = wToL[key]
				b = wordOcc[lem1]
				i1 = precision(b)

				value = word['val']
				newChild = dict()
				newChild['word'] = key
				newChild['size'] = round(wordOcc[lem1], i1) #wordCounts[key]
				newChild['edge'] = value
				scatterList.append(newChild)
			except:
				#no data for key word
				pass

	# add selected word
	newChild = dict()
	# word occurance with precision
	lem1 = wToL[selectedWord]
	b = wordOcc[lem1]
	i1 = precision(b)
	newChild['word'] = selectedWord + "**"
	newChild['size'] = round(wordOcc[lem1], i1)
	newChild['edge'] = 1
	scatterList.append(newChild)
	return scatterList
