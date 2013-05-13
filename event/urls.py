from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from event.models import Event
from event import views

urlpatterns = patterns('event.views',

    url(r'^$', "homepage", name="home"),

    url(r'^(?P<pk>\d+)$', "single",	name='single'),

    url(r'^archives/$', 'archives', name='archives'),
    url(r'^tag/(?P<tag>\w+)$', 'tagpage', name='tag'),
    url(r'^post/$', 'post', name="post"),
    url(r'^order/$', 'order', name="order"),

    url(r'^(\d+)/(\d+)/add_comment/$', 'add_comment', name="add_comment"),
    url(r'^(\d+)/edit$', 'edit_event', name="edit_event"),
    url(r'^(\d+)/like/$', 'like_event', name="like_event"),
    url(r'^(\d+)/unlike/$', 'unlike_event', name="unlike_event"),
    url(r'^(\d+)/email/$', 'share_email', name="share_email"),
    #url(r'^(\d+)/save/$', 'save_event', name="save_event"), 
    
    url(r'^msg/$', 'msg_send', name="msg_send"),
    url(r'^search/$', 'search', name="search"),
                       
)
