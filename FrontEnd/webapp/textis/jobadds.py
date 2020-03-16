from FrontEnd.webapp.textis.apps import longPhrases, Conf, wordCounts


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
			value = word['val']
			newChild = dict()
			newChild['word'] = key
			newChild['size'] = wordCounts[key]
			newChild['edge'] = value
			scatterList.append(newChild)
	# add selected word
	newChild = dict()
	newChild['word'] = selectedWord + "**"
	newChild['size'] = wordCounts[lem]
	newChild['edge'] = 1
	scatterList.append(newChild)
	return scatterList
