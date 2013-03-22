#from event.models import Event
from dons.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from dons.forms import RegForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def DonsReg(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/profile')
	if request.method == 'POST':
                form = RegForm(request.POST)
                if form.is_valid():
                        user = User.objects.create_user(username=form.cleaned_data['username'], email = form.cleaned_data['email'], password = form.cleaned_data['password'])
                        user.save()
                        don = Don(user=user, name=form.cleaned_data['name'])
                        don.save()
                        return HttpResponseRedirect('/profile/')
                else:
                        return render_to_response('user_register.html', {'form': form}, context_instance=RequestContext(request))
        else:
                ''' user is not submitting the form, show them a blank registration form '''
                form = RegForm()
                context = {'form': form}
                return render_to_response('user_register.html', context, context_instance=RequestContext(request))



def DonsLogin(request):
        if request.user.is_authenticated():
                return HttpResponseRedirect('/profile/')
        if request.method == 'POST':
                form = LoginForm(request.POST)
                if form.is_valid():
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        don = authenticate(username=username, password=password)
                        if don is not None:
                                login(request, don)
                                return HttpResponseRedirect('/profile/')
                        else: # don is not found in database
                                return render_to_response('user_login.html', {'form': form}, context_instance=RequestContext(request))
                else: # form data is invalid
                        return render_to_response('user_login.html', {'form': form}, context_instance=RequestContext(request))
        else: # user is not submitting a POST
                ''' user is not submitting the form, show the login form '''
                form = LoginForm()
                context = {'form': form}
                return render_to_response('user_login.html', context, context_instance=RequestContext(request))


def DonsLogout(request):
        logout(request)
        return HttpResponseRedirect('/event/')
