from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView
from event.models import Event

urlpatterns = patterns('',
    url(r'^', ListView.as_view(
	queryset = Event.objects.all().order_by("-created")[:5],
	template_name = "event.html")),

)
