from event.models import Event
from django.shortcuts import render_to_response

# Create your views here.
def tagpage(request, tag):
	events = Event.objects.filter(tags__name = tag)
	return render_to_response("tagpage.html", {"events":events, "tag":tag})
