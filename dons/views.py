#from event.models import Event
from dons.models import *
from django.shortcuts import render_to_response

# Create your views here.
"""
def tagpage(request, tag):
	events = Event.objects.filter(tags__name = tag)
	return render_to_response("tag_single.html", {"events":events, "tag":tag})
"""

def login(request):
	return render_to_response("user_login.html")
