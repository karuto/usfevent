#from event.models import Event
from dons.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from dons.forms import RegForm

# Create your views here.
"""
def tagpage(request, tag):
	events = Event.objects.filter(tags__name = tag)
	return render_to_response("tag_single.html", {"events":events, "tag":tag})
"""

def DonsReg(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/profile')
	if request.method == 'POST':
		pass
	else:
		form = RegForm()
		context = {'form': form}
		return render_to_response("user_register.html", context, context_instance = RequestContext(request))


def DonsLogin(request):
	return render_to_response("user_login.html")
