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
from global_func import base_template_vals
from notification.models import Message


def sys_notification(target, types, from_user, event_id):
    """Collects / sends message for 'followed' and 'commented' notification.
    
    Set's that the user who sent the message is the 'Admin', creates 
    appropriate message based on notification type, and then saves the message.
    
    Args:
        target: User that message is being sent to.
        types: Type of message that is being sent.
        from_user: User that sent the message.
        event_id: ? ? ? #TODO: Bin decide if you're gonna use 'event_id' or not.
        
    Returns:
        None.
    
    Raises:
        None.
    """
    
    msg_from = UserProfile.objects.get(
               django_user=User.objects.get(username__exact='admin'))  
               #admin userprofile #TODO: FUCKING HARDCODE, BUT NO BETTER WAY?!

    message = Message()
    message.msg_from = msg_from
    message.msg_to = target

    print "prepare to send"

    if (types == "followed"):
        message.title = str(from_user.django_user) + " followed you."
        message.content = str(from_user.django_user) + " followed you."
        print "send"
    elif(types == "add_comment"):
        message.title = str(from_user.django_user) + " comments on your event."
        message.content = str(from_user.django_user) + " comments on your event." + "<a href='/events/"+ event_id+"'>link</a>"
    elif(types == "save_event"):
        message.title = "The event saved successfully. "
        message.content = "The event saved successfully. " + "<a href='/events/"+ event_id+"'>link</a>"
    elif(types == "approve_event"):
        message.title = "The event has been approved."
        message.content = "The event has been approved. " + "<a href='/events/"+ event_id+"'>link</a>"
    elif(types == "approve_user"):
        message.title = "You have been promoted. "
        message.content = "You have been promoted. "
    

    else:
        message.title = "Unknown System Notification."
        message.content = "Unknown System Notification."    
    message.save()


@login_required
def msg_open(request, pk):
    """Loads single message view.
    
    Collects message object based on pk, sets the message as read and saves the message.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ID of message.
    
    Returns:
        HttpResponse with the message's content.
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    current_user_profile = UserProfile.objects.filter(
                          django_user=request.user)[0]
    msg = Message.objects.get(msg_to=current_user_profile, id=pk)
    

    if(msg):
        msg.is_read = True
        msg.save()
    template_var["message"] = msg
    return render_to_response("notification/msg_single.html", template_var,
                              context_instance=RequestContext(request))


@login_required
def msg_delete(request, pk):
    """Deletes single message view.
    
    Collects message object based on pk, sets the message as read and saves the message.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
        pk: ID of message.
    
    Returns:
        HttpResponse with the message's content.
        
    Raises:
        None.
    """
    template_var = base_template_vals(request)
    current_user_profile = UserProfile.objects.filter(
                          django_user=request.user)[0]
    msg = Message.objects.get(msg_to=current_user_profile, id=pk)
    

    if(msg):
        msg.delete()
    return redirect('msg_box')


@login_required
def msg_box(request):
    """Loads user's messages inbox.
    
    Gathers and displays user's recieved messages.

    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
            
    Returns:
        notification/msg_box.html with template_vars
    
    Raises:
        None.    
    """
    template_var = base_template_vals(request)
    current_user_profile = UserProfile.objects.filter(
                          django_user=request.user)[0]
    template_var["msg_received_list"] = Message.objects.filter(
                                        msg_to=current_user_profile).order_by('-time')
    return render_to_response("notification/msg_box.html", template_var,
                              context_instance=RequestContext(request))
                              
                              
