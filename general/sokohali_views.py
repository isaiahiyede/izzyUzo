from general.forms import LoginForm, SubscriberForm, UserForm, EditSubscriberProfileForm
from views import LoginRequest
from django.contrib import messages
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

from django.http import  HttpResponseRedirect
from service_provider.models import Subscriber
from general.models import User
# from service_provider.models import Subscriber
from django.contrib.auth.models import User
from general.custom_functions import sokohali_subscriber_sendmail, sokohali_subscriber_mail
from django.core.mail import send_mail, EmailMessage

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from service_provider.models import Subscriber
from django.utils.crypto import get_random_string




def register(request):

	# print "rP: ", request.POST
	rp = request.POST

	if request.method == 'POST':
		subscribers_form = SubscriberForm(request.POST, request.FILES)
		user_form = UserForm(request.POST)

		if User.objects.filter(username = rp.get('username')).exists():
			print 'username exists'
			return render(request,'sokohali/register.html',{'subscribers_form':subscribers_form, 'user_form':user_form,'username_is_taken':True})                
		if User.objects.filter(email = rp.get('email')).exists():
			print 'email exists'                
			return render(request,'sokohali/register.html',{'subscribers_form':subscribers_form, 'user_form':user_form,'email_taken':True})                
		else:
			if user_form.is_valid and subscribers_form.is_valid:
				password  = rp.get('password')
				password1   = rp.get('password1')
				if password != password1:
					return render(request, 'sokohali/register.html', {'subscribers_form':subscribers_form, 'user_form':user_form,'password_mismatch':True})
				if len(password) < 8:
					return render(request, 'sokohali/register.html', {'subscribers_form':subscribers_form, 'user_form':user_form,'password_too_short':True})
				if password == rp.get('first_name'):
					return render(request, 'sokohali/register.html', {'subscribers_form':subscribers_form, 'user_form':user_form,'password_same_as_first_name':True})
				if password.isalpha():
					return render(request, 'sokohali/register.html', {'subscribers_form':subscribers_form, 'user_form':user_form,'password_should_be_alphanumeric':True})
				user = User.objects.create(username = rp.get('username'), email = rp.get('email').lower(),
					first_name = rp.get('first_name'), last_name = rp.get('last_name'))
	
				user.set_password(rp.get('password')) 
	
				photo = request.FILES.get('photo_id')
				country = request.POST.get('country')
				state = request.POST.get('state')
				
				subscribers = Subscriber.objects.create(
						user = user,
						photo_id = photo,
						address1 = rp.get('address1'),
						address2 = rp.get('address2'),
						city = rp.get('city'),
						phone_number = rp.get('phone_number'),
						zip_code = rp.get('zip_code'),
						state = state,
						country = country
							)
				
				subscribers.save()
				user.save()
	
				try:
					sokohali = 'Sokohali'
					subject = "Welcome to %s" %(sokohali)
					text = 'email/welcome_subscriber_email.txt'
					user = subscribers.user
					sokohali_subscriber_sendmail(request, user, subject, text, None)
				except Exception as e:
					print 'reg email error: ',e
					pass
	
				messages.success(request, 'Registration successful')
				return redirect('/login/')
			else:
				print "errors: ", subscribers_form.errors, user_form.errors

	else:
		subscribers_form = SubscriberForm()
		user_form = UserForm()
		return render(request,'sokohali/register.html',{'subscribers_form':subscribers_form, 'user_form':user_form})


	
def change_password(request, username=None):
	users = request.user.username
	print "User :",users
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		
		# if users.is_active:
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('general:change_password')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'sokohali/change_password.html', {'form': form})



def passwordrequest(request):
	rp = request.POST
	print "rp:",rp
	if request.method =='POST':
		email=request.POST['email']
		# print"Email :",email
		try:
			email_match = Subscriber.objects.get(user__email=email).user.email
			# print "Email Match : ",email_match

			user_match = Subscriber.objects.get(user__email=email).user.username
			# print "Email Match : ",user_match

			random_code = get_random_string(length=20)
			# print"Random Code :",random_code

			if user_match :
				user_value = User.objects.get(username=user_match)
				# print "S: ",user_value
				user_value.set_password(random_code)
				user_value.save()

			messages.success(request, 'Password changed successful!')
		except Exception as e:
			print "error: ",e
			pass

		'''send email to subscriber'''
		try:
			sokohali = 'Sokohali'
			subject = "Welcome to %s" %(sokohali)
			text = 'Your temporary password to Login: ' + random_code
			# print "Got Here"
			user = user_match
			email=email_match
			# print "Mail ",email
			sokohali_subscriber_mail(request, user, subject, text, email)
		except Exception as e:
			print 'reg email error: ',e
			pass
		
		return redirect('/login/')

	return render(request,'sokohali/login.html')



class LoginSubscriber(LoginRequest):
	template_name = 'sokohali/login.html'

	def post(self, request, *args, **kwargs):
		request = self.request


		#next = request.GET.get('next', '')
		if request.GET.has_key('next'):
			next_page = request.GET['next']
		#get next from cookies, if user is most likely a first timer
		elif request.COOKIES.has_key('next_page'):
			next_page = request.COOKIES["next_page"]
		else:
			next_page = ""

		error_msg = "There was an error with your E-Mail/Password combination. Please check and try again."

		form = LoginForm(request.POST)

		if form.is_valid():
				data_gotten  = str(request.POST.get('username_email')).strip()
				print 'data gottem: ', data_gotten
				if '@' in data_gotten:
					try:
						username_email = Subscriber.objects.get(user__email=data_gotten).user.username
					except:
						error_msg = "Email not found"
						messages.warning(request, error_msg)
						return redirect (request.META.get('HTTP_REFERER', '/'))
				else:
					try:
						username_email = data_gotten
					except:
						error_msg = "Username not found"
						messages.warning(request, error_msg)
						return redirect (request.META.get('HTTP_REFERER', '/'))

				password = form.cleaned_data['password']
				# print username_email
				user = authenticate(username=username_email, password=password)
				print "User",user
				# if not user:
				# 		user = sokohali_authenticate(username = username_email, password=password)
				if user is None:# or useraccount is None:
						messages.warning(request, error_msg)
						return redirect (request.META.get('HTTP_REFERER', '/'))

				else:
					redirect_to = next_page
					print 'user: ',user
					if user.is_active and user.subscriber:
							login(request, user)

							if user.is_superuser:
								response = redirect (reverse ("sokohaliAdmin:superuser_dasboard"))
							elif user.is_staff and user.subscriber:
								if user.last_login == user.date_joined:
									response = redirect (reverse ("sokohaliAdmin:client_dashboard"))
								else:
									if redirect_to == '':
										response = redirect (reverse ("sokohaliAdmin:client_dashboard"))
									else:
										response = redirect(redirect_to)
							elif user.subscriber:
								if redirect_to == '':
									response = redirect (reverse ("sokohaliAdmin:client_dashboard"))
								else:
									response = redirect(redirect_to)
							else:
								response = redirect (reverse ("access_denied"))

							return response

					else:
						error_msg = "Sorry, you need to activate your account before you can log-in.\
														Please contact customer service. Thank you."
						messages.warning(request, error_msg)
						return redirect (request.META.get('HTTP_REFERER', '/'))

				# else:
				#     redirect_to = next_page
				#     print 'user: ',user
				#     if user.is_active and user.subscriber:
				#         login(request, user)
				#
				#         if user.is_staff:
				#             if redirect_to == '':
				#                 response = redirect (reverse ("sokohaliAdmin:client_dashboard"))
				#             else:
				#                 response = redirect(redirect_to)
				#         else:
				#             response = redirect (reverse ("access_denied"))
				#
				#         return response
				#
				#             #return redirect(redirect_to)
				#     else:
				#         error_msg = "Sorry, you need to activate your account before you can log-in.\
				#                         Please contact customer service. Thank you."
				#         messages.warning(request, error_msg)
				#         return redirect (request.META.get('HTTP_REFERER', '/'))

		else:
			#print form.errors
			messages.warning(request, error_msg)
			return redirect (request.META.get('HTTP_REFERER', '/'))


	def get(self, request, *args, **kwargs):
		context = super(LoginSubscriber, self).get(request, *args, **kwargs)

		if request.user.is_authenticated():
			return redirect (reverse ("homepage"))
		return super(LoginRequest, self).get(request, *args, **kwargs)


def sokohali_logout(request):
		logout(request)
		return HttpResponseRedirect(reverse ("homepage"))


def business_settings(request):
	context = {}
	return render(request,'sokohali/business_settings.html',context)


def about(request):
	context = {}
	return render(request,'sokohali/about.html',context)

def contact(request):
	context = {}
	return render(request,'sokohali/contact.html',context)

def demopage(request):
	context = {}
	return render(request,'sokohali/demo.html',context)

def legal(request):
	context = {}
	return render(request,'sokohali/legal.html',context)


def subscriber_profile(request, username):
	profile = User.objects.get(username=username).useraccount.marketer.subscriber
	# profile = get_object_or_404(Subscriber, user__username = username)
	print "Profile : ",profile
	return render(request,'sokohali/subscriber_profile.html', {'profile':profile})

def subscriber_edit_profile(request, username=None):
	subscrber_detail = request.user.useraccount.marketer.subscriber
	# print "Subscriber :",subscrber_detail

	rp = request.POST
	print "rp",rp
	if request.method == 'POST':
		subscribers_edit_form =EditSubscriberProfileForm(request.POST, request.FILES or None, instance=request.user.useraccount.marketer.subscriber)
		user_edit_form =UserForm(request.POST,instance=request.user.useraccount.marketer.subscriber)

		if subscribers_edit_form.is_valid():
			subscribers_edit_form.save()

			return redirect('/')
		else:
			print "subscribers errors :",subscribers_edit_form.errors
			subscribers_edit_form = EditSubscriberProfileForm(instance=request.user.useraccount.marketer.subscriber)
			subscribers_edit_form1 = EditSubscriberProfileForm(instance=request.user.useraccount.marketer.subscriber)
	else:
		subscribers_edit_form = EditSubscriberProfileForm(instance=request.user.useraccount.marketer.subscriber)
		subscribers_edit_form1 = EditSubscriberProfileForm(instance=request.user.useraccount.marketer.subscriber)

	return render(request,'sokohali/subscriber_edit_profile.html', {'subscribers_edit_form':subscribers_edit_form,'subscribers_edit_form1':subscribers_edit_form1})


# def total_packages(request, user_id):
#     user = request.user
#     if user.
