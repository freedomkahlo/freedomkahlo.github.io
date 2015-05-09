from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from .models import Instance, Invitee, Notification, PossTime, UserProfile, VetoTime, Message
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import timedelta, datetime
from backend import cal
import pytz
import math

# Render the home page after being logged in
@login_required
def index(request):
	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	user_list = User.objects.all()
	context = {'latest_event_list': latest_event_list, 'user_list': user_list, 'showIndexTour': False}

	user = request.user
	if user.UserProfile.firstTimeHome: #Only need to show tour their first time
		context['showIndexTour'] = True
		user.UserProfile.firstTimeHome = False
		user.UserProfile.save()

	request.path_info = '/'
	return render(request, 'index.html', context)

# Render the event page for a given eventID
def detail(request, eventID):
	event = get_object_or_404(Instance, eventID=eventID)
	resp = deletePastPossTimes(request, eventID)
	if resp: #If event was deleted
		return resp

	context = {'event': event, 'showInviteeTour': False, 'showCreatorTour': False}

	if request.user.is_authenticated(): # Only show more information to those that are logged in
		username = request.user.username
		user = get_object_or_404(User, username=username)

		isInvitee = False
		invitees = event.invitee_set.all()
		for invitee in event.invitee_set.all():
			if invitee.name == username:
				isInvitee = True
				break

		# Set instructions based on whether they've seen it before
		if (event.creator == username) and (user.UserProfile.firstTimeEventAsCreator):
			context['showCreatorTour'] = True
			user.UserProfile.firstTimeEventAsCreator = False
			user.UserProfile.save()
		elif isInvitee and user.UserProfile.firstTimeEventAsInvitee:
			context['showInviteeTour'] = True
			user.UserProfile.firstTimeEventAsInvitee = False
			user.UserProfile.save()

	return render(request, 'detail.html', context)

# Called when a user creates an event
@login_required
def add(request):	
	eventIDLength = 10

	# Pull the event parameters from the request
	title=request.POST.get('title', '')
	desc=request.POST.get('desc', '')
	start_date=request.POST.get('start_date', '')
	end_date=request.POST.get('end_date', '')
	start_time=request.POST.get('start_time', '')
	end_time=request.POST.get('end_time', '')
	event_length=request.POST.get('event_length', '')
	creator = request.POST['username']
	timezone = request.POST.get('timezone', 'Eastern')
	
	# Get a unique identifier for the event
	eventID = get_random_string(length=eventIDLength)
	while Instance.objects.filter(eventID__iexact=eventID).count() != 0:
		eventID = get_random_string(length=eventIDLength)

	# Save the form context if there was an error creating the event
	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	returnMsg = {'error': '', 'latest_event_list': latest_event_list,
			'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'start_time':start_time,
			'end_time':end_time, 'event_length':event_length, 'creator':creator, 'timezone':timezone}

	#Parse the time range
	timeSplit = event_length.split()
	if len(timeSplit) == 4: #both hours and minutes
		event_length = timeSplit[0] + ':' + timeSplit[2]
	elif timeSplit[1][0] == 'h': #only hours
		event_length = timeSplit[0] + ':0'
	else:
		event_length = '0:' + timeSplit[0]
	e = Instance(title=title, desc=desc, start_date=start_date, end_date=end_date, 
		start_time=start_time, end_time=end_time, event_length=event_length,
		creator=creator, eventID=eventID, timezone = timezone, is_scheduled = False)

	#try catch here check validity
	try:
		e.save()
	except ValidationError as e:
		returnMsg['error'] = e[0]
		return render(request, 'index.html', returnMsg)

	return getTimes(request, eventID) # Generate the times that work for the event creator

# Handle the request to change password (on the my account page)
@login_required
def changePassword(request):
	user = request.user
	oldPass = request.POST['oldPassword']

	# Check if old password correct and new passwords match
	if not user.check_password(oldPass):
		return render(request, 'user.html', {'invalidPassword':'Incorrect password.'})
	newPass = request.POST['newPassword']
	newPass2 = request.POST['confirmPassword']
	if newPass != newPass2:
		return render(request, 'user.html', {'invalidPassword':'Passwords do not match.'})
	if newPass == '':
		return render(request, 'user.html', {'invalidPassword':'Password cannot be blank.'})
	user.set_password(newPass)
	user.save()

	messages.success(request, 'Your password has successfully been changed!')
	return HttpResponseRedirect('/userPage/')


@login_required
def delete(request):
	eventID = request.POST['eventID']
	event = get_object_or_404(Instance, eventID=eventID)

	# Notification telling the invitees that the event was deleted
	n = Notification(desc=event.title, notificationType="deleteNot", originUserName =event.creator, pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

	for invitee in event.invitee_set.all():
		user = get_object_or_404(User, username=invitee.name)
		user.notification_set.add(n)
		user.save()

	event.delete()
	return HttpResponseRedirect('/')

# Delete all of the possible times that have already elapsed
def deletePastPossTimes(request, eventID=None):
	if eventID == None:
		eventID = request.POST['eventID']

	event = get_object_or_404(Instance, eventID=eventID)
	tz = pytz.timezone('US/' + event.timezone)

	possTimes = event.posstime_set.all()
	badPossTimes = [x for x in possTimes if x.startTime < datetime.now(tz)] # All times that have occured in the past

	for x in badPossTimes:
		x.delete()

	# Delete all the times that were vetoed that were in the past
	vetoTimes = event.vetotime_set.all()
	badVetoTimes = [x for x in vetoTimes if x.startTime < datetime.now(tz)]

	for x in badVetoTimes:
		x.delete()

	# If the event has no possible times left (event occured in the past), delete the event
	if len(event.posstime_set.all()) == 0 and not event.is_scheduled:
		#Need to delete event
		n = Notification(desc=event.title, notificationType="noTimeNot", originUserName =event.creator, pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for invitee in event.invitee_set.all():
			user = get_object_or_404(User, username=invitee.name)
			user.notification_set.add(n)
			user.save()

		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		event.delete()
		messages.success(request, 'Your event has expired before scheduling.')
		return HttpResponseRedirect('/')

# Handle forget password requests
def forgotPassword(request, login_key=''):
	if request.method == 'POST': #Submitted request of forgot password
		# Send verification email to make sure they want to reset their password
		email = request.POST['username']
		if len(User.objects.filter(username=email)) == 0:
			#No user with that username found
			return render(request, 'login.html', {'invalidUsername':'No user with that email found.'})
		#Now send link to change password
		profile = User.objects.filter(username=email)[0].UserProfile
		keyLength = 10

		key = get_random_string(length=keyLength)
		while UserProfile.objects.filter(login_key__iexact=key).count() != 0:
			key = get_random_string(length=keyLength)
		profile.login_key = key

		profile.save()

		#Send email with validation key
		msg = '''Hi %s, 
We have received a request to reset the password associated with this e-mail address. Click the link below to reset your password:
http://www.skedg.tk:82/forgotPassword/%s
If you did not request to have your password reset, please ignore this email.''' % (profile.user.first_name, key)
		send_mail('Skedg Password Assistance', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
		return render(request, 'login.html', {'successForgot':"We have sent an email to the email specified with instructions for resetting your password. If you don't receive this email, please check your spam folder."})

	# Reached if they have pressed the link to reset their password
	elif request.method == 'GET':
		user_profile = get_object_or_404(UserProfile, login_key=login_key)

		user_profile.login_key = ''
		user_profile.save()

		passLength = 10
		password = get_random_string(length=passLength)
		user_profile.user.set_password(password)
		user_profile.user.save()
		#Send email with their new password
		msg = '''Hi %s, 
You have successfully reset your password. After logging in, you can change your password on the My Account page.
Your password is: %s''' % (user_profile.user.first_name, password)
		send_mail('Skedg Password Assistance', msg, 'skedg.notify@gmail.com', [user_profile.user.username], fail_silently=False)
		return render(request, 'login.html', {'successForgot':'We have reset your password. Please check your email for your new password. You can change your password on the My Account page.'})

# Get the valid time intervals from cal.py and then generate the possible times in 15 minute increments
def getTimes(request, eventID=None):
	roundToMin = 15 #minutes

	#round up to nearest 15 minutes
	def roundUpByTimeDelta(tm):
		upmins = math.ceil(float(tm.minute)/15)*15
		diffmins = upmins - tm.minute
		return timedelta(minutes=diffmins)

	if eventID == None:
		eventID = request.POST['eventID']

	# Get the event and all the current invitees
	event = get_object_or_404(Instance, eventID=eventID)
	many = []
	many.append(event.creator)

	for i in event.invitee_set.all():
		many.append(i.name)
	duration = timedelta(minutes=(int(event.event_length.split(':')[0]) * 60 + int(event.event_length.split(':')[1])))

	tz = pytz.timezone('US/' + event.timezone)

	startInDateTime = tz.localize(datetime.strptime(event.start_date + ' ' + event.start_time, '%m/%d/%Y %I:%M %p'))
	endInDateTime = tz.localize(datetime.strptime(event.start_date + ' ' + event.end_time, '%m/%d/%Y %I:%M %p'))
	finalEndDateTime = tz.localize(datetime.strptime(event.end_date + ' ' + event.end_time, '%m/%d/%Y %I:%M %p'))

	if startInDateTime > endInDateTime:
		endInDateTime += timedelta(days=1)
		#finalEndDateTime += timedelta(days=1)
		
	times = cal.findTimeForMany(many, startInDateTime, endInDateTime, finalEndDateTime, duration)

	# 15 minute intervals for starting time; rounding start time; etc.
	processedTimes = []
	for t in times:
		roundBy = roundUpByTimeDelta(t['startTime'])
		startEvent = t['startTime']

		# Ignore all the possible times that have occurred in the past
		while startEvent < datetime.now(tz) and startEvent + duration <= t['endTime']:
			startEvent += timedelta(minutes=roundToMin)
		if startEvent < datetime.now(tz): # If all of the possible times in this interval have occured in the past, ignore this interval
			continue
		endEvent = startEvent + duration

		# if rounding makes the event go beyond endtime, then just add the time range and call it good.
		if startEvent + roundBy + duration > finalEndDateTime:
			priorityValue = -int(t['numFree'])*1000
			needToContinue = False
			for d in processedTimes: # Check if we have already added the possible times list to prevent duplicates
				if d['endTime'] == endEvent and d['startTime'] == startEvent:
					if d['priority'] > priorityValue:
						d['participants'] = t['participants']
						d['numFree'] = t['numFree']
						d['priority'] = priorityValue
					needToContinue = True
					break
			if needToContinue:
				continue
			processedTimes.append({'priority':priorityValue, 'startTime':startEvent, 'endTime':endEvent, 'numFree':t['numFree'], 'participants':t['participants']})
			continue
		else:
			# Iterate over the time range, adding 15 minutes every time
			i = 0
			while endEvent <= t['endTime']:
				priorityValue = -int(t['numFree'])*1000 + i
				needToContinue = False
				for d in processedTimes: # Check if we have already added the possible times list to prevent duplicates
					if d['endTime'] == endEvent and d['startTime'] == startEvent:
						if d['priority'] > priorityValue:
							d['participants'] = t['participants']
							d['numFree'] = t['numFree']
							d['priority'] = priorityValue
						needToContinue = True
						break
				if not needToContinue:
					processedTimes.append({'priority':priorityValue, 'startTime':startEvent, 'endTime':endEvent, 'numFree':t['numFree'], 'participants':t['participants']})
				i += 1
				startEvent += timedelta(minutes=roundToMin)
				endEvent = startEvent + duration

	# Now consider vetoed times
	for t in processedTimes:
		for vetoed in event.vetotime_set.filter(startTime=t['startTime']): # For each vetoed time, remove that user from the list that can make it
			if t['participants'].find(vetoed.invitee.name) > -1:
				t['participants'] = t['participants'].replace(', ' + vetoed.invitee.name, '')
				t['participants'] = t['participants'].replace(vetoed.invitee.name + ', ', '')
				t['numFree'] -= 1
				t['priority'] += 1000

	# Sort the possible times by priority measure
	processedTimes = sorted(processedTimes, key=lambda k: k['priority'])

	#Delete all previous possTimes and add the new ones
	event.posstime_set.all().delete()

	for t in processedTimes:
		possTime = PossTime(startTime=t['startTime'], endTime=t['endTime'], nFree=t['numFree'], peopleList=t['participants'])
		event.posstime_set.add(possTime)
	return HttpResponseRedirect('/' + eventID)

#creator can boot someone, delete/skedge/getTimes on event.
@login_required
def manageCreator(request):
	eventID = request.POST['eventID']
	event = get_object_or_404(Instance, eventID=eventID)
	if request.user.username != event.creator: #If someone tried to artificially generate a request to do creator only options, do nothing
		return HttpResponseRedirect('/')

	if 'boot' in request.POST: # Creator wants to boot some malicious user from their event
		i_name = request.POST['invitee_name']
		invitee = event.invitee_set.get(name=i_name)
		invitee.delete()

		# Give notification to the booted user that they've been booted
		n = Notification(desc=event.title, originUserName=event.creator, notificationType="bootNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		u = get_object_or_404(User, username=i_name)
		u.notification_set.add(n)
		u.save()

		return getTimes(request)

	if 'delete' in request.POST: # Creator wants to delete their event
		return delete(request)
	if 'skedg' in request.POST:	# Creator wants to schedule their event	
		invitees = event.invitee_set.all()
		peopleList = []

		# Add notification that the event has been scheduled
		n = Notification(desc=event.title, originUserName=event.creator, notificationType="skedgNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for i in invitees:
			peopleList.append(i.name)
			u = get_object_or_404(User, username=i.name)
			u.notification_set.add(n)
			u.save()

		# Add the scheduled time into everyone's calendar
		peopleList.append(event.creator)
		possIndex=int(request.POST['skedgeTime'])
		possEvents = event.posstime_set.all()
		start = possEvents.get(id=possIndex).startTime
		end = possEvents.get(id=possIndex).endTime
		cal.putTimeForMany(usernameList=peopleList, eventName=event.title, startInDateTime=start, endInDateTime=end, organizer=event.creator, location=None,description=event.desc)
		messages.success(request, 'Your event has been successfully skedged!')

		for time in event.posstime_set.all():
			time.delete()
		
		event.is_scheduled = True
		event.scheduled_start = start
		event.scheduled_end = end
		event.save()
		
		return HttpResponseRedirect('/' + eventID)

	return HttpResponseRedirect('/')

#user can join, remove self, and vote
@login_required
def manageInvitee(request):
	# Get user/event information
	eventID = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, eventID=eventID)
	username = request.POST['username']
	firstName = request.POST['firstName']
	lastName = request.POST['lastName']

	if 'join' in request.POST: # If the user wants join the event
		invitee = Invitee(name=username, firstName=firstName, lastName=lastName)
		event.invitee_set.add(invitee)

		# Notify the creator that someone joined the event
		n = Notification(desc=event.title, originUserName=username, notificationType="joinNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		if not event.is_scheduled:
			return getTimes(request)
		else:
			return HttpResponseRedirect('/' + eventID)

	if 'decline' in request.POST: # If the user wants to leave the event
		inviteeSet = event.invitee_set.all()
		invitee = inviteeSet.get(name=username)
		invitee.delete()

		# Notify the creator that someone has left his event
		n = Notification(desc=event.title, originUserName=username, notificationType="leaveNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		if not event.is_scheduled: # Update the possible times since someone left
			return getTimes(request)
		else:
			return HttpResponseRedirect('/' + eventID)
	if 'veto' in request.POST: # Handle the case if the user added a conflict
		return vetoPoss(request)

# Manage the message board
@login_required
def manageMessage(request):
	eventID = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, eventID=eventID)
	postAuthor = request.POST['username']

	if 'write' in request.POST: # Someone posted on the message board
		postFirstName = request.POST['firstName']
		postLastName = request.POST['lastName']
		message = request.POST['message']
		if message.replace(' ', '') == '': # Ignore blank message postings
			return HttpResponseRedirect('/' + eventID)
		author = postAuthor
		pub_date = datetime.now()

		message = Message(text=message, author=author, pub_date=pub_date, firstName=postFirstName, lastName=postLastName)
		event.message_set.add(message)

		# Notify the other people in the event that someone has posted on the message board
		n = Notification(desc=event.title, originUserName=postAuthor, notificationType="composeNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for i in event.invitee_set.all():
			if i.name == postAuthor:
				continue
			u = get_object_or_404(User, username=i.name)
			u.notification_set.add(n)
			u.save()

		if postAuthor != event.creator:
			u2 = get_object_or_404(User, username=event.creator)
			u2.notification_set.add(n)
			u2.save()

	if 'erase' in request.POST: #delete message by the event creator
		message = get_object_or_404(Message, pk=request.POST['messageID'])
		
		# Tell message creator that his message has been deleted
		n = Notification(desc=event.title, originUserName=event.creator, notificationType="eraseNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		if message.author != event.creator: #If event creator is deleting his own message, no notification.
			user = get_object_or_404(User, username=message.author)
			user.notification_set.add(n)
			user.save()
		
		message.delete()
	
	return HttpResponseRedirect('/' + eventID)

# Handle notification requests
@login_required
def manageNotification(request):
	if 'dismiss' in request.POST: # Delete a single notification
		n_id = request.POST['notificationID']
		notification = get_object_or_404(Notification, pk=n_id)
		notification.delete()
	if 'clear' in request.POST: # Delete all notifications
		user = get_object_or_404(User, username=request.POST['username'])
		for n in user.notification_set.all():
			n.delete()

	return HttpResponseRedirect('/')
	
# Handle registration from the event detail page
def register(request):
	context = RequestContext(request)
	first_name = request.POST['first_name']
	last_name = request.POST['last_name']
	email = request.POST['username']
	saveInfo = {'first_name':first_name, 'last_name':last_name, 'email':email}

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		if user_form.is_valid(): # Check the form for any errors (done in forms.py)
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = UserProfile.objects.create(user=user)

			# Get the validation key that they need to click within 48 hours
			keyLength = 10

			key = get_random_string(length=keyLength)
			while UserProfile.objects.filter(activation_key__iexact=key).count() != 0:
				key = get_random_string(length=keyLength)
			profile.activation_key = key

			profile.save()

			#Send email with validation key
			msg = '''Hi %s, 
Thanks for signing up. Click this link within 48 hours to prevent your account from being deactivated:
http://www.skedg.tk:82/confirm/%s''' % (user.first_name, key)
			send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
		else:
			# Fill out context of what errors the form had
			errorList = {}
			if user_form.errors.get('username', '') != '':
				errorList.update({'emailError':user_form.errors.get('username', '')[0]})
			if user_form.errors.get('password', '') != '':
				errorList.update({'passwordError':user_form.errors.get('password', '')[0]})
			if user_form.errors.get('password2', '') != '':
				errorList.update({'password2Error':user_form.errors.get('password2', '')[0]})
			if user_form.errors.get('__all__', '') != '':
				errorList.update({'registerError':user_form.errors.get('__all__', '')[0]})
			errorList.update(saveInfo)
			return render_to_response('login.html', errorList, context)

	else:
		user_form = UserForm()

	# Redirect to the home page
	return render_to_response(
			'login.html',
			{'registered': True},
			context)

# Handle registration from the home page
def registerEvent(request):
	context = RequestContext(request)
	first_name = request.POST['first_name']
	last_name = request.POST['last_name']
	email = request.POST['username']
	eventID = request.POST.get('eventID', '')
	event = get_object_or_404(Instance, eventID=eventID)
	saveInfo = {'first_name':first_name, 'last_name':last_name, 'email':email, 'event':event}
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		if user_form.is_valid():# Check the form for any errors (done in forms.py)
			user = user_form.save()
			#user.is_active = False
			user.set_password(user.password)
			user.save()
			profile = UserProfile.objects.create(user=user)

			# Get the validation key that they need to click within 48 hours
			keyLength = 10

			key = get_random_string(length=keyLength)
			while UserProfile.objects.filter(activation_key__iexact=key).count() != 0:
				key = get_random_string(length=keyLength)
			profile.activation_key = key

			profile.save()
			registered = True

			#Send email with validation key
			msg = '''Hi %s, 
Thanks for signing up. Click this link within 48 hours to prevent your account from being deactivated:
http://www.skedg.tk:82/confirm/%s''' % (user.first_name, key)
			send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
		else:
			# Fill out context of what errors the form had
			errorList = {}
			if user_form.errors.get('username', '') != '':
				errorList.update({'emailError':user_form.errors.get('username', '')[0]})
			if user_form.errors.get('password', '') != '':
				errorList.update({'passwordError':user_form.errors.get('password', '')[0]})
			if user_form.errors.get('password2', '') != '':
				errorList.update({'password2Error':user_form.errors.get('password2', '')[0]})
			if user_form.errors.get('__all__', '') != '':
				errorList.update({'registerError':user_form.errors.get('__all__', '')[0]})
			errorList.update(saveInfo)
			return render_to_response('detail.html', errorList, context)

	else:
		user_form = UserForm()

	# Redirect back to the event page that they were looking at
	return render_to_response(
			'detail.html',
			{'registered': registered, 'event':event},
			context)

# Called when the user wants to change which Google calendar they use
@login_required
def resetGAuth(request):
	username = request.user.username
	return cal.getCredClient(username, eventID=None)

# User clicked link to register their email
def register_confirm(request, activation_key):
	user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

	# Activate the user if necessary
	if user_profile.activated:
		return HttpResponseRedirect('/')
	user_profile.activated = True
	user_profile.activation_key = ''
	user_profile.save()
	user_profile.user.is_active = True
	user_profile.user.save()
	messages.success(request, "Your account has been successfully activated!")
	return HttpResponseRedirect('/')

# Handle what html page is rendered when the user clicks "My Account"
@login_required
def userPage(request):
	return render(request, 'user.html')

# Handle logging in from the home page
def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		email = request.POST.get('username', '')
		password = request.POST.get('password', '')

		user = authenticate(username=email, password=password)

		if user:
			# If the user still hasn't clicked on email verification email after 48 hours, block their account
			if not user.UserProfile.activated and user.date_joined + timedelta(days=2) < datetime.now(pytz.timezone('utc')):
				user.is_active = False

			if user.is_active:
				# Get their google calendar information if we don't have it already
				resp = cal.validateToken(email)
				if (resp =="Already Has Token"):
					login(request, user)
					return HttpResponseRedirect('/')
				return resp
			else:
				# Resend verification email if they haven't clicked it yet
				msg = '''Hi %s, 
Thanks for signing up. Click this link within 48 hours to prevent your account from being deactivated:
http://www.skedg.tk:82/confirm/%s''' % (user.first_name, user.UserProfile.activation_key)
				send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
				return render(request, 'login.html', {'invalidLogin':"Please activate your account through the link in the email we sent.", 'username': email})
		else:
			return render(request, 'login.html', {'invalidLogin':"Invalid login details supplied.", 'username': email})

	else:
		return render_to_response('login.html', {}, context)

# Handle logging in from the view event Detail page
def user_loginEvent(request):
	context = RequestContext(request)

	if request.method == 'POST':
		email = request.POST.get('username', '')
		password = request.POST.get('password', '')
		eventID = request.POST.get('eventID', '')

		user = authenticate(username=email, password=password)

		if user:
			# If the user still hasn't clicked on email verification email after 48 hours, block their account
			if not user.UserProfile.activated and user.date_joined + timedelta(days=2) < datetime.now(pytz.timezone('utc')):
				user.is_active = False

			if user.is_active:
				# Get their google calendar information if we don't have it already
				resp = cal.validateToken(email,eventID)
				if (resp =="Already Has Token"):
					login(request, user)
					return HttpResponseRedirect('/' + eventID)
				return resp
			else:
				# Resend verification email if they haven't clicked it yet
				event = get_object_or_404(Instance, eventID=eventID)
				msg = '''Hi %s, 
Thanks for signing up. Click this link within 48 hours to prevent your account from being deactivated:
http://www.skedg.tk:82/confirm/%s''' % (user.first_name, user.UserProfile.activation_key)
				send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
				return render(request, 'detail.html', {'invalidLogin':"Please activate your account through the link in the email we sent.", 'username': email, 'event':event})
		else:
			event = get_object_or_404(Instance, eventID=eventID)
			return render(request, 'detail.html', {'invalidLogin':"Invalid login details supplied.", 'username': email, 'event':event})

	else:
		return render_to_response('detail.html', {}, context)

# Logout the user and redirect to the login page
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')

# Handles when an invitee to an event adds a conflict
def vetoPoss(request):
	eventID = request.POST['eventID']
	event = get_object_or_404(Instance, eventID=eventID)
	invitee = event.invitee_set.all().get(name=request.POST['username'])
	invitee.hasVoted = True
	invitee.save()
	possTimes = event.posstime_set.all()
	requestTimes = [int(x) for x in request.POST.getlist('vetoTimes')]
	for pID in requestTimes:
		p = possTimes.get(id=pID)
		needToContinue = False
		for x in event.vetotime_set.all(): # Check if the user has already vetoed this time to prevent duplicates
			if x.startTime == p.startTime and x.endTime == p.endTime and x.invitee == invitee:
				needToContinue = True
				break
		if needToContinue:
			continue
		vetoTime = VetoTime(event=event, invitee=invitee, startTime=p.startTime, endTime=p.endTime)
		vetoTime.save()

	# Refind the best times given the new conflict
	return getTimes(request)
