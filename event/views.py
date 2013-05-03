"""Coding Style:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""

# Python imports
from datetime import datetime
import time

# django-level imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template import loader
from django.template import RequestContext

# app-level imports
from accounts.models import UserProfile
from event.models import Comment
from event.models import Event
from event.models import Like
from event.models import Message
from global_func import base_template_vals
from notification.views import sys_notification
from taggit.managers import TaggableManager
from taggit.models import Tag


def homepage(request):
    """Creates standard index page view for Don's Affairs.
    
    Gets user profile object and its list of "Like" objects,
    list of "Event" objects inorder of creation and formats
    each event object to its title.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        event/event_homepage.html with template_vars.
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    template_var["events"] = Event.objects.filter(is_approved=True
                             ).order_by("-created")
    
    return render_to_response("event/event_homepage.html", template_var,
                              context_instance=RequestContext(request))


@login_required
def index(request):
    """Creates standard index page view for Don's Affairs.

    Gets user profile object and its list of "Like" objects,
    list of "Event" objects inorder of creation and formats
    each event object to its title.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        event/index.html with template_vars.
        
    Raises:
        Http404 error.
    """
    template_var = base_template_vals(request)
    up = UserProfile.objects.filter(django_user=request.user)
    template_var["likes"] = Like.objects.filter(user=up[0])
    
    try:
        event_list = Event.objects.all().order_by('id')
    except Event.DoesNotExist:
        raise Http404
    output = ', '.join([e.title for e in event_list])    
    template_var["events"] = output	
    return render_to_response("event/index.html", template_var,
                              context_instance=RequestContext(request))


@login_required
def single(request, pk):
    """Gathers data for single event object.
    
    Attempts to find event object based on pk argument and then gathers
    any comments if they exist. Then collects all the "User" and
    "UserProfile" objects necessary for "save the date" info.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: The specific event's numerical ID.
        
    Returns:
        event/event_single.html with template_vars.
        
    Raises:
        Http404 error, if event can't be found or isn't approved yet.
    """
    template_var = base_template_vals(request)
    try:
        e = Event.objects.get(pk=int(pk))
        if e.is_approved is False:
            raise Http404
        template_var['event'] = e
    except Event.DoesNotExist:
        raise Http404
    try:
        template_var['comments'] = Comment.objects.filter(event=e)
    except Comment.DoesNotExist:
        template_var['comments'] = []
        
    # Save the date related
    template_var["allusers"] = UserProfile.objects.all()
    template_var["auth_users"] = User.objects.all()

    
    like = Like.objects.filter(event=Event.objects.get(id=pk), user = UserProfile.objects.filter(django_user=request.user)[0])
    if(len(like) == 0):
        template_var["isAlreadySaved"] = False
    else:
        template_var["isAlreadySaved"] = True
        
    return render_to_response("event/event_single.html", template_var,
                              context_instance=RequestContext(request))
    

@login_required
def archives(request):
    """Gathers archive list of all events for list_view of events.
        
    Gets list of "Event" objects in order of event occurance.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        event/event_listview.html with template_vars.
        
    Raises:
        Http404 error.
    """
    template_var = base_template_vals(request)
    try:
        template_var["events"] = Event.objects.all().filter(
                                 is_approved=True).order_by("-event_time")
    except Event.DoesNotExist:
        raise Http404
    return render_to_response("event/event_listview.html", template_var,
                              context_instance=RequestContext(request))


def tagpage(request, tag):
    """Gathers list of events based on a specific tag.
    
    Gets a list of "Event" obejcts based on tag passed in as argument.

    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        tag: Tag to show results for.
        
    Returns:
        event/tag_single.html with template_vars.
        
    Raises:
        Http404 error.
    """
    template_var = base_template_vals(request)
    template_var["tag"] = tag
    try:
        template_var["events"] = Event.objects.filter(is_approved=True
                                 ).filter(tags__name__in = [tag])
    except Event.DoesNotExist:
        raise Http404
    return render_to_response("event/tag_single.html", template_var,
                              context_instance=RequestContext(request))



@login_required	
def add_comment(request, pk, pk2):
    """Posts comment to specific event.
    
    Checks if the request has "content" and the user is authenticated.
    If they both are "True", creates and saves comment object.
    Then sends a notification to the event poster with the sys_notification function.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ID for event that's recieving comment.
        pk2: ID for user posting the comment.
    
    Returns: 
        Calls "single"" function passing in "request"  from input args
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    p = request.POST
    
    if p.has_key("content") and p["content"]:
        if request.user.is_authenticated():
            comment = Comment(event=Event.objects.get(id=pk))
            comment.user = UserProfile.objects.get(django_user=request.user)
            comment.content = p["content"]
            comment.save()

            # Sys notification
            from_user = UserProfile.objects.get(django_user=pk2) # Who's event that is commented on
            to_user = Event.objects.get(id=pk).author
            event_id = pk
            sys_notification(to_user, "add_comment", from_user, event_id)
    return single(request, pk)


@login_required	
def like_event(request, pk):
    """Adds a like to an event.
    
    Creates and saves a Like object which contains the User who liked the event.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ID of event receiving the "Like".
        
    Returns:
        redirect to index.
    
    Raises:
        None.
        
    """
    template_var = base_template_vals(request)
    previousLike = Like.objects.filter(event=Event.objects.get(id=pk), 
                                        user=UserProfile.objects.filter(
                                        django_user=request.user)[0])
    if(len(previousLike) == 0):
        like = Like(event=Event.objects.get(id=pk))
        like.user = UserProfile.objects.filter(django_user=request.user)[0]
        like.save()
        #sys notification
        from_user = UserProfile.objects.get(django_user = User.objects.get(
                                            username__exact='admin')) 
        to_user = UserProfile.objects.get(django_user=request.user)
        event_id = pk
        sys_notification(to_user, "save_event", from_user, event_id)
    return redirect('index')


@login_required	
def unlike_event(request, pk):
    """unlike a saved event.
    
    remove a Like object which contains the User who liked the event.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ID of event receiving the "Like".
        
    Returns:
        redirect to index.
    
    Raises:
        None.
        
    """
    template_var = base_template_vals(request)
    previousLike = Like.objects.filter(event=Event.objects.get(id=pk), 
                                        user=UserProfile.objects.filter(
                                        django_user=request.user)[0])
    if(len(previousLike) != 0):
        like = previousLike[0]
        like.delete()
    return redirect('index')



@login_required
def share_email(request, pk):
    """Shares an Event via email with another user.
    
    Collects address to send email to and link for event from request.
    Then builds message content and sends email.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ? ? ? #TODO: Bin unused variable.
        
    Returns:
        redirect to index.
    
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    subject = 'Your friend shared an event with you on Dons Affairs!'
    from_email = 'from@example.com'
    to = 'donsaffair@gmail.com'
    to = request.POST["email_to"] #default is sending to self 'donsaffair@gmail.com'
    link = request.POST["abs_url"]
    text_content = 'This is an important message.'
    text_content += 'Your friend shared an event link with you. ' + link
    html_content = '<p>Hi Dear,</p>' 
    html_content += '<p>Your friend shared an exciting event with you on ' 
    html_content += '<a href="http://mtk.im/usf">Don\'s Affairs</a>!</p>'
    html_content += '<p><a href="' + link + '"> '
    html_content += 'Here is the link to the event.</a>' 
    html_content += '<br>Feel free to check it out!</p>' + '<p><br>With love,'
    html_content += '<br>Don\'s Affairs Team</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return redirect('index')
    

@login_required
def save_event(request):
    """Saves event to profile for later access.
    
    Creates a message object that is sent to the user about the event.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        IF REQUEST IS POST:
        HttpResponseRedirect to /events/msg/
        ELSE:
        event/message_send.html with template_vars
    
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    template_var["allusers"] = UserProfile.objects.all()    
    if request.method == "POST":
        if request.user.is_authenticated():
            message = Message()
            message.msg_from = UserProfile.objects.filter(
                               django_user=request.user)[0]
            message.msg_to = UserProfile.objects.filter(
                             id__exact=request.POST["msg_to_django_user_id"])[0]
            message.content = request.POST["content"]
            message.save()
        return HttpResponseRedirect("/events/msg/")
        
    return render_to_response("event/message_send.html", template_var, 
                              context_instance=RequestContext(request))


@login_required
def post(request):
    """Posts an event, only moderators can access.
    
    Processes the event form and has exceptions to handle invalid time input
    and lack of picture.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        IF POST SUCCESSFUL:
        HttpResponseRedirect to index
        ELSE:
        event/event_post.html with template_vars
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    user = template_var["u"]
    from_user = UserProfile.objects.get(django_user=request.user)
    if user.is_moderator or user.is_superuser:
        if request.method == "POST":
            title_ = request.POST["title"]
            body_ =  request.POST["body"]
            refer_ = request.POST["refer"]
            date_ = request.POST["date"]
            try:
                time.strptime(date_, '%m/%d/%Y')
            except ValueError:
                current_day = datetime.now().strftime("%Y-%m-%d %H:%M")
                date_ = datetime.strptime(current_day, '%Y-%m-%d %H:%M')
                
            loc_ = request.POST["loc"]
            tags_ = request.POST["tags"]
            if(len(tags_) == 0):
                tags_ = "untagged"
            try:
                image1_ = request.FILES["picture"]
                event = Event(title=title_, body=body_, location=loc_,
                              refer=refer_, event_time=date_, image1=image1_,
                              author=from_user)
            except:
                event = Event(title=title_, body=body_, location=loc_,
                              refer=refer_, event_time=date_, author=from_user)
            event.save() 
            tags = splitTags(tags_)
            for tag in tags:
                event.tags.add(tag)
            event.save() 
            return HttpResponseRedirect(reverse("index")) 
    else:
        return HttpResponseRedirect(reverse("index"))   

    return render_to_response("event/event_post.html", template_var,
                              context_instance=RequestContext(request))



def splitTags(user_input):
    """Parses a list of tags.
    
    Splits string containing tags seperated either by spaces or commas.
    
    Args:
        user_input: String containing all the tags.
        
    Returns:
        List containing tags.
    
    Raises:
        None.
    """
    
    elements = []
    if ',' in user_input:
        elements = user_input.split(',')
    elif ' ' in user_input:
        elements = user_input.split(' ')
    else:
        elements.append(user_input)

    tags = []
    for element in elements:
        element = element.strip(' \t\n\r').lower()
        if(len(element) == 0): continue
        if element not in tags:
            tags.append(element)
    return tags


@login_required
def msg_send(request):
    """Sends message from one user to another.
    
    Fills template vars and creates and saves message object. 
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        IF MESSAGE SEND SUCCESSFUL:
        HttpResponseRedirect to /events/msg/
        ELSE:
        event/message_send.html with template_vars
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    template_var["allusers"] = UserProfile.objects.all()
    current_django_user = UserProfile.objects.filter(
                          django_user=request.user)[0]
    template_var["msg_sent_list"] = Message.objects.filter(
                                    msg_from=current_django_user)
    template_var["msg_received_list"] = Message.objects.filter(
                                        msg_to=current_django_user)
    
    if request.method == "POST":
        if request.user.is_authenticated():
            message = Message()
            message.msg_from = UserProfile.objects.filter(
                               django_user=request.user)[0]
            message.msg_to = UserProfile.objects.filter(
                             id__exact=request.POST["msg_to_django_user_id"])[0]
            message.content = request.POST["content"]
            message.save()    

        return HttpResponseRedirect("/events/msg/")
        
    return render_to_response("event/message_send.html", template_var,
                              context_instance=RequestContext(request))
    
    
def search(request):
    """Creates search results.
    
    First checks that the search query isn't empty and if so, sets advanced_search to True.
    Then creates a list of tags based on the query and gathers the applicable events.
    Then sorts events by date created by default if they started query with space,
    otherwise sorts events by tags if advanced_search = True else finds all events with tag.
    If the advanced_search is True removes duplicates and appends to events_found otherwise
    appends all events to events_found. Then sorts events by sort method, ie; descending, ascending or alphabetically.
    Then finally returns events.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        event/event_search_results.html with template_vars.
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    if request.method=="GET":
        event_id_list = []
        events_found = []
        events_found_advanced = []
        events_found_basic = []
        checkbox_session = []
        advanced_search = False
        tags = Tag.objects.all()
        template_var["tags"] = tags

        query_tags = request.GET.getlist('query_tag')
        if len(query_tags) > 0:  # at least one checkbox selected
            advanced_search = True
            query_tag_list = []
        
            #strip >>u''<< prefix
            for query_tag in query_tags:
                checkbox_session.append(str(query_tag))
                query_tag_list.append(str(query_tag))
                
            events_found_advanced = Event.objects.filter(is_approved=True
                                    ).filter(tags__name__in=query_tag_list)
               
        query = request.GET.get('query', '').strip('\t\n\r')
        if query == '' : #first came in/accidentily type space/..
            if advanced_search:
                events_found_advanced = events_found_advanced #TODO: Bin this line does nothing.
            else:
                events_found_basic = Event.objects.filter(is_approved=True
                                     ).order_by("-created")  
        else:
            if advanced_search:
                events_found_advanced = events_found_advanced.filter(
                                        tags__name__in=[query])
            else:
                events_found_basic = Event.objects.filter(
                                     tags__name__in=[query])

        #finally
        if advanced_search:
            #take out duplicated result
            for event_found_advanced in events_found_advanced:
                if(event_found_advanced.id not in event_id_list):
                    event_id_list.append(event_found_advanced.id)
                    events_found.append(event_found_advanced)
        else:
            for event in events_found_basic:
                events_found.append(event)

        #sort result
        sorted_method = request.GET.get('sorted_method', 'desc') #default is desc
        if sorted_method == 'desc':
            events_found.sort(key=lambda event: event.event_time, reverse=True)  
        elif sorted_method == 'asc':
            events_found.sort(key=lambda event: event.event_time,
                              reverse=False)  
        elif sorted_method == 'alphabet':
            events_found.sort(key=lambda event: event.title.lower(),
                              reverse=False)  
           
        template_var["events_found"] = events_found

        request.session["sorted_method_session"] = sorted_method
        request.session["checkbox_session"] = checkbox_session
        request.session["query_session"] = query
        return render_to_response("event/event_search_results.html",
                                  template_var,
                                  context_instance=RequestContext(request))

    return render_to_response("event/event_search_results.html", template_var,
                              context_instance=RequestContext(request))
    
    
