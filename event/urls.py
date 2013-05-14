from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from event.models import Event
from event import views

urlpatterns = patterns('event.views',

    url(r'^$', 'homepage', name='homepage'),
    url(r'^order/$', 'order', name='order'),
    url(r'^(?P<pk>\d+)$', 'single',	name='single'),
    url(r'^archives/$', 'archives', name='archives'),
    url(r'^tag/(?P<tag>\w+)$', 'tagpage', name='tag'),
    url(r'^search/$', 'search', name='search'),
    url(r'^(\d+)/edit$', 'edit', name='edit'),
    url(r'^post/$', 'post', name='post'),

    url(r'^(\d+)/like/$', 'like_event', name='like_event'),
    url(r'^(\d+)/unlike/$', 'unlike_event', name='unlike_event'),
    url(r'^(\d+)/email/$', 'share_email', name='share_email'),
    url(r'^(\d+)/(\d+)/add_comment/$', 'add_comment', name='add_comment'),
                       
)
