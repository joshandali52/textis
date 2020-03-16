from django.urls import path
from FrontEnd.webapp.textis import views, wordCompare, wordTree

#entry point for django views
urlpatterns = [
	path('', views.analyzeSyllables),
	path('compare', wordCompare.compare),
	path('tree', wordTree.tree),
	path('syllabussingle', views.syllabusSingle),

	#ajax urls
	#path('phrases', views.getjobads)
]

