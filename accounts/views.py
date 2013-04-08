#coding=utf-8
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from forms import RegisterForm,LoginForm
from models import UserProfile


def index(request):
    '''index'''
    template_var={"w":_(u"welcome, visitor!")}
    if request.user.is_authenticated():
        template_var["w"]=_(u"welcome %s!")%request.user.username
        up = UserProfile.objects.filter(userReference=request.user)
        template_var["up"]=up[0]

        
    return render_to_response("accounts/welcome.html",template_var,context_instance=RequestContext(request))

def register(request):
    '''register'''
    template_var={}
    form = RegisterForm()    
    if request.method=="POST":
        form=RegisterForm(request.POST.copy())
        if form.is_valid():
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            user=User.objects.create_user(username,email,password)
            user.save()
            locaiton_ = request.POST['location']
            interest_ = request.POST['interest'] 
            profile = UserProfile(userReference = user, location = locaiton_, interest = interest_)
            profile.save()

            
            _login(request,username,password)#already register, login
            return HttpResponseRedirect(reverse("index"))    
    template_var["form"]=form        
    return render_to_response("accounts/register.html",template_var,context_instance=RequestContext(request))
    
def login(request):
    '''login'''
    template_var={}
    form = LoginForm()    
    if request.method == 'POST':
        form=LoginForm(request.POST.copy())
        if form.is_valid():
            _login(request,form.cleaned_data["username"],form.cleaned_data["password"])
            return HttpResponseRedirect(reverse("index"))
    template_var["form"]=form        
    return render_to_response("accounts/login.html",template_var,context_instance=RequestContext(request))
    
def _login(request,username,password):
    '''login core'''
    ret=False
    user=authenticate(username=username,password=password)
    if user:
        if user.is_active:
            auth_login(request,user)
            ret=True
        else:
            messages.add_message(request, messages.INFO, _(u'user has not activted'))
    else:
        messages.add_message(request, messages.INFO, _(u'user does not exist'))
    return ret
    
def logout(request):
    '''logout'''
    auth_logout(request)
    return HttpResponseRedirect(reverse('index'))
