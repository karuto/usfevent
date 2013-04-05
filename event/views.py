# Create your views here.
from event.models import Event
from django.http import HttpResponse
from django.template import Context, loader

def index(request):
	event_list = Event.objects.all().order_by('id')
	
	output = ', '.join([e.title for e in event_list])
	return HttpResponse(output)


