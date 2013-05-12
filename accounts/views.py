"""Coding Style:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""


# Python imports
from datetime import date
import string

# django-level imports
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

# app-level imports
from accounts.models import Friendship
from accounts.models import UserProfile
from event.models import Comment
from event.models import Event
from event.models import Like
from global_func import base_template_vals
from notification.models import Message
from notification.views import sys_notification


@login_required 
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
        Http404, if either of the friendship participants is non-existent.      
    """    
    template_var = base_template_vals(request)   
    try:
        from_user = UserProfile.objects.get(django_user=request.user)    
    except UserProfile.DoesNotExist:
        raise Http404  
    try:
        to_user = UserProfile.objects.get(id=pk)    
    except UserProfile.DoesNotExist:
        raise Http404  

    if(from_user == to_user):#should not follow self
        return HttpResponseRedirect(reverse('index'))
    
    size = len(Friendship.objects.filter(friend_from=from_user,
                                         friend_to=to_user))
    if(size == 0):
        f = Friendship(friend_from=from_user, friend_to=to_user)
        f.save()
        # System notification
        event_id = 0  # Should be nothing in this case
        print str(to_user)
        print str(from_user)
        sys_notification(to_user, "followed", from_user, event_id)

    return HttpResponseRedirect(reverse('index'))

@login_required 
def remove_friend(request, pk): 
    """remove targeted user from the friend-list of the current user.
    
    Only works if current user is authenticated.
    Retrieves the current user and the targeted user's (user_id = pk)
    UserProfile objects, check if they are friends already; if so, remove their.
    Friendship from database.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: Parameter in URL, representing targeted user's UserProfile id.
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.       
    """

    #global template_var
    template_var = base_template_vals(request)
    
    if request.user.is_authenticated():
        from_user = UserProfile.objects.get(django_user=request.user)
        to_user = UserProfile.objects.get(id=pk)
        size = len(Friendship.objects.filter(
                    friend_from=from_user, friend_to=to_user))
        if(size != 0):
            f = Friendship.objects.filter(
                    friend_from=from_user, friend_to=to_user)[0]
            f.delete()

    return HttpResponseRedirect(reverse('index'))

@login_required 
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
        accounts/public_profile.html with template_vars, if the querying user 
        exists; if user try to access public profile of non-existent users, 
        redirect back to index.
    
    Raises:
        None.       
    """
    

    template_var = base_template_vals(request)
    if request.user.is_authenticated():
        try:
            template_var["user"] = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(reverse('index'))
        # Retrieve list of friends of current user.
        friends = Friendship.objects.filter(friend_from=template_var["user"])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        template_var["friends_num"] = len(friends)
        
        # Retrieve list of friends' saved events of current user.

        template_var["saved_events"] = Like.objects.filter(
                                       user=template_var["user"])
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

        
        template_var["friend_events"] = friends_events_
        template_var["friends_saved_entries"] = friends_saved_entries

        #checck if current login user follow selected public profile user or not
        currentUser = UserProfile.objects.filter(django_user=request.user)
        isAlreadyFollowed = Friendship.objects.filter(friend_from=currentUser, friend_to=template_var["user"])
        if(len(isAlreadyFollowed) != 0):
            template_var["isAlreadyFollowed"] = True;
        else:
            template_var["isAlreadyFollowed"] = False;
        
    return render_to_response("accounts/public_profile.html", template_var,
                              context_instance=RequestContext(request))



@login_required
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

    
    template_var = base_template_vals(request)
    if request.user.is_authenticated():
        # Retrieve data for current user's private profile
        up = UserProfile.objects.filter(django_user=request.user)
        if len(up) == 0: # no userprofile, say root user created in terminal
            return render_to_response("accounts/profile.html", template_var,
                                      context_instance=RequestContext(request))
        template_var["up"] = up[0]

        # Retrieve message / notification related lists of current user
        current_user_profile = UserProfile.objects.filter(
                              django_user=request.user)[0]
        template_var["msg_sent_list"] = Message.objects.filter(
                                        msg_from=current_user_profile)
        template_var["msg_received_list"] = Message.objects.filter(
                                            msg_to=current_user_profile)
        
        # Retrieve likes (saved events) list of current user
        template_var["likes"] = Like.objects.filter(user=up[0])
        
        # Retrieve friend list of current user
        friends = Friendship.objects.filter(friend_from=up[0])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        template_var["friends_num"] = len(friends)
        
        # Retrieve and parse friends' saved events' list of current user
        friends_events = []
        for friend in friends:
            print friend.friend_to
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
        template_var["friends_events"] = []
        
    return render_to_response("accounts/profile.html", template_var,
                              context_instance=RequestContext(request))



@login_required 
def show_friends(request, pk):
    """show friends for given user
        
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
    

    template_var = base_template_vals(request)
    if request.user.is_authenticated():
        template_var["user"] = UserProfile.objects.get(id=pk)
        
        # Retrieve list of friends of current user.
        friends = Friendship.objects.filter(friend_from=template_var["user"])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        template_var["friends_num"] = len(friends)
        
        

        
    return render_to_response("accounts/show_friends.html", template_var,
                              context_instance=RequestContext(request))



@login_required
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

    
    template_var = base_template_vals(request)
    if request.user.is_authenticated():
        # Retrieve data for current user's private profile
        up = UserProfile.objects.filter(django_user=request.user)
        if len(up) == 0: # no userprofile, say root user created in terminal
            return render_to_response("accounts/profile.html", template_var,
                                      context_instance=RequestContext(request))
        template_var["up"] = up[0]

        # Retrieve message / notification related lists of current user
        current_user_profile = UserProfile.objects.filter(
                              django_user=request.user)[0]
        template_var["msg_sent_list"] = Message.objects.filter(
                                        msg_from=current_user_profile)
        template_var["msg_received_list"] = Message.objects.filter(
                                            msg_to=current_user_profile)
        
        # Retrieve likes (saved events) list of current user
        template_var["likes"] = Like.objects.filter(user=up[0])
        
        # Retrieve friend list of current user
        friends = Friendship.objects.filter(friend_from=up[0])
        friends = list(friends) # Cast queryset to list to avoid u("")
        template_var["friends"] = friends
        template_var["friends_num"] = len(friends)
        
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

        USER LOGGED IN: 
        HttpResponseRedirect, to the homepage (index) with no parameters.
        REGISTRATION SUCCESSFUL:
        HttpResponseRedirect, to the homepage (index) with no parameters.
        NO POST REQUEST:
        accounts/register.html with template_vars.
    
    Raises:
        None.       
    """

    template_var = base_template_vals(request)
    grad_years = []
    for y in range(date.today().year, date.today().year + 5): 
        grad_years.append(y)
    template_var["grad_years"] = grad_years
    template_var["errors"] = None
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index"))  
        
    if request.method == "POST":
        print request.POST
        # TODO: don't assume all these fields are in the POST! Check if exist.
        firstname = strip_tags(request.POST['firstname'])
        lastname = strip_tags(request.POST['lastname'])
        username = firstname + "_" + lastname
        email = strip_tags(request.POST['email'])
        password = request.POST['password']
        grad_ = request.POST['grad_year']
        major = request.POST['major']
        bio_ = strip_tags(request.POST['bio'])
        print "bio_", bio_
        aff_test = False
        if 'aff' in request.POST:
            aff_ = request.POST['aff']
            aff_test = True        
        affmsg_ = strip_tags(request.POST['affmsg'])

        # Check for clean input
        results = sanitize(firstname, lastname, email, bio_, password)
        print "results ", results
        if all(results) and aff_test is True: #all tests passed
            print "tests passed"
            firstname = " ".join(firstname.split())
            print "firstname ", firstname
            lastname = " ".join(lastname.split())
            print "lastname ", lastname
            bio_ = " ".join(bio_.split())
            print "bio_ ", bio_
            affmsg_ = " ".join(affmsg_.split())
            print "affmsg_ ", affmsg_
        else: # gotta kick back
            print "tests failed"
            results.insert(-1, aff_test)
            errors = results
            print "errors ", errors
            old_input = {}
            template = "accounts/register.html"
            if len(firstname) > 0: 
                old_input['firstname'] = firstname
            if len(lastname) > 0:   
                old_input['lastname'] = lastname
            if len(email) > 0:
                old_input['email'] = email
            if len(password) > 0:
                old_input['password'] = password
            old_input['grad_year'] = grad_
            if len(bio_) > 0:
                old_input['bio'] = bio_
            if aff_test is True:
                old_input['aff'] = aff_
            if len(affmsg_) > 0:
                old_input['affmsg'] = affmsg_
            old_input['errors'] = errors
            old_input['grad_years'] = template_var["grad_years"]
            print "old input ", old_input
            return render_to_response(template, old_input,
                                      context_instance=RequestContext(request))
        
        # Does this username already exist in user database? Prepare to check
        i = 0
        queryname = str(username) + "_" + str(i)        
        # If username "first_last_i" already exists...
        while (len(User.objects.filter(username = queryname)) > 0):
            i = i + 1
            # Check "first_last_i++"
            queryname = str(username) + "_" + str(i)
        
        user = User.objects.create_user(queryname, email, password)
        user.save()
    
        try:
            try:
                avatar_ = request.FILES["picture"]
                profile = UserProfile(django_user=user, 
                                      firstname=firstname,
                                      lastname=lastname,
                                      major=major,
                                      graduation_year=grad_,
                                      affiliation_type=aff_,
                                      affiliation_msg=affmsg_,
                                      bio=bio_,
                                      avatar=avatar_)
            except:
                profile = UserProfile(django_user=user,
                                      firstname=firstname,
                                      lastname=lastname, 
                                      major=major,
                                      graduation_year=grad_,
                                      affiliation_type=aff_,
                                      affiliation_msg=affmsg_,
                                      bio=bio_)
            profile.save()
            login_helper(request, email, password)
            return HttpResponseRedirect(reverse("index"))    
        except Exception:
            # If we can not finish saving userprofile, delete the user object
            # Because we don't want users without userprofiles attached
            user.delete()
        
    return render_to_response("accounts/register.html", template_var, 
                              context_instance=RequestContext(request))

    
def login(request):
    """Completes login procedure to login registered users to their account.
    
    Checks first, if user is already logged in, if so redirects user to index.
    If user isn't logged in, checks for 'POST' method and validates form.
    Upon validation, calls login_helper to login user if the email password
    pair belongs to a user. If form is valid, check if there's an auto redirect
    URL and return to that. Otherwise returns user to index. If form is invalid
    returns user to login page.
    
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        VALID LOGIN:
        HttpResponseRedirect, to the homepage (index) with no parameters.
        INVALID LOGIN:
        accounts/login.html with template_vars.
        
    Raises:
        None.    
    """ 
    template_var = base_template_vals(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("index"))
     
    if request.method == 'POST':
        email = strip_tags(request.POST['email'])
        password = request.POST['password']
        results = sanitize_login(email, password)
        if all(results) == False:
            old_input = {}
            if len(email) > 0:
                old_input['email'] = email
            if len(password) > 0:
                old_input['password'] = password
            old_input['errors'] = results
            return render_to_response("accounts/login.html", old_input,
                                      context_instance=RequestContext(request))
        if login_helper(request, email, password):
            if len(request.GET) > 0:
                next_url = request.GET["next"]
                if next_url:
                    return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse("index"))
        else:
            old_input = {}
            if len(email) > 0:
                old_input['email'] = email
            if len(password) > 0:
                old_input['password'] = password
            old_input['errors'] = [False, False]
            return render_to_response("accounts/login.html", old_input,
                                      context_instance=RequestContext(request))
    return render_to_response("accounts/login.html", template_var,
                              context_instance=RequestContext(request))
    
    
def login_helper(request, email, password):
    """Determines whether email password pair exists.
    
    Login helper function to check that email password pair exists
    and is active.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        email: Email adress supplied to login form.
        pssword: Password supplied to login form.
    
    Returns:
        ret: Boolean that is "False" if user doesn't exist or isn't active,
             however only "True" if email password is exists and is active.
    
    Raises:
        None.
    """    
    ret = False
    user = authenticate(email=email, password=password)
    if user:
        if user.is_active:
            auth_login(request, user)
            ret = True
    return ret
    
    
@login_required    
def logout(request):
    """Logs out user from account.
    
    Logs out user by sending a logout request to the server with auth_logout.
    Then makes an HTTP request to redirect user to index.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.
    """
    auth_logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required    
def edit_profile(request):
    """edit current user's profile.
    
    Modify user's profile
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    current_user_profile = template_var["u"]

    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        bio_ = request.POST['bio']
        affmsg_ = request.POST['affmsg']
        current_user_profile.firstname = firstname
        current_user_profile.lastname = lastname
        current_user_profile.bio = bio_
        current_user_profile.affmsg = affmsg_
        current_user_profile.save()

        try:
            avatar_ = request.FILES["picture"]
            current_user_profile.avatar = avatar_
            current_user_profile.save()
        except:
            print "no pics"
        
        
        return HttpResponseRedirect(reverse("index"))
    return render_to_response("accounts/edit_profile.html", template_var,
                              context_instance=RequestContext(request))


def sanitize(first, last, email, bio, password):

    result = [True, True, True, True, True]
    
    for c in first:
        if c not in string.ascii_letters and c.isspace() is False:
            result[0] = False
            print "invalid first name"
            break
    if len(first) == 0:
        result[0] = False
    for c in last:
        if c not in string.ascii_letters and c.isspace() is False:
            result[1] = False
            print "invalid last name"
            break
    if len(last) == 0:
        result[1] = False
    if len(bio) > 500:
        result[3] = False
        print "invalid bio"
    if len(password) == 0:
        result[4] == False
    if email_re.match(email):
       return result
    else:
       result[2] = False
       print "invalid email"
       return result
  
   
def sanitize_login(email, password):

    result = [True, True]
    
    if len(password) == 0:
        result[1] == False
    if email_re.match(email):
       return result
    else:
       result[0] = False
       print "invalid email"
       return result    
