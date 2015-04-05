from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Desc, Invitee, InitTime

def index(request):
	latest_event_list = Desc.objects.order_by('-pub_date')[:5]
	context = {'latest_event_list': latest_event_list}
	return render(request, 'events/index.html', context)
def detail(request, desc_id):
	event = get_object_or_404(Desc, pk=desc_id)
	return render(request, 'events/detail.html', {'event': event})