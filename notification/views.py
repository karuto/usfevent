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
from global_func import base_template_vals
import time


def test(request):
    template_var = {}
    
    return HttpResponse("Hello, world. You're at the poll index.")


def sys_notification(target, types, from_user, event_id):
    msg_from = UserProfile.objects.get(django_user = User.objects.get(username__exact='admin'))  #admin userprofile #TODO: FUCKING HARDCODE, BUT NO BETTER WAY?!
    message = Message()
    message.msg_from = msg_from
    message.msg_to = target

    if(types == "followed"):
        message.content = str(from_user.django_user) + " followed you."
    elif(types == "add_comment"):
        message.content = str(from_user.django_user) + " comments on your event." + "<a href='/events/1'>link</a>"
    else:
        message.content = "Unknown System Notification."    
    message.save()


def msg_open(request, pk):
    
    #global template_var
    template_var = base_template_vals(request)
    
    #template_var["user"] = UserProfile.objects.get(id=pk)
    current_django_user = UserProfile.objects.filter(django_user=request.user)[0]
    msg = Message.objects.get(msg_to=current_django_user, id=pk)
    if(msg):
        msg.is_read = True
        msg.save()
    template_var["msg"] = msg
    return HttpResponse(msg.content)
    #return render_to_response("accounts/msg_new_unread.html", template_var, context_instance=RequestContext(request))

def msg_box(request):

    #global template_var
    template_var = base_template_vals(request)
    
    #template_var["user"] = UserProfile.objects.get(id=pk)
    current_django_user = UserProfile.objects.filter(django_user=request.user)[0]
    template_var["msg_received_list"] = Message.objects.filter(msg_to=current_django_user)
    #return HttpResponse(len(template_var["msg_received_list"]))
    return render_to_response("notification/msg_box.html", template_var, context_instance=RequestContext(request))

