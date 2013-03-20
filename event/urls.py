from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView
from event.models import Event

urlpatterns = patterns('event.views',

    url(r'^$', ListView.as_view(
	queryset = Event.objects.all().order_by("-created")[:2],
	template_name = "events.html")),

    url(r'^(?P<pk>\d+)$', DetailView.as_view(
	model = Event,
	template_name = "event.html")),

    url(r'^archives/$', ListView.as_view(
	queryset = Event.objects.all().order_by("-created"),
	template_name = "archives.html")),

    url(r'^tag/(?P<tag>\w+)$', 'tagpage'),

)
