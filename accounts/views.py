#coding=utf-8
from accounts.models import Friendship
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


def add_friend(request, pk):    
    template_var={}
    if request.user.is_authenticated():
        from_user = UserProfile.objects.get(django_user=request.user)
        to_user = UserProfile.objects.get(id=pk)
        size = len(Friendship.objects.filter(friend_from=from_user, friend_to=to_user))
        if(size == 0):
            f = Friendship(friend_from=from_user, friend_to=to_user)
            f.save()
        
    return HttpResponseRedirect(reverse('index'))


def public_profile(request, pk):
    template_var={}
    if request.user.is_authenticated():
        template_var["user"] = UserProfile.objects.get(id=pk)
        
        friends = Friendship.objects.filter(friend_from=template_var["user"])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        
        template_var["saved_events"] = Like.objects.filter(user=template_var["user"])
        
        friends_events = []
        friends_saved_entries = []
        for friend in friends:
            local_likes = Like.objects.filter(user=friend.friend_to)
            if len(local_likes) > 0:
                friends_saved_entries.append(local_likes[0])
                friends_events.append(local_likes[0].event)
        event_id_list = []
        friends_events_ = []
        for friends_event in friends_events:
            if(friends_event.id not in event_id_list):
                event_id_list.append(friends_event.id)
                friends_events_.append(friends_event)
        for f in friends_saved_entries:
            print f.event
        
        template_var["friend_events"] = friends_events_
        template_var["friends_saved_entries"] = friends_saved_entries
        
    
    return render_to_response("accounts/public_profile.html", template_var, context_instance=RequestContext(request))


def index(request):
    '''index'''
    template_var = {"w":_(u"welcome, visitor!")}
    if request.user.is_authenticated():
        up = UserProfile.objects.filter(django_user=request.user)
        if len(up) == 0:# no userprofile, e.g. a root user
            return render_to_response("accounts/profile.html", template_var, context_instance=RequestContext(request))

        template_var["up"] = up[0]

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
        my_user = UserProfile.objects.get(django_user=request.user)
        friends = Friendship.objects.filter(friend_from=my_user)
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        
        friends_events = []
        for friend in friends:
            local_likes = Like.objects.filter(id__exact=friend.friend_to.id)
            if len(local_likes) > 0:
                friends_events.append(local_likes[0].event)
        event_id_list = []
        friends_events_ = []
        for friends_event in friends_events:
                if(friends_event.id not in event_id_list):
                    event_id_list.append(friends_event.id)
                    friends_events_.append(friends_event)
        
        template_var["friends_events"] = friends_events_
        

        
    return render_to_response("accounts/profile.html", template_var, context_instance=RequestContext(request))

def register(request):
    '''register'''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index"))  
        
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

            try:
                locaiton_ = request.POST['location']
                interest_ = request.POST['interest']
                preferencelist = request.POST.getlist('preferences')
                             
                preferences_ = ""
                for preference in preferencelist:
                    preferences_ += preference + ","
                
                preferences_ = preferences_[:len(preferences_)-1]

                try:
                    avatar_ = request.FILES["picture"]
                    profile = UserProfile(django_user = user, location = locaiton_, interest = interest_, preferences = preferences_, avatar = avatar_)
                except:
                    profile = UserProfile(django_user = user, location = locaiton_, interest = interest_, preferences = preferences_)
                      
                #profile = UserProfile(django_user = user, location = locaiton_, interest = interest_, preferences = preferences_, avatar = avatar_)
                profile.save()
            except Exception:
                user.delete()

            
            _login(request,email,password)#already register, login
            return HttpResponseRedirect(reverse("index"))    
    template_var["form"]=form        
    return render_to_response("accounts/register.html",template_var,context_instance=RequestContext(request))
    
def login(request):
    '''login'''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index")) 
    template_var={}
    form = LoginForm()    
    if request.method == 'POST':
        form=LoginForm(request.POST.copy())
        if form.is_valid():
            _login(request,form.cleaned_data["email"],form.cleaned_data["password"])
            return HttpResponseRedirect(reverse("index"))
    template_var["form"]=form        
    return render_to_response("accounts/login.html",template_var,context_instance=RequestContext(request))
    
    
def _login(request,email,password):
    '''login core'''
    ret=False
    user=authenticate(email=email,password=password)
    if user:
        if user.is_active:
            auth_login(request,user)
            print "Email:" + user.email
            print "Email2:" + email
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
    
    
