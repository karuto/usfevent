from accounts.models import UserProfile
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from event.models import Comment, Event, Message, Like
import time


def sys_notification(target, types, from_user, event_id):
    """
    
    """
    msg_from = UserProfile.objects.get(
               django_user=User.objects.get(username__exact='admin'))  #admin userprofile #TODO: FUCKING HARDCODE, BUT NO BETTER WAY?!
    message = Message()
    message.msg_from = msg_from
    message.msg_to = target

    if (types == "followed"):
        message.content = str(from_user.django_user) + " followed you."
    elif (types == "add_comment"):
        message.content = str(from_user.django_user) + 
                          " comments on your event." + 
                          " <a href='/events/1'>link</a>" #TODO: BIN! URL IS HARDCODED!!!!!
    else:
        message.content = "Unknown System Notification."    
    message.save()


def msg_open(request, pk):
    """
    
    """
    template_var = {}
    current_django_user = UserProfile.objects.filter(
                          django_user=request.user)[0]
    msg = Message.objects.get(msg_to=current_django_user, id=pk)
    if (msg):
        msg.is_read = True
        msg.save()
    template_var["msg"] = msg
    return HttpResponse(msg.content)


def msg_box(request):
    """
    
    """
    template_var = {}
    current_django_user = UserProfile.objects.filter(django_user=request.user)[0]
    template_var["msg_received_list"] = Message.objects.filter(msg_to=current_django_user)
    return render_to_response("notification/msg_box.html", template_var, context_instance=RequestContext(request))

