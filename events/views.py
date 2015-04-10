from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from .models import Instance, Invitee
from .forms import UserForm, UserProfileForm
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def home(request):
	return render(request, './index.html')

@login_required
def index(request):
	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
#	latest_event_list = [event in latest_event_list if event.creator is request.user.username]
	context = {'latest_event_list': latest_event_list}
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
	e = Instance(title=title, desc=desc, start_date=start_date, end_date=end_date, 
		start_time=start_time, end_time=end_time, creator=creator)
	print (e.title)
	print start_date, end_date, start_time, end_time
	#try catch here check validity
	try:
		e.save()
	except ValidationError as e:
		latest_event_list = Instance.objects.order_by('-pub_date')[:100]
		return render(request, 'events/index.html', {'error': e[0], 'latest_event_list': latest_event_list,
			'title':title, 'desc':desc, 'start_date':start_date, 'end_date':end_date, 'start_time':start_time,
			'end_time':end_time, 'creator':creator})
	#return HttpResponseRedirect(reverse('events:results', args=(e.id,)))
	invitees = request.POST.get('invitees', '').split()
	for i in invitees:
		newInvitee = Invitee(name=i, userID=User.objects.get(username=i).id, rsvpAccepted=False)
		e.invitee_set.add(newInvitee)
	return index(request)

def delete(request):
	e_id = request.POST['eventID']
	event = get_object_or_404(Instance, pk=e_id)
	event.delete()
	return index(request)

def deleteInvitee(request):
	return index(request)

def getTimes(request):
	e_id = request.POST['eventID']
	event = get_object_or_404(Instance, pk=e_id)
	time = PossTime(event=event, time=ptime)
	return index(request)

def manageCreator(request):
	if 'delete' in request.POST:
		return delete(request)
	if 'getTimes' in request.POST:
		return getTimes(request)
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
		return index(request)
	else:
		invitee.delete()
		#event.invitee_set = event.invitee_set.all().exclude(name=username)
		return index(request)

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
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True
		else:
			print (user_form.errors, profile_form.errors)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
			'events/register.html',
			{'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
			context)

def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
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
