from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from .models import Instance, Invitee, Notification, PossTime, UserProfile
from .forms import UserForm, UserProfileForm
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import *
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

def detail(request, instance_id):
	event = get_object_or_404(Instance, pk=instance_id)
	return render(request, 'events/detail.html', {'event': event})

@login_required
def add(request):
	title=request.POST.get('title', '')
	desc=request.POST.get('desc', '')
	start_date=request.POST.get('start_date', '')
	end_date=request.POST.get('end_date', '')
	start_time=request.POST.get('start_time', '')
	end_time=request.POST.get('end_time', '')
	creator=request.POST.get('creator', '')

	is_scheduled=False
	e = Instance(title=title, desc=desc, start_date=start_date, end_date=end_date, 
		start_time=start_time, end_time=end_time, creator=creator)

	#try catch here check validity
	try:
		e.save()
	except ValidationError as e:
		latest_event_list = Instance.objects.order_by('-pub_date')[:100]
		return render(request, 'events/index.html', {'error': e[0], 'latest_event_list': latest_event_list,
			'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'start_time':start_time,
			'end_time':end_time, 'creator':creator, 'invitees':request.POST.get('invitees', '')})
	#return HttpResponseRedirect(reverse('events:results', args=(e.id,)))

	#nstr = e.creator + " has invited you to " + e.title + "!" 
	#n = Notification(desc=nstr, pub_date=datetime.now())
	invitees = [x for x in request.POST.get('invitees', '').split(', ') if x.replace(' ', '') != '']
	for i in invitees:
		try:
			User.objects.get(username = i)
		except User.DoesNotExist as e:
			latest_event_list = Instance.objects.order_by('-pub_date')[:100]
			msg = 'User: %s, does not exist' % i
			return render(request, 'events/index.html', {'error': msg, 'latest_event_list': latest_event_list,
				'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'start_time':start_time,
				'end_time':end_time, 'creator':creator, 'invitees':request.POST.get('invitees', '')})
	for i in invitees:
		newInvitee = Invitee(name=i, userID=User.objects.get(username=i).id, rsvpAccepted=False)
		e.invitee_set.add(newInvitee)
		emailTitle = '%s Has Invited You To %s!' % (e.creator, e.title)
		emailMsg = 'Login and respond!'
		send_mail(emailTitle, emailMsg, 'skedg.notify@gmail.com', [User.objects.get(username=i).email], fail_silently=False)

	#	user = User.objects.get(username=i)
	#	user.notification_set.add(n)
	return HttpResponseRedirect('/events/')

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
	e_id = request.POST['eventID']
	event = get_object_or_404(Instance, pk=e_id)

	ntstr = event.creator + " has cancelled " + event.title
	n = Notification(desc=ntstr, pub_date=datetime.now())

	for invitee in event.invitee_set.all():
		user = get_object_or_404(User, username=invitee.name)
		user.notification_set.add(n)
		user.save()

	event.delete()
	return HttpResponseRedirect('/events/')

def deleteInvitee(request):
	return index(request)

def manageCreator(request):
	if 'delete' in request.POST:
		return delete(request)
	if 'getTimes' in request.POST:
		e_id = request.POST['eventID']
		event = get_object_or_404(Instance, pk=e_id)
		event.is_scheduled = True
		event.save()
		
		many = []
		many.append(event.creator)

		for i in event.invitee_set.all():
			many.append(i.name)

	
		#TEMPORARY
		startTime = datetime.strptime(event.start_date + ' ' + event.start_time, '%m/%d/%Y %I:%M %p')
		endTime = datetime.strptime(event.end_date + ' ' + event.end_time, '%m/%d/%Y %I:%M %p')
		startTime = startTime.strftime('%Y-%m-%dT%H:%M:00-04:00')
		endTime = endTime.strftime('%Y-%m-%dT%H:%M:00-04:00')
		#The error is here: "access_token" error when I try to call findTimeForMany.
		times = cal.findTimeForMany(many, timeStart=startTime, timeEnd=endTime, duration = 3600)
		for t in times:
			possTime = PossTime(startTime=t['startTime'], endTime=t['endTime'], nConflicts=t['conflicts'])
			event.posstime_set.add(possTime)
		#possTime = PossTime()
		#event.posstime_set.add(possTime)

		return index(request)
	else:
		return index(request)

def manageInvitee(request):
	e_id = request.POST.get('eventID', -1)
	event = get_object_or_404(Instance, pk=e_id)

	username = request.POST['username']
	inviteeSet = event.invitee_set.all()
	invitee = inviteeSet.get(name=username)
	
	if 'accept' in request.POST:
		invitee.rsvpAccepted = True
		invitee.save()
		return HttpResponseRedirect('/events/')
	else:
		ntstr = username + " has been removed from " + event.title
		n = Notification(desc=ntstr, pub_date=datetime.now())
		creator = get_object_or_404(User, username=event.creator)
		creator.notification_set.add(n)
		invitee.delete()
		#event.invitee_set = event.invitee_set.all().exclude(name=username)
		return HttpResponseRedirect('/events/')

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

def results(request, instance_id):
	event = get_object_or_404(Question, pk=instance_id)
	return render(request, 'events/results.html', {'event': event})
	
def register(request):
	context = RequestContext(request)
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.is_active = False
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
			'events/register.html',
			{'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
			context)

def register_confirm(request, activation_key):
	if request.user.is_authenticated():
		#User already authenticated
		return HttpResponseRedirect('/events/')
	user_profile = get_object_or_404(UserProfile, activation_key = activation_key)

	user = user_profile.user
	user.is_active=True
	user.save()
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