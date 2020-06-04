#
# userViews.py - Contains user management for dashboard
#
# Date 31.07.2016, Malcesine - after 4 hours 4.7 session, DonMiguel
#
# User management contains the following features base on the django user model:
# - register new user
#   - login/logout
#   - reset password via eMail

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
import json
from django.utils.http import int_to_base36, base36_to_int

from FrontEnd.webapp.designer.lib.sendMail import sendMail
from designer.models import Profile
from FrontEnd.webapp.designer.settings import TEMPLATE_MAIL_PATH, REDIRECT_AFTER_RESET, REDIRECT_AFTER_LOGIN

TEMPLATE_USER_PATH =  "user/"



class userForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']



def reset(request):
	error = ""
	uemail = None

	if request.method == 'POST':
		templateName = TEMPLATE_MAIL_PATH + "password_reset_email.html"
		uemail = request.POST['email']

		users = User.objects.filter(email__iexact=uemail, is_active=True)

		if not len(users):
			error = "We are sorry, but your eMail address was not found!"
		else:
			"""
			Generates a one-use only link for resetting password and sends it to the
			user.
			"""
			for user in users:
				c = {
					'email': user.email,
					'domain': get_current_site(request).domain + "/",
					'site_name': "Dashboard",
					'uid': int_to_base36(user.id),
					'user': user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
				}
				sendMail.send(templateName, c, "Password reset", user.email)

			return redirect(REDIRECT_AFTER_RESET)

	return render(request, TEMPLATE_USER_PATH + 'pwdreset.htm', {
		'error': error,
		'email': uemail,
	})




def userLogin(request):
	error = None
	response = dict()

	#if there are old session data, clean up first
	if request.user.is_authenticated:
		return redirect(REDIRECT_AFTER_LOGIN)

	#login
	if request.method == 'POST':
		user = authenticate(username=request.POST['email'],
		                    password=request.POST['pwd'])

		next = request.POST.get('next')

		# set error text first . if logged in,
		error = "User not found or password is wrong."

		if user is not None:
			if user.is_active:
				login(request, user)
				profile = Profile.objects.get(IsUser=user)
				# now, is that profile locked ??
				if profile.IsEnabled:
					request.session['DashProfileId'] = profile.id
					stayloggedin = request.POST.get('stayloggedin')

					if stayloggedin == "on":
						profile.StayLoggedIn = True
					else:
						profile.StayLoggedIn = False
						#delete session when closing the browser
						request.session.set_expiry(0)

					profile.LoginCount = profile.LoginCount + 1
					profile.save()

					if next != '':
						return redirect(next)
					return redirect(REDIRECT_AFTER_LOGIN)

			# oh ... locked ...
			error = "Profile found, but disabled."

	#return login form
	return render(request, TEMPLATE_USER_PATH + 'login.htm', {
		'error': error,
		'next': request.GET.get('next', '')
	})



def userLogout(request):
	error = None
	response = dict()

	#if there are old session data, clean up first
	if request.user.is_authenticated:
		logout(request)

	return redirect(REDIRECT_AFTER_RESET)




def confirmNewPassword(request, uid, token):
	error = ""

	# try to find a user with given token
	try:
		uid_int = base36_to_int(uid)
		user = User.objects.get(id=uid_int)
	except (ValueError, User.DoesNotExist):
		user = None

	if request.POST:
		if request.POST['pwd1'] == request.POST['pwd2']:
			user.set_password(request.POST['pwd1'])
			user.save()
			return redirect(REDIRECT_AFTER_LOGIN)
		else:
			error = "New password and confirm password are not the same."

	validlink = 0

	# if no user found and given token is not valid, display error message
	if user is not None and default_token_generator.check_token(user, token):
		validlink = 1

	return render(request, TEMPLATE_USER_PATH + 'pwdconfirm.htm', {
		'validlink': validlink,
		'error' : error,
	})




def register(request):
	error = None
	eMail = ""
	fname = ""
	lname = ""

	if request.POST:
		eMail = request.POST['email']
		pwd = request.POST['pwd']
		fname = request.POST['firstname']
		lname = request.POST['lastname']
		#code = request.POST['code']

		# same e-mail not allowed
		# password has to fit ..
		if pwd != request.POST['confirm']:
			error = "Password does not match confirmed password."

		if User.objects.filter(username=eMail).count() != 0:
			error = "This E-Mail (%s) does already exist. Please contact our administrator, but try to login first." % (eMail)

		elif not '@' in eMail or not '.' in eMail:
			error = "Please enter your email in the form name@domain.xy"

		if error is None:
			# create user
			profile, error = createNewUser(request, eMail, pwd, fname, lname)

			#login user after register
			user = authenticate(username=request.POST['email'], password=request.POST['pwd'])

			if user is not None:
				if user.is_active:
					login(request, user)
					request.session['DashProfileId'] = profile.id

					profile.LoginCount = profile.LoginCount + 1
					profile.save()
			else:
				error = "User not authenticated! Login in again."

		if error is None:
			#redirct after register
			return redirect(REDIRECT_AFTER_LOGIN)

	# return register form
	return render(request, TEMPLATE_USER_PATH + 'register.htm', {
		                                                            'error': error,
	                                                                'email': eMail,
	                                                                'fname': fname,
	                                                                'lname': lname
		                                                             })




@login_required
def getProfile(request):
	error = None

	profile = request.user.profile

	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = userForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			userform = userForm(request.POST, instance=profile.IsUser, prefix="user")

			userform.save()

			#does user want to change his password?
			if request.POST['oldPassword'] != '' and request.POST['newPassword'] != '':
				#old password is correct?
				if check_password(request.POST['oldPassword'], profile.IsUser.password):
					#new password is confirmed?
					if request.POST['newPassword'] == request.POST['retPassword']:
						#change password...
						profile.IsUser.set_password(request.POST['newPassword'])
						try:
							profile.IsUser.save()
						except:
							error = 'Oops, we could not save your changes. Something went wrong...'
					else:
						error = 'New password and confirm password are not the same.'
				else:
					error = 'Your old password is not correct.'

			# redirect to a new URL:
			if error is None:
				return redirect(REDIRECT_AFTER_LOGIN)

	# if a GET (or any other method) we'll create a blank form
	else:
		userform = userForm(instance=profile.IsUser, prefix="user")

	return render(request, TEMPLATE_USER_PATH + 'profile.htm', {
		'userform': userform,
		'error': error,
		'profile' : profile,
	})



@login_required
def sendMessage(request, uid):
	error = None

	profile = request.user.profile

	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		subject = request.POST['subject']
		message = request.POST['message']

		# add mew Data
		if (len(message) > 1):
			templateName = "mail/sendMail.htm"

			c = {
				'message': message,
				'user' : profile.IsUser,
				'name': profile.IsUser.first_name + ' ' + profile.IsUser.last_name
			}
			sendMail.send(templateName, c, 'Lunch Event: ' + subject, profile.IsUser.email)

		return redirect(REDIRECT_AFTER_LOGIN)

	# if a GET (or any other method) we'll create a blank form

	return render(request, TEMPLATE_MAIL_PATH + 'message.htm', {
	                                                          'user' : profile
	                                                          })


'''
send mail sends a message with a subject to a email address.
Method can be used as ajax call or http post.
'''
def sendMsg(request):
	#only as ajax possible
	response = dict()
	response['error'] = ""

	if request.is_ajax():
		emailto = request.POST['emailto']
		emailfrom = request.POST['emailfrom']
		subject = request.POST['subject']
		message = request.POST['message']
		name = request.POST['name']

		#add mew Data
		if (len(message) > 1):
			templateName = TEMPLATE_MAIL_PATH + "sendMail.htm"

			c = {
				'message': message,
				'name': name,
				'from': emailfrom
			}
			sendMail.send(templateName, c, subject, emailto)
		else:
			response['error'] = "No message to send."

	response['html'] = "Message successfully send."

	return JsonResponse(json.dumps(response), safe=False)


'''
Creates a new django user and Profile
'''
def createNewUser(request, mail, pwd, firstname, lastname):
	error = None
	user = User.objects.create_user(mail, mail, pwd)
	user.is_staff = False
	user.is_active = True
	user.first_name = firstname
	user.last_name = lastname
	user.save()

	lang = 'de'
	if 'HTTP_ACCEPT_LANGUAGE' in request.META:
		lang = request.META['HTTP_ACCEPT_LANGUAGE'].strip()
		lang = lang[0:2].lower()

	# create profile
	profile = Profile()
	profile.IsUser = user
	profile.Lang = lang
	profile.MailNotification = True

	#set all locations as default
	profile.save()
	return profile, error