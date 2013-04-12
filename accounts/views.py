#coding=utf-8
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from forms import RegisterForm, LoginForm
from models import UserProfile
from event.models import Event, Message, Comment, Like


def index(request):
    '''index'''
    template_var={"w":_(u"welcome, visitor!")}
    if request.user.is_authenticated():
        template_var["username"]= request.user.username
        up = UserProfile.objects.filter(django_user=request.user)
        template_var["up"]=up[0]

        template_var["preferences"] = up[0].preferences
        preferencelist = up[0].preferences.split(",")
        eventPreferenced = []

        for preference in preferencelist:
            eventPreferenced_ = Event.objects.filter(tags__name__in=[preference])
            eventPreferenced.extend(eventPreferenced_)


        current_django_user = UserProfile.objects.filter(django_user=request.user)[0];
        template_var["msg_sent_list"] = Message.objects.filter(msg_from=current_django_user)
        template_var["msg_received_list"] = Message.objects.filter(msg_to=current_django_user)
        
        
        template_var["likes"] = Like.objects.filter(user=up[0])
        
        #eventList = []
        #for e in eventPreferenced:
        #    eventList.append(e.title)
        #template_var["eventPreferenced"] = str(eventList)

        template_var["eventPreferenced"] = eventPreferenced

        
    return render_to_response("accounts/welcome.html", template_var, context_instance=RequestContext(request))

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
            preferencelist = request.POST.getlist('preferences')
            avatar_ = request.FILES["picture"]

            preferences_ = ""
            for preference in preferencelist:
                preferences_ += preference + ","
            
            preferences_ = preferences_[:len(preferences_)-1]


            profile = UserProfile(django_user = user, location = locaiton_, interest = interest_, preferences = preferences_, avatar = avatar_)
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
