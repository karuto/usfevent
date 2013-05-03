from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from accounts.models import UserProfile
from accounts import views

urlpatterns = patterns('accounts.views',

    url(r'^(?P<pk>\d+)$', "public_profile", name='profile'),
    url(r'^(?P<pk>\d+)/add/$', "add_friend", name='friend'),
    url(r'^(?P<pk>\d+)/remove/$', "remove_friend", name='unfriend'),
    url(r'^(?P<pk>\d+)/friends/$', "show_friends", name='show_friends'),

    url(r'^index/$', 'index', name="accounts_index"),
    url(r'^register/$', 'register', name="register"),
    url(r'^login/$', 'login', name="login"),
    url(r'^logout/$', 'logout', name="logout"),

    url(r'^edit_profile/$', 'edit_profile', name="edit_profile"),

)
