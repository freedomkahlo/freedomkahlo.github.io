from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from .models import Instance, Invitee

def home(request):
	return render(request, './index.html')
def index(request):
	latest_event_list = Instance.objects.order_by('-pub_date')[:5]
	context = {'latest_event_list': latest_event_list}
	return render(request, 'events/index.html', context)
def detail(request, instance_id):
	event = get_object_or_404(Instance, pk=instance_id)
	return render(request, 'events/detail.html', {'event': event})
#def add(request, )