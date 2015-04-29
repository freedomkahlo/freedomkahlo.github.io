from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from .models import Instance, Invitee, Notification, PossTime, UserProfile
from .forms import UserForm, UserProfileForm
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import *
from heapq import *
import json
import hashlib, random
from backend import cal

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
	return render(request, 'events/detail.html', {'event': event})

@login_required
def add(request):	
	title=request.POST.get('title', '')
	desc=request.POST.get('desc', '')
	start_date=request.POST.get('start_date', '')
	end_date=request.POST.get('end_date', '')
	time_range=request.POST.get('time_range', '')
	event_length=request.POST.get('event_length', '')
	creator = request.POST['username']
	eventID = get_random_string(length=32)

	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	returnMsg = {'error': '', 'latest_event_list': latest_event_list,
			'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'time_range':time_range,
			'event_length':event_length, 'creator':creator}

	is_scheduled=False
	if (time_range == ''):
		returnMsg['error'] = 'Time Range Cannot Be Blank'
		return render(request, 'events/index.html', returnMsg)

	#Parse the time range
	timeSplit = event_length.split()
	if len(timeSplit) == 4: #both hours and minutes
		event_length = timeSplit[0] + ':' + timeSplit[2]
	elif timeSplit[1][0] == 'h': #only hours
		event_length = timeSplit[0] + ':0'
	else:
		event_length = '0:' + timeSplit[0]
	e = Instance(title=title, desc=desc, start_date=start_date, end_date=end_date, 
		start_time=time_range.split('-')[0], end_time=time_range.split('-')[1], event_length=event_length, creator=creator, eventID=eventID)

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
	messages.success(request, 'Your event has been successfully created! The event url to share is skedg.tk/events/eventDetails/' + eventID)
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

	ntstr = event.creator + " has cancelled " + event.title
	n = Notification(desc=ntstr, pub_date=datetime.now())

	for invitee in event.invitee_set.all():
		user = get_object_or_404(User, username=invitee.name)
		user.notification_set.add(n)
		user.save()

	event.delete()
	return HttpResponseRedirect('/events/')

def getTimes(request, eventID=None):
	roundToMin = 15 #minutes


	def roundUpByTimeDelta(dt, roundTo = roundToMin * 60):
		"""Round a datetime object to any time laps in seconds
		dt : datetime.datetime object, default now.
		roundTo : Closest number of seconds to round up to, default 15 minutes.
		"""
		seconds = (dt - dt.min).seconds
		# // is a floor division, not a comment on following line:
		rounding = (seconds+roundTo) // roundTo * roundTo
		return timedelta(0,rounding-seconds,-dt.microsecond)

	if eventID == None:
		eventID = request.POST['eventID']

	event = get_object_or_404(Instance, eventID=eventID)

	event.is_scheduled = True
	event.save()

	many = []
	many.append(event.creator)

	for i in event.invitee_set.all():
		many.append(i.name)
	duration = int(event.event_length.split(':')[0]) * 3600 + int(event.event_length.split(':')[1]) * 60

	#TEMPORARY: fixed time zone
	startInDateTime = datetime.strptime(event.start_date + ' ' + event.start_time, '%m/%d/%Y %I:%M %p')
	if startInDateTime < datetime.now():
		startInDateTime = datetime.now()
	endInDateTime = datetime.strptime(event.start_date + ' ' + event.end_time, '%m/%d/%Y %I:%M %p')
	finalEndDateTime = datetime.strptime(event.end_date + ' ' + event.end_time, '%m/%d/%Y %I:%M %p')
	
	times = cal.findTimeForMany(many, startInDateTime, endInDateTime, finalEndDateTime, duration)
	
	print times
	# 30 minute intervals for starting time; rounding start time; etc.
	processedTimes = []
	for t in times:
		roundBy = roundUpByTimeDelta(t['startTime'])
		startEvent = t['startTime']
		# if rounding makes the event go beyond endtime, then just add the time range and call it good.
		#print (startEvent + roundBy).strftime('%Y-%m-%dT%H:%M')
		if startEvent + roundBy + timedelta(seconds=duration) > endInDateTime:
			endEvent = startEvent + timedelta(seconds=duration)
			priorityValue = int(t['conflicts'])*1000
			processedTimes.append({'priority':priorityValue, 'startTime':startEvent, 'endTime':endEvent, 'conflicts':t['conflicts']})
			continue
		else:
			startEvent += timedelta(minutes=roundToMin)
			endEvent = startEvent + timedelta(seconds=duration)
			i = 0
			while endEvent < t['endTime']:
				priorityValue = int(t['conflicts'])*1000 + i
				processedTimes.append({'priority':priorityValue, 'startTime':startEvent, 'endTime':endEvent, 'conflicts':t['conflicts']})
				i += 1
				startEvent += timedelta(minutes=roundToMin)
				endEvent = startEvent + timedelta(seconds=duration)
	#list.sort(processedTimes)
	processedTimes = sorted(processedTimes, key=lambda k: k['priority'])

	event.posstime_set.clear()
	for t in processedTimes:
		possTime = PossTime(startTime=t['startTime'], endTime=t['endTime'], nConflicts=t['conflicts'])
		event.posstime_set.add(possTime)
	#possTime = PossTime()
	#event.posstime_set.add(possTime)

	print "almost there!"
	return detail(request, eventID)
	
#creator can boot someone, delete/skedge/getTimes on event.
def manageCreator(request):
	if 'boot' in request.POST:
		eventID = request.POST['eventID']
		event = get_object_or_404(Instance, eventID=eventID)
		i_name = request.POST['invitee_name']
		invitee = get_object_or_404(Invitee, name=i_name)
		invitee.delete();
		getTimes(request)

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
		ntstr = event.creator + " has skedged " + event.title + " and it has been added to your calendar! GG, everyone."
		n = Notification(desc=ntstr, pub_date=datetime.now())
		
		for i in invitees:
			peopleList.append(i.name)
			u = get_object_or_404(User, username=i.name)
			u.notification_set.add(n)
		peopleList.append(event.creator)
		possIndex=int(request.POST['skedgeTime'])
		possEvents = event.posstime_set.all()
		start = possEvents.get(id=possIndex).startTime
		end = possEvents.get(id=possIndex).endTime
		cal.putTimeForMany(usernameList=peopleList, eventName=event.title, startInDateTime=start, endInDateTime=end, organizer=event.creator, location=None,description=event.desc)
		messages.success(request, 'Your event has been successfully skedged!')
		event.delete()
		return HttpResponseRedirect('/events/')
	else:
		return index(request)

#user can join, remove self, and vote
def manageInvitee(request):
	eventID = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, eventID=eventID)
	username = request.POST['username']

	print request.POST

	if 'join' in request.POST:
		if (len(event.invitee_set.filter(name = username)) > 0):
			messages.success(request, "You already part of the party, yo.")
			return detail(request, eventID)
		else:
			invitee = Invitee(name=username)
			event.invitee_set.add(invitee)
			return getTimes(request)
	if 'decline' in request.POST:
		if (len(event.invitee_set.filter(name = username)) > 0):
			# commenting out notification for now
			#ntstr = username + " has been removed from " + event.title
			#n = Notification(desc=ntstr, pub_date=datetime.now())
			#creator = get_object_or_404(User, username=event.creator)
			#creator.notification_set.add(n)

			inviteeSet = event.invitee_set.all()
			invitee = inviteeSet.get(name=username)
			invitee.delete()
			return getTimes(request)
		#event.invitee_set = event.invitee_set.all().exclude(name=username)
		else:
			messages.success(request, "You were not invited, foo.")
			return detail(request, eventID)
			#return detail(request, e_id)
	if 'vote' in request.POST:
		invitee.hasVoted = True
		invitee.save()
		return vetoPoss(request)	

def manageNotification(request):
	if 'dismiss' in request.POST:
		n_id = request.POST['notificationID']
		notification = get_object_or_404(Notification, pk=n_id)
		notification.delete()
	if 'clear' in request.POST:
		user = get_object_or_404(User, username=request.POST['username'])
		for n in user.notification_set.all():
			n.delete()

	return HttpResponseRedirect('/events/')

def results(request, eventID):
	event = get_object_or_404(Question, eventID=eventID)
	return render(request, 'events/results.html', {'event': event})
	
def register(request):
	context = RequestContext(request)
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

			email = user.email
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

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
			'events/login.html',
			{'registered': registered},
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
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				resp = cal.validateToken(username)
				if (resp != None):
					return resp
				return HttpResponseRedirect('/events/')
			else:
				return HttpResponse("Your Skedge account is disabled.")
		else:
			print ("Invalid login details: {0}, {1}".format(username, password))
			return render(request, 'events/login.html', {'invalidLogin':"Invalid login details supplied.", 'username': username})

	else:
		return render_to_response('events/login.html', {}, context)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/events/')

def vetoPoss(request):
	eventID = request.POST['eventID']
	event = get_object_or_404(Instance, eventID=eventID)
	possTimes = event.posstime_set.all()
	requestTimes = [int(x) for x in request.POST.getlist('vetoTimes')]
	for pID in requestTimes:
		p = possTimes.get(id=pID)
		p.nConflicts += 1
		p.save()
	return HttpResponseRedirect('/events/')
