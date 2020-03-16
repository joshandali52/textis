from django.db import models



class Syllables(models.Model):
	text = models.TextField('Syllables Text')


class WordCompare(models.Model):
	word1 = models.CharField('Word1', max_length=200)
	word2 = models.CharField('Word2', max_length=200)


class WordTree(models.Model):
	word = models.CharField('Word', max_length=200)
