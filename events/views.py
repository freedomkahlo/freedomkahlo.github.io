from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from .models import Instance, Invitee, Notification, PossTime, UserProfile, VetoTime, Message
from .forms import UserForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import timedelta, datetime
import json
import hashlib, random
from backend import cal
import pytz
import math


def home(request):
	return render(request, './index.html')

@login_required
def index(request):
	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	user_list = User.objects.all()
#	latest_event_list = [event in latest_event_list if event.creator is request.user.username]
	context = {'latest_event_list': latest_event_list, 'user_list': user_list}
	request.path_info = '/events/'
	return render(request, 'events/index.html', context)

#@login_required
def detail(request, eventID):
	event = get_object_or_404(Instance, eventID=eventID)
	resp = deletePastPossTimes(request, eventID)
	if resp: #If event was deleted
		return resp
	return render(request, 'events/detail.html', {'event': event})

@login_required
def add(request):	
	title=request.POST.get('title', '')
	desc=request.POST.get('desc', '')
	start_date=request.POST.get('start_date', '')
	end_date=request.POST.get('end_date', '')
	start_time=request.POST.get('start_time', '')
	end_time=request.POST.get('end_time', '')
	event_length=request.POST.get('event_length', '')
	creator = request.POST['username']
	timezone = request.POST.get('timezone', 'Eastern')
	eventID = get_random_string(length=32)

	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	returnMsg = {'error': '', 'latest_event_list': latest_event_list,
			'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'start_time':start_time,
			'end_time':end_time, 'event_length':event_length, 'creator':creator, 'timezone':timezone}

	#5/3/2015 2:00 PM
	#startTmp = time_range.split('-')[0].split(':')
	#startHour = startTmp[0]
	#startMin = startTmp[1].split()[0]

	#if (startTmp[1].split()[1] == 'PM')
	#	startHour = int(startHour) + 12

	#startDateTimeString = start_date + "," + startHour + ":" + startMin
	#startDateTime = datetime.strptime(startDateTimeString, '%Y/%m/%d,%H:%M.%fZ')
	#print startDateTime
	#if (startDateTime < datetime.now()):
	#	returnMsg['error'] = 'Event start time cannot be in the past.'
	#	return render(request, 'events/index.html', returnMsg)

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
		return render(request, 'events/index.html', returnMsg)
	#return HttpResponseRedirect(reverse('events:results', args=(e.id,)))

	#nstr = e.creator + " has invited you to " + e.title + "!" 
	#n = Notification(desc=nstr, pub_date=datetime.now())

	#	user = User.objects.get(username=i)
	#	user.notification_set.add(n)
	#messages.success(request, 'Your event has been successfully created! The event url to share is skedg.tk/events/eventDetails/' + eventID)
	return getTimes(request, eventID)

def autocomplete_user(request):
    term = request.GET.get('term') #jquery-ui.autocomplete parameter
    users = User.objects.filter(username__istartswith=term) #lookup for a city
    res = []
    for c in users:
         #make dict with the metadatas that jquery-ui.autocomple needs (the documentation is your friend)
         dict = {'id':c.id, 'label':c.__unicode__(), 'value':c.__unicode__()}
         res.append(dict)
    return HttpResponse(json.dumps(res))

def delete(request):
	eventID = request.POST['eventID']
	event = get_object_or_404(Instance, eventID=eventID)

	n = Notification(desc=event.title, notificationType="deleteNot", originUserName =event.creatorName, pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

	for invitee in event.invitee_set.all():
		user = get_object_or_404(User, username=invitee.name)
		user.notification_set.add(n)
		user.save()

	event.delete()
	return HttpResponseRedirect('/events/')

def deletePastPossTimes(request, eventID=None):
	if eventID == None:
		eventID = request.POST['eventID']

	event = get_object_or_404(Instance, eventID=eventID)
	tz = pytz.timezone('US/' + event.timezone)

	possTimes = event.posstime_set.all()
	badPossTimes = [x for x in possTimes if x.startTime < datetime.now(tz)]

	for x in badPossTimes:
		x.delete()

	vetoTimes = event.vetotime_set.all()
	badVetoTimes = [x for x in vetoTimes if x.startTime < datetime.now(tz)]

	for x in badVetoTimes:
		x.delete()

	if len(event.posstime_set.all()) == 0 and not event.is_scheduled:
		#Need to delete event
		n = Notification(desc=event.title, notificationType="noTimeNot", originUserName =event.creatorName, pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for invitee in event.invitee_set.all():
			user = get_object_or_404(User, username=invitee.name)
			user.notification_set.add(n)
			user.save()

		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		event.delete()
		return HttpResponseRedirect('/events/')

def getTimes(request, eventID=None):
	roundToMin = 15 #minutes

	def roundUpByTimeDelta(tm):
		upmins = math.ceil(float(tm.minute)/15)*15 #round up to nearest 15 minutes
		diffmins = upmins - tm.minute
		return timedelta(minutes=diffmins)

	if eventID == None:
		eventID = request.POST['eventID']

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
		finalEndDateTime += timedelta(days=1)
		
	times = cal.findTimeForMany(many, startInDateTime, endInDateTime, finalEndDateTime, duration)
	print 'Gotten Times:', times
	# 30 minute intervals for starting time; rounding start time; etc.
	processedTimes = []
	for t in times:
		roundBy = roundUpByTimeDelta(t['startTime'])
		startEvent = t['startTime']
		while startEvent < datetime.now(tz) and startEvent + duration <= t['endTime']:
			startEvent += timedelta(minutes=roundToMin)
		if startEvent < datetime.now(tz):
			continue
		endEvent = startEvent + duration
		# if rounding makes the event go beyond endtime, then just add the time range and call it good.
		#print (startEvent + roundBy).strftime('%Y-%m-%dT%H:%M')
		if startEvent + roundBy + duration > finalEndDateTime:
			priorityValue = -int(t['numFree'])*1000
			needToContinue = False
			for d in processedTimes:
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
			if len(event.vetotime_set.filter(startTime=startEvent)) > 0:
				for vetoed in event.vetotime_set.filter(startTime=t['startTime']):
					if processedTimes[-1]['participants'].find(vetoed.invitee.name) > -1:
						processedTimes[-1]['participants'] = processedTimes[-1]['participants'].replace(', ' + vetoed.invitee.name, '')
						processedTimes[-1]['participants'] = processedTimes[-1]['participants'].replace(vetoed.invitee.name + ', ', '')
						processedTimes[-1]['numFree'] -= 1
						processedTimes[-1]['priority'] += 1000
			continue
		else:
			i = 0
			while endEvent <= t['endTime']:
				priorityValue = -int(t['numFree'])*1000 + i
				needToContinue = False
				for d in processedTimes:
					if d['endTime'] == endEvent and d['startTime'] == startEvent:
						if d['priority'] > priorityValue:
							d['participants'] = t['participants']
							d['numFree'] = t['numFree']
							d['priority'] = priorityValue
						needToContinue = True
						break
				if not needToContinue:
					processedTimes.append({'priority':priorityValue, 'startTime':startEvent, 'endTime':endEvent, 'numFree':t['numFree'], 'participants':t['participants']})
					if len(event.vetotime_set.filter(startTime=startEvent)) > 0:
						for vetoed in event.vetotime_set.filter(startTime=t['startTime']):
							if processedTimes[-1]['participants'].find(vetoed.invitee.name) > -1:
								processedTimes[-1]['participants'] = processedTimes[-1]['participants'].replace(', ' + vetoed.invitee.name, '')
								processedTimes[-1]['participants'] = processedTimes[-1]['participants'].replace(vetoed.invitee.name + ', ', '')
								processedTimes[-1]['numFree'] -= 1
								processedTimes[-1]['priority'] += 1000
				i += 1
				startEvent += timedelta(minutes=roundToMin)
				endEvent = startEvent + duration
	#list.sort(processedTimes)
	processedTimes = sorted(processedTimes, key=lambda k: k['priority'])
	print 'Processed:'
	for t in processedTimes:
		t['startTime'].isoformat() + ' ' + t['endTime'].isoformat() + ' ' + t['participants'] + ' ' + str(t['priority'])

	#Delete all previous possTimes 
	event.posstime_set.all().delete()

	for t in processedTimes:
		possTime = PossTime(startTime=t['startTime'], endTime=t['endTime'], nFree=t['numFree'], peopleList=t['participants'])
		event.posstime_set.add(possTime)
	#possTime = PossTime()
	#event.posstime_set.add(possTime)

	print "almost there!"
	return HttpResponseRedirect('/events/eventDetails/' + eventID)
	
#creator can boot someone, delete/skedge/getTimes on event.
def manageCreator(request):
	if 'boot' in request.POST:
		eventID = request.POST['eventID']
		event = get_object_or_404(Instance, eventID=eventID)
		i_name = request.POST['invitee_name']
		invitee = event.invitee_set.get(name=i_name)
		invitee.delete()

		n = Notification(desc=event.title, originUserName=event.creator, notificationType="bootNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		u = get_object_or_404(User, username=i_name)
		u.notification_set.add(n)
		u.save()

		return getTimes(request)

	if 'delete' in request.POST:
		return delete(request)
	if 'getTimes' in request.POST:
		return getTimes(request)
	if 'skedg' in request.POST:			
		eventID = request.POST['eventID']
		event = get_object_or_404(Instance, eventID=eventID)
		invitees = event.invitee_set.all()
		peopleList = []

		#add notification
		n = Notification(desc=event.title, originUserName=event.creator, notificationType="skedgNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for i in invitees:
			peopleList.append(i.name)
			u = get_object_or_404(User, username=i.name)
			u.notification_set.add(n)
			u.save()

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
		
		return HttpResponseRedirect('/events/eventDetails/' + eventID)
	else:
		return index(request)

#user can join, remove self, and vote
def manageInvitee(request):
	eventID = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, eventID=eventID)
	username = request.POST['username']
	firstName = request.POST['firstName']
	lastName = request.POST['lastName']

	print request.POST

	if 'join' in request.POST:
		invitee = Invitee(name=username, firstName=firstName, lastName=lastName)
		event.invitee_set.add(invitee)

		n = Notification(desc=event.title, originUserName=username, notificationType="joinNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		if not event.is_scheduled:
			return getTimes(request)
		else:
			return detail(request, eventID)

	if 'decline' in request.POST:
		inviteeSet = event.invitee_set.all()
		invitee = inviteeSet.get(name=username)
		invitee.delete()

		n = Notification(desc=event.title, originUserName=username, notificationType="leaveNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		user = get_object_or_404(User, username=event.creator)
		user.notification_set.add(n)
		user.save()

		if not event.is_scheduled:
			return getTimes(request)
		else:
			return detail(request, eventID)
		#event.invitee_set = event.invitee_set.all().exclude(name=username)
	if 'veto' in request.POST:
		return vetoPoss(request)	

#user can join, remove self, and vote
def manageMessage(request):
	#print request.POST
	eventID = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, eventID=eventID)
	postAuthor = request.POST['username']

	if 'write' in request.POST:
		postFirstName = request.POST['firstName']
		postLastName = request.POST['lastName']
		message = request.POST['message']
		author = postAuthor
		pub_date = datetime.now()

		message = Message(text=message, author=author, pub_date=pub_date, firstName=postFirstName, lastName=postLastName)
		event.message_set.add(message)

		n = Notification(desc=event.title, originUserName=postAuthor, notificationType="composeNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))

		for i in event.invitee_set.all():
			u = get_object_or_404(User, username=i.name)
			u.notification_set.add(n)
			u.save()

		u2 = get_object_or_404(User, username=event.creator)
		u2.notification_set.add(n)
		u2.save()

	if 'erase' in request.POST:
		message = get_object_or_404(Message, pk=request.POST['messageID'])
		
		n = Notification(desc=event.title, originUserName=event.creator, notificationType="eraseNot", pub_date=datetime.now(pytz.timezone('US/' + event.timezone)))
		user = get_object_or_404(User, username=message.author)
		user.notification_set.add(n)
		user.save()
		message.delete()
	
	return HttpResponseRedirect('/events/eventDetails/' + eventID)

def manageNotification(request):
	print "HI"
	if 'dismiss' in request.POST:
		n_id = request.POST['notificationID']
		notification = get_object_or_404(Notification, pk=n_id)
		notification.delete()
	if 'clear' in request.POST:
		user = get_object_or_404(User, username=request.POST['username'])
		for n in user.notification_set.all():
			n.delete()

	return HttpResponseRedirect('/events/')
	
def register(request):
	context = RequestContext(request)
	first_name = request.POST['first_name']
	last_name = request.POST['last_name']
	email = request.POST['username']
	saveInfo = {'first_name':first_name, 'last_name':last_name, 'email':email}
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			#user.is_active = False
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			email = user.username
			key = hashlib.sha1(str(random.random())).hexdigest()[:5]
			key = hashlib.sha1(key + email).hexdigest()
			profile.activation_key = key

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True

			#Send email with validation key
			msg = '''Hi %s, 
Thanks for signing up. To activate your account, click this link within 48 hours:
http://skedg.tk/events/confirm/%s''' % (user.username, key)
			send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
		else:
			print (user_form.errors, profile_form.errors)
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
			return render_to_response('events/login.html', errorList, context)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
			'events/login.html',
			{'registered': registered},
			context)

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
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			#user.is_active = False
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			email = user.username
			key = hashlib.sha1(str(random.random())).hexdigest()[:5]
			key = hashlib.sha1(key + email).hexdigest()
			profile.activation_key = key

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True

			#Send email with validation key
			msg = '''Hi %s, 
Thanks for signing up. To activate your account, click this link within 48 hours:
http://skedg.tk/events/confirm/%s''' % (user.username, key)
			send_mail('Account confirmation', msg, 'skedg.notify@gmail.com', [email], fail_silently=False)
		else:
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
			return render_to_response('events/detail.html', errorList, context)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
			'events/detail.html',
			{'registered': registered, 'event':event},
			context)

def register_confirm(request, activation_key):
	if request.user.is_authenticated():
		#User already authenticated
		return HttpResponseRedirect('/events/')
	user_profile = get_object_or_404(UserProfile, activation_key = activation_key)

	user = user_profile.user
	user.is_active=True
	user.save()
	messages.success(request, "Your account has been successfully activated!")
	return HttpResponseRedirect('/events/')

def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		email = request.POST.get('username', '')
		password = request.POST.get('password', '')

		user = authenticate(username=email, password=password)

		if user:
			if user.is_active:
				resp = cal.validateToken(email)
				if (resp =="Already Has Token"):
					login(request, user)
					return HttpResponseRedirect('/events/')
				return resp
			else:
				return HttpResponse("Your Skedge account is disabled.")
		else:
			print ("Invalid login details: {0}, {1}".format(email, password))
			return render(request, 'events/login.html', {'invalidLogin':"Invalid login details supplied.", 'username': email})

	else:
		return render_to_response('events/login.html', {}, context)

def user_loginEvent(request):
	context = RequestContext(request)

	if request.method == 'POST':
		email = request.POST.get('username', '')
		password = request.POST.get('password', '')
		eventID = request.POST.get('eventID', '')

		user = authenticate(username=email, password=password)

		if user:
			if user.is_active:
				resp = cal.validateToken(email)
				if (resp =="Already Has Token"):
					login(request, user)
					return HttpResponseRedirect('/events/eventDetails/' + eventID)
				return resp
			else:
				return HttpResponse("Your Skedge account is disabled.")
		else:
			print ("Invalid login details: {0}, {1}".format(email, password))
			event = get_object_or_404(Instance, eventID=eventID)
			return render(request, 'events/detail.html', {'invalidLogin':"Invalid login details supplied.", 'username': email, 'event':event})

	else:
		return render_to_response('events/detail.html', {}, context)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/events/')

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
		for x in event.vetotime_set.all():
			if x.startTime == p.startTime and x.endTime == p.endTime and x.invitee == invitee:
				needToContinue = True
				break
		if needToContinue:
			continue
		vetoTime = VetoTime(event=event, invitee=invitee, startTime=p.startTime, endTime=p.endTime)
		vetoTime.save()
	return getTimes(request)
