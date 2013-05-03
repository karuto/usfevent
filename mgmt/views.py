"""Coding Style:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""

# Python imports
from datetime import date

# django-level imports
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# app-level imports
from accounts.models import Friendship
from accounts.models import UserProfile
from event.models import Comment
from event.models import Event
from event.models import Like
from event.models import Message
from event.views import index
from global_func import base_template_vals
from notification.views import msg_box
from notification.views import sys_notification

@login_required
def db_init(request): 
    """Initialize the global database.
    
    Fill in pre-set content and taxonomies.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.       
    """
    template_var = base_template_vals(request) 
    user = template_var["u"]
    if user.is_superuser:
        return render_to_response("mgmt/init.html", template_var,
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))
    

@login_required
def overview(request): 
    """Provides an overview for superuser to manage the site.
    
    Displays number of pending order forms, admin requests and event 
    submissions, and the detailed list below.
    
    Args:
        request: Django's HttpRequest object that contains metadata.
            https://docs.djangoproject.com/en/dev/ref/request-response/
    
    Returns:
        HttpResponseRedirect, to the homepage (index) with no parameters.
    
    Raises:
        None.       
    """
    template_var = base_template_vals(request)
    user = template_var["u"]
    if user.is_superuser:
        # Retrieve objects if its "affiliation_msg" string length > 1
        # http://stackoverflow.com/questions/15708416/django-lookup-by-length-of-text-field
        template_var["user_list"] = UserProfile.objects.filter(
                                    affiliation_msg__iregex=r'^.{1,}$').filter(
                                    is_approved=False)
        template_var["user_num"] = len(template_var["user_list"])
        template_var["event_list"] = Event.objects.filter(is_approved=False)
        template_var["event_num"] = len(template_var["event_list"])
        return render_to_response("mgmt/overview.html", template_var,
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))


@login_required
def approve_user(request, pk): 
    template_var = base_template_vals(request)
    user = template_var["u"]
    if user.is_superuser:
        approved_user = UserProfile.objects.get(id=pk)
        approved_user.affiliation_msg = ""
        approved_user.is_moderator = True
        approved_user.is_approved = True
        approved_user.save()
        return HttpResponseRedirect(reverse('overview'))
    else:
        return HttpResponseRedirect(reverse('index'))


@login_required
def approve_event(request, pk): 
    template_var = base_template_vals(request)
    user = template_var["u"]
    if user.is_superuser:
        approved_event = Event.objects.get(id=pk)
        approved_event.is_approved = True
        approved_event.save()
        return HttpResponseRedirect(reverse('overview'))
    else:
        return HttpResponseRedirect(reverse('index'))
    
    
