"""Coding Style:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""

# django-level imports
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# app-level imports
from accounts.models import Friendship
from event.models import Comment
from event.models import Event
from event.models import Like
from event.models import Message
from forms import LoginForm
from forms import RegisterForm
from models import UserProfile


def add_friend(request, pk): 
    """Adds targeted user as a friend of the current user.
    
    Only works if current user is authenticated.
    Retrieves the current user and the targeted user's (user_id = pk)
    UserProfile objects, check if they are friends already; and if not, create
    a new friendship object and store it in database.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: Parameter in URL, representing targeted user's UserProfile id.
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.       
    """
    
    template_var = {}    
    if request.user.is_authenticated():
        from_user = UserProfile.objects.get(django_user=request.user)
        to_user = UserProfile.objects.get(id=pk)
        size = len(Friendship.objects.filter(
                    friend_from=from_user, friend_to=to_user))
        if(size == 0):
            f = Friendship(friend_from=from_user, friend_to=to_user)
            f.save()        
    return HttpResponseRedirect(reverse('index'))


def public_profile(request, pk):
    """Processes data needed for an user's public profile.
        
    Only works if current user is authenticated.
    Retrieves the the targeted user's (user_id = pk) UserProfile object, 
    list of friends, list of friends' saved events, 
    a new friendship object and store it in database.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: Parameter in URL, representing targeted user's UserProfile id.
    
    Returns:
        accounts/public_profile.html with template_vars.
    
    Raises:
        None.       
    """
    
    template_var = {}
    if request.user.is_authenticated():
        template_var["user"] = UserProfile.objects.get(id=pk)
        
        # Retrieve list of friends of current user.
        friends = Friendship.objects.filter(friend_from=template_var["user"])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        
        # Retrieve list of friends' saved events of current user.
        template_var["saved_events"] = Like.objects.filter(user=
                                            template_var["user"])
        friends_events = []
        friends_saved_entries = []
        for friend in friends:
            local_likes = Like.objects.filter(user=friend.friend_to)
            if len(local_likes) > 0:
                friends_saved_entries.append(local_likes[0])
                friends_events.append(local_likes[0].event)
        event_id_list = []
        friends_events_ = [] # This is the final list that get passed to HTML
        for friends_event in friends_events:
            if(friends_event.id not in event_id_list):
                event_id_list.append(friends_event.id)
                friends_events_.append(friends_event)
        #for f in friends_saved_entries:
        #    print f.event
        
        template_var["friend_events"] = friends_events_
        template_var["friends_saved_entries"] = friends_saved_entries
        
    return render_to_response("accounts/public_profile.html", template_var,
         context_instance=RequestContext(request))


def index(request):
    """Processes data needed for public index, or an user's private profile.
    
    If current user is NOT authenticated, display a general index page.    
    Private profile only works if current user is authenticated.
    Retrieves the the current user's UserProfile object, and messages / 
    notifications, saved events, friends, friends' saved events' list of the
    current user.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        accounts/profile.html with template_vars.
    
    Raises:
        None.       
    """
    
    template_var = {}
    if request.user.is_authenticated():
        # Retrieve data for current user's private profile
        up = UserProfile.objects.filter(django_user=request.user)
        if len(up) == 0: # no userprofile, say root user created in terminal
            return render_to_response("accounts/profile.html", template_var,
                 context_instance=RequestContext(request))
        template_var["up"] = up[0]

        # Parse "preferences" string in current user's userprofile
        template_var["preferences"] = up[0].preferences
        preferencelist = up[0].preferences.split(",")
        prefered_events = []
        for p in preferencelist:
            prefered_events_ = Event.objects.filter(tags__name__in=[p])
            prefered_events.extend(prefered_events_) # Concatenates two lists
        template_var["prefered_events"] = prefered_events

        # Retrieve message / notification related lists of current user
        current_django_user = UserProfile.objects.filter(
                                    django_user=request.user)[0];
        template_var["msg_sent_list"] = Message.objects.filter(
                                            msg_from=current_django_user)
        template_var["msg_received_list"] = Message.objects.filter(
                                            msg_to=current_django_user)
        
        # Retrieve likes (saved events) list of current user
        template_var["likes"] = Like.objects.filter(user=up[0])
        
        # Retrieve friend list of current user
        friends = Friendship.objects.filter(friend_from=up[0])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        
        # Retrieve and parse friends' saved events' list of current user
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
        
    return render_to_response("accounts/profile.html", template_var,
         context_instance=RequestContext(request))


def register(request):
    """Handles user registration.
    
    If current user is authenticated, redirect the user to index / homepage.    
    Registration only works if current user is NOT authenticated. Captures the
    HTTP POST object and parse associated fields. Combines first and last name
    to create username.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        accounts/register.html with template_vars.
    
    Raises:
        None.       
    """
    
    template_var = {}
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index"))  
        
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        username = firstname + "_" + lastname
        print "###username = " + username
        
        # Does this username already exist in user database? Prepare to check
        i = 0
        queryname = str(username) + "_" + str(i)
        is_username_valid = False
        
        # If username "first_last_i" already exists...
        while (len(User.objects.filter(username = queryname)) > 0):
            i = i + 1
            # check "first_last_i++"
            queryname = str(username) + "_" + str(i)
        user = User.objects.create_user(queryname, email, password)
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
                profile = UserProfile(django_user=user, location=locaiton_, 
                                      interest=interest_,
                                      preferences=preferences_, avatar=avatar_)
            except:
                profile = UserProfile(django_user=user, location=locaiton_,
                             interest=interest_, preferences=preferences_)
                  
            profile.save()
            
        except Exception:
            # If we can not finish saving userprofile, delete the user object
            # Because we don't want users without userprofiles attached
            user.delete()

        
        _login(request, email, password)
        return HttpResponseRedirect(reverse("index"))    
        
    return render_to_response("accounts/register.html", template_var, 
         context_instance=RequestContext(request))

    
def login(request):
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index")) 
    template_var={}
    form = LoginForm()    
    if request.method == 'POST':
        form = LoginForm(request.POST.copy())
        if form.is_valid():
            _login(request,form.cleaned_data["email"],form.cleaned_data["password"])
            return HttpResponseRedirect(reverse("index"))
    template_var["form"]=form        
    return render_to_response("accounts/login.html", template_var,
                              context_instance=RequestContext(request))
    
    
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
    
    
