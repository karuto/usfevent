from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView
#from event.models import Event
from dons import views

urlpatterns = patterns('dons.views',

    url(r'^login/$', 'login'),
"""
    url(r'^$', ListView.as_view(
	queryset = Event.objects.all().order_by("-created")[:6],
	template_name = "event_homepage.html")),

    url(r'^(?P<pk>\d+)$', DetailView.as_view(
	model = Event,
	template_name = "event_single.html"),
	name = 'single'),

    url(r'^archives/$', ListView.as_view(
	queryset = Event.objects.all().order_by("-created"),
	template_name = "event_listview.html")),

    url(r'^tag/(?P<tag>\w+)$', 'tagpage', name = 'tag'),
"""
)
