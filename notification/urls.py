from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from event.models import Event
from event import views

urlpatterns = patterns('notification.views',

    url(r'^msg_box$', "msg_box", name='msg_box'),
    url(r'^(?P<pk>\d+)/msg_open$', "msg_open", name='msg_open'),
)
