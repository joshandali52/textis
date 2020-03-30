from django.contrib import admin

# Register your models here.
from textis.models import WordCompare, WordTree, Syllables


class SyllablesAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ['text']

admin.site.register(Syllables, SyllablesAdmin)


class WordCompareAdmin(admin.ModelAdmin):
    list_display = ('id', 'word1', 'word2')
    search_fields = ['word1']

admin.site.register(WordCompare, WordCompareAdmin)


class WordTreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ['word']

admin.site.register(WordTree, WordTreeAdmin)