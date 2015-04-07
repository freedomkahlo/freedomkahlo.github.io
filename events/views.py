from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from .models import Instance, Invitee
from .forms import UserForm, UserProfileForm
from django.shortcuts import render_to_response

def home(request):
	return render(request, './index.html')
def index(request):
	latest_event_list = Instance.objects.order_by('-pub_date')[:100]
	context = {'latest_event_list': latest_event_list}
	return render(request, 'events/index.html', context)
def detail(request, instance_id):
	event = get_object_or_404(Instance, pk=instance_id)
	return render(request, 'events/detail.html', {'event': event})
def add(request):
	e = Instance(title=request.POST['title'], desc=request.POST['desc'], 
		start_date=request.POST['start_date'], end_date=request.POST['end_date'],
		start_time=request.POST['start_time'], end_time=request.POST['end_time'])
	print (e.title)
	e.save()
	return index(request)
	#return HttpResponseRedirect(reverse('events:results', args=(e.id,)))
def delete(request):
	e_id = request.POST['eventID']
	event = get_object_or_404(Instance, pk=e_id)
	event.delete()
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