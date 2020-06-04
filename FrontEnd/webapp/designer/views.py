import sys

from django.http import HttpResponse
from django.shortcuts import render

# get method name
from designer.models import taskProperty

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

#static process navigation table
navigation = {  'form11': {'next': 'form12', 'nextlabel': '1.2 Identify Stakeholders'},
				'form12': {'prev': 'form11', 'prevlabel': '1.1 Declare Rationale',
						   'next': 'form13', 'nextlabel': '1.3 Derive Objectives'},
				'form13': {'prev': 'form12', 'prevlabel': '1.2 Identify Stakeholders',
						   'next': 'form14', 'nextlabel': '1.4 Set up Communication Plan'},
				'form14': {'prev': 'form13', 'prevlabel': '1.3 Derive Objectives',
						   'next': 'form21', 'nextlabel': '2.1 Assess Status Quo'},
				'form21': {'prev': 'form14', 'prevlabel': '1.4 Set up Communication Plan',
						   'next': 'form22', 'nextlabel': '2.2 Identify Gaps'},
				'form22': {'prev': 'form21', 'prevlabel': '2.1 Assess Status Quo',
						   'next': 'form31', 'nextlabel': '3.1 Select Content'},
				'form31': {'prev': 'form22', 'prevlabel': '2.2 Identify Gaps',
						   'next': 'form32', 'nextlabel': '3.2 Integrate Content'},
				'form32': {'prev': 'form31', 'prevlabel': '3.1 Select Content',
						   'next': 'form41', 'nextlabel': '4.1 Communicate Results'},
				'form41': {'prev': 'form32', 'prevlabel': '3.2 Integrate Content',
						   'next': 'form42', 'nextlabel': '4.2 Evaluate Curriculum'},
				'form42': {'prev': 'form41', 'prevlabel': '4.1 Communicate Results',
						   'next': 'form43', 'nextlabel': '4.3 Set Up CDP Continuity'},
				'form43': {'prev': 'form42', 'prevlabel': '4.2 Evaluate Curriculum'}}


def handleProcessForm(formName, request):
	'''
	:param formName: name of the actual form. Serves as selector in the DB.
	:param request: django request parameter contains form data.
	:return: properties stored in the DB.
	'''
	contextDict = dict()
	contextDict['form'] = formName
	contextDict['navigation'] = navigation[formName]

	#check if user is logged in
	if request.user.is_authenticated:
		profile = request.user.profile
	else:
		return contextDict

	#handle POST data
	if request.POST:
		properties = taskProperty.objects.filter(IsEnabled=True, Form=formName, Owner=profile)

		# Reset all params
		for param in properties:
			param.IsChecked = False
			param.save()

		# Set selected params
		for key, value in request.POST.items():
			# consider only checkboxes!!
			if value == 'on':
				# check if property exist already and update
				try:
					# update property
					property = taskProperty.objects.get(Name=key, Form=formName)
					property.IsChecked = True
				except:
					# create new property
					property = taskProperty()
					property.Form = formName
					property.Owner = profile
					property.Name = key
					property.IsChecked = True

				#store property in DB
				property.save()
	else:
		#handle REQUEST
		pass

	#get all properties stored in the DB
	properties = taskProperty.objects.filter(IsEnabled=True, Form=formName, Owner=profile)

	#create dictionary for easier property handling in templates
	for property in properties:
		contextDict[property.Name] = property.IsChecked

	return contextDict




# Create your views here.

def home(request):
	return HttpResponse(render(request, 'home.html', None))


def form1(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form.html', {'properties': contextDict,}))

def form11(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form11.html', {'properties': contextDict,}))

def form12(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form12.html', {'properties': contextDict,}))

def form13(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form13.html', {'properties': contextDict,}))

def form14(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form14.html', {'properties': contextDict,}))

def form21(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form21.html', {'properties': contextDict,}))

def form22(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form22.html', {'properties': contextDict, }))

def form31(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form31.html', {'properties': contextDict,}))

def form32(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form32.html', {'properties': contextDict, }))

def form41(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form41.html', {'properties': contextDict,}))

def form42(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form42.html', {'properties': contextDict, }))

def form43(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form43.html', {'properties': contextDict, }))

def form2(request):
	formName = currentFuncName()
	contextDict = handleProcessForm(formName, request)

	return HttpResponse(render(request, 'form2.html', {'properties': contextDict,}))

